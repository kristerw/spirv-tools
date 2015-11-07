from spirv_tools.passes import dead_inst_elim
from spirv_tools.passes import dead_func_elim
from spirv_tools.passes import instcombine
from spirv_tools.passes import mem2reg
from spirv_tools.passes import simplify_cfg

def optimize(module):
    """Do basic optimizations.

    This only runs optimization passes that are likely to be profitable
    on all architectures (such as removing dead code)."""
    instcombine.run(module)
    simplify_cfg.run(module)
    dead_inst_elim.run(module)
    dead_func_elim.run(module)
    mem2reg.run(module)
    instcombine.run(module)
    simplify_cfg.run(module)
    dead_inst_elim.run(module)
    dead_func_elim.run(module)
