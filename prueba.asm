.data
var1: .word 10
var2: .word 4

.text
    add x5, x6, x7       # instrucción tipo R
    sw x5, 0(x10)        # instrucción tipo S
    addi x1, x2, 15      # instrucción tipo I

loop:
    beq x1, x2, end      # instrucción tipo B
    addi x1, x1, -1
    jal x0, loop         # instrucción tipo J (salto atrás)

end:
    sub x8, x9, x10      # instrucción tipo R
