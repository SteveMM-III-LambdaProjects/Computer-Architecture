"""CPU functionality."""

import sys


# Instructions ------------------------------------------->
LDI  = 0b10000010
PRN  = 0b01000111
HLT  = 0b00000001
ADD  = 0b10100000
SUB  = 0b10100001
MUL  = 0b10100010
DIV  = 0b10100011
POP  = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET  = 0b00010001
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
        self.sp       = 6
        self.fl       = 5

        self.reg[ self.sp ] = len( self.ram ) - 1
        self.reg[ self.fl ] = 0b00000000

        # ALU
        self.alu = {}
        self.alu[ ADD ] = self.hndl_add
        self.alu[ SUB ] = self.hndl_sub
        self.alu[ MUL ] = self.hndl_mul
        self.alu[ DIV ] = self.hndl_div

        # Branch Table
        self.b_tbl = {}
        self.b_tbl[ LDI  ] = self.hndl_ldi
        self.b_tbl[ PRN  ] = self.hndl_prn
        self.b_tbl[ POP  ] = self.hndl_pop
        self.b_tbl[ PUSH ] = self.hndl_push
        self.b_tbl[ CALL ] = self.hndl_call
        self.b_tbl[ RET  ] = self.hndl_ret
        self.b_tbl[ ADD  ] = self.alu[ ADD ]
        self.b_tbl[ SUB  ] = self.alu[ SUB ]
        self.b_tbl[ MUL  ] = self.alu[ MUL ]
        self.b_tbl[ DIV  ] = self.alu[ DIV ]
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

        try:
            with open( sys.argv[ 1 ] ) as f:
                for line in f:
                    line = line.split( '#' )
                    num  = line[ 0 ].strip()

                    if num == '':
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

    """ 
    # ALU ------------------------------------------------>
    def alu(self, ins, reg_a, reg_b):
        """'''ALU operations.'''"""

        if   ins == ADD:
            self.reg[ reg_a ] += self.reg[ reg_b ]

        elif ins == SUB:
            self.reg[ reg_a ] -= self.reg[ reg_b ]

        elif ins == MUL:
            self.reg[ reg_a ] *= self.reg[ reg_b ]

        elif ins == DIV:
            self.reg[ reg_a ] /= self.reg[ reg_b ]

        else:
            raise Exception("Unsupported ALU operation")

        self.pc += 3 # +1 base increment plus 1 for each used operand
    # ====================================================>
    """

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


    # Instruction Handlers & Helpers --------------------->
    def hndl_ldi( self, a, b ):
        self.reg[ a ] = b
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ===========>


    def hndl_prn( self, a, b ):
        print ( self.reg[ a ] )
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ===========>


    def hndl_pop( self, a, b ):
        self.reg[ a ] = self.ram_read( self.reg[ self.sp ] )
        self.inc_sp()
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ===========>


    def hndl_push( self, a, b ):
        self.dec_sp()
        self.ram_write( self.reg[ self.sp ], self.reg[ a ] )
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ===========>


    def hndl_call( self, a, b ):
        self.dec_sp()
        self.ram_write( self.reg[ self.sp ], self.pc + 2 )
        self.pc = self.reg[ a ]
    # ===========>


    def hndl_ret( self, a, b ):
        self.pc = self.ram_read( self.reg[ self.sp ] )
        self.inc_sp()
    # ===========>


    def hndl_add( self, a, b):
        self.reg[ a ] += self.reg[ b ]
        self.limiter( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ===========>


    def hndl_sub( self, a, b):
        self.reg[ a ] -= self.reg[ b ]
        self.limiter( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ===========>


    def hndl_mul( self, a, b):
        self.reg[ a ] *= self.reg[ b ]
        self.limiter( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ===========>


    def hndl_div( self, a, b):
        self.reg[ a ] /= self.reg[ b ]
        self.limiter( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ===========>


    def inc_pc( self, num ):
        self.pc += num
    # ===========>


    def inc_sp( self ):
        self.reg[ self.sp ] += 1
        self.limiter( self.sp )
    # ===========>


    def dec_sp( self ):
        self.reg[ self.sp ] -= 1
    # ===========>


    def limiter( self, a ):
        self.reg[ a ] &= 0xFF
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
                func( op_a, op_b )
# EoF ---------------------------------------------------->