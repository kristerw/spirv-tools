# spirv-tools
This module implements an [API](doc/API_reference.md) for creating and manipulating SPIR-V binaries, and uses the API for a high-level assembler/disassembler.

The assembler syntax is not finalized yet, but the format used by the initial implementation is described in my [blog](http://kristerw.blogspot.se/2015/05/human-friendly-spir-v-textual.html). See the [TODO](TODO.md) file for a list of the issues/limitations in the current implementation.

Usage:
```
spirv-as [-O] file.il
spirv-dis [-r] [-O] file.spv
```
