##API Overview
This API is meant to be used for basic analysis and manipulation of SPIR-V
binaries, and it tries to keep its representation close to the real binary;
the IR consists of the SPIR-V instructions, and iterators traverse the IR
in the order they are stored in the binary. But there is one layer of
abstraction on top of this to represent functions and basic blocks, in
order to simplify implementation of analysis and transformation passes.

The IR is encapsulated in a `Module` object. This consists of a list of global
instructions and a list of functions. The `Function` class represents
one function, that is, all instructions from an `OpFunction` to the
`OpFunctionEnd`. The instructions are grouped in the `BasicBlock` class,
which consists of all instructions from an `OpLabel` to the branch or return
instruction. Finally the instructions are represented by the `Instruction`
class, where the SPIR-V IDs are represented by the `Id` class.

Most class attributes (such as lists of functions, basic blocks,
instructions) are meant to be used by applications, but applications must
not modify the information directly. Instead, the objects have methods
for updating the data. The reason for this is so the IR implementation
may update data structures keeping track of various information in order to
make the API more efficient, or for validity checking.

The `Instruction` object consists of the result ID, opcode name, type ID, and
operands. The fields are mostly represented in the same form as in the
high level assembly language used by the `spirv-as`/`spirv-dis`; the IDs
are represented as objects of the `Id` class that contains the value of the ID
and a link to the instruction that defines the ID. An application should in general
never create ID values itself; the only exception is when implementing an assembler.
All other IDs should be created implicitly by creating the instructions without
providing an ID. The opcode is represented by
the operation name (such as `'OpFAdd'`). The operands for the enumerated constants (such as
the Storage Class) are represented as strings of the values (such as
`'Input'`), and masks are represented as a list of enumerated constants.
Integer and string literals are represented as integers and strings.

The `result_id` and `type_id` values are `None` for operations not using
them, and `operands` is an empty list for instructions without operands.

Instructions are immutable, so it is not possible to modify an instruction
after it is created. The way of modifying instructions is to create a new
(nearly) identical instruction, and to substitute the original with the new.
For example, to switch the order of two operands of `inst`:

```
new_inst = ir.Instruction(module, inst.op_name, inst.type_id,
                          [inst.operands[1], inst.operands[0]])
inst.replace_with(new_inst)
```

This changes the ID of the instruction, and it may be argued that
it is useful to modify one instruction (i.e. to keep the
original ID) in order to make minimal change in the binary. This
is not directly supported in the API, but it can be accomplished
by inserting a temporary instruction

```
tmp_inst = ir.Instruction(module, 'OpUndef', inst.type_id, [])
tmp_inst.insert_after(inst)
inst.replace_uses_with(tmp_inst)
new_inst = ir.Instruction(module, inst.op_name, inst.type_id,
                          [inst.operands[1], inst.operands[0]],
                          result_id=inst.result_id)
tmp_inst.replace_with(new_inst)
inst.destroy()
```

It is possible to iterate
over all instructions in the module by `module.instructions()`. The
instructions are retrieved in the same order as in the binary. It is
allowed to modify the IR while iterating over the instructions, but
instruction added to the current basic block will not be seen by the
iterator. Instructions that are moved (i.e. removed and re-inserted)
in the current basic block may be returned as if it was in its old
position.

**TBD** - Decorations, debug instructions etc.

**TBD** - Global instructions

**TBD** - Functions and basic blocks

## IR
###class ir.Module
####ir.Module – Methods
<dl>
  <dt><code>append_function(function)</code></dt>
  <dd>Insert function at the end of the module.</dd>

  <dt><code>dump(stream=sys.stdout)</code></dt>
  <dd><p>
  Write a debug dump of the module to <code>stream</code>.
  </p><p>
  The format of the dump is similar to the high level assembly syntax used by <code>read_il</code> and <code>write_il</code>.
  </p></dd>

  <dt><code>get_constant()</code></dt>
  <dd><p>
  Return a constant instruction with the provided value and type. An existing
  instruction is returned if it exists, otherwise a newly created instruction
  is returned and inserted into the module.
  </p><p>
  For vector types, the value need to be a list of the same length
  as the vector size, or a scalar, in which case the value is
  replicated for all elements.
  </p><p>
  For matrix types, the value need to be a list of the same length
  as the column count (where each element is a list of the column with
  or a scalar), or a scalar, in which case the value is replicated for
  all elements.
  </p><p>
  Floating point values can be provided as either a floating point
  number (such as. <code>1.0</code>), or as an integer representing
  the bits of the value (such as <code>0x3f800000</code>).
  </p></dd>

  <dt><code>get_global_inst(op_name, type_id, operands)</code></dt>
  <dd><p>
  Return a global instruction corresponding to the <code>op_name</code>,
  <code>type_id</code>, and <code>operations</code>. An existing instruction
  is returned if it exists, otherwise a newly created instruction is returned
  and inserted into the module.
  </p><p>
  This method is the preferred way of creating global instructions. For
  example, creating a type instruction for a 32-bit signed integer is done as
  <code>get_global_inst('OpTypeInt', 32, 1)</code>
  </p></dd>

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
  Iterator for iterating over the module's instructions in the order they are
  located in the SPIR-V binary.
  </p><p>
  It is allowed to insert or remove instructions while iterating, although
  instructions inserted during iteration are not guaranteed to be seen during
  the iteration.
  </p><p>
  It is not allowed to insert/remove basic blocks or functions while iterating
  over the instructions.
  </p></dd>

  <dt><code>instructions_reversed()</code></dt>
  <dd><p>
  Iterator for iterating over the module's instructions in reverse order.
  </p><p>
  It is allowed to insert or remove instructions while iterating, although
  instructions inserted during iteration are not guaranteed to be seen during
  the iteration.
  </p><p>
  It is not allowed to insert/remove basic blocks or functions while iterating
  over the instructions.
  </p></dd>

  <dt><code>prepend_function(function)</code></dt>
  <dd>Insert function at the top of the module.</dd>

  <dt><code>renumber_temp_ids()</code></dt>
  <dd>Convert temp IDs to real IDs.</dd>
</dl>

####ir.Module – Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code>bound</code></dt>
  <dd>The SPIR-V ID bound.</dd>

  <dt><code>global_instructions</code></dt>
  <dd>The pseudo-basic block of class <code>_GlobalInstructions</code>
  containing the module's global instructions.</dd>

  <dt><code>functions</code></dt>
  <dd>A list of the functions in this module.</dd>
</dl>

###class ir.Function
####ir.Function – Methods
<dl>
  <dt><code>append_basic_block(basic_block)</code></dt>
  <dd>Insert basic block <code>basic_block</code> at the end of the
  function.</dd>

  <dt><code>append_parameter(inst)</code></dt>
  <dd>Insert the <code>OpFunctionParameter</code> instruction <code>inst</code>
  at the end of the function's parameter list.</dd>

  <dt><code>destroy()</code></dt>
  <dd><p>
  Destroy this function.
  </p><p>
  This removes the function from the module (if it is attached to a module),
  and destroys the function's basic blocks and instructions.
  </p><p>
  The function must not be used after it is destroyed.
  </p></dd>

  <dt><code>dump(stream=sys.stdout)</code></dt>
  <dd><p>Write a debug dump of the function to <code>stream</code>.
  </p><p>
  The format of the dump is similar to the high level assembly syntax used by
  <code>read_il</code> and <code>write_il</code>.
  </p></dd>

  <dt><code>insert_basic_block_after(basic_block, insert_pos_basic_block)</code></dt>
  <dd>Insert basic block <code>basic_block</code> after the basic block
  <code>insert_pos_basic_block</code>.</dd>

  <dt><code>insert_basic_block_before(basic_block, insert_pos_basic_block)</code></dt>
  <dd>Insert basic block <code>basic_block</code> before the basic block
  <code>insert_pos_basic_block</code>.</dd>

  <dt><code>instructions()</code></dt>
  <dd><p>
  Iterator for iterating over the function's instructions in the order they
  are located in the SPIR-V binary.
  </p><p>
  It is allowed to insert or remove instructions while iterating, although
  instructions inserted during iteration are not guaranteed to be seen during
  the iteration.
  </p><p>
  It is not allowed to insert/remove basic blocks while iterating over the
  instructions.
  </p></dd>

  <dt><code>instructions_reversed()</code></dt>
  <dd><p>
  Iterator for iterating over the function's instructions in reverse order.
  </p><p>
  It is allowed to insert or remove instructions while iterating, although
  instructions inserted during iteration are not guaranteed to be seen during
  the iteration.
  </p><p>
  It is not allowed to insert/remove basic blocks while iterating over the
  instructions.
  </p></dd>

  <dt><code>prepend_basic_block(basic_block)</code></dt>
  <dd>Insert basic block <code>basic_block</code> at the top of the
  function.</dd>

  <dt><code>remove()</code></dt>
  <dd>Remove this function from the module.</dd>
</dl>

####ir.Function – Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code>parameters</code></dt>
  <dd>A list of the <code>OpFunctionParameter</code> instructions for
  the function's parameters.</dd>

  <dt><code>basic_blocks</code></dt>
  <dd>A list of the basic blocks within this function.</dd>

  <dt><code>inst</code></dt>
  <dd>The <code>OpFunction</code> instruction defining this function.</dd>

  <dt><code>end_inst</code></dt>
  <dd>The <code>OpFunctionEnd</code> instruction ending this function.</dd>

  <dt><code>module</code></dt>
  <dd>The module this function is associated with.</dd>
</dl>

###class ir.BasicBlock
####ir.BasicBlock – Methods
<dl>
  <dt><code>append_inst(inst)</code></dt>
  <dd>Insert instruction <code>inst</code> at the end of the basic block.</dd>

  <dt><code>destroy()</code></dt>
  <dd><p>
  Destroy this basic block.
  </p><p>
  This removes the basic block from the function (if it is attached to a function), and destroys all the basic block's instructions.
  </p><p>
  The basic block must not be used after it is destroyed.
  </p></dd>

  <dt><code>dump(stream=sys.stdout)</code></dt>
  <dd><p>Write a debug dump of the basic block to <code>stream</code>.
  </p><p>
  The format of the dump is similar to the high level assembly syntax used by
  <code>read_il</code> and <code>write_il</code>.
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

  <dt><code>insert_after(insert_pos_bb)</code></dt>
  <dd>Insert this basic block after the basic block <code>insert_pos_bb</code>.</dd>

  <dt><code>insert_before(insert_pos_bb)</code></dt>
  <dd>Insert this basic block before the basic block <code>insert_pos_bb</code>.</dd>

  <dt><code>remove()</code></dt>
  <dd>Remove this basic block from function.</dd>

  <dt><code>remove_inst(inst)</code></dt>
  <dd>Remove instruction <code>inst</code> from the basic block.</dd>
</dl>

####ir.BasicBlock – Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code>function</code></dt>
  <dd>The function containing this basic block, or <code>None</code> if
  this basic block is not inserted into a function.</dd>

  <dt><code>inst</code></dt>
  <dd>The <code>OpLabel</code> instruction defining this basic block.</dd>

  <dt><code>insts</code></dt>
  <dd>The instructions in this basic block (not including the
  <code>OpLabel</code> instruction).</dd>

  <dt><code>module</code></dt>
  <dd>The module this basic block is associated with.</dd>
</dl>

###class ir.Instruction
####ir.Instruction – Methods
<dl>
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
  This removes the instruction from the basic block (if it is in a basic
  block).
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
  Debug and decoration instructions are not returned.
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
  <dd>Return <code>True</code> if the instruction may have side effects,
  <code>False</code> otherwise.</dd>

  <dt><code>is_commutative()</code></dt>
  <dd>Return <code>True</code> if the instruction is commutative,
  <code>False</code> otherwise.</dd>

  <dt><code>is_constant_value(value)</code></dt>
  <dd><p>
  Return <code>True</code> if this instruction is a
  constant with the value <code>value</code>, <code>False</code> otherwise.
  </p><p>
  For vector types, the value need to be a list of the same length
  as the vector size, or a scalar, in which case the value is
  replicated for all elements.
  </p><p>
  For matrix types, the value need to be a list of the same length
  as the column count (where each element is a list of the column with
  or a scalar), or a scalar, in which case the value is replicated for
  all elements.
  </p><p>
  Floating point values can be provided as either a floating point
  number (such as. <code>1.0</code>), or as an integer representing
  the bits of the value (such as <code>0x3f800000</code>).
  </p></dd>

  <dt><code>is_global_inst()</code></dt>
  <dd>Return <code>True</code> if this is a global instruction,
  <code>False</code> otherwise.</dd>

  <dt><code>copy_decorations(src_inst)</code></dt>
  <dd>Copy the decorations from <code>src_inst</code> to this instruction.</dd>
</dl>

####ir.Instruction – Attributes
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

  <dt><code>function</code></dt>
  <dd>The function containing this instruction, or <code>None</code> if
  this instruction is not inserted into a function.</dd>
</dl>

###class ir.Id
####ir.Id – Methods
<dl>
  <dt><code>destroy()</code></dt>
  <dd><p>
  Destroy this ID.
  </p><p>
  The ID must not be used after it is destroyed.
  </p></dd>
</dl>

####ir.Id – Attributes
<b>Note</b>: The following attributes are read-only.
<dl>
  <dt><code>inst</code></dt>
  <dd>The instruction which has this ID as <code>result_id</code>, or
  <code>None</code> if there is no such instruction.</dd>

  <dt><code>is_temp</code></dt>
  <dd><code>True</code> if this is a temporary ID (i.e. an ID that has not
  got a real value yet), <code>False</code> otherwise.</dd>

  <dt><code>uses</code></dt>
  <dd>A set containing all instructions in the module that are using this ID
  (excluding the instruction in <code>inst</code>). Only instructions that
  have been inserted into the module are included in the set (i.e. removing
  an instruction from a basic block will get it removed from the
  <code>uses</code> set too).</dd>

  <dt><code>value</code></dt>
  <dd><p>
  The ID's value.
  </p><p>
  Temporary IDs have a value outside of the valid range.
  </p></dd>
</dl>

###class ir._GlobalInstructions
####ir._GlobalInstructions – Methods
<dl>
  <dt><code>dump(stream=sys.stdout)</code></dt>
  <dd><p>Write a debug dump of the global instructions to <code>stream</code>.
  </p><p>
  The format of the dump is similar to the high level assembly syntax used by
  <code>read_il</code> and <code>write_il</code>.
  </p></dd>

  <dt><code>instructions()</code></dt>
  <dd><p>
  Iterator for iterating over the global instructions in the order they are
  located in the SPIR-V binary.
  </p><p>
  It is allowed to insert or remove instructions while iterating, although
  instructions inserted during iteration are not guaranteed to be seen during
  the iteration.
  </p></dd>

  <dt><code>instructions_reversed()</code></dt>
  <dd><p>
  Iterator for iterating over the global instructions in reverse order.
  </p><p>
  It is allowed to insert or remove instructions while iterating, although
  instructions inserted during iteration are not guaranteed to be seen during
  the iteration.
  </p></dd>

  <dt><code>get_inst(op_name, type_id, operands)</code></dt>
  <dd>
  Return a global instruction corresponding to the <code>op_name</code>,
  <code>type_id</code>, and <code>operations</code>. An existing instruction
  is returned if it exists, otherwise a newly created instruction is returned
  and inserted into the module.
  </dd>

  <dt><code>append_inst(inst)</code></dt>
  <dd>Insert instruction <code>inst</code> at the end of its section among
  the global instructions.</dd>

  <dt><code>prepend_inst(inst)</code></dt>
  <dd>Insert instruction <code>inst</code> at the top of its section among
  the global instructions.</dd>

  <dt><code>insert_inst_after(inst, insert_pos_inst)</code></dt>
  <dd><p>Insert instruction <code>inst</code> after the instruction
  <code>insert_pos_inst</code>.
  </p><p>
  The instruction is inserted at the first valid position among the global
  instructions.
  </p></dd>

  <dt><code>insert_inst_before(inst, insert_pos_inst)</code></dt>
  <dd><p>Insert instruction <code>inst</code> before the instruction
  <code>insert_pos_inst</code>.
  </p><p>
  The instruction is inserted at the first valid position among the global
  instructions.
  </p></dd>

  <dt><code>remove_inst(inst)</code></dt>
  <dd>Remove instruction <code>inst</code> from the global instructions.</dd>
</dl>

####ir._GlobalInstructions – Attributes
**Note**: The following attributes are read-only.
<dl>
  <dt><code>decoration_insts</code></dt>
  <dd>A list containing the decoration instructions.</dd>

  <dt><code>name_insts</code></dt>
  <dd>A list containing the <code>OpName</code> and <code>OpMemberName</code>
  instructions.</dd>

  <dt><code>op_capability_insts</code></dt>
  <dd>A list containing the <code>OpCapability</code> instructions.</dd>

  <dt><code>op_entry_point_insts</code></dt>
  <dd>A list containing the <code>OpEntryPoint</code> instructions.</dd>

  <dt><code>op_execution_mode_insts</code></dt>
  <dd>A list containing the <code>OpExecutionMode</code> instructions.</dd>

  <dt><code>op_extension_insts</code></dt>
  <dd>A list containing the <code>OpExtension</code> instructions.</dd>

  <dt><code>op_extinstimport_insts</code></dt>
  <dd>A list containing the <code>OpExtInstImport</code> instructions.</dd>

  <dt><code>op_line_insts</code></dt>
  <dd>A list containing the <code>OpLine</code> instructions.</dd>

  <dt><code>op_memory_model_insts</code></dt>
  <dd>A list containing the <code>OpMemoryModel</code> instructions.</dd>

  <dt><code>op_string_insts</code></dt>
  <dd>A list containing the <code>OpString</code> instructions.</dd>

  <dt><code>op_source_extension_insts</code></dt>
  <dd>A list containing the <code>OpSourceExtension</code> instructions.</dd>

  <dt><code>op_source_insts</code></dt>
  <dd>A list containing the <code>OpSource</code> instructions.</dd>

  <dt><code>type_insts</code></dt>
  <dd>A list containing the type declaration, constant, spec-constant, and
  global <code>OpVariable</code> instructions.</dd>
</dl>

## Input/Output
**TBD**: `read_il`, `write_il`, `read_spirv`, `write_spirv`.

## Optimizations
**TBD**: `instcombine`, `simplify_cfg`, `dead_inst_elim`, `dead_func_elim`,
`mem2reg`.
