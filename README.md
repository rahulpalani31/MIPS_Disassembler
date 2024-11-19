# MIPS Disassembler

A simple Python-based MIPS disassembler that converts hexadecimal `.obj` files into human-readable assembly `.s` files.

## Features

- **R-type and I-type Instruction Support**: Handles a variety of MIPS instructions including arithmetic, logic, memory access, and branch operations.
- **Branch Target Identification**: Automatically detects and labels branch targets for easier code navigation.
- **Register Mapping**: Converts register numbers to their corresponding MIPS register names.
- **Error Handling**: Validates input file format and instruction integrity, providing informative error messages.

## Requirements

- Python 3.x

## Usage

1. **Prepare the Input File**: Ensure you have a `.obj` file containing MIPS instructions in hexadecimal format, one instruction per line.

2. **Run the Disassembler**:

   ```bash
   python myDisassembler.py <input_file.obj>

## Example

Given an input file `example.obj` with the following content:

```bash
012A4020 8D0B0004
```

Produces `example.s`:


```bash
add $t0, $t1, $t2
lw $t3, 4($t0)
```
