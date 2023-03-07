import matplotlib.pyplot as plt
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
        hi = np.uint16(self.read(addr + 1))

        return np.uint16((hi << 8) | lo)

    def write_u16(self, addr: np.uint16, data: np.uint16) -> bool:
        try:
            lo = np.uint8(data & 0xFF)
            hi = np.uint8(data >> 8)
            self.write(addr, lo)
            self.write(addr + 1, hi)
        except:
            return False
        return True

    def load_program(self, p: Program):
        self.memory[0x0600 : 0x0600 + len(p.program)] = p.program

        return 0x0600

    def visualise_memory(self):
        display = np.zeros((32, 32))
        xx, yy = np.meshgrid(range(32), range(32))
        for i in range(0x0200, 0x05FF + 1):
            ind = i - 0x0200
            x, y = xx.ravel()[ind], yy.ravel()[ind]
            display[y, x] = self.memory[i]
        plt.figure()
        plt.imshow(display)
        plt.axis(False)
        plt.show()
