import numpy as np
from memory import Memory

class Bus:
    def __init__(self) -> None:
        """Main for component interfacing.
        TODO: Implement memory mirroring for RAM.
        """
        self.wram = Memory()
        self.vram = None

    def write(self, addr: np.uint16, value: np.uint8) -> None:
        self.wram.write(addr, value)
    
    def read(self, addr: np.uint16) -> np.uint8:
        return self.wram.read(addr)
    
    def write_u16(self, addr: np.uint16, value: np.uint16) -> None:
        self.wram.write_u16(addr, value)
    
    def read_u16(self, addr: np.uint16) -> np.uint16:
        return self.wram.read_u16(addr)