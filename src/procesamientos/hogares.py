
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

    material_nro = int(material_nro)

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


def clasificar_hogar_habitabilidad(agua, origen_agua, baño, ubi_baño, tipo_baño, desague, techo_material, piso_material):
    try:
        agua = int(agua)
        origen_agua = int(origen_agua)
        baño = int(baño)
        tipo_baño = int(tipo_baño)
        desague = int(desague)
        piso_material = int(piso_material)

        problemas = 0

        # 1. Agua
        if agua == 2:  # Agua fuera de la vivienda, pero dentro del terreno
            problemas += 2
        elif agua == 3:  # Agua fuera del terreno
            problemas += 3

        # 2. Origen del agua
        if origen_agua == 2:  # Perforación con bomba a motor
            problemas += 1
        elif origen_agua == 3:  # Perforación con bomba manual
            problemas += 2
        elif origen_agua == 4:  # Otra fuente
            problemas += 3

        # 3. Baño
        if baño == 2:
            return 'Insuficiente'

        # 4. Ubicación del baño
        if ubi_baño == 2:  # Baño fuera de la vivienda, pero dentro del terreno
            problemas += 1
        elif ubi_baño == 3:   # Baño fuera del terreno
            problemas += 2

        # 5. Tipo de baño
        if tipo_baño == 1:  # Inodoro con arrastre de agua
            problemas += 0
        elif tipo_baño == 2:  # Inodoro sin arrastre de agua
            problemas += 3
        else:  # Letrina
            problemas += 4

        # 6. Desagüe del baño
        if desague == 2:  # Desagüe a cámara séptica o pozo ciego
            problemas += 1
        elif desague == 3:  # Desagüe solo a pozo ciego
            problemas += 2
        elif desague == 4:  # Desagüe a hoyo/excavación
            problemas += 3

        # 7. Material del techo
        if techo_material == "Material precario":
            problemas += 6

        # 8. Material del piso
        if piso_material == 2:
            problemas += 1
        else:  # Material precario
            problemas += 2

        # Clasificación final según los problemas
        if problemas >= 10:
            return "Insuficiente"
        elif 6 <= problemas < 10:
            return "Regular"
        elif 4 <= problemas < 6:
            return "Saludable"
        else:
            return "Buena"
    except ValueError:
        return None  # Guarda este valor cuando hay error


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
