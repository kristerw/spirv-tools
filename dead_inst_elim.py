"""Removes unused instructions.

The definition of "unused instruction" is an instruction having a return
ID that is not used by any non-debug and non-decoration instruction, and
does not have side effects."""
import ir


def remove_debug_if_dead(inst):
    """Remove debug instruction if it is not used."""
    assert inst.op_name in ir.DEBUG_INSTRUCTIONS
    if inst.op_name != 'OpString':
        if inst.operands[0].inst is None:
            inst.destroy()


def remove_decoration_if_dead(inst):
    """Remove decoration instruction if it is not used."""
    assert inst.op_name in ir.DECORATION_INSTRUCTIONS
    if inst.op_name != 'OpDecorationGroup':
        if inst.operands[0].inst is None:
            inst.destroy()


def optimize(module):
    """Remove all unused instructions."""

    # Garbage collect old unused debug and decoration instructions.
    # This is done before the real pass because:
    # * They need some special handling, as they do not have inst.result_id
    # * They come in the wrong order with regard to constants, so we would
    #   need extra code in the real pass to ensure constants used in OpLine
    #   are removed.
    # Note: the debug and decoration instructions that are live at the start
    # of this pass is handled by the real pass when the instruction they
    # point to is removed.
    for inst in module.global_instructions.op_line_insts:
        remove_debug_if_dead(inst)
    for inst in module.global_instructions.name_insts:
        remove_debug_if_dead(inst)
    for inst in module.global_instructions.op_string_insts:
        remove_debug_if_dead(inst)
    for inst in reversed(module.global_instructions.decoration_insts):
        remove_decoration_if_dead(inst)

    # Remove unused instructions.
    #
    # We need to re-run the pass if elimination of a phi-node makes
    # instructions dead in an already processed basic block.
    rerun = True
    while rerun:
        rerun = False
        processed_bbs = set()
        for inst in module.instructions_reversed():
            if inst.op_name == 'OpLabel':
                processed_bbs.add(inst.basic_block)
            if not inst.has_side_effect() and not inst.uses():
                if inst.op_name == 'OpPhi':
                    processed_bbs.add(inst.basic_block)
                    operands = inst.operands[:]
                    inst.destroy()
                    for operand in operands:
                        if (operand.inst.op_name != 'OpLabel' and
                                operand.inst.basic_block in processed_bbs and
                                not operand.inst.uses()):
                            rerun = True
                            break
                else:
                    inst.destroy()
