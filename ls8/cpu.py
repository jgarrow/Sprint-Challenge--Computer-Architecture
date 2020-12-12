"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # 256 bytes of memory
        self.reg = [0] * 8 # 8 registers
        self.reg[7] = 0xF4 # set the SP (stack pointer)
        self.pc = 0 
        self.fl = 0b00000000 # 00000LGE - initiliaze all to false
        self.running = False
        self.commands = {
            0b00000001: self.hlt, # HLT: halt the CPU and exit the emulator
            0b10000010: self.ldi, # LDI: load "immediate", store a value in a register, or "set this register to this value"
            0b01000111: self.prn, # PRN: a pseudo-instruction that prints the numeric value stored in a register
            0b10100010: self.mul, # MUL: multiply the values in 2 registers together
            0b01000101: self.push, # PUSH the value in the given register on the stack
            0b01000110: self.pop, # POP the value at the top of the stack into the given register
            0b01010000: self.call, # CALL a subroutine (function) at the address stored in the register
            0b00010001: self.ret, # RET
            0b10100000: self.add, # ADD the value in 2 registers and store the result in registerA
            0b10100111: self.cmp, # CMP: compare values in 2 registers; if registerA = register Bset Equal `E` flag to 1 or if registerA < registerB set Less-than `L` flag to 1 or if registerA > registerB set Greater-than `G` flag to 1
            0b01010100: self.jmp, # JMP: jump to the address stored in the given register
            0b01010101: self.jeq, # JEQ: if Equal `E` flag is true, jump to address stored in given register
            0b01010110: self.jne # JNE: if Equal `E` flag is NOT true, jump to address stored in given register
        }

    # Inside the CPU, there are two internal registers used for memory operations: the Memory Address Register (MAR) and the Memory Data Register (MDR). 
    # The MAR contains the address that is being read or written to. The MDR contains the data that was read or the data to write. 
    # You don't need to add the MAR or MDR to your CPU class, but they would make handy parameter names for `ram_read()` and `ram_write()`
    
    # mar = Memory Address Register
    def ram_read(self, mar):
        return self.ram[mar]
    
    # mar = Memory Address Register
    # mdr = Memory Data Register
    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
    
    # halt the CPU and exit the emulator
    def hlt(self):
        self.running = False
        sys.exit()
        
        
    # LDI register immediate
    # Set the value of a register to an integer
    def ldi(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        self.reg[operand_a] = operand_b
        
    
    # PRN register pseudo-instruction
    # print the numeric value stored in a register
    def prn(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
    
    def mul(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]
    
    def add(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        self.reg[operand_a] = self.reg[operand_a] + self.reg[operand_b]

    
    def push(self):
        # decrement the SP (stack pointer)
        self.reg[7] -= 1

        # copy value from given register into address pointed to by SP
        register_address = self.ram_read(self.pc + 1)
        value = self.reg[register_address]

        sp = self.reg[7]
        self.ram_write(sp, value)

    def pop(self):
        # copy the value from the address pointed to by `SP` to the given register

        # get the SP
        sp = self.reg[7]

        # copy the value from memory at that SP address
        value = self.ram_read(sp)

        # get the target register address
        register_address = self.ram_read(self.pc + 1)

        # Put the value in that register
        self.reg[register_address] = value

        # Increment the SP (move it back up)
        self.reg[7] += 1

    def call(self):
        # The address of the instruction directly after CALL is pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
        ## find the address of the command after CALL (self.pc + 2)
        next_command_address = self.pc + 2

        ## push the address onto the stack
            ### decrement SP
        self.reg[7] -= 1

        ### put next command address at the location in memory where the SP points
        sp = self.reg[7]
        self.ram_write(sp, next_command_address)

        # The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
        ## find the number of the register to look at 
        register_number_address = self.ram_read(self.pc + 1)

        ## get the address of our subroutine out of that register
        address_to_jump_to = self.reg[register_number_address]

        ## set the pc
        self.pc = address_to_jump_to

    def ret(self):
        # pop the value from the top of the stack and store it in the pc

        ## pop from top of stack
        ### get the value first -- this is our return address that we want our pc to go back to
        sp = self.reg[7]
        return_address = self.ram_read(sp)

        ### then move the SP back up
        self.reg[7] += 1

        ## Jump back, set pc to this return address value
        self.pc = return_address
    
    def cmp(self):
        # get values to compare
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        # set E flag to 1
        if self.reg[operand_a] == self.reg[operand_b]:
            self.fl = 0b00000001

        # set G flag to 1
        elif self.reg[operand_a] > self.reg[operand_b]:
             self.fl = 0b00000010
            
        # set L flag to 1
        else:
            self.fl = 0b00000100
    
    def jmp(self):
        address_to_jump_to = self.ram_read(self.pc + 1)
        self.pc = self.reg[address_to_jump_to]
    
    def jeq(self):
        # jump if equal
        if self.fl == 0b00000001:
            self.jmp()
        else:
            self.pc += 2
    
    def jne(self):
        # jump if the Equal `E` flag is not set
        if self.fl != 0b00000001:
            self.jmp()
        else:
            self.pc += 2


    def load(self):
        """Load a program into memory."""

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     print(f'instruction: {instruction}')
        #     self.ram[address] = instruction
        #     address += 1
        
        # print(self.ram)

        try:
            if len(sys.argv) < 2:
                print(f'Error from {sys.argv[0]}: missing filename argument')
                print(f'Usage: python3 {sys.argv[0]} <somefilename>')
                sys.exit(1)

            # add a counter that adds to memory at that index
            ram_index = 0

            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split("#")[0]
                    stripped_split_line = split_line.strip()

                    if stripped_split_line != "":
                        command = int(stripped_split_line, 2)
                        
                        # load command into memory
                        self.ram_write(ram_index, command)
                        ram_index += 1

        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')



    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram_read(self.pc) # instruction register/command

            self.commands[ir]()

            # https://github.com/LambdaSchool/Computer-Architecture/blob/master/LS8-spec.md#instruction-layout
            # meanings iof the bits in the first byte of each instruction/command: AABCDDDD
            ## AA = Number of operands for this opcode, 0-2
            ## B = 1 if this is an ALU operation
            ## C = 1 if this instruction sets the PC
            ## DDDD = instruction identifier

            # right shift 6 bits to just get the 'AA' 
            number_of_operands = ir >> 6

            # bit shift and mask to isolate the 'C' bit
            # will only evaluate to true if the 'C' bit is a 1
            sets_pc_directly = ((ir >> 4) & 0b001) == 0b001
    
            if not sets_pc_directly:
                self.pc += (1 + number_of_operands)