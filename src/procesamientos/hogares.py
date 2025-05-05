
# ------------------------------------------------------------------------------
# PROCESAMIENTO HOGARES
# ------------------------------------------------------------------------------
def clasificar_hogar_hab(cant_personas):
    """
    Clasifica un hogar según la cantidad de personas que lo habitan.

    Parameters:
        cant_personas (int or str): Cantidad de personas en el hogar. Puede ser un entero o una cadena que represente un número.

    Returns:
        str: Tipo de hogar clasificado como:
            - "Unipersonal": si hay 1 persona
            - "Nuclear": si hay entre 2 y 4 personas
            - "Extendido": si hay 5 o más personas
    """

    personas = int(cant_personas)

    if personas == 1:
        tipo = "Unipersonal"
    elif 2 <= personas <= 4:
        tipo = "Nuclear"
    elif personas >= 5:
        tipo = "Extendido"
    return tipo

def clasificar_hogar_densidad_hab(cant_personas, cant_hab):
    try:
        cant_personas = int(cant_personas)
        cant_hab = int(cant_hab)

        if cant_hab == 0:
            return "Desconocido"  # Evitar división por cero

        personas_por_hab = cant_personas / cant_hab

        if personas_por_hab < 1:
            return "Bajo"
        elif personas_por_hab <= 2:
            return "Medio"
        else:
            return "Alto"

    except ValueError:
        return None  # Guarda este valor cuando hay error
   
def clasificar_hogar_techo(material_nro):
    """
    Clasifica el tipo de techo de un hogar según tipo de material.

    Parameters:
        material_nro (int or str): Número que representa el tipo de material del techo.

    Returns:
        str: Tipo de techo clasificado como:
            - "Material durable": si el número del material está entre 1 y 4.
            - "Material precario": si el número del material está entre 5 y 7.
            - "No aplica": si el número del material es 9 o si hay un error en el dato.
    """
    try:
        material_nro = int(material_nro)
    except (ValueError, TypeError):
        return 'No aplica'

    if 1 <= material_nro <= 4:
        tipo = "Material durable"
    elif 5 <= material_nro <= 7:
        tipo = "Material precario"
    elif material_nro == 9:
        tipo = "No aplica"
    return tipo

def clasificar_hogar_densidad_hab(cant_personas, cant_hab):
    try:
        cant_personas = int(cant_personas)
        cant_hab = int(cant_hab)

        if cant_hab == 0:
            return "Desconocido"  # Evitar división por cero

        personas_por_hab = cant_personas / cant_hab

        if personas_por_hab < 1:
            return "Bajo"
        elif personas_por_hab <= 2:
            return "Medio"
        else:
            return "Alto"

    except ValueError:
        return None  # Guarda este valor cuando hay error


def clasificar_hogar_habitabilidad(agua, origen_agua, banio, ubi_banio, tipo_banio, desague, techo_material, piso_material):
    ponderador = {
        "agua": {1: "buena", 2: "regular", 3: "insuficiente"},
        "origen_agua": {1: "buena", 2: "saludable", 4: "regular"},
        "banio": {1: "buena", 2: "insuficiente"},
        "tipo_banio": {1: "buena", 2: "saludable", 3: "regular"},
        "desague": {1: "buena", 2: "saludable", 3: "saludable", 4: "insuficiente"},
        "piso_material": {1: "buena", 2: "saludable", 3: "regular"},
        "ubi_banio": {1: "buena", 2: "saludable", 3: "insuficiente"},
        "techo_material": {"Material durable": "buena", "Material precario": "insuficiente", 9: "insuficiente"}
    }

    try:
        agua = int(agua)
        origen_agua = int(origen_agua)
        banio = int(banio)
        ubi_banio = int(ubi_banio)
        tipo_banio = int(tipo_banio)
        desague = int(desague)
        techo_material = int(techo_material)
        piso_material = int(piso_material)
    except ValueError:
        return None  # Si no se pueden convertir a int, retorna None

    # Condición inmediata de habitabilidad insuficiente
    if agua == 3 or banio == 2 or ubi_banio == 3:
        return "insuficiente"

    # Contar ponderaciones
    contador = {'buena': 0, 'saludable': 0, 'regular': 0, 'insuficiente': 0}
    variables = {
        "agua": agua,
        "origen_agua": origen_agua,
        "banio": banio,
        "tipo_banio": tipo_banio,
        "desague": desague,
        "piso_material": piso_material,
        "ubi_banio": ubi_banio,
        "techo_material": techo_material
    }

    for key, value in variables.items():
        categoria = ponderador[key].get(value)
        if categoria:
            contador[categoria] += 1

    # Clasificación final según cantidad de cada categoría
    if contador["insuficiente"] == 1 and contador["regular"] >= 2:
        return "insuficiente"
    elif contador["regular"] > 2:
        return "regular"
    elif contador["regular"] <= 2 and contador["buena"] < 3:
        return "saludable"
    else:
        return "buena"



def procesar_hogares(header, data):
    """
    Procesa los datos de los hogares y agrega nuevas columnas con clasificaciones.
    """

    # Agrego las nuevas columnas al header
    header.extend(["TIPO_HOGAR", "MATERIAL_TECHUMBRE",
                  "DENSIDAD_HOGAR", "CONDICION_DE_HABITABILIDAD"])

    # Recorro las fila y realizo los procesos
    for row in data:

        # Clasifico el tipo de hogar según el número total de personas en Unipersonal,Nuclear o extendido
        row['TIPO_HOGAR'] = clasificar_hogar_hab(row['IX_TOT'])

        # Clasifico  según el tipo de material del techo en Material durable,precario,no aplica
        row['MATERIAL_TECHUMBRE'] = clasificar_hogar_techo(row['IV4'])

        # Clasifico segun la densidad por hogar bajo,medio,alto
        row['DENSIDAD_HOGAR'] = clasificar_hogar_densidad_hab(
            row['IX_TOT'], row['IV2'])

        # Clasifico la condición de habitabilidad del hogar basado en varios atributos relacionados con la vivienda
        row['CONDICION_DE_HABITABILIDAD'] = clasificar_hogar_habitabilidad(
            row['IV6'], row['IV7'], row['IV8'], row['IV9'], row['IV10'], row['IV11'], row['MATERIAL_TECHUMBRE'], row['IV3'])
