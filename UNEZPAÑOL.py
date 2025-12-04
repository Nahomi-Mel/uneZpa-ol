# --- INTERPRETE SIMPLE: UNEZPAÑOL (v1.1) ---
import re  # Importa el módulo de Expresiones Regulares para el análisis de patrones.

# ============================================
# === TABLA DE SÍMBOLOS GLOBAL ===
variables = {}

# ============================================
# === FASE DE EVALUACIÓN DE EXPRESIONES ===
# ============================================

def evaluar(expr):
    """
    Evalúa expresiones UNEZPAÑOL (aritméticas, lógicas o de cadena) utilizando
    el motor 'eval' de Python, después de sustituir las variables.

    Args:
        expr (str): La expresión a evaluar (ej. 'x + 5', 'y >= 10', '"Hola" + nombre').

    Returns:
        any: El resultado de la expresión evaluada (número, string, o booleano).

    Raises:
        ValueError: Si ocurre un error durante la sustitución o la evaluación.

    """
    # 1. Copia de la expresión original para sustitución
    expr_sustituida = expr

    # --- FASE DE SUSTITUCIÓN DE VARIABLES ---
    # Reemplaza los nombres de las variables en la expresión por sus valores reales.
    for nombre, valor in variables.items():
        expr_sustituida = re.sub(rf'\b{nombre}\b', repr(valor), expr_sustituida)
    try:
        # 2. Ejecuta la expresión transformada usando la función nativa eval() de Python.
        return eval(expr_sustituida)
    except Exception as e:
        # Manejo de errores durante la evaluación.
        raise ValueError(f"Error al evaluar '{expr}' (transformada a '{expr_sustituida}'): {e}")


# ============================================
# === FASE DE INTERPRETACIÓN PRINCIPAL ===
# ============================================

def interpretar(codigo):
    """
    Interprete principal. Procesa y ejecuta el código UNEZPAÑOL línea por línea.
    Utiliza recursión para manejar bloques de código (condicionales y bucles).

    Args:
        codigo (list[str]): Una lista de cadenas, donde cada cadena es una línea de código.
    """
    i = 0
    while i < len(codigo):
        linea = codigo[i].strip()

        # ----------------------------------------
        # 1. Ignorar comentarios o líneas vacías
        # ----------------------------------------
        if linea == "" or linea.startswith("#"):
            i += 1
            continue

        # ----------------------------------------
        # 2. Declaraciones (entero | cadena):
        # Patrón: (tipo) (nombre) = (valor/expresión);
        # Ej: entero x = 5; | cadena nombre = "Juan";
        # ----------------------------------------
        m = re.match(r'(entero|cadena)\s+(\w+)\s*=\s*(.+);', linea)
        if m:
            tipo, nombre, valor_expr = m.groups()
            valor_expr = valor_expr.strip()

            if tipo == "cadena":
                # Para cadenas: elimina las comillas de los bordes.
                # Nota: Esto es simple y no maneja comillas escapadas internas.
                valor = valor_expr.strip('"')
                variables[nombre] = valor
            elif tipo == "entero":
                # Para enteros: evalúa la expresión para obtener el valor numérico.
                valor_evaluado = evaluar(valor_expr)
                # Asegura que el resultado final se guarde como un entero de Python.
                variables[nombre] = int(valor_evaluado)

            i += 1
            continue
        
        # ----------------------------------------
        # 3. Asignación/Reasignación (Si se desea añadir)
        # Patrón: (nombre) = (valor/expresión);
        # El código original no maneja esto, pero se añadiría aqui.
        # ----------------------------------------
        # m = re.match(r'(\w+)\s*=\s*(.+);', linea)
        # if m and m.group(1) in variables:
        #     ... Ejercicio 1 de Lenguajes y automatas
        # ----------------------------------------
        # 4. Sentencia Imprimir:
        # Patrón: Imprimir((expresión));
        # Ej: Imprimir("El valor es: " + str(x));
        # ----------------------------------------
        m = re.match(r'Imprimir\((.+)\);', linea)
        if m:
            expr = m.group(1).strip()
            # Evalúa la expresión y envía el resultado a la salida estándar.
            print(evaluar(expr))
            i += 1
            continue

        # ----------------------------------------
        # 5. Sentencia Pausar:
        # Patron: Pausar();
        # ----------------------------------------
        if re.match(r'Pausar\(\);', linea):
            # Pausa la ejecución hasta que el usuario presione Enter.
            input("\n[Ejecución pausada] Presiona ENTER para continuar...\n")
            i += 1
            continue

        # ----------------------------------------
        # 6. Estructura condicional: Si ... Entonces ... FinSi
        # Patrón: Si (condición) Entonces
        # ----------------------------------------
        if linea.startswith("Si") and "Entonces" in linea:
            # Extrae con re la condición entre 'Si' y 'Entonces'
            condicion = re.findall(r'Si\s+(.+)\s+Entonces', linea)[0].strip()
            bloque = []
            i += 1
            nivel = 1  # Contador para manejar el anidamiento (Si dentro de Si)

            # Recorre las líneas para recolectar el bloque de código interno
            while i < len(codigo) and nivel > 0:
                l = codigo[i].strip()
                if l.startswith("Si") and "Entonces" in l:
                    nivel += 1
                elif l == "FinSi":
                    nivel -= 1
                    if nivel == 0:
                        i += 1  # Avanza más allá del 'FinSi'
                        break # Bloque completado
                
                # Solo añade la línea al bloque si no es el 'FinSi' de cierre.
                if nivel > 0:
                    bloque.append(codigo[i])
                i += 1

            # Si la condición evaluada es verdadera, ejecuta el bloque de forma recursiva.
            if evaluar(condicion):
                interpretar(bloque)
            continue # Continua la ejecución despues del bloque Si/FinSi

        # ----------------------------------------
        # 7. Bucle Mientras: Mientras ... Hacer ... FinMientras
        # Patrón: Mientras (condición) Hacer
        # ----------------------------------------
        if linea.startswith("Mientras") and "Hacer" in linea:
            # Extrae la condición entre 'Mientras' y 'Hacer'
            condicion = re.findall(r'Mientras\s+(.+)\s+Hacer', linea)[0].strip()
            bloque = []
            i += 1
            nivel = 1 # Contador para manejar el anidamiento

            # Recolección del bloque (misma lógica que el bloque Si)
            while i < len(codigo) and nivel > 0:
                l = codigo[i].strip()
                if l.startswith("Mientras") and "Hacer" in l:
                    nivel += 1
                elif l == "FinMientras":
                    nivel -= 1
                    if nivel == 0:
                        i += 1
                        break
                if nivel > 0:
                    bloque.append(codigo[i])
                i += 1

            # Ejecución del bucle
            contador_seguridad = 0
            while evaluar(condicion):
                # Ejecuta el bloque de forma recursiva
                interpretar(bloque)
                contador_seguridad += 1
                
                # Medida de seguridad para evitar bucles infinitos
                if contador_seguridad > 10000:
                    raise RuntimeError("Posible bucle infinito detectado. Límite de 10000 iteraciones alcanzado.")
            continue

        # ----------------------------------------
        # 8. Error de Sintaxis
        # Si la línea no coincide con ningún patrón, se considera un error.
        # ----------------------------------------
        raise SyntaxError(f"Línea no reconocida/Sintaxis inválida: {linea}")

# ----------------------------------------
# --- PROGRAMA DE EJEMPLO COMPLETO ---
codigo = [
    '# --- Declaraciones ---',
    'entero x = 5;',
    'entero y = 10;',
    'entero z = 0;',
    'cadena nombre = "Juan";',
    'cadena saludo = "Hola";',

    '# --- Condicional simple ---',
    'Si x < y Entonces',
    '    Imprimir("x es menor que y");',
    '    Si nombre == "Juan" Entonces',
    '        Imprimir("Bienvenido " + nombre);',
    '    FinSi',
    'FinSi',

    '# --- Bucle mientras ---',
    'Mientras x < 8 Hacer',
    '    Imprimir("Iteración con x=" + str(x));',
    '    entero x = x + 1;',
    'FinMientras',

    '# --- Operaciones combinadas ---',
    'entero z = x + y;',
    'Imprimir("El resultado de x+y es: " + str(z));',

    '# --- Condición combinada ---',
    'Si z > 10 and nombre == "Juan" Entonces',
    '    Imprimir("Condición doble cumplida");',
    'FinSi',

    '# --- Pausa de usuario ---',
    'Pausar();',

    '# --- Salida final ---',
    'Imprimir("Programa finalizado. Variables:");',
    'Imprimir("x=" + str(x) + ", y=" + str(y) + ", z=" + str(z));'
]

# Ejecutar el programa
interpretar(codigo)

# ----------------------------------------
# --- Código a interpretar (Programa Fuente) ---
codigo = [
    'entero x = 18;',
    'entero y = 25;',
    'entero z = 5;',
    'cadena nombre = "Juan";',
    'cadena apellido = "Pérez";',
    'cadena otronombre = "pepe";',
    '',
    'Si x >= 18 Entonces',
    '    Imprimir("Nivel 1: Mayor de edad");',
    '    Si y > x Entonces',
    '        Imprimir("Nivel 2: y > x");',
    '        Si z < 10 Entonces',
    '            Imprimir("Nivel 3: z < 10");',
    '            Si nombre == "Juan" Entonces',
    '                Imprimir("Nivel 4: nombre es Juan");',
    '            FinSi',
    '        FinSi',
    '    FinSi',
    'FinSi',
    '',
    'Si otronombre == "pepe" Entonces',
    '    Imprimir("Nivel 1: otronombre es pepe");',
    '    Si x + y > 40 and z < 10 Entonces',
    '        Imprimir("Nivel 2: x+y>40 y z<10");',
    '        Si apellido == "Pérez" Entonces',
    '            Imprimir("Nivel 3: apellido es Pérez");',
    '        FinSi',
    '    FinSi',
    'FinSi',
    '',
    'Si x < 10 or y > 20 Entonces',
    '    Imprimir("Nivel 1: alguna condición combinada se cumple");',
    'FinSi',
    '',
    'Mientras x < 10005 Hacer',
    '    Imprimir(x);',
    '    entero x = x + 1;',
    'FinMientras',
    'Pausar();',
    'Imprimir("Fin del programa. Variables: " + nombre + ", " + otronombre + ", " + apellido + ", x=" + str(x) + ", y=" + str(y) + ", z=" + str(z));'
]

# Inicia la interpretación del programa
interpretar(codigo)