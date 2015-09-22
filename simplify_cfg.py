"""Performs dead code elimination and basic block merging.

Specifically:
* Removes basic blocks with no predecessors.
* Merges a basic block into its predecessor if there is only one and the
  predecessor only has one successor.
* Eliminates PHI nodes for basic blocks with a single predecessor.
* Eliminates conditional branches having a constant conditional."""
import ir


def update_conditional_branch(module, inst, dest_id):
    """Change the conditional branch instruction to a branch to dest_id."""
    assert inst.op_name == 'OpBranchConditional'
    basic_block = inst.basic_block
    branch_inst = ir.Instruction(module, 'OpBranch', None, None, [dest_id])
    inst.replace_with(branch_inst)
    assert basic_block.insts[-2].op_name in ['OpSelectionMerge', 'OpLoopMerge']
    basic_block.insts[-2].destroy()


def remove_constant_cond_branches(module):
    """Eliminate conditional branches having a constant conditional."""
    for function in module.functions:
        for basic_block in function.basic_blocks:
            inst = basic_block.insts[-1]
            if inst.op_name == 'OpBranchConditional':
                cond_inst = inst.operands[0].inst
                if cond_inst.op_name == 'OpConstantTrue':
                    update_conditional_branch(module, inst, inst.operands[1])
                elif cond_inst.op_name == 'OpConstantFalse':
                    update_conditional_branch(module, inst, inst.operands[2])


def remove_unused_basic_blocks(module):
    """Removes basic blocks with no predecessors."""
    for function in module.functions:
        for basic_block in function.basic_blocks[1:]:
            if not basic_block.predecessors():
                basic_block.destroy()


def get_merge_targest(module):
    """Return a set of BBs that are a taget of a merge instruction."""
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
    """Eliminates PHI nodes for basic blocks with a single predecessor."""
    for function in module.functions:
        for basic_block in function.basic_blocks:
            for inst in basic_block.insts:
                if inst.op_name != 'OpPhi':
                    break
                if len(inst.operands) == 2:
                    source_inst = inst.operands[0].inst
                    inst.replace_with(source_inst)


def optimize(module):
    """Perform dead code elimination and basic block merging."""
    remove_constant_cond_branches(module)
    remove_unused_basic_blocks(module)
    merge_basic_blocks(module)
    eliminate_phi_nodes(module)
    module.finalize()
