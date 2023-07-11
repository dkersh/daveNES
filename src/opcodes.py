from .cpu import AddressingMode
import numpy as np

def ADC(self, mode: AddressingMode):
    addr = self.get_operand_address(mode)
    value = self.ram.read(addr)

    a = np.uint16(self.r_accumulator)
    m = np.uint16(value)
    c = np.uint16(self.r_status["flag_C"])

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
    # TODO: Should probably split this up into accumulator / non accumulator
    if mode == AddressingMode.ACCUMULATOR:
        value = self.get_operand_address(mode)
    else:
        addr = self.get_operand_address(mode)
        value = self.ram.read(addr)
    shifted = value << 1

    self.r_status["flag_C"] = True if shifted > 255 else False

    if mode == AddressingMode.ACCUMULATOR:
        self.r_accumulator = np.uint8(shifted)
        self.update_zero_and_negative_flags(np.uint8(shifted))
        if self.r_accumulator == 0:
            self.r_status['flag_Z'] = True
    else:
        self.ram.write(addr, np.uint8(shifted))
        self.update_zero_and_negative_flags(np.uint8(shifted))
    

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
    # A-B = A + (-B) and -B = !B + 1
    addr = self.get_operand_address(mode)
    value = self.ram.read(addr)

    a = self.r_accumulator
    b = np.uint8(value)

    

    #print(result := a + (~b + self.r_status['flag_C']))
    #print(result := a + (~b + (not self.r_status['flag_C'])) + 1)
    #print(result := a + (b ^ 0x00FF) + self.r_status['flag_C']) # http://forum.6502.org/viewtopic.php?p=37758#p37758
    result = a + (b ^ 0x00FF) + self.r_status['flag_C']

    #print(f'{value =}')
    #print(f'{a =}')
    #print(f'{b =}')
    #print(f'{result =}')
    #print(f'{self.r_status["flag_C"] = }')

    # Setting Flags
    self.r_status["flag_C"] = True if result > 255 else False
    result = np.uint8(result)
    self.r_status["flag_V"] = True if (~(value ^ result) & (a ^ result)) & 0x80 else False
    self.r_accumulator = result
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
