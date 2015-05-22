##Code cleanup
The current code is partly an explorational implementation to determine what kind of functionality I need in the IR (both for the assembler/disassembler, and for some other tools I'm working on), and partly an attempt to learn python. As such, there are many parts of the code that I know are bad. For example, the IR has 15 lists/dictionaries that contains overlapping information and are often out of synch. And the code has several functions that tries to iterate over instructions instead of using a centralized iterator.

The work package here is to
* Design a real representation for the IR.
* Implement functionality for iterating over, and manipulating, the IR.
* Update the implementation to use the new infrastructure.
* Add tests for everything before each functionality is implemented.

##Bugs and Limitations
Known bugs and limitations include:
* Type instructions are not always written in the pretty-printed output
* Bitmasks are always written as a number
* Decorations are only implemented for global variables
* Structure/arrays/matrices/etc. are not pretty-printed
* Constants are written as separate instructions
* `OpExtInst` is not pretty-printed
* `FunctionControl` is not handled in pretty-printed functions
* Debug information is not used for naming local variables/function arguments
* The CFG is not updated
* Disassembling with the `-r` option and assembling the result may give a binary that differs from the original (as e.g. debug instructions may be output in a different order)

But there are surely more bugs and limitations – much of the code is untested...

##Syntax
There are open questions about how to best formatting some constructs. For example
* Should the operation names be changed to be shorter?
* Pointers are important for OpenCL. How to pretty-print them in a compact form without losing address space information?
* Should `OpLoopMerge` be written as modifier to `OpBranchConditional` (and similar for the other “merge” instructions)?

 
