"""Write module to a stream as a SPIR-V binary."""
import array

from spirv_tools import spirv
from spirv_tools import ir


def mask_to_value(kind, mask_list):
    """Return the value represented by a list of mask strings."""
    value = 0
    for mask in mask_list:
        value = value | spirv.spv[kind][mask]
    return value


def format_var_operand(inst_data, kind, operands):
    """Add a var/optional operand to inst_data.

    A var operand may contain of several operands in the instruction.
    The provided operands list contains the instruction operands for
    this operand."""
    if kind == 'VariableLiteralNumber':
        for operand in operands:
            inst_data.append(operand)
    elif kind == 'VariableId':
        for operand in operands:
            inst_data.append(operand.value)
    elif kind == 'VariableIdLiteralPair':
        while operands:
            target_id = operands.pop(0)
            inst_data.append(target_id.value)
            inst_data.append(operands.pop(0))
    elif kind == 'VariableLiteralIdPair':
        while operands:
            inst_data.append(operands.pop(0))
            target_id = operands.pop(0)
            inst_data.append(target_id.value)


def output_instruction(stream, inst):
    """Output one instruction."""
    inst_data = [0]
    op_format = ir.INST_FORMAT[inst.op_name]

    if op_format['type']:
        inst_data.append(inst.type_id.value)
    if op_format['result']:
        inst_data.append(inst.result_id.value)

    kind = None
    for operand, kind in zip(inst.operands, op_format['operands']):
        if kind == 'Id' or kind == 'OptionalId':
            inst_data.append(operand.value)
        elif kind == 'LiteralNumber' or kind == 'OptionalLiteralNumber':
            inst_data.append(operand)
        elif kind in ir.MASKS:
            inst_data.append(mask_to_value(kind, operand))
        elif kind[:8] == 'Optional' and kind[-4:] == 'Mask':
            inst_data.append(mask_to_value(kind[8:], operand))
        elif kind == 'LiteralString' or kind == 'OptionalLiteralString':
            for i in range(0, len(operand) + 1, 4):
                word = 0
                for char in reversed(operand[i:i+4]):
                    word = word << 8 | ord(char)
                inst_data.append(word)
        elif kind[:8] == 'Variable':
            # The variable kind must be the last (as rest of the operands
            # are included in them.
            operands = inst.operands[(len(op_format['operands'])-1):]
            format_var_operand(inst_data, kind, operands)
        elif kind in spirv.spv:
            constants = spirv.spv[kind]
            inst_data.append(constants[operand])
        else:
            raise Exception('Unhandled kind ' + kind)

    inst_data[0] = (len(inst_data) << 16) + spirv.spv['Op'][inst.op_name]
    words = array.array('I', inst_data)
    words.tofile(stream)


def output_header(stream, module):
    """Output the SPIR-V header."""
    header = [ir.MAGIC, ir.VERSION, ir.GENERATOR_MAGIC, module.bound, 0]
    words = array.array('I', header)
    words.tofile(stream)


def write_module(stream, module):
    """Write module to stream as a SPIR-V binary."""
    module.renumber_temp_ids()
    output_header(stream, module)
    for inst in module.instructions():
        output_instruction(stream, inst)
