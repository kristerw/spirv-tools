import re
import sys

import ir
import spirv


def output_instruction(stream, module, inst, is_raw_mode, indent='  '):
    """Output one instruction."""
    line = indent
    if inst.result_id is not None:
        result_id = inst.result_id
        if result_id in module.id_to_symbol_name:
            result_id = module.id_to_symbol_name[result_id]
        line = line + result_id + ' = '
    line = line + inst.op_name
    if inst.type_id is not None:
        line = line + ' ' + module.type_id_to_name[inst.type_id]

    if not is_raw_mode:
        line = line + format_decorations_for_inst(module, inst)

    if inst.operands:
        line = line + ' '
        for operand in inst.operands:
            if operand in module.id_to_symbol_name:
                operand = module.id_to_symbol_name[operand]
            if operand in module.type_id_to_name:
                operand = module.type_id_to_name[operand]
            line = line + operand + ', '
        line = line[:-2]

    stream.write(line + '\n')


def get_decorations(module, inst_id):
    decorations = []
    for inst in module.global_insts:
        if inst.op_name == 'OpDecorate' and inst.operands[0] == inst_id:
            decorations.append(inst)
    return decorations


def get_symbol_name(module, symbol_id):
    if symbol_id in module.id_to_symbol_name:
        return module.id_to_symbol_name[symbol_id]

    for inst in module.global_insts:
        if inst.op_name == 'OpName' and inst.operands[0] == symbol_id:
            name = inst.operands[1]
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

            symbol_name = '%' + new_name
            break
    else:
        symbol_name = '%' + symbol_id[1:]

    module.id_to_symbol_name[symbol_id] = symbol_name

    return symbol_name


def format_decoration(decoration_inst):
    res = decoration_inst.operands[1]
    if decoration_inst.operands[2:]:
        res = res + '('
        for param in decoration_inst.operands[2:]:
            res = res + param + ', '
        res = res[:-2] + ')'
    return res


def format_decorations_for_inst(module, inst):
    line = ''
    decorations = get_decorations(module, inst.result_id)
    for decoration in decorations:
        line = line + ' ' + format_decoration(decoration)
    return line


def add_type_if_needed(module, inst, needed_types):
    if inst.op_name in spirv.TYPE_DECLARATION_INSTRUCTIONS:
        if inst.op_name != 'OpTypeFunction':
            if module.type_id_to_name[inst.result_id] == inst.result_id:
                needed_types.add(inst.result_id)
        for operand in inst.operands:
            if operand[0] == '%':
                type_inst = module.id_to_inst[operand]
                add_type_if_needed(module, type_inst, needed_types)
    if inst.type_id is not None:
        if module.type_id_to_name[inst.type_id] == inst.type_id:
            needed_types.add(inst.type_id)


def get_needed_types(module):
    needed_types = set()
    for inst in module.instructions():
        if inst.op_name not in spirv.TYPE_DECLARATION_INSTRUCTIONS:
            add_type_if_needed(module, inst, needed_types)
    return needed_types


def output_global_instructions(stream, module, is_raw_mode, names, newline=True):
    for inst in module.global_insts:
        if inst.op_name in names:
            if newline:
                stream.write('\n')
                newline = False
            output_instruction(stream, module, inst, is_raw_mode, indent='')


def output_basic_block(stream, module, basic_block):
    """Output one basic block."""
    stream.write(basic_block.inst.result_id + ':\n')
    for inst in basic_block.insts:
        output_instruction(stream, module, inst, False)


def output_function_raw(stream, module, func):
    """Output one function (raw mode)."""
    stream.write('\n')
    noindent_names = ['OpFunction', 'OpLabel', 'OpFunctionParameter',
                      'OpFunctionEnd']
    for inst in func.instructions():
        if inst.op_name in noindent_names:
            indent = ''
        else:
            indent = '  '
        output_instruction(stream, module, inst, True, indent=indent)


def output_function(stream, module, func):
    """Output one function (pretty-printed mode)."""
    stream.write('\n')
    symbol_name = get_symbol_name(module, func.inst.result_id)
    line = 'define ' + module.type_id_to_name[func.inst.type_id] + ' '
    line = line + symbol_name + '('
    for inst in func.arguments:
        line = line + module.type_id_to_name[inst.type_id]
        line = line + ' ' + inst.result_id + ', '
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


def generate_global_symbols(module):
    """Add function/global varible names to the symbol table."""
    for func in module.functions:
        get_symbol_name(module, func.inst.result_id)
    for inst in module.global_insts:
        if inst.op_name == 'OpVariable':
            get_symbol_name(module, inst.result_id)


def add_type_name(module, inst):
    if inst.op_name == 'OpTypeVoid':
        type_name = 'void'
    elif inst.op_name == 'OpTypeBool':
        type_name = 'bool'
    elif inst.op_name == 'OpTypeInt':
        width = inst.operands[0]
        if width not in ['8', '16', '32', '64']:
            raise ir.IRError("Invalid OpTypeInt width " + width)
        signedness = inst.operands[1]
        if not signedness in ['0', '1']:
            error = "Invalid OpTypeInt signedness " + str(signedness)
            raise ir.IRError(error)
        type_name = 's' if signedness else 'u'
        type_name = type_name + width
    elif inst.op_name == 'OpTypeFloat':
        width = inst.operands[0]
        if width not in ['16', '32', '64']:
            raise ir.IRError("Invalid OpTypeFloat width " + width)
        type_name = 'f' + width
    elif inst.op_name == 'OpTypeVector':
        component_type = module.type_id_to_name[inst.operands[0]]
        count = inst.operands[1]
        if int(count) not in range(2, 16):
            error = "Invalid OpTypeVector component count " + str(count)
            raise ir.IRError(error)
        type_name = '<' + str(count) + ' x ' + component_type + '>'
    else:
        type_name = inst.result_id

    module.type_id_to_name[inst.result_id] = type_name


def add_type_names(module):
    for inst in module.global_insts:
        if inst.op_name in spirv.TYPE_DECLARATION_INSTRUCTIONS:
            add_type_name(module, inst)


def write_module(stream, module, is_raw_mode=False):
    module.id_to_symbol_name = {}
    module.type_id_to_name = {}

    add_type_names(module)
    if not is_raw_mode:
        generate_global_symbols(module)

    for name in spirv.INITIAL_INSTRUCTIONS:
        if name != 'OpExtInstImport':
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
    else:
        needed_types = get_needed_types(module)
        if needed_types:
            stream.write('\n')
            for inst in module.global_insts:
                if inst.result_id in needed_types:
                    output_instruction(stream, module, inst, is_raw_mode,
                                       indent='')

    output_global_instructions(stream, module, is_raw_mode,
                               spirv.CONSTANT_INSTRUCTIONS)
    output_global_instructions(stream, module, is_raw_mode,
                               spirv.GLOBAL_VARIABLE_INSTRUCTIONS)
    output_functions(stream, module, is_raw_mode)

    del module.type_id_to_name
    del module.id_to_symbol_name
