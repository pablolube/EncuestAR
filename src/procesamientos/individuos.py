# Este diccionario contiene los nombres de los aglomerados según su número
AGLOMERADOS_NOMBRES = {
    2: "Gran La Plata",
    3: "Bahía Blanca - Cerri",
    4: "Gran Rosario",
    5: "Gran Santa Fe",
    6: "Gran Paraná",
    7: "Posadas",
    8: "Gran Resistencia",
    9: "Comodoro Rivadavia - Rada Tilly",
    10: "Gran Mendoza",
    12: "Corrientes",
    13: "Gran Córdoba",
    14: "Concordia",
    15: "Formosa",
    17: "Neuquén - Plottier",
    18: "Santiago del Estero - La Banda",
    19: "Jujuy - Palpalá",
    20: "Río Gallegos",
    22: "Gran Catamarca",
    23: "Gran Salta",
    25: "La Rioja",
    26: "Gran San Luis",
    27: "Gran San Juan",
    29: "Gran Tucumán - Tafí Viejo",
    30: "Santa Rosa - Toay",
    31: "Ushuaia - Río Grande",
    32: "Ciudad Autónoma de Buenos Aires",
    33: "Partidos del GBA",
    34: "Mar del Plata",
    36: "Río Cuarto",
    38: "San Nicolás - Villa Constitución",
    91: "Rawson - Trelew",
    93: "Viedma - Carmen de Patagones",
}




def add_data_ch04str(row):
    """
    Agrega la clasificación Masculino/Femenino a la columna ch4_str.

    Args:
    :param row: Fila a la que se le agregarán las columnas.
    """

    row["CH04_str"] = "Masculino" if row["CH04"] == "1" else "Femenino"


def add_data_nivel_ed_str(row):
    """
    Agrega la clasificación de nivel educativo a la columna nivel_ed_str.

    Args:
    :param row: Fila a la que se le agregarán las columnas.
    """

    match row["NIVEL_ED"]:
        case "1":
            row["NIVEL_ED_str"] = "Primario incompleto"
        case "2":
            row["NIVEL_ED_str"] = "Primario completo"
        case "3":
            row["NIVEL_ED_str"] = "Secundario incompleto"
        case "4":
            row["NIVEL_ED_str"] = "Secundario completo"
        case "5" | "6":
            row["NIVEL_ED_str"] = "Superior o universitario"
        case "7" | "9":
            row["NIVEL_ED_str"] = "Sin Información"


def add_data_cond_lab(row):
    """
    Agrega la clasificación de condición laboral a la columna CONDICION_LABORAL.

    Args:
    :param row: Fila a la que se le agregarán las columnas.
    """

    estado = int(row["ESTADO"])
    cat_ocup = int(row["CAT_OCUP"])

    if estado == 1 and cat_ocup in (1, 2):
        row["CONDICION_LABORAL"] = "Ocupado autónomo"
    elif estado == 1 and cat_ocup in (3, 4, 9):
        row["CONDICION_LABORAL"] = "Ocupado dependiente"
    elif estado == 2:
        row["CONDICION_LABORAL"] = "Desocupado"
    elif estado == 3:
        row["CONDICION_LABORAL"] = "Inactivo"
    else:
        row["CONDICION_LABORAL"] = "Fuera de categoría/sin información"


def add_data_universitario(row):
    """
    Agrega la clasificación de nivel universitario a la columna UNIVERSITARIO.

    Args:
    :param row: Fila a la que se le agregarán las columnas.
    """

    if int(row["CH06"]) < 18:  # CH06 es la edad
        row["UNIVERSITARIO"] = 2
        return

    row["UNIVERSITARIO"] = 1 if row["CH12"] == "8" or row["CH12"] == "7" and row["CH13"] == "1" else 0


def imprimir_alfabetizadas(diccionario):
    """
    Imprime la cantidad de personas alfabetizadas por año.

    Args:
    :param diccionario: Diccionario con los datos de alfabetización.
    """

    print("Año\tAlfabetizados\tNo alfabetizados")
    for key, value in diccionario.items():
        print(f"{key}\t{value['A']}\t\t{value['NA']}")


def cant_personas_alfabetizadas(data):
    """
    Cuenta la cantidad de personas alfabetizadas en el archivo CSV por año.
    Se clasifican a las personas que tengan 2 años o más.

    Args:
    :param data: lista de datos del dataset.
    """

    # Inicializa el contador
    count = {}

    # Itera sobre cada fila del lector CSV
    for row in data:

        # Si el año no existe, lo crea
        if row["ANO4"] not in count:
            count[row["ANO4"]] = {"A": 0, "NA": 0}

        # Analiza solo si está en el trimestre 4 y edad (CH06) mayor a 6 años
        if row["CH06"] > "6" and row["TRIMESTRE"] == "4":
            if row["CH09"] == "1":
                count[row["ANO4"]]["A"] += int(row["PONDERA"])
            else:
                count[row["ANO4"]]["NA"] += int(row["PONDERA"])

    imprimir_alfabetizadas(count)


def porc_extranjero_universitario(anio, trim, data):
    """
    Imprime el % de personas extranjeras que hayan cursado el nivel universitario o superior.

    Args:
    :anio: año a analizar.
    :trim: trimestre a analizar.
    :param data: lista de datos del dataset.
    """

    count = {"argentino": 0, "extranjero": 0}

    for row in data:
        if row["ANO4"] == anio and row["TRIMESTRE"] == trim and row["NIVEL_ED_str"] == "Superior o universitario":
            # CH15 donde nacio
            if int(row["CH15"]) in (4, 5):
                count["extranjero"] += int(row["PONDERA"])
            else:
                count["argentino"] += int(row["PONDERA"])

    try:
        porcentaje = (count["extranjero"] /
                      (count["argentino"] + count["extranjero"])) * 100
    except ZeroDivisionError:
        porcentaje = 0

    print(
        f"El % de personas extranjeras que han cursado el nivel superior o universitario en el trimestre {trim} del año {anio} es del: {porcentaje:.2f}%")


def info_menor_desocupacion(data):
    """
    Informa el año y trimestre donde hubo menor desocupación
    y la cantidad de personas desocupadas.

    Args:
    :param data: lista de datos del dataset
    """

    # Filtra los datos para obtener solo los desocupados
    desocupados = filter(
        lambda x: x["CONDICION_LABORAL"] == "Desocupado", data)

    # Inicializa un diccionario para almacenar la cantidad de desocupados por año y trimestre
    total_trim = {}

    # Itera sobre cada fila de los desocupados para acumular el total por año y trimestre
    for row in desocupados:
        if row["ANO4"] not in total_trim:
            total_trim[row["ANO4"]] = {}
        if row["TRIMESTRE"] not in total_trim[row["ANO4"]]:
            total_trim[row["ANO4"]][row["TRIMESTRE"]] = 0

        total_trim[row['ANO4']][row["TRIMESTRE"]] += int(row["PONDERA"])

    # Se obtiene el menor valor de desocupacion
    min_valor = min(valor for trimestres in total_trim.values()
                    for valor in trimestres.values())

    resultados = []
    for anio, trimestres in total_trim.items():
        for trimestre, valor in trimestres.items():
            if valor == min_valor:
                resultados.append((anio, trimestre))

    print(
        f"Valor mínimo de desocupación: {min_valor} en los siguientes años y trimestres:")
    for anio, trimestre in resultados:
        print(f"Año: {anio}, Trimestre: {trimestre}")


# Funciones para el Ejercicio 4 de la Sección B 

# Se espera que el archivo de individuos ya esté procesado y contenga las columnas necesarias.
# Se asume que el archivo de individuos tiene las siguientes columnas:
# CODUSU, NRO_HOGAR, ANO4, TRIMESTRE, AGLOMERADO, PONDERA, UNIVERSITARIO

def contar_universitarios_y_pondera_por_hogar(individuos):
    """
    Cuenta cuántas personas con UNIVERSITARIO == '1' hay por hogar y guarda el PONDERA de ese hogar.
    
    Retorna dos diccionarios:
      - universitarios_por_hogar: clave = (CODUSU, NRO_HOGAR, ANO4, TRIMESTRE, AGLOMERADO), valor = cantidad de universitarios
      - pondera_por_hogar: misma clave, valor = PONDERA (una sola vez por hogar) 
      (Aclaración: se guarda el PONDERA de cada hogar)
    """
    universitarios_por_hogar = {}
    pondera_por_hogar = {}

    for row in individuos:
        clave = (
            row["CODUSU"],
            row["NRO_HOGAR"],
            row["ANO4"],
            row["TRIMESTRE"],
            row["AGLOMERADO"]
        )

        # Guardar el pondera solo una vez por hogar
        if clave not in pondera_por_hogar:
            pondera_por_hogar[clave] = float(row["PONDERA"])

        # Contar personas con estudios universitarios
        if row.get("UNIVERSITARIO") == "1":
            if clave in universitarios_por_hogar:
                universitarios_por_hogar[clave] += 1
            # Primera vez que encontramos una persona con UNIVERSITARIO == "1" en este hogar
            # Iniciamos el contador en 1 (no en 0, porque ya hay una persona)
            else:
                universitarios_por_hogar[clave] = 1

    return universitarios_por_hogar, pondera_por_hogar



def filtrar_hogares_con_min_universitarios(contador_universitarios, pondera_por_hogar, min_universitarios=2):
    """
    Filtra los hogares que tienen al menos 'min_universitarios' individuos con estudios universitarios o superiores
    y guarda el valor del PONDERA asociado a cada hogar.
    
    Parámetros:
    contador_universitarios (dict): Clave = hogar_id, valor = cantidad de individuos universitarios.
    pondera_por_hogar (dict): Clave = hogar_id, valor = PONDERA.
    min_universitarios (int): Mínimo requerido para incluir el hogar.
    
    Retorna:
    dict: Clave = hogar_id, valor = PONDERA del hogar.
    """
    hogares_filtrados = {}
    
    for hogar_id, cantidad_universitarios in contador_universitarios.items():
        if cantidad_universitarios >= min_universitarios:
            hogares_filtrados[hogar_id] = pondera_por_hogar[hogar_id]
            
    return hogares_filtrados


def contar_hogares(hogares_ponderados):
    """
    Cuenta hogares ponderados por aglomerado. También se usa para contar hogares filtrados por aglomerado.
    
    hogares_ponderados (dict): Clave = hogar_id, Valor = pondera del hogar.
    
    Retorna:
    - dict: Clave = aglomerado, Valor = suma de pondera.
    """
    conteo_hogares_ponderados = {}
    for clave_hogar, pondera in hogares_ponderados.items():
        aglomerado = clave_hogar[-1]  # Último elemento de la clave
        conteo_hogares_ponderados[aglomerado] = conteo_hogares_ponderados.get(aglomerado, 0) + pondera
    return conteo_hogares_ponderados



# Obtención de porcentajes y ranking 

def obtener_top_n_porcentaje_hogares_universitarios(total_hogares, total_hogares_con_universitarios, top_n=5):
    """
    Calcula el porcentaje de hogares con al menos 2 universitarios por aglomerado,
    ordena los resultados y devuelve el top N aglomerados con mayor porcentaje.

    Parámetros:
    - total_hogares (dict): Clave = (nro_aglomerado, nombre), valor = total de hogares (ponderado).
    - hogares_con_universitarios (dict): Clave = (nro_aglomerado, nombre), valor = hogares con 2+ universitarios (ponderado).
    - top_n (int): El número de aglomerados a devolver en el ranking (por defecto 5).

    Retorna:
    - list of dict: Los N primeros aglomerados con mayor porcentaje de hogares con al menos 2 universitarios.
    """
    # Calcular los porcentajes
    porcentajes = []
    for aglomerado, total in total_hogares.items():
        con_universitarios = total_hogares_con_universitarios.get(aglomerado, 0)
        porcentaje = (con_universitarios / total) * 100 if total > 0 else 0
        print(f"Procesando aglomerado: {aglomerado}, Total: {total}, Universitarios: {con_universitarios}")
        porcentajes.append({
            "AGLOMERADO": aglomerado,  # nro
            "PORCENTAJE": porcentaje
        })

    # Ordenar y devolver el top N
    return sorted(porcentajes, key=lambda aglomerado: aglomerado["PORCENTAJE"], reverse=True)[:top_n]



def imprimir_ranking_aglomerados(top_aglomerados, cantidad=5):
    """
    Imprime el ranking de aglomerados con su número, nombre y porcentaje de hogares con al menos 2 universitarios.

    Parámetros:
    - top_aglomerados (list of dict): Cada dict tiene "AGLOMERADO" (número) y "PORCENTAJE".
    - cantidad (int): Cuántos aglomerados mostrar. Por defecto 5.
    """
    print(f"Ranking de los {cantidad} aglomerados con mayor porcentaje de hogares con 2 o más universitarios:")
    for i, aglomerado_info in enumerate(top_aglomerados[:cantidad], 1):
        aglomerado_num = aglomerado_info["AGLOMERADO"]
        porcentaje = aglomerado_info["PORCENTAJE"]
        # Aseguramos que sea un entero para buscar bien
        aglomerado_num_int = int(aglomerado_num)
        nombre_aglomerado = AGLOMERADOS_NOMBRES.get(aglomerado_num_int, "Desconocido")
        
        print(f"{i}. Aglomerado {aglomerado_num} - {nombre_aglomerado}: {porcentaje:.2f}%")
        
        




#---------------- Fin de funciones para el Ejercicio 4 de la Sección B ------------------