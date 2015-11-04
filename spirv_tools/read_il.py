"""Create a module from high-level assembly read from a stream."""
import re
from operator import itemgetter

from spirv_tools import ext_inst
from spirv_tools import spirv
from spirv_tools import ir


class ParseError(Exception):
    """Raised when encountering invalid constructs while parsing."""


class VerificationError(Exception):
    """Raised when encountering invalid SPIR-V when sanity checking module."""
    def __init__(self, line_no, message):
        super(VerificationError, self).__init__(message)
        self.line_no = line_no


class Lexer(object):
    """This class represents the assembly file being parsed."""
    def __init__(self, stream):
        token_exprs = [
            (r'%([1-9][0-9]*|[a-zA-Z_][a-zA-Z0-9_]*):', 'LABEL'),
            (r'%([1-9][0-9]*|[a-zA-Z_][a-zA-Z0-9_]*)', 'ID'),
            (r'[a-zA-Z][a-zA-Z0-9.]*', 'NAME'),
            (r'[,={}\(\)|]', None),
            (r'<[1-9]+ x [a-zA-Z0-9]*>', 'VEC_TYPE'),
            (r'-?(0b[01]+|0x[0-9a-fA-F]+|[1-9][0-9]*|0)', 'INT'),
            (r'".*"', 'STRING')
        ]
        self.stream = stream
        self.line = None
        self.line_no = 0
        self.peeked_value = (None, None)
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
        token, tag = self.peeked_value
        if token is not None:
            if not peek:
                self.peeked_value = (None, None)
            if expect is not None and token != expect:
                raise ParseError('Expected ' + expect)
            return token, tag

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
                self.line = self.line[match.end(0):]
                if peek:
                    self.peeked_value = (token, tag)
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


def get_scalar_value(token, tag, type_id):
    """Return a value from token representing a scalar constant."""
    if tag == 'INT':
        if type_id.inst.op_name != 'OpTypeInt':
            raise ParseError('Type must be OpTypeInt')
        min_val, max_val = ir.get_int_type_range(type_id)
        value = get_integer_value(token, min_val, max_val)
    elif token in ['true', 'false']:
        if type_id.inst.op_name != 'OpTypeBool':
            raise ParseError('Type must be OpTypeBool')
        value = (token == 'true')
    else:
        raise ParseError('Expected an integer or true/false')
    return value


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
            new_id = ir.Id(module)
            module.symbol_name_to_id[token] = new_id
            name = token[1:]
            inst = ir.Instruction(module, 'OpName', None, [new_id, name])
            module.insert_global_inst(inst)
        else:
            value = int(token[1:])
            if value in module.value_to_id:
                return module.value_to_id[value]
            new_id = ir.Id(module, value)
            module.value_to_id[value] = new_id
        return new_id
    elif tag == 'INT' or token in ['true', 'false']:
        value = get_scalar_value(token, tag, type_id)
        inst = module.get_constant(type_id, value)
        return inst.result_id
    elif token in module.type_name_to_id:
        return module.type_name_to_id[token]
    else:
        return get_or_create_type(module, token)


def parse_vector_const(lexer, module, token, type_id):
    """Parse a vector constant."""
    if type_id.inst.op_name != 'OpTypeVector':
        raise ParseError('Type must be OpTypeVector')
    elements = []
    while True:
        token, tag = lexer.get_next_token()
        elements.append(get_scalar_value(token, tag, type_id.inst.operands[0]))
        token, _ = lexer.get_next_token()
        if token == ')':
            break
        elif token != ',':
            raise ParseError('Expected , or )')
    inst = module.get_constant(type_id, elements)
    return inst.result_id


def parse_id(lexer, module, accept_eol=False, type_id=None):
    """Parse one ID.

    This parses generalized Id's, so it accepts e.g. type names such as 'f32'
    where the ID for the 'OpTypeFloat' is returned.  See 'create_id' for
    which generalizations are accepted.
    """
    token, tag = lexer.get_next_token(accept_eol=accept_eol)
    if accept_eol and token == '':
        return None
    elif token == '(':
        return parse_vector_const(lexer, module, token, type_id)
    else:
        return create_id(module, token, tag, type_id)


def get_integer_value(token, min_val, max_val):
    """Get the value in the range [min_val, max_val] from an INT token."""
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
    if value < min_val or value > max_val:
        raise ParseError('Value out of range')
    return value


def parse_literal_number(lexer):
    """Parse one LiteralNumber operand."""
    token, tag = lexer.get_next_token()
    if tag != 'INT':
        raise ParseError('Expected an integer literal')
    return get_integer_value(token, 0, 0xffffffff)


def expand_mask(kind, value):
    """Format the mask as a list of mask strings."""
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


def parse_mask(lexer, kind):
    """Parse one mask kind."""
    value = 0
    while True:
        token, tag = lexer.get_next_token(peek=True)
        if tag == 'INT':
            tok_value = parse_literal_number(lexer)
        else:
            token, tag = lexer.get_next_token()
            if token not in spirv.spv[kind]:
                raise ParseError('Unknown mask value ' + token +
                                 ' for ' + kind)
            tok_value = spirv.spv[kind][token]
        value = value | tok_value
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token != '|':
            break
        lexer.get_next_token('|')

    return expand_mask(kind, value)


def get_or_create_type(module, token):
    """Return a type inst corresponding to the token.

    An already existing type instruction is returned if it exists, otherwise
    a new instruction is created and added to the global instructions.
    """
    if not token in module.type_name_to_id:
        if token == 'void':
            inst = module.get_global_inst('OpTypeVoid', None, [])
        elif token == 'bool':
            inst = module.get_global_inst('OpTypeBool', None, [])
        elif token in ['s8', 's16', 's32', 's64']:
            width = int(token[1:])
            inst = module.get_global_inst('OpTypeInt', None, [width, 1])
        elif token in ['u8', 'u16', 'u32', 'u64']:
            width = int(token[1:])
            inst = module.get_global_inst('OpTypeInt', None, [width, 0])
        elif token in ['f16', 'f32', 'f64']:
            width = int(token[1:])
            inst = module.get_global_inst('OpTypeFloat', None, [width])
        elif token[0] == '<':
            assert token[-1] == '>'
            nof_elem, _, base_type = token[1:-1].partition(' x ')
            base_type_id = get_or_create_type(module, base_type)
            inst = module.get_global_inst('OpTypeVector', None,
                                          [base_type_id, int(nof_elem)])
        else:
            raise ParseError('Not a valid type: ' + token)

        module.type_name_to_id[token] = inst.result_id

    return module.type_name_to_id[token]


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


def parse_var_operand(lexer, module, kind, type_id):
    """Parse one instruction operand of the specified var/optional kind.

    The var/optional kind may be realized by multiple "real" operands, so
    the result is returned as a list.

    Operands of the 'Id' kind may be a literal, in which case a constant
    inst is created using the type in type_id.
    """
    if kind == 'VariableLiterals' or kind == 'OptionalLiteral':
        kinds = ['LiteralNumber']
    elif kind == 'VariableIds' or kind == 'OptionalId':
        kinds = ['Id']
    elif kind == 'VariableIdLiteral':
        kinds = ['Id', 'LiteralNumber']
    elif kind == 'VariableLiteralId':
        kinds = ['LiteralNumber', 'Id']
    else:
        raise Exception("Invalid kind " + str(kind))

    operands = []
    while True:
        tmp_kinds = kinds[:]
        while tmp_kinds:
            kind = tmp_kinds.pop(0)
            if kind == 'Id':
                operands.append(parse_id(lexer, module, type_id=type_id))
            elif kind == 'LiteralNumber':
                operands.append(parse_literal_number(lexer))

            if tmp_kinds:
                lexer.get_next_token(',')

        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            break
        lexer.get_next_token(',')
    return operands


def parse_extinst_set(lexer, module):
    """Parse the set field of OpExtInst instruction."""
    token, tag = lexer.get_next_token()
    if tag == 'ID':
        extimport_id = create_id(module, token, tag)
        if (extimport_id.inst is None or
                extimport_id.inst.op_name != 'OpExtInstImport'):
            raise ParseError('ID is not an OpExtInstImport instruction.')
        return extimport_id
    elif tag == 'STRING':
        assert token[0] == '"' and token[-1] == '"'
        inst = module.get_global_inst('OpExtInstImport', None, [token[1:-1]])
        return inst.result_id
    else:
        raise ParseError('Expected an extended instruction set ID or string.')


def parse_extinst_instruction(lexer, set_id):
    """Parse instruction field of OpExtInst instruction."""
    assert set_id.inst.op_name == 'OpExtInstImport'
    _, tag = lexer.get_next_token(peek=True)
    if tag == 'INT':
        return parse_literal_number(lexer)
    elif tag == 'NAME':
        token, _ = lexer.get_next_token()
        if set_id.inst.operands[0] not in ext_inst.EXT_INST:
            return ParseError('Unknown extended instruction set.')
        ext_ops = ext_inst.EXT_INST[set_id.inst.operands[0]]
        for operation in ext_ops:
            if ext_ops[operation]['name'] == token:
                return operation
        raise ParseError('Unknown instruction.')
    else:
        raise ParseError('Expected an integer or operation name.')


def parse_extinst_operands(lexer, module, type_id):
    """Parse operands for an OpExtInst instruction."""
    set_id = parse_extinst_set(lexer, module)
    lexer.get_next_token(',')
    instruction = parse_extinst_instruction(lexer, set_id)
    lexer.get_next_token(',')
    operands = parse_operand(lexer, module, 'VariableIds', type_id)
    return [set_id, instruction] + operands


def parse_operand(lexer, module, kind, type_id):
    """Parse one instruction operand of the specified kind.

    Operands of the 'Id' kind may be a literal, in which case a constant
    inst is created using the type in type_id.
    """
    if kind == 'Id':
        operands = [parse_id(lexer, module, type_id=type_id)]
    elif kind == 'LiteralNumber':
        operands = [parse_literal_number(lexer)]
    elif kind in ir.MASKS:
        operands = [parse_mask(lexer, kind)]
    elif kind in ['VariableLiterals', 'OptionalLiteral', 'VariableIds',
                  'OptionalId', 'VariableIdLiteral', 'VariableLiteralId']:
        operands = parse_var_operand(lexer, module, kind, type_id)
    elif kind == 'LiteralString':
        token, tag = lexer.get_next_token()
        if tag != 'STRING':
            raise ParseError('Expected a string literal')
        operands = [token[1:-1]]
    elif kind == 'OptionalImage':
        operands = []
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token != '':
            operands.append(parse_literal_number(lexer))
            token, _ = lexer.get_next_token(peek=True, accept_eol=True)
            if token == ',':
                lexer.get_next_token()
                operands = operands + parse_var_operand(lexer, module,
                                                        'VariableIds', type_id)
    elif kind in spirv.spv:
        value, _ = lexer.get_next_token()
        if value not in spirv.spv[kind]:
            error = 'Invalid value ' + value + ' for ' + kind
            raise ParseError(error)
        operands = [value]
    else:
        raise ParseError('Unknown parameter kind "' + kind + '"')
    return operands


def parse_operands(lexer, module, op_format, type_id):
    """Parse operands for one instruction."""
    operands = []
    kinds = op_format['operands'][:]
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
                        'VariableIds', 'OptionalImage', 'VariableIdLiteral',
                        'VariableLiteralId']:
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
    if op_name not in ir.INST_FORMAT:
        raise ParseError('Invalid operation ' + op_name)
    op_format = ir.INST_FORMAT[op_name]
    if op_format['type']:
        type_id = parse_type(lexer, module)
    else:
        type_id = None

    parse_decorations(lexer, module, result_id, op_name)
    if op_name == 'OpExtInst':
        operands = parse_extinst_operands(lexer, module, type_id)
    else:
        operands = parse_operands(lexer, module, op_format, type_id)
    lexer.done_with_line()

    if op_name == 'OpFunction':
        function = ir.Function(module, operands[0], operands[1],
                               result_id=result_id)
        module.inst_to_line[function.inst] = lexer.line_no
        module.inst_to_line[function.end_inst] = lexer.line_no
        return function
    elif op_name == 'OpLabel':
        basic_block = ir.BasicBlock(module, result_id)
        module.inst_to_line[basic_block.inst] = lexer.line_no
        return basic_block
    else:
        inst = ir.Instruction(module, op_name, type_id, operands,
                              result_id=result_id)
        module.inst_to_line[inst] = lexer.line_no
        return inst


def parse_decorations(lexer, module, variable_name, op_name):
    """Parse pretty-printed decorations."""
    while True:
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        if token == '':
            return
        elif token not in spirv.spv['Decoration']:
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
        if not decoration in spirv.spv['Decoration']:
            raise ParseError('Unknown decoration ' + decoration)
        token, _ = lexer.get_next_token(peek=True, accept_eol=True)
        operands = [variable_name, decoration]
        if token == '(':
            lexer.get_next_token()
            while True:
                operands.append(parse_literal_number(lexer))
                token, _ = lexer.get_next_token()
                if token == ')':
                    break
                if token != ',':
                    raise ParseError('Syntax error in decoration')
        inst = ir.Instruction(module, 'OpDecorate', None, operands)
        module.insert_global_inst(inst)


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
            module.append_function(func)
        else:
            inst = parse_instruction(lexer, module)
            if isinstance(inst, ir.Function):
                func = parse_function_raw(lexer, module, inst)
                module.append_function(func)
            elif isinstance(inst, ir.BasicBlock):
                raise ParseError('Basic block defined outside a function')
            else:
                module.insert_global_inst(inst)


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
    function.append_basic_block(basic_block)


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
            function.append_basic_block(inst)
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
    result_id = parse_id(lexer, module)
    parameters = parse_parameters(lexer, module)

    if result_id.inst is not None:
        id_name = get_id_name(module, result_id)
        raise ParseError(id_name + ' is already defined')

    operands = [return_type] + [param[0] for param in parameters]
    function_type_inst = module.get_global_inst('OpTypeFunction', None,
                                                operands)
    function = ir.Function(module, [], function_type_inst.result_id,
                           result_id=result_id) # XXX
    for (param_type, param_id) in parameters:
        param_inst = ir.Instruction(module, 'OpFunctionParameter', param_type,
                                    [], result_id=param_id)
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
    if id_to_check.inst is None:
        if inst in module.inst_to_line:
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
    module.symbol_name_to_id = {}
    module.inst_to_line = {}
    module.value_to_id = {}
    lexer = Lexer(stream)
    try:
        parse_translation_unit(lexer, module)
        verify_ids_are_defined(module)
        return module
    except (ParseError, ir.IRError) as err:
        raise ParseError(str(lexer.line_no) + ': error: ' + err.message)
    except VerificationError as err:
        raise ParseError(str(err.line_no) + ': error: ' + err.message)
    finally:
        del module.value_to_id
        del module.inst_to_line
        del module.symbol_name_to_id
        del module.type_name_to_id
