"""CPU functionality."""

import sys
from time import time

# Instructions & Flags ----------------------------------->
# region
CALL = 0b01010000
HLT  = 0b00000001
LDI  = 0b10000010
POP  = 0b01000110
PRN  = 0b01000111
PUSH = 0b01000101
RET  = 0b00010001
ST   = 0b10000100
PRA  = 0b01001000
JMP  = 0b01010100
# ALU Instructions ---->
ADD  = 0b10100000
AND  = 0b10101000
CMP  = 0b10100111
DEC  = 0b01100110
DIV  = 0b10100011
INC  = 0b01100101
MOD  = 0b10100100
MUL  = 0b10100010
NOT  = 0b01101001
OR   = 0b10101010
SHL  = 0b10101100
SHR  = 0b10101101
SUB  = 0b10100001
XOR  = 0b10101011
# Flags --------------->
FLB  = 0b00000000
FLE  = 0b00000001
FLG  = 0b00000010
FLL  = 0b00000100
# Interrupts ---------->
INT  = 0b01010010
IRET = 0b00010011
I0   = 0b00000001
I1   = 0b00000010
I2   = 0b00000100
I3   = 0b00001000
I4   = 0b00010000
I5   = 0b00100000
I6   = 0b01000000
I7   = 0b10000000
# endregion
# ========================================================>


class CPU:
    """Main CPU class."""

    # Constructor ---------------------------------------->
    def __init__(self):
        """Construct a new CPU."""
        self.ram     = [ 0 ] * 256     # RAM
        self.reg     = [ 0 ] * 8       # Registers
        self.pc      = 0               # Program Counter
        self.running = True            # Main Loop Var
        self.sp      = 7               # Stack Pointer
        self.fl      = FLB             # Flag
        self.imsk    = 5               # Interrupt Mask
        self.istat   = 6               # Interrupt Status

        self.intrpts_enbld = True      # Interrupt Bool

        self.reg[ self.sp ]   = 0xF4   # Empty Stack
        self.reg[ self.imsk ] = [ 0b00000011 ]
        
        # Interrupt Vector Table
        self.ivt = [ 0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE, 0xFF ]

        # ALU
        self.alu = {}
        self.alu[ ADD ] = self.hndl_add
        self.alu[ AND ] = self.hndl_and
        self.alu[ CMP ] = self.hndl_cmp
        self.alu[ DEC ] = self.hndl_dec
        self.alu[ DIV ] = self.hndl_div
        self.alu[ INC ] = self.hndl_inc
        self.alu[ MOD ] = self.hndl_mod
        self.alu[ MUL ] = self.hndl_mul
        self.alu[ NOT ] = self.hndl_not
        self.alu[ OR  ] = self.hndl_or
        self.alu[ SHL ] = self.hndl_shl
        self.alu[ SHR ] = self.hndl_shr
        self.alu[ SUB ] = self.hndl_sub
        self.alu[ XOR ] = self.hndl_xor

        # Branch Table
        self.b_tbl = {}
        self.b_tbl[ LDI  ] = self.hndl_ldi
        self.b_tbl[ PRN  ] = self.hndl_prn
        self.b_tbl[ PUSH ] = self.hndl_push
        self.b_tbl[ POP  ] = self.hndl_pop
        self.b_tbl[ CALL ] = self.hndl_call
        self.b_tbl[ RET  ] = self.hndl_ret
        self.b_tbl[ INT  ] = self.hndl_intrpt
        self.b_tbl[ IRET ] = self.hndl_iret
        self.b_tbl[ ST   ] = self.hndl_st
        self.b_tbl[ PRA  ] = self.hndl_pra
        self.b_tbl[ JMP  ] = self.hndl_jmp
        self.b_tbl[ ADD  ] = self.alu[ ADD ]
        self.b_tbl[ AND  ] = self.alu[ AND ]
        self.b_tbl[ CMP  ] = self.alu[ CMP ]
        self.b_tbl[ DEC  ] = self.alu[ DEC ]
        self.b_tbl[ DIV  ] = self.alu[ DIV ]
        self.b_tbl[ INC  ] = self.alu[ INC ]
        self.b_tbl[ MOD  ] = self.alu[ MOD ]
        self.b_tbl[ MUL  ] = self.alu[ MUL ]
        self.b_tbl[ NOT  ] = self.alu[ NOT ]
        self.b_tbl[ OR   ] = self.alu[ OR  ]
        self.b_tbl[ SHL  ] = self.alu[ SHL ]
        self.b_tbl[ SHR  ] = self.alu[ SHR ]
        self.b_tbl[ SUB  ] = self.alu[ SUB ]
        self.b_tbl[ XOR  ] = self.alu[ XOR ]
    # ====================================================>


    # Memory Functions ----------------------------------->
    # Memory Address Register (MAR)
    # Memory Data    Register (MDR)
    def ram_read( self, MAR ):
        return self.ram[ MAR ]
    # ============>


    def ram_write( self, MAR, MDR ):
        self.ram[ MAR ] = MDR
    # ============>


    def load( self ):
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


    # Traceback ------------------------------------------>
    def trace( self ):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print( f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read( self.pc     ),
            self.ram_read( self.pc + 1 ),
            self.ram_read( self.pc + 2 )
        ), end = '' )

        for i in range( 8 ):
            print( " %02X" % self.reg[ i ], end = '' )

        print()
    # ====================================================>


    # Instruction Handlers ------------------------------->
    def hndl_ldi( self, a, b ):
        self.reg[ a ] = b
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_prn( self, a, b ):
        print ( self.reg[ a ] )
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_push( self, a, b ):
        self.base_push( self.reg[ a ] )
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_pop( self, a, b ):
        self.reg[ a ] = self.base_pop()
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_call( self, a, b ):
        self.dec_sp()
        self.ram_write( self.reg[ self.sp ], self.pc + 2 )
        self.pc = self.reg[ a ]
    # ============>


    def hndl_ret( self, a, b ):
        self.pc = self.ram_read( self.reg[ self.sp ] )
        self.inc_sp()
    # ============>


    def hndl_intrpt( self, a, b ):
        val = self.reg[ a ] & self.reg[ self.imsk ]
        if val in [ I0, I1 ]:
            self.reg[ self.istat ] |= val
    # ============>


    def hndl_iret( self, a, b ):
        for i in range( 6, -1, -1 ):
            self.reg[ i ] = self.base_pop()

        self.fl = self.base_pop()
        self.pc = self.base_pop()

        self.intrpts_enbld = True
    # ============>

    def hndl_st( self, a, b ):
        self.ram_write( self.reg[ a ], self.reg[ b ] )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_pra( self, a, b ):
        print( chr( self.reg[ a ] ) )
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_jmp( self, a, b ):
        self.pc = self.reg[ a ]
    # ============>

    # ALU Instructions Handlers -------------------------->
    def hndl_add( self, a, b ):
        self.reg[ a ] += self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_and( self, a, b ):
        self.base_and( a, self.reg[ b ] )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_cmp( self, a, b ):
        first  = self.reg[ a ]
        second = self.reg[ b ]

        if first == second:
            self.set_flag( FLE )

        elif first > second:
            self.set_flag( FLG )

        elif first < second:
            self.set_flag( FLL )

        else:
            self.set_flag( FLB )
    # ============>


    def hndl_dec( self, a, b ):
        self.reg[ a ] -= 1
        self.base_and( a )
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_div( self, a, b ):
        self.reg[ a ] /= self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_inc( self, a, b ):
        self.reg[ a ] += 1
        self.base_and( a )
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_mod( self, a, b ):
        self.reg[ a ] %= self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_mul( self, a, b ):
        self.reg[ a ] *= self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_not( self, a, b ):
        self.reg[ a ] = ~self.reg[ a ]
        self.base_and( a )
        self.inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_or( self, a, b ):
        self.reg[ a ] |= self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_shl( self, a, b ):
        self.reg[ a ] <<= self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_shr( self, a, b ):
        self.reg[ a ] >>= self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_sub( self, a, b ):
        self.reg[ a ] -= self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def hndl_xor( self, a, b ):
        self.reg[ a ] ^= self.reg[ b ]
        self.base_and( a )
        self.inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    # Instruction Helpers -------------------------------->
    def inc_pc( self, num ):
        self.pc += num
    # ============>


    def inc_sp( self ):
        self.reg[ self.sp ] += 1
        self.base_and( self.sp )
    # ============>


    def dec_sp( self ):
        self.reg[ self.sp ] -= 1
    # ============>

    def base_push( self, a ):
        self.dec_sp()
        self.ram_write( self.reg[ self.sp ], a )
    # ============>


    def base_pop( self ):
        val = self.ram_read( self.reg[ self.sp ] )
        self.inc_sp()
        return val
    # ============>


    def base_and( self, a, b=0xFF ):
        self.reg[ a ] &= b
    # ============>


    def set_flag( self, flag ):
        self.fl = flag
    # ============>


    def process_intrpt( self ):
        self.intrpts_enbld = False
        
        pc = None
        status = self.reg[ self.istat ]

        if status & I0:
            self.reg[ self.istat ] -= I0
            pc = self.ram_read( self.ivt[ 0 ] )

        elif status & I1:
            self.reg[ self.istat ] -= I1
            pc = self.ram_read( self.ivt[ 1 ] )
        
        if pc is not None:
            self.base_push( self.pc )
            self.base_push( self.fl )

            for i in range( 0, 7 ):
                self.base_push( self.reg[ i ] )
            
            self.pc = pc
    # ====================================================>


    # Main Loop ------------------------------------------>
    def run(self):
        """Run the CPU."""
        
        start_time = time()

        while self.running:
            if self.intrpts_enbld:
                if self.reg[ self.istat ] != 0:
                    self.process_intrpt()

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
            
            time_check = time()

            if time_check - start_time >= 1:
                self.reg[ self.istat ] += I0
                start_time = time()
# EoF ---------------------------------------------------->