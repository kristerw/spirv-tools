import array

import spirv
import ir


class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class SpirvBinary(object):
    def __init__(self, words):
        magic = words[0]
        if magic != spirv.MAGIC:
            words.byteswap()
            magic = words[0]
            if magic != spirv.MAGIC:
                raise ParseError('Incorrect magic: ' + format(magic, '#x'))

        version = words[1]
        if version != spirv.VERSION:
            raise ParseError('Unknown version ' + str(version))

        self.words = words
        self.idx = 5
        self.length = 0

    def discard_inst(self):
        self.idx += self.words[self.idx] >> 16

    def get_next_opcode(self, peek=False, throw_on_eol=False):
        if not throw_on_eol:
            if self.idx == len(self.words):
                return None

        opcode = self.words[self.idx] & 0xFFFF
        self.length = (self.words[self.idx] >> 16) - 1

        if not peek:
            self.idx += 1

        if opcode not in spirv.OPCODE_TABLE:
            raise ParseError('Invalid opcode ' + str(opcode))

        return spirv.OPCODE_TABLE[opcode]

    def get_next_word(self, peek=False, throw_on_eol=True):
        if not throw_on_eol:
            if self.length == 0:
                return None

        if self.length == 0:
            raise ParseError('Incorrect length')

        word = self.words[self.idx]

        if not peek:
            self.idx += 1
            self.length -= 1

        return word

    def expect_eol(self):
        if self.length != 0:
            raise ParseError('Spurius words after parsing instruction')


def parse_literal_string(binary):
    """parse one LiteralString."""
    result = []
    while True:
        word = binary.get_next_word()
        for _ in range(4):
            octet = word & 255
            if octet == 0:
                return ''.join(result).decode('utf-8')
            result.append(chr(octet))
            word >>= 8
    raise ParseError('bad encoding')


def parse_id(binary):
    """parse one Id."""
    return '%' + str(binary.get_next_word())


def parse_operand(binary, kind):
    """Parse one instruction operand."""
    if kind == 'Id':
        return [parse_id(binary)]
    elif kind == 'LiteralNumber' or kind == 'FunctionControlMask':
        return [binary.get_next_word()]
    elif kind == 'LiteralString':
        return ['"' + parse_literal_string(binary) + '"']
    elif kind == 'VariableLiterals' or kind == 'OptionalLiteral' :
        operands = []
        while True:
            word = binary.get_next_word(throw_on_eol=False)
            if word is None:
                return operands
            operands.append(word)
    elif kind == 'VariableIds' or kind == 'OptionalId':
        operands = []
        while True:
            word = binary.get_next_word(throw_on_eol=False)
            if word is None:
                return operands
            operands.append('%' + str(word))
    elif kind in spirv.CONSTANTS:
        val = binary.get_next_word()
        constants = spirv.CONSTANTS[kind]
        for name in constants:
            if constants[name] == val:
                return [name]
        raise ParseError('Unknown "' + kind + '" value' + str(val))
    elif kind in spirv.MASKS:
        val = binary.get_next_word()
        return [val]

    raise ParseError('Unknown kind "' + kind + '"')


def parse_instruction(binary, module):
    """Parse one instruction."""
    opcode = binary.get_next_opcode()
    operands = []
    inst_type = None
    if opcode['type']:
        inst_type = parse_id(binary)
    result = None
    if opcode['result']:
        result = parse_id(binary)
    for kind in opcode['operands']:
        operands = operands + parse_operand(binary, kind)
    binary.expect_eol()

    if opcode['name'] == 'OpFunction':
        return ir.Function(module, result, operands[0], operands[1])
    else:
        return ir.Instruction(module, opcode['name'], result, inst_type,
                              operands)


def parse_global_instructions(binary, module):
    """Parse all global instructions (i.e. up to the first function). """
    while True:
        opcode = binary.get_next_opcode(peek=True)
        if opcode is None:
            return
        if opcode['name'] == 'OpFunction':
            return

        inst = parse_instruction(binary, module)
        module.add_global_inst(inst)


def parse_basic_block(binary, module, function):
    """Parse one basic block."""
    opcode = binary.get_next_opcode()
    basic_block_id = str(parse_id(binary))
    binary.expect_eol()
    basic_block = ir.BasicBlock(module, basic_block_id)

    while True:
        opcode = binary.get_next_opcode(peek=True)
        inst = parse_instruction(binary, module)
        basic_block.append_inst(inst)
        if opcode['name'] in spirv.BASIC_BLOCK_ENDING_INSTRUCTIONS:
            function.add_basic_block(basic_block)
            return


def parse_function(binary, module):
    """Parse one function."""
    function = parse_instruction(binary, module)

    while True:
        opcode = binary.get_next_opcode(peek=True)
        if opcode['name'] == 'OpLabel':
            parse_basic_block(binary, module, function)
        elif opcode['name'] == 'OpFunctionEnd':
            binary.discard_inst()
            return function
        elif opcode['name'] == 'OpFunctionParameter':
            inst = parse_instruction(binary, module)
            function.append_argument(inst)
        else:
            raise ParseError('Invalid opcode ' + opcode['name'])


def parse_functions(binary, module):
    """Parse all functions (i.e. rest of the module)."""
    while True:
        opcode = binary.get_next_opcode(peek=True, throw_on_eol=False)
        if opcode is None:
            return
        if opcode['name'] != 'OpFunction':
            raise ParseError('Expected an "OpFunction" instruction')

        function = parse_function(binary, module)
        module.add_function(function)


def read_module(stream):
    words = array.array('L', stream.read())
    binary = SpirvBinary(words)

    module = ir.Module()
    parse_global_instructions(binary, module)
    parse_functions(binary, module)

    module.finalize()
    return module
