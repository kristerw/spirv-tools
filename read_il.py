import re

import spirv
import ir


class ParseError(Exception):
    def __init__(self, value):
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
            r'%[a-zA-Z0-9]*:',
            r'%[0-9]+',
            r'%[a-zA-Z][a-zA-Z0-9_]*',
            r'<[1-9]+ x [a-zA-Z0-9]*>',
            r'".+"',
            r'define',
            r',',
            r'=',
            r'{',
            r'}',
            r'\(',
            r'\)',
            r'ret',
            r'[a-zA-Z0-9.]+'
        ]

        if self.line is None:
            self.line = self.stream.readline()
            if not self.line:
                return None
            self.line_no += 1

        self.line = self.line.strip()
        if not self.line or self.line[0] == ';':
            if accept_eol:
                return ''
            else:
                raise ParseError('Expected more tokens')

        for pattern in token_exprs:
            regex = re.compile(pattern)
            match = regex.match(self.line)
            if match:
                token = match.group(0)
                if not peek:
                    self.line = self.line[match.end(0):]
                if expect is not None and token != expect:
                    raise ParseError('Expected ' + expect)
                return token

        raise ParseError('Syntax error')


    def done_with_line(self):
        """Check that no tokens are remaining, and mark the line as done."""
        if self.get_next_token(accept_eol=True) != '':
            raise ParseError('Spurius tokens after expected end of line')
        self.line = None


def create_id(module, token):
    """Create the 'real' ID from an ID token."""
    if token in module.symbol_name_to_id:
        return module.symbol_name_to_id[token]
    elif token[0] == '%':
        if not token[1].isdigit():
            new_id = module.new_id()
            module.symbol_name_to_id[token] = new_id
            name = '"' + token[1:] + '"'
            inst = ir.Instruction(module, 'OpName', None, None,
                                  [new_id, name])
            module.add_global_inst(inst)
            return new_id
        return token
    elif token in module.type_name_to_id:
        return module.type_name_to_id[token]
    else:
        return get_or_create_type(module, token)


def parse_id(lexer, module, accept_eol=False):
    """parse one Id."""
    token = lexer.get_next_token(accept_eol=accept_eol)
    if accept_eol and token == '':
        return ''
    else:
        return create_id(module, token)


def add_vector_type(module, token):
    orig_token = token
    if token[0] != '<' or token[-1] != '>':
        raise ParseError('Not a valid type: ' + orig_token)
    token = token[1:-1]
    if token[-6:-3] == ' x ':
        base_type = token[-3:]
        nof_elem = token[:-6]
    elif token[-5:-2] == ' x ':
        base_type = token[-2:]
        nof_elem = token[:-5]
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
            width = token[1:]
            inst = ir.Instruction(module, 'OpTypeInt', new_id, None,
                                  [width, '1'])
            module.add_global_inst(inst)
        elif token in ['u8', 'u16', 'u32', 'u64']:
            new_id = module.new_id()
            width = token[1:]
            inst = ir.Instruction(module, 'OpTypeInt', new_id, None,
                                  [width, '0'])
            module.add_global_inst(inst)
        elif token in ['f16', 'f32', 'f64']:
            new_id = module.new_id()
            width = token[1:]
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
    token = lexer.get_next_token()
    if token in module.symbol_name_to_id:
        return module.symbol_name_to_id[token]
    elif token[0] == '%':
        return token
    else:
        return get_or_create_type(module, token)


def get_or_create_function_type(module, return_type, arguments):
    for inst in module.global_insts:
        if inst.op_name == 'OpTypeFunction':
            if inst.operands[0] == return_type:
                if len(arguments) == len(inst.operands[1:]):
                    # XXX check arguments
                    return inst.result_id
    operands = [return_type] + [arg[0] for arg in arguments]
    new_id = module.new_id()
    inst = ir.Instruction(module, 'OpTypeFunction', new_id, None, operands)
    module.add_global_inst(inst)
    return new_id


def parse_operand(lexer, module, kind):
    """Parse one instruction operand."""
    if kind == 'Id':
        return [parse_id(lexer, module)]
    elif kind in spirv.MASKS:
        return [lexer.get_next_token()]
    elif kind in ['LiteralNumber',
                  'LiteralString',
                  'VariableLiterals']:
        return [lexer.get_next_token()]
    elif kind == 'VariableIds' or kind == 'OptionalId':
        operands = []
        while True:
            operand_id = parse_id(lexer, module, accept_eol=True)
            if operand_id == '':
                return operands
            operands.append(operand_id)
            if lexer.get_next_token(peek=True, accept_eol=True) == ',':
                lexer.get_next_token()
    elif kind in spirv.CONSTANTS:
        value = lexer.get_next_token()
        if value not in spirv.CONSTANTS[kind]:
            error = 'Invalid value "' + value + '"' 'for "'+ kind + '"'
            raise ParseError(error)
        return [value]

    raise ParseError('Unknown argument kind "' + kind + '"')


def parse_instruction(lexer, module):
    """Parse one instruction."""
    token = lexer.get_next_token(peek=True)
    if token[0] == '%':
        token = parse_id(lexer, module)
        op_result = token
        lexer.get_next_token('=')
        op_name = lexer.get_next_token()
    else:
        token = lexer.get_next_token()
        op_name = token
        op_result = None
    if op_name not in spirv.OPNAME_TABLE:
        raise ParseError('Invalid operation ' + op_name)
    opcode = spirv.OPNAME_TABLE[op_name]
    if opcode['type']:
        op_type = parse_type(lexer, module)
    else:
        op_type = None
    operands = []

    parse_decorations(lexer, module, op_result)

    for kind in opcode['operands']:
        operands = operands + parse_operand(lexer, module, kind)
        comma = lexer.get_next_token(',', accept_eol=True)
        if comma == '':
            break
    # XXX Check that we have got the correct number of operands
    # when things like 'VariableLiterals' may be absent

    lexer.done_with_line()

    return ir.Instruction(module, op_name, op_result, op_type, operands)


def parse_decorations(lexer, module, variable_name):
    """Parse pretty-printed decorations."""
    while True:
        token = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            return
        elif token not in spirv.DECORATIONS:
            return

        decoration = lexer.get_next_token()
        if not decoration in spirv.DECORATIONS:
            raise ParseError('Unknown decoration ' + decoration)
        token = lexer.get_next_token(peek=True, accept_eol=True)
        operands = [variable_name, decoration]
        if token == '(':
            lexer.get_next_token()
            while True:
                token = lexer.get_next_token()
                operands.append(token)
                token = lexer.get_next_token()
                if token == ')':
                    break
                if token != ',':
                    raise ParseError('Syntax error in decoration')
        inst = ir.Instruction(module, 'OpDecorate', None, None, operands)
        module.add_global_inst(inst)


def parse_instructions(lexer, module):
    """Parse all instructions."""
    while True:
        token = lexer.get_next_token(peek=True, accept_eol=True)
        if token is None:
            return
        elif token == 'define':
            func = parse_function(lexer, module)
            module.add_function(func)
        elif token == '':
            lexer.done_with_line()  # This is an empty line -- nothing to do.
        else:
            inst = parse_instruction(lexer, module)
            if inst.op_name == 'OpFunction':
                func = parse_function_raw(lexer, module, inst)
                module.add_function(func)
            else:
                module.add_global_inst(inst)


def parse_basic_block_body(lexer, module, basic_block):
    """Parse the instructions in one basic block."""
    while True:
        token = lexer.get_next_token(peek=True, accept_eol=True)

        if token == '':
            lexer.done_with_line()  # This is an empty line -- nothing to do.
        elif token[-1] == ':':
            raise ParseError('Label without terminating previous basic block')
        else:
            inst = parse_instruction(lexer, module)
            basic_block.append_inst(inst)
            if token in spirv.BASIC_BLOCK_ENDING_INSTRUCTIONS:
                return


def parse_basic_block(lexer, module, function, initial_insts):
    """Parse one basic block."""
    token = lexer.get_next_token()
    lexer.done_with_line()
    basic_block_id = create_id(module, token[:-1])
    basic_block = ir.BasicBlock(module, basic_block_id)

    for inst in initial_insts:
        basic_block.append_inst(inst)

    parse_basic_block_body(lexer, module, basic_block)
    function.add_basic_block(basic_block)


def parse_function_raw(lexer, module, inst):
    """Parse one function staring with the 'OpFunction' instruction."""
    function = ir.Function(module,
                           inst.result_id,
                           inst.operands[0],
                           inst.operands[1])

    while True:
        token = lexer.get_next_token(peek=True)
        if token == '':
            break  # This is an empty line -- nothing to do.

        inst = parse_instruction(lexer, module)

        if inst.op_name == 'OpLabel':
            basic_block = ir.BasicBlock(module, inst.result_id)
            parse_basic_block_body(lexer, module, basic_block)
            function.add_basic_block(basic_block)
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
    while lexer.get_next_token(peek=True) != ')':
        arg_type = parse_type(lexer, module)
        arg_id = parse_id(lexer, module)
        arguments.append((arg_type, arg_id))
        if lexer.get_next_token(peek=True) == ',':
            lexer.get_next_token()
            if lexer.get_next_token(peek=True) == ')':
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

    function = ir.Function(module, name, '0', function_type) # XXX
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
        token = lexer.get_next_token(peek=True, accept_eol=True)

        if token == '':
            lexer.done_with_line()  # This is an empty line -- nothing to do.
        elif token == '}':
            lexer.get_next_token()
            lexer.done_with_line()
            return func
        elif token[-1] == ':':
            parse_basic_block(lexer, module, func, param_loads)
            param_loads = []
        else:
            raise ParseError('Syntax error')


def read_module(stream):
    module = ir.Module()
    module.type_name_to_id = {}
    module.symbol_name_to_id = {}
    lexer = Lexer(stream)
    try:
        parse_instructions(lexer, module)
        module.finalize()
        del module.symbol_name_to_id
        del module.type_name_to_id
        return module
    except ParseError as err:
        raise ParseError(str(lexer.line_no) + ': error: ' + err.value)
    except ir.IRError as err:
        raise ParseError(str(lexer.line_no) + ': error: ' + err.value)
