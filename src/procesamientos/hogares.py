# ------------------------------------------------------------------------------
# PROCESAMIENTO HOGARES DETALLE
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
    """
    Clasifica la densidad habitacional de un hogar según la relación entre la cantidad de personas 
    y la cantidad de habitaciones.

    Parámetros:
        cant_personas (int o str): Número total de personas en el hogar.
        cant_hab (int o str): Número de habitaciones en el hogar.

    Retorna:
        str:
            - "Bajo" si hay menos de 1 persona por habitación.
            - "Medio" si hay entre 1 y 2 personas por habitación.
            - "Alto" si hay más de 2 personas por habitación.
            - "Desconocido" si la cantidad de habitaciones es 0 (para evitar división por cero).
        None: si los valores no son válidos (por ejemplo, texto que no se puede convertir a entero).
    """
    try:
        cant_personas = int(cant_personas)
        cant_hab = int(cant_hab)
       
        personas_por_hab = cant_personas / cant_hab

        if personas_por_hab < 1:
            return "Bajo"
        elif personas_por_hab <= 2:
            return "Medio"
        else:
            return "Alto"

    except (ValueError, TypeError, ZeroDivisionError):
        return None
   
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

def clasificar_hogar_habitabilidad(agua, origen_agua, banio, ubi_banio, tipo_banio, desague, techo_material, piso_material):

    """
    Clasifica el nivel de habitabilidad de un hogar en función de diversas variables relacionadas con
    el acceso a servicios básicos, materiales de construcción y condiciones sanitarias.

    Parámetros:
        agua (int): Acceso al agua (1: buena, 2: regular, 3: insuficiente).
        origen_agua (int): Fuente del agua (1: buena, 2: saludable, 3-4: regular).
        banio (int): Existencia de baño (0: insuficiente, 1: buena, 2: insuficiente).
        ubi_banio (int): Ubicación del baño (1: buena, 2: saludable, 3: insuficiente).
        tipo_banio (int): Tipo de baño (0: insuficiente, 1: buena, 2: saludable, 3: regular).
        desague (int): Tipo de desagüe (0 o 4: insuficiente, 1: buena, 2-3: saludable).
        techo_material (str): Material del techo ("Material durable", "Material precario", "No Aplica").
        piso_material (int): Material del piso (1: buena, 2: saludable, 3-4: regular).

    Returns:
        str or None: Nivel de habitabilidad. Posibles valores:
            - "buena"
            - "saludable"
            - "regular"
            - "insuficiente"
            - "otro"
            - None (si los valores no son válidos)
    """
    
    ponderador = {
        "agua": {1: "buena", 2: "regular", 3: "insuficiente"},
        "origen_agua": {1: "buena", 2: "saludable", 3: "regular", 4: "regular"},
        "banio": {0: "insuficiente", 1: "buena", 2: "insuficiente"},
        "tipo_banio": {0: "insuficiente", 1: "buena", 2: "saludable", 3: "regular"},
        "desague": {0: "insuficiente", 1: "buena", 2: "saludable", 3: "saludable", 4: "insuficiente"},
        "piso_material": {1: "buena", 2: "saludable", 3: "regular", 4: "regular"},
        "ubi_banio": {1: "buena", 2: "regular", 3: "insuficiente"},
        "techo_material": {
            "Material durable": "buena",
            "Material precario": "insuficiente",
            "No Aplica": "buena"
        }
    }

    try:
        agua = int(agua)
        origen_agua = int(origen_agua)
        banio = int(banio)
        ubi_banio = int(ubi_banio)
        tipo_banio = int(tipo_banio)
        desague = int(desague)
        piso_material = int(piso_material)
        techo_material = str(techo_material).strip()
    except ValueError:
        return None

    # Corte directo por condiciones críticas
    if agua == 3 or banio == 2 or ubi_banio == 3:
        return "insuficiente"

    # Contador por categoría
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

    # Clasificación según reglas
    if 0 < contador["insuficiente"] <=2 and contador["regular"] >= 2:
        return "insuficiente"
    
    elif contador["regular"] >= 5:
        return "insuficiente"

    elif 0 < contador["insuficiente"] <=2 and  contador["regular"] == 1:
        return "regular"

    elif desague == 4:
        return "regular"
    
    elif agua == 2:
        return "regular"
  
    
    elif contador["regular"] >= 3:  
        return "regular"
    
    elif contador["insuficiente"]==1 and contador["regular"] == 0:
        return "Saludable"
    
    elif contador["insuficiente"]<=2 and contador["regular"] == 0:
        return "Saludable"
    

    elif contador["buena"] >= 4:
        return "buena"
    
    else:
        return "buena"

from src.utils.helpers import extraer_fecha,actualizarmaxmin_fechas
# -------------------------------------------------------------------------------
# PROCESAMIENTO DE HOGARES
# -------------------------------------------------------------------------------

def procesar_hogares(header, data):
    """
    Procesa los datos de los hogares y agrega nuevas columnas con clasificaciones.
    """
    # Inicializo las fechas mínima y máxima
    min_fecha = None
    max_fecha = None

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
        
        fecha_actual = extraer_fecha(row)
        if fecha_actual:
            min_fecha, max_fecha = actualizarmaxmin_fechas(fecha_actual, min_fecha, max_fecha)
    return min_fecha, max_fecha


        
      



