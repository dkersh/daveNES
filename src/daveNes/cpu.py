# import pygame
import time
from enum import Enum, IntFlag, auto

import numpy as np

from daveNes.bus import Bus
from daveNes.opcodes import opcode_table
from program import Program


class StatusRegister(IntFlag):
    C = 0x01
    Z = 0x02
    I = 0x04
    D = 0x08
    B0 = 0x10
    B1 = 0x20
    V = 0x40
    N = 0x80


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
        self.r_status: StatusRegister = StatusRegister.B1
        self.memory = None

        # imported from opcodes
        self.lookup_table = opcode_table

    def connect_to_bus(self) -> None:
        """Initiate the Bus and attach to CPU object. Could probably be made part of the init method."""
        self.bus = Bus()

    def load_program(self, program: Program) -> None:
        """Load program into memory.

        Args:
            program (Program): Target program object to load into memory.
        """
        for i, val in enumerate(program.program):
            self.bus.write(0x0600 + i, val)
        self.bus.write_u16(
            0xFFFC, 0x0600
        )  # Write the start of the program to addr 0xFFFC
        # self.bus.write_u16(0x07FE, 0x0600)
        self.reset()

    def step_program(self) -> None:
        """Step through the program, by reading from memory, executing the instruction, and then
        incrementing the program counter (offloaded to the addressing modes)

        This method has been modified to run the snake program, requiring a random value to be written to memory
        address $00FE.
        """

        opcode = self.bus.read(self.r_program_counter)
        # print(f'{hex(opcode)}, {self.lookup_table[opcode][3]}')
        self.print_system()

        self.r_program_counter += 1
        f = self.lookup_table[int(opcode)].operation
        a = self.lookup_table[int(opcode)].addressing_mode
        f(self, a)  # run the opcode with the specified addressing mode

    """
    def run_program(self) -> None:
        while True:
            self.step_program()

            if self.break_flag:
                print('program ending')
                break
    """

    def run_program(self) -> None:
        """Execute the program loaded into memory. This method is more elaborate
        as due to the snake game, we wish to render a region of memory to the screen.
        We do this using the pygame library.
        """

        while True:
            self.step_program()

            if self.r_status["flag_B0"] == True:
                break

    def reset(self) -> None:
        """Reset the CPU, setting all registers and status to default."""
        self.r_program_counter = self.bus.read_u16(0xFFFC)  # 0xFFFC
        self.r_stack_pointer = np.uint8(0xFF)
        self.r_accumulator = np.uint8(0)
        self.r_index_X = np.uint8(0)
        self.r_index_Y = np.uint8(0)
        self.r_status = dict.fromkeys(self.r_status, False)
        ###
        self.r_status["flag_B0"] = False
        self.r_status["flag_B1"] = True
        ###

    def get_operand_address(self, mode: AddressingMode) -> np.uint8 | np.uint16:
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
                return base + np.uint16(
                    self.r_index_X
                )  # Wrapping Add (may throw overflow exception)

            case AddressingMode.ABSOLUTE_Y:
                base = self.bus.read_u16(self.r_program_counter)
                self.r_program_counter += 2
                return base + np.uint16(
                    self.r_index_Y
                )  # Wrapping Add (may throw overflow exception)

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
                hi = self.bus.read(
                    (base + np.uint8(1))
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

    def print_system(self) -> None:
        print(
            f"PC: 0x{self.r_program_counter:04x}, "
            f"SP: 0x{self.r_stack_pointer:02x}, "
            f"A: 0x{self.r_accumulator:02x}, "
            f"X: 0x{self.r_index_X:02x}, "
            f"Y: 0x{self.r_index_Y:02x}, "
            f"{self.status_to_value()}",
        )
