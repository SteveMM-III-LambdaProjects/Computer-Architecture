; histogram.asm
;
; Expected output:
; *
; **
; ****
; ********
; ****************
; ********************************
; ****************************************************************

LDI R0,1        ; 0 - current asterisks
LDI R1,1        ; 1 - current line
LDI R2,8        ; 2 - max lines + 1
LDI R3,2        ; 3 - multiply by
LDI R4,Print    ; 4 - load print address

Print:

PRL R0          ; 5 - print line with current asterisks
MUL R0,R3       ; 6 - double current asterisks
INC R1          ; 7 - increment current line
CMP R1,R2       ; 8 - compare lines
JLT R4          ; 9 - less than max lines loop back to print
HLT             ; 10 - halt when done

