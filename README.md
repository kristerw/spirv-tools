# spirv-tools
This package tries to provide functionality that I saw a need for when I was working as an architect for a GPU compiler — many teams have a need to manipulate shaders/shader binaries, and they prefer not to modify the compiler...

A typical case is a need to analyze an application API trace. For example, customer support need to analyze why the application misbehaves. One part of this is disassembling shaders to see what they do. And it is also useful to write scripts that identifies common problems (for example, is the shader using `RelaxedPrecision` in a way that may be problematic for an implementation using 16-bit precision for those calcualtions?), and to modify shaders to test hypotheses (such as removing `RelaxedPrecision` from all calculations).

One other important use case is test generation. This may be generating shaders that trigger all possible combinations of some hardware features, or fuzz testing the compiler by generating/modifying shaders.

A third use case is experimenting with optimization ideas before implementing them for real in the compiler.

This package contains a Python [API](doc/API_reference.md) that is meant to be easy to use for manipulating SPIR-V — iterating through binaries, and doing local modification is done with a few lines of Python code. For example, reading a SPIR-V binary from a file `orig.spv`, optimizing away all cases of double negation (i.e. `-(-a)` is changed to `a`), and writing the result to a file `result.spv` can be done as
```python
#!/usr/bin/env python
import read_spirv
import write_spirv

with open('orig.spv', 'r') as stream:
    module = read_spirv.read_module(stream)

for inst in module.instructions():
    if inst.op_name == 'OpSNegate':
        operand_inst = inst.operands[0].inst
        if operand_inst.op_name == 'OpSNegate':
            inst.replace_uses_with(operand_inst.operands[0].inst)

with open('result.spv', 'w') as stream:
    write_spirv.write_module(stream, module)
```

There are also a number of optimization passes for things like dead code removal, peephole optimizations, and promoting local variables to registers, etc. (So the example above could have been done by just calling the instcombine optimization pass...)

The package also contains an assembler and disassembler using a somewhat higher level representation than the assembly in the SPIR-V specification, that makes it easier to write / modify shaders. The syntax is LLVM-like, and you can use named ID values instead of numerical, and the assembler keeps track of many of the constraints, so you do not need to e.g. specify basic types before you use them.

Here is assembler output from a [Warzone 2011](https://wz2100.net/) shader as an example of the syntax
```
OpSource GLSL, 120
OpCapability Shader
OpMemoryModel Logical, GLSL450
OpEntryPoint Fragment, %main, "main"
OpExecutionMode %main, OriginLowerLeft

%11 = OpTypeImage f32, Dim2D, 0, 0, 0, 1, Unknown
%12 = OpTypeSampledImage %11
%13 = OpTypePointer UniformConstant, %12
%18 = OpTypeArray <4 x f32>, 1
%19 = OpTypePointer Input, %18
%23 = OpTypePointer Input, <4 x f32>
%29 = OpTypePointer UniformConstant, s32
%44 = OpTypePointer Output, <4 x f32>
%47 = OpTypePointer UniformConstant, <4 x f32>

%Texture0 = OpVariable %13 UniformConstant
%gl_TexCoord = OpVariable %19 Smooth Input
%tcmask = OpVariable %29 UniformConstant
%Texture1 = OpVariable %13 UniformConstant
%gl_FragColor = OpVariable %44 BuiltIn(FragColor) Output
%teamcolour = OpVariable %47 UniformConstant
%gl_Color = OpVariable %23 Smooth Input

define void %main() {
%5:
  %15 = OpLoad %12 %Texture0
  %24 = OpAccessChain %23 %gl_TexCoord, 0
  %25 = OpLoad <4 x f32> %24
  %27 = OpVectorShuffle <2 x f32> %25, %25, 0, 1
  %28 = OpImageSampleImplicitLod <4 x f32> %15, %27
  %31 = OpLoad s32 %tcmask
  %34 = OpIEqual bool %31, 1
  OpSelectionMerge %36, MaskNone
  OpBranchConditional %34, %35, %60

%35:
  %39 = OpLoad %12 %Texture1
  %43 = OpImageSampleImplicitLod <4 x f32> %39, %27
  %49 = OpLoad <4 x f32> %teamcolour
  %52 = OpFSub <4 x f32> %49, (0.5, 0.5, 0.5, 0.5)
  %54 = OpCompositeExtract f32 %43, 3
  %55 = OpVectorTimesScalar <4 x f32> %52, %54
  %56 = OpFAdd <4 x f32> %28, %55
  %58 = OpLoad <4 x f32> %gl_Color
  %59 = OpFMul <4 x f32> %56, %58
  OpStore %gl_FragColor, %59
  OpBranch %36

%60:
  %62 = OpLoad <4 x f32> %gl_Color
  %63 = OpFMul <4 x f32> %28, %62
  OpStore %gl_FragColor, %63
  OpBranch %36

%36:
  OpReturn
}
```
The assembler syntax is not finalized yet (I'm waiting for the final SPIR-V specification), but the format used by the initial implementation is described in a [blog post](http://kristerw.blogspot.se/2015/05/human-friendly-spir-v-textual.html).

The assembler/dissassembler are used as:
```
spirv-as [-O] file.il
spirv-dis [-r] [-O] file.spv
```
The `-r` option to the dissassembler restricts the use of features in order to generate output that assembles to an identical binary as the original (for example, it always defines types before usage, so that the assembler does not need to add new operations for those, which in general gives them different ID numbers compared to the original binary).

This package is very much "work in progress", and is only lightly tested as the SPIR-V specification is not done yet, and there are no implementations to interoperate with...  See the [TODO](TODO.md) file for a list of the issues/limitations in the current implementation.
