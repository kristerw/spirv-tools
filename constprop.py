"""Change instructions having only constant operands to a constant.

This pass tends to leave dead instructions, so dead_code_elim should
be run after."""
import ir


def optimize_OpCompositeConstruct(module, inst):
    new_inst = ir.Instruction(module, 'OpConstantComposite', module.new_id(),
                              inst.type_id, inst.operands[:])
    module.add_global_inst(new_inst)
    return new_inst


def optimize_OpCompositeExtract(inst):
    result_inst = inst.operands[0].inst
    for index in inst.operands[1:]:
        result_inst = result_inst.operands[index].inst
    return result_inst


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
    new_inst = ir.Instruction(module, 'OpConstantComposite', module.new_id(),
                              inst.type_id, components)
    module.add_global_inst(new_inst)
    return new_inst


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
    elif inst.op_name == 'OpVectorShuffle':
        inst = optimize_OpVectorShuffle(module, inst)

    return inst


def optimize(module):
    """Simple constant propagation and merging"""
    for function in module.functions:
        for inst in function.instructions():
            optimized_inst = optimize_inst(module, inst)
            if optimized_inst != inst:
                inst.replace_uses_with(optimized_inst)
    module.finalize()
