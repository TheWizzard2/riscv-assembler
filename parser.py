# Importar el json con las instrucciones
import json

with open("instructions.json", "r") as file:
    instructions_file = json.load(file)

# Lee un archivo ASM y devolver su contenido como una lista de líneas
def read_asm_file(filename):
    with open(filename, "r") as f:
        return f.readlines()

# Limpia una línea de comentarios y espacios en blanco
def clean_line(line):
    for sep in ["#", "//"]:
        if sep in line:
            line = line.split(sep, 1)[0]
    return line.strip()

# Diccionario de alias de registros a nombres estándar
REG_ALIAS = {
    "zero": "x0", "ra": "x1", "sp": "x2", "gp": "x3", "tp": "x4",
    "t0": "x5", "t1": "x6", "t2": "x7", "s0": "x8", "fp": "x8",
    "s1": "x9", "a0": "x10", "a1": "x11", "a2": "x12", "a3": "x13",
    "a4": "x14", "a5": "x15", "a6": "x16", "a7": "x17",
    "s2": "x18", "s3": "x19", "s4": "x20", "s5": "x21",
    "s6": "x22", "s7": "x23", "s8": "x24", "s9": "x25",
    "s10": "x26", "s11": "x27",
    "t3": "x28", "t4": "x29", "t5": "x30", "t6": "x31"
}

# Normaliza un nombre de registro a su forma estándar
def normalize_register(reg):
    reg = reg.strip()
    if reg in REG_ALIAS:
        return REG_ALIAS[reg]
    return reg

# Parsea una línea de código ASM en sus componentes
def parse_line(line, line_number):
    # Estructura del resultado por cada línea
    result = {
        "label": None,
        "mnemonic": None,
        "operands": [],
        "line_number": line_number,
        "raw": line
    }

    # Si hay etiqueta
    if ":" in line:
        parts = line.split(":", 1)
        result["label"] = parts[0].strip()
        line = parts[1].strip()
        if not line:  # línea solo con etiqueta
            return result

    # Si no hay instrucción, retorna None
    if not line:
        return None

    tokens = line.replace(",", " ").split()
    result["mnemonic"] = tokens[0]
    result["operands"] = [normalize_register(op) for op in tokens[1:]]
    return result

# Parsea un archivo ASM completo y devuelve una lista de instrucciones parseadas
def parse_file(filename):
    lines = read_asm_file(filename)
    instructions = []

    # Itera sobre las líneas, limpiándolas y parseándolas
    for i, line in enumerate(lines, start=1):
        clean = clean_line(line)
        if not clean:
            continue
        parsed = parse_line(clean, i)
        if parsed:
            instructions.append(parsed)

    return instructions

# Recibe la instrucción y devuelve su tipo (R, I, S, B, U, J)
def extract_type(mnemonic):
    for instr in instructions_file:
        if instr["mnemonic"] == mnemonic:
            return instr["format"]
        
def get_funct7(mnemonic):
    for instr in instructions_file:
        if instr["mnemonic"] == mnemonic:
            return instr["funct7"]
    return None

def get_funct3(mnemonic):
    for instr in instructions_file:
        if instr["mnemonic"] == mnemonic:
            return instr["funct3"]
    return None

def get_opcode(mnemonic):
    for instr in instructions_file:
        if instr["mnemonic"] == mnemonic:
            return instr["opcode"]
    return None


# Codifica una instrucción tipo-R en su representación binaria
def encode_r_type(instr, funct3, funct7, opcode):
    # Convertir a enteros los campos que vienen como strings binarias
    funct7 = int(funct7, 2)
    funct3 = int(funct3, 2)
    opcode = int(opcode, 2)

    rs2 = int(instr["operands"][2][1:])  # Segundo operando
    rs1 = int(instr["operands"][1][1:])  # Primer operando
    rd = int(instr["operands"][0][1:])   # Destino

    # Formatear a cadenas binarias con padding fijo
    funct7_bin = format(funct7, "07b")
    rs2_bin    = format(rs2, "05b")
    rs1_bin    = format(rs1, "05b")
    funct3_bin = format(funct3, "03b")
    rd_bin     = format(rd, "05b")
    opcode_bin = format(opcode, "07b")

    # Concatenar en orden correcto (32 bits totales)
    instr_bin = funct7_bin + rs2_bin + rs1_bin + funct3_bin + rd_bin + opcode_bin

    # Convertir a entero y hex
    instr_int = int(instr_bin, 2)
    instr_hex = hex(instr_int)[2:].zfill(8)  # quitar "0x" y rellenar a 8 dígitos

    return {
        "bin": instr_bin,
        "hex": instr_hex
    }


# Prueba del parser
file_instr = parse_file("prueba.asm")

# Lista para almacenar instrucciones codificadas
instrucciones_cod = []

for instr in file_instr:
    # Extraemos el tipo de instrucción
    type_instr = extract_type(instr["mnemonic"])

    # Extraemos funct3, funct7 y opcode
    funct_3 = get_funct3(instr["mnemonic"])
    funct_7 = get_funct7(instr["mnemonic"])
    opcode = get_opcode(instr["mnemonic"])

    # Codificación según tipo
    match type_instr:
        case "R":
            encoded = encode_r_type(instr, funct_3, funct_7, opcode)
            instrucciones_cod.append(encoded)

# Escribir archivos de salida
with open("resultado.txt", "w") as f:
    for instr in instrucciones_cod:
        f.write(f"{instr['bin']}   {instr['hex']}\n")


