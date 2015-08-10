# spirv-tools
This module implements an [API](doc/API_reference.md) for creating and manipulating SPIR-V binaries (see my [blog post](http://kristerw.blogspot.se/2015/06/api-for-manipulating-and-optimizing.html) for examples), and uses the API for a high-level assembler/disassembler.

The assembler syntax is not finalized yet, but the format used by the initial implementation is described in a [blog post](http://kristerw.blogspot.se/2015/05/human-friendly-spir-v-textual.html).

Usage:
```
spirv-as [-O] file.il
spirv-dis [-r] [-O] file.spv
```

This module is very much "work in progress", altough I'm not working that actively on this as the specification is not done yet, and there are no implementations to interoperate with...  See the [TODO](TODO.md) file for a list of the issues/limitations in the current implementation.
