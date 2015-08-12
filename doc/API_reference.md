##API Overview
This API is meant to be used for basic analysis and manipulation of SPIR-V 
binaries, and it tries to keep its representation close to the real binary;
the IR consists of the SPIR-V instructions, and iterators traverse the IR
in the order they are stored in the binary. But there is one layer of
abstraction on top of this to represent functions and basic blocks, in
order to simplify implementation of analysis and transformation passes.

The IR is encapsulated in a `Module`. This consists of a list of global
instructions and a list of functions. The `Function` class represents
one function, that is, all instructions from an `OpFunction` to the
`OpFunctionEnd`. The instructions are grouped in the `BasicBlock` class,
which consists of all instructions from an `OpLabel` to the branch or return
instruction. Finally the instructions are represented by the `Instruction`
class.

Most information in the classes (such as lists of functions, basic blocks,
instructions) are meant to be read by applications, but applications must
not modify the information directly. Instead, the objects have methods
for updating the data. The reason for this is so the IR implementation
may update data structures keeping track of various information in order to
make the API more efficient, or for validity checking.

_**Note**: The current implementation does not use any data structure on the
side, which makes some operations very slow. For example, finding uses of an
instruction iterates through the whole binary. This is expected to be
fixed soon..._

The `Instruction` object consists of the result ID, opcode name, type ID, and
operands. The fields are mostly represented in the same form as in the
high level assembly language used by the `spirv-as`/`spirv-dis`; the IDs
are represented as strings `'%123'` where the ID number is the one used
in the binary. The implementation may add temporary IDs of the form
`'%.23'` that is allocated to real numbers at end of every transformation
pass. An application should in general never create IDs itself; the only
exception is when implementing an assembler. All other IDs should be
created by calling `module.new_id()`. The opcode is represented by
the operation name (such as `'OpFAdd'`). The operands for the enumerated constants (such as
the Storage Class) are represented as strings of the values (such as
`'Input'`).

_**TODO**: Integers, floating point, and Boolean values are currently represented
as strings of the integer value used the binary. This will change. But it is not
clear to me that Python floating point values are guaranteed to preserve
the exact value._

_**TODO**: Masks are currently represented as a string of the integer value.
This should probably change to a normal integer._

The `result_id` and `type_id` values are `None` for operations not using
them, and `operands` is an empty list for instructions without operands.

The types and most operands are represented as the ID as used in the
binary. But most transformations on the IR need the instruction, so the
application need to transform between the instruction and ID using the
`module.id_to_inst[]` dictionary. For example, the type instruction
used by `inst` is retrieved by `module.id_to_inst[inst.type_id]`.

Instructions are immutable, so it is not possible to modify it after
it is created. The way of modifying it is to create a new (nearly)
identical instruction, and to substitute the original with the new
instruction. For example, to switch the order of two operands of
`inst`:

```
new_inst = ir.Instruction(module, inst.op_name, module.new_id(), inst.type_id,
                          [inst.operands[1], inst.operands[0]]
inst.replace_with(new_inst)
```

This changes the ID of the instruction, and it may be argued that 
there is a use case to modify one instruction (i.e. to keep the
original ID) in order to make minimal change in the binary. This
is not directly supported in the API, but it can be accomplished
by inserting a temporary instruction

```
tmp_inst = ir.Instruction(module, 'OpUndef', module.new_id(), inst.type_id, [])
inst.replace_with(tmp_inst)
new_inst = ir.Instruction(module, inst.op_name, module.new_id(), inst.type_id,
                          [inst.operands[1], inst.operands[0]]
tmp_inst.replace_with(new_inst)
```

There is one exception to instructions being immutable – it is possible to update
the type and operands IDs to use some other ID by calling the
`substitute_type_and_operands()` method. This is usually not done
directly, but happens in the background of the `replace_with()` above.

It is possible to iterate
over all instructions in the module by `module.instructions()`. The
instructions are retrieved in the same order as in the binary. It is
allowed to modify the IR while iterating over the instructions, but
instruction added to the current basic block will not be seen by the
iterator. Instructions that are moved (i.e. removed and re-inserted)
in the current basic block may be returned as if it was in its old
position.

TBD - Decorations, debug instructions etc.

TBD - Global instructions

## IR
TBD

## Input/Output
TBD

## Optimizations
TBD
