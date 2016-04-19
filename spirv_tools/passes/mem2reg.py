"""Change OpVariable (of Function storage class) to registers.

This pass promotes the OpVariable that only are accessed by OpLoad and
OpStore instructions.

The pass implementation naively inserts a OpPhi instruction at each join point,
and promotes the loads and stores as it iterates through the function.

This pass tends to leave dead OpPhi instructions, so dead_inst_elim should
be run after."""
import collections

from spirv_tools import ir


def calculate_pred(func):
    """Return a dictionary with predecessors for each basic block."""
    pred = collections.defaultdict(list)
    for basic_block in func.basic_blocks:
        for successor in basic_block.get_successors():
            if basic_block not in pred[successor]:
                pred[successor].append(basic_block)
    return pred


def optimize_variable(module, func, var_inst):
    """Promote/eliminate the var_inst variable if possible."""
    # Delete variable if it is not used.
    if not var_inst.result_id.uses:
        var_inst.destroy()
        return

    # We only handle simple loads and stores.
    for inst in var_inst.uses():
        if inst.op_name not in ['OpLoad', 'OpStore']:
            return

    # Eliminate loads/store instructions for the variable
    pred = calculate_pred(func)
    exit_value = {}
    phi_nodes = []
    undef_insts = []
    var_type_id = var_inst.type_id.inst.operands[1]
    for basic_block in func.basic_blocks:
        # Get the variable's value at start of the basic block.
        if not pred[basic_block]:
            stored_inst = None
        elif len(pred[basic_block]) == 1:
            stored_inst = exit_value[pred[basic_block][0]]
        else:
            stored_inst = ir.Instruction(module, 'OpPhi', var_type_id, [])
            basic_block.prepend_inst(stored_inst)
            phi_nodes.append(stored_inst)

        # Eliminate loads/store instructions.
        ordered_uses = [inst for inst in basic_block.insts
                        if inst in var_inst.result_id.uses]
        for inst in ordered_uses:
            if inst.op_name == 'OpLoad':
                if stored_inst is None:
                    stored_inst = ir.Instruction(module, 'OpUndef',
                                                 inst.type_id, [])
                    undef_insts.append(stored_inst)
                    stored_inst.insert_before(inst)
                inst.replace_uses_with(stored_inst)
                inst.destroy()
            elif inst.op_name == 'OpStore':
                stored_inst = inst.operands[1].inst
                inst.destroy()

        # Save the variable's value at end of the basic block.
        exit_value[basic_block] = stored_inst

    # Add operands to the phi-nodes.
    for inst in phi_nodes:
        for pred_bb in pred[inst.basic_block]:
            if exit_value[pred_bb] is None:
                undef_inst = ir.Instruction(module, 'OpUndef', var_type_id, [])
                undef_insts.append(undef_inst)
                last_insts = pred_bb.insts[-2:]
                if (last_insts[0].op_name in ['OpLoopMerge',
                                              'OpSelectionMerge'] or
                        last_insts[0].op_name in ir.BRANCH_INSTRUCTIONS):
                    undef_inst.insert_before(last_insts[0])
                else:
                    undef_inst.insert_after(last_insts[0])
                exit_value[pred_bb] = undef_inst
            inst.add_to_phi(exit_value[pred_bb], pred_bb.inst)

    # Destroy obviously dead instructions.
    for inst in reversed(phi_nodes):
        if not inst.result_id.uses:
            inst.destroy()
    for inst in undef_insts:
        if not inst.result_id.uses:
            inst.destroy()
    var_inst.destroy()


def process_function(module, function):
    """Run the pass on one function."""
    for inst in function.basic_blocks[0].insts[:]:
        # The variables must be defined at the top of the basic block,
        # i.e. we are done when we find the first non-OpVariable inst.
        if inst.op_name != 'OpVariable':
            break
        optimize_variable(module, function, inst)


def run(module):
    """Change OpVariable (of Function storage class) to registers."""
    for function in module.functions:
        process_function(module, function)
