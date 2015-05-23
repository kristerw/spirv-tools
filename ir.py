import spirv

class Module(object):
    def __init__(self):
        self.bound = None

        self.id_to_instruction = {}

        self.initial_instructions = []
        self.debug_instructions = []
        self.decoration_instructions = []
        self.type_declaration_instructions = []
        self.constant_instructions = []
        self.global_variable_instructions = []

        self.type_name_to_id = {}
        self.type_id_to_name = {}
        self.symbol_name_to_id = {}

        self.functions = []
        self.instructions = []

        self.internal_id_counter = 0

        self.id_to_name = {}

        # Only in output_id
        self.id_to_alias = {}
        self.alias_to_id = {}

    def get_new_id(self):
        self.internal_id_counter += 1
        return '%.' + str(self.internal_id_counter)

    def add_global_instruction(self, instr):
        self.instructions.append(instr)
        if instr.result_id is not None:
            self.id_to_instruction[instr.result_id] = instr

        if instr.name in spirv.INITIAL_INSTRUCTIONS:
            self.initial_instructions.append(instr)
        elif instr.name in spirv.DEBUG_INSTRUCTIONS:
            self.debug_instructions.append(instr)
        elif instr.name in spirv.DECORATION_INSTRUCTIONS:
            self.decoration_instructions.append(instr)
        elif instr.name in spirv.TYPE_DECLARATION_INSTRUCTIONS:
            self.add_type_name(instr)
            self.type_declaration_instructions.append(instr)
        elif instr.name in spirv.CONSTANT_INSTRUCTIONS:
            self.constant_instructions.append(instr)
        elif instr.name in spirv.GLOBAL_VARIABLE_INSTRUCTIONS:
            self.global_variable_instructions.append(instr)
        else:
            raise Exception("Unknown global instruction: " + instr.name)

    def add_type_name(self, instr):
        if instr.name == 'OpTypeVoid':
            type_name = 'void'
        elif instr.name == 'OpTypeBool':
            type_name = 'bool'
        elif instr.name == 'OpTypeInt':
            width = instr.operands[0]
            signedness = instr.operands[1]

            if width not in ['8', '16', '32', '64']:
                raise Exception("Invalid OpTypeInt width " + width)
            if not signedness in ['0', '1']:
                error = "Invalid OpTypeInt signedness " + str(signedness)
                raise Exception(error)

            type_name = 's' if signedness else 'u'
            type_name = type_name + width
        elif instr.name == 'OpTypeFloat':
            width = instr.operands[0]
            if width not in ['16', '32', '64']:
                raise Exception("Invalid OpTypeFloat width " + width)
            type_name = 'f' + width
        elif instr.name == 'OpTypeVector':
            component_type = self.type_id_to_name[instr.operands[0]]
            count = instr.operands[1]
            if int(count) not in range(2, 16):
                error = "Invalid OpTypeVector component count " + str(count)
                raise Exception(error)
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

    def calculate_bound_helper(self, instr, named_ids):
        if instr.result_id is not None:
            if instr.result_id[1].isdigit():
                self.bound = max(self.bound, int(instr.result_id[1:]))
            else:
                if not instr.result_id in named_ids:
                    named_ids.append(instr.result_id)

    def calculate_bound(self):
        named_ids = []
        self.bound = 0
        for function in self.functions:
            for basic_block in function.basic_blocks:
                for instr in basic_block.instrs:
                    self.calculate_bound_helper(instr, named_ids)
        for instr in self.instructions:
            self.calculate_bound_helper(instr, named_ids)
        for arg in function.arguments:
            self.calculate_bound_helper(instr, named_ids)
        self.bound += 1
        return named_ids

    def finalize(self):
        all_instructions = []
        for id in self.id_to_instruction:
            all_instructions.append(self.id_to_instruction[id])
        for instr in self.instructions:
            if not instr in all_instructions:
                all_instructions.append(instr)

        # Determine ID bound, and collcet named IDs that need to be changed
        # to numeric names.
        named_ids = self.calculate_bound()
        for function in self.functions:
            if not function.name[1].isdigit():
                named_ids.append(function.name)

        # Create new numric ID name for the named IDs.
        id_rename = {}
        for id in named_ids:
            id_rename[id] = '%' + str(self.bound)
            self.bound += 1

        # Update all usage to use new numeric ID name
        for instr in all_instructions:
            self.rename_ids(instr, id_rename)
        for function in self.functions:
            function.name = self.rename_id(function.name, id_rename)
            function.return_type = self.rename_id(function.return_type, id_rename)
            function.function_type_id = self.rename_id(function.function_type_id, id_rename)
            for i in range(len(function.arguments)):
                function.arguments[i] = self.rename_id(function.arguments[i],
                                                       id_rename)
            for basic_block in function.basic_blocks:
                for instr in basic_block.instrs:
                    self.rename_ids(instr, id_rename)

        # Delete old names.
        for id in id_rename:
            if id in self.type_id_to_name:
                name = self.type_id_to_name[id]
                self.type_id_to_name[id_rename[id]] = name
                self.type_name_to_id[name] = id_rename[id]

            if id in self.id_to_instruction:
                self.id_to_instruction[id_rename[id]] = self.id_to_instruction[id]
                del self.id_to_instruction[id]


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
    def __init__(self, module, name, function_control, function_type_id):
        function_type_instr = module.id_to_instruction[function_type_id]
        self.function_type_id = function_type_id
        self.name = name
        self.return_type = function_type_instr.operands[0]
        self.argument_types = function_type_instr.operands[1:]
        self.function_control = function_control
        self.arguments = []
        self.basic_blocks = []

    def add_basic_block(self, basic_block):
        self.basic_blocks.append(basic_block)


class BasicBlock(object):
    def __init__(self, name):
        self.name = name
        self.instrs = []


class Instruction(object):
    def __init__(self, name, result_id, type, operands):
        self.name = name
        self.result_id = result_id
        self.type = type
        self.operands = operands
