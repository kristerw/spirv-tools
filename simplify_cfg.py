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
    assert basic_block.insts[-2].op_name == 'OpSelectionMerge'
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


def merge_basic_blocks(module):
    """Merges a basic block into its predecessor if there is only one and
    the predecessor only has one successor."""
    for function in module.functions:
        for basic_block in reversed(function.basic_blocks[1:]):
            predecessors = basic_block.predecessors()
            if len(predecessors) == 1:
                pred_block = predecessors[0]
                if pred_block.insts[-1].op_name == 'OpBranch':
                    pred_block.insts[-1].destroy()
                    for inst in basic_block.insts[:]:
                        inst.remove()
                        pred_block.append_inst(inst)
                    basic_block.destroy()


def eliminate_phi_nodes(module):
    """Eliminates PHI nodes for basic blocks with a single predecessor."""
    for inst in module.instructions():
        if inst.op_name == 'OpPhi':
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
