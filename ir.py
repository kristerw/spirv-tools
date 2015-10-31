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
    """Raised when incorrect IR is created/detected."""


class Module(object):
    def __init__(self):
        self.bound = 1
        self.functions = []
        self.global_instructions = _GlobalInstructions(self)

    def dump(self, stream=sys.stdout):
        """Write debug dump to stream."""
        self.global_instructions.dump()
        for function in self.functions:
            stream.write('\n')
            function.dump(stream)

    def optimize(self):
        """Do basic optimizations.

        This only runs optimization passes that are likely to be profitable
        on all architectures (such as removing dead code)."""
        instcombine.run(self)
        simplify_cfg.run(self)
        dead_inst_elim.run(self)
        dead_func_elim.run(self)
        mem2reg.run(self)
        instcombine.run(self)
        simplify_cfg.run(self)
        dead_inst_elim.run(self)
        dead_func_elim.run(self)

    def instructions(self):
        """Iterate over all instructions in the module."""
        for inst in self.global_instructions.instructions():
            yield inst
        for function in self.functions[:]:
            for inst in function.instructions():
                yield inst

    def instructions_reversed(self):
        """Iterate in reverse order over all instructions in the module."""
        for function in reversed(self.functions[:]):
            for inst in function.instructions_reversed():
                yield inst
        for inst in self.global_instructions.instructions_reversed():
            yield inst

    def insert_global_inst(self, inst):
        """Insert a global instruction into the module."""
        self.global_instructions.append_inst(inst)
        _add_use_to_id(inst)

    def get_global_inst(self, op_name, type_id, operands):
        """Return a global instruction.

        An already existing instruction is returned if possible. A new
        global instruction is created and inserted in the module if no
        such instruction is available."""
        return self.global_instructions.get_inst(op_name, type_id, operands)

    def append_function(self, function):
        """Insert function at the end of the module."""
        self.functions.append(function)

    def prepend_function(self, function):
        """Insert function at the top of the module."""
        self.functions = [function] + self.functions

    def insert_function_after(self, function, insert_pos_function):
        """Insert function after an existing function."""
        idx = self.functions.index(insert_pos_function)
        self.functions.insert(idx + 1, function)

    def insert_function_before(self, function, insert_pos_function):
        """Insert function before an existing function."""
        idx = self.functions.index(insert_pos_function)
        self.functions.insert(idx, function)

    def get_constant(self, type_id, value):
        """Get a constant with the provided value and type.

        The constant is created if not already existing.
        For vector types, the value need to be a list of the same length
        as the vector size, or a scalar, in which case the value is
        replicated for all elements.

        For matrix types, the value need to be a list of the same length
        as the column count (where each element is a list of the column with
        or a scalar), or a scalar, in which case the value is replicated for
        all elements."""
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
            return self.get_global_inst('OpConstant', type_id, operands)
        elif (type_id.inst.op_name == 'OpTypeVector' or
              type_id.inst.op_name == 'OpTypeMatrix'):
            nof_elements = type_id.inst.operands[1]
            if not isinstance(value, (list, tuple)):
                value = [value] * nof_elements
            operands = []
            for elem in value:
                instr = self.get_constant(type_id.inst.operands[0], elem)
                operands.append(instr.result_id)
            return self.get_global_inst('OpConstantComposite', type_id,
                                        operands)
        elif type_id.inst.op_name == 'OpTypeBool':
            op_name = 'OpConstantTrue' if value else 'OpConstantFalse'
            return self.get_global_inst(op_name, type_id, [])
        else:
            raise IRError('Invalid type for constant')

    def is_constant_value(self, inst, value):
        """Return true if the instruction is a constant with value.

        For vector types, the value need to be a list of the same length
        as the vector size, or a scalar, in which case the value is
        replicated for all elements.

        For matrix types, the value need to be a list of the same length
        as the column count (where each element is a list of the column with
        or a scalar), or a scalar, in which case the value is replicated for
        all elements."""
        if inst.op_name not in CONSTANT_INSTRUCTIONS:
            return False
        type_id = inst.type_id
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
            return inst.operands == operands
        elif (type_id.inst.op_name == 'OpTypeVector' or
              type_id.inst.op_name == 'OpTypeMatrix'):
            nof_elements = type_id.inst.operands[1]
            if not isinstance(value, (list, tuple)):
                value = [value] * nof_elements
            operands = []
            for operand, val in zip(inst.operands, value):
                if not self.is_constant_value(operand.inst, val):
                    return False
            return True
        elif type_id.inst.op_name == 'OpTypeBool':
            op_name = 'OpConstantTrue' if value else 'OpConstantFalse'
            return inst.op_name == op_name
        else:
            raise IRError('Invalid type for constant')

    def renumber_temp_ids(self):
        """Convert temp IDs to real IDs."""
        # Collect all temporary IDs.
        # The temporary IDs are placed in a list (rather than e.g. a set)
        # so that we get deterministic result when we renumber by iterating
        # over the temporary IDs.
        temp_ids = [inst.result_id for inst in self.instructions()
                    if inst.result_id is not None and inst.result_id.is_temp]

        # Create a new ID for each temporary ID, and update the instructions.
        # The code modifies the instructions, which is "wrong" -- the correct
        # way of handling this is to replace the old instruction with a
        # cloned instruction having the new ID. But the API does currently
        # not handle cloning/replacing OpFunction, OpFunctionParameter, or
        # OpLabel (and you could argue it does not need to, as no application
        # should do this kind of modification).
        for old_id in temp_ids:
            new_id = Id(self, self.bound)
            old_id.inst.result_id = new_id
            new_id.inst = old_id.inst
            old_id.inst = None
            for inst in old_id.uses:
                if inst.type_id == old_id:
                    inst.type_id = new_id
                for i in range(len(inst.operands)):
                    if inst.operands[i] == old_id:
                        inst.operands[i] = new_id
            new_id.uses = old_id.uses


class _GlobalInstructions(object):
    def __init__(self, module):
        self.module = module
        self.op_source_insts = []
        self.op_source_extension_insts = []
        self.op_capability_insts = []
        self.op_extension_insts = []
        self.op_extinstimport_insts = []
        self.op_memory_model_insts = []
        self.op_entry_point_insts = []
        self.op_execution_mode_insts = []
        self.op_string_insts = []
        self.name_insts = []
        self.op_line_insts = []
        self.decoration_insts = []
        self.type_insts = []

    def __str__(self):
        return 'global instructions pseudo-BB'

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return other is self

    def __ne__(self, other):
        return not self.__eq__(other)

    def dump(self, stream=sys.stdout):
        """Write debug dump to stream."""
        for inst in self.instructions():
            stream.write('  ' + str(inst) + '\n')

    def _get_insts_list(self, op_name):
        """Get the list containing instructions of inst's kind.

        The function returns both the list and the list's position in the
        order the lists are written in the binary."""
        if op_name == 'OpSource':
            insts_list = self.op_source_insts
            order = 0
        elif op_name == 'OpSourceExtension':
            insts_list = self.op_source_extension_insts
            order = 1
        elif op_name == 'OpCapability':
            insts_list = self.op_capability_insts
            order = 2
        elif op_name == 'OpExtension':
            insts_list = self.op_extension_insts
            order = 3
        elif op_name == 'OpExtInstImport':
            insts_list = self.op_extinstimport_insts
            order = 4
        elif op_name == 'OpMemoryModel':
            insts_list = self.op_memory_model_insts
            order = 5
        elif op_name == 'OpEntryPoint':
            insts_list = self.op_entry_point_insts
            order = 6
        elif op_name == 'OpExecutionMode':
            insts_list = self.op_execution_mode_insts
            order = 7
        elif op_name == 'OpString':
            insts_list = self.op_string_insts
            order = 8
        elif op_name in ['OpName', 'OpMemberName']:
            insts_list = self.name_insts
            order = 9
        elif op_name == 'OpLine':
            insts_list = self.op_line_insts
            order = 10
        elif op_name in DECORATION_INSTRUCTIONS:
            insts_list = self.decoration_insts
            order = 11
        elif (op_name in TYPE_DECLARATION_INSTRUCTIONS or
              op_name in CONSTANT_INSTRUCTIONS or
              op_name in SPECCONSTANT_INSTRUCTIONS or
              op_name in  GLOBAL_VARIABLE_INSTRUCTIONS):
            insts_list = self.type_insts
            order = 12
        else:
            raise IRError(op_name + ' is not a valid global instruction')
        return insts_list, order

    def instructions(self):
        """Iterate over all global instructions."""
        for inst in self.op_source_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_source_extension_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_capability_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_extension_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_extinstimport_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_memory_model_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_entry_point_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_execution_mode_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_string_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.name_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.op_line_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.decoration_insts[:]:
            if inst.basic_block is not None:
                yield inst
        for inst in self.type_insts[:]:
            if inst.basic_block is not None:
                yield inst

    def instructions_reversed(self):
        """Iterate in reverse order over all global instructions."""
        for inst in reversed(self.type_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.decoration_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_line_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.name_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_string_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_execution_mode_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_entry_point_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_memory_model_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_extinstimport_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_extension_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_capability_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_source_extension_insts[:]):
            if inst.basic_block is not None:
                yield inst
        for inst in reversed(self.op_source_insts[:]):
            if inst.basic_block is not None:
                yield inst

    def get_inst(self, op_name, type_id, operands):
        """Return a global instruction.

        An already existing instruction is returned if possible. A new
        global instruction is created and inserted in the module if no
        such instruction is available."""
        insts_list, _ = self._get_insts_list(op_name)
        for inst in insts_list:
            if (inst.op_name == op_name and
                    inst.type_id == type_id and
                    inst.operands == operands):
                return inst
        inst = Instruction(self.module, op_name, type_id, operands)
        self.append_inst(inst)
        return inst

    def append_inst(self, inst):
        """Insert inst at the end of the global instructions of its kind."""
        insts_list, _ = self._get_insts_list(inst.op_name)
        insts_list.append(inst)
        inst.basic_block = self
        _add_use_to_id(inst)

    def prepend_inst(self, inst):
        """Insert inst at the top of the global instructions of its kind."""
        insts_list, _ = self._get_insts_list(inst.op_name)
        insts_list.insert(0, inst)
        inst.basic_block = self
        _add_use_to_id(inst)

    def insert_inst_after(self, inst, insert_pos_inst):
        """Insert instruction after an existing instruction."""
        insert_pos_list, insert_ord = self._get_insts_list(insert_pos_inst)
        insts_list, inst_ord = self._get_insts_list(inst.op_name)
        if insert_pos_list == insts_list:
            idx = insert_pos_list.index(insert_pos_inst)
            insert_pos_list.insert(idx + 1, inst)
            inst.basic_block = self
            _add_use_to_id(inst)
        else:
            if inst_ord > insert_ord:
                self.prepend_inst(inst)
            else:
                raise IRError(inst.op_name + ' cannot be inserted after ' +
                              insert_pos_inst.op_name)

    def insert_inst_before(self, inst, insert_pos_inst):
        """Insert instruction before an existing instruction."""
        insert_list, insert_ord = self._get_insts_list(insert_pos_inst.op_name)
        insts_list, inst_ord = self._get_insts_list(inst.op_name)
        if insert_list == insts_list:
            idx = insert_list.index(insert_pos_inst)
            insert_list.insert(idx, inst)
            inst.basic_block = self
            _add_use_to_id(inst)
        else:
            if inst_ord < insert_ord:
                self.append_inst(inst)
            else:
                raise IRError(inst.op_name + ' cannot be inserted before ' +
                              insert_pos_inst.op_name)

    def remove_inst(self, inst):
        """Remove the inst instruction from global instructions."""
        _remove_use_from_id(inst)
        insts_list, _ = self._get_insts_list(inst.op_name)
        insts_list.remove(inst)
        inst.basic_block = None


class Function(object):
    def __init__(self, module, function_control, type_id, result_id=None):
        self.module = module
        self.parameters = []
        self.basic_blocks = []
        self.inst = Instruction(self.module, 'OpFunction',
                                type_id.inst.operands[0],
                                [function_control, type_id],
                                result_id=result_id)
        _add_use_to_id(self.inst)
        self.end_inst = Instruction(self.module, 'OpFunctionEnd', None, [])
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
        for inst in self.parameters[:]:
            _remove_use_from_id(inst)
            inst.destroy()
        _remove_use_from_id(self.end_inst)
        self.end_inst.destroy()
        _remove_use_from_id(self.inst)
        self.inst.destroy()
        self.module = None
        self.parameters = None
        self.basic_blocks = None
        self.inst = None
        self.end_inst = None

    def remove(self):
        """Remove function from module."""
        self.module.functions.remove(self)

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
            if inst in self.parameters:
                yield inst
        for basic_block in self.basic_blocks[:]:
            yield basic_block.inst
            for inst in basic_block.insts[:]:
                if inst.basic_block is not None:
                    yield inst
        yield self.end_inst

    def instructions_reversed(self):
        """Iterate in reverse order over all instructions in the function."""
        yield self.end_inst
        for basic_block in reversed(self.basic_blocks[:]):
            for inst in reversed(basic_block.insts[:]):
                if inst.basic_block is not None:
                    yield inst
            yield basic_block.inst
        for inst in reversed(self.parameters[:]):
            if inst in self.parameters:
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

    def append_basic_block(self, basic_block):
        """Insert basic block at the end of the function."""
        self.basic_blocks.append(basic_block)
        basic_block.function = self

    def prepend_basic_block(self, basic_block):
        """Insert basic block at the top of the function."""
        self.basic_blocks = [basic_block] + self.basic_blocks
        basic_block.function = self

    def insert_basic_block_after(self, basic_block, insert_pos_basic_block):
        """Insert basic block after an existing basic block."""
        idx = self.basic_blocks.index(insert_pos_basic_block)
        self.basic_blocks.insert(idx + 1, basic_block)

    def insert_basic_block_before(self, basic_block, insert_pos_basic_block):
        """Insert basic block before an existing basic block."""
        idx = self.basic_blocks.index(insert_pos_basic_block)
        self.basic_blocks.insert(idx, basic_block)


class BasicBlock(object):
    def __init__(self, module, label_id):
        self.function = None
        self.module = module
        self.inst = Instruction(self.module, 'OpLabel', None, [],
                                result_id=label_id)
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
        """Return list of successor basic blocks."""
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
        """Insert instruction at the end of the basic block."""
        if inst.is_global_inst():
            raise IRError(inst.op_name + ' is a global instruction')
        self.insts.append(inst)
        inst.basic_block = self
        _add_use_to_id(inst)

    def prepend_inst(self, inst):
        """Insert instruction at the top of the basic block."""
        if inst.is_global_inst():
            raise IRError(inst.op_name + ' is a global instruction')
        self.insts = [inst] + self.insts
        inst.basic_block = self
        _add_use_to_id(inst)

    def insert_inst_after(self, inst, insert_pos_inst):
        """Insert instruction after an existing instruction."""
        idx = self.insts.index(insert_pos_inst)
        self.insts.insert(idx + 1, inst)
        inst.basic_block = self
        _add_use_to_id(inst)

    def insert_inst_before(self, inst, insert_pos_inst):
        """Insert instruction before an existing instruction."""
        idx = self.insts.index(insert_pos_inst)
        self.insts.insert(idx, inst)
        inst.basic_block = self
        _add_use_to_id(inst)

    def remove_inst(self, inst):
        """Remove instruction from basic block."""
        _remove_use_from_id(inst)
        self.insts.remove(inst)
        inst.basic_block = None

    def remove(self):
        """Remove basic block from function."""
        if self.function is None:
            raise IRError('Basic block is not in function')
        self.function.basic_blocks.remove(self)
        self.function = None

    def destroy(self):
        """Destroy the basic block.

        This destroys all instructions used in the basic block, and
        removes the basic block from the function (if it is attached
        to a function).

        The basic block must not be used after it is destroyed."""
        self.remove()
        uses = self.inst.uses()
        for tmp_inst in uses:
            if tmp_inst.op_name == 'OpPhi':
                tmp_inst.remove_from_phi(self)
        for inst in reversed(self.insts[:]):
            inst.destroy()
        self.module = None
        self.insts = None

    def predecessors(self):
        """Return the predecessor basic blocks.

        Note: The predecessors are returned in arbitrary order."""
        return [inst.basic_block for inst in self.inst.uses()
                if inst.op_name != 'OpPhi']


class Instruction(object):
    def __init__(self, module, op_name, type_id, operands, result_id=None):
        if result_id is None:
            if op_name not in INST_FORMAT:
                raise IRError('Invalid op_name ' + str(op_name))
            if INST_FORMAT[op_name]['result']:
                result_id = Id(module)
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
        return Instruction(self.module, self.op_name, self.type_id,
                           self.operands[:])

    def insert_after(self, insert_pos_inst):
        """Insert instruction after an existing instruction."""
        basic_block = insert_pos_inst.basic_block
        if basic_block is None:
            raise IRError('Instruction is not in a basic block')
        basic_block.insert_inst_after(self, insert_pos_inst)

    def insert_before(self, insert_pos_inst):
        """Insert instruction before an existing instruction."""
        basic_block = insert_pos_inst.basic_block
        if basic_block is None:
            raise IRError('Instruction is not in a basic block')
        basic_block.insert_inst_before(self, insert_pos_inst)

    def remove(self):
        """Remove instruction from basic block or global instruction list.

        The instruction's debug and decoration instructions are unaffected,
        so that it is possible to re-insert the instruction again."""
        if self.basic_block is None:
            raise IRError('Instruction is not in basic block or module')
        self.basic_block.remove_inst(self)

    def destroy(self):
        """Destroy instruction.

        This removes the instruction, together with its debug and decoration
        instructions, from the module. The instruction must not be used
        after it is destroyed."""
        if self.result_id is not None:
            uses = [inst for inst in self.result_id.uses
                    if (inst.op_name in DECORATION_INSTRUCTIONS or
                        inst.op_name in DEBUG_INSTRUCTIONS)]
            for inst in uses:
                inst.destroy()
        if self.basic_block is not None:
            self.basic_block.remove_inst(self)
        if self.result_id is not None:
            self.result_id.inst = None
        self.basic_block = None
        self.op_name = None
        self.result_id = None
        self.type_id = None
        self.operands = None

    def add_to_phi(self, variable_inst, parent_inst):
        """Add a variable/parent to a phi-node."""
        assert self.op_name == 'OpPhi'
        self.operands.append(variable_inst.result_id)
        variable_inst.result_id.uses.add(self)
        self.operands.append(parent_inst.result_id)
        parent_inst.result_id.uses.add(self)

    def remove_from_phi(self, parent_id):
        """Remove a parent (and corresponding variable) from a phi-node."""
        assert self.op_name == 'OpPhi'
        idx = self.operands.index(parent_id)
        variable_id = self.operands[idx - 1]
        del self.operands[idx - 1 : idx + 1]
        self.operands.append(variable_id)
        variable_id.operand.uses.remove(self)
        self.operands.append(parent_id)
        parent_id.operand.uses.remove(self)

    def uses(self):
        """Return all instructions using this instruction.

        Debug and decoration instructions are not considered using
        any instruction."""
        if self.result_id is not None:
            res = [inst for inst in self.result_id.uses
                   if (inst.op_name not in DECORATION_INSTRUCTIONS and
                       inst.op_name not in DEBUG_INSTRUCTIONS)]
        else:
            res = []
        return res

    def get_decorations(self):
        """Return all decorations for this instruction."""
        if self.result_id is not None:
            res = [inst for inst in self.result_id.uses
                   if inst.op_name in DECORATION_INSTRUCTIONS]
            res.sort(key=lambda decoration_inst: decoration_inst.operands[1])
        else:
            res = []
        return res

    def replace_uses_with(self, new_inst):
        """Replace all uses of this instruction with new_inst.

        Decoration and debug instructions are not updated, as they are
        considered being a part of the instruction they reference."""
        for inst in self.uses():
            _remove_use_from_id(inst)
            if inst.type_id == self.result_id:
                inst.type_id = new_inst.result_id
            for idx in range(len(inst.operands)):
                if inst.operands[idx] == self.result_id:
                    inst.operands[idx] = new_inst.result_id
            _add_use_to_id(inst)

    def replace_with(self, new_inst):
        """Replace this instruction with new_inst.

        All uses of this instruction is replaced by new_inst, the
        new_inst is inserted in the location of this instruction,
        and this instruction is destroyed.

        Decoration and debug instructions are not updated, as they are
        considered being a part of the instruction they reference."""
        new_inst.insert_after(self)
        self.replace_uses_with(new_inst)
        self.destroy()

    def has_side_effects(self):
        """Return True if the instruction may have side effects."""
        # XXX Need to handle OpExtInst correctly (it is conservative now)
        if self.result_id is None and self.result_id != 'OpNop':
            return True
        return self.op_name in _HAS_SIDE_EFFECT

    def is_commutative(self):
        """True if the instruction is commutative."""
        return self.op_name in _IS_COMMUTATIVE

    def is_global_inst(self):
        """Return true if this is a global instruction, false otherwise."""
        if ((self.op_name in INITIAL_INSTRUCTIONS or
             self.op_name in DEBUG_INSTRUCTIONS or
             self.op_name in DECORATION_INSTRUCTIONS or
             self.op_name in TYPE_DECLARATION_INSTRUCTIONS or
             self.op_name in CONSTANT_INSTRUCTIONS or
             self.op_name in GLOBAL_VARIABLE_INSTRUCTIONS) and
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
                                   None, new_operands)
            self.module.insert_global_inst(new_inst)


class Id(object):
    _temp_id_counter = 0

    def __init__(self, module, value=None):
        if value is None:
            self._temp_id_counter += 1
            self.value = self._temp_id_counter
            self.is_temp = True
        else:
            assert 0 < value < 0xffffffff
            self.value = value
            self.is_temp = False
            module.bound = max(module.bound, value + 1)
        self.inst = None
        self.uses = set()

    def destroy(self):
        """Destroy the ID."""
        self.is_temp = False
        self.inst = None
        self.uses = None
        # Change the value to be out of range so that it will be caught
        # if the ID escapes and is written to a binary, and so that the
        # original value can be retrieved by subtracting 0x200000000, which
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

BRANCH_INSTRUCTIONS = set([
    'OpReturnValue',
    'OpBranch',
    'OpBranchConditional',
    'OpReturn',
    'OpKill',
    'OpUnreachable',
    'OpSwitch'
])

# The instructions in the first part of the binary (before debug and
# annotation instructions).
INITIAL_INSTRUCTIONS = set([
    'OpSource',
    'OpSourceExtension',
    'OpCapability',
    'OpExtension',
    'OpExtInstImport',
    'OpMemoryModel',
    'OpEntryPoint',
    'OpExecutionMode'
])

DEBUG_INSTRUCTIONS = set([
    'OpString',
    'OpName',
    'OpMemberName',
    'OpLine',
])

DECORATION_INSTRUCTIONS = set([
    'OpDecorate',
    'OpMemberDecorate',
    'OpGroupDecorate',
    'OpGroupMemberDecorate',
    'OpDecorationGroup'
])

TYPE_DECLARATION_INSTRUCTIONS = set([
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
])

CONSTANT_INSTRUCTIONS = set([
    'OpConstantTrue',
    'OpConstantFalse',
    'OpConstant',
    'OpConstantComposite',
    'OpConstantSampler',
    'OpConstantNull',
])

SPECCONSTANT_INSTRUCTIONS = set([
    'OpSpecConstantTrue',
    'OpSpecConstantFalse',
    'OpSpecConstant',
    'OpSpecConstantComposite',
    'OpSpecConstantOp'
])

GLOBAL_VARIABLE_INSTRUCTIONS = set([
    'OpVariable'
])

_HAS_SIDE_EFFECT = set([
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

_IS_COMMUTATIVE = set([
    'OpLogicalAnd',
    'OpFAdd',
    'OpIMul',
    'OpBitwiseOr',
    'OpFMul',
    'OpBitwiseAnd',
    'OpLogicalOr',
    'OpBitwiseXor',
    'OpIAdd',
    'OpLogicalEqual',
    'OpLogicalNotEqual'
])
