# Importar el json con las instrucciones
import json
import sys

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
    data_section = {}   # ahora será un diccionario

    current_section = None
    for i, line in enumerate(lines, start=1):
        clean = clean_line(line)
        if not clean:
            continue

        if clean.startswith(".data"):
            current_section = "data"
            continue
        elif clean.startswith(".text"):
            current_section = "text"
            continue

        if current_section == "data":
            # ejemplo: var1: .word 10
            if ":" in clean:
                label, rest = clean.split(":", 1)
                label = label.strip()
                parts = rest.strip().split()
                if parts[0] == ".word":
                    value = int(parts[1])
                    data_section[label] = value   # guardamos directo en dict
            continue

        if current_section == "text":
            parsed = parse_line(clean, i)
            if parsed:
                instructions.append(parsed)

    return instructions, data_section

def build_label_table(file_instr, data_section, base_data_addr=0x10000000):
    label_table = {}
    pc = 0
    data_addr = base_data_addr

    # Recorremos instrucciones (sección .text)
    for instr in file_instr:
        if instr.get("label"):  # Si la instrucción tiene etiqueta
            label_table[instr["label"]] = pc
        pc += 4  # cada instrucción ocupa 4 bytes

    # Recorremos data (sección .data)
    for entry in data_section:
        if isinstance(entry, dict) and "label" in entry:
            label_table[entry["label"]] = data_addr
        data_addr += 4  # solo soportamos .word (4 bytes)

    return label_table

# Resuelve el offset para instrucciones B y J
def resolver_offset(instr, label_table, pc):
    # Extraer operando de destino (para B y J es la etiqueta)
    target = instr["operands"][-1]  # último operando siempre es label

    # Verificamos si es un label en la tabla
    if target in label_table:
        target_addr = label_table[target]
        offset = target_addr - pc
    else:
        # Si no es label, asumimos que es un número (inmediato)
        offset = int(target)

    # En RV32I, las instrucciones se alinean a 2 bytes para branches/jumps
    offset >>= 1

    return offset

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

# Parsea una línea en la sección .data
def parse_data_line(line, line_number):
    if ":" not in line:
        raise ValueError(f"Error en línea {line_number}: falta etiqueta en .data")

    label, rest = line.split(":", 1)
    label = label.strip()
    tokens = rest.strip().split()

    if tokens[0] != ".word":
        raise ValueError(f"Error en línea {line_number}: solo se soporta .word")

    value = int(tokens[1])  # lo guardamos como entero
    return label, value

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

#codifica una instruccion tipò I en su representacion binaria y hexadecimal
def encode_i_type(instr, funct3, opcode):
    rd = int(instr["operands"][0][1:])   # destino
    rs1 = int(instr["operands"][1][1:])  # registro base
    imm = int(instr["operands"][2])      # inmediato (decimal)

    imm_bin    = format(imm & 0xFFF, "012b")   # inmediato 12 bits
    rs1_bin    = format(rs1, "05b")
    funct3_bin = format(int(funct3, 2), "03b") # viene en binario -> lo normalizamos
    rd_bin     = format(rd, "05b")
    opcode_bin = format(int(opcode, 2), "07b") # igual acá

    bin_str = imm_bin + rs1_bin + funct3_bin + rd_bin + opcode_bin
    hex_str = hex(int(bin_str, 2))[2:].zfill(8)

    return {
        "bin": bin_str,
        "hex": hex_str
    }

# Codifica una instrucción tipo-U en su representación binaria
def encode_u_type(instr, opcode):
    # extraer rd
    rd = int(instr["operands"][0][1:])  # "x5" -> 5
    if not (0 <= rd < 32):
        raise ValueError(f"rd fuera de rango: {rd}")

    # parsear inmediato (soporta "0x..." o decimal)
    imm_raw = int(instr["operands"][1], 0)

    # decidir imm[31:12] (20 bits)
    if (imm_raw & 0xFFF) == 0:
        # si se da un valor de 32-bit alineado a 4K -> tomar bits 31..12 por slicing del binario
        full_bin = format(imm_raw & 0xFFFFFFFF, "032b")  # 32 bits
        imm20_bin = full_bin[:20]                         # bits 31..12
    else:
        # si se pasa directamente el campo de 20 bits
        imm20_bin = format(imm_raw & 0xFFFFF, "020b")     # 20 bits

    #se comprueba si se pasa un número >20 bits que no está alineado
    if imm_raw > 0xFFFFF and (imm_raw & 0xFFF) != 0:
        raise ValueError(
            "Inmediato ambiguo/fuera de rango: pase el campo U (20 bits) "
        )

    # rd y opcode a cadenas
    rd_bin = format(rd, "05b")
    opcode_int = int(opcode, 2) if isinstance(opcode, str) else int(opcode)
    opcode_bin = format(opcode_int & 0x7F, "07b")

    # concatenar
    bin_str = imm20_bin + rd_bin + opcode_bin
    hex_str = hex(int(bin_str, 2))[2:].zfill(8)

    return {"bin": bin_str, "hex": hex_str}
    
# Codifica una instrucción tipo-S en su representación binaria
def encode_s_type(instr, funct3, opcode):
    # Asumimos que funct3 y opcode vienen en string binario
    funct3 = int(funct3, 2)
    opcode = int(opcode, 2)

    # Operandos
    rs2 = int(instr["operands"][0][1:])
    offset, base = instr["operands"][1].split("(")
    rs1 = int(base[1:-1])  # quitar "x" y ")"
    imm = int(offset)

    # Convertir a binarios
    rs1_bin    = format(rs1, "05b")
    rs2_bin    = format(rs2, "05b")
    funct3_bin = format(funct3, "03b")
    opcode_bin = format(opcode, "07b")

    imm_bin = format(imm & 0xFFF, "012b")  # inmediato a 12 bits
    imm_high = imm_bin[:7]   # imm[11:5]
    imm_low  = imm_bin[7:]   # imm[4:0]

    instr_bin = imm_high + rs2_bin + rs1_bin + funct3_bin + imm_low + opcode_bin
    instr_hex = hex(int(instr_bin, 2))[2:].zfill(8)

    return {
        "bin": instr_bin,
        "hex": instr_hex
    }

# Codifica una instrucción tipo-B en su representación binaria
def encode_b_type(instr, funct3, opcode, pc, label_table):
    rs1 = int(instr["operands"][0][1:])
    rs2 = int(instr["operands"][1][1:])
    label = instr["operands"][2]

    if label not in label_table:
        raise ValueError(f"Etiqueta {label} no encontrada")

    target_addr = label_table[label]
    offset = target_addr - pc
    imm = offset >> 1  # descartar bit 0

    # Convertir a 13 bits (incluye signo)
    imm_bin = format(imm & 0x1FFF, "013b")  # 13 bits: [12][11][10:0]

    # Separar los bits según B-type
    imm_12   = imm_bin[0]       # bit 12
    imm_11   = imm_bin[1]       # bit 11
    imm_10_5 = imm_bin[2:8]     # bits 10..5
    imm_4_1  = imm_bin[8:12]    # bits 4..1

    # Convertir registros y campos
    rs1_bin    = format(rs1, "05b")
    rs2_bin    = format(rs2, "05b")
    funct3_bin = format(int(funct3, 2), "03b")
    opcode_bin = format(int(opcode, 2), "07b")

    # Concatenar en orden correcto para B-type
    bin_str = imm_12 + imm_10_5 + rs2_bin + rs1_bin + funct3_bin + imm_4_1 + imm_11 + opcode_bin
    hex_str = hex(int(bin_str, 2))[2:].zfill(8)

    return {"bin": bin_str, "hex": hex_str}

# Codifica una instrucción tipo-J en su representación binaria
def encode_j_type(opcode, rd, offset):
    rd_bin = format(rd, "05b")
    opcode_bin = format(int(opcode, 2), "07b")
    
    # offset de 20 bits para J-type
    imm_bin = format(offset & 0xFFFFF, "020b")
    
    # reordenar bits según formato J-type: [20][10:1][11][19:12]
    j_bin = imm_bin[0] + imm_bin[10:20] + imm_bin[9] + imm_bin[1:9] + rd_bin + opcode_bin
    
    hex_str = hex(int(j_bin, 2))[2:].zfill(8)
    return {"bin": j_bin, "hex": hex_str}

def main():
    if len(sys.argv) != 4:
        print("Uso: python assembler.py program.asm program.hex program.bin")
        sys.exit(1)

    asm_file = sys.argv[1]
    hex_file = sys.argv[2]
    bin_file = sys.argv[3]
    
    # Parseamos el archivo ASM
    file_instr, data_section = parse_file(asm_file)

    # Construimos la tabla de etiquetas
    label_table = build_label_table(file_instr, data_section)

    # Lista para almacenar instrucciones codificadas
    instrucciones_cod = []

    # PC inicial
    pc = 0

    for instr in file_instr:
        if instr is None:
            continue  # ignora líneas vacías o solo etiquetas

        type_instr = extract_type(instr["mnemonic"])
        if type_instr is None:
            continue  # ignora líneas que no tienen mnemonic

        match type_instr:
            case "R":
                funct_3 = get_funct3(instr["mnemonic"])
                funct_7 = get_funct7(instr["mnemonic"])
                opcode = get_opcode(instr["mnemonic"])
                encoded = encode_r_type(instr, funct_3, funct_7, opcode)

            case "S":
                funct_3 = get_funct3(instr["mnemonic"])
                opcode = get_opcode(instr["mnemonic"])
                encoded = encode_s_type(instr, funct_3, opcode)

            case "I":
                funct_3 = get_funct3(instr["mnemonic"])
                opcode = get_opcode(instr["mnemonic"])
                encoded = encode_i_type(instr, funct_3, opcode)

            case "B":
                funct_3 = get_funct3(instr["mnemonic"])
                opcode = get_opcode(instr["mnemonic"])
                offset = resolver_offset(instr, label_table, pc)
                encoded = encode_b_type(instr, funct_3, opcode, offset, label_table)

            case "U":
                opcode = get_opcode(instr["mnemonic"])
                encoded = encode_u_type(instr, opcode)

            case "J":
                opcode = get_opcode(instr["mnemonic"])
                rd = int(instr["operands"][0][1:])       # registro destino
                offset = resolver_offset(instr, label_table, pc)
                encoded = encode_j_type(opcode, rd, offset)

            case _:
                print(f"Instrucción no soportada: {instr['mnemonic']}")
                continue

        instrucciones_cod.append(encoded)
        pc += 4  # Incrementar PC por cada instrucción (4 bytes)

    # Guardar salidas
    with open(hex_file, "w") as fhex, open(bin_file, "w") as fbin:
        for instr in instrucciones_cod:
            fbin.write(instr["bin"] + "\n")
            fhex.write(instr["hex"] + "\n")

    print(f"Ensamblado completado.\nHEX guardado en {hex_file}\nBIN guardado en {bin_file}")

if __name__ == "__main__":
    main()