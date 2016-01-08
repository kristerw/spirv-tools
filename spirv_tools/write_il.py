"""Write module to a stream as high-level assembler."""
import re

from spirv_tools import ext_inst
from spirv_tools import spirv
from spirv_tools import ir


def id_name(module, operand):
    """Return a pretty-printed name for the ID."""
    if operand in module.id_to_symbol_name:
        return module.id_to_symbol_name[operand]
    elif operand in module.type_id_to_name:
        return module.type_id_to_name[operand]
    else:
        return str(operand)


def format_mask(kind, mask_list):
    """Format the list of mask strings as the assembly syntax."""
    if not mask_list:
        return [val for val in spirv.spv[kind] if spirv.spv[kind][val] == 0][0]
    separator = ' | '
    return separator.join(mask_list)


def output_extinst_instruction(stream, module, inst, is_raw_mode, indent='  '):
    """Output an OpExtInst instruction."""
    assert inst.op_name == 'OpExtInst'
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

    operand = inst.operands[0]
    assert operand.inst.op_name == 'OpExtInstImport'
    import_name = operand.inst.operands[0]
    if is_raw_mode:
        line = line + ' ' + id_name(module, operand) + ', '
    else:
        line = line + ' "' + import_name + '", '

    operand = inst.operands[1]
    if import_name in ext_inst.EXT_INST:
        line = line + ext_inst.EXT_INST[import_name][operand]['name'] + ', '
    else:
        line = line + str(operand) + ', '

    operands = inst.operands[2:]
    for operand in operands:
        line = line + id_name(module, operand) + ', '
    line = line[:-2]

    stream.write(line + '\n')


def output_instruction(stream, module, inst, is_raw_mode, indent='  '):
    """Output one instruction."""
    if inst.op_name == 'OpExtInst':
        output_extinst_instruction(stream, module, inst, is_raw_mode,
                                   indent=indent)
        return

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
        operand_kind = zip(inst.operands, op_format['operands'])
        while operand_kind:
            operand, kind = operand_kind[0]
            if kind == 'Id' or kind == 'OptionalId':
                line = line + id_name(module, operand) + ', '
            elif kind == 'LiteralNumber' or kind == 'OptionalLiteralNumber':
                line = line + str(operand) + ', '
            elif kind in ir.MASKS:
                line = line + format_mask(kind, operand) + ', '
            elif kind == 'LiteralString' or kind == 'OptionalLiteralString':
                line = line + '"' + operand + '"' + ', '
            elif kind[:8] == 'Optional' and kind[-4:] == 'Mask':
                line = line + format_mask(kind[8:], operand) + ', '
            elif kind[:8] == 'Variable':
                # This loop handles only one operand/kind per iteration.
                # Handle the variable elements after this loop (this works
                # as they are always the last operands).
                break
            elif kind in spirv.spv:
                line = line + operand + ', '
            else:
                raise Exception('Unhandled kind ' + kind)
            operand_kind = operand_kind[1:]

        while operand_kind:
            operand, kind = operand_kind.pop(0)
            if kind == 'VariableIdLiteralPair':
                operands = inst.operands[(len(op_format['operands'])-1):]
                while operands:
                    line = line + id_name(module, operands.pop(0)) + ', '
                    line = line + str(operands.pop(0)) + ', '
            elif kind == 'VariableId':
                operands = inst.operands[(len(op_format['operands'])-1):]
                for operand in operands:
                    line = line + id_name(module, operand) + ', '
            elif kind == 'VariableLiteralIdPair':
                operands = inst.operands[(len(op_format['operands'])-1):]
                while operands:
                    line = line + str(operands.pop(0)) + ', '
                    line = line + id_name(module, operands.pop(0)) + ', '
            elif kind == 'VariableLiteralNumber':
                operands = inst.operands[(len(op_format['operands'])-1):]
                for operand in operands:
                    line = line + str(operand) + ', '
            else:
                raise Exception('Unhandled kind ' + kind)

        line = line[:-2]

    stream.write(line + '\n')


def get_symbol_name(module, symbol_id):
    """Return a pretty printed name for the symbol_id if available.

    The pretty printed name is created from OpName decorations for the
    symbol_id if available, otherwise a numerical ID (e.g. '%23') is
    returned.

    Names are not unique in SPIR-V, so it is possible that several IDs
    have the same name in their OpName decoration. This function will
    return that name for the first ID found, and the rest will get a
    numerical name."""
    if symbol_id in module.id_to_symbol_name:
        return module.id_to_symbol_name[symbol_id]

    for inst in module.global_instructions.name_insts:
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
                # possible, as the decorations we are using for symbol
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
    """Return a string of a pretty-printed decoration instruction."""
    res = decoration_inst.operands[1]
    if decoration_inst.operands[2:]:
        res = res + '('
        for param in decoration_inst.operands[2:]:
            res = res + str(param) + ', '
        res = res[:-2] + ')'
    return res


def format_decorations_for_inst(inst):
    """Return a string of the decorations for inst."""
    line = ''
    if inst.result_id is not None:
        decorations = inst.get_decorations()
        for decoration in decorations:
            line = line + ' ' + format_decoration(decoration)
    return line


def add_type_if_needed(module, inst, needed_types):
    """Add this type inst to the needed_types set if it is needed.

    The type instruction is needed if it is used by the module, and it
    cannot be pretty-printed.

    The types needed by this type are added recursively."""
    if inst not in needed_types:
        if inst.op_name != 'OpTypeFunction':
            if module.type_id_to_name[inst.result_id] == str(inst.result_id):
                needed_types.add(inst)
        for operand in inst.operands:
            if isinstance(operand, ir.Id):
                if operand.inst.op_name in ir.TYPE_DECLARATION_INSTRUCTIONS:
                    add_type_if_needed(module, operand.inst, needed_types)


def get_needed_types(module):
    """Determine the type instruction needed in a pretty-printed IL.

    The type instruction is needed if it is used by the module, and it
    cannot be pretty-printed."""
    needed_types = set()
    for inst in module.instructions():
        if inst.type_id is not None:
            add_type_if_needed(module, inst.type_id.inst, needed_types)
    return needed_types


def output_instructions(stream, module, insts, is_raw_mode, newline=True):
    """Output instructions."""
    if insts and newline:
        stream.write('\n')
    for inst in insts:
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
    """Add function/global variable names to the symbol table."""
    for func in module.functions:
        get_symbol_name(module, func.inst.result_id)
    for inst in module.global_instructions.type_insts:
        if inst.op_name == 'OpVariable':
            get_symbol_name(module, inst.result_id)


def format_type_name(module, inst):
    """Format type as a pretty-printed type name."""
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
    return type_name


def generate_type_names(module):
    """Populate type_id_to_name table with pretty-printed type names."""
    for inst in module.global_instructions.type_insts:
        if inst.op_name in ir.TYPE_DECLARATION_INSTRUCTIONS:
            type_name = format_type_name(module, inst)
            module.type_id_to_name[inst.result_id] = type_name


def write_module(stream, module, is_raw_mode=False):
    """Write module to stream as high-level assembler."""
    module.symbol_name_to_id = {}
    module.id_to_symbol_name = {}
    module.type_id_to_name = {}
    try:
        module.renumber_temp_ids()
        generate_type_names(module)
        if not is_raw_mode:
            generate_global_symbols(module)

        # Output the global instructions.
        #
        # We could do it by just iterating over the instructions and print
        # them in order.  But we want some nicer output, with different
        # types of instructions split into sections (and with unneeded
        # instructions eliminated for non-raw mode), so we need to do some
        # extra work here...
        globals = module.global_instructions
        output_instructions(stream, module, globals.op_source_insts,
                            is_raw_mode, newline=False)
        output_instructions(stream, module, globals.op_source_extension_insts,
                            is_raw_mode, newline=False)
        output_instructions(stream, module, globals.op_capability_insts,
                            is_raw_mode, newline=False)
        output_instructions(stream, module, globals.op_extension_insts,
                            is_raw_mode, newline=False)
        output_instructions(stream, module, globals.op_memory_model_insts,
                            is_raw_mode, newline=False)
        output_instructions(stream, module, globals.op_entry_point_insts,
                            is_raw_mode, newline=False)
        output_instructions(stream, module, globals.op_execution_mode_insts,
                            is_raw_mode, newline=False)

        output_instructions(stream, module, globals.op_extinstimport_insts,
                            is_raw_mode)
        if is_raw_mode:
            output_instructions(stream, module, globals.op_string_insts,
                                is_raw_mode)
            output_instructions(stream, module, globals.name_insts,
                                is_raw_mode)
            output_instructions(stream, module, globals.op_line_insts,
                                is_raw_mode)
            output_instructions(stream, module, globals.decoration_insts,
                                is_raw_mode)
            output_instructions(stream, module, globals.type_insts,
                                is_raw_mode)
        else:
            needed_types = get_needed_types(module)
            type_insts = []
            for inst in globals.type_insts:
                if (inst.op_name in ir.TYPE_DECLARATION_INSTRUCTIONS and
                        inst in needed_types):
                    type_insts.append(inst)
                if (inst.op_name in ir.CONSTANT_INSTRUCTIONS or
                        inst.op_name in ir.SPECCONSTANT_INSTRUCTIONS):
                    type_insts.append(inst)
            output_instructions(stream, module, type_insts, is_raw_mode)

            global_vars = [inst for inst in globals.type_insts
                           if inst.op_name in ir.GLOBAL_VARIABLE_INSTRUCTIONS]
            output_instructions(stream, module, global_vars, is_raw_mode)

        # Output rest of the module.
        output_functions(stream, module, is_raw_mode)
    finally:
        del module.type_id_to_name
        del module.id_to_symbol_name
        del module.symbol_name_to_id
