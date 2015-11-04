INST_FORMAT = {
    0 : {
        'name' : 'acos',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    1 : {
        'name' : 'acosh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    2 : {
        'name' : 'acospi',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    3 : {
        'name' : 'asin',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    4 : {
        'name': 'asinh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    5 : {
        'name' : 'asinpi',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    6 : {
        'name' : 'atan',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    7 : {
        'name' : 'atan2',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    8 : {
        'name' : 'atanh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    9 : {
        'name' : 'atanpi',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    10 : {
        'name' : 'atan2pi',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    11 : {
        'name' : 'cbrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    12 : {
        'name' : 'ceil',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    13 : {
        'name' : 'copysign',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    14 : {
        'name' : 'cos',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    15 : {
        'name' : 'cosh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    16 : {
        'name' : 'cospi',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    17 : {
        'name' : 'erfc',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    18 : {
        'name' : 'erf',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    19 : {
        'name' : 'exp',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    20 : {
        'name' : 'exp2',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    21 : {
        'name' : 'exp10',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    22 : {
        'name' : 'expm1',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    23 : {
        'name' : 'fabs',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    24 : {
        'name' : 'fdim',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    25 : {
        'name' : 'floor',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    26 : {
        'name' : 'fma',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    27 : {
        'name' : 'fmax',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    28 : {
        'name' : 'fmin',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    29 : {
        'name' : 'fmod',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    30: {
        'name' : 'fract',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    31 : {
        'name' : 'frexp',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    32 : {
        'name' : 'hypot',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    33 : {
        'name' : 'ilogb',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    34 : {
        'name' : 'ldexp',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    35 : {
        'name' : 'lgamma',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    36 : {
        'name' : 'lgamma_r',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    37 : {
        'name' : 'log',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    38 : {
        'name' : 'log2',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    39 : {
        'name' : 'log10',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    40 : {
        'name' : 'log1p',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    41 : {
        'name' : 'logb',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    42 : {
        'name' : 'mad',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    43 : {
        'name' : 'maxmag',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    44 : {
        'name' : 'minmag',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    45 : {
        'name' : 'modf',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    46 : {
        'name' : 'nan',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    47 : {
        'name' : 'nextafter',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    48 : {
        'name' : 'pow',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    49 : {
        'name' : 'pown',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    50 : {
        'name' : 'powr',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    51 : {
        'name' : 'remainder',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    52 : {
        'name' : 'remquo',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    53 : {
        'name' : 'rint',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    54 : {
        'name' : 'rootn',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    55 : {
        'name' : 'round',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    56 : {
        'name' : 'rsqrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    57 : {
        'name' : 'sin',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    58 : {
        'name' : 'sincos',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    59 : {
        'name' : 'sinh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    60 : {
        'name' : 'sinpi',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    61 : {
        'name' : 'sqrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    62 : {
        'name' : 'tan',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    63 : {
        'name' : 'tanh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    64 : {
        'name' : 'tanpi',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    65 : {
        'name' : 'tgamma',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    66 : {
        'name' : 'trunc',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    67 : {
        'name' : 'half_cos',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    68 : {
        'name' : 'half_divide',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    69 : {
        'name' : 'half_exp',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    70 : {
        'name' : 'half_exp2',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    71 : {
        'name' : 'half_exp10',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    72 : {
        'name' : 'half_log',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    73 : {
        'name' : 'half_log2',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    74 : {
        'name' : 'half_log10',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    75 : {
        'name' : 'half_powr',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    76 : {
        'name' : 'half_recip',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    77 : {
        'name' : 'half_rsqrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    78 : {
        'name' : 'half_sin',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    79 : {
        'name' : 'half_sqrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    80 : {
        'name' : 'half_tan',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    81 : {
        'name' : 'native_cos',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    82 : {
        'name' : 'native_divide',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    83 : {
        'name' : 'native_exp',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    84 : {
        'name' : 'native_exp2',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    85 : {
        'name' : 'native_exp10',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    86 : {
        'name' : 'native_log',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    87 : {
        'name' : 'native_log2',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    88 : {
        'name' : 'native_log10',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    89 : {
        'name' : 'native_powr',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    90 : {
        'name' : 'native_recip',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    91 : {
        'name' : 'native_rsqrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    92 : {
        'name' : 'native_sin',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    93 : {
        'name' : 'native_sqrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    94 : {
        'name' : 'native_tan',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },

    95 : {
        'name' : 'fclamp',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    96 : {
        'name' : 'degrees',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    97 : {
        'name' : 'fmax_common',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    98 : {
        'name' : 'fmin_common',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    99 : {
        'name' : 'mix',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    100 : {
        'name' : 'radians',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    101 : {
        'name' : 'step',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    102 : {
        'name' : 'smoothstep',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    103 : {
        'name' : 'sign',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    104 : {
        'name' : 'cross',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    105 : {
        'name' : 'distance',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    106 : {
        'name' : 'length',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    107 : {
        'name' : 'normalize',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    108 : {
        'name' : 'fast_distance',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    109 : {
        'name' : 'fast_length',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    110 : {
        'name' : 'fast_normalize',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    129 : {
        'name' : 'write_imagef_mipmap_lod',
        'operands' : ['Id', 'Id', 'Id', 'Id'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    130 : {
        'name' : 'write_imagei_mipmap_lod',
        'operands' : ['Id', 'Id', 'Id', 'Id'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    131 : {
        'name' : 'write_imageui_mipmap_lod',
        'operands' : ['Id', 'Id', 'Id', 'Id'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    141 : {
        'name' : 's_abs',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    142 : {
        'name' : 's_abs_diff',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    143 : {
        'name' : 's_add_sat',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    144 : {
        'name' : 'u_add_sat',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    145 : {
        'name' : 's_hadd',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    146 : {
        'name' : 'u_hadd',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    147 : {
        'name' : 's_rhadd',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    148 : {
        'name' : 'u_rhadd',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    149 : {
        'name' : 's_clamp',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    150 : {
        'name' : 'u_clamp',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    151 : {
        'name' : 'clz',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    152 : {
        'name' : 'ctz',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    153 : {
        'name' : 's_mad_hi',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    156 : {
        'name' : 's_max',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    157 : {
        'name' : 'u_max',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    158 : {
        'name' : 's_min',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    159 : {
        'name' : 'u_min',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    160 : {
        'name' : 's_mul_hi',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    161 : {
        'name' : 'rotate',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    162 : {
        'name' : 's_sub_sat',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    163 : {
        'name' : 'u_sub_sat',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    164 : {
        'name' : 'u_upsample',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    165 : {
        'name' : 's_upsample',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    166 : {
        'name' : 'popcount',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    167 : {
        'name' : 's_mad24',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    168 : {
        'name' : 'u_mad24',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    169: {
        'name' : 's_mul24',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    170 : {
        'name' : 'u_mul24',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    171 : {
        'name' : 'vloadn',
        'operands' : ['Id', 'Id', 'LiteralNumber'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    172 : {
        'name' : 'vstoren',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    173 : {
        'name' : 'vload_half',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    174 : {
        'name' : 'vload_halfn',
        'operands' : ['Id', 'Id', 'LiteralNumber'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    175 : {
        'name' : 'vstore_half',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    176 : {
        'name' : 'vstore_half_r',
        'operands' : ['Id', 'Id', 'Id', 'FPRoundingMode'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    177 : {
        'name' : 'vstore_halfn',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    178 : {
        'name' : 'vstore_halfn_r',
        'operands' : ['Id', 'Id', 'Id', 'FPRoundingMode'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    179 : {
        'name' : 'vloada_halfn',
        'operands' : ['Id', 'Id', 'LiteralNumber'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    180 : {
        'name' : 'vstorea_halfn',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    181 : {
        'name' : 'vstorea_halfn_r',
        'operands' : ['Id', 'Id', 'Id', 'FPRoundingMode'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    182 : {
        'name' : 'shuffle',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    183 : {
        'name' : 'shuffle2',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    184 : {
        'name' : 'printf',
        'operands' : ['Id', 'VariableIds'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    185 : {
        'name' : 'prefetch',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : True,
        'is_commutative' : False
    },
    186 : {
        'name' : 'bitselect',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    187 : {
        'name' : 'select',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    201 : {
        'name' : 'u_abs',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    202 : {
        'name' : 'u_abs_diff',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    203 : {
        'name' : 'u_mul_hi',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    204 : {
        'name' : 'u_mad_hi',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    }
}
