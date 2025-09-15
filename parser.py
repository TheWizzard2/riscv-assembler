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

# Prueba del parser
instrs = parse_file("prueba.asm")
for instr in instrs:
    print(instr)
