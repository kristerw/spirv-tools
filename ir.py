import spirv


class IRError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Module(object):
    def __init__(self):
        self.bound = None
        self.id_to_instr = {}
        self.functions = []
        self.global_instrs = []
        self._tmp_id_counter = 0

    def instructions(self):
        """Iterate over all instructions in the module."""
        for instr in self.global_instrs[:]:
            yield instr
        for function in self.functions[:]:
            for instr in function.instructions():
                yield instr

    def instructions_reversed(self):
        """Iterate in reverse order over all instructions in the module."""
        for function in reversed(self.functions[:]):
            for instr in function.instructions_reversed():
                yield instr
        for instr in reversed(self.global_instrs[:]):
            yield instr

    def new_id(self):
        """Generate a new ID."""
        self._tmp_id_counter += 1
        return '%.' + str(self._tmp_id_counter)

    def _copy_global_instrs(self, output_array, names):
        for instr in self.global_instrs:
            if instr.op_name in names:
                output_array.append(instr)

    def _sort_global_instrs(self):
        sorted_instrs = []
        for name in spirv.INITIAL_INSTRUCTIONS:
            self._copy_global_instrs(sorted_instrs, [name])
        self._copy_global_instrs(sorted_instrs,
                                 spirv.DEBUG_INSTRUCTIONS)
        self._copy_global_instrs(sorted_instrs,
                                 spirv.DECORATION_INSTRUCTIONS)
        self._copy_global_instrs(sorted_instrs,
                                 spirv.TYPE_DECLARATION_INSTRUCTIONS)
        self._copy_global_instrs(sorted_instrs,
                                 spirv.CONSTANT_INSTRUCTIONS)
        self._copy_global_instrs(sorted_instrs,
                                 spirv.GLOBAL_VARIABLE_INSTRUCTIONS)
        self.global_instrs = sorted_instrs

    def add_global_instr(self, instr):
        """Add instruction to the module's global instructions."""
        if instr.op_name not in spirv.GLOBAL_INSTRUCTIONS:
            raise IRError(instr.op_name + ' is not a valid global instruction')
        self.global_instrs.append(instr)
        self._sort_global_instrs()

    def add_function(self, function):
        """Add function to the module."""
        self.functions.append(function)

    def finalize(self):
        # Determine ID bound.
        self.bound = 0
        for instr in self.instructions():
            if (instr.result_id is not None and
                instr.result_id[1].isdigit()):
                self.bound = max(self.bound, int(instr.result_id[1:]))
        self.bound += 1

        # Create new numeric IDs for the named IDs.
        named_ids = []
        for instr in self.instructions():
            if (instr.result_id is not None and
                not instr.result_id[1].isdigit() and
                not instr.result_id in named_ids):
                named_ids.append(instr.result_id)
        id_rename = {}
        for named_id in named_ids:
            id_rename[named_id] = '%' + str(self.bound)
            self.bound += 1

        # Update all uses of named IDs to use the new numeric IDs.
        for instr in self.instructions():
            if instr.result_id in id_rename:
                instr.result_id = id_rename[instr.result_id]
            if instr.type in id_rename:
                instr.type = id_rename[instr.type]
            for i in range(len(instr.operands)):
                if instr.operands[i] in id_rename:
                    instr.operands[i] = id_rename[instr.operands[i]]

        # Rebuild mapping table to get rid of obsolete entries.
        self.id_to_instr = {}
        for instr in self.instructions():
            self.id_to_instr[instr.result_id] = instr


class Function(object):
    def __init__(self, module, id, function_control, function_type_id):
        function_type_instr = module.id_to_instr[function_type_id]
        self.module = module
        self.arguments = []
        self.basic_blocks = []
        self.instr = Instruction(self.module, 'OpFunction',
                                 id, function_type_instr.operands[0],
                                 [function_control, function_type_id])
        self.end_instr = Instruction(self.module, 'OpFunctionEnd',
                                     None, None, [])

    def instructions(self):
        """Iterate over all instructions in the function."""
        yield self.instr
        for instr in self.arguments[:]:
            yield instr
        for basic_block in self.basic_blocks[:]:
            if basic_block.function is not None:
                yield basic_block.instr
                for instr in basic_block.instrs[:]:
                    yield instr
        yield self.end_instr

    def instructions_reversed(self):
        """Iterate in reverse order over all instructions in the function."""
        yield self.end_instr
        for basic_block in reversed(self.basic_blocks[:]):
            if basic_block.function is not None:
                for instr in reversed(basic_block.instrs[:]):
                    yield instr
                yield basic_block.instr
        for instr in reversed(self.arguments[:]):
            yield instr
        yield self.instr

    def append_argument(self, instr):
        self.arguments.append(instr)

    def append_basic_block(self, basic_block):
        self.basic_blocks.append(basic_block)
        basic_block.function = self


class BasicBlock(object):
    def __init__(self, module, id):
        self.function = None
        self.module = module
        self.instr = Instruction(self.module, 'OpLabel', id, None, [])
        self.instrs = []

    def append_instr(self, instr):
        """Add instruction at the end of the basic block."""
        instr.basic_block = self
        self.instrs.append(instr)

    def prepend_instr(self, instr):
        """Add instruction at the top of the basic block."""
        instr.basic_block = self
        self.instrs = [instr] + self.instrs

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
        for instr in reversed(self.instrs[:]):
            uses = instr.uses()
            for tmp_instr in uses:
                if tmp_instr.op_name != 'OpPhi':
                    IRError('Instruction is used in other basic block')
                IRError('Need to remove from phi node') # XXX
            instr.remove()
        self.module = None


class Instruction(object):
    def __init__(self, module, op_name, result_id, type, operands):
        self.module = module
        self.op_name = op_name
        self.result_id = result_id
        self.type = type
        self.operands = operands
        self.basic_block = None
        if result_id is not None:
            self.module.id_to_instr[self.result_id] = self

    def clone(self):
        """Create a copy of the instruction.

        The new instruction is identical to this instruction, except that
        it has a new result_id (if the instruction type has a result_id),
        and it is not bound to any basic block."""
        if self.result_id is not None:
            new_id = self.module.new_id()
        else:
            new_id = None
        return Instruction(self.module, self.op_name, new_id, self.type,
                           self.operands[:])

    def insert_after(self, insert_pos_instr):
        """Add instruction after an existing instruction."""
        basic_block = insert_pos_instr.basic_block
        if basic_block is None:
            raise IRError('Instruction is not in basic block')
        idx = basic_block.instrs.index(insert_pos_instr)
        self.basic_block = basic_block
        basic_block.instrs.insert(idx + 1, self)

    def insert_before(self, insert_pos_instr):
        """Add instruction before an existing instruction."""
        basic_block = insert_pos_instr.basic_block
        if basic_block is None:
            raise IRError('Instruction is not in basic block')
        idx = basic_block.instrs.index(insert_pos_instr)
        self.basic_block = basic_block
        basic_block.instrs.insert(idx, self)

    def remove(self):
        """Remove instruction from basic block or global instruction list."""
        if self.basic_block is None:
            if self not in self.module.global_instrs:
                raise IRError('Instruction is not in basic block or module')
            self.module.global_instrs.remove(self)
            return
        self.basic_block.instrs.remove(self)
        self.basic_block = None

    def is_using(self, instr):
        """Return True if this instruction is using the instruction.

        Debug and decoration instructions are not considered using
        any instruction."""
        if self.op_name in spirv.DECORATION_INSTRUCTIONS:
            return False
        if self.op_name in spirv.DEBUG_INSTRUCTIONS:
            return False
        if self.type == instr.result_id:
            return True
        for operand in self.operands:
            if operand == instr.result_id:
                return True
        return False

    def uses(self):
        """Return all instructions using this instructions.

        Debug and decoration instructions are not considered using
        any instruction."""
        uses = []
        for instr in self.module.instructions():
            if instr.is_using(self):
                uses.append(instr)
        return uses

    def replace_uses_with(module, new_instr):
        """Replace all uses of this instruction with new_instr.

        Decoration and debug instructions are not updated, as they are
        considered being a part of the instruction they reference."""
        for instr in module.instructions():
            if instr.op_name in spirv.DECORATION_INSTRUCTIONS:
                continue
            if instr.op_name in spirv.DEBUG_INSTRUCTIONS:
                continue
            instr.substitute_type_and_operands(self, new_instr)

    def replace_with(self, new_instr):
        """Replace this instruction with new_instr.

        All uses of this instruction is replaced by new_instr, the
        new_instr is inserted in the location of this instruction,
        and this instruction is removed."""
        new_instr.insert_after(self)
        self.replace_uses_with(new_instr)
        self.remove()

    def substitute_type_and_operands(self, old_instr, new_instr):
        """Change use of old_instr in this instruction to new_instr."""
        if self.type == old_instr.result_id:
            self.type = new_instr.result_id
        for idx in range(len(self.operands)):
            if self.operands[idx] == old_instr.result_id:
                self.operands[idx] = new_instr.result_id

    def has_side_effect(self):
        """True if the instruction may be removed if unused."""
        # XXX Need to handle OpExtInst correctly (it is convervative now)
        # XXX Global instructions are a bit special, so they are always
        #     considered having side effects for now.
        if self.op_name in spirv.GLOBAL_INSTRUCTIONS:
            return True
        if self.result_id is None:
            return True
        return self.op_name in spirv.HAS_SIDE_EFFECT

    def copy_decorations(self, src_instr):
        """Copy the decorations from src_instr to this instruction."""
        for instr in self.module.instructions():
            if (instr.op_name in spirv.DECORATION_INSTRUCTIONS and
                instr.op_name != 'OpDecorationGroup' and
                instr.operamds[0] == src_instr.result_id):
                new_operands = instr.operands[:]
                new_operands[0] = self.result_id
                new_instr = Instruction(self.module, instr.op_name,
                                        None, None,
                                        new_operands)
                self.module.add_global_instr(new_instr)
