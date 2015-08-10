##Bugs and Limitations
Known bugs and limitations in the API include:
* The CFG is not updated when adding basic blocks
* Phi-nodes are not handled correctly
* Need a `mem2reg` pass
* Representation of literals need to change (they are currently represented as strings)
* `Module.get_constant()` need to handle more types. At least Booleans, NULL pointers, etc. But probably "all" constants.
* Need an API similar to 'Module.get_constant()' for creating types
* The implementation is _very_ inefficient. Need to be able to get instruction uses etc. without iterating over the module

Known bugs and limitations in the assembler/disassembler include:
* The assembler syntax is mostly undocumented
* `OpConstant` does only handle 32-bit constants correctly.
* Bitmasks are always written as a number
* Structure/arrays/matrices/etc. are not pretty-printed
* Constants are written as separate instructions
* `OpExtInst` is not pretty-printed
* `FunctionControl` is not handled in pretty-printed functions
* Debug information is not used for naming local variables/function arguments
* The CFG is not updated
* The `OptionalId` of `OpVariable` is not handled in pretty-printed mode
* The assembler should check that the number of operands are correct for variable length operand list (e.g. `OpBranchContitional` must have 0 or 2 branch weights).

##Assembler syntax
Some things are missing or should be changed
* Hex/binary constants should be supported
* Negative constants should be supported

There are open questions about the best formatting of some constructs. For example
* Should the operation names be changed to be shorter? E.g. most instructions in ESSL shaders have a `PrecisionMedium` decoration, and it would be nice to have a short name for it. (But I still think that SPIR-V [should change how the ESSL precision modifiers are handled](http://kristerw.blogspot.se/2015/04/precision-qualifiers-in-spir-v.html)...) 
* Pointers are important for OpenCL. How to pretty-print them in a compact form without losing address space information?
* Should `OpLoopMerge` be written as modifier to `OpBranchConditional` (and similar for the other “merge” instructions)?
