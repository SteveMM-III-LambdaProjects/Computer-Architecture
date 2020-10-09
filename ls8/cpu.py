"""CPU functionality."""

import sys
from time import time

# Instructions & Flags ----------------------------------->
# region   <-- vscode collapse region tag
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
        self.__ram     = [ 0 ] * 256     # RAM
        self.__reg     = [ 0 ] * 8       # Registers
        self.__pc      = 0               # Program Counter
        self.__running = True            # Main Loop Var
        self.__sp      = 7               # Stack Pointer
        self.__fl      = FLB             # Flag
        self.__imsk    = 5               # Interrupt Mask
        self.__istat   = 6               # Interrupt Status

        self.__intrpts_enbld = True      # Interrupt Bool

        self.__reg[ self.__sp   ] = 0xF4 # Empty Stack
        # Interrupt Mask; I0 & I1 only
        self.__reg[ self.__imsk ] = [ 0b00000011 ]
        
        # Interrupt Vector Table
        self.__ivt = [ 0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE, 0xFF ]

        # ALU
        self.__alu = {}
        self.__alu[ ADD ] = self.__hndl_add
        self.__alu[ AND ] = self.__hndl_and
        self.__alu[ CMP ] = self.__hndl_cmp
        self.__alu[ DEC ] = self.__hndl_dec
        self.__alu[ DIV ] = self.__hndl_div
        self.__alu[ INC ] = self.__hndl_inc
        self.__alu[ MOD ] = self.__hndl_mod
        self.__alu[ MUL ] = self.__hndl_mul
        self.__alu[ NOT ] = self.__hndl_not
        self.__alu[ OR  ] = self.__hndl_or
        self.__alu[ SHL ] = self.__hndl_shl
        self.__alu[ SHR ] = self.__hndl_shr
        self.__alu[ SUB ] = self.__hndl_sub
        self.__alu[ XOR ] = self.__hndl_xor

        # Branch Table
        self.__b_tbl = {}
        self.__b_tbl[ LDI  ] = self.__hndl_ldi
        self.__b_tbl[ PRN  ] = self.__hndl_prn
        self.__b_tbl[ PUSH ] = self.__hndl_push
        self.__b_tbl[ POP  ] = self.__hndl_pop
        self.__b_tbl[ CALL ] = self.__hndl_call
        self.__b_tbl[ RET  ] = self.__hndl_ret
        self.__b_tbl[ INT  ] = self.__hndl_intrpt
        self.__b_tbl[ IRET ] = self.__hndl_iret
        self.__b_tbl[ ST   ] = self.__hndl_st
        self.__b_tbl[ PRA  ] = self.__hndl_pra
        self.__b_tbl[ JMP  ] = self.__hndl_jmp
        self.__b_tbl[ ADD  ] = self.__alu[ ADD ]
        self.__b_tbl[ AND  ] = self.__alu[ AND ]
        self.__b_tbl[ CMP  ] = self.__alu[ CMP ]
        self.__b_tbl[ DEC  ] = self.__alu[ DEC ]
        self.__b_tbl[ DIV  ] = self.__alu[ DIV ]
        self.__b_tbl[ INC  ] = self.__alu[ INC ]
        self.__b_tbl[ MOD  ] = self.__alu[ MOD ]
        self.__b_tbl[ MUL  ] = self.__alu[ MUL ]
        self.__b_tbl[ NOT  ] = self.__alu[ NOT ]
        self.__b_tbl[ OR   ] = self.__alu[ OR  ]
        self.__b_tbl[ SHL  ] = self.__alu[ SHL ]
        self.__b_tbl[ SHR  ] = self.__alu[ SHR ]
        self.__b_tbl[ SUB  ] = self.__alu[ SUB ]
        self.__b_tbl[ XOR  ] = self.__alu[ XOR ]
    # ====================================================>


    # Memory Functions ----------------------------------->
    # Memory Address Register (MAR)
    # Memory Data    Register (MDR)
    def __ram_read( self, MAR ):
        return self.__ram[ MAR ]
    # ============>


    def __ram_write( self, MAR, MDR ):
        self.__ram[ MAR ] = MDR
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
                            self.__ram_write( address, int( num, 2 ) )
                        except:
                            print( 'Could not convert string to integer' )
                    
                    address += 1

                    
        except:
            print( 'File not found' )
            sys.exit( 1 )
    # ====================================================>


    # Traceback ------------------------------------------>
    def __trace( self ):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print( f"TRACE: %02X | %02X %02X %02X |" % (
            self.__pc,
            self.__fl,
            #self.ie,
            self.__ram_read( self.__pc     ),
            self.__ram_read( self.__pc + 1 ),
            self.__ram_read( self.__pc + 2 )
        ), end = '' )

        for i in range( 8 ):
            print( " %02X" % self.__reg[ i ], end = '' )

        print()
    # ====================================================>


    # Instruction Handlers ------------------------------->
    def __hndl_ldi( self, a, b ):
        self.__reg[ a ] = b
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_prn( self, a, b ):
        print ( self.__reg[ a ] )
        self.__inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_push( self, a, b ):
        self.__push( self.__reg[ a ] )
        self.__inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_pop( self, a, b ):
        self.__reg[ a ] = self.__pop()
        self.__inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_call( self, a, b ):
        self.__dec_sp()
        self.__ram_write( self.__reg[ self.__sp ], self.__pc + 2 )
        self.__pc = self.__reg[ a ]
    # ============>


    def __hndl_ret( self, a, b ):
        self.__pc = self.__ram_read( self.__reg[ self.__sp ] )
        self.__inc_sp()
    # ============>


    def __hndl_intrpt( self, a, b ):
        val = self.__reg[ a ] & self.__reg[ self.__imsk ]
        if val in [ I0, I1 ]:
            self.__reg[ self.__istat ] |= val
    # ============>


    def __hndl_iret( self, a, b ):
        for i in range( 6, -1, -1 ):
            self.__reg[ i ] = self.__pop()

        self.__fl = self.__pop()
        self.__pc = self.__pop()

        self.__intrpts_enbld = True
    # ============>


    def __hndl_st( self, a, b ):
        self.__ram_write( self.__reg[ a ], self.__reg[ b ] )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_pra( self, a, b ):
        print( chr( self.__reg[ a ] ) )
        self.__inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_jmp( self, a, b ):
        self.__pc = self.__reg[ a ]
    # ============>


    # ALU Instructions Handlers -------------------------->
    def __hndl_add( self, a, b ):
        self.__reg[ a ] += self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_and( self, a, b ):
        self.__and( a, self.__reg[ b ] )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_cmp( self, a, b ):
        first  = self.__reg[ a ]
        second = self.__reg[ b ]

        if first == second:
            self.__set_flag( FLE )

        elif first > second:
            self.__set_flag( FLG )

        elif first < second:
            self.__set_flag( FLL )

        else:
            self.__set_flag( FLB )
    # ============>


    def __hndl_dec( self, a, b ):
        self.__reg[ a ] -= 1
        self.__and( a )
        self.__inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_div( self, a, b ):
        self.__reg[ a ] /= self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_inc( self, a, b ):
        self.__reg[ a ] += 1
        self.__and( a )
        self.__inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_mod( self, a, b ):
        self.__reg[ a ] %= self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_mul( self, a, b ):
        self.__reg[ a ] *= self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_not( self, a, b ):
        self.__reg[ a ] = ~self.__reg[ a ]
        self.__and( a )
        self.__inc_pc( 2 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_or( self, a, b ):
        self.__reg[ a ] |= self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_shl( self, a, b ):
        self.__reg[ a ] <<= self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_shr( self, a, b ):
        self.__reg[ a ] >>= self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_sub( self, a, b ):
        self.__reg[ a ] -= self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    def __hndl_xor( self, a, b ):
        self.__reg[ a ] ^= self.__reg[ b ]
        self.__and( a )
        self.__inc_pc( 3 ) # +1 base increment plus 1 for each used operand
    # ============>


    # Instruction Helpers -------------------------------->
    def __inc_pc( self, num ):
        self.__pc += num
    # ============>


    def __inc_sp( self ):
        self.__reg[ self.__sp ] += 1
        self.__and( self.__sp )
    # ============>


    def __dec_sp( self ):
        self.__reg[ self.__sp ] -= 1
    # ============>


    def __push( self, a ):
        self.__dec_sp()
        self.__ram_write( self.__reg[ self.__sp ], a )
    # ============>


    def __pop( self ):
        val = self.__ram_read( self.__reg[ self.__sp ] )
        self.__inc_sp()
        return val
    # ============>


    def __and( self, a, b=0xFF ):
        self.__reg[ a ] &= b
    # ============>


    def __set_flag( self, flag ):
        self.__fl = flag
    # ============>


    def __process_intrpt( self ):
        self.__intrpts_enbld = False
        
        pc = None
        status = self.__reg[ self.__istat ]

        if status & I0:
            self.__reg[ self.__istat ] -= I0
            pc = self.__ram_read( self.__ivt[ 0 ] )

        elif status & I1:
            self.__reg[ self.__istat ] -= I1
            pc = self.__ram_read( self.__ivt[ 1 ] )
        
        if pc is not None:
            self.__push( self.__pc )
            self.__push( self.__fl )

            for i in range( 0, 7 ):
                self.__push( self.__reg[ i ] )
            
            self.__pc = pc
    # ====================================================>


    # Main Loop ------------------------------------------>
    def run(self):
        """Run the CPU."""
        
        start_time = time()

        while self.__running:
            if self.__intrpts_enbld:
                if self.__reg[ self.__istat ] != 0:
                    self.__process_intrpt()

            # Instruction Register (IR)
            IR = self.__ram_read( self.__pc )

            if IR == HLT:
                self.__running = False

            elif IR not in self.__b_tbl:
                print( f'Instruction Register Unknown: {IR} at program counter {self.__pc}' )
                self.__running = False
                
            else:
                op_a = self.__ram_read( self.__pc + 1 )
                op_b = self.__ram_read( self.__pc + 2 )
                
                func = self.__b_tbl[ IR ]
                func( op_a, op_b )
            
            time_check = time()

            if time_check - start_time >= 1:
                self.__reg[ self.__istat ] += I0
                start_time = time()
# EoF ---------------------------------------------------->