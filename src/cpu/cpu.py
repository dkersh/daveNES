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

from .opcodes import MOS6502_OpCodes
from .bus import Bus

class MOS6502:
    def __init__(self) -> None:
        """Class which emulates the behaviour of the MOS6502 processor, notably used
        inside the Nintendo Entertainment System.
        """

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
        self.memory = None

        # imported from opcodes
        self.opcodes = MOS6502_OpCodes(self)
        self.lookup_table = self.opcodes.lookup_table

    def connect_to_bus(self) -> None:
        """Initiate the Bus and attach to CPU object. Could probably be made part of the init method.
        """
        self.bus = Bus()

    def load_program(self, program: Program) -> None:
        """Load program into memory.

        Args:
            program (Program): Target program object to load into memory.
        """
        for i, val in enumerate(program.program):
            self.bus.write(0x0600 + i, val)
        self.bus.write_u16(0xFFFC, 0x0600)  # Write the start of the program to addr 0xFFFC
        #self.bus.write_u16(0x07FE, 0x0600)
        self.reset()

    def step_program(self) -> None:
        """Step through the program, by reading from memory, executing the instruction, and then
        incrementing the program counter (offloaded to the addressing modes)

        This method has been modified to run the snake program, requiring a random value to be written to memory
        address $00FE.
        """

        # Random value required for Snake program
        # self.bus.write(0xfe, np.random.randint(1, 16, dtype=np.uint8)) # random value to memory

        opcode = self.bus.read(self.r_program_counter)
        #print(f'{hex(opcode)}, {self.lookup_table[opcode][3]}')
        self.print_system()

        self.r_program_counter += 1
        f = self.lookup_table[opcode][0]
        a = self.lookup_table[opcode][2]
        f(a) # run the opcode with the specified addressing mode

    '''
    def run_program(self) -> None:
        while True:
            self.step_program()

            if self.break_flag:
                print('program ending')
                break
    '''
    
    def run_program(self) -> None:
        """Execute the program loaded into memory. This method is more elaborate
        as due to the snake game, we wish to render a region of memory to the screen.
        We do this using the pygame library.
        """

        # For the snake program
        pygame.init()
        # Speed up pygame
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        screen = pygame.display.set_mode((640, 640))
        data = np.zeros(32*32)
        pygame.display.update()

        while True:
            self.step_program()
            
            # This is Explicitly for the snake program
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        self.r_status["flag_B0"] = True
                        break
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_UP:
                                self.bus.write(0xff, 0x77)
                                #print('UP PRESSED')
                            case pygame.K_RIGHT:
                                self.bus.write(0xff, 0x61)
                                #print('RIGHT PRESSED')
                            case pygame.K_LEFT:
                                self.bus.write(0xff, 0x64)
                                #print('LEFT PRESSED')
                            case pygame.K_DOWN:
                                self.bus.write(0xff, 0x73)
                                #print('DOWN PRESSED')

            # Render to screen if there's a change between the data var and the appropriate memory address.
            if np.all(data == self.bus.wram.memory[0x0200:0x05FF+1]) == False:
                time.sleep(0.05)
                data = np.copy(self.bus.wram.memory[0x0200:0x05FF+1])
                # Change background to white
                data_c = np.copy(data)
                data_c[data_c == 0] = 255
                #
                data_r = np.reshape(data_c, (32, 32))
                surf = pygame.surfarray.make_surface(data_r)
                scaled_surf = pygame.transform.scale(surf, (640, 640))
                screen.blit(scaled_surf, (0, 0))
                screen.blit(pygame.transform.rotate(screen, -90), (0, 0))
                #
                # add program status
                #
                font = pygame.font.Font(None, 20)
                text = (f"PC: 0x{self.r_program_counter:04x}, "
                    f"SP: 0x{self.r_stack_pointer:02x}, "
                    f"A: 0x{self.r_accumulator:02x}, "
                    f"X: 0x{self.r_index_X:02x}, "
                    f"Y: 0x{self.r_index_Y:02x}, "
                    f"{[int(self.r_status[k]) for k in self.r_status.keys()][::-1]}")
                text_surface = font.render(text, True, (255, 0, 0))
                text_rect = text_surface.get_rect()
                text_rect.topleft = (25, 25)
                screen.blit(text_surface, text_rect)
                #
                #
                #

                pygame.display.update()
                
            if self.r_status["flag_B0"] == True:
                break
        
        pygame.quit()
    

    def reset(self) -> None:
        """Reset the CPU, setting all registers and status to default.
        """
        self.r_program_counter = self.bus.read_u16(0xFFFC) #0xFFFC
        self.r_stack_pointer = np.uint8(0xFF)
        self.r_accumulator = np.uint8(0)
        self.r_index_X = np.uint8(0)
        self.r_index_Y = np.uint8(0)
        self.r_status = dict.fromkeys(self.r_status, False)
        ###
        self.r_status["flag_B0"] = False
        self.r_status["flag_B1"] = True
        ###

    def get_operand_address(self, mode: AddressingMode) -> np.uint16:
        """Return the address from a respective operation based on the addressing mode used.

        Args:
            mode (AddressingMode): Addressing Mode identified in the op-code

        Returns:
            np.uint16: Address returned as a result of the addressingmode specified.
        """

        match mode:
            case AddressingMode.IMMEDIATE:
                value = self.r_program_counter
                self.r_program_counter += 1
                return value

            case AddressingMode.ZERO_PAGE:
                value = self.bus.read(self.r_program_counter)
                self.r_program_counter += 1
                return value

            case AddressingMode.ZERO_PAGE_X:
                pos = self.bus.read(self.r_program_counter)
                value = (
                    pos + self.r_index_X
                )  # Wrapping Add (may throw overflow exception)
                self.r_program_counter += 1
                return np.uint8(value)

            case AddressingMode.ZERO_PAGE_Y:
                pos = self.bus.read(self.r_program_counter)
                value = (
                    pos + self.r_index_Y
                )  # Wrapping Add (may throw overflow exception)
                self.r_program_counter += 1
                return np.uint8(value)

            case AddressingMode.ABSOLUTE:
                value = self.bus.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                return value

            case AddressingMode.ABSOLUTE_X:
                base = self.bus.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                return base + np.uint16(self.r_index_X) # Wrapping Add (may throw overflow exception)

            case AddressingMode.ABSOLUTE_Y:
                base = self.bus.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                return base + np.uint16(self.r_index_Y)  # Wrapping Add (may throw overflow exception)

            case AddressingMode.INDIRECT:
                base = self.bus.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                base = self.bus.read_u16(base)
                self.r_program_counter += 2
                return base

            case AddressingMode.INDIRECT_X:
                base = self.bus.read(self.r_program_counter)
                self.r_program_counter += 1
                ptr = base + np.uint8(self.r_index_X)
                lo = self.bus.read(ptr)
                hi = self.bus.read(ptr + np.uint8(1))

                return hi << 8 | lo

            case AddressingMode.INDIRECT_Y:
                base = self.bus.read(self.r_program_counter)
                self.r_program_counter += 1

                lo = self.bus.read(base)
                hi = self.bus.read((base + np.uint8(1))
                )  # Wrapping Add (may throw overflow exception)
                deref_base = hi << 8 | lo

                return np.uint16(deref_base) + np.uint16(
                    self.r_index_Y
                )  # Wrapping Add (may throw overflow exception)

            case AddressingMode.IMPLICIT:
                # TODO: Technically, this should be trivial.
                raise NotImplementedError
            
            case AddressingMode.ACCUMULATOR:
                value = self.r_accumulator
                return value
            
            case AddressingMode.RELATIVE:
                value = self.r_program_counter
                self.r_program_counter += 1
                return value
    
    def value_to_status(self, value: np.uint8) -> None:
        """Convert a number into the booleans for the status register; useful for testing.

        Args:
            value (np.uint8): status number
        """
        for i, f in enumerate(self.r_status):
            self.r_status[f] = value & (1 << i) != 0
    
    def status_to_value(self) -> np.uint8:
        """Convert the status register (a dict) to a usigned 8 bit integer.

        Returns:
            np.uint8: integer representation of the status register
        """
        return np.uint8(int(''.join(str(int(self.r_status[k])) for k in self.r_status.keys())[::-1], 2))

    def stack_pop(self) -> np.uint8:
        self.r_stack_pointer += np.uint8(1)
        return self.bus.read(np.uint16(0x0100) + np.uint16(self.r_stack_pointer))

    def stack_pop_u16(self) -> np.uint16:
        lo = np.uint16(self.stack_pop())
        hi = np.uint16(self.stack_pop())

        return np.uint16(hi << 8 | lo)

    def stack_push(self, data: np.uint8) -> None:
        self.bus.write(np.uint16(0x0100) + np.uint16(self.r_stack_pointer), data)
        self.r_stack_pointer -= np.uint8(1)

    def stack_push_u16(self, data: np.uint16) -> None:
        lo = np.uint8(data & 0xFF)
        hi = np.uint8(data >> 8)
        self.stack_push(hi)
        self.stack_push(lo)

    def update_zero_and_negative_flags(self, register: np.uint8) -> None:
        """Update the zero and negative flags of the status register based on the value of the
        input register. Useful for abbreviated the OpCode methods.

        Args:
            register (np.uint8): register to be tested.
        """
        self.r_status["flag_Z"] = True if register == 0 else False
        self.r_status["flag_N"] = True if register & 0b1000_0000 != 0 else False

    def print_system(self) -> None:
        print(
            f"PC: 0x{self.r_program_counter:04x}, "
            f"SP: 0x{self.r_stack_pointer:02x}, "
            f"A: 0x{self.r_accumulator:02x}, "
            f"X: 0x{self.r_index_X:02x}, "
            f"Y: 0x{self.r_index_Y:02x}, "
            f"{self.status_to_value()}",
        )