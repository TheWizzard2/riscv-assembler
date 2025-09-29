.data
var1: .word 10
var2: .word 255
contador: .word -5

.text
# Instrucciones de prueba
add x5, x6, x7
sw x5, 0(x10)       # guardar valor en memoria
addi x1, x2, 15     # inmediato positivo
slti x3, x4, -3     # inmediato negativo
beq x1, x2, fin     # salto si son iguales
add x8, x8, x8      # instrucción que se ejecuta si no saltó

fin: sub x9, x9, x9 # etiqueta de destino
