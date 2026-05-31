from enum import Enum, auto
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from daveNes.cpu import MOS6502


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


def am_immediate(cpu: MOS6502) -> np.uint16:
    target_addr = cpu.r_program_counter
    cpu.r_program_counter += 1

    return target_addr


def am_zero_page(cpu: MOS6502) -> np.uint16:
    zero_page_offset = cpu.bus.read(cpu.r_program_counter)
    target_addr = np.uint16(zero_page_offset)
    cpu.r_program_counter += 1

    return target_addr


def am_zero_page_x(cpu: MOS6502) -> np.uint16:
    pos = cpu.bus.read(cpu.r_program_counter)
    target_addr = np.uint16(pos + cpu.r_index_X)

    cpu.r_program_counter += 1

    return target_addr


def am_zero_page_y(cpu: MOS6502) -> np.uint16:
    pos = cpu.bus.read(cpu.r_program_counter)
    target_addr = np.uint16(pos + cpu.r_index_Y)

    cpu.r_program_counter += 1

    return target_addr


def am_absolute(cpu: MOS6502) -> np.uint16:
    target_addr = cpu.bus.read_u16(cpu.r_program_counter)
    cpu.r_program_counter += 2

    return target_addr


def am_absolute_x(cpu: MOS6502) -> np.uint16:
    pos = cpu.bus.read_u16(cpu.r_program_counter)
    target_addr = np.uint16(pos + cpu.r_index_X)
    cpu.r_program_counter += 2

    return target_addr


def am_absolute_y(cpu: MOS6502) -> np.uint16:
    pos = cpu.bus.read_u16(cpu.r_program_counter)
    target_addr = np.uint16(pos + cpu.r_index_Y)
    cpu.r_program_counter += 2

    return target_addr


def am_indirect(cpu: MOS6502) -> np.uint16:
    base = cpu.bus.read_u16(cpu.r_program_counter)
    cpu.r_program_counter += 2
    base = cpu.bus.read_u16(base)
    cpu.r_program_counter += 2

    return base


def am_indirect_x(cpu: MOS6502) -> np.uint16:
    base = cpu.bus.read(cpu.r_program_counter)
    cpu.r_program_counter += 1
    ptr = base + cpu.r_index_X
    lo = cpu.bus.read(ptr)
    hi = cpu.bus.read(ptr + np.uint8(1))

    return np.uint16(hi << 8 | lo)


def am_indirect_y(cpu: MOS6502) -> np.uint16:
    base = cpu.bus.read(cpu.r_program_counter)
    cpu.r_program_counter += 1

    lo = cpu.bus.read(base)
    hi = cpu.bus.read(base + np.uint8(1))
    deref_base = hi << 8 | lo

    target_addr = np.uint16(deref_base) + np.uint16(cpu.r_index_Y)

    return target_addr


def am_implicit(cpu: MOS6502) -> np.uint16:
    raise NotImplementedError


def am_accumulator(cpu: MOS6502) -> np.uint16:
    target_addr = np.uint16(cpu.r_accumulator)

    return target_addr


def am_relative(cpu: MOS6502) -> np.uint16:
    # TODO: This is the same as immediate because my implementation of its dependents is wrong.
    target_addr = cpu.r_program_counter
    cpu.r_program_counter += 1

    return target_addr


addressing_mode_lookup_table = {
    AddressingMode.IMMEDIATE: am_immediate,
    AddressingMode.ZERO_PAGE: am_zero_page,
    AddressingMode.ZERO_PAGE_X: am_zero_page_x,
    AddressingMode.ZERO_PAGE_Y: am_zero_page_y,
    AddressingMode.ABSOLUTE: am_absolute,
    AddressingMode.ABSOLUTE_X: am_absolute_x,
    AddressingMode.ABSOLUTE_Y: am_absolute_y,
    AddressingMode.INDIRECT: am_indirect,
    AddressingMode.INDIRECT_X: am_indirect_x,
    AddressingMode.INDIRECT_Y: am_indirect_y,
    AddressingMode.IMPLICIT: am_implicit,
    AddressingMode.ACCUMULATOR: am_accumulator,
    AddressingMode.RELATIVE: am_relative,
}
