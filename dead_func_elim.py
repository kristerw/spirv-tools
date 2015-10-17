"""Removes unused functions."""


def reachable(func, reachable_funcs, id_to_func):
    """Recursively mark functions reachable from func."""
    reachable_funcs.add(func)
    for inst in func.instructions():
        if inst.op_name == 'OpFunctionCall':
            called_func = id_to_func[inst.operands[0]]
            if called_func not in reachable_funcs:
                reachable(called_func, reachable_funcs, id_to_func)


def optimize(module):
    """Remove all unused functions."""
    id_to_func = {}
    for func in module.functions:
        id_to_func[func.inst.result_id] = func

    reachable_funcs = set()
    for inst in module.global_instructions.op_entry_point_insts:
        reachable(id_to_func[inst.operands[1]],
                  reachable_funcs,
                  id_to_func)

    for func in module.functions[:]:
        if func not in reachable_funcs:
            func.destroy()
