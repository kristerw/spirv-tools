import spirv


class IRError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Module(object):
    def __init__(self):
        self.bound = None
        self.id_to_inst = {}
        self.functions = []
        self.global_insts = []
        self._tmp_id_counter = 0

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
        return '%.' + str(self._tmp_id_counter)

    def _copy_global_insts(self, output_array, names):
        for inst in self.global_insts:
            if inst.op_name in names:
                output_array.append(inst)

    def _sort_global_insts(self):
        sorted_insts = []
        for name in spirv.INITIAL_INSTRUCTIONS:
            self._copy_global_insts(sorted_insts, [name])
        self._copy_global_insts(sorted_insts,
                                spirv.DEBUG_INSTRUCTIONS)
        self._copy_global_insts(sorted_insts,
                                spirv.DECORATION_INSTRUCTIONS)
        self._copy_global_insts(sorted_insts,
                                spirv.TYPE_DECLARATION_INSTRUCTIONS)
        self._copy_global_insts(sorted_insts,
                                spirv.CONSTANT_INSTRUCTIONS)
        self._copy_global_insts(sorted_insts,
                                spirv.GLOBAL_VARIABLE_INSTRUCTIONS)
        self.global_insts = sorted_insts

    def add_global_inst(self, inst):
        """Add instruction to the module's global instructions."""
        if inst.op_name not in spirv.GLOBAL_INSTRUCTIONS:
            raise IRError(inst.op_name + ' is not a valid global instruction')
        self.global_insts.append(inst)
        self._sort_global_insts()

    def add_function(self, function):
        """Add function to the module."""
        self.functions.append(function)

    def get_constant(self, type_id, value):
        """Get a constant with the provided value and type.

        The constant is created if not already existing.
        For vector types, the value need to be a list of the same length
        as the vector size, or a scalar, in which case the value is
        replicated for all elements."""
        type_inst = self.id_to_inst[type_id]
        if (type_inst.op_name == 'OpTypeInt' or
                type_inst.op_name == 'OpTypeFloat'):
            for inst in self.global_insts:
                if (inst.op_name == 'OpConstant' and
                        inst.type_id == type_inst.result_id and
                        inst.operands[0] == str(value)):
                    return inst
            inst = Instruction(self, 'OpConstant', self.new_id(),
                               type_inst.result_id, [str(value)])
            self.add_global_inst(inst)
            return inst
        elif type_inst.op_name == 'OpTypeVector':
            nof_elements = int(type_inst.operands[1])
            if not isinstance(value, (list, tuple)):
                value = [value] * nof_elements
            operands = []
            for elem in value:
                instr = self.get_constant(type_inst.operands[0], elem)
                operands.append(instr.result_id)
            for inst in self.global_insts:
                if (inst.op_name == 'OpConstantComposite' and
                        inst.type_id == type_inst.result_id and
                        lists_are_identical(inst.operands, operands)):
                    return inst
            inst = Instruction(self, 'OpConstantComposite', self.new_id(),
                               type_inst.result_id, operands)
            self.add_global_inst(inst)
            return inst
        else:
            raise IRError('Invalid type for constant')

    def finalize(self):
        # Determine ID bound.
        self.bound = 0
        for inst in self.instructions():
            if (inst.result_id is not None and
                    inst.result_id[1].isdigit()):
                self.bound = max(self.bound, int(inst.result_id[1:]))
        self.bound += 1

        # Create new numeric IDs for the named IDs.
        named_ids = []
        for inst in self.instructions():
            if (inst.result_id is not None and
                    not inst.result_id[1].isdigit() and
                    not inst.result_id in named_ids):
                named_ids.append(inst.result_id)
        id_rename = {}
        for named_id in named_ids:
            id_rename[named_id] = '%' + str(self.bound)
            self.bound += 1

        # Update all uses of named IDs to use the new numeric IDs.
        for inst in self.instructions():
            if inst.result_id in id_rename:
                inst.result_id = id_rename[inst.result_id]
            if inst.type_id in id_rename:
                inst.type_id = id_rename[inst.type_id]
            for i in range(len(inst.operands)):
                if inst.operands[i] in id_rename:
                    inst.operands[i] = id_rename[inst.operands[i]]

        # Rebuild mapping table to get rid of obsolete entries.
        self.id_to_inst = {}
        for inst in self.instructions():
            self.id_to_inst[inst.result_id] = inst


class Function(object):
    def __init__(self, module, function_id, function_control, function_type_id):
        function_type_inst = module.id_to_inst[function_type_id]
        self.module = module
        self.arguments = []
        self.basic_blocks = []
        self.inst = Instruction(self.module, 'OpFunction',
                                function_id, function_type_inst.operands[0],
                                [function_control, function_type_id])
        self.end_inst = Instruction(self.module, 'OpFunctionEnd',
                                    None, None, [])

    def instructions(self):
        """Iterate over all instructions in the function."""
        yield self.inst
        for inst in self.arguments[:]:
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
        for inst in reversed(self.arguments[:]):
            yield inst
        yield self.inst

    def append_argument(self, inst):
        """Append argument to the arguments list."""
        self.arguments.append(inst)

    def add_basic_block(self, basic_block):
        """Add one basic block to the function."""
        self.basic_blocks.append(basic_block)
        basic_block.function = self


class BasicBlock(object):
    def __init__(self, module, label_id):
        self.function = None
        self.module = module
        self.inst = Instruction(self.module, 'OpLabel', label_id, None, [])
        self.inst.basic_block = self
        self.insts = []

    def append_inst(self, inst):
        """Add instruction at the end of the basic block."""
        inst.basic_block = self
        self.insts.append(inst)

    def prepend_inst(self, inst):
        """Add instruction at the top of the basic block."""
        inst.basic_block = self
        self.insts = [inst] + self.insts

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
        if result_id is not None:
            self.module.id_to_inst[self.result_id] = self

    def __str__(self):
        res = ''
        if self.result_id is not None:
            res = res + self.result_id + ' = '
        res = res + self.op_name
        if self.type_id is not None:
            res = res + ' ' + self.type_id
        if self.operands:
            res = res + ' '
            for operand in self.operands:
                res = res + operand + ', '
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
        basic_block = insert_pos_inst.basic_block
        if basic_block is None:
            raise IRError('Instruction is not in basic block')
        idx = basic_block.insts.index(insert_pos_inst)
        self.basic_block = basic_block
        basic_block.insts.insert(idx + 1, self)

    def insert_before(self, insert_pos_inst):
        """Add instruction before an existing instruction."""
        basic_block = insert_pos_inst.basic_block
        if basic_block is None:
            raise IRError('Instruction is not in basic block')
        idx = basic_block.insts.index(insert_pos_inst)
        self.basic_block = basic_block
        basic_block.insts.insert(idx, self)

    def remove(self):
        """Remove instruction from basic block or global instruction list.

        The instruction's debug and decoration instructions are unaffected,
        so that it is possible to re-insert the instruction again."""
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
        for inst in self.module.global_insts[:]:
            if (inst.op_name in spirv.DECORATION_INSTRUCTIONS or
                    inst.op_name in spirv.DEBUG_INSTRUCTIONS):
                if self.result_id in inst.operands:
                    inst.destroy()
        if self.basic_block is None:
            if self not in self.module.global_insts:
                raise IRError('Instruction is not in basic block or module')
            self.module.global_insts.remove(self)
            return
        self.basic_block.insts.remove(self)
        if self.result_id is not None:
            del self.module.id_to_inst[self.result_id]
        self.basic_block = None
        self.op_name = None
        self.result_id = None
        self.type_id = None
        self.operands = None

    def is_using(self, inst):
        """Return True if this instruction is using the instruction.

        Debug and decoration instructions are not considered using
        any instruction."""
        if self.op_name in spirv.DECORATION_INSTRUCTIONS:
            return False
        if self.op_name in spirv.DEBUG_INSTRUCTIONS:
            return False
        if self.type_id == inst.result_id:
            return True
        for operand in self.operands:
            if operand == inst.result_id:
                return True
        return False

    def uses(self):
        """Return all instructions using this instructions.

        Debug and decoration instructions are not considered using
        any instruction."""
        uses = []
        for inst in self.module.instructions():
            if inst.is_using(self):
                uses.append(inst)
        return uses

    def replace_uses_with(self, new_inst):
        """Replace all uses of this instruction with new_inst.

        Decoration and debug instructions are not updated, as they are
        considered being a part of the instruction they reference."""
        for inst in self.module.instructions():
            if inst.op_name in spirv.DECORATION_INSTRUCTIONS:
                continue
            if inst.op_name in spirv.DEBUG_INSTRUCTIONS:
                continue
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
        if self.type_id == old_inst.result_id:
            self.type_id = new_inst.result_id
        for idx in range(len(self.operands)):
            if self.operands[idx] == old_inst.result_id:
                self.operands[idx] = new_inst.result_id

    def has_side_effect(self):
        """True if the instruction may be removed if unused."""
        # XXX Need to handle OpExtInst correctly (it is conservative now)
        if self.result_id is None:
            return True
        return self.op_name in spirv.HAS_SIDE_EFFECT

    def copy_decorations(self, src_inst):
        """Copy the decorations from src_inst to this instruction."""
        for inst in self.module.instructions():
            if (inst.op_name in spirv.DECORATION_INSTRUCTIONS and
                    inst.op_name != 'OpDecorationGroup' and
                    inst.operands[0] == src_inst.result_id):
                new_operands = inst.operands[:]
                new_operands[0] = self.result_id
                new_inst = Instruction(self.module, inst.op_name,
                                       None, None, new_operands)
                self.module.add_global_inst(new_inst)


def lists_are_identical(list1, list2):
    """Return True if the lists are identical."""
    if len(list1) != len(list2):
        return False
    for elem1, elem2 in zip(list1, list2):
        if elem1 != elem2:
            return False
    return True
