##API Overview
This API is meant to be used for basic analysis and manipulation of SPIR-V 
binaries, and it tries to keep its representation close to the real binary.
The API can represent all valid SPIR-V binaries, so it is possible to read
a binary into the IR and writing the result to a new identical binary.

The IR consists of the SPIR-V instructions, and iterators traverse the IR
in the order they are written in the binary. But there are one layer of
abstraction in top of this to represent functions and basic blocks, to
simplify implementation of analysis and transformation passes.

The IR is encapsulated in a `Module`. This consist of a list of global
instructions and a list of function. The `Function` class represents
one function, that is, all instructions from a `OpFunction` to the
`OpFunctionEnd`. The instructions are grouped in the `BasicBlock` class,
which consists of all instructions from an `OpLabel` to the branch and return
instructions. Finally the instructions are represented by the `Instruction`
class.

Most information in the classes (such as lists of functions, basic blocks,
instructions) are meant to be read by applications, but applications must
not modify the informations directly. Instead, the objects have methods
for updating the fields. The reason for this is so that the IR implementation
may update data structures keeping track of various information in order to
make the API more efficient, or for validity checking.

_**Note**: The current implementation does not use any data structure on the
side, which makes some operations slow. For example, finding uses of an
instruction iterates through the whole binary. This is expected to be
fixed soon..._

The instruction is represented by its ID, operation name, type, and
operands. The fields are mostly represented in the same form as in the
high level assembly language used by the `spirv-as`/`spirv-dis`; the IDs
are represented as strings `'%123'` where the ID number is the one used
in the binary. The implementation may add temporary IDs of the form
`'%.23'` that is allocated to real numbers at end of every transformation
pass. An application should in general never create IDs itself; the only
exception is when implementing an assembler. All other IDs should be
created by calling `module.new_id()`. The operation is represented by
the operation name. The operands for the enumerated constants (such as
the Storage Class) are represented as stings of the value (such as
`'Input'`).

_**TODO**: Integers, floating point, and Boolean values are represented
as strings of the integer in the binary. This will change. But it is not
clear to me that Python floating point values are guaranteed to preserve
the exact value._

_**TODO**: Masks are currently represented as a string of the integer value.
This should change to a normal integer._

The `result_id` and `type` attributes are `None` for operations not using
them, and `operands` are the empty list for instructions without operands.

The types and most operands are represented as the ID as used in the
binary. But most transformations on the IR need the instruction, so the
application need to transform between the instruction and id using the
`module.id_to_instr[]` dictionary. For example, the type instruction
used by `instr` is retrieved by `module.id_to_instr[instr.type]`.

Instructions are immutable, so it is not possible to modify it after
it is created. The way of modifying it is to create a new (nearly)
identical instruction, and to substitute the original with the new
instruction. For example, to switch the order of two operands of
`instr`:

```
new_instr = ir.Instruction(module, instr.op_name, module.new_id(), instr.type,
                           [instr.operands[1], instr.operands[0]]
instr.replace_with(new_instr)
```

This changes the ID of the instruction, and it may be argued that 
there is a use case to modify one instruction (i.e. to keep the
original ID) in order to make minimal change in the binary. This
is not directly supported in the API, but it can be accomplished
by inserting a temporary instruction

```
tmp_instr = ir.Instruction(module, 'OpUndef', module.new_id(), instr.type, [])
instr.replace_with(tmp_instr)
new_instr = ir.Instruction(module, instr.op_name, module.new_id(), instr.type,
                           [instr.operands[1], instr.operands[0]]
tmp_instr.replace_with(new_instr)
```

There is one exception to “immutable” – it is possible to update
the type and operands IDs to use some other ID by calling the
`substitute_type_and_operands()` method. This is usually not done
directly, but happens in the background of the `replace_with()` above.

Most of the API use the instruction rather than the ID (and the ID
of instr is available as `instr.result_id`). It is possible to iterate
over all instructions in the module by `module.instructions()`. The
instructions are retrieved in the same order as in the binary. It is
allowed to modify the IR while iterating over the instructions, but
removed/added instructions may/may not be seen. Removed/destroyed
basic blocks are guaranteed to not be seen when iterating, but 
added basic blocks may/may not be seen, depending on the implementation.
