import spirv

class IRError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Module(object):
    def __init__(self):
        self.bound = None

        self.id_to_instruction = {}

        self.type_declaration_instructions = []
        self.global_variable_instructions = []

        self.type_name_to_id = {}
        self.type_id_to_name = {}
        self.symbol_name_to_id = {}

        self.functions = []
        self.global_instructions = []

        self.internal_id_counter = 0

        self.id_to_name = {}

        # Only in output_id
        self.id_to_alias = {}
        self.alias_to_id = {}

    def instructions(self):
        """Iterate over all instructions in the module."""
        for instr in self.global_instructions:
            yield instr
        for function in self.functions:
            for instr in function.instructions():
                yield instr

    def get_new_id(self):
        self.internal_id_counter += 1
        return '%.' + str(self.internal_id_counter)

    def add_global_instruction(self, instr):
        if instr.op_name not in spirv.GLOBAL_INSTRUCTIONS:
            raise IRError(instr.op_name + ' is not a valid global instruction')

        self.global_instructions.append(instr)

        if instr.op_name in spirv.TYPE_DECLARATION_INSTRUCTIONS:
            self.add_type_name(instr)
            self.type_declaration_instructions.append(instr)
        elif instr.op_name in spirv.GLOBAL_VARIABLE_INSTRUCTIONS:
            self.global_variable_instructions.append(instr)

    def add_type_name(self, instr):
        if instr.op_name == 'OpTypeVoid':
            type_name = 'void'
        elif instr.op_name == 'OpTypeBool':
            type_name = 'bool'
        elif instr.op_name == 'OpTypeInt':
            width = instr.operands[0]
            signedness = instr.operands[1]

            if width not in ['8', '16', '32', '64']:
                raise IRError("Invalid OpTypeInt width " + width)
            if not signedness in ['0', '1']:
                error = "Invalid OpTypeInt signedness " + str(signedness)
                raise IRError(error)

            type_name = 's' if signedness else 'u'
            type_name = type_name + width
        elif instr.op_name == 'OpTypeFloat':
            width = instr.operands[0]
            if width not in ['16', '32', '64']:
                raise IRError("Invalid OpTypeFloat width " + width)
            type_name = 'f' + width
        elif instr.op_name == 'OpTypeVector':
            component_type = self.type_id_to_name[instr.operands[0]]
            count = instr.operands[1]
            if int(count) not in range(2, 16):
                error = "Invalid OpTypeVector component count " + str(count)
                raise IRError(error)
            type_name = '<' + str(count) + ' x ' + component_type + '>'
        else:
            type_name = instr.result_id

        self.type_name_to_id[type_name] = instr.result_id
        self.type_id_to_name[instr.result_id] = type_name

    def add_function(self, function):
        self.functions.append(function)

    def rename_id(self, id, rename):
        if id in rename:
            return rename[id]
        return id

    def rename_ids(self, instr, rename):
        instr.result_id = self.rename_id(instr.result_id, rename)
        instr.type = self.rename_id(instr.type, rename)
        for i in range(len(instr.operands)):
            instr.operands[i] = self.rename_id(instr.operands[i], rename)

    def calculate_bound(self):
        self.bound = 0
        for instr in self.instructions():
            if instr.result_id is not None:
                if instr.result_id[1].isdigit():
                    self.bound = max(self.bound, int(instr.result_id[1:]))
        self.bound += 1

    def find_named_ids(self):
        named_ids = []
        for instr in self.instructions():
            if instr.result_id is not None:
                if not instr.result_id[1].isdigit():
                    if not instr.result_id in named_ids:
                        named_ids.append(instr.result_id)
        return named_ids

    def finalize(self):
        # Determine ID bound.
        self.calculate_bound()

        # Create new numeric ID for the named IDs.
        named_ids = self.find_named_ids()
        id_rename = {}
        for id in named_ids:
            id_rename[id] = '%' + str(self.bound)
            self.bound += 1

        # Update all usage to use new numeric ID.
        for instr in self.instructions():
            self.rename_ids(instr, id_rename)

        # Rebuild mapping tables to get rid of obsolete entries.
        self.id_to_instruction = {}
        for instr in self.instructions():
            self.id_to_instruction[instr.result_id] = instr
        self.type_id_to_name = {}
        self.type_name_to_id = {}
        for instr in self.global_instructions:
            if instr.op_name in spirv.TYPE_DECLARATION_INSTRUCTIONS:
                self.add_type_name(instr)


class GlobalVariable(object):
    def __init__(self, name, type, storage_class, initializer=None):
        self.name = name
        self.type = type
        self.storage_class = storage_class
        self.initializer = initializer

    def __str__(self):
        line = self.name + ' = ' + self.storage_class
        line = line + " " + self.type
        if self.initializer is not None:
            line = line + self.initializer
        return line


class Function(object):
    def __init__(self, module, id, function_control, function_type_id):
        function_type_instr = module.id_to_instruction[function_type_id]
        self.module = module
        self.function_type_id = function_type_id
        self.argument_types = function_type_instr.operands[1:]
        self.function_control = function_control
        self.arguments = []
        self.basic_blocks = []
        self._def_instr = Instruction(self.module, 'OpFunction',
                                      id, function_type_instr.operands[0],
                                      [self.function_control,
                                       self.function_type_id])
        self._end_instr = Instruction(self.module, 'OpFunctionEnd',
                                      None, None, [])

    def get_id(self):
        return self._def_instr.result_id

    def get_return_type(self):
        return self._def_instr.type

    def instructions(self):
        """Iterate over all instructions in the function."""
        yield self._def_instr
        for instr in self.arguments:
            yield instr
        for basic_block in self.basic_blocks:
            for instr in basic_block.instructions():
                yield instr
        yield self._end_instr

    def add_argument(self, instr):
        self.arguments.append(instr)

    def add_basic_block(self, basic_block):
        self.basic_blocks.append(basic_block)


class BasicBlock(object):
    def __init__(self, function, id):
        self.function = function
        self.module = function.module
        self._instr = Instruction(self.module, 'OpLabel', id, None, [])
        self._instrs = []
        function.add_basic_block(self)

    def get_id(self):
        """Return basic block ID."""
        return self._instr.result_id

    def instructions(self):
        """Iterate over all instructions in the basic block."""
        yield self._instr
        for instr in self._instrs:
            yield instr

    def append(self, instr):
        """Add instruction at the end of the basic block."""
        instr.basic_block = self
        self._instrs.append(instr)

    def prepend(self, instr):
        """Add instruction at the top of the basic block."""
        instr.basic_block = self
        self._instrs = [instr] + self._instrs

    def insert_after(self, instr, existing_instr):
        """Add instruction after an existing instruction."""
        if not existing_instr in self._instrs:
            raise IRError('Instruction is not in basic block ' + self.get_id())
        idx = self._instrs.index(existing_instr)
        instr.basic_block = self
        self._instrs.insert(idx + 1, instr)

    def insert_before(self, instr, existing_instr):
        """Add instruction before an existing instruction."""
        if not existing_instr in self._instrs:
            raise IRError('Instruction is not in basic block ' + self.get_id())
        idx = self._instrs.index(existing_instr)
        instr.basic_block = self
        self._instrs.insert(idx, instr)


class Instruction(object):
    def __init__(self, module, op_name, result_id, type, operands):
        self.module = module
        self.op_name = op_name
        self.result_id = result_id
        self.type = type
        self.operands = operands
        self.basic_block = None
        if result_id is not None:
            self.module.id_to_instruction[self.result_id] = self
