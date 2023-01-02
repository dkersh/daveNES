import numpy as np

class Program:
    def __init__(self, program) -> None:
            self.program = program
            self.program = np.array([np.uint8(int(x, base=16)) for x in self.program]) # Convert values from hex to uint8
            self.program_counter = 0

    @classmethod
    def from_file(cls, filename: str):
        with open(filename, 'rb') as f:
            return cls(f.read().split())

    @classmethod
    def from_array(cls, array: np.ndarray):
        return cls(array)

    def value(self):
        ind = self.program_counter
        self.program_counter += 1
        return self.program[ind]

    def rewind(self):
        self.program_counter = 0