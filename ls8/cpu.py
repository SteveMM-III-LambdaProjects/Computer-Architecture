"""CPU functionality."""

import sys


# Instructions ------------------------------------------->
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
# ========================================================>


class CPU:
    """Main CPU class."""

    # Constructor ---------------------------------------->
    def __init__(self):
        """Construct a new CPU."""
        self.ram      = [ 0 ] * 256
        self.reg      = [ 0 ] * 8
        self.reg[ 7 ] = 0xF4
        self.pc       = 0
        self.running  = True

        # Branch Table
        self.b_tbl = {}
        self.b_tbl[ LDI ] = self.hndl_ldi
        self.b_tbl[ PRN ] = self.hdnl_prn
        self.b_tbl[ ADD ] = self.hndl_alu
        self.b_tbl[ SUB ] = self.hndl_alu
        self.b_tbl[ MUL ] = self.hndl_alu
        self.b_tbl[ DIV ] = self.hndl_alu
    # ====================================================>


    # Memory Functions ----------------------------------->
    # Memory Address Register (MAR)
    # Memory Data    Register (MDR)
    def ram_read( self, MAR ):
        return self.ram[ MAR ]
    # ===========>

    def ram_write( self, MAR, MDR ):
        self.ram[ MAR ] = MDR
    # ===========>

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

                    if num == '' or num == '\n':
                        continue
                    else:
                        try:
                            self.ram_write( address, int( num, 2 ) )
                        except:
                            print( 'Could not convert string to integer' )
                    
                    address += 1

                    
        except:
            print( 'File not found' )
            sys.exit( 1 )
    # ====================================================>


    # ALU ------------------------------------------------>
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

    # Traceback ------------------------------------------>
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
    # ====================================================>


    # Instruction Handlers ------------------------------->
    def hndl_ldi( self, ins, a, b ):
        self.reg[ a ] = b
        self.pc += 3
    # ===========>

    def hdnl_prn( self, ins, a, b ):
        print ( self.reg[ a ] )
        self.pc += 2
    # ===========>

    def hndl_alu( self, ins, a, b ):
        self.alu( ins, a, b )
        self.pc += 3
    # ====================================================>


    # Main Loop ------------------------------------------>
    def run(self):
        """Run the CPU."""
        
        while self.running:
            # Instruction Register (IR)
            IR = self.ram_read( self.pc )

            if IR == HLT:
                self.running = False

            elif IR not in self.b_tbl:
                print( f'Instruction Register Unknown: {IR} at program counter {self.pc}' )
                self.running = False
            else:
                op_a = self.ram_read( self.pc + 1 )
                op_b = self.ram_read( self.pc + 2 )
                
                func = self.b_tbl[ IR ]
                func( IR, op_a, op_b )
# EoF ---------------------------------------------------->