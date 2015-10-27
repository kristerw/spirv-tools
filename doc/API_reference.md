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
class, where the SPIR-V IDs are represented by the `Id` class

Most class attributes (such as lists of functions, basic blocks,
instructions) are meant to be read by applications, but applications must
not modify the information directly. Instead, the objects have methods
for updating the data. The reason for this is so the IR implementation
may update data structures keeping track of various information in order to
make the API more efficient, or for validity checking.

The `Instruction` object consists of the result ID, opcode name, type ID, and
operands. The fields are mostly represented in the same form as in the
high level assembly language used by the `spirv-as`/`spirv-dis`; the IDs
are represented as objects of the `Id` class that contains the value of the ID,
and a link to the instruction that defines the ID. An application should in general
never create ID values itself; the only exception is when implementing an assembler.
All other IDs should be created implicitly by creating the instructions without
providing an ID. The opcode is represented by
the operation name (such as `'OpFAdd'`). The operands for the enumerated constants (such as
the Storage Class) are represented as strings of the values (such as
`'Input'`), and masks are represented as a list of enumerated constants.

The `result_id` and `type_id` values are `None` for operations not using
them, and `operands` is an empty list for instructions without operands.

Instructions are immutable, so it is not possible to modify it after
it is created. The way of modifying it is to create a new (nearly)
identical instruction, and to substitute the original with the new
instruction. For example, to switch the order of two operands of
`inst`:

```
new_inst = ir.Instruction(module, inst.op_name, inst.type_id,
                          [inst.operands[1], inst.operands[0]]
inst.replace_with(new_inst)
```

This changes the ID of the instruction, and it may be argued that 
there is a use case to modify one instruction (i.e. to keep the
original ID) in order to make minimal change in the binary. This
is not directly supported in the API, but it can be accomplished
by inserting a temporary instruction

```
tmp_inst = ir.Instruction(module, 'OpUndef', inst.type_id, [])
inst.replace_with(tmp_inst)
new_inst = ir.Instruction(module, inst.op_name, inst.type_id,
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

###Module methods
######`add_global_inst(inst)`
Add instruction `inst` to the module's global instructions.

The instruction is appended to its section in the module (For example, adding an `OpExtInstImport` instruction will be added after the existing `OpExtInstImport` instructions, but before the `OpMemoryModel` instruction).

**Note**: Applications should in general use `get_global_inst()` instead of `add_global_inst()`.

######`add_function(function)`
Add a function to the module.

######`dump(stream=sys.stdout)`
Write a debug dump of the module to stream.

The format of the dump is similar to the high level assembly syntax used by `read_il` and `write_il`

######`get_constant()`
**TODO**

######`get_global_inst(op_name, type_id, operands)`
Return a global instruction. An existing instruction is returned if it exist, otherwise a newly created instruction is returned and inserted into the module.

This method is the preferred way of creating global instructions. For example, creating a type instruction is done as
```
get_global_inst('OpTypeInt', 32, 1)
```

######`is_constant_value()`
**TODO**

######`instructions()`
Iterator for iterating over the module's instructions in the order they are located in the SPIR-V binary.

It is allowed to insert or remove instructions while iterating over the module, although instructions inserted during iteration are not guaranteed to be seen during the iteration.

It is not allowed to insert/remove basic blocks or functions while iterating over the instructions.

######`instructions_reversed()`
Iterator for iterating over the module's instructions in reversed order.

It is allowed to insert or remove instructions while iterating over the module, although instructions inserted during iteration are not guaranteed to be seen during the iteration.

It is not allowed to insert/remove basic blocks or functions while iterating over the instructions.

######`optimize()`
Run basic optimization passes.

The aim of the optimization passes is to only do optimizations that are profitable for all architectures, which means that it only do things like removing dead code, simple peephole optimizations in order to get rid of obviously needless code (such as `-(-a)` is changed to `a`), and promoting function-local `OpVariable` to registers.

######`renumber_temp_ids()`
**TODO**

## Input/Output
TBD

## Optimizations
TBD
