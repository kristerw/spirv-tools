import array

import spirv


def output_instruction(stream, inst):
    """Output one instruction."""
    inst_data = [0]
    opcode = spirv.OPNAME_TABLE[inst.op_name]

    if opcode['type']:
        inst_data.append(inst.type_id.value)
    if opcode['result']:
        inst_data.append(inst.result_id.value)

    kind = None
    for operand, kind in zip(inst.operands, opcode['operands']):
        if kind == 'Id' or kind == 'OptionalId':
            inst_data.append(operand.value)
        elif kind == 'LiteralNumber' or kind == 'SamplerImageFormat':
            inst_data.append(operand)
        elif kind in spirv.MASKS:
            inst_data.append(operand)
        elif kind == 'LiteralString':
            operand = operand[1:-1]    # Strip '"'
            operand = operand.encode('utf-8') + '\x00'
            for i in range(0, len(operand), 4):
                word = 0
                for char in reversed(operand[i:i+4]):
                    word = word << 8 | ord(char)
                inst_data.append(word)
        elif kind in ['VariableLiterals',
                      'OptionalLiteral',
                      'VariableIds',
                      'OptionalImage',
                      'VariableLiteralId']:
            # The variable kind must be the last (as rest of the operands
            # are included in them.  But loop will only give us one.
            # Handle these after the loop.
            break
        elif kind in spirv.CONSTANTS:
            constants = spirv.CONSTANTS[kind]
            inst_data.append(constants[operand])
        else:
            raise Exception('Unhandled kind ' + kind)

    if kind == 'VariableLiterals' or kind == 'OptionalLiteral':
        operands = inst.operands[(len(opcode['operands'])-1):]
        for operand in operands:
            inst_data.append(operand)
    elif kind == 'VariableIds':
        operands = inst.operands[(len(opcode['operands'])-1):]
        for operand in operands:
            inst_data.append(operand.value)
    elif kind == 'OptionalImage':
        operands = inst.operands[(len(opcode['operands'])-1):]
        inst_data.append(operands[0])
        for operand in operands[1:]:
            inst_data.append(operand.value)
    elif kind == 'VariableLiteralId':
        operands = inst.operands[(len(opcode['operands'])-1):]
        while operands:
            inst_data.append(operands.pop(0))
            target_id = operands.pop(0)
            inst_data.append(target_id.value)

    inst_data[0] = (len(inst_data) << 16) + opcode['opcode']
    words = array.array('I', inst_data)
    words.tofile(stream)


def output_header(stream, module):
    """Output the SPIR-V header."""
    header = [spirv.MAGIC, spirv.VERSION, spirv.GENERATOR_MAGIC,
              module.bound, 0]
    words = array.array('I', header)
    words.tofile(stream)


def write_module(stream, module):
    module.finalize()
    output_header(stream, module)
    for inst in module.instructions():
        output_instruction(stream, inst)
