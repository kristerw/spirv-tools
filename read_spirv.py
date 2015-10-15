import array
from operator import itemgetter

import spirv
import ir


class ParseError(Exception):
    def __init__(self, message):
        super(ParseError, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class SpirvBinary(object):
    def __init__(self, words):
        if len(words) < 5:
            raise ParseError('File length shorter than header size')
        magic = words[0]
        if magic != ir.MAGIC:
            words.byteswap()
            magic = words[0]
            if magic != ir.MAGIC:
                raise ParseError('Incorrect magic: ' + format(magic, '#x'))

        version = words[1]
        if version != ir.VERSION:
            raise ParseError('Unknown version ' + str(version))

        self.words = words
        self.idx = 5
        self.length = 0

    def discard_inst(self):
        self.idx += self.words[self.idx] >> 16
        # Ensure we do not read past end of file (i.e. if the instruction's
        # length field is corrupt).  It is OK for idx to point to the word
        # after the binary (which happens if we discard the last instruction
        # in the file).
        if self.idx > len(self.words):
            raise ParseError('Unexpected end of file')

    def get_next_opcode(self, peek=False, throw_on_eol=False):
        if self.idx == len(self.words):
            if throw_on_eol:
                raise ParseError('Unexpected end of file')
            else:
                return None, None

        opcode = self.words[self.idx] & 0xFFFF
        self.length = (self.words[self.idx] >> 16) - 1

        if not peek:
            self.idx += 1

        if opcode not in ir.OPCODE_TO_OPNAME:
            raise ParseError('Invalid opcode ' + str(opcode))

        op_name = ir.OPCODE_TO_OPNAME[opcode]
        return op_name, ir.INST_FORMAT[op_name]

    def get_next_word(self, peek=False, throw_on_eol=True):
        if self.idx == len(self.words):
            if throw_on_eol:
                raise ParseError('Unexpected end of file')
            else:
                return None

        if self.length == 0:
            if throw_on_eol:
                raise ParseError('Incorrect instruction length')
            else:
                return None

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


def parse_id(binary, module):
    """parse one Id."""
    return module.get_id(binary.get_next_word())


def expand_mask(kind, value):
    """Convert the mask to a list of mask strings."""
    result = []
    if value != 0:
        mask_values = zip(spirv.spv[kind].values(), spirv.spv[kind].keys())
        mask_values = sorted(mask_values, key=itemgetter(0))
        for mask_number, mask_token in mask_values:
            if (mask_number & value) != 0:
                result.append(mask_token)
                value = value ^ mask_number
        if value != 0:
            raise ParseError('Invalid mask value')
    return result


def parse_operand(binary, module, kind):
    """Parse one instruction operand."""
    if kind == 'Id':
        return [parse_id(binary, module)]
    elif kind == 'LiteralNumber':
        return [binary.get_next_word()]
    elif kind == 'LiteralString':
        return [parse_literal_string(binary)]
    elif kind == 'VariableLiterals' or kind == 'OptionalLiteral':
        operands = []
        while True:
            word = binary.get_next_word(throw_on_eol=False)
            if word is None:
                return operands
            operands.append(word)
    elif kind == 'OptionalImage':
        operands = []
        word = binary.get_next_word(throw_on_eol=False)
        if word is None:
            return operands
        operands.append(word)
        while True:
            word = binary.get_next_word(throw_on_eol=False)
            if word is None:
                return operands
            operands.append(module.get_id(word))
    elif kind in ['VariableIds', 'OptionalId']:
        operands = []
        while True:
            word = binary.get_next_word(throw_on_eol=False)
            if word is None:
                return operands
            operands.append(module.get_id(word))
    elif kind == 'VariableIdLiteral':
        operands = []
        while True:
            word = binary.get_next_word(throw_on_eol=False)
            if word is None:
                return operands
            operands.append(module.get_id(word))
            word = binary.get_next_word()
            operands.append(word)
    elif kind == 'VariableLiteralId':
        operands = []
        while True:
            word = binary.get_next_word(throw_on_eol=False)
            if word is None:
                return operands
            operands.append(word)
            word = binary.get_next_word()
            operands.append(module.get_id(word))
    elif kind in ir.MASKS:
        val = binary.get_next_word()
        return [expand_mask(kind, val)]
    elif kind in spirv.spv:
        val = binary.get_next_word()
        constants = spirv.spv[kind]
        for name in constants:
            if constants[name] == val:
                return [name]
        raise ParseError('Unknown "' + kind + '" value' + str(val))

    raise ParseError('Unknown kind "' + kind + '"')


def parse_instruction(binary, module):
    """Parse one instruction."""
    op_name, op_format = binary.get_next_opcode()
    operands = []
    inst_type = None
    if op_format['type']:
        inst_type = parse_id(binary, module)
    result = None
    if op_format['result']:
        result = parse_id(binary, module)
        if result.inst is not None:
            raise ParseError('ID ' + str(result) + ' is already defined')
    for kind in op_format['operands']:
        operands = operands + parse_operand(binary, module, kind)
    binary.expect_eol()

    if op_name == 'OpFunction':
        return ir.Function(module, result, operands[0], operands[1])
    else:
        return ir.Instruction(module, op_name, result, inst_type, operands)


def parse_global_instructions(binary, module):
    """Parse all global instructions (i.e. up to the first function). """
    while True:
        op_name, _ = binary.get_next_opcode(peek=True)
        if op_name is None:
            return
        if op_name == 'OpFunction':
            return

        inst = parse_instruction(binary, module)
        module.add_global_inst(inst)


def parse_basic_block(binary, module, function):
    """Parse one basic block."""
    binary.get_next_opcode()
    basic_block_id = parse_id(binary, module)
    binary.expect_eol()
    basic_block = ir.BasicBlock(module, basic_block_id)

    while True:
        inst = parse_instruction(binary, module)
        if not isinstance(inst, ir.Instruction):
            raise ParseError('Invalid opcode OpFunction in basic block')
        if inst.op_name == 'OpLabel':
            raise ParseError('Invalid opcode OpLabel in basic block')
        basic_block.append_inst(inst)
        if inst.op_name in ir.BRANCH_INSTRUCTIONS:
            function.add_basic_block(basic_block)
            return


def parse_function(binary, module):
    """Parse one function."""
    function = parse_instruction(binary, module)

    while True:
        op_name, _ = binary.get_next_opcode(peek=True)
        if op_name == 'OpLabel':
            parse_basic_block(binary, module, function)
        elif op_name == 'OpFunctionEnd':
            binary.discard_inst()
            return function
        elif op_name == 'OpFunctionParameter':
            inst = parse_instruction(binary, module)
            function.append_parameter(inst)
        else:
            raise ParseError('Invalid opcode ' + op_name)


def parse_functions(binary, module):
    """Parse all functions (i.e. rest of the module)."""
    while True:
        op_name, _ = binary.get_next_opcode(peek=True, throw_on_eol=False)
        if op_name is None:
            return
        if op_name != 'OpFunction':
            raise ParseError('Expected an "OpFunction" instruction')

        function = parse_function(binary, module)
        module.add_function(function)


def read_module(stream):
    data = stream.read()
    if len(data) % 4 != 0:
        raise ParseError('File length is not divisible by 4')
    words = array.array('I', data)
    binary = SpirvBinary(words)

    module = ir.Module()
    parse_global_instructions(binary, module)
    parse_functions(binary, module)

    return module
