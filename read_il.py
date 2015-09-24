import re

import ir


class ParseError(Exception):
    def __init__(self, message):
        super(ParseError, self).__init__(message)


class VerificationError(Exception):
    def __init__(self, line_no, message):
        super(VerificationError, self).__init__(message)
        self.line_no = line_no


class Lexer(object):
    def __init__(self, stream):
        token_exprs = [
            (r'%[1-9][0-9]*:', 'LABEL'),
            (r'%[a-zA-Z_][a-zA-Z0-9_]*:', 'LABEL'),
            (r'%[1-9][0-9]*', 'ID'),
            (r'%[a-zA-Z_][a-zA-Z0-9_]*', 'ID'),
            (r'[a-zA-Z][a-zA-Z0-9.]*', 'NAME'),
            (r'[,={}\(\)]', None),
            (r'<[1-9]+ x [a-zA-Z0-9]*>', 'VEC_TYPE'),
            (r'[1-3]D', 'NAME'),
            (r'-?0b[01]+', 'INT'),
            (r'-?0x[0-9a-fA-F]+', 'INT'),
            (r'-?[1-9][0-9]*', 'INT'),
            (r'-?0', 'INT'),
            (r'".*"', "STRING")
        ]
        self.stream = stream
        self.line = None
        self.line_no = 0
        self.compiled_token_exprs = []
        for pattern, tag in token_exprs:
            regex = re.compile(pattern)
            self.compiled_token_exprs.append((regex, tag))

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

        for regex, tag in self.compiled_token_exprs:
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
        if type_id.inst.op_name != 'OpTypeInt':
            raise ParseError('Type must be OpTypeInt')

        min_val, max_val = ir.get_int_type_range(module, type_id)
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
            name = token[1:]
            inst = ir.Instruction(module, 'OpName', None, None,
                                  [new_id, name])
            module.add_global_inst(inst)
            return new_id
        else:
            return module.get_id(int(token[1:]))
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
        return None
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
    elif token[-7:-4] == ' x ':
        base_type = token[-4:]
        nof_elem = int(token[:-7])
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
        module.id_to_type_name[inst.result_id] = token

    return module.type_name_to_id[token]


def add_type_name(module, inst):
    """Create a name for the type instruction.

    This is the "inverse" of get_or_create_type() and adds a name for
    a given type instruction. This is needed when assembling "raw" IL,
    as all of the original type instructions are present.

    This function must handle exactly the same types as get_or_create_type().
    """
    assert inst.op_name in ir.TYPE_DECLARATION_INSTRUCTIONS
    if inst.result_id in module.id_to_type_name:
        return

    if inst.op_name == 'OpTypeVoid':
        type_name = 'void'
    elif inst.op_name == 'OpTypeBool':
        type_name = 'bool'
    elif inst.op_name == 'OpTypeInt':
        if inst.operands[1] == 1:
            type_name = 's' + str(inst.operands[0])
        else:
            type_name = 'u' + str(inst.operands[0])
    elif inst.op_name == 'OpTypeFloat':
        type_name = 'f' + str(inst.operands[0])
    elif inst.op_name == 'OpTypeVector':
        base_type_id = inst.operands[0]
        if base_type_id not in module.id_to_type_name:
            return
        base_name = module.id_to_type_name[base_type_id]
        nof_elem = inst.operands[1]
        type_name = '<' + str(nof_elem) + ' x ' +  base_name + '>'
    else:
        return

    module.type_name_to_id[type_name] = inst.result_id
    module.id_to_type_name[inst.result_id] = type_name


def parse_type(lexer, module):
    """Parse one ID representing a type."""
    token, tag = lexer.get_next_token()
    if tag not in ['ID', 'NAME', 'VEC_TYPE']:
        raise ParseError('Not a valid type: ' + token)
    type_id = create_id(module, token, tag)
    if type_id.inst is None:
        raise ParseError(token + ' used but not defined')
    if type_id.inst.op_name not in ir.TYPE_DECLARATION_INSTRUCTIONS:
        raise ParseError('Not a valid type: ' + token)
    return type_id


def get_or_create_function_type(module, return_type, parameters):
    for inst in module.global_insts:
        if inst.op_name == 'OpTypeFunction':
            if inst.operands[0] == return_type:
                if [param[0] for param in parameters] == inst.operands[1:]:
                    return inst.result_id
    operands = [return_type] + [param[0] for param in parameters]
    new_id = module.new_id()
    inst = ir.Instruction(module, 'OpTypeFunction', new_id, None, operands)
    module.add_global_inst(inst)
    return new_id


def parse_operand(lexer, module, kind, type_id):
    """Parse one instruction operand."""
    if kind == 'Id':
        return [parse_id(lexer, module, type_id=type_id)]
    elif kind in ir.MASKS:
        token, tag = lexer.get_next_token()
        return [int(token)]
    elif kind == 'LiteralNumber':
        token, tag = lexer.get_next_token()
        return [int(token)]
    elif kind == 'VariableLiterals' or kind == 'OptionalLiteral':
        operands = []
        while True:
            token, tag = lexer.get_next_token(accept_eol=True)
            if token == '':
                return operands
            operands.append(int(token))
            token, tag = lexer.get_next_token(peek=True, accept_eol=True)
            if token == ',':
                lexer.get_next_token()
    elif kind == 'LiteralString':
        token, tag = lexer.get_next_token()
        return [token[1:-1]]
    elif kind == 'OptionalImage':
        operands = []
        token, tag = lexer.get_next_token(accept_eol=True)
        if token == '':
            return operands
        operands.append(int(token))
        token, tag = lexer.get_next_token(peek=True, accept_eol=True)
        if token == ',':
            lexer.get_next_token()
        while True:
            operand_id = parse_id(lexer, module, accept_eol=True,
                                  type_id=type_id)
            if operand_id is None:
                return operands
            operands.append(operand_id)
            token, tag = lexer.get_next_token(peek=True, accept_eol=True)
            if token == ',':
                lexer.get_next_token()
    elif kind in ['VariableIds', 'OptionalId']:
        operands = []
        while True:
            operand_id = parse_id(lexer, module, accept_eol=True,
                                  type_id=type_id)
            if operand_id is None:
                return operands
            operands.append(operand_id)
            token, tag = lexer.get_next_token(peek=True, accept_eol=True)
            if token == ',':
                lexer.get_next_token()
    elif kind == 'VariableLiteralId':
        operands = []
        while True:
            token, tag = lexer.get_next_token(accept_eol=True)
            if token == '':
                return operands
            operands.append(int(token))
            lexer.get_next_token(',')
            operand_id = parse_id(lexer, module, type_id=type_id)
            operands.append(operand_id)
            token, _ = lexer.get_next_token(peek=True, accept_eol=True)
            if token == ',':
                lexer.get_next_token()
    elif kind in ir.KINDS:
        value, tag = lexer.get_next_token()
        if value not in ir.KINDS[kind]:
            error = 'Invalid value ' + value + ' for ' + kind
            raise ParseError(error)
        return [value]

    raise ParseError('Unknown parameter kind "' + kind + '"')


def parse_operands(lexer, module, opcode, type_id):
    """Parse operands for one instruction."""
    operands = []
    kinds = opcode['operands'][:]
    while kinds:
        kind = kinds.pop(0)
        operands = operands + parse_operand(lexer, module, kind, type_id)
        token, _ = lexer.get_next_token(',', accept_eol=True)
        if token == '':
            break
        if not kinds:
            raise ParseError('Spurious "," after last operand')

    # There are no more operands in the input.  This is OK if all the
    # remaining instruction operands are optional.
    while kinds:
        kind = kinds.pop(0)
        if kind not in ['OptionalLiteral', 'OptionalId', 'VariableLiterals',
                        'VariableIds', 'OptionalImage', 'VariableLiteralId']:
            raise ParseError('Missing operands')

    return operands


def parse_instruction(lexer, module):
    """Parse one instruction."""
    _, tag = lexer.get_next_token(peek=True)
    if tag == 'ID':
        result_id = parse_id(lexer, module)
        if result_id.inst is not None:
            id_name = get_id_name(module, result_id)
            raise ParseError(id_name + ' is already defined')
        lexer.get_next_token('=')
    else:
        result_id = None
    op_name, tag = lexer.get_next_token()
    if tag != 'NAME':
        raise ParseError('Expected an operation name')
    if op_name not in ir.OPNAME_TABLE:
        raise ParseError('Invalid operation ' + op_name)
    opcode = ir.OPNAME_TABLE[op_name]
    if opcode['type']:
        type_id = parse_type(lexer, module)
    else:
        type_id = None

    parse_decorations(lexer, module, result_id, op_name)
    operands = parse_operands(lexer, module, opcode, type_id)
    lexer.done_with_line()

    if op_name == 'OpFunction':
        function = ir.Function(module, result_id, operands[0], operands[1])
        module.inst_to_line[function.inst] = lexer.line_no
        module.inst_to_line[function.end_inst] = lexer.line_no
        return function
    elif op_name == 'OpLabel':
        basic_block = ir.BasicBlock(module, result_id)
        module.inst_to_line[basic_block.inst] = lexer.line_no
        return basic_block
    else:
        inst = ir.Instruction(module, op_name, result_id, type_id, operands)
        module.inst_to_line[inst] = lexer.line_no
        if op_name in ir.TYPE_DECLARATION_INSTRUCTIONS:
            add_type_name(module, inst)
        return inst


def parse_decorations(lexer, module, variable_name, op_name):
    """Parse pretty-printed decorations."""
    while True:
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            return
        elif token not in ir.DECORATIONS:
            return

        # XXX We should check that the decorations are valid for the
        # operation.
        #
        # In particular 'Uniform' is both a decoration and a storage class,
        # so instructions that have 'StorageClass' as first operand must
        # not parse 'Uniform' as a decoration (and 'Uniform' is not a valid
        # decoration for those operations).  At this as a special case
        # here until the real decoration check has been implemented.
        if op_name in ['OpTypePointer', 'OpVariable'] and token == 'Uniform':
            return

        decoration, _ = lexer.get_next_token()
        if not decoration in ir.DECORATIONS:
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


def parse_translation_unit(lexer, module):
    """Parse a translation unit."""
    while True:
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token is None:
            return
        elif token == '':
            lexer.done_with_line()
        elif token == 'define':
            func = parse_function(lexer, module)
            module.add_function(func)
        else:
            inst = parse_instruction(lexer, module)
            if isinstance(inst, ir.Function):
                func = parse_function_raw(lexer, module, inst)
                module.add_function(func)
            elif isinstance(inst, ir.BasicBlock):
                raise ParseError('Basic block defined outside a function')
            else:
                module.add_global_inst(inst)


def parse_basic_block_body(lexer, module, basic_block):
    """Parse the instructions in one basic block."""
    while True:
        token, tag = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            lexer.done_with_line()
        elif tag == 'LABEL':
            raise ParseError('Label without terminating previous basic block')
        elif token == '}':
            raise ParseError(
                'Ending function without terminating previous basic block')
        else:
            inst = parse_instruction(lexer, module)
            if isinstance(inst, ir.BasicBlock):
                raise ParseError(
                    'Label without terminating previous basic block')
            elif isinstance(inst, ir.Function):
                raise ParseError('OpFunction within function')
            elif inst.op_name == 'OpFunctionEnd':
                raise ParseError(
                    'OpFunctionEnd without terminating previous basic block')
            basic_block.append_inst(inst)
            if token in ir.BRANCH_INSTRUCTIONS:
                return


def parse_basic_block(lexer, module, function):
    """Parse one pretty-printed basic block."""
    token, tag = lexer.get_next_token()
    assert tag == 'LABEL' and token[-1] == ':'
    lexer.done_with_line()

    basic_block_id = create_id(module, token[:-1], 'ID')
    if basic_block_id.inst is not None:
        id_name = get_id_name(module, basic_block_id)
        raise ParseError(id_name + ' is already defined')
    basic_block = ir.BasicBlock(module, basic_block_id)

    parse_basic_block_body(lexer, module, basic_block)
    function.add_basic_block(basic_block)


def parse_function_raw(lexer, module, function):
    """Parse a function staring with the 'OpFunction' instruction."""
    func_type_inst = function.inst.operands[1].inst
    assert func_type_inst.op_name == 'OpTypeFunction'
    params = func_type_inst.operands[1:]
    while True:
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            lexer.done_with_line()
            continue

        inst = parse_instruction(lexer, module)

        if params:
            if (not isinstance(inst, ir.Instruction) or
                    inst.op_name != 'OpFunctionParameter'):
                raise ParseError('Expected OpFunctionParameter')

        if isinstance(inst, ir.BasicBlock):
            parse_basic_block_body(lexer, module, inst)
            function.add_basic_block(inst)
        elif isinstance(inst, ir.Function):
            raise ParseError('OpFunction within function')
        elif inst.op_name == 'OpFunctionEnd':
            return function
        elif inst.op_name == 'OpFunctionParameter':
            if not params:
                raise ParseError('Too many OpFunctionParameter')
            params.pop(0)
            function.append_parameter(inst)
        else:
            raise ParseError('Expected a new label or OpFunctionEnd')


def parse_parameters(lexer, module):
    """Parse the parameters of a pretty-printed function."""
    parameters = []
    lexer.get_next_token('(')
    token, _ = lexer.get_next_token(peek=True)
    if token == 'void':
        lexer.get_next_token('void')
    else:
        while lexer.get_next_token(peek=True) != (')', None):
            param_type = parse_type(lexer, module)
            param_id = parse_id(lexer, module)
            parameters.append((param_type, param_id))
            if lexer.get_next_token(peek=True) == (',', None):
                lexer.get_next_token()
                if lexer.get_next_token(peek=True) == (')', None):
                    raise ParseError('Expected parameter after ","')
    lexer.get_next_token(')')
    return parameters


def parse_function_definition(lexer, module):
    """Parse the 'definition' line of a pretty-printed function."""
    lexer.get_next_token('define')
    return_type = parse_type(lexer, module)
    function_id = parse_id(lexer, module)
    parameters = parse_parameters(lexer, module)

    if function_id.inst is not None:
        id_name = get_id_name(module, function_id)
        raise ParseError(id_name + ' is already defined')

    function_type = get_or_create_function_type(module, return_type,
                                                parameters)
    function = ir.Function(module, function_id, 0, function_type) # XXX
    for (param_type, param_id) in parameters:
        param_inst = ir.Instruction(module, 'OpFunctionParameter', param_id,
                                    param_type, [])
        function.append_parameter(param_inst)

    return function


def parse_function(lexer, module):
    """Parse a pretty-printed function."""
    func = parse_function_definition(lexer, module)

    while True:
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            lexer.done_with_line()
        else:
            break
    lexer.get_next_token('{')
    lexer.done_with_line()

    while True:
        token, tag = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            lexer.done_with_line()
        elif token == '}':
            lexer.get_next_token()
            lexer.done_with_line()
            return func
        elif tag == 'LABEL':
            parse_basic_block(lexer, module, func)
        else:
            raise ParseError('Expected a label or }')


def get_id_name(module, id_to_check):
    """Return the ID name if defined, otherwise return the numbered ID."""
    for name in module.symbol_name_to_id:
        if module.symbol_name_to_id[name] == id_to_check:
            return name
    return str(id_to_check)


def verify_id(module, inst, id_to_check):
    """Verify that the ID is defined in a user-defined instruction.

    Raise an 'used but not defined' exception if the ID is not defined for
    a user-defined instruction (i.e. an instruction that has a line number).
    Instructions introduced by the implementation are ignored (e.g. an
    OpName instruction that was inserted because a user-defined instruction
    used an undefined named ID) as the error will be reported for a
    user-defined instruction anyway.
    """
    if inst in module.inst_to_line:
        if id_to_check.inst is None:
            id_name = get_id_name(module, id_to_check)
            line_no = module.inst_to_line[inst]
            raise VerificationError(line_no, id_name + ' used but not defined')


def verify_ids_are_defined(module):
    """Verify that all IDs in user-defined instructions are defined."""
    for inst in module.instructions():
        if inst.result_id is not None:
            verify_id(module, inst, inst.result_id)
        if inst.type_id is not None:
            verify_id(module, inst, inst.type_id)
        for operand in inst.operands:
            if isinstance(operand, ir.Id):
                verify_id(module, inst, operand)


def read_module(stream):
    """Create a module from the IL read from the stream."""
    module = ir.Module()
    module.type_name_to_id = {}
    module.id_to_type_name = {}
    module.symbol_name_to_id = {}
    module.inst_to_line = {}
    lexer = Lexer(stream)
    try:
        parse_translation_unit(lexer, module)
        verify_ids_are_defined(module)
        module.finalize()
        return module
    except (ParseError, ir.IRError) as err:
        raise ParseError(str(lexer.line_no) + ': error: ' + err.message)
    except VerificationError as err:
        raise ParseError(str(err.line_no) + ': error: ' + err.message)
    finally:
        del module.inst_to_line
        del module.symbol_name_to_id
        del module.id_to_type_name
        del module.type_name_to_id
