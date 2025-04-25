
# PROCESAMIENTO HOGARES
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
                                    .

    Returns:
        str: Tipo de techo clasificado como:
            - "Material durable": si el número del material está entre 1 y 4.
            - "Material precario": si el número del material está entre 5 y 7.
            - "No aplica": si el número del material es 9.
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
    """
    Clasifica la densidad del hogar según la cantidad de personas y habitaciones.

    La clasificación se realiza dividiendo la cantidad de personas entre la cantidad de habitaciones,
    y asignando una categoría de densidad según el valor obtenido.
    Parameters:
        cant_personas (int or str): Cantidad de personas en el hogar. Puede ser un número entero o una cadena.
        cant_hab (int or str): Cantidad de habitaciones del hogar. Puede ser un número entero o una cadena.

    Returns:
        str: La clasificación de la densidad del hogar:
            - "Bajo" si la densidad es menor a 1 persona por habitación.
            - "Medio" si la densidad está entre 1 y 2 personas por habitación.
            - "Alto" si la densidad es mayor a 2 personas por habitación.
    """

    cant_hab=int(cant_hab)
    cant_personas=int(cant_personas)

    # Intentamos dividir las variables
    personas_por_hab = float(cant_personas / cant_hab)

        # Clasificación según la densidad
    if personas_por_hab < 1:
        tipo = "Bajo"
    elif 1 <= personas_por_hab <= 2:
        tipo = "Medio"
    elif personas_por_hab > 2:
        tipo = "Alto"
        
    return tipo

def clasificar_hogar_habitabilidad(agua, origen_agua, baño, ubi_baño, tipo_baño, desague, techo_material, piso_material):
 
    agua=int(agua)
    origen_agua=int(origen_agua)
    baño=int(baño)
    tipo_baño=int(tipo_baño)
    desague=int(desague)
    piso_material=int(piso_material)
    
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
    if  ubi_baño == 2:  # Baño fuera de la vivienda, pero dentro del terreno
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

