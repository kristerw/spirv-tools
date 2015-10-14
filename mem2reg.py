import ir


def optimize_variable(module, func, var_inst):
    uses = var_inst.uses()
    if not uses:
        var_inst.destroy()
        return
    ordered_uses = [inst for inst in func.instructions() if inst in uses]

    usage_bb = ordered_uses[0].basic_block
    for inst in ordered_uses:
        if inst.basic_block != usage_bb:
            return
        if inst.op_name not in ['OpLoad', 'OpStore']:
            return

    stored_inst = None
    for inst in ordered_uses:
        if inst.op_name == 'OpLoad':
            if stored_inst is None:
                stored_inst = ir.Instruction(module, 'OpUndef',
                                             module.new_id(),
                                             inst.type_id, [])
                stored_inst.insert_before(inst)
            inst.replace_uses_with(stored_inst)
            inst.destroy()
        elif inst.op_name == 'OpStore':
            stored_inst = inst.operands[1].inst
            inst.destroy()
    var_inst.destroy()


def optimize(module):
    for function in module.functions:
        for inst in function.basic_blocks[0].insts[:]:
            if inst.op_name != 'OpVariable':
                break
            optimize_variable(module, function, inst)
