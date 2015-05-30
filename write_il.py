import re
import sys

import spirv

def output_instruction(stream, module, instr, is_raw_mode, indent='  '):
    """Output one instruction."""
    line = indent
    if instr.result_id is not None:
        line = line + instr.result_id + ' = '
    line = line + instr.op_name
    if instr.type is not None:
        line = line + ' ' + module.type_id_to_name[instr.type]

    if not is_raw_mode:
        line = line + format_decorations_for_instr(module, instr)

    if instr.operands:
        line = line + ' '
        for operand in instr.operands:
            if operand in module.id_to_alias:
                operand = module.id_to_alias[operand]
            if operand in module.type_id_to_name:
                operand = module.type_id_to_name[operand]
            line = line + operand + ', '
        line = line[:-2]

    stream.write(line + '\n')


def get_decorations(module, instr_id):
    decorations = []
    for instr in module.global_instructions:
        if instr.op_name == 'OpDecorate' and instr.operands[0] == instr_id:
            decorations.append(instr)
    return decorations


def get_symbol_name(module, symbol_id):
    if symbol_id in module.id_to_alias:
        return module.id_to_alias[symbol_id]

    for instr in module.global_instructions:
        if instr.op_name == 'OpName' and instr.operands[0] == symbol_id:
            name = instr.operands[1]
            name = name[1:-1]

            # glslang tend to add type information to function names.
            # E.g. "foo(vec4)" get the symbol name "foo(vf4;"
            # Truncate such names to fit our IL.
            regex = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*')
            match = regex.match(name)
            new_name = match.group(0)
            if new_name != name:
                sys.stderr.write('warning: truncated symbol name "'
                                 + name + '" to "' + new_name + '"\n')

            symbol_name = '@' + new_name
            break
    else:
        symbol_name = '@' + symbol_id[1:]

    module.id_to_alias[symbol_id] = symbol_name
    module.alias_to_id[symbol_name] = symbol_id

    return symbol_name


def format_decoration(decoration_instr):
    res = decoration_instr.operands[1]
    if decoration_instr.operands[2:]:
        res = res + '('
        for param in decoration_instr.operands[2:]:
            res = res + param + ', '
        res = res[:-2] + ')'
    return res


def format_decorations_for_instr(module, instr):
    line = ''
    decorations = get_decorations(module, instr.result_id)
    for decoration in decorations:
        line = line + ' ' + format_decoration(decoration)
    return line


def output_global_variable(stream, module, instr):
    """Output one global variable."""
    assert instr.op_name == 'OpVariable'
    ptr_instr = module.id_to_instruction[instr.type]
    assert ptr_instr.operands[0] == instr.operands[0]  # Verify storage class
    variable_type = module.type_id_to_name[ptr_instr.operands[1]]
    symbol_name = get_symbol_name(module, instr.result_id)
    line = symbol_name + ' = ' + instr.operands[0] + ' ' + variable_type

    line = line + format_decorations_for_instr(module, instr)

    stream.write(line + '\n')


def add_type_if_needed(module, instr, needed_types):
    if instr.op_name in spirv.TYPE_DECLARATION_INSTRUCTIONS:
        if instr.op_name != 'OpTypeFunction':
            if module.type_id_to_name[instr.result_id] == instr.result_id:
                needed_types.add(instr.result_id)
        for operand in instr.operands:
            if operand[0] == '%':
                type_instr = module.id_to_instruction[operand]
                add_type_if_needed(module, type_instr, needed_types)
    if instr.type is not None:
        if module.type_id_to_name[instr.type] == instr.type:
            needed_types.add(instr.type)


def get_needed_types(module):
    needed_types = set()
    for instr in module.instructions():
        if instr.op_name == 'OpVariable' and instr in module.global_instructions:
            type_instr = module.id_to_instruction[instr.type]
            assert type_instr.op_name == 'OpTypePointer'
            ptr_type_instr = module.id_to_instruction[type_instr.operands[1]]
            add_type_if_needed(module, ptr_type_instr, needed_types)
        elif instr.op_name not in spirv.TYPE_DECLARATION_INSTRUCTIONS:
            add_type_if_needed(module, instr, needed_types)
    return needed_types


def output_global_instructions(stream, module, is_raw_mode, names, newline=True):
    for instr in module.global_instructions:
        if instr.op_name in names:
            if newline:
                stream.write('\n')
                newline = False
            output_instruction(stream, module, instr, is_raw_mode, indent='')


def output_basic_block(stream, module, basic_block):
    """Output one basic block."""
    stream.write(basic_block.instr.result_id + ':\n')
    for instr in basic_block.instrs:
        output_instruction(stream, module, instr, False)


def output_function_raw(stream, module, func):
    """Output one function (raw mode)."""
    stream.write('\n')
    noindent_names = ['OpFunction', 'OpLabel', 'OpFunctionParameter',
                      'OpFunctionEnd']
    for instr in func.instructions():
        if instr.op_name in noindent_names:
            indent = ''
        else:
            indent = '  '
        output_instruction(stream, module, instr, True, indent=indent)


def output_function(stream, module, func):
    """Output one function (pretty-printed mode)."""
    stream.write('\n')
    symbol_name = get_symbol_name(module, func.instr.result_id)
    line = 'define ' + module.type_id_to_name[func.instr.type] + ' '
    line = line + symbol_name + '('
    for instr in func.arguments:
        line = line + module.type_id_to_name[instr.type]
        line = line + ' ' + instr.result_id + ', '
    if line[-2:] == ', ':
        line = line[:-2]
    line = line + ') {\n'
    stream.write(line)

    for basic_block in func.basic_blocks:
        if basic_block != func.basic_blocks[0]:
            stream.write('\n')
        output_basic_block(stream, module, basic_block)

    stream.write('}\n')


def output_functions(stream, module, is_raw_mode):
    """Output all functions."""
    for func in module.functions:
        if is_raw_mode:
            output_function_raw(stream, module, func)
        else:
            output_function(stream, module, func)


def generate_function_symbols(module):
    """Add all function names to the symbol table."""
    for func in module.functions:
        get_symbol_name(module, func.instr.result_id)


def write_module(stream, module, is_raw_mode):
    output_order = ['OpSource',
                    'OpSourceExtension',
                    'OpCompileFlag',
                    'OpExtension',
                    'OpMemoryModel',
                    'OpEntryPoint',
                    'OpExecutionMode']

    if not is_raw_mode:
        generate_function_symbols(module)

    for name in output_order:
        output_global_instructions(stream, module, is_raw_mode, [name],
                                   newline=False)
    output_global_instructions(stream, module, is_raw_mode,
                               ['OpExtInstImport'])

    if is_raw_mode:
        output_global_instructions(stream, module, is_raw_mode,
                                   spirv.DEBUG_INSTRUCTIONS)
        output_global_instructions(stream, module, is_raw_mode,
                                   spirv.DECORATION_INSTRUCTIONS)
        output_global_instructions(stream, module, is_raw_mode,
                                   spirv.TYPE_DECLARATION_INSTRUCTIONS)
        output_global_instructions(stream, module, is_raw_mode,
                                   spirv.CONSTANT_INSTRUCTIONS)
        output_global_instructions(stream, module, is_raw_mode,
                                   spirv.GLOBAL_VARIABLE_INSTRUCTIONS)
    else:
        if module.type_declaration_instructions:
            stream.write('\n')
            needed_types = get_needed_types(module)
            for instr in module.type_declaration_instructions:
                if instr.result_id in needed_types:
                    output_instruction(stream, module, instr, is_raw_mode,
                                       indent='')
        output_global_instructions(stream, module, is_raw_mode,
                                   spirv.CONSTANT_INSTRUCTIONS)
        if module.global_variable_instructions:
            stream.write('\n')
            for instr in module.global_variable_instructions:
                output_global_variable(stream, module, instr)

    output_functions(stream, module, is_raw_mode)
