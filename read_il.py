import re

import spirv
import ir


class ParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class VerificationError(Exception):
    def __init__(self, line_no, value):
        self.line_no = line_no
        self.value = value

    def __str__(self):
        return repr(self.value)


class Lexer(object):
    def __init__(self, stream):
        self.stream = stream
        self.line = None
        self.line_no = 0

    def get_next_token(self, expect=None, peek=False, accept_eol=False):
        """Return the next token from the file

        The tokenizer is working one line at a time, and a new line is
        read after the current line is consumed. Next line is read after
        done_with_line is executed.

        Args:
          expect (str, optional): A token to expect at this position. A
            syntax error is raised if it does not match. Defaults to None.
          peek (bool, optional): If True, return the token, but do not
            advance to the next position. Defaults to False.
          accept_eol (bool, optional): If True, return None when reading
            past the end of file instead of raising a ParseError.
            Defaults to False.

        Returns:
          str: The next token, or empty string if reading past end of
          line (and the accept_eol parameter is True)
          None: If reading past end of file

        Raises:
          ParseError: If no valid token can be created from the input,
          or when a token does not match the expected token (if the
          expect parameter is provided)
        """

        token_exprs = [
            (r'%[a-zA-Z_][a-zA-Z0-9_]*:', 'LABEL'),
            (r'%[1-9][0-9]*:', 'LABEL'),
            (r'%[a-zA-Z_][a-zA-Z0-9_]*', 'ID'),
            (r'%[1-9][0-9]*', 'ID'),
            (r'<[1-9]+ x [a-zA-Z0-9]*>', 'VEC_TYPE'),
            (r'".*"', "STRING"),
            (r',', None),
            (r'=', None),
            (r'{', None),
            (r'}', None),
            (r'\(', None),
            (r'\)', None),
            (r'-?0b[0-9]+', 'INT'),
            (r'-?0x[0-9]+', 'INT'),
            (r'-?[1-9][0-9]*', 'INT'),
            (r'-?0', 'INT'),
            (r'[a-zA-Z0-9.]+', 'NAME')
        ]

        if self.line is None:
            self.line = self.stream.readline()
            if not self.line:
                return None, None
            self.line_no += 1

        self.line = self.line.strip()
        if not self.line or self.line[0] == ';':
            if accept_eol:
                return '', None
            else:
                raise ParseError('Expected more tokens')

        for token_expr in token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(self.line)
            if match:
                token = match.group(0)
                if not peek:
                    self.line = self.line[match.end(0):]
                if expect is not None and token != expect:
                    raise ParseError('Expected ' + expect)
                return token, tag

        raise ParseError('Syntax error')


    def done_with_line(self):
        """Check that no tokens are remaining, and mark the line as done."""
        token, _ = self.get_next_token(accept_eol=True)
        if  token != '':
            raise ParseError('Spurius tokens after expected end of line')
        self.line = None


def get_type_range(module, type_id):
    type_inst = module.id_to_inst[type_id]
    if type_inst.op_name != 'OpTypeInt':
        raise ParseError('Type must be OpTypeInt')
    bitwidth = type_inst.operands[0]
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
    return min_val, max_val


def get_or_create_scalar_constant(module, token, type_id):
    if token == 'true':
        type_id = get_or_create_type(module, 'bool')
        inst = ir.Instruction(module, 'OpConstantTrue', module.new_id(),
                              type_id, [])
        module.add_global_inst(inst)
    elif token == 'false':
        type_id = get_or_create_type(module, 'bool')
        inst = ir.Instruction(module, 'OpConstantFalse', module.new_id(),
                              type_id, [])
        module.add_global_inst(inst)
    else:
        min_val, max_val = get_type_range(module, type_id)
        is_neg = token[0] == '-'
        if is_neg:
            token = token[1:]

        if token[0:2] == '0x':
            value = int(token, 16)
        elif token[0:2] == '0b':
            value = int(token, 2)
        else:
            value = int(token)

        if is_neg:
            value = -value
            if value < min_val:
                raise ParseError('Value out of range')
            value = value & max_val
        else:
            if value > max_val:
                raise ParseError('Value out of range')

        inst = module.get_constant(type_id, value)

    return inst.result_id


def create_id(module, token, tag, type_id=None):
    """Create the 'real' ID from an ID token.

    The IDs are generalized; it accepts e.g. type names such as 'f32'
    where the ID for the 'OpTypeFloat' is returned. Valid generalized
    IDs are:
      * types
      * integer scalar constants (the value can be decimal, binary, or
        hexadecimal)
    """
    if token in module.symbol_name_to_id:
        return module.symbol_name_to_id[token]
    elif tag == 'ID':
        assert token[0] == '%'
        if not token[1].isdigit():
            new_id = module.new_id()
            module.symbol_name_to_id[token] = new_id
            name = '"' + token[1:] + '"'
            inst = ir.Instruction(module, 'OpName', None, None,
                                  [new_id, name])
            module.add_global_inst(inst)
            return new_id
        return token
    elif tag == 'INT' or token in ['true', 'false']:
        return get_or_create_scalar_constant(module, token, type_id)
    elif token in module.type_name_to_id:
        return module.type_name_to_id[token]
    else:
        return get_or_create_type(module, token)


def parse_id(lexer, module, accept_eol=False, type_id=None):
    """Parse one ID.

    This parses generalized Id's, so it accepts e.g. type names such as 'f32'
    where the ID for the 'OpTypeFloat' is returned.  See 'create_id' for
    which generalizations are accepted.
    """
    token, tag = lexer.get_next_token(accept_eol=accept_eol)
    if accept_eol and token == '':
        return ''
    else:
        return create_id(module, token, tag, type_id)


def add_vector_type(module, token):
    orig_token = token
    if token[0] != '<' or token[-1] != '>':
        raise ParseError('Not a valid type: ' + orig_token)
    token = token[1:-1]
    if token[-6:-3] == ' x ':
        base_type = token[-3:]
        nof_elem = int(token[:-6])
    elif token[-5:-2] == ' x ':
        base_type = token[-2:]
        nof_elem = int(token[:-5])
    else:
        raise ParseError('Not a valid type: ' + orig_token)

    base_type_id = get_or_create_type(module, base_type)
    new_id = module.new_id()
    inst = ir.Instruction(module, 'OpTypeVector', new_id, None,
                          [base_type_id, nof_elem])
    module.add_global_inst(inst)
    return inst


def get_or_create_type(module, token):
    if not token in module.type_name_to_id:
        if token == 'void':
            new_id = module.new_id()
            inst = ir.Instruction(module, 'OpTypeVoid', new_id, None, [])
            module.add_global_inst(inst)
        elif token == 'bool':
            new_id = module.new_id()
            inst = ir.Instruction(module, 'OpTypeBool', new_id, None, [])
            module.add_global_inst(inst)
        elif token in ['s8', 's16', 's32', 's64']:
            new_id = module.new_id()
            width = int(token[1:])
            inst = ir.Instruction(module, 'OpTypeInt', new_id, None,
                                  [width, 1])
            module.add_global_inst(inst)
        elif token in ['u8', 'u16', 'u32', 'u64']:
            new_id = module.new_id()
            width = int(token[1:])
            inst = ir.Instruction(module, 'OpTypeInt', new_id, None,
                                  [width, 0])
            module.add_global_inst(inst)
        elif token in ['f16', 'f32', 'f64']:
            new_id = module.new_id()
            width = int(token[1:])
            inst = ir.Instruction(module, 'OpTypeFloat', new_id, None,
                                  [width])
            module.add_global_inst(inst)
        elif token[0] == '<':
            inst = add_vector_type(module, token)
        else:
            raise ParseError('Not a valid type: ' + token)
        module.type_name_to_id[token] = inst.result_id

    return module.type_name_to_id[token]


def parse_type(lexer, module):
    token, tag = lexer.get_next_token()
    type_id = create_id(module, token, tag)
    type_inst = module.id_to_inst[type_id]
    if type_inst.op_name not in spirv.TYPE_DECLARATION_INSTRUCTIONS:
        raise ParseError('Not a valid type: ' + token)
    return type_id


def get_or_create_function_type(module, return_type, arguments):
    for inst in module.global_insts:
        if inst.op_name == 'OpTypeFunction':
            if inst.operands[0] == return_type:
                if [arg[0] for arg in arguments] == inst.operands[1:]:
                    return inst.result_id
    if arguments:
        operands = [return_type] + [arg[0] for arg in arguments]
    else:
        operands = [return_type] + [get_or_create_type(module, 'void')]
    new_id = module.new_id()
    inst = ir.Instruction(module, 'OpTypeFunction', new_id, None, operands)
    module.add_global_inst(inst)
    return new_id


def parse_operand(lexer, module, kind, type_id):
    """Parse one instruction operand."""
    if kind == 'Id':
        return [parse_id(lexer, module, type_id=type_id)]
    elif kind in spirv.MASKS:
        token, tag = lexer.get_next_token()
        return [int(token)]
    elif kind in ['LiteralNumber',
                  'VariableLiterals',
                  'OptionalLiteral']:
        token, tag = lexer.get_next_token()
        return [int(token)]
    elif kind == 'LiteralString':
        token, tag = lexer.get_next_token()
        return [token]
    elif kind == 'VariableIds' or kind == 'OptionalId':
        operands = []
        while True:
            operand_id = parse_id(lexer, module, accept_eol=True,
                                  type_id=type_id)
            if operand_id == '':
                return operands
            operands.append(operand_id)
            token, tag = lexer.get_next_token(peek=True, accept_eol=True)
            if token == ',':
                lexer.get_next_token()
    elif kind in spirv.CONSTANTS:
        value, tag = lexer.get_next_token()
        if value not in spirv.CONSTANTS[kind]:
            error = 'Invalid value "' + value + '"' 'for "' + kind + '"'
            raise ParseError(error)
        return [value]

    raise ParseError('Unknown argument kind "' + kind + '"')


def parse_instruction(lexer, module):
    """Parse one instruction."""
    token, tag = lexer.get_next_token(peek=True)
    if tag == 'ID':
        token = parse_id(lexer, module)
        op_result = token
        lexer.get_next_token('=')
        op_name, tag = lexer.get_next_token()
    else:
        token, tag = lexer.get_next_token()
        op_name = token
        op_result = None
    if tag != 'NAME':
        raise ParseError('Expected an operation name')
    if op_name not in spirv.OPNAME_TABLE:
        raise ParseError('Invalid operation ' + op_name)
    opcode = spirv.OPNAME_TABLE[op_name]
    if opcode['type']:
        op_type = parse_type(lexer, module)
    else:
        op_type = None
    operands = []

    parse_decorations(lexer, module, op_result)

    kinds = opcode['operands'][:]
    while kinds:
        kind = kinds.pop(0)
        operands = operands + parse_operand(lexer, module, kind, op_type)
        comma, tag = lexer.get_next_token(',', accept_eol=True)
        if comma == '':
            break

    # There are no more operands in the input.  This is OK if all the
    # remaining instruction operands are optional.
    while kinds:
        kind = kinds.pop(0)
        if kind not in ['OptionalLiteral', 'OptionalId', 'VariableLiterals']:
            raise ParseError('Missing operands')

    lexer.done_with_line()

    if op_name == 'OpFunction':
        function = ir.Function(module, op_result, operands[0], operands[1])
        module.inst_to_line[function.inst] = lexer.line_no
        module.inst_to_line[function.end_inst] = lexer.line_no
        return function
    elif op_name == 'OpLabel':
        basic_block = ir.BasicBlock(module, op_result)
        module.inst_to_line[basic_block.inst] = lexer.line_no
        return basic_block
    else:
        inst = ir.Instruction(module, op_name, op_result, op_type, operands)
        module.inst_to_line[inst] = lexer.line_no
        return inst


def parse_decorations(lexer, module, variable_name):
    """Parse pretty-printed decorations."""
    while True:
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            return
        elif token not in spirv.DECORATIONS:
            return

        decoration, _ = lexer.get_next_token()
        if not decoration in spirv.DECORATIONS:
            raise ParseError('Unknown decoration ' + decoration)
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        operands = [variable_name, decoration]
        if token == '(':
            lexer.get_next_token()
            while True:
                token, tag = lexer.get_next_token()
                operands.append(int(token))
                token, _ = lexer.get_next_token()
                if token == ')':
                    break
                if token != ',':
                    raise ParseError('Syntax error in decoration')
        inst = ir.Instruction(module, 'OpDecorate', None, None, operands)
        module.add_global_inst(inst)


def parse_instructions(lexer, module):
    """Parse all instructions."""
    while True:
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token is None:
            return
        elif token == 'define':
            func = parse_function(lexer, module)
            module.add_function(func)
        elif token == '':
            lexer.done_with_line()  # This is an empty line -- nothing to do.
        else:
            inst = parse_instruction(lexer, module)
            if isinstance(inst, ir.Function):
                func = parse_function_raw(lexer, module, inst)
                module.add_function(func)
            else:
                module.add_global_inst(inst)


def parse_basic_block_body(lexer, module, basic_block):
    """Parse the instructions in one basic block."""
    while True:
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)

        if token == '':
            lexer.done_with_line()  # This is an empty line -- nothing to do.
        elif token[-1] == ':':
            raise ParseError('Label without terminating previous basic block')
        else:
            inst = parse_instruction(lexer, module)
            if isinstance(inst, ir.BasicBlock):
                raise ParseError(
                    'Label without terminating previous basic block')
            elif isinstance(inst, ir.Function):
                raise ParseError('OpFunction within function')
            basic_block.append_inst(inst)
            if token in spirv.BRANCH_INSTRUCTIONS:
                return


def parse_basic_block(lexer, module, function, initial_insts):
    """Parse one basic block."""
    token, tag = lexer.get_next_token()
    assert tag == 'LABEL' and token[-1] == ':'
    lexer.done_with_line()
    basic_block_id = create_id(module, token[:-1], 'ID')
    basic_block = ir.BasicBlock(module, basic_block_id)

    for inst in initial_insts:
        basic_block.append_inst(inst)

    parse_basic_block_body(lexer, module, basic_block)
    function.add_basic_block(basic_block)


def parse_function_raw(lexer, module, function):
    """Parse one function staring with the 'OpFunction' instruction."""
    while True:
        token, _ = lexer.get_next_token(peek=True)
        if token == '':
            break  # This is an empty line -- nothing to do.

        inst = parse_instruction(lexer, module)

        if isinstance(inst, ir.BasicBlock):
            parse_basic_block_body(lexer, module, inst)
            function.add_basic_block(inst)
        elif isinstance(inst, ir.Function):
            raise ParseError('OpFunction within function')
        elif inst.op_name == 'OpFunctionEnd':
            return function
        elif inst.op_name == 'OpFunctionParameter':
            function.append_argument(inst)
        else:
            raise ParseError('Syntax error')


def parse_arguments(lexer, module):
    """Parse the arguments of a pretty-printed function."""
    arguments = []
    lexer.get_next_token('(')
    token, _ = lexer.get_next_token(peek=True)
    if token == 'void':
        lexer.get_next_token('void')
        lexer.get_next_token(')')
        return []
    while lexer.get_next_token(peek=True) != (')', None):
        arg_type = parse_type(lexer, module)
        arg_id = parse_id(lexer, module)
        arguments.append((arg_type, arg_id))
        if lexer.get_next_token(peek=True) == (',', None):
            lexer.get_next_token()
            if lexer.get_next_token(peek=True) == (')', None):
                raise ParseError('Expected argument after ","')
    lexer.get_next_token(')')
    return arguments


def parse_function_definition(lexer, module):
    """Parse the 'definition' line of a pretty-printed function."""
    lexer.get_next_token('define')
    return_type = parse_type(lexer, module)
    name = parse_id(lexer, module)
    arguments = parse_arguments(lexer, module)
    lexer.get_next_token('{')
    lexer.done_with_line()

    function_type = get_or_create_function_type(module, return_type, arguments)

    function = ir.Function(module, name, 0, function_type) # XXX
    param_loads = []
    for (arg_type, arg_id) in arguments:
        arg_inst = ir.Instruction(module, 'OpFunctionParameter', arg_id,
                                  arg_type, [])
        function.append_argument(arg_inst)

    return function, param_loads


def parse_function(lexer, module):
    """Parse one pretty-printed function."""
    func, param_loads = parse_function_definition(lexer, module)

    while True:
        token, tag = lexer.get_next_token(peek=True, accept_eol=True)

        if token == '':
            lexer.done_with_line()  # This is an empty line -- nothing to do.
        elif token == '}':
            lexer.get_next_token()
            lexer.done_with_line()
            return func
        elif tag == 'LABEL':
            parse_basic_block(lexer, module, func, param_loads)
            param_loads = []
        else:
            raise ParseError('Syntax error')


def verify_id(module, inst, id_to_check):
    """Verify that the ID is defined in user defined instructions.

    Raise an 'used by not defined' exception if the ID is not defined for
    a user defined instruction.  Instructions introduced by the implementation
    are ignored (e.g. an OpName instruction that was inserted because a
    user defined instruction used an undefined named ID) as the error will
    be reported for the used defined instruction anyway.
    """
    if inst not in module.inst_to_line:
        return
    if not id_to_check in module.id_to_inst:
        id_name = id_to_check
        for name in module.symbol_name_to_id:
            if module.symbol_name_to_id[name] == id_to_check:
                id_name = name
                break
        line_no = module.inst_to_line[inst]
        raise VerificationError(line_no, id_name + ' used but not defined')


def verify_ids_are_defined(module):
    """Verify that all IDs are defined in used defined instructions."""
    for inst in module.instructions():
        if inst.result_id is not None:
            verify_id(module, inst, inst.result_id)
        if inst.type_id is not None:
            verify_id(module, inst, inst.type_id)
        for operand in inst.operands:
            if isinstance(operand, basestring):
                if operand[0] == '%':
                    verify_id(module, inst, operand)


def read_module(stream):
    module = ir.Module()
    module.type_name_to_id = {}
    module.symbol_name_to_id = {}
    module.inst_to_line = {}
    lexer = Lexer(stream)
    try:
        parse_instructions(lexer, module)
        verify_ids_are_defined(module)
        module.finalize()
        return module
    except ParseError as err:
        raise ParseError(str(lexer.line_no) + ': error: ' + err.value)
    except ir.IRError as err:
        raise ParseError(str(lexer.line_no) + ': error: ' + err.value)
    except VerificationError as err:
        raise ParseError(str(err.line_no) + ': error: ' + err.value)
    finally:
        del module.inst_to_line
        del module.symbol_name_to_id
        del module.type_name_to_id
