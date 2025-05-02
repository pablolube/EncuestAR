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

# Este diccionario contiene los nombres de los aglomerados según su número
REGIONES_NOMBRES = {
    1 : "Gran Buenos Aires",
    40 : "Noroeste", 
    41 : "Noreste", 
    42 : "Cuyo", 
    43 : "Pampeana", 
    44 : "Patagonia" }

# Definición de los niveles educativos
niveles_educativos = {
    1: "Primario incompleto / Ed. especial",
    2: "Primario completo",
    3: "Secundario incompleto",
    4: "Secundario completo",
    5: "Superior universitario incompleto",
    6: "Superior universitario completo",
    7: "Sin instrucción"
 }

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 1 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------

def imprimir_alfabetizadas(diccionario):
    """
    Realiza calculos porcentuales 

    Imprime la cantidad de personas alfabetizadas por año.

    Args:
    :param diccionario: Diccionario con los datos de alfabetización.
    """
    print(f"{'Año':<10}{'% Alfabetos':>15}{'% No Alfabetos':>20}")
    print("-" * 45)

    # Calculo resultados porcentuales por año
    for anio in sorted(diccionario.keys()):
        valor_alf = diccionario[anio]["A"]
        valor_nalf = diccionario[anio]["NA"]
        total = valor_alf + valor_nalf

        porcentaje_alf = round((valor_alf / total) * 100, 2) if total > 0 else 0.0
        porcentaje_Nalf = round((valor_nalf / total) * 100, 2) if total > 0 else 0.0

        # Imprimo resultados
        print(f"{anio:<10}{porcentaje_alf:>15.2f}%{porcentaje_Nalf:>20.2f}%")

def cant_personas_alfabetizadas(data):
    """
    Cuenta la cantidad de personas alfabetizadas en el archivo CSV por año.
    Se clasifican a las personas que tengan 6 años o más.

    Args:
    :param data: lista de datos del dataset.
    """

    # Inicializa el contador
    count = {}

    # Itera sobre cada fila del lector CSV
    for row in data:

        # Si el año no existe, lo crea
        if row["ANO4"] not in count:
            # ----------------------- Crea un diccionario de diccionarios no?
            count[row["ANO4"]] = {"A": 0, "NA": 0}

        # Analiza solo si la edad (CH06) mayor a 6 años
        if row["CH06"] > "6" :
            if row["CH09"] == "1":
                count[row["ANO4"]]["A"] += int(row["PONDERA"])
            else:
                count[row["ANO4"]]["NA"] += int(row["PONDERA"])

    imprimir_alfabetizadas(count)

# --------------------------------------------------------------------
# FUNCIONES PUNTO 2 (ANÁLISIS) - INDIVIDUOS
# --------------------------------------------------------------------

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

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 3 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 4 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------

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
        conteo_hogares_ponderados[aglomerado] = conteo_hogares_ponderados.get(
            aglomerado, 0) + pondera
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
        con_universitarios = total_hogares_con_universitarios.get(
            aglomerado, 0)
        porcentaje = (con_universitarios / total) * 100 if total > 0 else 0
        print(
            f"Procesando aglomerado: {aglomerado}, Total: {total}, Universitarios: {con_universitarios}")
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
    print(
        f"Ranking de los {cantidad} aglomerados con mayor porcentaje de hogares con 2 o más universitarios:")
    for i, aglomerado_info in enumerate(top_aglomerados[:cantidad], 1):
        aglomerado_num = aglomerado_info["AGLOMERADO"]
        porcentaje = aglomerado_info["PORCENTAJE"]
        # Aseguramos que sea un entero para buscar bien
        aglomerado_num_int = int(aglomerado_num)
        nombre_aglomerado = AGLOMERADOS_NOMBRES.get(
            aglomerado_num_int, "Desconocido")

        print(
            f"{i}. Aglomerado {aglomerado_num} - {nombre_aglomerado}: {porcentaje:.2f}%")
        
# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 7 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------

def imprimo_info_porcentual_educacionsuperior_aglomerado(resultado):
    """
    Imprime el porcentaje de personas mayores de 18 años que cursaron al menos nivel universitario o superior,
    agrupado por aglomerado.

    Parámetros:
    :param resultado: dict con los resultados a imprimir.
    """
 
    # Imprimo encabezado
    print(f"{'Aglomerado':<40}{'Porcentaje (%)':>15}")
    print("-" * 55)

    # Imprimo los resultados ordenados por porcentaje de mayor a menor
    for aglo, porcentaje in sorted(resultado.items(), key=lambda x: x[1], reverse=True):
        nombre_aglo = AGLOMERADOS_NOMBRES.get(int(aglo), "Desconocido")
        aglo_texto = f"{aglo} - {nombre_aglo}"
        print(f"{aglo_texto:<40}{porcentaje:>15.2f}%")


def info_porcentual_educacionsuperior_aglomerado(data):
    """
    Calcula el porcentaje de personas mayores de 18 años que cursaron al menos nivel universitario o superior,
    agrupado por aglomerado.

    Parámetros:
    :param data: lista de datos del dataset.

    Genera:
    dict: Claves son aglomerados, valores son porcentajes (float).
    """
    # Inicializa el diccionario para almacenar los resultados
    resultado = {}
    conteo = {}

    # Itera sobre cada fila del lector CSV
    for row in data:

        #if row["CH06"] is None or row["NIVEL_ED_str"] is None or row["AGLOMERADO"] is None or int(row["PONDERA"]) is None:
            #continue  # salteamos registros incompletos

        # Acumulo por aglomerado, si no existe lo inicializo
        if row["AGLOMERADO"] not in conteo:
            conteo[row["AGLOMERADO"]] = {'total_mayores': 0, 'universitarios': 0}

        # Acumulo el total de mayores de edad sobre el cual se calculará el porcentaje
        if int(row["CH06"]) >= 18:
            conteo[row["AGLOMERADO"]]['total_mayores'] += int(row["PONDERA"])
            # Acumulo el total de universitarios
            if row["NIVEL_ED_str"] == "Superior o universitario":
                conteo[row["AGLOMERADO"]]['universitarios'] += int(row["PONDERA"])

    # Calculo el porcentaje por aglomerado
    for row["AGLOMERADO"] in conteo:
        total = conteo[row["AGLOMERADO"]]['total_mayores']
        nivel_sup = conteo[row["AGLOMERADO"]]['universitarios']
        resultado[row["AGLOMERADO"]] = round((nivel_sup / total) *
                                100, 2) if total > 0 else 0.0

    # Imprimo resultados
    imprimo_info_porcentual_educacionsuperior_aglomerado(resultado)


# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 8 (ANÁLISIS) - HOGARES
# -----------------------------------------------------------------------------------

def imprimo_ranking_inquilinos_por_region(ranking):
    """
    Imprime el ranking de regiones según el porcentaje de inquilinos.
    """
    # Encabezado
    print(f"{'Puesto':<8}{'Región':<30}{'Porcentaje de Inquilinos (%)':>30}")
    print("-" * 70)
    
    # Imprimir el ranking
    for i, (region, porcentaje) in enumerate(ranking, start=1):
        nombre_reg = REGIONES_NOMBRES.get(int(region))
        print(f"{i:<8}{region} - {nombre_reg:<30}{porcentaje:>10.2f}%")


def ranking_inquilinos_por_region(data_hogares):
    """
    Calcula el ranking de regiones según el porcentaje de inquilinos, en orden descendente.

    Parámetros:
    data_hogar (list): Lista de registros EPH (diccionarios).

    Retorna:
    Lista de tuplas (REGION, porcentaje) ordenadas de mayor a menor.
    """
    # Inicializa un diccionario para almacenar el conteo de inquilinos y el total de hogares por región
    conteo = {}

    for row in data_hogares:

        # Nombro variables para mejor legibilidad
        region = row["REGION"]
        inquilino = row["II7"]
        pondera = int(row["PONDERA"])

         # Salteamos registros incompletos
        if region is None or inquilino is None or pondera is None:
            continue
        
        # Inicializa el conteo para la región si no existe
        if region not in conteo:
            conteo[region] = {'total': 0, 'inquilinos': 0}
        # Acumulo total de hogares de la region 
        conteo[region]['total'] += pondera

        # Acumulo total de inquilinos de la region
        if int(inquilino) == 3:  # código de inquilino
            conteo[region]['inquilinos'] += pondera

    ranking = []

    # Itero sobre el conteo para calcular el porcentaje de inquilinos por región
    for region, datos in conteo.items():
        total = datos['total']
        inqui = datos['inquilinos']
        porcentaje = round((inqui / total) * 100, 2) if total > 0 else 0.0

        # Agrego a la lista de ranking
        ranking.append((region, porcentaje))

    # Ordenar de mayor a menor porcentaje
    ranking.sort(key=lambda x: x[1], reverse=True)

    # Imprimo el ranking
    imprimo_ranking_inquilinos_por_region(ranking)

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 9 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------

def imprimo_tabla_nivel_educativo(conteo):
    """
    Imprime la tabla con cantidad de personas mayores de 18 por nivel educativo,
    agrupada por año y trimestre.

    Parámetros:
    conteo: dict con los resultados a imprimir.
    """

    # Imprimir tablas por aglomerado
    for aglo, anios_trimestres in conteo.items():
        # Encabezado por aglomerado
        print(f"{'='*350}")
        nombre_aglo = AGLOMERADOS_NOMBRES.get(int(aglo), "Desconocido")
        print(f"{'Aglomerado ':<15}{aglo} - {nombre_aglo}")
        print(f"{'*'*350}")

        # Encabezado de la tabla con los niveles educativos
        print(f"{'Año':<8}{'Trimestre':<12}", end="")
        for nivel in range(1, 8):
            print(f"{niveles_educativos[nivel]:<40}", end="")
        print()
        print("*" * 350)

        # Imprimir los datos de cada aglomerado
        for (anio, trimestre), niveles in anios_trimestres.items():
            print(f"{anio:<8}{trimestre:<12}", end="")
            for nivel in range(1, 8):
                # Imprimir la ponderación de cada nivel educativo
                print(f"{int(niveles[nivel]):<40}", end="")
            print()


def tabla_nivel_educativo(data, aglomerado):

    """
    Genera una tabla con cantidad de personas mayores de 18 por nivel educativo,
    agrupada por año y trimestre, para el aglomerado ingresado.

    Parámetros:
    data: Lista de registros EPH (diccionarios).
    aglomerado: Código del aglomerado seleccionado.

    """

    # Inicializa el diccionario para almacenar los resultados 
    conteo = {} 

    # Verifica si el aglomerado existe en los datos
    aglomerado_encontrado = False

    for row in data:

        # Asegúrate de que los valores sean enteros y no nulos
        try:
            aglo = int(row["AGLOMERADO"])
            edad = int(row["CH06"])
            nivel_ed = int(row["NIVEL_ED"])
            anio = int(row["ANO4"])
            trimestre = int(row["TRIMESTRE"])
            pondera = int(row["PONDERA"])
        except (ValueError, KeyError):
            continue  # Ignorar filas con valores erróneos o incompletos

        # Verificamos condiciones
        if edad >= 18 and nivel_ed in range(1, 8) and aglo == int(aglomerado):
            aglomerado_encontrado = True
            if aglo not in conteo:
                conteo[aglo] = {}

            if (anio, trimestre) not in conteo[aglo]:
                conteo[aglo][(anio, trimestre)] = {nivel: 0 for nivel in range(1, 8)}

            conteo[aglo][(anio, trimestre)][nivel_ed] += pondera

    # Si no se encontró el aglomerado, imprimir un mensaje de advertencia
    if not aglomerado_encontrado:
        print(f"No se encontraron registros para el aglomerado {aglomerado}.")
    else:
        # Imprimo tabla final
        imprimo_tabla_nivel_educativo(conteo)



