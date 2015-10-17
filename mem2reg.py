import ir


def optimize_variable(module, func, var_inst):
    uses = var_inst.uses()

    # Delete variable if it is not used.
    if not uses:
        var_inst.destroy()
        return

    # We only handle simple loads and stores for now.
    for inst in uses:
        if inst.op_name not in ['OpLoad', 'OpStore']:
            return

    # We only handle cases where all usages are in the same basic block.
    usage_bb = uses[0].basic_block
    for inst in uses:
        if inst.basic_block != usage_bb:
            return

    ordered_uses = [inst for inst in func.instructions() if inst in uses]
    stored_inst = None
    for inst in ordered_uses:
        if inst.op_name == 'OpLoad':
            if stored_inst is None:
                # The variable is loaded before it is written. This need
                # a phi-node if it is within a loop, so skip this variable.
                return
            inst.replace_uses_with(stored_inst)
            inst.destroy()
        elif inst.op_name == 'OpStore':
            stored_inst = inst.operands[1].inst
            inst.destroy()
    var_inst.destroy()


def optimize(module):
    for function in module.functions:
        for inst in function.basic_blocks[0].insts[:]:
            # The variables must be defined at the top of the basic block,
            # i.e. we are done when we find the first non-OpVariable inst.
            if inst.op_name != 'OpVariable':
                break

            optimize_variable(module, function, inst)
