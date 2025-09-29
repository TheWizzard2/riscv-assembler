# RISC-V Instruction Assembler

This project is a simple assembler for a subset of **RISC-V instructions**, supporting both **base instructions** and **pseudo-instructions** (aliases that expand into one or more base instructions).

## ✨ Features

- Supports **R-type, I-type, S-type, B-type, U-type, and J-type** instructions.  
- The use of pseudo-instructions is currently in **develop**, only works with base instructions.
- Generates 32-bit **machine code** in binary and hexadecimal formats.  
- Provides an **instruction lookup table** (`instr_table.json`) that can be easily extended.  

---

## 📖 Instruction Table

The assembler uses a JSON-based **instruction table**.  
Each entry defines either a **base instruction** or a **pseudo-instruction**.

### Base instruction example
```json
{
  "mnemonic": "sub",
  "format": "R",
  "opcode": "0110011",
  "funct3": "000",
  "funct7": "0100000",
  "operand_order": ["rd", "rs1", "rs2"],
  "aliases": ["neg"]
}
```
## Usage

1. Open a terminal shell.

2. Run the following command.
```shell
    python assembler.py program.asm program.hex program.bin
```

3. Explanation:
    - assembler.py is the main program
    - program.asm name of the Assembler program written in RISCV
    - program.hex and program.bin the name of the two output files with encode results.

### Workteam
Worked by:
- Miguel Angel Soto Grajales
- Illian Felipe Osorio