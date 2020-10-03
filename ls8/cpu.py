"""CPU functionality."""

import sys


LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram      = [ 0 ] * 256
        self.reg      = [ 0 ] * 8
        self.reg[ 7 ] = 0xF4
        self.pc       = 0
        self.running  = True

    def load(self):
        """Load a program into memory."""

        if len( sys.argv ) != 2:
            print( 'Insufficient number of arguments' )
            sys.exit( 1 )

        address  = 0
        filename = sys.argv[ 1 ]

        try:
            with open( filename ) as f:
                for line in f:
                    line = line.split( '#' )
                    num  = line[ 0 ].strip()

                    if num == '':
                        continue
                    else:
                        try:
                            self.ram[ address ] = int( num, 2 )
                        except:
                            print( 'Could not convert string to integer' )
                    
                    address += 1

                    
        except:
            print( 'File not found' )
            sys.exit( 1 )

    """ 
        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]
 
        for instruction in program:
            self.ram[ address ] = instruction
            address += 1
    """

    # Memory Address Register (MAR)
    # Memory Data    Register (MDR)
    def ram_read( self, MAR ):
        return self.ram[ MAR ]


    def ram_write( self, MAR, MDR ):
        self.ram[ MAR ] = MDR


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if   op == ADD:
            self.reg[ reg_a ] += self.reg[ reg_b ]

        elif op == SUB:
            self.reg[ reg_a ] -= self.reg[ reg_b ]

        elif op == MUL:
            self.reg[ reg_a ] *= self.reg[ reg_b ]

        elif op == DIV:
            self.reg[ reg_a ] /= self.reg[ reg_b ]
            
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    def execute( self, instruction, op_a, op_b ):
        if   instruction == HLT:
            self.running = False

        elif instruction == LDI:
            self.reg[ op_a ] = op_b
            self.pc += 2

        elif instruction == PRN:
            print( self.reg[ op_a ] )
            self.pc += 1

        elif instruction in [ ADD, SUB, MUL, DIV ]:
            self.alu( instruction, op_a, op_b )
            self.pc += 2

        else:
            print( f'Instruction Register Unknown: {instruction} at program counter {self.pc}' )
            self.running = False

        self.pc += 1


    def run(self):
        """Run the CPU."""
        
        while self.running:
            # Instruction Register (IR)
            IR = self.ram_read( self.pc )

            op_a = self.ram_read( self.pc + 1 )
            op_b = self.ram_read( self.pc + 2 )

            self.execute( IR, op_a, op_b )