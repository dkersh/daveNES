from .cpu import AddressingMode
#from .cpu import MOS6502
import numpy as np

class MOS6502_OpCodes():
    def __init__(self, cpu: 'MOS6502') -> None:
        """Class containing the MOS6502 56 operating codes. Dependency injection
        used to attach to the MOS6502 CPU class.
        The lookup_table attribute is used to pull the relevant OpCode based on the input key.
        Methods are not documented purposefully.

        Args:
            cpu (MOS6502): MOS6502 class dependent on operating codes.
        """
        self.cpu = cpu
        self.lookup_table = {
            0x69: [self.ADC, 2, AddressingMode.IMMEDIATE, "ADC", ],
            0x65: [self.ADC, 3, AddressingMode.ZERO_PAGE, "ADC"],
            0x75: [self.ADC, 4, AddressingMode.ZERO_PAGE_X, "ADC"],
            0x6D: [self.ADC, 4, AddressingMode.ABSOLUTE, "ADC"],
            0x7D: [self.ADC, 4, AddressingMode.ABSOLUTE_X, "ADC"],
            0x79: [self.ADC, 4, AddressingMode.ABSOLUTE_Y, "ADC"],
            0x61: [self.ADC, 6, AddressingMode.INDIRECT_X, "ADC"],
            0x71: [self.ADC, 5, AddressingMode.INDIRECT_Y, "ADC"],
            0x29: [self.AND, 2, AddressingMode.IMMEDIATE, "AND"],
            0x25: [self.AND, 3, AddressingMode.ZERO_PAGE, "AND"],
            0x35: [self.AND, 4, AddressingMode.ZERO_PAGE_X, "AND"],
            0x2D: [self.AND, 4, AddressingMode.ABSOLUTE, "AND"],
            0x3D: [self.AND, 4, AddressingMode.ABSOLUTE_X, "AND"],
            0x39: [self.AND, 4, AddressingMode.ABSOLUTE_Y, "AND"],
            0x21: [self.AND, 6, AddressingMode.INDIRECT_X, "AND"],
            0x31: [self.AND, 5, AddressingMode.INDIRECT_Y, "AND"],
            0x0A: [self.ASL, 2, AddressingMode.ACCUMULATOR, "ASL"],
            0x06: [self.ASL, 5, AddressingMode.ZERO_PAGE, "ASL"],
            0x16: [self.ASL, 6, AddressingMode.ZERO_PAGE_X, "ASL"],
            0x0E: [self.ASL, 6, AddressingMode.ABSOLUTE, "ASL"],
            0x1E: [self.ASL, 7, AddressingMode.ABSOLUTE_X, "ASL"],
            0x90: [self.BCC, 2, AddressingMode.RELATIVE, "BCC"],
            0xB0: [self.BCS, 2, AddressingMode.RELATIVE, "BCS"],
            0xF0: [self.BEQ, 2, AddressingMode.RELATIVE, "BEQ"],
            0x24: [self.BIT, 3, AddressingMode.ZERO_PAGE, "BIT"],
            0x2C: [self.BIT, 4, AddressingMode.ABSOLUTE, "BIT"],
            0x30: [self.BMI, 2, AddressingMode.RELATIVE, "BMI"],
            0xD0: [self.BNE, 2, AddressingMode.RELATIVE, "BNE"],
            0x10: [self.BPL, 2, AddressingMode.RELATIVE, "BPL"],
            0x00: [self.BRK, 7, None, "BRK"],
            0x50: [self.BVC, 2, AddressingMode.RELATIVE, "BVC"],
            0x70: [self.BVS, 2, AddressingMode.RELATIVE, "BVS"],
            0x18: [self.CLC, 2, None, "CLC"],
            0xD8: [self.CLD, 2, None, "CLD"],
            0x58: [self.CLI, 2, None, "CLI"],
            0xB8: [self.CLV, 2, None, "CLV"],
            0xC9: [self.CMP, 2, AddressingMode.IMMEDIATE, "CMP"],
            0xC5: [self.CMP, 3, AddressingMode.ZERO_PAGE, "CMP"],
            0xD5: [self.CMP, 4, AddressingMode.ZERO_PAGE_X, "CMP"],
            0xCD: [self.CMP, 4, AddressingMode.ABSOLUTE, "CMP"],
            0xDD: [self.CMP, 4, AddressingMode.ABSOLUTE_X, "CMP"],
            0xD9: [self.CMP, 4, AddressingMode.ABSOLUTE_Y, "CMP"],
            0xC1: [self.CMP, 6, AddressingMode.INDIRECT_X, "CMP"],
            0xD1: [self.CMP, 5, AddressingMode.INDIRECT_Y, "CMP"],
            0xE0: [self.CPX, 2, AddressingMode.IMMEDIATE, "CPX"],
            0xE4: [self.CPX, 3, AddressingMode.ZERO_PAGE, "CPX"],
            0xEC: [self.CPX, 4, AddressingMode.ABSOLUTE, "CPX"],
            0xC0: [self.CPY, 2, AddressingMode.IMMEDIATE, "CPY"],
            0xC4: [self.CPY, 3, AddressingMode.ZERO_PAGE, "CPY"],
            0xCC: [self.CPY, 4, AddressingMode.ABSOLUTE, "CPY"],
            0xC6: [self.DEC, 5, AddressingMode.ZERO_PAGE, "DEC"],
            0xD6: [self.DEC, 6, AddressingMode.ZERO_PAGE_X, "DEC"],
            0xCE: [self.DEC, 6, AddressingMode.ABSOLUTE, "DEC"],
            0xDE: [self.DEC, 7, AddressingMode.ABSOLUTE_X, "DEC"],
            0xCA: [self.DEX, 2, None, "DEX"],
            0x88: [self.DEY, 2, None, "DEY"],
            0x49: [self.EOR, 2, AddressingMode.IMMEDIATE, "EOR"],
            0x45: [self.EOR, 3, AddressingMode.ZERO_PAGE, "EOR"],
            0x55: [self.EOR, 4, AddressingMode.ZERO_PAGE_X, "EOR"],
            0x4D: [self.EOR, 4, AddressingMode.ABSOLUTE, "EOR"],
            0x5D: [self.EOR, 4, AddressingMode.ABSOLUTE_X, "EOR"],
            0x59: [self.EOR, 4, AddressingMode.ABSOLUTE_Y, "EOR"],
            0x41: [self.EOR, 6, AddressingMode.INDIRECT_X, "EOR"],
            0x51: [self.EOR, 5, AddressingMode.INDIRECT_Y, "EOR"],
            0xE6: [self.INC, 5, AddressingMode.ZERO_PAGE, "INC"],
            0xF6: [self.INC, 6, AddressingMode.ZERO_PAGE_X, "INC"],
            0xEE: [self.INC, 6, AddressingMode.ABSOLUTE, "INC"],
            0xFE: [self.INC, 7, AddressingMode.ABSOLUTE_X, "INC"],
            0xE8: [self.INX, 2, None, "INX"],
            0xC8: [self.INY, 2, None, "INY"],
            0x4C: [self.JMP, 3, AddressingMode.ABSOLUTE, "JMP"],
            0x6C: [self.JMP, 3, AddressingMode.INDIRECT, "JMP"],
            0x20: [self.JSR, 6, AddressingMode.ABSOLUTE, "JSR"],
            0xA9: [self.LDA, 2, AddressingMode.IMMEDIATE, "LDA"],
            0xA5: [self.LDA, 3, AddressingMode.ZERO_PAGE, "LDA"],
            0xB5: [self.LDA, 4, AddressingMode.ZERO_PAGE_X, "LDA"],
            0xAD: [self.LDA, 4, AddressingMode.ABSOLUTE, "LDA"],
            0xBD: [self.LDA, 4, AddressingMode.ABSOLUTE_X, "LDA"],
            0xB9: [self.LDA, 4, AddressingMode.ABSOLUTE_Y, "LDA"],
            0xA1: [self.LDA, 6, AddressingMode.INDIRECT_X, "LDA"],
            0xB1: [self.LDA, 5, AddressingMode.INDIRECT_Y, "LDA"],
            0xA2: [self.LDX, 2, AddressingMode.IMMEDIATE, "LDX"],
            0xA6: [self.LDX, 3, AddressingMode.ZERO_PAGE, "LDX"],
            0xB6: [self.LDX, 4, AddressingMode.ZERO_PAGE_Y, "LDX"],
            0xAE: [self.LDX, 4, AddressingMode.ABSOLUTE, "LDX"],
            0xBE: [self.LDX, 4, AddressingMode.ABSOLUTE_Y, "LDX"],
            0xA0: [self.LDY, 2, AddressingMode.IMMEDIATE, "LDY"],
            0xA4: [self.LDY, 3, AddressingMode.ZERO_PAGE, "LDY"],
            0xB4: [self.LDY, 4, AddressingMode.ZERO_PAGE_X, "LDY"],
            0xAC: [self.LDY, 4, AddressingMode.ABSOLUTE, "LDY"],
            0xBC: [self.LDY, 4, AddressingMode.ABSOLUTE_X, "LDY"],
            0x4A: [self.LSR_accumulator, 2, AddressingMode.ACCUMULATOR, "LSR"],
            0x46: [self.LSR, 5, AddressingMode.ZERO_PAGE, "LSR"],
            0x56: [self.LSR, 6, AddressingMode.ZERO_PAGE_X, "LSR"],
            0x4E: [self.LSR, 6, AddressingMode.ABSOLUTE, "LSR"],
            0x5E: [self.LSR, 7, AddressingMode.ABSOLUTE_X, "LSR"],
            0xEA: [self.NOP, 2, None, "NOP"],
            0x09: [self.ORA, 2, AddressingMode.IMMEDIATE, "ORA"],
            0x05: [self.ORA, 3, AddressingMode.ZERO_PAGE, "ORA"],
            0x15: [self.ORA, 4, AddressingMode.ZERO_PAGE_X, "ORA"],
            0x0D: [self.ORA, 4, AddressingMode.ABSOLUTE, "ORA"],
            0x1D: [self.ORA, 4, AddressingMode.ABSOLUTE_X, "ORA"],
            0x19: [self.ORA, 4, AddressingMode.ABSOLUTE_Y, "ORA"],
            0x01: [self.ORA, 6, AddressingMode.INDIRECT_X, "ORA"],
            0x11: [self.ORA, 5, AddressingMode.INDIRECT_Y, "ORA"],
            0x48: [self.PHA, 3, None, "PHA"],
            0x08: [self.PHP, 3, None, "PHP"],
            0x68: [self.PLA, 4, None, "PLA"],
            0x28: [self.PLP, 4, None, "PLP"],
            0x2A: [self.ROL, 2, AddressingMode.ACCUMULATOR, "ROL"],
            0x26: [self.ROL, 5, AddressingMode.ZERO_PAGE, "ROL"],
            0x36: [self.ROL, 6, AddressingMode.ZERO_PAGE_X, "ROL"],
            0x2E: [self.ROL, 6, AddressingMode.ABSOLUTE, "ROL"],
            0x3E: [self.ROL, 7, AddressingMode.ABSOLUTE_X, "ROL"],
            0x6A: [self.ROR, 2, AddressingMode.ACCUMULATOR, "ROR"],
            0x66: [self.ROR, 5, AddressingMode.ZERO_PAGE, "ROR"],
            0x76: [self.ROR, 6, AddressingMode.ZERO_PAGE_X, "ROR"],
            0x6E: [self.ROR, 6, AddressingMode.ABSOLUTE, "ROR"],
            0x7E: [self.ROR, 7, AddressingMode.ABSOLUTE_X, "ROR"],
            0x40: [self.RTI, 6, None, "RTI"],
            0x60: [self.RTS, 6, None, "RTS"],
            0xE9: [self.SBC, 2, AddressingMode.IMMEDIATE, "SBC"],
            0xE5: [self.SBC, 3, AddressingMode.ZERO_PAGE, "SBC"],
            0xF5: [self.SBC, 4, AddressingMode.ZERO_PAGE_X, "SBC"],
            0xED: [self.SBC, 4, AddressingMode.ABSOLUTE, "SBC"],
            0xFD: [self.SBC, 4, AddressingMode.ABSOLUTE_X, "SBC"],
            0xF9: [self.SBC, 4, AddressingMode.ABSOLUTE_Y, "SBC"],
            0xE1: [self.SBC, 6, AddressingMode.INDIRECT_X, "SBC"],
            0xF1: [self.SBC, 5, AddressingMode.INDIRECT_Y, "SBC"],
            0x38: [self.SEC, 2, None, "SEC"],
            0xF8: [self.SED, 2, None, "SED"],
            0x78: [self.SEI, 2, None, "SEI"],
            0x85: [self.STA, 3, AddressingMode.ZERO_PAGE, "STA"],
            0x95: [self.STA, 4, AddressingMode.ZERO_PAGE_X, "STA"],
            0x8D: [self.STA, 4, AddressingMode.ABSOLUTE, "STA"],
            0x9D: [self.STA, 5, AddressingMode.ABSOLUTE_X, "STA"],
            0x99: [self.STA, 5, AddressingMode.ABSOLUTE_Y, "STA"],
            0x81: [self.STA, 6, AddressingMode.INDIRECT_X, "STA"],
            0x91: [self.STA, 6, AddressingMode.INDIRECT_Y, "STA"],
            0x86: [self.STX, 3, AddressingMode.ZERO_PAGE, "STX"],
            0x96: [self.STX, 4, AddressingMode.ZERO_PAGE_Y, "STX"],
            0x8E: [self.STX, 4, AddressingMode.ABSOLUTE, "STX"],
            0x84: [self.STY, 3, AddressingMode.ZERO_PAGE, "STY"],
            0x94: [self.STY, 4, AddressingMode.ZERO_PAGE_X, "STY"],
            0x8C: [self.STY, 4, AddressingMode.ABSOLUTE, "STY"],
            0xAA: [self.TAX, 2, None, "TAX"],
            0xA8: [self.TAY, 2, None, "TAY"],
            0xBA: [self.TSX, 2, None, "TSX"],
            0x8A: [self.TXA, 2, None, "TXA"],
            0x9A: [self.TXS, 2, None, "TXS"],
            0x98: [self.TYA, 2, None, "TYA"],
        }
        
    def ADC(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        a = np.uint16(self.cpu.r_accumulator)
        m = np.uint16(value)
        c = np.uint16(self.cpu.r_status["flag_C"])

        result = a + m + c

        self.cpu.r_accumulator = np.uint8(result)

        # Setting Flags
        self.cpu.r_status["flag_C"] = True if result > 255 else False
        self.cpu.r_status["flag_V"] = True if (~(a ^ m) & (a ^ result)) & 0x80 else False
        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def AND(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        self.cpu.r_accumulator &= value
        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def ASL(self, mode: AddressingMode):
        # TODO: Should probably split this up into accumulator / non accumulator
        if mode == AddressingMode.ACCUMULATOR:
            value = self.cpu.get_operand_address(mode)
        else:
            addr = self.cpu.get_operand_address(mode)
            value = self.cpu.bus.read(addr)
        shifted = value << 1

        self.cpu.r_status["flag_C"] = True if shifted > 255 else False

        if mode == AddressingMode.ACCUMULATOR:
            self.cpu.r_accumulator = np.uint8(shifted)
            self.cpu.update_zero_and_negative_flags(np.uint8(shifted))
            if self.cpu.r_accumulator == 0:
                self.cpu.r_status['flag_Z'] = True
        else:
            self.cpu.bus.write(addr, np.uint8(shifted))
            self.cpu.update_zero_and_negative_flags(np.uint8(shifted))
        

    def BCC(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        if self.cpu.r_status["flag_C"] == False:
            self.cpu.r_program_counter += np.int8(value)

    def BCS(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        if self.cpu.r_status["flag_C"]:
            self.cpu.r_program_counter += np.int8(value)

    def BEQ(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        if self.cpu.r_status["flag_Z"]:
            self.cpu.r_program_counter += np.int8(value) # + np.uint8(1)

    def BIT(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)
        result = self.cpu.r_accumulator & value

        self.cpu.r_status["flag_Z"] = True if result == 0 else False
        self.cpu.r_status["flag_V"] = bool(value & 0b0100_0000)
        self.cpu.r_status["flag_N"] = bool(value & 0b1000_0000)

    def BMI(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        if self.cpu.r_status["flag_N"]:
            print('flag N')
            self.cpu.r_program_counter += np.int8(value)

    def BNE(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        if self.cpu.r_status["flag_Z"] == False:
            self.cpu.r_program_counter += np.int8(value)

    def BPL(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        if self.cpu.r_status["flag_N"] == False:
            self.cpu.r_program_counter += np.int8(value)

    def BRK(self, mode: AddressingMode):
        print('BREAK')
        self.cpu.r_status['flag_B0'] = True
        self.cpu.r_program_counter += 1

    def BVC(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        if self.cpu.r_status["flag_V"] == False:
            self.cpu.r_program_counter += np.int8(value)

    def BVS(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        if self.cpu.r_status["flag_V"]:
            self.cpu.r_program_counter += np.int8(value)

    def CLC(self, mode: AddressingMode):
        self.cpu.r_status["flag_C"] = False

    def CLD(self, mode: AddressingMode):
        self.cpu.r_status["flag_D"] = False

    def CLI(self, mode: AddressingMode):
        self.cpu.r_status["flag_I"] = False

    def CLV(self, mode: AddressingMode):
        self.cpu.r_status["flag_V"] = False

    def CMP(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)
        result = np.uint8(self.cpu.r_accumulator) - value

        #print(f'r_a: {self.cpu.r_accumulator}, value: {value}')
        #print(f'The result is {result}')

        self.cpu.r_status["flag_C"] = True if self.cpu.r_accumulator >= value else False
        self.cpu.r_status["flag_Z"] = True if self.cpu.r_accumulator == value else False
        self.cpu.r_status["flag_N"] = bool(result & 0b1000_0000)

    def CPX(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)
        result = np.uint8(self.cpu.r_index_X) - value

        self.cpu.r_status["flag_C"] = True if self.cpu.r_index_X >= value else False
        self.cpu.r_status["flag_Z"] = True if self.cpu.r_index_X == value else False
        self.cpu.r_status["flag_N"] = bool(result & 0b1000_0000)

    def CPY(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)
        result = np.uint8(self.cpu.r_index_Y) - value

        self.cpu.r_status["flag_C"] = True if self.cpu.r_index_Y >= value else False
        self.cpu.r_status["flag_Z"] = True if self.cpu.r_index_Y == value else False
        self.cpu.r_status["flag_N"] = bool(result & 0b1000_0000)

    def DEC(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)
        result = value - np.uint8(1)
        self.cpu.bus.write(addr, result)

        self.cpu.r_status["flag_Z"] = True if result == 0 else False
        self.cpu.r_status["flag_N"] = bool(result >> 7)

    def DEX(self, mode: AddressingMode):
        self.cpu.r_index_X -= np.uint8(1)
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_X)

    def DEY(self, mode: AddressingMode):
        self.cpu.r_index_Y -= np.uint8(1)
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_Y)

    def EOR(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)
        print(value)
        self.cpu.r_accumulator ^= value

        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def INC(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)
        result = value + np.uint8(1)
        self.cpu.bus.write(addr, result)

        self.cpu.r_status["flag_Z"] = True if result == 0 else False
        self.cpu.r_status["flag_N"] = bool(result >> 7)

    def INX(self, mode: AddressingMode):
        self.cpu.r_index_X = np.uint8(self.cpu.r_index_X) + np.uint8(1)
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_X)

    def INY(self, mode: AddressingMode):
        self.cpu.r_index_Y = np.uint8(self.cpu.r_index_Y) + np.uint8(1)
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_Y)

    def JMP(self, mode: AddressingMode):
        # TODO: There is a bug which needs implementing in this function
        addr = self.cpu.get_operand_address(mode)
        self.cpu.r_program_counter = addr

    def JSR(self, mode: AddressingMode):
        self.cpu.stack_push_u16(
            self.cpu.r_program_counter + np.uint8(1)
        )  # For some reason the ebook puts this as + 2 - 1 (ie + 1)
        addr = self.cpu.get_operand_address(mode)
        self.cpu.r_program_counter = addr

    def LDA(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        self.cpu.r_accumulator = value
        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def LDX(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        self.cpu.r_index_X = value
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_X)

    def LDY(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        self.cpu.r_index_Y = value
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_Y)

    def LSR_accumulator(self, mode: AddressingMode):
        value = self.cpu.r_accumulator
        # Setting Flags
        if value & np.uint8(1) == 1:
            self.cpu.r_status['flag_C'] = True
        else:
            self.cpu.r_status['flag_C'] = False
        value = value >> 1

        self.cpu.r_accumulator = value
        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def LSR(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        # Setting Flags
        if value & np.uint8(1) == 1:
            self.cpu.r_status['flag_C'] = True
        else:
            self.cpu.r_status['flag_C'] = False
        value = value >> 1
        self.cpu.bus.write(addr, value)
        self.cpu.update_zero_and_negative_flags(value)
        
    def NOP(self, mode: AddressingMode):
        # This is supposed to be a pass
        pass

    def ORA(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)
        self.cpu.r_accumulator |= value

        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def PHA(self, mode: AddressingMode):
        self.cpu.stack_push(self.cpu.r_accumulator)
        #self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def PHP(self, mode: AddressingMode):
        self.cpu.stack_push(self.cpu.status_to_value())

    def PLA(self, mode: AddressingMode):
        self.cpu.r_accumulator = self.cpu.stack_pop()
        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def PLP(self, mode: AddressingMode):
        value = self.cpu.stack_pop()
        self.cpu.value_to_status(value)

    def ROL(self, mode: AddressingMode):
        # Acts different based on Accumulator or Not Addressing Mode
        if mode == AddressingMode.ACCUMULATOR:
            value = self.cpu.get_operand_address(mode)
            print(f'value: {value}')
        else:
            addr = self.cpu.get_operand_address(mode)
            value = self.cpu.bus.read(addr)
        
        old_carry = self.cpu.r_status['flag_C']
        if value >> 7 == 1:
            self.cpu.r_status['flag_N'] == True
        else:
            self.cpu.r_status['flag_N'] == False

        value = np.uint8(value << 1)
        print(f'new value: {value}')
        if old_carry:
            value = value | 0b0000_0001
        if mode == AddressingMode.ACCUMULATOR:
            self.cpu.r_accumulator = value
        else:
            self.cpu.bus.write(addr, value)

    def ROR(self, mode: AddressingMode):
        # Acts different based on Accumulator or Not Addressing Mode
        if mode == AddressingMode.ACCUMULATOR:
            value = self.cpu.get_operand_address(mode)
            print(f'value: {value}')
        else:
            addr = self.cpu.get_operand_address(mode)
            value = self.cpu.bus.read(addr)
        
        old_carry = self.cpu.r_status['flag_C']
        if value >> 7 == 1:
            self.cpu.r_status['flag_N'] == True
        else:
            self.cpu.r_status['flag_N'] == False

        value = np.uint8(value >> 1)
        if old_carry:
            value = value | 0b1000_0000
        if mode == AddressingMode.ACCUMULATOR:
            self.cpu.r_accumulator = value
        else:
            self.cpu.bus.write(addr, value)

    def RTI(self, mode: AddressingMode):
        raise NotImplementedError

    def RTS(self, mode: AddressingMode):
        value = self.cpu.stack_pop_u16()
        self.cpu.r_program_counter = value + np.uint8(1)

    def SBC(self, mode: AddressingMode):
        # A-B = A + (-B) and -B = !B + 1
        addr = self.cpu.get_operand_address(mode)
        value = self.cpu.bus.read(addr)

        a = self.cpu.r_accumulator
        b = np.uint8(value)

        #print(result := a + (~b + self.cpu.r_status['flag_C']))
        #print(result := a + (~b + (not self.cpu.r_status['flag_C'])) + 1)
        #print(result := a + (b ^ 0x00FF) + self.cpu.r_status['flag_C']) # http://forum.6502.org/viewtopic.php?p=37758#p37758
        result = a + (b ^ 0x00FF) + self.cpu.r_status['flag_C']

        #print(f'{value =}')
        #print(f'{a =}')
        #print(f'{b =}')
        #print(f'{result =}')
        #print(f'{self.cpu.r_status["flag_C"] = }')

        # Setting Flags
        self.cpu.r_status["flag_C"] = True if result > 255 else False
        result = np.uint8(result)
        self.cpu.r_status["flag_V"] = True if (~(value ^ result) & (a ^ result)) & 0x80 else False
        self.cpu.r_accumulator = result
        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def SEC(self, mode: AddressingMode):
        self.cpu.r_status["flag_C"] = True

    def SED(self, mode: AddressingMode):
        self.cpu.r_status["flag_D"] = True

    def SEI(self, mode: AddressingMode):
        self.cpu.r_status["flag_I"] = True

    def STA(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        self.cpu.bus.write(addr, self.cpu.r_accumulator)

    def STX(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        self.cpu.bus.write(addr, self.cpu.r_index_X)

    def STY(self, mode: AddressingMode):
        addr = self.cpu.get_operand_address(mode)
        self.cpu.bus.write(addr, self.cpu.r_index_Y)

    def TAX(self, mode: AddressingMode):
        self.cpu.r_index_X = self.cpu.r_accumulator
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_X)

    def TAY(self, mode: AddressingMode):
        self.cpu.r_index_Y = self.cpu.r_accumulator
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_Y)

    def TSX(self, mode: AddressingMode):
        self.cpu.r_index_X = self.cpu.r_stack_pointer
        self.cpu.update_zero_and_negative_flags(self.cpu.r_index_X)

    def TXA(self, mode: AddressingMode):
        self.cpu.r_accumulator = self.cpu.r_index_X
        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)

    def TXS(self, mode: AddressingMode):
        self.cpu.r_stack_pointer = self.cpu.r_index_X

    def TYA(self, mode: AddressingMode):
        self.cpu.r_accumulator = self.cpu.r_index_Y
        self.cpu.update_zero_and_negative_flags(self.cpu.r_accumulator)