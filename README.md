# spirv-tools
A high-level assembler/disassembler for SPIR-V.

The assembler syntax is not finalized yet, but the format used by the initial implementation is described in my [blog](http://kristerw.blogspot.se/2015/05/human-friendly-spir-v-textual.html). See the [TODO](TODO.md) file for a list of the issues/limitations in the current implementation.

Usage:
```
spirv-as file.il
spirv-dis [-r] file.spv
```
