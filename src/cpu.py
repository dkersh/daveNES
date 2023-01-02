import numpy as np
from program import Program
from memory import Memory
from enum import Enum

class AddressingMode(Enum):
    IMMEDIATE = 1
    ZERO_PAGE = 2
    ZERO_PAGE_X = 3
    ZERO_PAGE_Y = 4
    ABSOLUTE = 5
    ABSOLUTE_X = 6
    ABSOLUTE_Y = 7
    INDIRECT = 8
    INDIRECT_X = 9
    INDIRECT_Y = 10
    IMPLICIT = 11
    ACCUMULATOR = 12
    RELATIVE = 13

class MOS6502:
    def __init__(self) -> None:
        # The Registers
        self.r_program_counter = np.uint16(0)
        self.r_stack_pointer = np.uint8(0)
        self.r_accumulator = np.uint8(0)
        self.r_index_X = np.uint8(0)
        self.r_index_Y = np.uint8(0)
        self.r_status = {
            'flag_C': False,
            'flag_Z': False,
            'flag_I': False,
            'flag_D': False,
            'flag_B': False,
            'flag_V': False,
            'flag_N': False
            }
        # self.r_status = np.uint8(0) # NV B*B* DIZC, B* == Break
        self.memory = None
        self.break_flag = False

        # TODO: Add number of cycles to each command.
        # hexcode: [function, addressing mode, number of cycles, string for reference]
        self.lookup_table = {
            0x69: [self.ADC, AddressingMode.IMMEDIATE, 'ADC'],
            0x65: [self.ADC, AddressingMode.ZERO_PAGE, 'ADC'],
            0x75: [self.ADC, AddressingMode.ZERO_PAGE_X, 'ADC'],
            0x6D: [self.ADC, AddressingMode.ABSOLUTE, 'ADC'],
            0x7D: [self.ADC, AddressingMode.ABSOLUTE_X, 'ADC'],
            0x79: [self.ADC, AddressingMode.ABSOLUTE_Y, 'ADC'],
            0x61: [self.ADC, AddressingMode.INDIRECT_X, 'ADC'],
            0x71: [self.ADC, AddressingMode.INDIRECT_Y, 'ADC'],

            0x29: [self.AND, AddressingMode.IMMEDIATE, 'AND'],
            0x25: [self.AND, AddressingMode.ZERO_PAGE, 'AND'],
            0x35: [self.AND, AddressingMode.ZERO_PAGE_X, 'AND'],
            0x2D: [self.AND, AddressingMode.ABSOLUTE, 'AND'],
            0x3D: [self.AND, AddressingMode.ABSOLUTE_X, 'AND'],
            0x39: [self.AND, AddressingMode.ABSOLUTE_Y, 'AND'],
            0x21: [self.AND, AddressingMode.INDIRECT_X, 'AND'],
            0x31: [self.AND, AddressingMode.INDIRECT_Y, 'AND'],

            0x0A: [self.ASL, AddressingMode.ACCUMULATOR, 'ASL'],
            0x06: [self.ASL, AddressingMode.ZERO_PAGE, 'ASL'],
            0x16: [self.ASL, AddressingMode.ZERO_PAGE_X, 'ASL'],
            0x0E: [self.ASL, AddressingMode.ABSOLUTE, 'ASL'],
            0x1E: [self.ASL, AddressingMode.ABSOLUTE_X, 'ASL'],

            0x90: [self.BCC, AddressingMode.RELATIVE, 'BCC'],

            0xB0: [self.BCS, AddressingMode.RELATIVE, 'BCS'],

            0xF0: [self.BEQ, AddressingMode.RELATIVE, 'BEQ'],

            0x24: [self.BIT, AddressingMode.ZERO_PAGE, 'BIT'],
            0x2C: [self.BIT, AddressingMode.ABSOLUTE, 'BIT'],

            0x30: [self.BMI, AddressingMode.RELATIVE, 'BMI'],

            0xD0: [self.BNE, AddressingMode.RELATIVE, 'BNE'],

            0x10: [self.BPL, AddressingMode.RELATIVE, 'BPL'],

            0x00: [self.BRK, None, 'BRK'],

            0x50: [self.BVC, AddressingMode.RELATIVE, 'BVC'],

            0x70: [self.BVS, AddressingMode.RELATIVE, 'BVS'],

            0x18: [self.CLC, None, 'CLC'],

            0xD8: [self.CLD, None, 'CLD'],

            0x58: [self.CLI, None, 'CLI'],

            0xB8: [self.CLV, None, 'CLV'],

            0xC9: [self.CMP, AddressingMode.IMMEDIATE, 'CMP'],
            0xC5: [self.CMP, AddressingMode.ZERO_PAGE, 'CMP'],
            0xD5: [self.CMP, AddressingMode.ZERO_PAGE_X, 'CMP'],
            0xCD: [self.CMP, AddressingMode.ABSOLUTE, 'CMP'],
            0xDD: [self.CMP, AddressingMode.ABSOLUTE_X, 'CMP'],
            0xD9: [self.CMP, AddressingMode.ABSOLUTE_Y, 'CMP'],
            0xC1: [self.CMP, AddressingMode.INDIRECT_X, 'CMP'],
            0xD1: [self.CMP, AddressingMode.INDIRECT_Y, 'CMP'],

            0xE0: [self.CPX, AddressingMode.IMMEDIATE, 'CPX'],
            0xE4: [self.CPX, AddressingMode.ZERO_PAGE, 'CPX'],
            0xEC: [self.CPX, AddressingMode.ABSOLUTE, 'CPX'],

            0xC0: [self.CPY, AddressingMode.IMMEDIATE, 'CPY'],
            0xC4: [self.CPY, AddressingMode.ZERO_PAGE, 'CPY'],
            0xCC: [self.CPY, AddressingMode.ABSOLUTE, 'CPY'],

            0xC6: [self.DEC, AddressingMode.ZERO_PAGE, 'DEC'],
            0xD6: [self.DEC, AddressingMode.ZERO_PAGE_X, 'DEC'],
            0xCE: [self.DEC, AddressingMode.ABSOLUTE, 'DEC'],
            0xDE: [self.DEC, AddressingMode.ABSOLUTE_X, 'DEC'],

            0xCA: [self.DEX, None, 'DEX'],
            0x88: [self.DEY, None, 'DEY'],

            0x49: [self.EOR, AddressingMode.IMMEDIATE, 'EOR'],
            0x45: [self.EOR, AddressingMode.ZERO_PAGE, 'EOR'],
            0x55: [self.EOR, AddressingMode.ZERO_PAGE_X, 'EOR'],
            0x4D: [self.EOR, AddressingMode.ABSOLUTE, 'EOR'],
            0x5D: [self.EOR, AddressingMode.ABSOLUTE_X, 'EOR'],
            0x59: [self.EOR, AddressingMode.ABSOLUTE_Y, 'EOR'],
            0x41: [self.EOR, AddressingMode.INDIRECT_X, 'EOR'],
            0x51: [self.EOR, AddressingMode.INDIRECT_Y, 'EOR'],

            0xE6: [self.INC, AddressingMode.ZERO_PAGE, 'INC'],
            0xF6: [self.INC, AddressingMode.ZERO_PAGE_X, 'INC'],
            0xEE: [self.INC, AddressingMode.ABSOLUTE, 'INC'],
            0xFE: [self.INC, AddressingMode.ABSOLUTE_X, 'INC'],

            0xE8: [self.INX, None, 'INX'],
            0xC8: [self.INY, None, 'INY'],

            0x4C: [self.JMP, AddressingMode.ABSOLUTE, 'JMP'],
            0x6C: [self.JMP, AddressingMode.INDIRECT, 'JMP'],

            0x20: [self.JSR, AddressingMode.ABSOLUTE, 'JSR'],

            0xA9: [self.LDA, AddressingMode.IMMEDIATE, 'LDA'],
            0xA5: [self.LDA, AddressingMode.ZERO_PAGE, 'LDA'],
            0xB5: [self.LDA, AddressingMode.ZERO_PAGE_X, 'LDA'],
            0xAD: [self.LDA, AddressingMode.ABSOLUTE, 'LDA'],
            0xBD: [self.LDA, AddressingMode.ABSOLUTE_X, 'LDA'],
            0xB9: [self.LDA, AddressingMode.ABSOLUTE_Y, 'LDA'],
            0xA1: [self.LDA, AddressingMode.INDIRECT_X, 'LDA'],
            0xB1: [self.LDA, AddressingMode.INDIRECT_Y, 'LDA'],

            0xA2: [self.LDX, AddressingMode.IMMEDIATE, 'LDX'],
            0xA6: [self.LDX, AddressingMode.ZERO_PAGE, 'LDX'],
            0xB6: [self.LDX, AddressingMode.ZERO_PAGE_Y, 'LDX'],
            0xAE: [self.LDX, AddressingMode.ABSOLUTE, 'LDX'],
            0xBE: [self.LDX, AddressingMode.ABSOLUTE_Y, 'LDX'],

            0xA0: [self.LDY, AddressingMode.IMMEDIATE, 'LDY'],
            0xA4: [self.LDY, AddressingMode.ZERO_PAGE, 'LDY'],
            0xB4: [self.LDY, AddressingMode.ZERO_PAGE_X, 'LDY'],
            0xAC: [self.LDY, AddressingMode.ABSOLUTE, 'LDY'],
            0xBC: [self.LDY, AddressingMode.ABSOLUTE_X, 'LDY'],

            0x4A: [self.LSR, AddressingMode.ACCUMULATOR, 'LSR'],
            0x46: [self.LSR, AddressingMode.ZERO_PAGE, 'LSR'],
            0x56: [self.LSR, AddressingMode.ZERO_PAGE_X, 'LSR'],
            0x4E: [self.LSR, AddressingMode.ABSOLUTE, 'LSR'],
            0x5E: [self.LSR, AddressingMode.ABSOLUTE_X, 'LSR'],

            0xEA: [self.NOP, None, 'NOP'],

            0x09: [self.ORA, AddressingMode.IMMEDIATE, 'ORA'],
            0x05: [self.ORA, AddressingMode.ZERO_PAGE, 'ORA'],
            0x15: [self.ORA, AddressingMode.ZERO_PAGE_X, 'ORA'],
            0x0D: [self.ORA, AddressingMode.ABSOLUTE, 'ORA'],
            0x1D: [self.ORA, AddressingMode.ABSOLUTE_X, 'ORA'],
            0x19: [self.ORA, AddressingMode.ABSOLUTE_Y, 'ORA'],
            0x01: [self.ORA, AddressingMode.INDIRECT_X, 'ORA'],
            0x11: [self.ORA, AddressingMode.INDIRECT_Y, 'ORA'],

            0x48: [self.PHA, None, 'PHA'],

            0x08: [self.PHP, None, 'PHP'],

            0x68: [self.PLA, None, 'PLA'],

            0x28: [self.PLP, None, 'PLP'],

            0x2A: [self.ROL, AddressingMode.ACCUMULATOR, 'ROL'],
            0x26: [self.ROL, AddressingMode.ZERO_PAGE, 'ROL'],
            0x36: [self.ROL, AddressingMode.ZERO_PAGE_X, 'ROL'],
            0x2E: [self.ROL, AddressingMode.ABSOLUTE, 'ROL'],
            0x3E: [self.ROL, AddressingMode.ABSOLUTE_X, 'ROL'],

            0x6A: [self.ROR, AddressingMode.ACCUMULATOR, 'ROR'],
            0x66: [self.ROR, AddressingMode.ZERO_PAGE, 'ROR'],
            0x76: [self.ROR, AddressingMode.ZERO_PAGE_X, 'ROR'],
            0x6E: [self.ROR, AddressingMode.ABSOLUTE, 'ROR'],
            0x7E: [self.ROR, AddressingMode.ABSOLUTE_X, 'ROR'],

            0x40: [self.RTI, None, 'ROR'],

            0x60: [self.RTS, None, 'RTS'],

            0xE9: [self.SBC, AddressingMode.IMMEDIATE, 'SBC'],
            0xE5: [self.SBC, AddressingMode.ZERO_PAGE, 'SBC'],
            0xF5: [self.SBC, AddressingMode.ZERO_PAGE_X, 'SBC'],
            0xED: [self.SBC, AddressingMode.ABSOLUTE, 'SBC'],
            0xFD: [self.SBC, AddressingMode.ABSOLUTE_X, 'SBC'],
            0xF9: [self.SBC, AddressingMode.ABSOLUTE_Y, 'SBC'],
            0xE1: [self.SBC, AddressingMode.INDIRECT_X, 'SBC'],
            0xF1: [self.SBC, AddressingMode.INDIRECT_Y, 'SBC'],

            0x38: [self.SEC, None, 'SEC'],

            0xF8: [self.SED, None, 'SED'],

            0x78: [self.SEI, None, 'SEI'],

            0x85: [self.STA, AddressingMode.ZERO_PAGE, 'STA'],
            0x95: [self.STA, AddressingMode.ZERO_PAGE_X, 'STA'],
            0x8D: [self.STA, AddressingMode.ABSOLUTE, 'STA'],
            0x9D: [self.STA, AddressingMode.ABSOLUTE_X, 'STA'],
            0x99: [self.STA, AddressingMode.ABSOLUTE_Y, 'STA'],
            0x81: [self.STA, AddressingMode.INDIRECT_X, 'STA'],
            0x91: [self.STA, AddressingMode.INDIRECT_Y, 'STA'],

            0x86: [self.STX, AddressingMode.ZERO_PAGE, 'STX'],
            0x96: [self.STX, AddressingMode.ZERO_PAGE_Y, 'STX'],
            0x8E: [self.STX, AddressingMode.ABSOLUTE, 'STX'],

            0x84: [self.STY, AddressingMode.ZERO_PAGE, 'STY'],
            0x94: [self.STY, AddressingMode.ZERO_PAGE_X, 'STY'],
            0x8C: [self.STY, AddressingMode.ABSOLUTE, 'STY'],

            0xAA: [self.TAX, None, 'TAX'],

            0xA8: [self.TAY, None, 'TAY'],

            0xBA: [self.TSX, None, 'TSX'],

            0x8A: [self.TXA, None, 'TXA'],

            0x9A: [self.TXS, None, 'TXS'],

            0x98: [self.TYA, None, 'TYA']
        }

    def initialise_RAM(self) -> None:
        self.ram = Memory()
    
    def load_program(self, program: Program) -> None:
        self.ram.load_program(program)
        self.ram.write_u16(0xFFFC, 0x8000) # Write the start of the program to 0xFFFC 
        self.reset()

    def run_program(self) -> None:

        while True:
            print(f'A: {hex(self.r_accumulator)}, PC: {hex(self.r_program_counter)}, SP: {hex(self.r_stack_pointer)}')
            opcode = self.ram.read(self.r_program_counter) # Code from program
            print(self.lookup_table[opcode][2])
            


            
            self.r_program_counter += 1
            f = self.lookup_table[opcode][0]
            a = self.lookup_table[opcode][1]
            try:
                f(a)
            except:
                pass

            if self.break_flag == True:
                break

    def reset(self) -> None:
        self.r_program_counter = self.ram.read_u16(0xFFFC)
        self.r_stack_pointer = np.uint8(0xFD)
        self.r_accumulator = np.uint8(0)
        self.r_index_X = np.uint8(0)
        self.r_index_Y = np.uint8(0)
        self.r_status = dict.fromkeys(self.r_status, False)

        self.break_flag = False

    def get_operand_address(self, mode: AddressingMode) -> np.uint16:
        # TODO: Update the program counter numbers so they're gotten from the lookup
        match mode:
            case AddressingMode.IMMEDIATE:
                value = self.r_program_counter
                self.r_program_counter += 1
                return value

            case AddressingMode.ZERO_PAGE:
                value = self.ram.read(self.r_program_counter)
                self.r_program_counter += 1
                return value

            case AddressingMode.ZERO_PAGE_X:
                pos = self.ram.read(self.r_program_counter)
                value = pos + self.r_index_X # Wrapping Add (may throw overflow exception)
                self.r_program_counter += 1
                return value

            case AddressingMode.ZERO_PAGE_Y:
                pos = self.ram.read(self.r_program_counter)
                value = pos + self.r_index_Y # Wrapping Add (may throw overflow exception)
                self.r_program_counter += 1
                return value

            case AddressingMode.ABSOLUTE:
                value = self.ram.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                return value

            case AddressingMode.ABSOLUTE_X:
                base = self.ram.read_u16(self.r_program_counter)
                return base + self.r_index_X.astype(np.uint16) # Wrapping Add (may throw overflow exception)

            case AddressingMode.ABSOLUTE_Y:
                base = self.ram.read_u16(self.r_program_counter)
                return base + self.r_index_Y.astype(np.uint16) # Wrapping Add (may throw overflow exception)

            case AddressingMode.INDIRECT:
                raise NotImplementedError

            case AddressingMode.INDIRECT_X:
                base = self.ram.read(self.r_program_counter)
                ptr = base + self.r_index_X # Wrapping Add (may throw overflow exception)
                lo = self.ram.read(ptr.astype(np.uint16))
                hi = self.ram.read((ptr + np.uint8(1)).astype(np.uint16)) # Wrapping Add (may throw overflow exception)
                return np.uint16(hi) << 8 | np.uint16(lo)


            case AddressingMode.INDIRECT_Y:
                base = self.ram.read(self.r_program_counter)

                lo = self.read(base.astype(np.uint16))
                hi = self.read((base + np.uint8).astype(np.uint16)) # Wrapping Add (may throw overflow exception)
                deref_base = np.uint16(hi) << 8 | np.uint16(lo)

                return np.uint16(deref_base) + np.uint16(self.r_index_Y) # Wrapping Add (may throw overflow exception)

            case AddressingMode.IMPLICIT:
                raise NotImplementedError
            case AddressingMode.ACCUMULATOR:
                raise NotImplementedError
            case AddressingMode.RELATIVE:
                # TODO: Verify this is correct
                return self.r_program_counter

    def stack_pop(self) -> np.uint8:
        self.r_stack_pointer += np.uint8(1)
        return self.ram.read(np.uint16(0x1000) + self.r_stack_pointer)

    def stack_pop_u16(self) -> np.uint16:
        lo = np.uint16(self.stack_pop())
        hi = np.uint16(self.stack_pop())

        return np.uint16(hi << 8 | lo)

    def stack_push(self, data: np.uint8):
        self.ram.write(np.uint16(0x1000) + np.uint16(self.r_stack_pointer), data)
        self.r_stack_pointer += np.uint8(1)

    def stack_push_u16(self, data: np.uint16):
        lo = np.uint8(data & 0xff)
        hi = np.uint8(data >> 8)
        self.stack_push(hi)
        self.stack_push(lo)

    def update_zero_and_negative_flags(self, register):
        self.r_status['flag_Z'] = True if register == 0 else False
        self.r_status['flag_N'] = True if register & 0b1000_0000 != 0 else False

    # ----------------------------------------------------------------
    # Implementation of Instructions
    # ----------------------------------------------------------------

    def ADC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        a = np.uint16(self.r_accumulator)
        m = np.uint16(value)
        c = np.uint16(self.r_status & 0b0000_0001)

        result = a + m + c

        self.r_accumulator = np.uint8(result)

        # Setting Flags
        self.r_status['flag_C'] = True if result > 255 else False
        self.r_status['flag_V'] = True if (~(a ^ m) & (a ^ result)) & 0x80 else False
        self.update_zero_and_negative_flags(self.r_accumulator)

    def AND(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        self.r_accumulator &= value
        self.update_zero_and_negative_flags(self.r_accumulator)

    def ASL(self, mode: AddressingMode):
        #TODO: Test this method
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        shifted = value << 1

        self.r_status['flag_C'] = True if shifted > 255 else False
        self.update_zero_and_negative_flags(self.r_accumulator)

        if mode == AddressingMode.ACCUMULATOR:
            self.r_accumulator(np.uint8(shifted))
        else:
            self.ram.write(addr, np.uint8(shifted))

    def BCC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status['flag_C'] == False:
            self.r_program_counter += value

    def BCS(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status['flag_C']:
            self.r_program_counter += value

    def BEQ(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status['flag_Z']:
            self.r_program_counter += value

    def BIT(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = self.r_accumulator & value

        self.r_status['flag_Z'] = True if result == 0 else False
        self.r_status['flag_V'] = bool(result >> 6)
        self.r_status['flag_N'] = bool(result >> 7)

    def BMI(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status['flag_N']:
            self.r_program_counter += value
    
    def BNE(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status['flag_Z'] == False:
            self.r_program_counter += value

    def BPL(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status['flag_N'] == False:
            self.r_program_counter += value

    def BRK(self, mode: AddressingMode):
        self.break_flag = True

    def BVC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status['flag_V'] == False:
            self.r_program_counter += value

    def BVS(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status['flag_V']:
            self.r_program_counter += value

    def CLC(self, mode: AddressingMode):
        self.r_status['flag_C'] = False

    def CLD(self, mode: AddressingMode):
        self.r_status['flag_D'] = False

    def CLI(self, mode: AddressingMode):
        self.r_status['flag_I'] = False

    def CLV(self, mode: AddressingMode):
        self.r_status['flag_V'] = False

    def CMP(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = np.uint8(self.r_accumulator - value)

        self.r_status['flag_C'] = True if self.r_accumulator >= value else False
        self.r_status['flag_Z'] = True if self.r_accumulator == value else False
        self.r_status['flag_N'] = bool(result >> 7)

    def CPX(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = np.uint8(self.r_index_X - value)

        self.r_status['flag_C'] = True if self.r_index_X >= value else False
        self.r_status['flag_Z'] = True if self.r_index_X == value else False
        self.r_status['flag_N'] = bool(result >> 7)

    def CPY(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = np.uint8(self.r_index_Y - value)

        self.r_status['flag_C'] = True if self.r_index_Y >= value else False
        self.r_status['flag_Z'] = True if self.r_index_Y == value else False
        self.r_status['flag_N'] = bool(result >> 7)

    def DEC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = value - 1
        self.ram.write(addr, result)

        self.r_status['flag_Z'] = True if result == 0 else False
        self.r_status['flag_N'] = bool(result >> 7)

    def DEX(self, mode: AddressingMode):
        self.r_index_X -= 1
        self.update_zero_and_negative_flags(self.r_index_X)

    def DEY(self, mode: AddressingMode):
        self.r_index_Y -= 1
        self.update_zero_and_negative_flags(self.r_index_Y)

    def EOR(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        self.r_accumulator ^= value

        self.update_zero_and_negative_flags(self.r_accumulator)

    def INC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = value + 1
        self.ram.write(addr, result)

        self.r_status['flag_Z'] = True if result == 0 else False
        self.r_status['flag_N'] = bool(result >> 7)

    def INX(self, mode: AddressingMode):
        self.r_index_X += 1
        self.update_zero_and_negative_flags(self.r_index_X)

    def INY(self, mode: AddressingMode):
        self.r_index_Y += 1
        self.update_zero_and_negative_flags(self.r_index_Y)

    def JMP(self, mode: AddressingMode):
        #TODO: There is a bug which needs implementing in this function
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        self.r_program_counter = value

    def JSR(self, mode: AddressingMode):
        self.stack_push_u16(self.r_program_counter + 1) # For some reason the ebook puts this as + 2 - 1 (ie + 1)
        addr = self.get_operand_address(mode)
        self.r_program_counter = addr

    def LDA(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        self.r_accumulator = value
        self.update_zero_and_negative_flags(self.r_accumulator)

    def LDX(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        self.r_index_X = value
        self.update_zero_and_negative_flags(self.r_index_X)

    def LDY(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        self.r_index_Y = value
        self.update_zero_and_negative_flags(self.r_index_Y)

    def LSR(self, mode: AddressingMode):
        raise NotImplementedError

    def NOP(self, mode: AddressingMode):
        pass

    def ORA(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        self.r_accumulator |= value

        self.update_zero_and_negative_flags(self.r_accumulator)

    def PHA(self, mode: AddressingMode):
        raise NotImplementedError

    def PHP(self, mode: AddressingMode):
        raise NotImplementedError

    def PLA(self, mode: AddressingMode):
        raise NotImplementedError

    def PLP(self, mode: AddressingMode):
        raise NotImplementedError

    def ROL(self, mode: AddressingMode):
        raise NotImplementedError

    def ROR(self, mode: AddressingMode):
        raise NotImplementedError

    def RTI(self, mode: AddressingMode):
        raise NotImplementedError

    def RTS(self, mode: AddressingMode):
        raise NotImplementedError

    def SBC(self, mode: AddressingMode):
        raise NotImplementedError

    def SEC(self, mode: AddressingMode):
        self.r_status['flag_C'] = True

    def SED(self, mode: AddressingMode):
        self.r_status['flag_D'] = True

    def SEI(self, mode: AddressingMode):
        self.r_status['flag_I'] = True

    def STA(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        self.ram.write(addr, self.r_accumulator)

    def STX(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        self.ram.write(addr, self.r_index_X)

    def STY(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        self.ram.write(addr, self.r_index_Y)

    def TAX(self, mode: AddressingMode):
        self.r_index_X = self.r_accumulator
        self.update_zero_and_negative_flags(self.r_index_X)

    def TAY(self, mode: AddressingMode):
        self.r_index_Y = self.r_accumulator
        self.update_zero_and_negative_flags(self.r_index_Y)

    def TSX(self, mode: AddressingMode):
        raise NotImplementedError

    def TXA(self, mode: AddressingMode):
        self.r_accumulator = self.r_index_X
        self.update_zero_and_negative_flags(self.r_accumulator)

    def TXS(self, mode: AddressingMode):
        raise NotImplementedError

    def TYA(self, mode: AddressingMode):
        raise NotImplementedError