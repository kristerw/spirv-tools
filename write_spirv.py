import array

import spirv


def output_instruction(stream, instr):
    """Output one instruction."""
    instr_data = [0]
    opcode = spirv.OPNAME_TABLE[instr.op_name]

    if opcode['type']:
        instr_data.append(int(instr.type[1:]))
    if opcode['result']:
        instr_data.append(int(instr.result_id[1:]))

    kind = None
    for operand, kind in zip(instr.operands, opcode['operands']):
        if kind == 'Id' or kind == 'OptionalId':
            instr_data.append(int(operand[1:]))
        elif kind == 'LiteralNumber':
            instr_data.append(int(operand))
        elif kind in spirv.MASKS:
            instr_data.append(int(operand))
        elif kind == 'LiteralString':
            operand = operand[1:-1]    # Strip '"'
            operand = operand.encode('utf-8') + '\x00'
            for i in range(0, len(operand), 4):
                word = 0
                for char in reversed(operand[i:i+4]):
                    word = word << 8 | ord(char)
                instr_data.append(word)
        elif kind == 'VariableLiterals' or kind == 'VariableIds':
            # The variable kind must be the last (as rest of the operands
            # are included in them.  But loop will only give us one.
            # Handle these after the loop.
            break
        elif kind in spirv.CONSTANTS:
            constants = spirv.CONSTANTS[kind]
            instr_data.append(constants[operand])
        else:
            raise Exception('Unhandled kind "' + kind)

    if kind == 'VariableLiterals':
        operands = instr.operands[(len(opcode['operands'])-1):]
        for operand in operands:
            instr_data.append(int(operand))
    elif kind == 'VariableIds':
        operands = instr.operands[(len(opcode['operands'])-1):]
        for operand in operands:
            instr_data.append(int(operand[1:]))

    instr_data[0] = (len(instr_data) << 16) + opcode['opcode']
    words = array.array('L', instr_data)
    words.tofile(stream)


def output_header(stream, module):
    """Output the SPIR-V header."""
    header = [spirv.MAGIC, spirv.VERSION, spirv.GENERATOR_MAGIC,
              module.bound, 0]
    words = array.array('L', header)
    words.tofile(stream)


def write_module(stream, module):
    output_header(stream, module)
    for instr in module.instructions():
        output_instruction(stream, instr)
