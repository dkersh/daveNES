from enum import Enum, auto

import numpy as np

from memory import Memory
from program import Program
import pygame
import time


class AddressingMode(Enum):
    IMMEDIATE = auto()
    ZERO_PAGE = auto()
    ZERO_PAGE_X = auto()
    ZERO_PAGE_Y = auto()
    ABSOLUTE = auto()
    ABSOLUTE_X = auto()
    ABSOLUTE_Y = auto()
    INDIRECT = auto()
    INDIRECT_X = auto()
    INDIRECT_Y = auto()
    IMPLICIT = auto()
    ACCUMULATOR = auto()
    RELATIVE = auto()


class MOS6502:
    def __init__(self, debug=False) -> None:
        self.debug = debug
        # The Registers
        self.r_program_counter = np.uint16(0)
        self.r_stack_pointer = np.uint8(0)
        self.r_accumulator = np.uint8(0)
        self.r_index_X = np.uint8(0)
        self.r_index_Y = np.uint8(0)
        self.r_status = {
            "flag_C": False,
            "flag_Z": False,
            "flag_I": False,
            "flag_D": False,
            "flag_B0": False,
            "flag_B1": True,
            "flag_V": False,
            "flag_N": False,
        }
        # self.r_status = np.uint8(0) # NV B*B* DIZC, B* == Break
        self.memory = None
        self.break_flag = False

        # TODO: Add number of cycles to each command.
        # hexcode: [function, number of cycles,addressing mode, , string for reference]
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

    def initialise_RAM(self) -> None:
        self.ram = Memory()

    def load_program(self, program: Program) -> None:
        self.ram.load_program(program)
        self.ram.write_u16(0xFFFC, 0x0600)  # Write the start of the program to addr 0xFFFC
        self.reset()

    def step_program(self) -> bool:
        # TODO: Gravitate towards a step program paradigm.
        # Random value required for Snake program
        # self.ram.write(0xfe, np.random.randint(1, 16, dtype=np.uint8)) # random value to memory

        if self.debug:
            self.ram.visualise_memory()
            input("Press Button to continue")

        opcode = self.ram.read(self.r_program_counter)  # Code from program
        print(f'{hex(opcode)}, {self.lookup_table[opcode][3]}')
        self.print_system()

        self.r_program_counter += 1
        f = self.lookup_table[opcode][0]
        a = self.lookup_table[opcode][2]
        f(a) # run the opcode with the specified addressing mode

    def run_program(self) -> None:
        while True:
            self.step_program()

            if self.break_flag:
                print('program ending')
                break
    
    '''
    def run_program(self) -> None:
        # Set up pygame
        # TODO: Offload to a different class


        # For the snake program
        pygame.init()
        screen = pygame.display.set_mode((320, 320))
        data = np.zeros(32*32)
        pygame.display.update()

        while True:
            self.step_program()
            
            # This is Explicitly for the snake program
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.break_flag = True
                    break
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    print('UP PRESSED')
                    #print(f'{hex(opcode)}, {self.lookup_table[opcode][3]}')
                    #self.print_system()
                    self.ram.write(0xff, 0x77)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    print('RIGHT PRESSED')
                    self.ram.write(0xff, 0x61)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    print('LEFT PRESSED')
                    self.ram.write(0xff, 0x64)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    print('DOWN PRESSED')
                    self.ram.write(0xff, 0x73)

            if np.all(data == self.ram.memory[0x0200:0x05FF+1]) == False:
                data = self.ram.memory[0x0200:0x05FF+1]
                data = np.reshape(data, (32, 32))
                surf = pygame.surfarray.make_surface(data)
                scaled_surf = pygame.transform.scale(surf, (320, 320))
                screen.blit(scaled_surf, (0, 0))
                screen.blit(pygame.transform.rotate(screen, -90), (0, 0))
                pygame.display.update()

            if self.break_flag == True:
                break
        
        #

            # time.sleep(0.0000001)
        pygame.quit()
    '''

    def reset(self) -> None:
        self.r_program_counter = self.ram.read_u16(0xFFFC)
        self.r_stack_pointer = np.uint8(0xFF)
        self.r_accumulator = np.uint8(0)
        self.r_index_X = np.uint8(0)
        self.r_index_Y = np.uint8(0)
        self.r_status = dict.fromkeys(self.r_status, False)
        ###
        self.r_status["flag_B0"] = False
        self.r_status["flag_B1"] = True
        ###

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
                value = (
                    pos + self.r_index_X
                )  # Wrapping Add (may throw overflow exception)
                self.r_program_counter += 1
                return np.uint8(value)

            case AddressingMode.ZERO_PAGE_Y:
                pos = self.ram.read(self.r_program_counter)
                value = (
                    pos + self.r_index_Y
                )  # Wrapping Add (may throw overflow exception)
                self.r_program_counter += 1
                return np.uint8(value)

            case AddressingMode.ABSOLUTE:
                value = self.ram.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                return value

            case AddressingMode.ABSOLUTE_X:
                base = self.ram.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                return base + np.uint16(self.r_index_X) # Wrapping Add (may throw overflow exception)

            case AddressingMode.ABSOLUTE_Y:
                base = self.ram.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                return base + np.uint16(self.r_index_Y)  # Wrapping Add (may throw overflow exception)

            case AddressingMode.INDIRECT:
                base = self.ram.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                base = self.ram.read_u16(base)
                self.r_program_counter += 2
                return base

            case AddressingMode.INDIRECT_X:
                base = self.ram.read(self.r_program_counter)
                self.r_program_counter += 1
                ptr = base + np.uint8(self.r_index_X)
                lo = self.ram.read(ptr)
                hi = self.ram.read(ptr + np.uint8(1))

                return hi << 8 | lo

            case AddressingMode.INDIRECT_Y:
                base = self.ram.read(self.r_program_counter)
                self.r_program_counter += 1

                lo = self.ram.read(base.astype(np.uint16))
                hi = self.ram.read(
                    (base + np.uint8(1)).astype(np.uint16)
                )  # Wrapping Add (may throw overflow exception)
                deref_base = np.uint16(hi) << 8 | np.uint16(lo)

                return np.uint16(deref_base) + np.uint16(
                    self.r_index_Y
                )  # Wrapping Add (may throw overflow exception)

            case AddressingMode.IMPLICIT:
                raise NotImplementedError
            case AddressingMode.ACCUMULATOR:
                # TODO: Any time this addressingmode is requested, act directly on Accumulator
                value = self.r_accumulator
                #self.r_program_counter += 1
                return value
            case AddressingMode.RELATIVE:
                # TODO: Verify this is correct
                value = self.r_program_counter
                self.r_program_counter += 1
                return value
    
    def value_to_status(self, value):
        for i, f in enumerate(self.r_status):
            self.r_status[f] = value & (1 << i) != 0
    
    def status_to_value(self):
        raise NotImplementedError


    def stack_pop(self) -> np.uint8:
        self.r_stack_pointer += np.uint8(1)
        return self.ram.read(np.uint16(0x0100) + np.uint16(self.r_stack_pointer))

    def stack_pop_u16(self) -> np.uint16:
        lo = np.uint16(self.stack_pop())
        hi = np.uint16(self.stack_pop())

        return np.uint16(hi << 8 | lo)

    def stack_push(self, data: np.uint8):
        self.ram.write(np.uint16(0x0100) + np.uint16(self.r_stack_pointer), data)
        self.r_stack_pointer -= np.uint8(1)

    def stack_push_u16(self, data: np.uint16):
        lo = np.uint8(data & 0xFF)
        hi = np.uint8(data >> 8)
        self.stack_push(hi)
        self.stack_push(lo)

    def update_zero_and_negative_flags(self, register):
        self.r_status["flag_Z"] = True if register == 0 else False
        self.r_status["flag_N"] = True if register & 0b1000_0000 != 0 else False

    def print_system(self) -> None:
        print(
            f"PC: 0x{self.r_program_counter:04x}, "
            f"SP: 0x{self.r_stack_pointer:02x}, "
            f"A: 0x{self.r_accumulator:02x}, "
            f"X: 0x{self.r_index_X:02x}, "
            f"Y: 0x{self.r_index_Y:02x}, "
            f"{[int(self.r_status[k]) for k in self.r_status.keys()][::-1]}"
        )
 
    # ----------------------------------------------------------------
    # Implementation of OpCodes
    # ----------------------------------------------------------------

    def ADC(self, mode: AddressingMode):
        print(f'ADC - PC: {self.r_program_counter}')
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        a = np.uint16(self.r_accumulator)
        m = np.uint16(value)
        c = np.uint16(self.r_status["flag_C"])

        print(f'{a}, {m}, {c}')

        result = a + m + c

        self.r_accumulator = np.uint8(result)

        # Setting Flags
        self.r_status["flag_C"] = True if result > 255 else False
        self.r_status["flag_V"] = True if (~(a ^ m) & (a ^ result)) & 0x80 else False
        self.update_zero_and_negative_flags(self.r_accumulator)

    def AND(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        self.r_accumulator &= value
        self.update_zero_and_negative_flags(self.r_accumulator)

    def ASL(self, mode: AddressingMode):
        if mode == AddressingMode.ACCUMULATOR:
            value = self.get_operand_address(mode)
        else:
            addr = self.get_operand_address(mode)
            value = self.ram.read(addr)
        shifted = value << 1

        self.r_status["flag_C"] = True if shifted > 255 else False

        if mode == AddressingMode.ACCUMULATOR:
            self.r_accumulator = np.uint8(shifted)
        else:
            self.ram.write(addr, np.uint8(shifted))
        self.update_zero_and_negative_flags(shifted)

    def BCC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status["flag_C"] == False:
            self.r_program_counter += np.int8(value)

    def BCS(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status["flag_C"]:
            self.r_program_counter += np.int8(value)

    def BEQ(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status["flag_Z"]:
            self.r_program_counter += np.int8(value) # + np.uint8(1)

    def BIT(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = self.r_accumulator & value

        self.r_status["flag_Z"] = True if result == 0 else False
        self.r_status["flag_V"] = bool(value & 0b0100_0000)
        self.r_status["flag_N"] = bool(value & 0b1000_0000)

    def BMI(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status["flag_N"]:
            print('flag N')
            self.r_program_counter += np.int8(value)

    def BNE(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status["flag_Z"] == False:
            self.r_program_counter += np.int8(value)

    def BPL(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status["flag_N"] == False:
            self.r_program_counter += np.int8(value)

    def BRK(self, mode: AddressingMode):
        print('BREAK')
        self.break_flag = True
        self.r_status['flag_B0'] = True
        self.r_program_counter += 1

    def BVC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status["flag_V"] == False:
            self.r_program_counter += np.int8(value)

    def BVS(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        if self.r_status["flag_V"]:
            self.r_program_counter += np.int8(value)

    def CLC(self, mode: AddressingMode):
        self.r_status["flag_C"] = False

    def CLD(self, mode: AddressingMode):
        self.r_status["flag_D"] = False

    def CLI(self, mode: AddressingMode):
        self.r_status["flag_I"] = False

    def CLV(self, mode: AddressingMode):
        self.r_status["flag_V"] = False

    def CMP(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = np.uint8(self.r_accumulator) - value

        #print(f'r_a: {self.r_accumulator}, value: {value}')
        #print(f'The result is {result}')

        self.r_status["flag_C"] = True if self.r_accumulator >= value else False
        self.r_status["flag_Z"] = True if self.r_accumulator == value else False
        self.r_status["flag_N"] = bool(result & 0b1000_0000)

    def CPX(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = np.uint8(self.r_index_X) - value

        self.r_status["flag_C"] = True if self.r_index_X >= value else False
        self.r_status["flag_Z"] = True if self.r_index_X == value else False
        self.r_status["flag_N"] = bool(result & 0b1000_0000)

    def CPY(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = np.uint8(self.r_index_Y) - value

        self.r_status["flag_C"] = True if self.r_index_Y >= value else False
        self.r_status["flag_Z"] = True if self.r_index_Y == value else False
        self.r_status["flag_N"] = bool(result & 0b1000_0000)

    def DEC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = value - np.uint8(1)
        self.ram.write(addr, result)

        self.r_status["flag_Z"] = True if result == 0 else False
        self.r_status["flag_N"] = bool(result >> 7)

    def DEX(self, mode: AddressingMode):
        self.r_index_X -= np.uint8(1)
        self.update_zero_and_negative_flags(self.r_index_X)

    def DEY(self, mode: AddressingMode):
        self.r_index_Y -= np.uint8(1)
        self.update_zero_and_negative_flags(self.r_index_Y)

    def EOR(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        print(value)
        self.r_accumulator ^= value

        self.update_zero_and_negative_flags(self.r_accumulator)

    def INC(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        result = value + np.uint8(1)
        self.ram.write(addr, result)

        self.r_status["flag_Z"] = True if result == 0 else False
        self.r_status["flag_N"] = bool(result >> 7)

    def INX(self, mode: AddressingMode):
        self.r_index_X = np.uint8(self.r_index_X) + np.uint8(1)
        self.update_zero_and_negative_flags(self.r_index_X)

    def INY(self, mode: AddressingMode):
        self.r_index_Y = np.uint8(self.r_index_Y) + np.uint8(1)
        self.update_zero_and_negative_flags(self.r_index_Y)

    def JMP(self, mode: AddressingMode):
        # TODO: There is a bug which needs implementing in this function
        addr = self.get_operand_address(mode)
        self.r_program_counter = addr

    def JSR(self, mode: AddressingMode):
        self.stack_push_u16(
            self.r_program_counter + np.uint8(1)
        )  # For some reason the ebook puts this as + 2 - 1 (ie + 1)
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

    def LSR_accumulator(self, mode: AddressingMode):
        value = self.r_accumulator
        # Setting Flags
        if value & np.uint8(1) == 1:
            self.r_status['flag_C'] = True
        else:
            self.r_status['flag_C'] = False
        value = value >> 1

        self.r_accumulator = value
        self.update_zero_and_negative_flags(self.r_accumulator)

    def LSR(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        # Setting Flags
        if value & np.uint8(1) == 1:
            self.r_status['flag_C'] = True
        else:
            self.r_status['flag_C'] = False
        value = value >> 1
        self.ram.write(addr, value)
        self.update_zero_and_negative_flags(value)
        
    def NOP(self, mode: AddressingMode):
        pass

    def ORA(self, mode: AddressingMode):
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
        self.r_accumulator |= value

        self.update_zero_and_negative_flags(self.r_accumulator)

    def PHA(self, mode: AddressingMode):
        self.stack_push(self.r_accumulator)
        #self.update_zero_and_negative_flags(self.r_accumulator)

    def PHP(self, mode: AddressingMode):
        raise NotImplementedError

    def PLA(self, mode: AddressingMode):
        self.r_accumulator = self.stack_pop()
        self.update_zero_and_negative_flags(self.r_accumulator)

    def PLP(self, mode: AddressingMode):
        value = self.stack_pop()
        self.value_to_status(value)

    def ROL(self, mode: AddressingMode):
        #TODO: Probably not the correct implementation
        addr = self.get_operand_address(mode) 
        value = self.ram.read(addr)
        old_carry = self.r_status['flag_C']

        if value >> 7 == 1:
            self.r_status['flag_N'] == True
        else:
            self.r_status['flag_N'] == False

        value = value << 1
        if old_carry:
            value = value | 1
        self.ram.write(addr, value)

    def ROR(self, mode: AddressingMode):
        raise NotImplementedError

    def RTI(self, mode: AddressingMode):
        raise NotImplementedError

    def RTS(self, mode: AddressingMode):
        value = self.stack_pop_u16()
        self.r_program_counter = value + np.uint8(1)

    def SBC(self, mode: AddressingMode):
        print('SBC performed')
        # A-B = A + (-B) and -B = !B + 1
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)

        a = self.r_accumulator
        b = np.uint8(value)

        result = a + (~b + self.r_status['flag_C'])

        self.r_accumulator = np.uint8(result)

        # Setting Flags
        self.r_status["flag_C"] = True if result > 255 else False
        self.r_status["flag_V"] = True if (~(a ^ b) & (a ^ result)) & 0x80 else False
        self.update_zero_and_negative_flags(self.r_accumulator)

    def SEC(self, mode: AddressingMode):
        self.r_status["flag_C"] = True

    def SED(self, mode: AddressingMode):
        self.r_status["flag_D"] = True

    def SEI(self, mode: AddressingMode):
        self.r_status["flag_I"] = True

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
        self.r_stack_pointer = self.r_index_X

    def TYA(self, mode: AddressingMode):
        raise NotImplementedError
