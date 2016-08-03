"""Create a module from a SPIR-V binary read from a stream."""
import array
from operator import itemgetter

from spirv_tools import spirv
from spirv_tools import ir


class ParseError(Exception):
    """Raised when encountering invalid SPIR-V constructs while parsing."""


class SpirvBinary(object):
    """This class represent the SPIR-V binary being parsed."""
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

    def get_next_opcode(self, peek=False, accept_eol=False):
        """Start parsing one instruction and return the opcode.

        Args:
          peek (bool, optional): If True, return the opcode, but do not
            advance to the next position. Defaults to False.

          accept_eol (bool, optional): If False, raise an exception if
            reading past the end of the file. Defaults to False

        Returns:
          The opcode as a pair:
          - a string containing the operation name
          - a dictionary describing the format of the instruction

        Raises:
          ParseError: If reading past the end of the instruction (and
          accept_eol is False)
        """
        if self.idx == len(self.words):
            if accept_eol:
                return None, None
            else:
                raise ParseError('Unexpected end of file')

        opcode = self.words[self.idx] & 0xFFFF
        self.length = (self.words[self.idx] >> 16) - 1

        if not peek:
            self.idx += 1

        if opcode not in ir.OPCODE_TO_OPNAME:
            raise ParseError('Invalid opcode ' + str(opcode))

        op_name = ir.OPCODE_TO_OPNAME[opcode]
        return op_name, ir.INST_FORMAT[op_name]

    def get_next_word(self, peek=False, accept_eol=False):
        """Return the next word of the instruction.

        Args:
          peek (bool, optional): If True, return the word, but do not
            advance to the next position. Defaults to False.

          accept_eol (bool, optional): If False, raise an exception if
            reading past the end of the instruction. Defaults to False

        Returns:
          The instruction word as an integer, or None if reading past the
          end of the instruction (and accept_eol is True)

        Raises:
          ParseError: If reading past the end of the instruction (and
          accept_eol is False)
        """
        if self.idx == len(self.words):
            if accept_eol:
                return None
            else:
                raise ParseError('Unexpected end of file')

        if self.length == 0:
            if accept_eol:
                return None
            else:
                raise ParseError('Incorrect instruction length')

        word = self.words[self.idx]

        if not peek:
            self.idx += 1
            self.length -= 1

        return word

    def expect_eol(self):
        """Check that all words in the instruction have been consumed.

        Raises:
          ParseError: If not all words in the instruction have been consumed.
        """
        if self.length != 0:
            raise ParseError('Spurius words after parsing instruction')


def parse_literal_string(binary):
    """Parse one LiteralString."""
    result = []
    while True:
        word = binary.get_next_word()
        for _ in range(4):
            octet = word & 255
            if octet == 0:
                return ''.join(result)
            result.append(chr(octet))
            word >>= 8
    raise ParseError('bad encoding')


def parse_id(binary, module, accept_eol=False):
    """Parse one Id."""
    word = binary.get_next_word(accept_eol=accept_eol)
    if word is not None:
        if word in module.value_to_id:
            return module.value_to_id[word]
        new_id = ir.Id(module, word)
        module.value_to_id[word] = new_id
        return new_id
    else:
        return None


def expand_mask(kind, value):
    """Convert the mask value to a list of mask strings."""
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
    elif kind == 'OptionalLiteralString':
        word = binary.get_next_word(peek=True, accept_eol=True)
        if word is None:
            return []
        return [parse_literal_string(binary)]
    elif kind == 'VariableLiteralNumber' or kind == 'OptionalLiteralNumber':
        operands = []
        while True:
            word = binary.get_next_word(accept_eol=True)
            if word is None:
                return operands
            operands.append(word)
    elif kind in ['VariableId', 'OptionalId']:
        operands = []
        while True:
            tmp_id = parse_id(binary, module, accept_eol=True)
            if tmp_id is None:
                return operands
            operands.append(tmp_id)
    elif kind == 'VariableIdLiteralPair':
        operands = []
        while True:
            tmp_id = parse_id(binary, module, accept_eol=True)
            if tmp_id is None:
                return operands
            operands.append(tmp_id)
            word = binary.get_next_word()
            operands.append(word)
    elif kind == 'VariableLiteralIdPair':
        operands = []
        while True:
            word = binary.get_next_word(accept_eol=True)
            if word is None:
                return operands
            operands.append(word)
            tmp_id = parse_id(binary, module)
            operands.append(tmp_id)
    elif kind == 'OptionalMemoryAccessMask':
        val = binary.get_next_word(accept_eol=True)
        if val is None:
            return []
        result = expand_mask(kind[8:], val)
        try:
            aligned_idx = result.index('Aligned')
        except ValueError:
            pass
        else:
            result[aligned_idx] = (
                    'Aligned', binary.get_next_word(accept_eol=False))
        return [result]

    elif kind[:8] == 'Optional' and kind[-4:] == 'Mask':
        val = binary.get_next_word(accept_eol=True)
        if val is None:
            return []
        return [expand_mask(kind[8:], val)]
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
    inst_type_id = None
    if op_format['type']:
        inst_type_id = parse_id(binary, module)
    result_id = None
    if op_format['result']:
        result_id = parse_id(binary, module)
        if result_id.inst is not None:
            raise ParseError('ID ' + str(result_id) + ' is already defined')
    for kind in op_format['operands']:
        operands = operands + parse_operand(binary, module, kind)
    binary.expect_eol()

    if op_name == 'OpFunction':
        return ir.Function(module, operands[0], operands[1],
                           result_id=result_id)
    else:
        return ir.Instruction(module, op_name, inst_type_id, operands,
                              result_id=result_id)


def parse_global_instructions(binary, module):
    """Parse all global instructions (i.e. up to the first function)."""
    while True:
        op_name, _ = binary.get_next_opcode(peek=True, accept_eol=True)
        if op_name is None:
            return
        if op_name == 'OpFunction':
            return

        inst = parse_instruction(binary, module)
        module.insert_global_inst(inst)


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
            function.append_basic_block(basic_block)
            return


def parse_function(binary, module):
    """Parse one function."""
    function = parse_instruction(binary, module)

    while True:
        op_name, _ = binary.get_next_opcode(peek=True)
        if op_name == 'OpLabel':
            parse_basic_block(binary, module, function)
        elif op_name == 'OpFunctionEnd':
            binary.get_next_opcode()
            binary.expect_eol()
            return function
        elif op_name == 'OpFunctionParameter':
            inst = parse_instruction(binary, module)
            function.append_parameter(inst)
        else:
            raise ParseError('Invalid opcode ' + op_name)


def parse_functions(binary, module):
    """Parse all functions (i.e. rest of the module)."""
    while True:
        op_name, _ = binary.get_next_opcode(peek=True, accept_eol=True)
        if op_name is None:
            return
        if op_name != 'OpFunction':
            raise ParseError('Expected an "OpFunction" instruction')

        function = parse_function(binary, module)
        module.append_function(function)


def read_module(stream):
    """Create a module from a SPIR-V binary read from stream."""
    data = stream.read()
    if len(data) % 4 != 0:
        raise ParseError('File length is not divisible by 4')
    words = array.array('I', data)
    binary = SpirvBinary(words)

    module = ir.Module()
    module.value_to_id = {}
    try:
        parse_global_instructions(binary, module)
        parse_functions(binary, module)
        return module
    finally:
        del module.value_to_id
