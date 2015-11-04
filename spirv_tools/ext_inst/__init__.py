from spirv_tools.ext_inst import glsl_std_450
from spirv_tools.ext_inst import opencl_std

EXT_INST = {}
EXT_INST['GLSL.std.450'] = glsl_std_450.INST_FORMAT
EXT_INST['OpenCL.std'] = opencl_std.INST_FORMAT
