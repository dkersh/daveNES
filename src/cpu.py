import numpy as np
from program import Program

class MOS6502:
    def __init__(self) -> None:
        # The Rgisters
        self.r_program_counter = np.uint16(0)
        self.r_stack_pointer = np.uint8(0)
        self.r_accumulator = np.uint8(0)
        self.r_index_X = np.uint8(0)
        self.r_index_Y = np.uint8(0)
        self.r_status = np.uint8(0) # NV B*B* DIZC, B* == Break

    def run_program(self, program: Program) -> None:

        while True:
            opcode = program.value() # Code from program
            print(hex(opcode))
            self.r_program_counter += 1
            match opcode:
                case 0xA9:
                    self.r_accumulator = program.value()
                    self.r_program_counter += 1
                    if self.r_accumulator == 0:
                        self.r_status = self.r_status | 0b0000_0010
                    else:
                        self.r_status = self.r_status & 0b1111_1101

                    if self.r_accumulator & 0b1000_0000 != 0:
                        self.r_status = self.r_status | 0b1000_0000
                    else:
                        self.r_status = self.r_status & 0b0111_1111

                case 0xAA:
                    self.r_index_X = self.r_accumulator
                    self.r_program_counter += 1
                    if self.r_index_X == 0:
                        self.r_status = self.r_status | 0b0000_0010
                    else:
                        self.r_status = self.r_status & 0b1111_1101

                    if self.r_index_X & 0b1000_0000 != 0:
                        self.r_status = self.r_status | 0b1000_0000
                    else:
                        self.r_status = self.r_status & 0b0111_1111

                case 0x00:
                    # Force Interupt
                    print('Exiting Program')
                    break

class Memory:
    def __init__(self):
        self.memory = np.zeros(0xFFFF, dtype=np.uint8)

    def read(self, addr: np.uint16) -> np.uint8:
        return self.memory[addr]

    def write(self, addr: np.uint16, data: np.uint8) -> bool:
        try:
            self.memory[addr] = data
        except:
            return False
        return True

    def read_u16(self, addr: np.uint16) -> np.uint16:
        lo = np.uint16(self.read(addr))
        hi = np.uint16(self.read(addr+1))

        return (hi << 8) | lo

    def write_u16(self, addr: np.uint16, data: np.uint16) -> bool:
        try:
            lo = np.uint8(data & 0xff) 
            hi = np.uint8(data >> 8)
            self.write(addr, lo)
            self.write(addr+1, hi)
        except:
            return False
        return True

    def load_program(self, p: Program):
        self.memory[0x8000:0x8000+len(p.program)] = p.program

        return 0x8000