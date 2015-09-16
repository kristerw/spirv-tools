"""Combine/simplify instructions, to fewer/simpler instructions

This pass tends to leave dead instructions, so dead_code_elim should
be run after."""
import ir
import constprop


def optimize_OpVectorShuffle(module, inst):
    vec1_inst = module.id_to_inst[inst.operands[0]]
    vec2_inst = module.id_to_inst[inst.operands[1]]
    components = inst.operands[2:]

    # Change vectors shuffles "A, undef" or "undef, A" to "A, A" where
    # the second operand is not used.
    #
    # We use this form for swizzles, as it avoids extra operations for
    # the OpUndef, and it makes the constant folder handle this for
    # constant A, without needed it to special case OpUndef operands.
    if vec2_inst.op_name == 'OpUndef':
        vec2_inst = vec1_inst
    elif vec1_inst.op_name == 'OpUndef':
        vec1_type_inst = module.id_to_inst[vec1_inst.type_id]
        assert vec1_type_inst.op_name == 'OpTypeVector'
        vec1_len = vec1_type_inst.operands[1]
        for idx in range(len(components)):
            if components[idx] != 0xffffffff:
                components[idx] = components[idx] - vec1_len
        vec1_inst = vec2_inst

    # Change shuffle "A, A" so that only the first is used.
    if vec1_inst == vec2_inst:
        vec1_type_inst = module.id_to_inst[vec1_inst.type_id]
        assert vec1_type_inst.op_name == 'OpTypeVector'
        vec1_len = vec1_type_inst.operands[1]
        for idx in range(len(components)):
            if components[idx] != 0xffffffff and components[idx] >= vec1_len:
                components[idx] = components[idx] - vec1_len

    # Eliminate identity swizzles.
    if vec1_inst == vec2_inst:
        if inst.type_id == vec1_inst.type_id:
            for idx in range(len(components)):
                if components[idx] != 0xffffffff and components[idx] != idx:
                    break
            else:
                return vec1_inst

    # Create new inst if we have changed the instruction.
    operands = [vec1_inst.result_id, vec2_inst.result_id] + components
    if cmp(operands, inst.operands) != 0:
        new_inst = ir.Instruction(module, 'OpVectorShuffle', module.new_id(),
                                  inst.type_id, operands)
        new_inst.insert_before(inst)
        return new_inst

    return inst


def optimize_inst(module, inst):
    """Simplify one instruction"""
    if inst.op_name == 'OpVectorShuffle':
        inst = optimize_OpVectorShuffle(module, inst)

    # It is common that the simplified instruction can be constant
    # folded, or constant folded instructions can give opportunities
    # for simplification.  We therefore run constprop here instead
    # of needing to iterate constprop and instcombine  passes until
    # the result stabilizes.
    inst = constprop.optimize_inst(module, inst)

    return inst


def optimize(module):
    """Combine/simplify instructions, to fewer/simpler instructions"""
    for function in module.functions:
        for inst in function.instructions():
            optimized_inst = optimize_inst(module, inst)
            if optimized_inst != inst:
                inst.replace_uses_with(optimized_inst)
    module.finalize()
