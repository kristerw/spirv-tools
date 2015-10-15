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
    for inst in reversed(module.global_insts[:]):
        if inst.op_name in ir.DEBUG_INSTRUCTIONS:
            remove_debug_if_dead(inst)
        elif inst.op_name in ir.DECORATION_INSTRUCTIONS:
            remove_decoration_if_dead(inst)

    # Remove unused instructions.
    for inst in module.instructions_reversed():
        if not inst.has_side_effect() and not inst.uses():
            inst.destroy()
