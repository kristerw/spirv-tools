INST_FORMAT = {
    'OpAccessChain' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'VariableId'],
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
    'OpAtomicFlagClear' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask'],
    },
    'OpAtomicFlagTestAndSet' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Scope', 'MemorySemanticsMask'],
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
        'operands': ['Id', 'Id', 'Id', 'VariableLiteralNumber'],
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
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpCommitWritePipe' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpCompositeConstruct' : {
        'type': True,
        'result': True,
        'operands': ['VariableId'],
    },
    'OpCompositeExtract' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'VariableLiteralNumber'],
    },
    'OpCompositeInsert' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'VariableLiteralNumber'],
    },
    'OpConstant' : {
        'type': True,
        'result': True,
        'operands': ['VariableLiteralNumber'],
    },
    'OpConstantComposite' : {
        'type': True,
        'result': True,
        'operands': ['VariableId'],
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
        'operands': ['Id', 'Id', 'OptionalMemoryAccessMask'],
    },
    'OpCopyMemorySized' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'Id', 'OptionalMemoryAccessMask'],
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
        'operands': ['Id', 'Decoration', 'VariableLiteralNumber'],
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
        'operands': ['Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'Id', 'VariableId'],
    },
    'OpEnqueueMarker' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpEntryPoint' : {
        'type': False,
        'result': False,
        'operands': ['ExecutionModel', 'Id', 'LiteralString', 'VariableId'],
    },
    'OpExecutionMode' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'ExecutionMode', 'OptionalLiteralNumber'],
    },
    'OpExtInst' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'LiteralNumber', 'VariableId'],
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
        'operands': ['Id', 'VariableId'],
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
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpGetNumPipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id'],
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
    'OpGroupAsyncCopy' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id', 'Id', 'Id', 'Id', 'Id'],
    },
    'OpGroupBroadcast' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id', 'Id'],
    },
    'OpGroupCommitReadPipe' : {
        'type': False,
        'result': False,
        'operands': ['Scope', 'Id', 'Id', 'Id', 'Id'],
    },
    'OpGroupCommitWritePipe' : {
        'type': False,
        'result': False,
        'operands': ['Scope', 'Id', 'Id', 'Id', 'Id'],
    },
    'OpGroupDecorate' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'VariableId'],
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
        'operands': ['Id', 'VariableIdLiteralPair'],
    },
    'OpGroupReserveReadPipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id', 'Id', 'Id', 'Id'],
    },
    'OpGroupReserveWritePipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Scope', 'Id', 'Id', 'Id', 'Id'],
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
    'OpGroupWaitEvents' : {
        'type': False,
        'result': False,
        'operands': ['Scope', 'Id', 'Id'],
    },
    'OpIAdd' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
    },
    'OpIAddCarry' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id'],
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
        'operands': ['Id', 'Id'],
    },
    'OpImage' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpImageDrefGather' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageFetch' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageGather' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
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
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSampleDrefExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSampleDrefImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSampleExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSampleImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSampleProjDrefExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSampleProjDrefImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSampleProjExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSampleProjImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseDrefGather' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseFetch' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseGather' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseSampleDrefExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseSampleDrefImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseSampleExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseSampleImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseSampleProjDrefExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseSampleProjDrefImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseSampleProjExplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseSampleProjImplicitLod' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpImageSparseTexelsResident' : {
        'type': True,
        'result': True,
        'operands': ['Id'],
    },
    'OpImageTexelPointer' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id'],
    },
    'OpImageWrite' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'Id', 'OptionalImageOperandsMask', 'VariableId'],
    },
    'OpInBoundsAccessChain' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'VariableId'],
    },
    'OpInBoundsPtrAccessChain' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'VariableId'],
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
        'operands': ['Id', 'LiteralNumber', 'LiteralNumber'],
    },
    'OpLoad' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'OptionalMemoryAccessMask'],
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
        'operands': ['Id', 'Id', 'LoopControlMask'],
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
        'operands': ['Id', 'LiteralNumber', 'Decoration', 'VariableLiteralNumber'],
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
    'OpNoLine' : {
        'type': False,
        'result': False,
        'operands': [],
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
        'operands': ['VariableId'],
    },
    'OpPtrAccessChain' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'VariableId'],
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
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpReleaseEvent' : {
        'type': False,
        'result': False,
        'operands': ['Id'],
    },
    'OpReserveReadPipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpReserveWritePipePackets' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
    'OpReservedReadPipe' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id', 'Id', 'Id'],
    },
    'OpReservedWritePipe' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id', 'Id', 'Id'],
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
    'OpSMulExtended' : {
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
        'operands': ['SourceLanguage', 'LiteralNumber', 'OptionalId', 'OptionalLiteralString'],
    },
    'OpSourceContinued' : {
        'type': False,
        'result': False,
        'operands': ['LiteralString'],
    },
    'OpSourceExtension' : {
        'type': False,
        'result': False,
        'operands': ['LiteralString'],
    },
    'OpSpecConstant' : {
        'type': True,
        'result': True,
        'operands': ['VariableLiteralNumber'],
    },
    'OpSpecConstantComposite' : {
        'type': True,
        'result': True,
        'operands': ['VariableId'],
    },
    'OpSpecConstantFalse' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpSpecConstantOp' : {
        'type': True,
        'result': True,
        'operands': ['LiteralNumber', 'VariableId'],
    },
    'OpSpecConstantTrue' : {
        'type': True,
        'result': True,
        'operands': [],
    },
    'OpStore' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'OptionalMemoryAccessMask'],
    },
    'OpString' : {
        'type': False,
        'result': True,
        'operands': ['LiteralString'],
    },
    'OpSwitch' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'Id', 'VariableLiteralIdPair'],
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
    'OpTypeForwardPointer' : {
        'type': False,
        'result': False,
        'operands': ['Id', 'StorageClass'],
    },
    'OpTypeFunction' : {
        'type': False,
        'result': True,
        'operands': ['Id', 'VariableId'],
    },
    'OpTypeImage' : {
        'type': False,
        'result': True,
        'operands': ['Id', 'Dim', 'LiteralNumber', 'LiteralNumber', 'LiteralNumber', 'LiteralNumber', 'ImageFormat', 'OptionalAccessQualifierMask'],
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
        'operands': ['AccessQualifier'],
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
        'operands': ['VariableId'],
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
    'OpUMulExtended' : {
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
        'operands': ['Id', 'Id', 'VariableLiteralNumber'],
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
    'OpWritePipe' : {
        'type': True,
        'result': True,
        'operands': ['Id', 'Id', 'Id', 'Id'],
    },
}
