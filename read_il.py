#!/usr/bin/env python

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

        Tha tokenizer is working one line at a time, and a new line is
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
            r'@[a-zA-Z][a-zA-Z0-9_]*',
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


def parse_id(lexer, module, accept_eol=False):
    """parse one Id."""
    token = lexer.get_next_token(accept_eol=accept_eol)
    if accept_eol and token == '':
        return ''
    elif token[0] == '%':
        return token
    elif token in module.type_name_to_id:
        return module.type_name_to_id[token]
    elif token in module.symbol_name_to_id:
        return module.symbol_name_to_id[token]
    elif token[0] == '@':
        new_id = module.get_new_id()
        module.symbol_name_to_id[token] = new_id
        name = '"' + token[1:] + '"'
        instr = ir.Instruction('OpName', None, None, [new_id, name])
        module.add_global_instruction(instr)
        return new_id
    else:
        return get_or_create_type(module, token)


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
    new_id = module.get_new_id()
    instr = ir.Instruction('OpTypeVector', new_id, None,
                           [base_type_id, nof_elem])
    module.add_global_instruction(instr)


def get_or_create_type(module, token):
    if not token in module.type_name_to_id:
        if token == 'void':
            new_id = module.get_new_id()
            instr = ir.Instruction('OpTypeVoid', new_id, None, [])
            module.add_global_instruction(instr)
        elif token == 'bool':
            new_id = module.get_new_id()
            instr = ir.Instruction('OpTypeBool', new_id, None, [])
            module.add_global_instruction(instr)
        elif token in ['s8', 's16', 's32', 's64']:
            new_id = module.get_new_id()
            width = token[1:]
            instr = ir.Instruction('OpTypeInt', new_id, None, [width, '1'])
            module.add_global_instruction(instr)
        elif token in ['u8', 'u16', 'u32', 'u64']:
            new_id = module.get_new_id()
            width = token[1:]
            instr = ir.Instruction('OpTypeInt', new_id, None, [width, '0'])
            module.add_global_instruction(instr)
        elif token in ['f16', 'f32', 'f64']:
            new_id = module.get_new_id()
            width = token[1:]
            instr = ir.Instruction('OpTypeFloat', new_id, None, [width])
            module.add_global_instruction(instr)
        elif token[0] == '<':
            add_vector_type(module, token)
        else:
            raise ParseError('Not a valid type: ' + token)

    return module.type_name_to_id[token]


def parse_type(lexer, module):
    token = lexer.get_next_token()
    if token[0] == '%':
        return token
    else:
        return get_or_create_type(module, token)


def get_or_create_function_type(module, return_type, arguments):
    for type_id in module.type_id_to_name:
        instr = module.id_to_instruction[type_id]
        if instr.name == 'OpTypeFunction':
            if instr.operands[0] == return_type:
                if len(arguments) == len(instr.operands[1:]):
                    # XXX check arguments
                    return type_id
    operands = [return_type] + [arg[0] for arg in arguments]
    new_id = module.get_new_id()
    instr = ir.Instruction('OpTypeFunction', new_id, None, operands)
    module.add_global_instruction(instr)
    return new_id


def get_or_create_pointer_type(module, base_type_id, storage_class):
    for type_id in module.type_id_to_name:
        instr = module.id_to_instruction[type_id]
        if instr.name == 'OpTypePointer':
            operands = instr.operands
            if operands[0] == storage_class and operands[1] == base_type_id:
                return type_id
    operands = [storage_class, base_type_id]
    new_id = module.get_new_id()
    instr = ir.Instruction('OpTypePointer', new_id, None, operands)
    module.add_global_instruction(instr)
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
    token = lexer.get_next_token()
    if token[0] == '%':
        op_result = token
        lexer.get_next_token('=')
        op_name = lexer.get_next_token()
    else:
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

    for kind in opcode['operands']:
        operands = operands + parse_operand(lexer, module, kind)
        comma = lexer.get_next_token(',', accept_eol=True)
        if comma == '':
            break
    # XXX Check that we have got the correct number of operands
    # when things like 'VariableLiterals' may be absent

    lexer.done_with_line()

    return ir.Instruction(op_name, op_result, op_type, operands)


def parse_decorations(lexer, module, variable_name):
    """Parse pretty-printed decorations."""
    while True:
        token = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            lexer.done_with_line()
            return

        decoration = lexer.get_next_token()
        if not decoration in spirv.CONSTANTS['Decoration']:
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
        instr = ir.Instruction('OpDecorate', None, None, operands)
        module.add_global_instruction(instr)


def parse_global_variable(lexer, module):
    """Parse one pretty-printed global variable."""
    variable_name = lexer.get_next_token()
    assert variable_name[0] == '@'
    lexer.get_next_token('=')
    storage_class = lexer.get_next_token()
    variable_type = parse_type(lexer, module)
    # XXX Handle OptionalId

    ptr_type = get_or_create_pointer_type(module, variable_type, storage_class)
    new_id = module.get_new_id()
    instr = ir.Instruction('OpVariable', new_id, ptr_type, [storage_class])
    module.add_global_instruction(instr)
    module.symbol_name_to_id[variable_name] = new_id
    tmp_name = '"' + variable_name[1:] + '"'
    instr = ir.Instruction('OpName', None, None, [new_id, tmp_name])
    module.add_global_instruction(instr)

    parse_decorations(lexer, module, new_id)


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
        elif token[0] == '@':
            parse_global_variable(lexer, module)
        else:
            instr = parse_instruction(lexer, module)
            if instr.name == 'OpFunction':
                func = parse_function_raw(lexer, module, instr)
                module.add_function(func)
            else:
                module.add_global_instruction(instr)


def parse_basic_block_body(lexer, module, basic_block):
    """Parse the instructions in one basic block."""
    while True:
        token = lexer.get_next_token(peek=True, accept_eol=True)

        if token == '':
            lexer.done_with_line()  # This is an empty line -- nothing to do.
        elif token[-1] == ':':
            raise ParseError('Label without terminating previous basic block')
        else:
            instr = parse_instruction(lexer, module)
            basic_block.instrs.append(instr)
            if token in spirv.TERMINATING_INSTRUCTIONS:
                return


def parse_basic_block(lexer, module, initial_instrs):
    """Parse one basic block."""
    token = lexer.get_next_token()
    lexer.done_with_line()
    basic_block = ir.BasicBlock(token[:-1])

    for instr in initial_instrs:
        basic_block.instrs.append(instr)

    parse_basic_block_body(lexer, module, basic_block)

    return basic_block


def parse_function_raw(lexer, module, instr):
    """Parse one function staring with the 'OpFunction' instruction."""
    function = ir.Function(module,
                           instr.result_id,
                           instr.operands[0],
                           instr.operands[1])

    while True:
        token = lexer.get_next_token(peek=True)
        if token == '':
            break  # This is an empty line -- nothing to do.

        instr = parse_instruction(lexer, module)

        if instr.name == 'OpLabel':
            basic_block = ir.BasicBlock(instr.result_id)
            parse_basic_block_body(lexer, module, basic_block)
            function.add_basic_block(basic_block)
        elif instr.name == 'OpFunctionEnd':
            return function
        elif instr.name == 'OpFunctionParameter':
            function.arguments.append(instr.result_id)
            module.id_to_instruction[instr.result_id] = instr
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
        arg_instr = ir.Instruction('OpFunctionParameter', arg_id, arg_type, [])
        module.id_to_instruction[arg_id] = arg_instr
        function.arguments.append(arg_id)

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
            basic_block = parse_basic_block(lexer, module, param_loads)
            param_loads = []
            func.add_basic_block(basic_block)
        else:
            raise ParseError('Syntax error')


def read_module(stream):
    module = ir.Module()
    lexer = Lexer(stream)
    try:
        parse_instructions(lexer, module)
        module.finalize()
        return module
    except ParseError as err:
        raise ParseError(str(lexer.line_no) + ': error: ' + err.value)
