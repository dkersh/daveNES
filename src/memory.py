import numpy as np
from program import Program

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