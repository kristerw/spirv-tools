import json
import os

MAGIC = 0x07230203
GENERATOR_MAGIC = 0
VERSION = 99

with open(os.path.join(os.path.dirname(__file__), 'spirv.json')) as fd:
    TABLES = json.load(fd)

OPCODE_TABLE = {}
OPNAME_TABLE = {}
for fmt in TABLES['instructions']:
    OPCODE_TABLE[fmt['opcode']] = fmt
    OPNAME_TABLE[fmt['name']] = fmt

CONSTANTS = TABLES['constants']
DECORATIONS = CONSTANTS['Decoration']
MASKS = TABLES['masks']

BASIC_BLOCK_ENDING_INSTRUCTIONS = [
    'OpReturnValue',
    'OpBranch',
    'OpBranchConditional',
    'OpReturn',
    'OpKill',
    'OpUnreachable',
    'OpSwitch'
]

INITIAL_INSTRUCTIONS = [
    'OpSource',
    'OpSourceExtension',
    'OpCompileFlag',
    'OpExtension',
    'OpExtInstImport',
    'OpMemoryModel',
    'OpEntryPoint',
    'OpExecutionMode'
]

DEBUG_INSTRUCTIONS = [
    'OpString',
    'OpName',
    'OpMemberName',
    'OpLine',
]

DECORATION_INSTRUCTIONS = [
    'OpDecorate',
    'OpMemberDecorate',
    'OpGroupDecorate',
    'OpGroupMemberDecorate',
    'OpDecorationGroup'
]

TYPE_DECLARATION_INSTRUCTIONS = [
    'OpTypeVoid',
    'OpTypeBool',
    'OpTypeInt',
    'OpTypeFloat',
    'OpTypeVector',
    'OpTypeMatrix',
    'OpTypeSampler',
    'OpTypeFilter',
    'OpTypeArray',
    'OpTypeRuntimeArray',
    'OpTypeStruct',
    'OpTypeOpaque',
    'OpTypePointer',
    'OpTypeFunction',
    'OpTypeEvent',
    'OpTypeDeviceEvent',
    'OpTypeReserveId',
    'OpTypeQueue',
    'OpTypePipe'
]

CONSTANT_INSTRUCTIONS = [
    'OpConstantTrue',
    'OpConstantFalse',
    'OpConstant',
    'OpConstantComposite',
    'OpConstantSampler',
    'OpConstantNullPointer',
    'OpConstantNullObject',

    'OpSpecConstantTrue',
    'OpSpecConstantFalse',
    'OpSpecConstant',
    'OpSpecConstantComposite'
]

GLOBAL_VARIABLE_INSTRUCTIONS = [
    'OpVariable',
    'OpVariableArray'
]

GLOBAL_INSTRUCTIONS = (INITIAL_INSTRUCTIONS +
                       DEBUG_INSTRUCTIONS +
                       DECORATION_INSTRUCTIONS +
                       TYPE_DECLARATION_INSTRUCTIONS +
                       CONSTANT_INSTRUCTIONS +
                       GLOBAL_VARIABLE_INSTRUCTIONS)

HAS_SIDE_EFFECT = [
    'OpFunction',
    'OpFunctionParameter',
    'OpFunctionCall',
    'OpExtInst',
    'OpAtomicExchange',
    'OpAtomicCompareExchange',
    'OpAtomicCompareExchangeWeak',
    'OpAtomicIIncrement',
    'OpAtomicIDecrement',
    'OpAtomicIAdd',
    'OpAtomicISub',
    'OpAtomicUMin',
    'OpAtomicUMax',
    'OpAtomicAnd',
    'OpAtomicOr',
    'OpAtomicXor',
    'OpLabel',
    'OpAsyncGroupCopy',
    'OpWaitGroupEvents',
    'OpGroupAll',
    'OpGroupAny',
    'OpGroupBroadcast',
    'OpGroupIAdd',
    'OpGroupFAdd',
    'OpGroupFMin',
    'OpGroupUMin',
    'OpGroupSMin',
    'OpGroupFMax',
    'OpGroupUMax',
    'OpGroupSMax',
    'OpReadPipe',
    'OpWritePipe',
    'OpReservedReadPipe',
    'OpReservedWritePipe',
    'OpReserveReadPipePackets',
    'OpReserveWritePipePackets',
    'OpGroupReserveWritePipePackets',
    'OpEnqueueMarker',
    'OpEnqueueKernel',
    'OpCreateUserEvent',
    'OpAtomicIMin',
    'OpAtomicIMax'
]
