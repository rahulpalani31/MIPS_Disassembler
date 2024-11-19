import sys
import re


def main():
    if len(sys.argv) != 2:
        print("Usage: python myDisassembler.py <input_file.obj>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not input_file.endswith('.obj'):
        print("Incorrect input file type (must be .obj file)")
        sys.exit(1)

    output_file = input_file[:-4] + '.s'

    disassembler = MIPSDisassembler()
    disassembler.read_input_file(input_file)
    disassembler.find_branches()
    output = disassembler.disassemble()
    disassembler.write_output_file(output_file, output)

class MIPSDisassembler:
    def __init__(self):

        self.instructions = []      # List to store all instructions
        self.labels = set()         # Set to store addresses
        self.current_address = 0    # Current address

        # Register name mapping
        self.register_names = {
            0: "$zero", 1: "$at", 2: "$v0", 3: "$v1", 4: "$a0", 5: "$a1", 6: "$a2", 7: "$a3",
            8: "$t0", 9: "$t1", 10: "$t2", 11: "$t3", 12: "$t4", 13: "$t5", 14: "$t6", 15: "$t7",
            16: "$s0", 17: "$s1", 18: "$s2", 19: "$s3", 20: "$s4", 21: "$s5", 22: "$s6", 23: "$s7",
            24: "$t8", 25: "$t9", 26: "$k0", 27: "$k1", 28: "$gp", 29: "$sp", 30: "$fp", 31: "$ra"
        }

        # R-type instruction mapping
        self.r_type_map = {
            0b100000: "add", 0b100001: "addu", 0b100100: "and", 0b100111: "nor",
            0b100101: "or", 0b101010: "slt", 0b101011: "sltu", 0b000000: "sll",
            0b000010: "srl", 0b100010: "sub", 0b100011: "subu"
        }

        # I-type instruction mapping
        self.i_type_map = {
            0b001000: "addi", 0b001001: "addiu", 0b001100: "andi", 0b000100: "beq",
            0b000101: "bne", 0b100100: "lbu", 0b100101: "lhu", 0b110000: "ll",
            0b001111: "lui", 0b100011: "lw", 0b001101: "ori", 0b001010: "slti",
            0b001011: "sltiu", 0b101000: "sb", 0b111000: "sc", 0b101001: "sh",
            0b101011: "sw"
        }

    # Reads input file and checks to ensure each line contains only 8 hex digits
    def read_input_file(self, filename):
        with open(filename, 'r') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()

                # Check if the line contains exactly 8 hex digits
                if not re.match(r'^[0-9A-Fa-f]{8}$', line):
                    print(f"Cannot disassemble {line} at line {line_number}")
                    sys.exit(1)

                # Convert the hexadecimal string to an integer and store it
                self.instructions.append(int(line, 16))

    # First parse of instructions: Identifies branch targets from instructions
    def find_branches(self):
        for i, instruction in enumerate(self.instructions):
            opcode = instruction >> 26

            if opcode == 0x4 or opcode == 0x5:  # beq or bne
                imm = instruction & 0xFFFF

                if imm & 0x8000:
                    imm -= 0x10000

                target_address = (i + 1 + imm) * 4
                self.labels.add(target_address)

    # Disassembles a singular MIPS instructions & returns assembly representation
    def disassemble_instruction(self, instruction, address):
        # Extract elements of the instruction
        opcode = instruction >> 26
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        shamt = (instruction >> 6) & 0x1F
        funct = instruction & 0x3F
        imm = instruction & 0xFFFF

        # Sign-extend the immediate value
        if imm & 0x8000:
            imm -= 0x10000

        if opcode == 0:  # R-type
            if funct in self.r_type_map:
                if self.r_type_map[funct] in ["sll", "srl"]:
                    return f"{self.r_type_map[funct]} {self.register_names[rd]}, {self.register_names[rt]}, {shamt}"
                else:
                    return f"{self.r_type_map[funct]} {self.register_names[rd]}, {self.register_names[rs]}, {self.register_names[rt]}"
            else:
                return f"Cannot disassemble {instruction:08x} at address {address:04x}"

        elif opcode in self.i_type_map:
            if self.i_type_map[opcode] in ["beq", "bne"]:
                target_address = (address + 4 + (imm << 2)) & 0xFFFF
                return f"{self.i_type_map[opcode]} {self.register_names[rs]}, {self.register_names[rt]}, Addr_{target_address:04x}"
            elif self.i_type_map[opcode] in ["lw", "sw", "lbu", "lhu", "ll", "sb", "sc", "sh"]:
                return f"{self.i_type_map[opcode]} {self.register_names[rt]}, {imm}({self.register_names[rs]})"
            elif self.i_type_map[opcode] == "lui":
                return f"{self.i_type_map[opcode]} {self.register_names[rt]}, {imm}"
            else:
                return f"{self.i_type_map[opcode]} {self.register_names[rt]}, {self.register_names[rs]}, {imm}"

        else:
            return f"Cannot disassemble {instruction:08x} at address {address:04x}"

    # Second parse of instructions: Generates disassembled output
    def disassemble(self):
        output = []

        for i, instruction in enumerate(self.instructions):
            address = i * 4

            # If  address is a branch target -> add a label
            if address in self.labels:
                output.append(f"Addr_{address:04x}:")

            # Disassemble instruction and add it to output
            disassembled = self.disassemble_instruction(instruction, address)
            output.append(disassembled)

        return output

    # Writes instructions to output file
    def write_output_file(self, filename, output):
        with open(filename, 'w') as f:
            for line in output:
                f.write(line + '\n')

if __name__ == "__main__":
    main()