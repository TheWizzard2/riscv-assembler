# Programa ejemplo

# Tipo R
add  x5, x6, x7      # prueba
sll  x8, x9, x10
sub  x11, x12, x13

# Tipo S
sw   x10, 8(x5)

# Tipo I
addi x1, x2, 10
slti x3, x4, 100

# Tipo B con etiquetas
start: 
    beq  x1, x2, equal_label   # si x1 == x2, salta
    bne  x3, x4, not_equal     # si x3 != x4, salta
    blt  x5, x6, less_than     # si x5 < x6, salta

equal_label:
    addi x7, x0, 1             # instrucción en destino 1

not_equal:
    addi x7, x0, 2             # instrucción en destino 2

less_than:
    addi x7, x0, 3             # instrucción en destino 3

end:
    addi x10, x0, 99           # fin del programa

#tipo U
lui x1, 0x12345
auipc x2, 0x10000
