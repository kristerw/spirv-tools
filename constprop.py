"""Change instructions having only constant operands to a constant.

This pass tends to leave dead instructions, so dead_code_elim should
be run after."""
import ir
import spirv


def optimize_OpCompositeExtract(module, inst):
    result_inst = module.id_to_inst[inst.operands[0]]
    for index in inst.operands[1:]:
        result_inst = module.id_to_inst[result_inst.operands[index]]
    return result_inst


def optimize_OpVectorShuffle(module, inst):
    vec1_inst = module.id_to_inst[inst.operands[0]]
    vec1_len = len(vec1_inst.operands)
    vec2_inst = module.id_to_inst[inst.operands[1]]
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
    new_inst.insert_before(inst)
    return new_inst


def optimize_inst(module, inst):
    """Simplify one instruction"""
    for operand in inst.operands:
        if isinstance(operand, basestring) and operand[0] == '%':
            operand_inst = module.id_to_inst[operand]
            if operand_inst.op_name not in spirv.CONSTANT_INSTRUCTIONS:
                return inst

    if inst.op_name == 'OpCompositeExtract':
        inst = optimize_OpCompositeExtract(module, inst)
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
