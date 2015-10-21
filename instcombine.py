"""Combine/simplify instructions, to fewer/simpler instructions

This pass tends to leave dead instructions, so dead_inst_elim should
be run after."""
import ir
import constprop


def optimize_OpBitcast(module, inst):
    # bitcast(bitcast(x)) -> bitcast(x) or x
    operand_inst = inst.operands[0].inst
    if operand_inst.op_name == 'OpBitcast':
        if inst.type_id == operand_inst.operands[0].inst.type_id:
            return operand_inst.operands[0].inst
        else:
            new_inst = ir.Instruction(module, 'OpBitcast', inst.type_id,
                                      [operand_inst.operands[0]])
            new_inst.copy_decorations(inst)
            new_inst.insert_before(inst)
            return new_inst
    return inst


def optimize_OpCompositeConstruct(module, inst):
    # Code of the form
    #   %20 = OpCompositeExtract f32 %19, 0
    #   %21 = OpCompositeExtract f32 %19, 1
    #   %22 = OpCompositeExtract f32 %19, 2
    #   %23 = OpCompositeConstruct <3 x f32> %20, %21, %22
    # can be changed to a OpVectorShuffle if all OpCompositeExtract
    # comes from one or two vectors.
    if inst.type_id.inst.op_name == 'OpTypeVector':
        sources = []
        for operand in inst.operands:
            if operand.inst.op_name != 'OpCompositeExtract':
                break
            src_inst = operand.inst.operands[0].inst
            if src_inst.result_id not in sources:
                if src_inst.type_id.inst.op_name != 'OpTypeVector':
                    break
                sources.append(src_inst.result_id)
            if len(sources) > 2:
                break
        else:
            vec1_id = sources[0]
            vec2_id = sources[0] if len(sources) == 1 else sources[1]
            vec1_len = vec1_id.inst.type_id.inst.operands[1]
            vecshuffle_operands = [vec1_id, vec2_id]
            for operand in inst.operands:
                idx = operand.inst.operands[1]
                if operand.inst.operands[0] != vec1_id:
                    idx = idx + vec1_len
                vecshuffle_operands.append(idx)
            new_inst = ir.Instruction(module, 'OpVectorShuffle',
                                      inst.type_id, vecshuffle_operands)
            new_inst.copy_decorations(inst)
            new_inst.insert_before(inst)
            return new_inst
    return inst


def optimize_OpLogicalNot(inst):
    # not(not(x)) -> x
    operand_inst = inst.operands[0].inst
    if operand_inst.op_name == 'OpLogicalNot':
        return operand_inst.operands[0].inst
    return inst


def optimize_OpNot(inst):
    # not(not(x)) -> x
    operand_inst = inst.operands[0].inst
    if operand_inst.op_name == 'OpNot':
        return operand_inst.operands[0].inst
    return inst


def optimize_OpSNegate(inst):
    # neg(neg(x)) -> x
    operand_inst = inst.operands[0].inst
    if operand_inst.op_name == 'OpSNegate':
        return operand_inst.operands[0].inst
    return inst


def optimize_OpTranspose(inst):
    # transpose(transpose(m)) -> m
    operand_inst = inst.operands[0].inst
    if operand_inst.op_name == 'OpTranspose':
        return operand_inst.operands[0].inst
    return inst


def optimize_OpVectorShuffle(module, inst):
    vec1_inst = inst.operands[0].inst
    vec2_inst = inst.operands[1].inst
    components = inst.operands[2:]

    # Change vectors shuffles "A, unused" or "unused, A" to "A, A" where
    # the second operand is not used.
    #
    # We use this form for swizzles instead of using an OpUndef for the
    # unused vector, as it avoids adding extra operations for the OpUndef,
    # and it makes the constant folder handle the shuffle for constant A
    # without needing to special case OpUndef operands.
    using_vec1 = False
    using_vec2 = False
    vec1_type_inst = vec1_inst.type_id.inst
    assert vec1_type_inst.op_name == 'OpTypeVector'
    vec1_len = vec1_type_inst.operands[1]
    for component in components:
        if component != 0xffffffff:
            if component < vec1_len:
                using_vec1 = True
            else:
                using_vec2 = True
    if not using_vec1 and not using_vec2:
        new_inst = ir.Instruction(module, 'OpUndef', inst.type_id, [])
        new_inst.insert_before(inst)
        return new_inst
    elif not using_vec2:
        vec2_inst = vec1_inst
    elif not using_vec1:
        for idx in range(len(components)):
            if components[idx] != 0xffffffff:
                components[idx] = components[idx] - vec1_len
        vec1_inst = vec2_inst

    # Change shuffle "A, A" so that only the first is used.
    if vec1_inst == vec2_inst:
        vec1_type_inst = vec1_inst.type_id.inst
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
    if operands != inst.operands:
        new_inst = ir.Instruction(module, 'OpVectorShuffle', inst.type_id,
                                  operands)
        new_inst.copy_decorations(inst)
        new_inst.insert_before(inst)
        return new_inst

    return inst


def peephole_inst(module, inst):
    """Do peephole optimizations for one instruction."""
    if inst.op_name == 'OpBitcast':
        inst = optimize_OpBitcast(module, inst)
    if inst.op_name == 'OpCompositeConstruct':
        inst = optimize_OpCompositeConstruct(module, inst)
    elif inst.op_name == 'OpLogicalNot':
        inst = optimize_OpLogicalNot(inst)
    elif inst.op_name == 'OpNot':
        inst = optimize_OpNot(inst)
    elif inst.op_name == 'OpSNegate':
        inst = optimize_OpSNegate(inst)
    elif inst.op_name == 'OpTranspose':
        inst = optimize_OpTranspose(inst)
    elif inst.op_name == 'OpVectorShuffle':
        inst = optimize_OpVectorShuffle(module, inst)

    return inst


def optimize_inst(module, inst):
    """Simplify one instruction"""

    # Do peephole kind of optimization. It is possible that the transformed
    # instruction trigger a new optimization rule, so this is iterated until
    # the result cannot be improved.
    while True:
        new_inst = peephole_inst(module, inst)
        if new_inst == inst:
            break
        inst = new_inst

    # It is common that the simplified instruction can be constant folded,
    # or constant folded instructions can give opportunities for simplifying
    # succeeding instructions. We therefore run constprop here instead of
    # needing to iterate constprop and instcombine passes until the result
    # stabilizes.
    inst = constprop.optimize_inst(module, inst)

    return inst


def optimize(module):
    """Combine/simplify instructions, to fewer/simpler instructions"""
    for function in module.functions:
        for inst in function.instructions():
            optimized_inst = optimize_inst(module, inst)
            if optimized_inst != inst:
                inst.replace_uses_with(optimized_inst)
