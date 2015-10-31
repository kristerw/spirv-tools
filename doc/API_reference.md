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

###class ir.Module
####Methods
<dl>
  <dt><code>append_function(function)</code></dt>
  <dd>Insert function at the end of the module.</dd>

  <dt><code>dump(stream=sys.stdout)</code></dt>
  <dd><p>
  Write a debug dump of the module to stream.
  </p><p>
  The format of the dump is similar to the high level assembly syntax used by <code>read_il</code> and <code>write_il</code>.
  </p></dd>

  <dt><code>get_constant()</code></dt>
  <dd><b>TODO</b></dd>

  <dt><code>get_global_inst(op_name, type_id, operands)</code></dt>
  <dd><p>
  Return a global instruction. An existing instruction is returned if it exist, otherwise a newly created instruction is returned and inserted into the module.
  </p><p>
  This method is the preferred way of creating global instructions. For example, creating a type instruction is done as <pre><code>get_global_inst('OpTypeInt', 32, 1)</code></pre>
  </p></dd>

  <dt><code>is_constant_value()</code></dt>
  <dd><b>TODO</b></dd>

  <dt><code>insert_global_inst(inst)</code></dt>
  <dd><p>
  Insert the global instruction <code>inst</code> into the module.
  </p><p>
  The instruction is appended to its section in the module (for example, adding an <code>OpExtInstImport</code> instruction will be added after the existing <code>OpExtInstImport</code> instructions, but before the <code>OpMemoryModel</code> instruction).
  </p><p>
  <b>Note</b>: Applications should in general use <code>get_global_inst()</code> instead of <code>insert_global_inst()</code>.
  </p></dd>

  <dt><code>insert_function_after(function, insert_pos_function)</code></dt>
  <dd>Insert function <code>function</code> after the function <code>insert_pos_function</code>.</dd>

  <dt><code>insert_function_before(function, insert_pos_function)</code></dt>
  <dd>Insert function <code>function</code> before the function <code>insert_pos_function</code>.</dd>

  <dt><code>instructions()</code></dt>
  <dd><p>
  Iterator for iterating over the module's instructions in the order they are located in the SPIR-V binary.
  </p><p>
  It is allowed to insert or remove instructions while iterating over the module, although instructions inserted during iteration are not guaranteed to be seen during the iteration.
  </p><p>
  It is not allowed to insert/remove basic blocks or functions while iterating over the instructions.
  </p></dd>

  <dt><code>instructions_reversed()</code></dt>
  <dd><p>
  Iterator for iterating over the module's instructions in reverse order.
  </p><p>
  It is allowed to insert or remove instructions while iterating over the module, although instructions inserted during iteration are not guaranteed to be seen during the iteration.
  </p><p>
  It is not allowed to insert/remove basic blocks or functions while iterating over the instructions.
  </p></dd>

  <dt><code>optimize()</code></dt>
  <dd><p>
  Run basic optimization passes.
  </p><p>
  The aim of the optimization passes is to only do optimizations that are profitable for all architectures, which means that it only do things like removing dead code, simple peephole optimizations in order to get rid of obviously needless code (such as <code>-(-a)</code> is changed to <code>a</code>), and promoting function-local <code>OpVariable</code> to registers.
  </p></dd>

  <dt><code>prepend_function(function)</code></dt>
  <dd>Insert function at the top of the module.</dd>

  <dt><code>renumber_temp_ids()</code></dt>
  <dd><b>TODO</b></dd>
</dl>

####Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code>global_instructions</code></dt>
  <dd>The pseudo-basic block of class <code>_GlobalInstructions</code>
  containing the module's global instructions.</dd>

  <dt><code>functions</code></dt>
  <dd>A list of the functions within this module.</dd>
</dl>

###class ir.Function
####Methods
<dl>
  <dt><code>append_basic_block(basic_block)</code></dt>
  <dd>Insert basic block <code>basic_block</code> at the end of the function.</dd>

  <dt><code>append_parameter(inst)</code></dt>
  <dd>Insert the <code>OpFunctionParameter</code> <code>inst</code> at the end of the function's parameter list.</dd>

  <dt><code>destroy()</code></dt>
  <dd><p>
  Destroy this function.
  </p><p>
  This removes the function from the module (if it is attached to a module), and destroys all basic blocks and instructions used in the function.
  </p><p>
  The function must not be used after it is destroyed.
  </p></dd>

  <dt><code>dump(stream=sys.stdout)</code></dt>
  <dd><p>Write a debug dump of the function to stream.
  </p><p>
  The format of the dump is similar to the high level assembly syntax used by <code>read_il</code> and <code>write_il</code>.
  </p></dd>

  <dt><code>insert_basic_block_after(basic_block, insert_pos_basic_block)</code></dt>
  <dd>Insert basic block <code>basic_block</code> after the basic_block <code>insert_pos_basic_block</code>.</dd>

  <dt><code>insert_basic_block_before(basic_block, insert_pos_basic_block)</code></dt>
  <dd>Insert basic block <code>basic_block</code> before the basic_block <code>insert_pos_basic_block</code>.</dd>

  <dt><code>instructions()</code></dt>
  <dd><p>
  Iterator for iterating over the function's instructions in the order they are located in the SPIR-V binary.
  </p><p>
  It is allowed to insert or remove instructions while iterating over the function, although instructions inserted during iteration are not guaranteed to be seen during the iteration.
  </p><p>
  It is not allowed to insert/remove basic blocks while iterating over the instructions.
  </p></dd>

  <dt><code>instructions_reversed()</code></dt>
  <dd><p>
  Iterator for iterating over the function's instructions in reverse order.
  </p><p>
  It is allowed to insert or remove instructions while iterating over the function, although instructions inserted during iteration are not guaranteed to be seen during the iteration.
  </p><p>
  It is not allowed to insert/remove basic blocks while iterating over the instructions.
  </p></dd>

  <dt><code>prepend_basic_block(basic_block)</code></dt>
  <dd>Insert basic block <code>basic_block</code> at the top of the function.</dd>
</dl>

####Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code>parameters</code></dt>
  <dd>A list of the <code>OpFunctionParameter</code> instructions for
  the function's parameters.</dd>

  <dt><code>basic_blocks</code></dt>
  <dd>A list of the basic_blocks within this function.</dd>

  <dt><code>inst</code></dt>
  <dd>The <code>OpFunction</code> instruction defining this function.</dd>

  <dt><code>end_inst</code></dt>
  <dd>The <code>OpFunctionEnd</code> instruction ending this function.</dd>

  <dt><code>module</code></dt>
  <dd>The module this function is associated with.</dd>
</dl>

###class ir.BasicBlock
####Methods
<dl>
  <dt><code>append_inst(inst)</code></dt>
  <dd>Insert instruction <code>inst</code> at the end of the basic block.</dd>

  <dt><code>destroy()</code></dt>
  <dd><p>
  Destroy this basic block.
  </p><p>
  This removes the basic block from the function (if it is attached to a function), and destroys all instructions used in the basic block.
  </p><p>
  The basic block must not be used after it is destroyed.
  </p></dd>

  <dt><code>dump(stream=sys.stdout)</code></dt>
  <dd><p>Write a debug dump of the module to stream.
  </p><p>
  The format of the dump is similar to the high level assembly syntax used by <code>read_il</code> and <code>write_il</code>.
  </p></dd>

  <dt><code>get_successors()</code></dt>
  <dd>Return list of successor basic blocks.</dd>

  <dt><code>insert_inst_after(inst, insert_pos_inst)</code></dt>
  <dd>Insert instruction <code>inst</code> after the instruction <code>insert_pos_inst</code>.</dd>

  <dt><code>insert_inst_before(inst, insert_pos_inst)</code></dt>
  <dd>Insert instruction <code>inst</code> before the instruction <code>insert_pos_inst</code>.</dd>

  <dt><code>predecessors()</code></dt>
  <dd><p>Return the predecessor basic blocks.
  </p><p>
  <b>Note</b>: The predecessors are returned in arbitrary order.
  </p></dd>

  <dt><code>prepend_inst(inst)</code></dt>
  <dd>Insert instruction <code>inst</code> at the top of the basic block.</dd>

  <dt><code>remove()</code></dt>
  <dd>Remove this basic block from function.</dd>

  <dt><code>remove_inst(inst)</code></dt>
  <dd>Remove instruction <code>inst</code> from the basic block.</dd>
</dl>

####Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code>function</code></dt>
  <dd>The function containing this basic block, or <code>None</code> if
  this basic block is not inserted into a function.</dd>

  <dt><code>inst</code></dt>
  <dd>The <code>OpLabel</code> instruction defining this basic block.</dd>

  <dt><code>insts</code></dt>
  <dd>The instructions in this basic block (not including the
  <code>OpLabel</code>)</dd>

  <dt><code>module</code></dt>
  <dd>The module this basic block is associated with.</dd>
</dl>

###class ir.Instruction
####Methods
<dl>
  <dt><code>clone()</code></dt>
  <dd><p>Return a copy of the instruction.
  </p><p>
  The new instruction is identical to this instruction, except that
  it has a new <code>result_id</code> (if the instruction type has a
  <code>result_id</code>), and the new instruction is not bound to
  any basic block.
  </p></dd>

  <dt><code>insert_after(insert_pos_inst)</code></dt>
  <dd>Insert this instruction after the instruction <code>insert_pos_inst</code>.</dd>

  <dt><code>insert_before(insert_pos_inst)</code></dt>
  <dd>Insert this instruction before the instruction <code>insert_pos_inst</code>.</dd>

  <dt><code>remove()</code></dt>
  <dd>Remove this instruction from its basic block.</dd>

  <dt><code>destroy()</code></dt>
  <dd><p>
  Destroy this instruction.
  </p><p>
  This removes the instruction from the basic block (if it is attached to a basic block), and destroys the ID representing this function (if its <code>result_id</code> is not <code>None</code>).
  </p><p>
  The instruction must not be used after it is destroyed.
  </p></dd>

  <dt><code>add_to_phi(variable_inst, parent_inst)</code></dt>
  <dd>Add a variable/parent to an <code>OpPhi</code> instruction.</dd>

  <dt><code>remove_from_phi(parent_id)</code></dt>
  <dd>Remove a parent (and corresponding variable) from an <code>OpPhi</code>
  instruction.</dd>

  <dt><code>uses()</code></dt>
  <dd><p>
  Return all instructions using this instruction.
  </p><p>
  Debug and decoration instructions are not considered using
  any instruction.
  </p></dd>

  <dt><code>get_decorations()</code></dt>
  <dd>Return all decorations for this instruction.</dd>

  <dt><code>replace_uses_with(new_inst)</code></dt>
  <dd><p>
  Replace all uses of this instruction with <code>new_inst</code>.
  </p><p>
  Decoration and debug instructions are not updated, as they are
  considered being a part of the instruction they reference.
  </p></dd>

  <dt><code>replace_with(new_inst)</code></dt>
  <dd><p>
  Replace this instruction with <code>new_inst</code>.
  </p><p>
  All uses of this instruction is replaced by <code>new_inst</code>, the
  <code>new_inst</code> is inserted in the location of this instruction,
  and this instruction is destroyed.
  </p><p>
  Decoration and debug instructions are not updated, as they are
  considered being a part of the instruction they reference.
  </p></dd>

  <dt><code>has_side_effects()</code></dt>
  <dd>Return <code>True</code> if the instruction may have side effects (and
  thus cannot be removed if its result is not used), <code>False</code>
  otherwise.</dd>

  <dt><code>is_commutative()</code></dt>
  <dd>Return <code>True</code> if the instruction is commutative,
  <code>False</code> otherwise.</dd>

  <dt><code>is_global_inst()</code></dt>
  <dd>Return <code>True</code> if this is a global instruction,
  <code>False</code> otherwise.</dd>

  <dt><code>copy_decorations(src_inst)</code></dt>
  <dd>Copy the decorations from <code>src_inst</code> to this instruction.</dd>
</dl>

####Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code>module</code></dt>
  <dd>The module this instruction is associated with.</dd>

  <dt><code>op_name</code></dt>
  <dd>The operation name for this instruction.</dd>

  <dt><code>result_id</code></dt>
  <dd>The ID for the instructions return value. <code>None</code> if the
  instruction does not return a value.</dd>

  <dt><code>type_id</code></dt>
  <dd>The ID for the instructions type. <code>None</code> if the
  instruction does not have a type.</dd>

  <dt><code>operands</code></dt>
  <dd>A list containing the instruction's operands. ID operands are represented
  as <code>class Id</code> objects. Operands for enumerated constants (such as
  the Storage Class) are represented as strings of the values (such as
  <code>'Input'</code>). Literal strings and integers are represented as
  strings and integers.
  </dd>

  <dt><code>basic_block</code></dt>
  <dd>The basic block containing this instruction, or <code>None</code> if
  this instruction is not inserted into a basic block.</dd>
</dl>

###class ir.Id
####Methods
<dl>
  <dt><code>destroy()</code></dt>
  <dd><p>
  Destroy this ID.
  </p><p>
  The ID must not be used after it is destroyed.
  </p></dd>
</dl>

####Attributes
<b>Note</b>: The following attributes are read-only.
<dl>
  <dt><code>inst</code></dt>
  <dd>The instruction which has this ID as <code>result_id</code>, or
  <code>None</code></dd> if there are no such instruction.</dd>

  <dt><code>is_temp</code></dt>
  <dd><code>True</code> if this is a temporary ID (i.e. an ID that has not
  got a real value yet), <code>False</code> otherwise.</dd>

  <dt><code>uses</code></dt>
  <dd>A set containing all instructions in the module that are using this ID
  (excluding the instruction in <code>inst</code>). Only instructions tha
  thave been inserted into the module are included in the set (i.e. removing
  an instruction from a basic block will get it removed from the
  <code>uses</code> set too).</dd>

  <dt><code>value</code></dt>
  <dd>The ID's value.</dd>
</dl>

###class ir._GlobalInstructions
####Methods
<dl>
  <dt><code>TODO</code></dt>
  <dd><b>TODO</b></dd>

</dl>

####Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code></code></dt>
  <dd></dd>
</dl>
**TODO**

## Input/Output
TBD

## Optimizations
TBD
