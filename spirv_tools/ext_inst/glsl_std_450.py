INST_FORMAT = {
    1 : {
        'name' : 'Round',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    2 : {
        'name' : 'RoundEven',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    3 : {
        'name' : 'Trunc',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    4 : {
        'name': 'FAbs',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    5 : {
        'name' : 'SAbs',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    6 : {
        'name' : 'FSign',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    7 : {
        'name' : 'SSign',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    8 : {
        'name' : 'Floor',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    9 : {
        'name' : 'Ceil',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    10 : {
        'name' : 'Fract',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    11 : {
        'name' : 'Radians',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    12 : {
        'name' : 'Degrees',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    13 : {
        'name' : 'Sin',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    14 : {
        'name' : 'Cos',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    15 : {
        'name' : 'Tan',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    16 : {
        'name' : 'Asin',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    17 : {
        'name' : 'Acos',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    18 : {
        'name' : 'Atan',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    19 : {
        'name' : 'Sinh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    20 : {
        'name' : 'Cosh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    21 : {
        'name' : 'Tanh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    22 : {
        'name' : 'Asinh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    23 : {
        'name' : 'Acosh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    24 : {
        'name' : 'Atanh',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    25 : {
        'name' : 'Atan2',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    26 : {
        'name' : 'Pow',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    27 : {
        'name' : 'Exp',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    28 : {
        'name' : 'Log',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    29 : {
        'name' : 'Exp2',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    30: {
        'name' : 'Log2',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    31 : {
        'name' : 'Sqrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    32 : {
        'name' : 'Inversesqrt',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    33 : {
        'name' : 'Determinant',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    34 : {
        'name' : 'Inverse',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    35 : {
        'name' : 'Modf',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    36 : {
        'name' : 'ModfStruct',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    37 : {
        'name' : 'FMin',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    38 : {
        'name' : 'UMin',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    39 : {
        'name' : 'SMin',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    40 : {
        'name' : 'FMax',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    41 : {
        'name' : 'UMax',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    42 : {
        'name' : 'SMax',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    43 : {
        'name' : 'FClamp',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    44 : {
        'name' : 'UClamp',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    45 : {
        'name' : 'SClamp',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    46 : {
        'name' : 'Mix',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    47 : {
        'name' : 'Step',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    48 : {
        'name' : 'Smoothstep',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    49 : {
        'name' : 'Fma',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    50 : {
        'name' : 'Frexp',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    51 : {
        'name' : 'FrexpStruct',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    52 : {
        'name' : 'Ldexp',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    53 : {
        'name' : 'PackSnorm4x8',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    54 : {
        'name' : 'PackUnorm4x8',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    55 : {
        'name' : 'PackSnorm2x16',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    56 : {
        'name' : 'PackUnrom2x16',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    57 : {
        'name' : 'PackHalf2x16',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    58 : {
        'name' : 'PackDouble2x32',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    59 : {
        'name' : 'PackSnorm2x16',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    60 : {
        'name' : 'UnpackUnorm2x16',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    61 : {
        'name' : 'UnpackHalf2x16',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    62 : {
        'name' : 'UnpackSnorm4x8',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    63 : {
        'name' : 'UnpackUnorm4x8',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    64 : {
        'name' : 'UnpackDouble2x32',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    65 : {
        'name' : 'Length',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    66 : {
        'name' : 'Distance',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : True
    },
    67 : {
        'name' : 'Cross',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    68 : {
        'name' : 'Normalize',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    69 : {
        'name' : 'Faceforward',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    70 : {
        'name' : 'Reflect',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    71 : {
        'name' : 'Refract',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    72 : {
        'name' : 'FindILsb',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    73 : {
        'name' : 'FindSMsb',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    74 : {
        'name' : 'FindUMsb',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    75 : {
        'name' : 'InterpolateAtCentroid',
        'operands' : ['Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    76 : {
        'name' : 'InterpolateAtSample',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    77 : {
        'name' : 'InterpolateAtOffset',
        'operands' : ['Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    78 : {
        'name' : 'UaddCarry',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    79 : {
        'name' : 'UsubBorrow',
        'operands' : ['Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    },
    80 : {
        'name' : 'UmulExtended',
        'operands' : ['Id', 'Id', 'Id', 'Id'],
        'has_side_effects' : False,
        'is_commutative' : False
    }
}
