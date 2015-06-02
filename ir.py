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
        """Iterate in reversed order over all instructions in the module."""
        for function in reversed(self.functions[:]):
            for instr in function.instructions_reversed():
                yield instr
        for instr in reversed(self.global_instrs[:]):
            yield instr

    def new_id(self):
        """Generate a new ID."""
        self._tmp_id_counter += 1
        return '%.' + str(self._tmp_id_counter)

    def copy_global_instrs(self, output_array, names):
        for instr in self.global_instrs:
            if instr.op_name in names:
                output_array.append(instr)

    def sort_global_instrs(self):
        sorted_instrs = []
        for name in spirv.INITIAL_INSTRUCTIONS:
            self.copy_global_instrs(sorted_instrs, [name])
        self.copy_global_instrs(sorted_instrs,
                                spirv.DEBUG_INSTRUCTIONS)
        self.copy_global_instrs(sorted_instrs,
                                spirv.DECORATION_INSTRUCTIONS)
        self.copy_global_instrs(sorted_instrs,
                                spirv.TYPE_DECLARATION_INSTRUCTIONS)
        self.copy_global_instrs(sorted_instrs,
                                spirv.CONSTANT_INSTRUCTIONS)
        self.copy_global_instrs(sorted_instrs,
                                spirv.GLOBAL_VARIABLE_INSTRUCTIONS)
        self.global_instrs = sorted_instrs

    def add_global_instr(self, instr):
        """Add instruction to the module's global instructions."""
        if instr.op_name not in spirv.GLOBAL_INSTRUCTIONS:
            raise IRError(instr.op_name + ' is not a valid global instruction')
        self.global_instrs.append(instr)
        self.sort_global_instrs()

    def add_function(self, function):
        """Add function to the module."""
        self.functions.append(function)

    def finalize(self):
        # Determine ID bound.
        self.bound = 0
        for instr in self.instructions():
            if instr.result_id is not None:
                if instr.result_id[1].isdigit():
                    self.bound = max(self.bound, int(instr.result_id[1:]))
        self.bound += 1

        # Create new numeric IDs for the named IDs.
        named_ids = []
        for instr in self.instructions():
            if instr.result_id is not None:
                if not instr.result_id[1].isdigit():
                    if not instr.result_id in named_ids:
                        named_ids.append(instr.result_id)
        id_rename = {}
        for named_id in named_ids:
            id_rename[named_id] = '%' + str(self.bound)
            self.bound += 1

        # Update all usage of named IDs to use the new numeric IDs.
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
                                 [function_control,
                                  function_type_id])
        self.end_instr = Instruction(self.module, 'OpFunctionEnd',
                                     None, None, [])

    def instructions(self):
        """Iterate over all instructions in the function."""
        yield self.instr
        for instr in self.arguments[:]:
            yield instr
        for basic_block in self.basic_blocks[:]:
            yield basic_block.instr
            for instr in basic_block.instrs[:]:
                yield instr
        yield self.end_instr

    def instructions_reversed(self):
        """Iterate in reversed order over all instructions in the function."""
        yield self.end_instr
        for basic_block in reversed(self.basic_blocks[:]):
            for instr in reversed(basic_block.instrs[:]):
                yield instr
            yield basic_block.instr
        for instr in reversed(self.arguments[:]):
            yield instr
        yield self.instr

    def append_argument(self, instr):
        self.arguments.append(instr)

    def add_basic_block(self, basic_block):
        self.basic_blocks.append(basic_block)


class BasicBlock(object):
    def __init__(self, function, id):
        self.function = function
        self.module = function.module
        self.instr = Instruction(self.module, 'OpLabel', id, None, [])
        self.instrs = []
        function.add_basic_block(self)

    def append_instr(self, instr):
        """Add instruction at the end of the basic block."""
        instr.basic_block = self
        self.instrs.append(instr)

    def prepend_instr(self, instr):
        """Add instruction at the top of the basic block."""
        instr.basic_block = self
        self.instrs = [instr] + self.instrs


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
        """Remove instruction from basic block."""
        if self.basic_block is None:
            raise IRError('Instruction is not in basic block')
        self.basic_block.instrs.remove(self)
