"""Change instructions having only constant operands to a constant.

This pass tends to leave dead instructions, so dead_inst_elim should
be run after."""
from spirv_tools import ir


def get_value(inst):
    # TODO: Handler integers and floats too.
    assert (inst.op_name == 'OpConstantTrue' or
            inst.op_name == 'OpConstantFalse')
    return True if inst.op_name == 'OpConstantTrue' else False


def transform_1op_componentwise(module, transform, type_id, const_inst):
    """Helper function for transform_componentwise)."""
    if type_id.inst.op_name in ['OpTypeVector', 'OpTypeMatrix']:
        operands = []
        for op1_id in const_inst.operands:
            inst = transform_1op_componentwise(module, transform,
                                               type_id.inst.operands[0],
                                               op1_id.inst)
            operands.append(inst.result_id)
        return module.get_global_inst('OpConstantComposite', type_id, operands)
    else:
        assert type_id.inst.op_name in ['OpTypeBool', 'OpTypeInt',
                                        'OpTypeFloat']
        value = transform(const_inst)
        return module.get_constant(type_id, value)


def transform_2op_componentwise(module, transform, type_id, inst1, inst2):
    """Helper function for transform_componentwise)."""
    if type_id.inst.op_name in ['OpTypeVector', 'OpTypeMatrix']:
        operands = []
        for op1_id, op2_id in zip(inst1.operands, inst2.operands):
            inst = transform_2op_componentwise(module, transform,
                                               type_id.inst.operands[0],
                                               op1_id.inst, op2_id.inst)
            operands.append(inst.result_id)
        return module.get_global_inst('OpConstantComposite', type_id, operands)
    else:
        assert type_id.inst.op_name in ['OpTypeBool', 'OpTypeInt',
                                        'OpTypeFloat']
        value = transform(inst1, inst2)
        return module.get_constant(type_id, value)


def transform_componentwise(module, transform, type_id, inst):
    """Constant fold inst per component.

    The result has the type_id, and the computation is done per component
    using the provided transform function.
    """
    if len(inst.operands) == 1:
        return transform_1op_componentwise(module, transform, type_id,
                                           inst.operands[0].inst)
    else:
        assert len(inst.operands) == 2
        return transform_2op_componentwise(module, transform, type_id,
                                           inst.operands[0].inst,
                                           inst.operands[1].inst)


def get_or_create_const_composite(module, type_id, operands):
    """Get an OpConstantComposite instruction with given type/operands.

    An existing instruction is returned, or a new one is created if there
    is no such instruction already."""
    for inst in module.global_instructions.type_insts:
        if (inst.op_name == 'OpConstantComposite' and
                inst.type_id == type_id and
                inst.operands == operands):
            return inst
    return module.get_global_inst('OpConstantComposite', type_id, operands[:])


def optimize_OpCompositeConstruct(module, inst):
    return get_or_create_const_composite(module, inst.type_id, inst.operands)


def optimize_OpCompositeExtract(inst):
    result_inst = inst.operands[0].inst
    for index in inst.operands[1:]:
        result_inst = result_inst.operands[index].inst
    return result_inst


def optimize_OpLogicalAnd(module, inst):
    transform = lambda x, y: get_value(x) and get_value(y)
    return transform_componentwise(module, transform, inst.type_id, inst)


def optimize_OpLogicalEqual(module, inst):
    transform = lambda x, y: get_value(x) == get_value(y)
    return transform_componentwise(module, transform, inst.type_id, inst)


def optimize_OpLogicalNot(module, inst):
    transform = lambda x: not get_value(x)
    return transform_componentwise(module, transform, inst.type_id, inst)


def optimize_OpLogicalNotEqual(module, inst):
    transform = lambda x, y: get_value(x) != get_value(y)
    return transform_componentwise(module, transform, inst.type_id, inst)


def optimize_OpLogicalOr(module, inst):
    transform = lambda x, y: get_value(x) or get_value(y)
    return transform_componentwise(module, transform, inst.type_id, inst)


def optimize_OpVectorShuffle(module, inst):
    vec1_inst = inst.operands[0].inst
    vec1_len = len(vec1_inst.operands)
    vec2_inst = inst.operands[1].inst
    components = []
    for component in inst.operands[2:]:
        if component == 0xffffffff:
            # Undefined component, so we may choose any value, e.g. the
            # first element from vector 1.
            components.append(vec1_inst.operands[0])
        elif component < vec1_len:
            components.append(vec1_inst.operands[component])
        else:
            components.append(vec2_inst.operands[component - vec1_len])
    return get_or_create_const_composite(module, inst.type_id, components)


def optimize_inst(module, inst):
    """Simplify one instruction"""
    for operand in inst.operands:
        if isinstance(operand, ir.Id):
            if operand.inst.op_name not in ir.CONSTANT_INSTRUCTIONS:
                return inst

    if inst.op_name == 'OpCompositeConstruct':
        inst = optimize_OpCompositeConstruct(module, inst)
    elif inst.op_name == 'OpCompositeExtract':
        inst = optimize_OpCompositeExtract(inst)
    elif inst.op_name == 'OpLogicalAnd':
        inst = optimize_OpLogicalAnd(module, inst)
    elif inst.op_name == 'OpLogicalEqual':
        inst = optimize_OpLogicalEqual(module, inst)
    elif inst.op_name == 'OpLogicalNot':
        inst = optimize_OpLogicalNot(module, inst)
    elif inst.op_name == 'OpLogicalNotEqual':
        inst = optimize_OpLogicalNotEqual(module, inst)
    elif inst.op_name == 'OpLogicalOr':
        inst = optimize_OpLogicalOr(module, inst)
    elif inst.op_name == 'OpVectorShuffle':
        inst = optimize_OpVectorShuffle(module, inst)

    return inst


def run(module):
    """Simple constant propagation and merging"""
    for function in module.functions:
        for inst in function.instructions():
            optimized_inst = optimize_inst(module, inst)
            if optimized_inst != inst:
                inst.replace_uses_with(optimized_inst)
