"""Combine/simplify instructions, to fewer/simpler instructions

This pass tends to leave dead instructions, so dead_inst_elim should
be run after."""
from spirv_tools import ir
from spirv_tools.passes import constprop


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


def optimize_OpIAdd(inst):
    # x + 0 -> x
    if inst.operands[1].inst.is_constant_value(0):
        return inst.operands[0].inst
    return inst


def optimize_OpIMul(module, inst):
    # x * 0 -> 0
    if inst.operands[1].inst.is_constant_value(0):
        return inst.operands[1].inst
    # x * 1 -> 1
    if inst.operands[1].inst.is_constant_value(1):
        return inst.operands[0].inst
    # x * -1 -> -x
    if inst.operands[1].inst.is_constant_value(-1):
        new_inst = ir.Instruction(module, 'OpSNegate', inst.type_id,
                                  [inst.operands[0]])
        new_inst.insert_before(inst)
        return new_inst
    return inst


def optimize_OpLogicalAnd(module, inst):
    # x and true -> x
    if inst.operands[1].inst.is_constant_value(True):
        return inst.operands[0].inst
    # x and false -> false
    if inst.operands[1].inst.is_constant_value(False):
        return inst.operands[1].inst
    # x and x -> x
    if inst.operands[0] == inst.operands[1]:
        return inst.operands[0].inst
    # (not x) and (not y) -> not (x or y)
    if (inst.operands[0].inst.op_name == 'OpLogicalNot' and
            inst.operands[1].inst.op_name == 'OpLogicalNot'):
        op_id0 = inst.operands[0].inst.operands[0]
        op_id1 = inst.operands[1].inst.operands[0]
        or_inst = ir.Instruction(module, 'OpLogicalOr', inst.type_id,
                                 [op_id0, op_id1])
        or_inst.insert_before(inst)
        not_inst = ir.Instruction(module, 'OpLogicalNot', inst.type_id,
                                  [or_inst.result_id])
        not_inst.insert_after(or_inst)
        return not_inst
    return inst


def optimize_OpLogicalEqual(module, inst):
    # Equal(x, true) -> x
    if inst.operands[1].inst.is_constant_value(True):
        return inst.operands[0].inst
    # Equal(x, false) -> not(x)
    if inst.operands[1].inst.is_constant_value(False):
        new_inst = ir.Instruction(module, 'OpLogicalNot', inst.type_id,
                                  [inst.operands[0]])
        new_inst.insert_before(inst)
        return new_inst
    # Equal(x, x) -> true
    if inst.operands[0] == inst.operands[1]:
        return module.get_constant(inst.type_id, True)
    return inst


def optimize_OpLogicalNot(inst):
    # not(not(x)) -> x
    operand_inst = inst.operands[0].inst
    if operand_inst.op_name == 'OpLogicalNot':
        return operand_inst.operands[0].inst
    return inst


def optimize_OpLogicalNotEqual(module, inst):
    # NotEqual(x, false) -> x
    if inst.operands[1].inst.is_constant_value(False):
        return inst.operands[0].inst
    # NotEqual(x, true) -> not(x)
    if inst.operands[1].inst.is_constant_value(True):
        new_inst = ir.Instruction(module, 'OpLogicalNot', inst.type_id,
                                  [inst.operands[0]])
        new_inst.insert_before(inst)
        return new_inst
    # NotEqual(x, x) -> false
    if inst.operands[0] == inst.operands[1]:
        return module.get_constant(inst.type_id, False)
    return inst


def optimize_OpLogicalOr(module, inst):
    # x or true -> true
    if inst.operands[1].inst.is_constant_value(True):
        return inst.operands[1].inst
    # x or false -> x
    if inst.operands[1].inst.is_constant_value(False):
        return inst.operands[0].inst
    # x or x -> x
    if inst.operands[0] == inst.operands[1]:
        return inst.operands[0].inst
    # (not x) or (not y) -> not (x and y)
    if (inst.operands[0].inst.op_name == 'OpLogicalNot' and
            inst.operands[1].inst.op_name == 'OpLogicalNot'):
        op_id0 = inst.operands[0].inst.operands[0]
        op_id1 = inst.operands[1].inst.operands[0]
        or_inst = ir.Instruction(module, 'OpLogicalAnd', inst.type_id,
                                 [op_id0, op_id1])
        or_inst.insert_before(inst)
        not_inst = ir.Instruction(module, 'OpLogicalNot', inst.type_id,
                                  [or_inst.result_id])
        not_inst.insert_after(or_inst)
        return not_inst
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

    # Change vector shuffles "A, unused" or "unused, A" to "A, A" where
    # the second operand is not used (and change to OpUndef if no elements
    # of the input vectors are used).
    #
    # We use this form for swizzles instead of using an OpUndef for the
    # unused vector in order to avoid adding an extra instruction for the
    # OpUndef. This form also makes the constant folder handle the shuffle
    # for constant A without needing to special the case where one operand
    # is constant, and one is OpUndef.
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
    elif inst.op_name == 'OpIAdd':
        inst = optimize_OpIAdd(inst)
    elif inst.op_name == 'OpIMul':
        inst = optimize_OpIMul(module, inst)
    elif inst.op_name == 'OpLogicalAnd':
        inst = optimize_OpLogicalAnd(module, inst)
    elif inst.op_name == 'OpLogicalEqual':
        inst = optimize_OpLogicalEqual(module, inst)
    elif inst.op_name == 'OpLogicalNot':
        inst = optimize_OpLogicalNot(inst)
    elif inst.op_name == 'OpLogicalNotEqual':
        inst = optimize_OpLogicalNotEqual(module, inst)
    elif inst.op_name == 'OpLogicalOr':
        inst = optimize_OpLogicalOr(module, inst)
    elif inst.op_name == 'OpNot':
        inst = optimize_OpNot(inst)
    elif inst.op_name == 'OpSNegate':
        inst = optimize_OpSNegate(inst)
    elif inst.op_name == 'OpTranspose':
        inst = optimize_OpTranspose(inst)
    elif inst.op_name == 'OpVectorShuffle':
        inst = optimize_OpVectorShuffle(module, inst)

    return inst


def canonicalize_inst(module, inst):
    """Canonicalize operand order if instruction is commutative.

    The canonical form is that a commutative instruction with one constant
    operand always has the constant as its second operand."""
    if inst.op_name == 'OpExtInst':
        extset_inst = inst.operands[0].inst
        assert extset_inst.op_name == 'OpExtInstImport'
        if extset_inst.operands[0] in ir.EXT_INST:
            ext_ops = ir.EXT_INST[extset_inst.operands[0]]
            if ext_ops[inst.operands[1]]['is_commutative']:
                new_inst = ir.Instruction(module, 'OpExtInst', inst.type_id,
                                          [inst.operands[0], inst.operands[1],
                                           inst.operands[3], inst.operands[2]])
                new_inst.insert_before(inst)
                return new_inst
    elif (inst.is_commutative() and
          inst.operands[0].inst.op_name in ir.CONSTANT_INSTRUCTIONS and
          inst.operands[1].inst.op_name not in ir.CONSTANT_INSTRUCTIONS):
        new_inst = ir.Instruction(module, inst.op_name, inst.type_id,
                                  [inst.operands[1], inst.operands[0]])
        new_inst.insert_before(inst)
        return new_inst
    return inst


def optimize_inst(module, inst):
    """Simplify one instruction"""
    inst = canonicalize_inst(module, inst)

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


def run(module):
    """Combine/simplify instructions, to fewer/simpler instructions"""
    for function in module.functions:
        for inst in function.instructions():
            optimized_inst = optimize_inst(module, inst)
            if optimized_inst != inst:
                inst.replace_uses_with(optimized_inst)
