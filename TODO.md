##Code cleanup
The current code is partly an explorational implementation to determine what kind of functionality I need in the IR (both for the assembler/disassembler, and for some other tools I'm working on), and partly an attempt to learn python. As such, there are many parts of the code that I know are bad. For example, the IR has 15 lists/dictionaries that contains overlapping information and are often out of synch. And the code has several functions that tries to iterate over instructions instead of using a centralized iterator.

The work package here is to
* Design a real representation for the IR.
* Implement functionality for iterating over, and manipulating, the IR.
* Update the implementation to use the new infrastructure.
* Add tests for everything before each functionality is implemented.

##Bugs and Limitations
Known bugs and limitations include:
* Bitmasks are always written as a number
* Structure/arrays/matrices/etc. are not pretty-printed
* Constants are written as separate instructions
* `OpExtInst` is not pretty-printed
* `FunctionControl` is not handled in pretty-printed functions
* Debug information is not used for naming local variables/function arguments
* The CFG is not updated
* Disassembling with the `-r` option and assembling the result may give a binary that differs from the original (as e.g. debug instructions may be output in a different order)
* The `OptionalId` of `OpVariable` is not handled in pretty-printed mode

But there are surely more bugs and limitations – much of the code is untested...

##Syntax
Some things are missing or should be changed
* `@` should not be used for function names – `%` works just fine
* Hex/binary constants should be supported
* Negative constants should be supported

There are open questions about the best formatting of some constructs. For example
* Should the operation names be changed to be shorter? E.g. most instructions in ESSL shaders have a `PrecisionMedium` decoration, and it would be nice to have a short name for it. (But I still think that SPIR-V [should change how the ESSL precision modifiers are handled](http://kristerw.blogspot.se/2015/04/precision-qualifiers-in-spir-v.html)...) 
* Pointers are important for OpenCL. How to pretty-print them in a compact form without losing address space information?
* Should `OpLoopMerge` be written as modifier to `OpBranchConditional` (and similar for the other “merge” instructions)?
* Should `@` be used for global symbols? It is not really needed, but parsing is slightly more annoying without it. And the `@` makes the global variables more visible.
