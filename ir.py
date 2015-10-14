import json
import os
import sys

import dead_inst_elim
import dead_func_elim
import instcombine
import mem2reg
import simplify_cfg
import spirv


class IRError(Exception):
    def __init__(self, message):
        super(IRError, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class Module(object):
    def __init__(self):
        self.bound = None
        self.functions = []
        self.global_insts = []
        self._value_to_id = {}
        self._tmp_id_counter = 0

    def dump(self, stream=sys.stdout):
        """Write debug dump to stream."""
        for inst in self.global_insts:
            stream.write(str(inst) + '\n')
        for function in self.functions:
            stream.write('\n')
            function.dump(stream)

    def optimize(self):
        """Do basic optimizations.

        This only runs optimization passes that are likely to be profitable
        on all architectures (such as removing dead code)."""
        instcombine.optimize(self)
        simplify_cfg.optimize(self)
        dead_inst_elim.optimize(self)
        dead_func_elim.optimize(self)
        mem2reg.optimize(self)
        instcombine.optimize(self)
        simplify_cfg.optimize(self)
        dead_inst_elim.optimize(self)
        dead_func_elim.optimize(self)

    def instructions(self):
        """Iterate over all instructions in the module."""
        for inst in self.global_insts[:]:
            yield inst
        for function in self.functions[:]:
            for inst in function.instructions():
                yield inst

    def instructions_reversed(self):
        """Iterate in reverse order over all instructions in the module."""
        for function in reversed(self.functions[:]):
            for inst in function.instructions_reversed():
                yield inst
        for inst in reversed(self.global_insts[:]):
            yield inst

    def new_id(self):
        """Generate a new ID."""
        self._tmp_id_counter += 1
        return Id(self, self._tmp_id_counter, True)

    def get_id(self, value):
        """Get or create the ID having the specied value."""
        if value in self._value_to_id:
            return self._value_to_id[value]
        new_id = Id(self, value)
        self._value_to_id[value] = new_id
        return new_id

    def _copy_global_insts(self, dest, names):
        """Copy global insts with the provided operation names to dest."""
        for inst in self.global_insts:
            if inst.op_name in names:
                dest.append(inst)

    def _sort_global_insts(self):
        """Sort self.global_insts as required by the SPIR-V specification."""
        sorted_insts = []
        for name in INITIAL_INSTRUCTIONS:
            self._copy_global_insts(sorted_insts, [name])
        self._copy_global_insts(sorted_insts, ['OpString'])
        self._copy_global_insts(sorted_insts, ['OpName', 'OpMemberName'])
        self._copy_global_insts(sorted_insts, ['OpLine'])
        self._copy_global_insts(sorted_insts, DECORATION_INSTRUCTIONS)
        self._copy_global_insts(sorted_insts,
                                TYPE_DECLARATION_INSTRUCTIONS +
                                CONSTANT_INSTRUCTIONS +
                                SPECCONSTANT_INSTRUCTIONS +
                                GLOBAL_VARIABLE_INSTRUCTIONS)
        assert len(self.global_insts) == len(sorted_insts)
        self.global_insts = sorted_insts

    def add_global_inst(self, inst):
        """Add instruction to the module's global instructions."""
        if not inst.is_global_inst():
            raise IRError(inst.op_name + ' is not a valid global instruction')
        self.global_insts.append(inst)
        _add_use_to_id(inst)

    def add_function(self, function):
        """Add function to the module."""
        self.functions.append(function)

    def get_constant(self, type_id, value):
        """Get a constant with the provided value and type.

        The constant is created if not already existing.
        For vector types, the value need to be a list of the same length
        as the vector size, or a scalar, in which case the value is
        replicated for all elements."""
        if (type_id.inst.op_name == 'OpTypeInt' or
                type_id.inst.op_name == 'OpTypeFloat'):
            min_val, max_val = get_int_type_range(type_id)
            if value < 0:
                if value < min_val:
                    raise IRError('Value out of range')
                value = value & max_val
            else:
                if value > max_val:
                    raise IRError('Value out of range')
            if type_id.inst.operands[0] == 64:
                operands = [value & 0xffffffff, value >> 32]
            else:
                operands = [value]
            for inst in self.global_insts:
                if (inst.op_name == 'OpConstant' and
                        inst.type_id == type_id and
                        inst.operands == operands):
                    return inst
            inst = Instruction(self, 'OpConstant', self.new_id(),
                               type_id, operands)
            self.add_global_inst(inst)
            return inst
        elif type_id.inst.op_name == 'OpTypeVector':
            nof_elements = type_id.inst.operands[1]
            if not isinstance(value, (list, tuple)):
                value = [value] * nof_elements
            operands = []
            for elem in value:
                instr = self.get_constant(type_id.inst.operands[0], elem)
                operands.append(instr.result_id)
            for inst in self.global_insts:
                if (inst.op_name == 'OpConstantComposite' and
                        inst.type_id == type_id and
                        inst.operands == operands):
                    return inst
            inst = Instruction(self, 'OpConstantComposite', self.new_id(),
                               type_id, operands)
            self.add_global_inst(inst)
            return inst
        elif type_id.inst.op_name == 'OpTypeBool':
            op_name = 'OpConstantTrue' if value else 'OpConstantFalse'
            for inst in self.global_insts:
                if inst.op_name == op_name:
                    return inst
            inst = Instruction(self, op_name, self.new_id(), type_id, [])
            self.add_global_inst(inst)
            return inst
        else:
            raise IRError('Invalid type for constant')

    def finalize(self):
        self._sort_global_insts()

        # Determine ID bound, and collect all temporary IDs.
        temp_ids = []
        self.bound = 0
        for inst in self.instructions():
            if inst.result_id is not None:
                if inst.result_id.is_temp:
                    temp_ids.append(inst.result_id)
                else:
                    self.bound = max(self.bound, inst.result_id.value)
        self.bound += 1

        # Create a new ID for each temporary ID.
        id_rename = {}
        for temp_id in temp_ids:
            id_rename[temp_id] = self.get_id(self.bound)
            id_rename[temp_id].uses = temp_id.uses
            self.bound += 1

        # Update all uses of temporary ID to use the new values.
        for inst in self.instructions():
            if inst.result_id in id_rename:
                new_id = id_rename[inst.result_id]
                old_id = inst.result_id
                inst.result_id = new_id
                new_id.inst = inst
                old_id.inst = None
            if inst.type_id in id_rename:
                inst.type_id = id_rename[inst.type_id]
            for i in range(len(inst.operands)):
                if isinstance(inst.operands[i], Id):
                    if inst.operands[i] in id_rename:
                        inst.operands[i] = id_rename[inst.operands[i]]

        # Rebuild ID mapping table to get rid of obsolete entries.
        for value in self._value_to_id.keys():
            if self._value_to_id[value].inst is None:
                self._value_to_id[value].destroy()
                del self._value_to_id[value]


class Function(object):
    def __init__(self, module, function_id, function_control, function_type_id):
        self.module = module
        self.parameters = []
        self.basic_blocks = []
        self.inst = Instruction(self.module, 'OpFunction',
                                function_id, function_type_id.inst.operands[0],
                                [function_control, function_type_id])
        _add_use_to_id(self.inst)
        self.end_inst = Instruction(self.module, 'OpFunctionEnd',
                                    None, None, [])
        _add_use_to_id(self.end_inst)

    def __str__(self):
        return str(self.inst)

    def destroy(self):
        """Destroy the function.

        This destroys all basic blocks and instructions used in the function.
        The function must not be used after it is destroyed."""
        self.module.functions.remove(self)
        for basic_block in reversed(self.basic_blocks[:]):
            basic_block.destroy()
        for inst in self.parameters:
            inst.destroy()
        self.end_inst.destroy()
        self.inst.destroy()
        self.module = None
        self.parameters = None
        self.basic_blocks = None
        self.inst = None
        self.end_inst = None

    def dump(self, stream=sys.stdout):
        """Write debug dump to stream."""
        stream.write(str(self.inst) + '\n')
        for basic_block in self.basic_blocks:
            basic_block.dump(stream)
        stream.write(str(self.end_inst) + '\n')

    def instructions(self):
        """Iterate over all instructions in the function."""
        yield self.inst
        for inst in self.parameters[:]:
            yield inst
        for basic_block in self.basic_blocks[:]:
            if basic_block.function is not None:
                yield basic_block.inst
                for inst in basic_block.insts[:]:
                    yield inst
        yield self.end_inst

    def instructions_reversed(self):
        """Iterate in reverse order over all instructions in the function."""
        yield self.end_inst
        for basic_block in reversed(self.basic_blocks[:]):
            if basic_block.function is not None:
                for inst in reversed(basic_block.insts[:]):
                    yield inst
                yield basic_block.inst
        for inst in reversed(self.parameters[:]):
            yield inst
        yield self.inst

    def append_parameter(self, inst):
        """Append parameter to the parameters list."""
        if inst.op_name != 'OpFunctionParameter':
            raise IRError('Expected OpFunctionParameter')
        func_type_inst = self.inst.operands[1].inst
        assert func_type_inst.op_name == 'OpTypeFunction'
        params = func_type_inst.operands[1:]
        param_idx = len(self.parameters)
        if param_idx >= len(params):
            raise IRError('Too many parameters')
        if inst.type_id != params[param_idx]:
            raise IRError('Incorrect parameter type')
        self.parameters.append(inst)
        _add_use_to_id(inst)

    def add_basic_block(self, basic_block):
        """Add one basic block to the function."""
        self.basic_blocks.append(basic_block)
        basic_block.function = self


class BasicBlock(object):
    def __init__(self, module, label_id):
        self.function = None
        self.module = module
        self.inst = Instruction(self.module, 'OpLabel', label_id, None, [])
        _add_use_to_id(self.inst)
        self.inst.basic_block = self
        self.insts = []

    def __str__(self):
        return str(self.inst)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return other is self

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_successors(self):
        """Return the list of successor basic blocks."""
        branch_inst = self.insts[-1]
        assert branch_inst.op_name in BRANCH_INSTRUCTIONS
        if branch_inst.op_name == 'OpBranch':
            successors = [branch_inst.operands[0].inst.basic_block]
        elif branch_inst.op_name == 'OpBranchConditional':
            successors = [branch_inst.operands[1].inst.basic_block,
                          branch_inst.operands[2].inst.basic_block]
        elif branch_inst.op_name == 'OpSwitch':
            successors = [branch_inst.operands[1].inst.basic_block]
            targets = branch_inst.operands[2:]
            while targets:
                targets.pop(0)
                successors.append(targets.pop(0).inst.basic_block)
        else:
            successors = []
        return successors

    def dump(self, stream=sys.stdout):
        """Write debug dump to stream."""
        stream.write(str(self.inst) + '\n')
        for inst in self.insts:
            stream.write('  ' + str(inst) + '\n')

    def append_inst(self, inst):
        """Add instruction at the end of the basic block."""
        if inst.is_global_inst():
            raise IRError(inst.op_name + ' is a global instruction')
        inst.basic_block = self
        self.insts.append(inst)
        _add_use_to_id(inst)

    def prepend_inst(self, inst):
        """Add instruction at the top of the basic block."""
        if inst.is_global_inst():
            raise IRError(inst.op_name + ' is a global instruction')
        inst.basic_block = self
        self.insts = [inst] + self.insts
        _add_use_to_id(inst)

    def remove(self):
        """Remove basic block from function."""
        if self.function is None:
            raise IRError('Basic block is not in function')
        self.function.basic_blocks.remove(self)
        self.function = None

    def destroy(self):
        """Destroy the basic block.

        This removes all instructions from the basic block, and removes the
        basic block from the function (if it is attached to a function).
        The basic block must not be used after it is destroyed."""
        self.remove()
        for inst in reversed(self.insts[:]):
            uses = inst.uses()
            for tmp_inst in uses:
                if tmp_inst.op_name == 'OpPhi':
                    IRError('Not implemented: remove from phi node') # XXX
            inst.destroy()
        self.module = None

    def predecessors(self):
        """Return this basic block's predecessors."""
        predecessors = []
        for inst in self.inst.uses():
            if inst.op_name != 'OpPhi':
                predecessors.append(inst.basic_block)
        return predecessors


class Instruction(object):
    def __init__(self, module, op_name, result_id, type_id, operands):
        self.module = module
        self.op_name = op_name
        self.result_id = result_id
        self.type_id = type_id
        self.operands = operands
        self.basic_block = None
        if op_name == 'OpFunction':
            function_type_inst = operands[1].inst
            if function_type_inst.op_name != 'OpTypeFunction':
                raise IRError('Expected OpTypeFunction as second operand')
        if result_id is not None:
            if result_id.inst is not None:
                raise IRError('ID ' + str(result_id) + ' already defined')
            result_id.inst = self

    def __str__(self):
        res = ''
        if self.result_id is not None:
            res = res + str(self.result_id) + ' = '
        res = res + self.op_name
        if self.type_id is not None:
            res = res + ' ' + str(self.type_id)
        if self.operands:
            res = res + ' '
            for operand in self.operands:
                res = res + str(operand) + ', '
            res = res[:-2]
        return res

    def clone(self):
        """Create a copy of the instruction.

        The new instruction is identical to this instruction, except that
        it has a new result_id (if the instruction type has a result_id),
        and it is not bound to any basic block."""
        if self.result_id is not None:
            new_id = self.module.new_id()
        else:
            new_id = None
        return Instruction(self.module, self.op_name, new_id, self.type_id,
                           self.operands[:])

    def insert_after(self, insert_pos_inst):
        """Add instruction after an existing instruction."""
        if self.is_global_inst():
            raise IRError(self.op_name + ' is a global instruction')
        basic_block = insert_pos_inst.basic_block
        if basic_block is None:
            raise IRError('Instruction is not in basic block')
        idx = basic_block.insts.index(insert_pos_inst)
        self.basic_block = basic_block
        basic_block.insts.insert(idx + 1, self)
        _add_use_to_id(self)

    def insert_before(self, insert_pos_inst):
        """Add instruction before an existing instruction."""
        if self.is_global_inst():
            raise IRError(self.op_name + ' is a global instruction')
        basic_block = insert_pos_inst.basic_block
        if basic_block is None:
            raise IRError('Instruction is not in basic block')
        idx = basic_block.insts.index(insert_pos_inst)
        self.basic_block = basic_block
        basic_block.insts.insert(idx, self)
        _add_use_to_id(self)

    def remove(self):
        """Remove instruction from basic block or global instruction list.

        The instruction's debug and decoration instructions are unaffected,
        so that it is possible to re-insert the instruction again."""
        _remove_use_from_id(self)
        if self.basic_block is None:
            if self not in self.module.global_insts:
                raise IRError('Instruction is not in basic block or module')
            self.module.global_insts.remove(self)
            return
        self.basic_block.insts.remove(self)
        self.basic_block = None

    def destroy(self):
        """Destroy instruction.

        This removes the instruction, together with its debug and decoration
        instructions, from the module. The instruction must not be used
        after it is destroyed."""
        _remove_use_from_id(self)
        for inst in self.module.global_insts[:]:
            if (inst.op_name in DECORATION_INSTRUCTIONS or
                    inst.op_name in DEBUG_INSTRUCTIONS):
                if self.result_id in inst.operands:
                    inst.destroy()
        if self.is_global_inst():
            self.module.global_insts.remove(self)
        if self.basic_block is not None:
            self.basic_block.insts.remove(self)
        if self.result_id is not None:
            self.result_id.inst = None
        self.basic_block = None
        self.op_name = None
        self.result_id = None
        self.type_id = None
        self.operands = None

    def uses(self):
        """Return all instructions using this instruction.

        Debug and decoration instructions are not considered using
        any instruction."""
        res = []
        if self.result_id is not None:
            res = [inst for inst in self.result_id.uses
                   if (inst.op_name not in DECORATION_INSTRUCTIONS and
                       inst.op_name not in DEBUG_INSTRUCTIONS)]
        return res

    def get_decorations(self):
        """Return all decorations for this instruction."""
        res = []
        if self.result_id is not None:
            res = [inst for inst in self.result_id.uses
                   if inst.op_name in DECORATION_INSTRUCTIONS]
            res.sort(key=_decoration_key)
        return res

    def replace_uses_with(self, new_inst):
        """Replace all uses of this instruction with new_inst.

        Decoration and debug instructions are not updated, as they are
        considered being a part of the instruction they reference."""
        for inst in self.uses():
            inst.substitute_type_and_operands(self, new_inst)

    def replace_with(self, new_inst):
        """Replace this instruction with new_inst.

        All uses of this instruction is replaced by new_inst, the
        new_inst is inserted in the location of this instruction,
        and this instruction is destroyed."""
        new_inst.insert_after(self)
        self.replace_uses_with(new_inst)
        self.destroy()

    def substitute_type_and_operands(self, old_inst, new_inst):
        """Change use of old_inst in this instruction to new_inst."""
        _remove_use_from_id(self)
        if self.type_id == old_inst.result_id:
            self.type_id = new_inst.result_id
        for idx in range(len(self.operands)):
            if self.operands[idx] == old_inst.result_id:
                self.operands[idx] = new_inst.result_id
        _add_use_to_id(self)

    def has_side_effect(self):
        """True if the instruction may be removed if unused."""
        # XXX Need to handle OpExtInst correctly (it is conservative now)
        if self.result_id is None and self.result_id != 'OpNop':
            return True
        return self.op_name in HAS_SIDE_EFFECT

    def is_global_inst(self):
        """Return true if this is a global instruction, false otherwise."""
        if (self.op_name in GLOBAL_INSTRUCTIONS and
                not (self.op_name == 'OpVariable' and
                     self.operands[0] == 'Function')):
            return True
        return False

    def copy_decorations(self, src_inst):
        """Copy the decorations from src_inst to this instruction."""
        for inst in src_inst.get_decorations():
            new_operands = inst.operands[:]
            new_operands[0] = self.result_id
            new_inst = Instruction(self.module, inst.op_name,
                                   None, None, new_operands)
            self.module.add_global_inst(new_inst)


class Id(object):
    def __init__(self, module, value, is_temp=False):
        assert 0 < value <= 0xffffffff
        assert is_temp or value not in module._value_to_id
        self.value = -value if is_temp else value
        self.is_temp = is_temp
        self.inst = None
        self.uses = set()

    def destroy(self):
        """Destroy the ID."""
        self.is_temp = False
        self.inst = None
        self.uses = None
        # Change the value to be out of range so that it will be caught
        # if the ID escapes and is written to a binary, and so that the
        # orginal value can be retrieved by subtracting 0x200000000, which
        # should be helpful during debugging.
        self.value = self.value + 0x200000000

    def __str__(self):
        if self.is_temp:
            return '%.' + str(-self.value)
        else:
            return '%' + str(self.value)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return other is self

    def __ne__(self, other):
        return not self.__eq__(other)


def _decoration_key(decoration_inst):
    """Comparision key to return decorations in deterministic order."""
    return decoration_inst.operands[1]


def _add_use_to_id(inst):
    if inst.type_id is not None:
        inst.type_id.uses.add(inst)
    for operand in inst.operands:
        if isinstance(operand, Id):
            operand.uses.add(inst)


def _remove_use_from_id(inst):
    if inst.type_id is not None:
        assert inst in inst.type_id.uses
        inst.type_id.uses.remove(inst)
    for operand in inst.operands:
        if isinstance(operand, Id):
            if inst in operand.uses:
                operand.uses.remove(inst)


def get_int_type_range(type_id):
    # Type must be OpTypeInt or OpTypeFloat (the OpTypeFloat is valid,
    # as its value is stored as integer words, and these words must
    # have value within the integer range).
    if type_id.inst.op_name not in ['OpTypeInt', 'OpTypeFloat']:
        raise IRError('Type must be OpTypeInt or OpTypeFloat')
    bitwidth = type_id.inst.operands[0]
    assert bitwidth in [16, 32, 64]
    if bitwidth == 16:
        min_val = -0x8000
        max_val = 0xffff
    elif bitwidth == 32:
        min_val = -0x80000000
        max_val = 0xffffffff
    else:
        min_val = -0x8000000000000000
        max_val = 0xffffffffffffffff

    if type_id.inst.op_name == 'OpTypeFloat':
        # A negative value for OpTypeFloat probably mean that the caller
        # has made a mistake (as it does not make much sense to specify
        # the bits of a float using negative values), so don't permit
        # negative values.
        min_val = 0

    return min_val, max_val


MAGIC = 0x07230203
GENERATOR_MAGIC = 0
VERSION = 99

with open(os.path.join(os.path.dirname(__file__), 'inst_format.json')) as fd:
    INST_FORMAT = json.load(fd)

OPCODE_TO_OPNAME = dict(zip(spirv.spv['Op'].values(), spirv.spv['Op'].keys()))

MASKS = set([_name for _name in spirv.spv if _name[-4:] == 'Mask'])

BRANCH_INSTRUCTIONS = [
    'OpReturnValue',
    'OpBranch',
    'OpBranchConditional',
    'OpReturn',
    'OpKill',
    'OpUnreachable',
    'OpSwitch'
]

# The order of the instructions in the first part of the binary (before
# the debug and annotation instructions).
INITIAL_INSTRUCTIONS = [
    'OpSource',
    'OpSourceExtension',
    'OpCapability',
    'OpExtension',
    'OpExtInstImport',
    'OpMemoryModel',
    'OpEntryPoint',
    'OpExecutionMode'
]

DEBUG_INSTRUCTIONS = [
    'OpString',
    'OpName',
    'OpMemberName',
    'OpLine',
]

DECORATION_INSTRUCTIONS = [
    'OpDecorate',
    'OpMemberDecorate',
    'OpGroupDecorate',
    'OpGroupMemberDecorate',
    'OpDecorationGroup'
]

TYPE_DECLARATION_INSTRUCTIONS = [
    'OpTypeVoid',
    'OpTypeBool',
    'OpTypeInt',
    'OpTypeFloat',
    'OpTypeVector',
    'OpTypeMatrix',
    'OpTypeImage',
    'OpTypeSampler',
    'OpTypeSampledImage',
    'OpTypeArray',
    'OpTypeRuntimeArray',
    'OpTypeStruct',
    'OpTypeOpaque',
    'OpTypePointer',
    'OpTypeFunction',
    'OpTypeEvent',
    'OpTypeDeviceEvent',
    'OpTypeReserveId',
    'OpTypeQueue',
    'OpTypePipe'
]

CONSTANT_INSTRUCTIONS = [
    'OpConstantTrue',
    'OpConstantFalse',
    'OpConstant',
    'OpConstantComposite',
    'OpConstantSampler',
    'OpConstantNull',
]

SPECCONSTANT_INSTRUCTIONS = [
    'OpSpecConstantTrue',
    'OpSpecConstantFalse',
    'OpSpecConstant',
    'OpSpecConstantComposite',
    'OpSpecConstantOp'
]

GLOBAL_VARIABLE_INSTRUCTIONS = [
    'OpVariable'
]

GLOBAL_INSTRUCTIONS = set(INITIAL_INSTRUCTIONS +
                          DEBUG_INSTRUCTIONS +
                          DECORATION_INSTRUCTIONS +
                          TYPE_DECLARATION_INSTRUCTIONS +
                          CONSTANT_INSTRUCTIONS +
                          GLOBAL_VARIABLE_INSTRUCTIONS)

HAS_SIDE_EFFECT = set([
    'OpFunction',
    'OpFunctionParameter',
    'OpFunctionCall',
    'OpExtInst',
    'OpAtomicExchange',
    'OpAtomicCompareExchange',
    'OpAtomicCompareExchangeWeak',
    'OpAtomicIIncrement',
    'OpAtomicIDecrement',
    'OpAtomicIAdd',
    'OpAtomicISub',
    'OpAtomicSMin',
    'OpAtomicUMin',
    'OpAtomicSMax',
    'OpAtomicUMax',
    'OpAtomicAnd',
    'OpAtomicOr',
    'OpAtomicXor',
    'OpLabel',
    'OpAsyncGroupCopy',
    'OpWaitGroupEvents',
    'OpGroupAll',
    'OpGroupAny',
    'OpGroupBroadcast',
    'OpGroupIAdd',
    'OpGroupFAdd',
    'OpGroupFMin',
    'OpGroupUMin',
    'OpGroupSMin',
    'OpGroupFMax',
    'OpGroupUMax',
    'OpGroupSMax',
    'OpReadPipe',
    'OpWritePipe',
    'OpReservedReadPipe',
    'OpReservedWritePipe',
    'OpReserveReadPipePackets',
    'OpReserveWritePipePackets',
    'OpGroupReserveWritePipePackets',
    'OpEnqueueMarker',
    'OpEnqueueKernel',
    'OpCreateUserEvent'
])
