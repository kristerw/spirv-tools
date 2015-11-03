INST_FORMAT = {
    'OpAccessChain' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'VariableIds'],
    },
    'OpAll' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpAny' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpArrayLength' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'LiteralNumber'],
    },
    'OpAsyncGroupCopy' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id', 'Id', 'Id', 'Id', 'Id'],
    },
    'OpAtomicAnd' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicCompareExchange' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'MemorySemanticsMask', 'Id', 'Id'],
    },
    'OpAtomicCompareExchangeWeak' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'MemorySemanticsMask', 'Id', 'Id'],
    },
    'OpAtomicExchange' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicIAdd' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicIDecrement' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask'],
    },
    'OpAtomicIIncrement' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask'],
    },
    'OpAtomicISub' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicLoad' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask'],
    },
    'OpAtomicOr' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicSMax' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicSMin' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicStore' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicUMax' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicUMin' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpAtomicXor' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask', 'Id'],
    },
    'OpBitCount' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpBitFieldInsert' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpBitFieldSExtract' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpBitFieldUExtract' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpBitReverse' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpBitcast' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpBitwiseAnd' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpBitwiseOr' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpBitwiseXor' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpBranch' : {
        'type': False,
        'result': False,
        'operands': ['Id'],
    },
    'OpBranchConditional' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'Id', 'VariableLiterals'],
    },
    'OpBuildNDRange' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpCapability' : {
        'type': False,
        'result': False,
        'operands': ['Capability'],
    },
    'OpCaptureEventProfilingInfo' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpCommitReadPipe' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id'],
    },
    'OpCommitWritePipe' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id'],
    },
    'OpCompositeConstruct' : {
        'type': True,
        'result': True,
        'operands': ['VariableIds'],
    },
    'OpCompositeExtract' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'VariableLiterals'],
    },
    'OpCompositeInsert' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'VariableLiterals'],
    },
    'OpConstant' : {
        'type': True,
        'result': True,
        'operands': ['VariableLiterals'],
    },
    'OpConstantComposite' : {
        'type': True,
        'result': True,
        'operands': ['VariableIds'],
    },
    'OpConstantFalse' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpConstantNull' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpConstantSampler' : {
        'type': True,
        'result': True,
        'operands': ['SamplerAddressingMode', 'LiteralNumber', 'SamplerFilterMode'],
    },
    'OpConstantTrue' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpControlBarrier' : {
        'type': False,
        'result': False,
        'operands': ['Scope', 'Scope', 'MemorySemanticsMask'],
    },
    'OpConvertFToS' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpConvertFToU' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpConvertPtrToU' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpConvertSToF' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpConvertUToF' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpConvertUToPtr' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpCopyMemory' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'OptionalLiteral'],
    },
    'OpCopyMemorySized' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'Id', 'OptionalLiteral'],
    },
    'OpCopyObject' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpCreateUserEvent' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpDPdx' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpDPdxCoarse' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpDPdxFine' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpDPdy' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpDPdyCoarse' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpDPdyFine' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpDecorate' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Decoration', 'VariableLiterals'],
    },
    'OpDecorationGroup' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpDot' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpEmitStreamVertex' : {
        'type': False,
        'result': False,
        'operands': ['Id'],
    },
    'OpEmitVertex' : {
        'type': False,
        'result': False,
        'operands': [],
    },
    'OpEndPrimitive' : {
        'type': False,
        'result': False,
        'operands': [],
    },
    'OpEndStreamPrimitive' : {
        'type': False,
        'result': False,
        'operands': ['Id'],
    },
    'OpEnqueueKernel' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'VariableIds'],
    },
    'OpEnqueueMarker' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpEntryPoint' : {
        'type': False,
        'result': False,
        'operands': ['ExecutionModel', 'Id', 'LiteralString'],
    },
    'OpExecutionMode' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'ExecutionMode', 'OptionalLiteral'],
    },
    'OpExtInst' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'LiteralNumber', 'VariableIds'],
    },
    'OpExtInstImport' : {
        'type': False,
        'result': True,
        'operands': ['LiteralString'],
    },
    'OpExtension' : {
        'type': False,
        'result': False,
        'operands': ['LiteralString'],
    },
    'OpFAdd' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFConvert' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpFDiv' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFMod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFMul' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFNegate' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpFOrdEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFOrdGreaterThan' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFOrdGreaterThanEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFOrdLessThan' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFOrdLessThanEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFOrdNotEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFRem' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFSub' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFUnordEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFUnordGreaterThan' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFUnordGreaterThanEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFUnordLessThan' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFUnordLessThanEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFUnordNotEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpFunction' : {
        'type': True,
        'result': True,
        'operands': ['FunctionControlMask', 'Id'],
    },
    'OpFunctionCall' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'VariableIds'],
    },
    'OpFunctionEnd' : {
        'type': False,
        'result': False,
        'operands': [],
    },
    'OpFunctionParameter' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpFwidth' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpFwidthCoarse' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpFwidthFine' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpGenericCastToPtr' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpGenericCastToPtrExplicit' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'StorageClass'],
    },
    'OpGenericPtrMemSemantics' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpGetDefaultQueue' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpGetKernelNDrangeMaxSubGroupSize' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id', 'Id'],
    },
    'OpGetKernelNDrangeSubGroupCount' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id', 'Id'],
    },
    'OpGetKernelPreferredWorkGroupSizeMultiple' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpGetKernelWorkGroupSize' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpGetMaxPipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpGetNumPipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpGroupAll' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id'],
    },
    'OpGroupAny' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id'],
    },
    'OpGroupBroadcast' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id', 'Id'],
    },
    'OpGroupCommitReadPipe' : {
        'type': False,
        'result': False,
        'operands': ['Scope', 'Id', 'Id'],
    },
    'OpGroupCommitWritePipe' : {
        'type': False,
        'result': False,
        'operands': ['Scope', 'Id', 'Id'],
    },
    'OpGroupDecorate' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'VariableIds'],
    },
    'OpGroupFAdd' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'GroupOperation', 'Id'],
    },
    'OpGroupFMax' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'GroupOperation', 'Id'],
    },
    'OpGroupFMin' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'GroupOperation', 'Id'],
    },
    'OpGroupIAdd' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'GroupOperation', 'Id'],
    },
    'OpGroupMemberDecorate' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'VariableIdLiteral'],
    },
    'OpGroupReserveReadPipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id', 'Id'],
    },
    'OpGroupReserveWritePipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id', 'Id'],
    },
    'OpGroupSMax' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'GroupOperation', 'Id'],
    },
    'OpGroupSMin' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'GroupOperation', 'Id'],
    },
    'OpGroupUMax' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'GroupOperation', 'Id'],
    },
    'OpGroupUMin' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'GroupOperation', 'Id'],
    },
    'OpIAdd' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpIAddCarry' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpIEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpIMul' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpIMulExtended' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpINotEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpISub' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpISubBorrow' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpImageDrefGather' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImage'],
    },
    'OpImageFetch' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImage'],
    },
    'OpImageGather' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImage'],
    },
    'OpImageQueryDim' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpImageQueryFormat' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpImageQueryLevels' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpImageQueryLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpImageQueryOrder' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpImageQuerySamples' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpImageQuerySize' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpImageQuerySizeLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpImageRead' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpImageSampleDrefExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImage'],
    },
    'OpImageSampleDrefImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImage'],
    },
    'OpImageSampleExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImage'],
    },
    'OpImageSampleImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImage'],
    },
    'OpImageSampleProjDrefExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImage'],
    },
    'OpImageSampleProjDrefImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImage'],
    },
    'OpImageSampleProjExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImage'],
    },
    'OpImageSampleProjImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImage'],
    },
    'OpImageTexelPointer' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpImageWrite' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpInBoundsAccessChain' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'VariableIds'],
    },
    'OpIsFinite' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpIsInf' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpIsNan' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpIsNormal' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpIsValidEvent' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpIsValidReserveId' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpKill' : {
        'type': False,
        'result': False,
        'operands': [],
    },
    'OpLabel' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpLessOrGreater' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpLifetimeStart' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'LiteralNumber'],
    },
    'OpLifetimeStop' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'LiteralNumber'],
    },
    'OpLine' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'LiteralNumber', 'LiteralNumber'],
    },
    'OpLoad' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'OptionalLiteral'],
    },
    'OpLogicalAnd' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpLogicalEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpLogicalNot' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpLogicalNotEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpLogicalOr' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpLoopMerge' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'LoopControlMask'],
    },
    'OpMatrixTimesMatrix' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpMatrixTimesScalar' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpMatrixTimesVector' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpMemberDecorate' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'LiteralNumber', 'Decoration', 'VariableLiterals'],
    },
    'OpMemberName' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'LiteralNumber', 'LiteralString'],
    },
    'OpMemoryBarrier' : {
        'type': False,
        'result': False,
        'operands': ['Scope', 'MemorySemanticsMask'],
    },
    'OpMemoryModel' : {
        'type': False,
        'result': False,
        'operands': ['AddressingModel', 'MemoryModel'],
    },
    'OpName' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'LiteralString'],
    },
    'OpNop' : {
        'type': False,
        'result': False,
        'operands': [],
    },
    'OpNot' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpOrdered' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpOuterProduct' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpPhi' : {
        'type': True,
        'result': True,
        'operands': ['VariableIds'],
    },
    'OpPtrAccessChain' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'VariableIds'],
    },
    'OpPtrCastToGeneric' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpQuantizeToF16' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpReadPipe' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpReleaseEvent' : {
        'type': False,
        'result': False,
        'operands': ['Id'],
    },
    'OpReserveReadPipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpReserveWritePipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpReservedReadPipe' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpReservedWritePipe' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpRetainEvent' : {
        'type': False,
        'result': False,
        'operands': ['Id'],
    },
    'OpReturn' : {
        'type': False,
        'result': False,
        'operands': [],
    },
    'OpReturnValue' : {
        'type': False,
        'result': False,
        'operands': ['Id'],
    },
    'OpSConvert' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpSDiv' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSGreaterThan' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSGreaterThanEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSLessThan' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSLessThanEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSMod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSNegate' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpSRem' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSampledImage' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSatConvertSToU' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpSatConvertUToS' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpSelect' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpSelectionMerge' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'SelectionControlMask'],
    },
    'OpSetUserEventStatus' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id'],
    },
    'OpShiftLeftLogical' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpShiftRightArithmetic' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpShiftRightLogical' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpSignBitSet' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpSource' : {
        'type': False,
        'result': False,
        'operands': ['SourceLanguage', 'LiteralNumber'],
    },
    'OpSourceExtension' : {
        'type': False,
        'result': False,
        'operands': ['LiteralString'],
    },
    'OpSpecConstant' : {
        'type': True,
        'result': True,
        'operands': ['VariableLiterals'],
    },
    'OpSpecConstantComposite' : {
        'type': True,
        'result': True,
        'operands': ['VariableIds'],
    },
    'OpSpecConstantFalse' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpSpecConstantOp' : {
        'type': True,
        'result': True,
        'operands': ['LiteralNumber', 'VariableIds'],
    },
    'OpSpecConstantTrue' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpStore' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'OptionalLiteral'],
    },
    'OpString' : {
        'type': False,
        'result': True,
        'operands': ['LiteralString'],
    },
    'OpSwitch' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'VariableLiteralId'],
    },
    'OpTranspose' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpTypeArray' : {
        'type': False,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpTypeBool' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpTypeDeviceEvent' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpTypeEvent' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpTypeFloat' : {
        'type': False,
        'result': True,
        'operands': ['LiteralNumber'],
    },
    'OpTypeFunction' : {
        'type': False,
        'result': True,
        'operands': ['Id', 'VariableIds'],
    },
    'OpTypeImage' : {
        'type': False,
        'result': True,
        'operands': ['Id', 'Dim', 'LiteralNumber', 'LiteralNumber', 'LiteralNumber', 'LiteralNumber', 'ImageFormat', 'OptionalLiteral'],
    },
    'OpTypeInt' : {
        'type': False,
        'result': True,
        'operands': ['LiteralNumber', 'LiteralNumber'],
    },
    'OpTypeMatrix' : {
        'type': False,
        'result': True,
        'operands': ['Id', 'LiteralNumber'],
    },
    'OpTypeOpaque' : {
        'type': False,
        'result': True,
        'operands': ['LiteralString'],
    },
    'OpTypePipe' : {
        'type': False,
        'result': True,
        'operands': ['Id', 'AccessQualifier'],
    },
    'OpTypePointer' : {
        'type': False,
        'result': True,
        'operands': ['StorageClass', 'Id'],
    },
    'OpTypeQueue' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpTypeReserveId' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpTypeRuntimeArray' : {
        'type': False,
        'result': True,
        'operands': ['Id'],
    },
    'OpTypeSampledImage' : {
        'type': False,
        'result': True,
        'operands': ['Id'],
    },
    'OpTypeSampler' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpTypeStruct' : {
        'type': False,
        'result': True,
        'operands': ['VariableIds'],
    },
    'OpTypeVector' : {
        'type': False,
        'result': True,
        'operands': ['Id', 'LiteralNumber'],
    },
    'OpTypeVoid' : {
        'type': False,
        'result': True,
        'operands': [],
    },
    'OpUConvert' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpUDiv' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpUGreaterThan' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpUGreaterThanEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpULessThan' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpULessThanEqual' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpUMod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpUndef' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpUnordered' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpUnreachable' : {
        'type': False,
        'result': False,
        'operands': [],
    },
    'OpVariable' : {
        'type': True,
        'result': True,
        'operands': ['StorageClass', 'OptionalId'],
    },
    'OpVectorExtractDynamic' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpVectorInsertDynamic' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpVectorShuffle' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'VariableLiterals'],
    },
    'OpVectorTimesMatrix' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpVectorTimesScalar' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpWaitGroupEvents' : {
        'type': False,
        'result': False,
        'operands': ['Scope', 'Id', 'Id'],
    },
    'OpWritePipe' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
}
