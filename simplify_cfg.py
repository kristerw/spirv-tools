"""Perform dead code elimination, basic block merging, and CFG simplifications.

Specifically:
* Removes unreachable basic blocks.
* Merges a basic block into its predecessor if there is only one predecessor
  and it only has one successor.
* Eliminates PHI nodes where all variables are identical.
* Changes conditional branches having constant conditional to an unconditional
  branch.
* Changes conditional branches or switch operations to an unconditional
  branch if all branch targets are identical.
"""
import ir


def update_conditional_branch(module, inst, dest_id):
    """Change the OpBranchConditional or OpSwitch to a branch to dest_id."""
    assert inst.op_name == 'OpBranchConditional' or inst.op_name == 'OpSwitch'
    basic_block = inst.basic_block
    branch_inst = ir.Instruction(module, 'OpBranch', None, None, [dest_id])
    inst.replace_with(branch_inst)
    assert basic_block.insts[-2].op_name in ['OpSelectionMerge', 'OpLoopMerge']
    basic_block.insts[-2].destroy()


def simplify_cond_branches(module):
    """Change conditional branches to unconditional branches if possible."""
    for function in module.functions:
        for basic_block in function.basic_blocks:
            inst = basic_block.insts[-1]
            if inst.op_name == 'OpBranchConditional':
                cond_inst = inst.operands[0].inst
                if cond_inst.op_name == 'OpConstantTrue':
                    update_conditional_branch(module, inst, inst.operands[1])
                elif cond_inst.op_name == 'OpConstantFalse':
                    update_conditional_branch(module, inst, inst.operands[2])
                elif inst.operands[1] == inst.operands[2]:
                    update_conditional_branch(module, inst, inst.operands[1])
            elif inst.op_name == 'OpSwitch':
                default_id = inst.operands[1]
                operands = inst.operands[2:]
                while operands:
                    if default_id != operands[1]:
                        break
                    operands = operands[2:]
                else:
                    update_conditional_branch(module, inst, default_id)


def reachable(basic_block, reachable_blocks):
    """Recursively mark basic blocks reachable from basic_block."""
    reachable_blocks.add(basic_block)
    for successor in basic_block.get_successors():
        if successor not in reachable_blocks:
            reachable(successor, reachable_blocks)


def remove_unused_basic_blocks(module):
    """Remove unreachable basic blocks."""
    for function in module.functions:
        reachable_blocks = set()
        reachable(function.basic_blocks[0], reachable_blocks)
        for basic_block in function.basic_blocks[:]:
            if basic_block not in reachable_blocks:
                basic_block.destroy()


def get_merge_targest(module):
    """Return a set of basic blocks that are targets of merge instructions."""
    merge_targets = set()
    for function in module.functions:
        for basic_block in function.basic_blocks:
            if (len(basic_block.insts) > 1 and
                    basic_block.insts[-2] in ['OpLoopMerge',
                                              'OpSelectionMerge']):
                target_id = basic_block.inst.operands[0]
                merge_targets.add(target_id.inst.basic_block)
    return merge_targets


def merge_basic_blocks(module):
    """Merges a basic block into its predecessor if there is only one and
    the predecessor only has one successor."""
    merge_targets = get_merge_targest(module)
    for function in module.functions:
        for basic_block in reversed(function.basic_blocks[1:]):
            predecessors = basic_block.predecessors()
            if len(predecessors) == 1 and basic_block not in merge_targets:
                pred_block = predecessors[0]
                if pred_block.insts[-1].op_name == 'OpBranch':
                    pred_block.insts[-1].destroy()
                    for inst in basic_block.insts[:]:
                        inst.remove()
                        pred_block.append_inst(inst)
                    basic_block.destroy()


def eliminate_phi_nodes(module):
    """Eliminates PHI nodes where all variables are identical."""
    for function in module.functions:
        for basic_block in function.basic_blocks:
            for inst in basic_block.insts:
                if inst.op_name != 'OpPhi':
                    break
                first_variable = inst.operands[0]
                operands = inst.operands[2:]
                while operands:
                    if first_variable != operands[0]:
                        break
                    operands = operands[2:]
                else:
                    inst.replace_uses_with(first_variable.inst)


def optimize(module):
    """Perform dead code elimination and basic block merging."""
    simplify_cond_branches(module)
    remove_unused_basic_blocks(module)
    merge_basic_blocks(module)
    eliminate_phi_nodes(module)
    module.finalize()
