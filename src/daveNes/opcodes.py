from dataclasses import dataclass
from typing import TYPE_CHECKING

from daveNes.cpu import AddressingMode, StatusRegister

if TYPE_CHECKING:
    from daveNes.cpu import MOS6502
from enum import Enum, IntFlag, auto
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class Instruction:
    name: str
    cycle: int
    addressing_mode: AddressingMode | None
    operation: Callable


# Helper Functions to Tidy Things up
def set_status_flag(status_register: StatusRegister, flag: IntFlag) -> StatusRegister:
    return status_register | flag


def clear_status_flag(status_register: StatusRegister, flag: IntFlag) -> StatusRegister:
    return status_register & ~flag


def update_zero_and_negative_flags(cpu: MOS6502, register: np.uint8) -> None:
    """Update the zero and negative flags of the status register based on the value of the
    input register. Useful for abbreviated the OpCode methods.

    Args:
        register (np.uint8): register to be tested.
    """
    cpu.r_status = (
        set_status_flag(cpu.r_status, StatusRegister.Z)
        if register == 0
        else clear_status_flag(cpu.r_status, StatusRegister.Z)
    )
    cpu.r_status = (
        set_status_flag(cpu.r_status, StatusRegister.N)
        if register & 0b1000_0000 != 0
        else clear_status_flag(cpu.r_status, StatusRegister.N)
    )


# Implementations of each OpCode
def ADC(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    a = np.uint16(cpu.r_accumulator)
    m = np.uint16(value)
    c = np.uint16(cpu.r_status & StatusRegister.C)

    result = a + m + c

    cpu.r_accumulator = np.uint8(result)

    # Setting Flags
    cpu.r_status = (
        set_status_flag(cpu.r_status, StatusRegister.C)
        if result > 255
        else clear_status_flag(cpu.r_status, StatusRegister.C)
    )
    cpu.r_status = (
        set_status_flag(cpu.r_status, StatusRegister.V)
        if (~(a ^ m) & (a ^ result)) & 0x80
        else clear_status_flag(cpu.r_status, StatusRegister.V)
    )
    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def AND(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    cpu.r_accumulator &= value
    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def ASL(cpu: MOS6502, mode: AddressingMode):
    # TODO: Should probably split this up into accumulator / non accumulator
    if mode == AddressingMode.ACCUMULATOR:
        value = cpu.get_operand_address(mode)
    else:
        addr = cpu.get_operand_address(mode)
        value = cpu.bus.read(addr)
    shifted = value << 1

    cpu.r_status = set_status_flag(cpu.r_status, StatusRegister.C, shifted > 255)

    if mode == AddressingMode.ACCUMULATOR:
        cpu.r_accumulator = np.uint8(shifted)
        update_zero_and_negative_flags(cpu, np.uint8(shifted))
        if cpu.r_accumulator == 0:
            cpu.r_status["flag_Z"] = True
    else:
        cpu.bus.write(addr, np.uint8(shifted))
        update_zero_and_negative_flags(cpu, np.uint8(shifted))


def BCC(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    if cpu.r_status["flag_C"] == False:
        cpu.r_program_counter += np.int8(value)


def BCS(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    if cpu.r_status["flag_C"]:
        cpu.r_program_counter += np.int8(value)


def BEQ(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    if cpu.r_status["flag_Z"]:
        cpu.r_program_counter += np.int8(value)  # + np.uint8(1)


def BIT(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)
    result = cpu.r_accumulator & value

    cpu.r_status["flag_Z"] = True if result == 0 else False
    cpu.r_status["flag_V"] = bool(value & 0b0100_0000)
    cpu.r_status["flag_N"] = bool(value & 0b1000_0000)


def BMI(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    if cpu.r_status["flag_N"]:
        print("flag N")
        cpu.r_program_counter += np.int8(value)


def BNE(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    if cpu.r_status["flag_Z"] == False:
        cpu.r_program_counter += np.int8(value)


def BPL(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    if cpu.r_status["flag_N"] == False:
        cpu.r_program_counter += np.int8(value)


def BRK(cpu: MOS6502):
    print("BREAK")
    cpu.r_status["flag_B0"] = True
    cpu.r_program_counter += 1


def BVC(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    if cpu.r_status["flag_V"] == False:
        cpu.r_program_counter += np.int8(value)


def BVS(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    if cpu.r_status["flag_V"]:
        cpu.r_program_counter += np.int8(value)


def CLC(cpu: MOS6502):
    cpu.r_status["flag_C"] = False


def CLD(cpu: MOS6502):
    cpu.r_status["flag_D"] = False


def CLI(cpu: MOS6502):
    cpu.r_status["flag_I"] = False


def CLV(cpu: MOS6502):
    cpu.r_status["flag_V"] = False


def CMP(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)
    result = np.uint8(cpu.r_accumulator) - value

    # print(f'r_a: {cpu.r_accumulator}, value: {value}')
    # print(f'The result is {result}')

    cpu.r_status["flag_C"] = True if cpu.r_accumulator >= value else False
    cpu.r_status["flag_Z"] = True if cpu.r_accumulator == value else False
    cpu.r_status["flag_N"] = bool(result & 0b1000_0000)


def CPX(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)
    result = np.uint8(cpu.r_index_X) - value

    cpu.r_status["flag_C"] = True if cpu.r_index_X >= value else False
    cpu.r_status["flag_Z"] = True if cpu.r_index_X == value else False
    cpu.r_status["flag_N"] = bool(result & 0b1000_0000)


def CPY(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)
    result = np.uint8(cpu.r_index_Y) - value

    cpu.r_status["flag_C"] = True if cpu.r_index_Y >= value else False
    cpu.r_status["flag_Z"] = True if cpu.r_index_Y == value else False
    cpu.r_status["flag_N"] = bool(result & 0b1000_0000)


def DEC(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)
    result = value - np.uint8(1)
    cpu.bus.write(addr, result)

    cpu.r_status["flag_Z"] = True if result == 0 else False
    cpu.r_status["flag_N"] = bool(result >> 7)


def DEX(cpu: MOS6502, mode: AddressingMode):
    cpu.r_index_X -= np.uint8(1)
    update_zero_and_negative_flags(cpu, cpu.r_index_X)


def DEY(cpu: MOS6502, mode: AddressingMode):
    cpu.r_index_Y -= np.uint8(1)
    update_zero_and_negative_flags(cpu, cpu.r_index_Y)


def EOR(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)
    print(value)
    cpu.r_accumulator ^= value

    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def INC(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)
    result = value + np.uint8(1)
    cpu.bus.write(addr, result)

    cpu.r_status["flag_Z"] = True if result == 0 else False
    cpu.r_status["flag_N"] = bool(result >> 7)


def INX(cpu: MOS6502, mode: AddressingMode):
    cpu.r_index_X = np.uint8(cpu.r_index_X) + np.uint8(1)
    update_zero_and_negative_flags(cpu, cpu.r_index_X)


def INY(cpu: MOS6502, mode: AddressingMode):
    cpu.r_index_Y = np.uint8(cpu.r_index_Y) + np.uint8(1)
    update_zero_and_negative_flags(cpu, cpu.r_index_Y)


def JMP(cpu: MOS6502, mode: AddressingMode):
    # TODO: There is a bug which needs implementing in this function
    addr = cpu.get_operand_address(mode)
    cpu.r_program_counter = addr


def JSR(cpu: MOS6502, mode: AddressingMode):
    cpu.stack_push_u16(
        cpu.r_program_counter + np.uint8(1)
    )  # For some reason the ebook puts this as + 2 - 1 (ie + 1)
    addr = cpu.get_operand_address(mode)
    cpu.r_program_counter = addr


def LDA(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    cpu.r_accumulator = value
    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def LDX(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    cpu.r_index_X = value
    update_zero_and_negative_flags(cpu, cpu.r_index_X)


def LDY(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    cpu.r_index_Y = value
    update_zero_and_negative_flags(cpu, cpu.r_index_Y)


def LSR_accumulator(cpu: MOS6502):
    value = cpu.r_accumulator
    # Setting Flags
    if value & np.uint8(1) == 1:
        cpu.r_status["flag_C"] = True
    else:
        cpu.r_status["flag_C"] = False
    value = value >> 1

    cpu.r_accumulator = value
    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def LSR(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    # Setting Flags
    if value & np.uint8(1) == 1:
        cpu.r_status["flag_C"] = True
    else:
        cpu.r_status["flag_C"] = False
    value = value >> 1
    cpu.bus.write(addr, value)
    update_zero_and_negative_flags(cpu, value)


def NOP(cpu: MOS6502):
    # This is supposed to be a pass
    pass


def ORA(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)
    cpu.r_accumulator |= value

    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def PHA(cpu: MOS6502):
    cpu.stack_push(cpu.r_accumulator)
    # update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def PHP(cpu: MOS6502):
    cpu.stack_push(cpu.status_to_value())


def PLA(cpu: MOS6502):
    cpu.r_accumulator = cpu.stack_pop()
    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def PLP(cpu: MOS6502):
    value = cpu.stack_pop()
    cpu.value_to_status(value)


def ROL(cpu: MOS6502, mode: AddressingMode):
    # Acts different based on Accumulator or Not Addressing Mode
    if mode == AddressingMode.ACCUMULATOR:
        value = cpu.get_operand_address(mode)
        print(f"value: {value}")
    else:
        addr = cpu.get_operand_address(mode)
        value = cpu.bus.read(addr)

    old_carry = cpu.r_status["flag_C"]
    if value >> 7 == 1:
        cpu.r_status["flag_N"] == True
    else:
        cpu.r_status["flag_N"] == False

    value = np.uint8(value << 1)
    print(f"new value: {value}")
    if old_carry:
        value = value | 0b0000_0001
    if mode == AddressingMode.ACCUMULATOR:
        cpu.r_accumulator = value
    else:
        cpu.bus.write(addr, value)


def ROR(cpu: MOS6502, mode: AddressingMode):
    # Acts different based on Accumulator or Not Addressing Mode
    if mode == AddressingMode.ACCUMULATOR:
        value = cpu.get_operand_address(mode)
        print(f"value: {value}")
    else:
        addr = cpu.get_operand_address(mode)
        value = cpu.bus.read(addr)

    old_carry = cpu.r_status["flag_C"]
    if value >> 7 == 1:
        cpu.r_status["flag_N"] == True
    else:
        cpu.r_status["flag_N"] == False

    value = np.uint8(value >> 1)
    if old_carry:
        value = value | 0b1000_0000
    if mode == AddressingMode.ACCUMULATOR:
        cpu.r_accumulator = value
    else:
        cpu.bus.write(addr, value)


def RTI(cpu: MOS6502):
    raise NotImplementedError


def RTS(cpu: MOS6502):
    value = cpu.stack_pop_u16()
    cpu.r_program_counter = value + np.uint8(1)


def SBC(cpu: MOS6502, mode: AddressingMode):
    # A-B = A + (-B) and -B = !B + 1
    addr = cpu.get_operand_address(mode)
    value = cpu.bus.read(addr)

    a = cpu.r_accumulator
    b = np.uint8(value)

    # print(result := a + (~b + cpu.r_status['flag_C']))
    # print(result := a + (~b + (not cpu.r_status['flag_C'])) + 1)
    # print(result := a + (b ^ 0x00FF) + cpu.r_status['flag_C']) # http://forum.6502.org/viewtopic.php?p=37758#p37758
    result = a + (b ^ 0x00FF) + cpu.r_status["flag_C"]

    # print(f'{value =}')
    # print(f'{a =}')
    # print(f'{b =}')
    # print(f'{result =}')
    # print(f'{cpu.r_status["flag_C"] = }')

    # Setting Flags
    cpu.r_status["flag_C"] = True if result > 255 else False
    result = np.uint8(result)
    cpu.r_status["flag_V"] = (
        True if (~(value ^ result) & (a ^ result)) & 0x80 else False
    )
    cpu.r_accumulator = result
    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def SEC(cpu: MOS6502):
    cpu.r_status["flag_C"] = True


def SED(cpu: MOS6502):
    cpu.r_status["flag_D"] = True


def SEI(cpu: MOS6502):
    cpu.r_status["flag_I"] = True


def STA(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    cpu.bus.write(addr, cpu.r_accumulator)


def STX(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    cpu.bus.write(addr, cpu.r_index_X)


def STY(cpu: MOS6502, mode: AddressingMode):
    addr = cpu.get_operand_address(mode)
    cpu.bus.write(addr, cpu.r_index_Y)


def TAX(cpu: MOS6502):
    cpu.r_index_X = cpu.r_accumulator
    update_zero_and_negative_flags(cpu, cpu.r_index_X)


def TAY(cpu: MOS6502):
    cpu.r_index_Y = cpu.r_accumulator
    update_zero_and_negative_flags(cpu, cpu.r_index_Y)


def TSX(cpu: MOS6502):
    cpu.r_index_X = cpu.r_stack_pointer
    update_zero_and_negative_flags(cpu, cpu.r_index_X)


def TXA(cpu: MOS6502):
    cpu.r_accumulator = cpu.r_index_X
    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


def TXS(cpu: MOS6502):
    cpu.r_stack_pointer = cpu.r_index_X


def TYA(cpu: MOS6502):
    cpu.r_accumulator = cpu.r_index_Y
    update_zero_and_negative_flags(cpu, cpu.r_accumulator)


opcode_table: dict[int, Instruction] = {
    0x69: Instruction("ADC", 2, AddressingMode.IMMEDIATE, ADC),
    0x65: Instruction("ADC", 3, AddressingMode.ZERO_PAGE, ADC),
    0x75: Instruction("ADC", 4, AddressingMode.ZERO_PAGE_X, ADC),
    0x6D: Instruction("ADC", 4, AddressingMode.ABSOLUTE, ADC),
    0x7D: Instruction("ADC", 4, AddressingMode.ABSOLUTE_X, ADC),
    0x79: Instruction("ADC", 4, AddressingMode.ABSOLUTE_Y, ADC),
    0x61: Instruction("ADC", 6, AddressingMode.INDIRECT_X, ADC),
    0x71: Instruction("ADC", 5, AddressingMode.INDIRECT_Y, ADC),
    0x29: Instruction("AND", 2, AddressingMode.IMMEDIATE, AND),
    0x25: Instruction("AND", 3, AddressingMode.ZERO_PAGE, AND),
    0x35: Instruction("AND", 4, AddressingMode.ZERO_PAGE_X, AND),
    0x2D: Instruction("AND", 4, AddressingMode.ABSOLUTE, AND),
    0x3D: Instruction("AND", 4, AddressingMode.ABSOLUTE_X, AND),
    0x39: Instruction("AND", 4, AddressingMode.ABSOLUTE_Y, AND),
    0x21: Instruction("AND", 6, AddressingMode.INDIRECT_X, AND),
    0x31: Instruction("AND", 5, AddressingMode.INDIRECT_Y, AND),
    0x0A: Instruction("ASL", 2, AddressingMode.ACCUMULATOR, ASL),
    0x06: Instruction("ASL", 5, AddressingMode.ZERO_PAGE, ASL),
    0x16: Instruction("ASL", 6, AddressingMode.ZERO_PAGE_X, ASL),
    0x0E: Instruction("ASL", 6, AddressingMode.ABSOLUTE, ASL),
    0x1E: Instruction("ASL", 7, AddressingMode.ABSOLUTE_X, ASL),
    0x90: Instruction("BCC", 2, AddressingMode.RELATIVE, BCC),
    0xB0: Instruction("BCS", 2, AddressingMode.RELATIVE, BCS),
    0xF0: Instruction("BEQ", 2, AddressingMode.RELATIVE, BEQ),
    0x24: Instruction("BIT", 3, AddressingMode.ZERO_PAGE, BIT),
    0x2C: Instruction("BIT", 4, AddressingMode.ABSOLUTE, BIT),
    0x30: Instruction("BMI", 2, AddressingMode.RELATIVE, BMI),
    0xD0: Instruction("BNE", 2, AddressingMode.RELATIVE, BNE),
    0x10: Instruction("BPL", 2, AddressingMode.RELATIVE, BPL),
    0x00: Instruction("BRK", 7, None, BRK),
    0x50: Instruction("BVC", 2, AddressingMode.RELATIVE, BVC),
    0x70: Instruction("BVS", 2, AddressingMode.RELATIVE, BVS),
    0x18: Instruction("CLC", 2, None, CLC),
    0xD8: Instruction("CLD", 2, None, CLD),
    0x58: Instruction("CLI", 2, None, CLI),
    0xB8: Instruction("CLV", 2, None, CLV),
    0xC9: Instruction("CMP", 2, AddressingMode.IMMEDIATE, CMP),
    0xC5: Instruction("CMP", 3, AddressingMode.ZERO_PAGE, CMP),
    0xD5: Instruction("CMP", 4, AddressingMode.ZERO_PAGE_X, CMP),
    0xCD: Instruction("CMP", 4, AddressingMode.ABSOLUTE, CMP),
    0xDD: Instruction("CMP", 4, AddressingMode.ABSOLUTE_X, CMP),
    0xD9: Instruction("CMP", 4, AddressingMode.ABSOLUTE_Y, CMP),
    0xC1: Instruction("CMP", 6, AddressingMode.INDIRECT_X, CMP),
    0xD1: Instruction("CMP", 5, AddressingMode.INDIRECT_Y, CMP),
    0xE0: Instruction("CPX", 2, AddressingMode.IMMEDIATE, CPX),
    0xE4: Instruction("CPX", 3, AddressingMode.ZERO_PAGE, CPX),
    0xEC: Instruction("CPX", 4, AddressingMode.ABSOLUTE, CPX),
    0xC0: Instruction("CPY", 2, AddressingMode.IMMEDIATE, CPY),
    0xC4: Instruction("CPY", 3, AddressingMode.ZERO_PAGE, CPY),
    0xCC: Instruction("CPY", 4, AddressingMode.ABSOLUTE, CPY),
    0xC6: Instruction("DEC", 5, AddressingMode.ZERO_PAGE, DEC),
    0xD6: Instruction("DEC", 6, AddressingMode.ZERO_PAGE_X, DEC),
    0xCE: Instruction("DEC", 6, AddressingMode.ABSOLUTE, DEC),
    0xDE: Instruction("DEC", 7, AddressingMode.ABSOLUTE_X, DEC),
    0xCA: Instruction("DEX", 2, None, DEX),
    0x88: Instruction("DEY", 2, None, DEY),
    0x49: Instruction("EOR", 2, AddressingMode.IMMEDIATE, EOR),
    0x45: Instruction("EOR", 3, AddressingMode.ZERO_PAGE, EOR),
    0x55: Instruction("EOR", 4, AddressingMode.ZERO_PAGE_X, EOR),
    0x4D: Instruction("EOR", 4, AddressingMode.ABSOLUTE, EOR),
    0x5D: Instruction("EOR", 4, AddressingMode.ABSOLUTE_X, EOR),
    0x59: Instruction("EOR", 4, AddressingMode.ABSOLUTE_Y, EOR),
    0x41: Instruction("EOR", 6, AddressingMode.INDIRECT_X, EOR),
    0x51: Instruction("EOR", 5, AddressingMode.INDIRECT_Y, EOR),
    0xE6: Instruction("INC", 5, AddressingMode.ZERO_PAGE, INC),
    0xF6: Instruction("INC", 6, AddressingMode.ZERO_PAGE_X, INC),
    0xEE: Instruction("INC", 6, AddressingMode.ABSOLUTE, INC),
    0xFE: Instruction("INC", 7, AddressingMode.ABSOLUTE_X, INC),
    0xE8: Instruction("INX", 2, None, INX),
    0xC8: Instruction("INY", 2, None, INY),
    0x4C: Instruction("JMP", 3, AddressingMode.ABSOLUTE, JMP),
    0x6C: Instruction("JMP", 3, AddressingMode.INDIRECT, JMP),
    0x20: Instruction("JSR", 6, AddressingMode.ABSOLUTE, JSR),
    0xA9: Instruction("LDA", 2, AddressingMode.IMMEDIATE, LDA),
    0xA5: Instruction("LDA", 3, AddressingMode.ZERO_PAGE, LDA),
    0xB5: Instruction("LDA", 4, AddressingMode.ZERO_PAGE_X, LDA),
    0xAD: Instruction("LDA", 4, AddressingMode.ABSOLUTE, LDA),
    0xBD: Instruction("LDA", 4, AddressingMode.ABSOLUTE_X, LDA),
    0xB9: Instruction("LDA", 4, AddressingMode.ABSOLUTE_Y, LDA),
    0xA1: Instruction("LDA", 6, AddressingMode.INDIRECT_X, LDA),
    0xB1: Instruction("LDA", 5, AddressingMode.INDIRECT_Y, LDA),
    0xA2: Instruction("LDX", 2, AddressingMode.IMMEDIATE, LDX),
    0xA6: Instruction("LDX", 3, AddressingMode.ZERO_PAGE, LDX),
    0xB6: Instruction("LDX", 4, AddressingMode.ZERO_PAGE_Y, LDX),
    0xAE: Instruction("LDX", 4, AddressingMode.ABSOLUTE, LDX),
    0xBE: Instruction("LDX", 4, AddressingMode.ABSOLUTE_Y, LDX),
    0xA0: Instruction("LDY", 2, AddressingMode.IMMEDIATE, LDY),
    0xA4: Instruction("LDY", 3, AddressingMode.ZERO_PAGE, LDY),
    0xB4: Instruction("LDY", 4, AddressingMode.ZERO_PAGE_X, LDY),
    0xAC: Instruction("LDY", 4, AddressingMode.ABSOLUTE, LDY),
    0xBC: Instruction("LDY", 4, AddressingMode.ABSOLUTE_X, LDY),
    0x4A: Instruction("LSR", 2, AddressingMode.ACCUMULATOR, LSR_accumulator),
    0x46: Instruction("LSR", 5, AddressingMode.ZERO_PAGE, LSR),
    0x56: Instruction("LSR", 6, AddressingMode.ZERO_PAGE_X, LSR),
    0x4E: Instruction("LSR", 6, AddressingMode.ABSOLUTE, LSR),
    0x5E: Instruction("LSR", 7, AddressingMode.ABSOLUTE_X, LSR),
    0xEA: Instruction("NOP", 2, None, NOP),
    0x09: Instruction("ORA", 2, AddressingMode.IMMEDIATE, ORA),
    0x05: Instruction("ORA", 3, AddressingMode.ZERO_PAGE, ORA),
    0x15: Instruction("ORA", 4, AddressingMode.ZERO_PAGE_X, ORA),
    0x0D: Instruction("ORA", 4, AddressingMode.ABSOLUTE, ORA),
    0x1D: Instruction("ORA", 4, AddressingMode.ABSOLUTE_X, ORA),
    0x19: Instruction("ORA", 4, AddressingMode.ABSOLUTE_Y, ORA),
    0x01: Instruction("ORA", 6, AddressingMode.INDIRECT_X, ORA),
    0x11: Instruction("ORA", 5, AddressingMode.INDIRECT_Y, ORA),
    0x48: Instruction("PHA", 3, None, PHA),
    0x08: Instruction("PHP", 3, None, PHP),
    0x68: Instruction("PLA", 4, None, PLA),
    0x28: Instruction("PLP", 4, None, PLP),
    0x2A: Instruction("ROL", 2, AddressingMode.ACCUMULATOR, ROL),
    0x26: Instruction("ROL", 5, AddressingMode.ZERO_PAGE, ROL),
    0x36: Instruction("ROL", 6, AddressingMode.ZERO_PAGE_X, ROL),
    0x2E: Instruction("ROL", 6, AddressingMode.ABSOLUTE, ROL),
    0x3E: Instruction("ROL", 7, AddressingMode.ABSOLUTE_X, ROL),
    0x6A: Instruction("ROR", 2, AddressingMode.ACCUMULATOR, ROR),
    0x66: Instruction("ROR", 5, AddressingMode.ZERO_PAGE, ROR),
    0x76: Instruction("ROR", 6, AddressingMode.ZERO_PAGE_X, ROR),
    0x6E: Instruction("ROR", 6, AddressingMode.ABSOLUTE, ROR),
    0x7E: Instruction("ROR", 7, AddressingMode.ABSOLUTE_X, ROR),
    0x40: Instruction("RTI", 6, None, RTI),
    0x60: Instruction("RTS", 6, None, RTS),
    0xE9: Instruction("SBC", 2, AddressingMode.IMMEDIATE, SBC),
    0xE5: Instruction("SBC", 3, AddressingMode.ZERO_PAGE, SBC),
    0xF5: Instruction("SBC", 4, AddressingMode.ZERO_PAGE_X, SBC),
    0xED: Instruction("SBC", 4, AddressingMode.ABSOLUTE, SBC),
    0xFD: Instruction("SBC", 4, AddressingMode.ABSOLUTE_X, SBC),
    0xF9: Instruction("SBC", 4, AddressingMode.ABSOLUTE_Y, SBC),
    0xE1: Instruction("SBC", 6, AddressingMode.INDIRECT_X, SBC),
    0xF1: Instruction("SBC", 5, AddressingMode.INDIRECT_Y, SBC),
    0x38: Instruction("SEC", 2, None, SEC),
    0xF8: Instruction("SED", 2, None, SED),
    0x78: Instruction("SEI", 2, None, SEI),
    0x85: Instruction("STA", 3, AddressingMode.ZERO_PAGE, STA),
    0x95: Instruction("STA", 4, AddressingMode.ZERO_PAGE_X, STA),
    0x8D: Instruction("STA", 4, AddressingMode.ABSOLUTE, STA),
    0x9D: Instruction("STA", 5, AddressingMode.ABSOLUTE_X, STA),
    0x99: Instruction("STA", 5, AddressingMode.ABSOLUTE_Y, STA),
    0x81: Instruction("STA", 6, AddressingMode.INDIRECT_X, STA),
    0x91: Instruction("STA", 6, AddressingMode.INDIRECT_Y, STA),
    0x86: Instruction("STX", 3, AddressingMode.ZERO_PAGE, STX),
    0x96: Instruction("STX", 4, AddressingMode.ZERO_PAGE_Y, STX),
    0x8E: Instruction("STX", 4, AddressingMode.ABSOLUTE, STX),
    0x84: Instruction("STY", 3, AddressingMode.ZERO_PAGE, STY),
    0x94: Instruction("STY", 4, AddressingMode.ZERO_PAGE_X, STY),
    0x8C: Instruction("STY", 4, AddressingMode.ABSOLUTE, STY),
    0xAA: Instruction("TAX", 2, None, TAX),
    0xA8: Instruction("TAY", 2, None, TAY),
    0xBA: Instruction("TSX", 2, None, TSX),
    0x8A: Instruction("TXA", 2, None, TXA),
    0x9A: Instruction("TXS", 2, None, TXS),
    0x98: Instruction("TYA", 2, None, TYA),
}
