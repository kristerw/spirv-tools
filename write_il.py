import re
import sys

import spirv
import ir


def id_name(module, operand):
    if operand in module.id_to_symbol_name:
        return module.id_to_symbol_name[operand]
    elif operand in module.type_id_to_name:
        return module.type_id_to_name[operand]
    else:
        return str(operand)


def format_mask(kind, mask_list):
    """Format the list of mask strings as the assembly syntax."""
    if not mask_list:
        return filter(lambda x: spirv.spv[kind][x] == 0, spirv.spv[kind])[0]
    spearator = ' | '
    return spearator.join(mask_list)


def output_instruction(stream, module, inst, is_raw_mode, indent='  '):
    """Output one instruction."""
    line = indent
    if inst.result_id is not None:
        result_id = inst.result_id
        if result_id in module.id_to_symbol_name:
            result_id = module.id_to_symbol_name[result_id]
        line = line + str(result_id) + ' = '
    line = line + inst.op_name
    if inst.type_id is not None:
        line = line + ' ' + module.type_id_to_name[inst.type_id]

    if not is_raw_mode:
        line = line + format_decorations_for_inst(inst)

    op_format = ir.INST_FORMAT[inst.op_name]
    kind = None
    if inst.operands:
        line = line + ' '
        for operand, kind in zip(inst.operands, op_format['operands']):
            if kind == 'Id' or kind == 'OptionalId':
                line = line + id_name(module, operand) + ', '
            elif kind == 'LiteralNumber':
                line = line + str(operand) + ', '
            elif kind in ir.MASKS:
                line = line + format_mask(kind, operand) + ', '
            elif kind == 'LiteralString':
                line = line + '"' + operand + '"' + ', '
            elif kind in ['VariableLiterals',
                          'OptionalLiteral',
                          'VariableIds',
                          'OptionalImage',
                          'VariableIdLiteral',
                          'VariableLiteralId']:
                # The variable kind must be the last (as rest of the operands
                # are included in them.  But loop will only give us one.
                # Handle these after the loop.
                break
            elif kind in spirv.spv:
                line = line + operand + ', '
            else:
                raise Exception('Unhandled kind ' + kind)

        if kind == 'VariableLiterals' or kind == 'OptionalLiteral':
            operands = inst.operands[(len(op_format['operands'])-1):]
            for operand in operands:
                line = line + str(operand) + ', '
        elif kind == 'VariableIds':
            operands = inst.operands[(len(op_format['operands'])-1):]
            for operand in operands:
                line = line + id_name(module, operand) + ', '
        elif kind == 'OptionalImage':
            operands = inst.operands[(len(op_format['operands'])-1):]
            line = line + str(operands[0]) + ', '
            for operand in operands[1:]:
                line = line + id_name(module, operand) + ', '
        elif kind == 'VariableIdLiteral':
            operands = inst.operands[(len(op_format['operands'])-1):]
            while operands:
                line = line + id_name(module, operands.pop(0)) + ', '
                line = line + str(operands.pop(0)) + ', '
        elif kind == 'VariableLiteralId':
            operands = inst.operands[(len(op_format['operands'])-1):]
            while operands:
                line = line + str(operands.pop(0)) + ', '
                line = line + id_name(module, operands.pop(0)) + ', '

        line = line[:-2]

    stream.write(line + '\n')


def get_symbol_name(module, symbol_id):
    if symbol_id in module.id_to_symbol_name:
        return module.id_to_symbol_name[symbol_id]

    for inst in module.global_insts:
        if inst.op_name == 'OpName' and inst.operands[0] == symbol_id:
            name = inst.operands[1]

            # glslang tend to add type information to function names.
            # E.g. "foo(vec4)" get the symbol name "foo(vf4;"
            # Truncate such names to fit our IL.
            regex = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*')
            match = regex.match(name)
            if match is None:
                return '%' + str(symbol_id.value)
            new_name = match.group(0)
            symbol_name = '%' + new_name
            if symbol_name in module.symbol_name_to_id:
                # This name is already used for another ID (which is
                # possible, as the decorations we are ussing for symbol
                # names are not guaranteed to be unique). Let the first
                # ID use this name, and use a numerical name for this ID.
                symbol_name = '%' + str(symbol_id.value)
            break
    else:
        symbol_name = '%' + str(symbol_id.value)

    module.id_to_symbol_name[symbol_id] = symbol_name
    module.symbol_name_to_id[symbol_name] = symbol_id

    return symbol_name


def format_decoration(decoration_inst):
    res = decoration_inst.operands[1]
    if decoration_inst.operands[2:]:
        res = res + '('
        for param in decoration_inst.operands[2:]:
            res = res + str(param) + ', '
        res = res[:-2] + ')'
    return res


def format_decorations_for_inst(inst):
    line = ''
    if inst.result_id is not None:
        decorations = inst.get_decorations()
        for decoration in decorations:
            line = line + ' ' + format_decoration(decoration)
    return line


def add_type_if_needed(module, inst, needed_types):
    """Add this type id to the needed_types set if it is needed.

    The type instruction is needed if it is not pretty-printed, and is used
    by a normal instruction or by a needed type instruction.

    The types needed by this type is added recursively."""
    if inst not in needed_types:
        if inst.op_name != 'OpTypeFunction':
            if module.type_id_to_name[inst.result_id] == str(inst.result_id):
                needed_types.add(inst)
        for operand in inst.operands:
            if isinstance(operand, ir.Id):
                if operand.inst.op_name in ir.TYPE_DECLARATION_INSTRUCTIONS:
                    add_type_if_needed(module, operand.inst, needed_types)


def get_needed_types(module):
    """Determine the type instruction needed in a prety-printed IL.

    The type instruction is needed if it is not pretty-printed, and is used
    by a normal instruction, or used by a needed type instruction."""
    needed_types = set()
    for inst in module.instructions():
        if inst.type_id is not None:
            add_type_if_needed(module, inst.type_id.inst, needed_types)
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
    stream.write(str(basic_block.inst.result_id) + ':\n')
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
    for inst in func.parameters:
        line = line + module.type_id_to_name[inst.type_id]
        line = line + ' ' + str(inst.result_id) + ', '
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
        if width not in [8, 16, 32, 64]:
            raise ir.IRError("Invalid OpTypeInt width " + str(width))
        signedness = inst.operands[1]
        if not signedness in [0, 1]:
            error = "Invalid OpTypeInt signedness " + str(signedness)
            raise ir.IRError(error)
        type_name = 's' if signedness else 'u'
        type_name = type_name + str(width)
    elif inst.op_name == 'OpTypeFloat':
        width = inst.operands[0]
        if width not in [16, 32, 64]:
            raise ir.IRError("Invalid OpTypeFloat width " + str(width))
        type_name = 'f' + str(width)
    elif inst.op_name == 'OpTypeVector':
        component_type = module.type_id_to_name[inst.operands[0]]
        count = inst.operands[1]
        if count not in range(2, 16):
            error = "Invalid OpTypeVector component count " + str(count)
            raise ir.IRError(error)
        type_name = '<' + str(count) + ' x ' + component_type + '>'
    else:
        type_name = str(inst.result_id)

    module.type_id_to_name[inst.result_id] = type_name


def add_type_names(module):
    for inst in module.global_insts:
        if inst.op_name in ir.TYPE_DECLARATION_INSTRUCTIONS:
            add_type_name(module, inst)


def write_module(stream, module, is_raw_mode=False):
    module.symbol_name_to_id = {}
    module.id_to_symbol_name = {}
    module.type_id_to_name = {}
    try:
        module.renumber_temp_ids()
        add_type_names(module)
        if not is_raw_mode:
            generate_global_symbols(module)

        # Output the global instructions.
        #
        # We could do it by just iterating over the instructions and print
        # them in order.  But we want some nicer output, with different
        # types of instructions split into sections (and with unneeded
        # instructions eliminated for non-raw mode), so we need to do some
        # extra work here...
        for name in ir.INITIAL_INSTRUCTIONS:
            if name != 'OpExtInstImport':
                output_global_instructions(stream, module, is_raw_mode, [name],
                                           newline=False)
        output_global_instructions(stream, module, is_raw_mode,
                                   ['OpExtInstImport'])
        if is_raw_mode:
            output_global_instructions(stream, module, is_raw_mode,
                                       ['OpString'])
            output_global_instructions(stream, module, is_raw_mode,
                                       ['OpName', 'OpMemberName'])
            output_global_instructions(stream, module, is_raw_mode,
                                       ['OpLine'])
            output_global_instructions(stream, module, is_raw_mode,
                                       ir.DECORATION_INSTRUCTIONS)
            output_global_instructions(stream, module, is_raw_mode,
                                       ir.TYPE_DECLARATION_INSTRUCTIONS +
                                       ir.CONSTANT_INSTRUCTIONS +
                                       ir.SPECCONSTANT_INSTRUCTIONS +
                                       ir.GLOBAL_VARIABLE_INSTRUCTIONS)
        else:
            needed_types = get_needed_types(module)
            if needed_types:
                stream.write('\n')
                for inst in module.global_insts:
                    if inst in needed_types:
                        output_instruction(stream, module, inst, is_raw_mode,
                                           indent='')
            output_global_instructions(stream, module, is_raw_mode,
                                       ir.CONSTANT_INSTRUCTIONS)
            output_global_instructions(stream, module, is_raw_mode,
                                       ir.SPECCONSTANT_INSTRUCTIONS)
            output_global_instructions(stream, module, is_raw_mode,
                                       ir.GLOBAL_VARIABLE_INSTRUCTIONS)

        # Output rest of the module.
        output_functions(stream, module, is_raw_mode)
    finally:
        del module.type_id_to_name
        del module.id_to_symbol_name
        del module.symbol_name_to_id
