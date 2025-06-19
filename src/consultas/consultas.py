from src.utils.constants import AGLOMERADOS_NOMBRES, REGIONES_NOMBRES, NIVELES_EDUCATIVOS
from collections import Counter

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 1 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------


def imprimir_alfabetizadas(data):
    """
    Realiza calculos porcentuales 

    Imprime el % de personas alfabetizadas por año.

    Args:
    :param data: data con los datos de alfabetización.
    """
    if not data:
        print("No hay datos para mostrar.")
        return

    print(f"{'Año':<10}{'% Alfabetos':>15}{'% No Alfabetos':>20}")
    print("-" * 45)

    # Calculo resultados porcentuales por año
    for anio in sorted(data.keys(), reverse=True):
        for trimestre in sorted(data[anio].keys(), reverse=True):
            if data[anio][trimestre]["A"] > 0 or data[anio][trimestre]["NA"] > 0:
                valor_alf = data[anio][trimestre]["A"]
                valor_nalf = data[anio][trimestre]["NA"]
                total = valor_alf + valor_nalf
                porcentaje_alf = round((valor_alf / total) * 100, 2)
                porcentaje_Nalf = round((valor_nalf / total) * 100, 2)
                print(f"{anio:<10}{porcentaje_alf:>15.2f}{porcentaje_Nalf:>20.2f}")
                break


def cantidad_alfabetizadas(data):
    """
    Devuelve la cantidad de personas alfabetizadas en el archivo CSV por el último trimestre de cada año.
    Se clasifican a las personas que tengan 6 años o más.

    Args:
    :param data: lista de datos del dataset.
    """

    count = {}

    for row in data:
        if row['CH06'] > '6' and row['CH09'] != '3' and row['PONDERA'].isdigit():
            if row['ANO4'] not in count:
                count[row['ANO4']] = {'1': {'A': 0, 'NA': 0}, '2': {'A': 0, 'NA': 0}, '3': {'A': 0, 'NA': 0}, '4': {'A': 0, 'NA': 0}}
            if row['CH09'] == '1':
                count[row['ANO4']][row['TRIMESTRE']]['A'] += int(row['PONDERA'])
            elif row['CH09'] == '2':
                count[row['ANO4']][row['TRIMESTRE']]['NA'] += int(row['PONDERA'])
    
    return count


# --------------------------------------------------------------------
# FUNCIONES PUNTO 2 (ANÁLISIS) - INDIVIDUOS
# --------------------------------------------------------------------

def porc_extranjero_universitario(anio, trim, data):
    """
    Devuelve el % de personas extranjeras que hayan cursado el nivel universitario o superior.

    Args:
    :anio: año a analizar.
    :trim: trimestre a analizar.
    :param data: lista de datos del dataset.
    """

    count = {'argentino': 0, 'extranjero': 0}

    for row in data:
        if row['ANO4'] == anio and row['TRIMESTRE'] == trim and row['NIVEL_ED_str'] == 'Superior o universitario':
            # CH15 donde nacio
            if row['CH15'] in ('4', '5') and row['PONDERA'].isdigit():
                count['extranjero'] += int(row['PONDERA'])
            else:
                count['argentino'] += int(row['PONDERA'])

    try:
        return (count['extranjero'] / (count['argentino'] + count['extranjero'])) * 100

    except ZeroDivisionError:
        return None



# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 3 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------

def imprimir_info_menor_desocupacion(data):

    print(f"{'Año':<10}{'Trimestre':<16}{'Desocupados':<18}")
    print("-" * 40)

    for anio, trimestre,cantidad in data:
        print(f"{anio:<10}{trimestre:<16}{cantidad:<18}")

def info_menor_desocupacion(data):
    """
    Informa el año y trimestre donde hubo menor desocupación y la cantidad de personas desocupadas.

    Args:
    :param data: lista de datos del dataset
    """

    desocupados = list(filter(lambda x: x["CONDICION_LABORAL"] == "Desocupado", data))

    if not desocupados:
        print("No hay datos de desocupación disponibles.")
        return None

    contador_desocupados = {}

    for row in desocupados:
        if row["ANO4"] not in contador_desocupados:
            contador_desocupados[row["ANO4"]] = {}
        if row["TRIMESTRE"] not in contador_desocupados[row["ANO4"]]:
            contador_desocupados[row["ANO4"]][row["TRIMESTRE"]] = 0
        contador_desocupados[row['ANO4']][row["TRIMESTRE"]] += int(row["PONDERA"])

    min_valor_desocupacion = min(valor for trimestres in contador_desocupados.values() for valor in trimestres.values())

    # Se guarda si hubo otros años y trimestres con el mismo valor que el minimo.
    resultados = []
    for anio, trimestres in contador_desocupados.items():
        for trimestre, valor in trimestres.items():
            if valor == min_valor_desocupacion:
                resultados.append((anio, trimestre,valor))

    return resultados



# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 4 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------

def contar_universitarios_y_pondera_por_hogar(individuos):
    """
    Cuenta cuántas personas con UNIVERSITARIO == '1' hay por hogar y guarda el PONDERA de ese hogar.

    Retorna dos diccionarios:
      - universitarios_por_hogar: clave = (CODUSU, NRO_HOGAR, ANO4, TRIMESTRE, AGLOMERADO), valor = cantidad de universitarios
      - pondera_por_hogar: misma clave, valor = PONDERA (una sola vez por hogar) 
    """
    universitarios_por_hogar = {}
    pondera_por_hogar = {}

    for row in individuos:
        try:
            clave = (
                row["CODUSU"],
                row["NRO_HOGAR"],
                row["ANO4"],
                row["TRIMESTRE"],
                int(row["AGLOMERADO"])
            )

            # Guardo el PONDERA solo una vez por hogar
            if clave not in pondera_por_hogar:
                pondera_por_hogar[clave] = float(row["PONDERA"])

            # Cuento personas con estudios universitarios
            if row.get("UNIVERSITARIO") == "1":
                if clave in universitarios_por_hogar:
                    universitarios_por_hogar[clave] += 1
                else:
                    universitarios_por_hogar[clave] = 1

        except (KeyError, ValueError) as e:
            # Para debuggear, podés activar este print:
            # print(f"Fila ignorada por error: {e} — Datos: {row}")
            continue

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
    Cuento hogares ponderados por aglomerado. Esta función también sirve para
    contar subconjuntos filtrados de hogares por aglomerado.

    Parámetros:
    - hogares_ponderados (dict): Diccionario con claves que identifican un hogar
      (tupla que incluye el aglomerado como último elemento) y valores que indican
      la ponderación del hogar.

    Retorno:
    - dict: Diccionario con claves de aglomerados y valores que indican la suma
      total de la ponderación de los hogares pertenecientes a cada aglomerado.
    """

    conteo_hogares_ponderados = {}  # Inicializo el diccionario resultado

    for clave_hogar, pondera in hogares_ponderados.items():
        # Extraigo el aglomerado, que es el último elemento de la tupla clave
        aglomerado = clave_hogar[-1]

        # Sumo la ponderación del hogar al total acumulado del aglomerado
        conteo_hogares_ponderados[aglomerado] = (
            conteo_hogares_ponderados.get(aglomerado, 0) + pondera
        )

    return conteo_hogares_ponderados
 
def generar_ranking_hogares_universitarios(individuos, min_universitarios=2, top_n=5):
    """
    Genera y muestra un ranking de aglomerados según el porcentaje de hogares
    con al menos 'min_universitarios' personas con estudios universitarios.
    """
    # Cuento universitarios por hogar y obtener PONDERA por hogar
    universitarios_por_hogar, pondera_por_hogar = contar_universitarios_y_pondera_por_hogar(individuos)

    # Verificación: ¿hay datos válidos?
    if not universitarios_por_hogar or not pondera_por_hogar:
        print("❌ Error: no hay datos válidos para generar el ranking. Verifique el archivo de entrada.")
        return

    # Cuento hogares totales por aglomerado
    total_hogares_por_aglomerado = contar_hogares(pondera_por_hogar)

    # Filtro hogares con al menos min_universitarios y contarlos por aglomerado
    hogares_filtrados = filtrar_hogares_con_min_universitarios(universitarios_por_hogar, pondera_por_hogar, min_universitarios)
    hogares_filtrados_por_aglomerado = contar_hogares(hogares_filtrados)

    # Armo resultados para cada aglomerado con (hogares_filtrados, total_hogares)
    resultados = {
        aglomerado: (hogares_filtrados_por_aglomerado.get(aglomerado, 0), total)
        for aglomerado, total in total_hogares_por_aglomerado.items()
    }

    # Calculo porcentajes y muestro ranking
    ranking = calcular_porcentajes(resultados)

    return ranking[:top_n]  # Retorno solo los primeros 'top_n' resultados ordenados 


# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 5 (ANÁLISIS) - HOGAR
# -----------------------------------------------------------------------------------


def contar_viviendas_propietarias(datos_hogares):
    """
    Procesa una lista de diccionarios de hogares y cuenta, para cada aglomerado:
      - El total ponderado de viviendas habitadas (tenencia entre 1 y 8).
      - El total ponderado de viviendas ocupadas por propietarios (tenencia 1 o 2).

    Args:
        datos_hogares (list of dict): Lista de registros de hogares.

    Returns:
        dict[int, list[float, float]]: aglomerado → [propietarias, totales]
    """
    PROPIETARIOS = {1, 2}
    TENENCIAS_VALIDAS = set(range(1, 9))  # 1 a 8 inclusive

    resultados = {}

    for fila in datos_hogares:
        try:
            aglomerado = int(fila["AGLOMERADO"])
            tenencia = int(fila["II7"].strip())
            pondera = int(fila["PONDERA"])
        except (ValueError, KeyError):
            continue

        # Salto registros con tenencia inválida
        if tenencia not in TENENCIAS_VALIDAS:
            continue

        if aglomerado not in resultados:
            resultados[aglomerado] = [0.0, 0.0]

        resultados[aglomerado][1] += pondera  # Total viviendas

        if tenencia in PROPIETARIOS:
            resultados[aglomerado][0] += pondera  # Viviendas propietarias

    return resultados


def calcular_porcentajes(resultados):
    """
    Dado el diccionario de resultados, devuelve una lista de tuplas:
    (aglomerado, nombre, porcentaje), ordenada en forma descendente.
    """
    lista = []
    for aglomerado, (propietarias, total) in resultados.items():
        if total > 0:
            porcentaje = ((propietarias / total) * 100)
        else:
            porcentaje = "0.0%"
        nombre = AGLOMERADOS_NOMBRES.get(aglomerado, "Nombre no disponible")
        lista.append((aglomerado, nombre, porcentaje))

    lista_ordenada = sorted(lista, key=lambda x: x[2], reverse=True)
    return lista_ordenada


def imprimir_tabla_ranking(porcentajes_por_aglomerado, cantidad=None):
    """
    Imprime el ranking de aglomerados en formato de tabla con columnas alineadas.

    Args:
        porcentajes_por_aglomerado (list of tuple): Lista de tuplas
            (aglomerado, nombre, porcentaje) ordenada de mayor a menor porcentaje.
        cantidad (int, opcional): Número de filas a mostrar. Si es None, muestra todas.
    """
    # Defino encabezados y calcular ancho dinámico
    encabezados = ["Puesto", "Código", "Aglomerado", "% Porcentaje"]
    formatos = ["{:<6}", "{:<6}", "{:<35}", "{:>15}"]
    header = "  ".join(fmt.format(txt)
                       for fmt, txt in zip(formatos, encabezados))
    separator = "-" * len(header)

    # Determino filas a mostrar
    filas = porcentajes_por_aglomerado if cantidad is None else porcentajes_por_aglomerado[
        :cantidad]

    # Imprimo encabezado y separador
    print(header)
    print(separator)

    # Imprimo cada fila con el mismo formato
    for i, (aglomerado, nombre, porcentaje) in enumerate(filas, start=1):
        print(
            f"{i:<6}  "
            f"{aglomerado:<6}  "
            f"{nombre:<35}  "
            f"{porcentaje:>14.2f}%"
        )

    
def procesar_y_mostrar_porcentajes(datos_hogares):
    """
    Ejecuta todo el procesamiento y la impresión del ranking de
    porcentajes de viviendas ocupadas por propietarios.

    Args:
        datos_hogares (list of dict): Lista de registros de hogares.
    """
    if not datos_hogares:
        print("❌ Error: no hay datos para realizar el análisis.")
        return

    # 1) Cuenta viviendas propietarias y totales por aglomerado
    resultados = contar_viviendas_propietarias(datos_hogares)

    if not resultados:
        print("❌ Error: no hay datos válidos para realizar el análisis.")
        return

    # 2) Calcula el porcentaje de viviendas propietarias
    porcentajes = calcular_porcentajes(resultados)

    if not porcentajes:
        print("❌ Error: no hay datos con tenencia válida para calcular porcentajes.")
        return

    return porcentajes    

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 6 (ANÁLISIS) - HOGAR
# -----------------------------------------------------------------------------------

def contar_viviendas_precarias(datos_hogares):
    """
    Cuenta la cantidad ponderada de viviendas precarias por aglomerado:
    - Más de 2 ocupantes
    - No tiene baño (IV8 == 2)

    Usa (CODUSU, NRO_HOGAR) como clave para evitar duplicados.
    """

    if not datos_hogares:
        print("❌ Error: no hay datos para realizar el análisis.")
        return {}

    viviendas_precarias_por_aglomerado = {}
    hogares_vistos = set()

    for fila in datos_hogares:
        try:
            clave_hogar = (fila["CODUSU"], fila["NRO_HOGAR"])
            if clave_hogar in hogares_vistos:
                continue
            hogares_vistos.add(clave_hogar)

            aglomerado = int(fila["AGLOMERADO"])
            ocupantes = int(fila["IX_TOT"])
            tiene_banio = int(fila["IV8"])  # 2 = no tiene baño
            pondera = int(fila["PONDERA"])
        except (ValueError, KeyError):
            continue

        if ocupantes > 2 and tiene_banio == 2:
            if aglomerado not in viviendas_precarias_por_aglomerado:
                viviendas_precarias_por_aglomerado[aglomerado] = 0
            viviendas_precarias_por_aglomerado[aglomerado] += pondera  # ponderado

    if not viviendas_precarias_por_aglomerado:
        print("❌ No se encontraron viviendas precarias.")
        return {}

    return viviendas_precarias_por_aglomerado


def aglomerado_con_mayor_cantidad_viviendas_precarias(datos_hogares):
    """
    Obtiene el aglomerado con la mayor cantidad de viviendas precarias (más de 2 ocupantes y sin baño).
    """
    viviendas_precarias_por_aglomerado = contar_viviendas_precarias(datos_hogares)

    if not viviendas_precarias_por_aglomerado:  # Verificamos si no hay resultados
        print("❌ No se encontraron viviendas precarias para realizar el análisis.")
        return None, 0

    # Encontramos el aglomerado con el máximo número de viviendas precarias
    aglomerado_max = max(viviendas_precarias_por_aglomerado, key=viviendas_precarias_por_aglomerado.get)
    cantidad_max = viviendas_precarias_por_aglomerado[aglomerado_max]

    print(f"Aglomerado con mayor cantidad de viviendas precarias (más de 2 ocupantes y sin baño):")
    print(f"Aglomerado {aglomerado_max} con {cantidad_max} viviendas.")

    return aglomerado_max, cantidad_max


# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 7 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------


def imprimir_info_porcentual_educacionsuperior_aglomerado(resultado):
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

        # if row["CH06"] is None or row["NIVEL_ED_str"] is None or row["AGLOMERADO"] is None or int(row["PONDERA"]) is None:
        # continue  # salteamos registros incompletos

        # Acumulo por aglomerado, si no existe lo inicializo
        if row["AGLOMERADO"] not in conteo:
            conteo[row["AGLOMERADO"]] = {
                'total_mayores': 0, 'universitarios': 0}

        # Acumulo el total de mayores de edad sobre el cual se calculará el porcentaje
        if int(row["CH06"]) >= 18:
            conteo[row["AGLOMERADO"]]['total_mayores'] += int(row["PONDERA"])
            # Acumulo el total de universitarios
            if row["NIVEL_ED_str"] == "Superior o universitario":
                conteo[row["AGLOMERADO"]
                       ]['universitarios'] += int(row["PONDERA"])

    # Calculo el porcentaje por aglomerado
    for row["AGLOMERADO"] in conteo:
        total = conteo[row["AGLOMERADO"]]['total_mayores']
        nivel_sup = conteo[row["AGLOMERADO"]]['universitarios']
        resultado[row["AGLOMERADO"]] = round((nivel_sup / total) *
                                             100, 2) if total > 0 else 0.0

    return resultado

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 8 (ANÁLISIS) - HOGARES
# -----------------------------------------------------------------------------------

def imprimir_ranking_inquilinos_por_region(ranking):
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
        try:
            region = row["REGION"]
            inquilino = row["II7"]
            pondera = int(row["PONDERA"])

            if region is None or inquilino is None:
                raise ValueError("Campos nulos")

            if region not in conteo:
                conteo[region] = {'total': 0, 'inquilinos': 0}

            conteo[region]['total'] += pondera

            if int(inquilino) == 3:
                conteo[region]['inquilinos'] += pondera

        except (ValueError, TypeError) as e:
            continue

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

    return ranking 

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
            print(f"{NIVELES_EDUCATIVOS[nivel]:<40}", end="")
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

    # Convertimos el aglomerado una sola vez
    aglomerado_normalizado = aglomerado.strip().lower()
    if aglomerado.isdigit():
        clave_aglo = int(aglomerado)
    else:
        clave_aglo = next((cod for cod, nombre in AGLOMERADOS_NOMBRES.items(
        ) if nombre.lower() == aglomerado_normalizado), None)
        if clave_aglo is None:
            raise ValueError(
                f"No se encontró un aglomerado con el nombre '{aglomerado}'.")

    # Inicializa el diccionario para almacenar los resultados
    conteo = {}

    # Procesamos los datos
    aglomerado_encontrado = False
    for row in data:
        try:
            aglo = int(row["AGLOMERADO"])
            edad = int(row["CH06"])
            nivel_ed = int(row["NIVEL_ED"])
            anio = int(row["ANO4"])
            trimestre = int(row["TRIMESTRE"])
            pondera = int(row["PONDERA"])
        except (ValueError, KeyError):
            continue

        # Condiciones de filtrado
        if edad >= 18 and nivel_ed in range(1, 8) and aglo == clave_aglo:
            aglomerado_encontrado = True
            if aglo not in conteo:
                conteo[aglo] = {}

            if (anio, trimestre) not in conteo[aglo]:
                conteo[aglo][(anio, trimestre)] = {
                    nivel: 0 for nivel in range(1, 8)}

            conteo[aglo][(anio, trimestre)][nivel_ed] += pondera

    if not aglomerado_encontrado:
        print(
            f"No se encontraron registros para el aglomerado '{aglomerado}'.")
    else:
        imprimo_tabla_nivel_educativo(conteo)

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 10 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------


def crear_estructura_datos():
    
    """
    Genera una estructura que se encargara de manejar los datos para guardarse
    en un solo recorrido del data
        
    return:
        Dict[]: diccionario con la estructura a cargar
        Cumplen_aglom_n: Individuos con el secundario incompleto y mayores de 18
         Todos_aglomn_18: Mayores a 18
    """
    return {
        "Cumplen_aglom_1": 0,
        "Todos_aglom1_18": 0,
        "Cumplen_aglom_2": 0,
        "Todos_aglom2_18": 0
    }


def personas_secundario_incompleto_anio_trimestre(aglomerado1, aglomerado2,  data):
    """
    Calcula el porcentaje de personas con secundario incompleto mayores de 18 años
    en dos aglomerados específicos, agrupando los resultados por año y trimestre.

    Args:
        aglomerado1 (int): Código del primer aglomerado a considerar.
        aglomerado2 (int): Código del segundo aglomerado a considerar.
        data (list[dict]): Lista de registros, cada uno representado como un diccionario
            que contiene las claves 'AGLOMERADO', 'NIVEL_ED_str', 'ANO4', 
            'TRIMESTRE', 'PONDERA' y 'CH06'.

    """
    # Inicializo la estructura de datos
    dats = {}

    for row in data:
        # guardo el aglomerado y nivel educativo de la persona actual

        try:
            aglo = int(row['AGLOMERADO'])
            nivel_ed = str(row['NIVEL_ED_str'])

            # creamos una clave anio trimestre que los vaya guardando en su respectivo bloque
            clave = (row['ANO4'], row['TRIMESTRE'])

            Pondera = int(row['PONDERA'])
            edad = int(row['CH06'])
        except (ValueError, KeyError):
            continue  # Saltar la fila si algo falló

        # para ir generando el archivo dats usamos

        if clave not in dats:
            dats[clave] = crear_estructura_datos()

        if aglo == aglomerado1:
            # revisamos si es mayor de edad
            if int(edad) >= 18:
                # y su nivel educativo
                if nivel_ed == "Secundario incompleto":
                    dats[clave]["Cumplen_aglom_1"] += Pondera

                # lo guarda para tener el general de individuos > 18
                dats[clave]['Todos_aglom1_18'] += Pondera
        elif aglo == aglomerado2:
            # revisamos si es mayor de edad
            if int(edad) >= 18:
                # y su nivel educativo
                if nivel_ed == "Secundario incompleto":
                    dats[clave]['Cumplen_aglom_2'] += Pondera

                # lo guarda para tener el general de individuos > 18
                dats[clave]['Todos_aglom2_18'] += Pondera

    return dats


def imprimir_porcentaje_secundario_incompleto(datos, aglo1, aglo2):

    """
    Imprime una tabla con los porcentajes de cumplimiento para dos aglomerados 
    a partir de un diccionario de datos organizados por año y trimestre.

    Parámetros:
        Datos(Dict[]) lista de diccionarios de clave Año trimestre
        De valor una estructura que recopila los mayores de 18 con educacion "Secundario Incompleto"
    """
    
    # Encabezado
    print(f"{'Año':^8} {'Trimestre':^8} {f'Aglomerado {aglo1}':^20} {
          f'Aglomerado {aglo2}':^20}")
    print("-" * 60)

    # sorted lo usa para ir imprimiendo ordenando por el par anio, trimestre
    for (anio, trimestre), valores in sorted(datos.items()):

        try:
            # Guardamos los valores de cada año trimestre
            cumplen1 = valores.get("Cumplen_aglom_1", 0)
            total1 = valores.get("Todos_aglom1_18", 0)
            cumplen2 = valores.get("Cumplen_aglom_2", 0)
            total2 = valores.get("Todos_aglom2_18", 0)

            # Calculamos porcentaje
            porcentaje1 = (cumplen1 / total1) * 100 if total1 > 0 else 0
            porcentaje2 = (cumplen2 / total2) * 100 if total2 > 0 else 0

            # Mejoramos el formato para la impresión
            porcentaje1 = f"{porcentaje1:.2f} %"
            porcentaje2 = f"{porcentaje2:.2f} %"

            # Imprimimos fila
            print(f"{anio:^8} {trimestre:^8} {porcentaje1:^20} {porcentaje2:^20}")

        except (KeyError, ValueError) as e:
            print(f"Error al procesar los datos para {anio}-{trimestre}: {e}")
            continue


# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 11 (ANÁLISIS) - HOGAR
# -----------------------------------------------------------------------------------

def obtener_datos_ultimo_trimestre(anio, data):
    """
    Obtiene los registros correspondientes al último trimestre disponible de un año específico.

    Args:
        anio (int or str): Año del cual se desea obtener la información del último trimestre.
        data (list[dict]): Lista de registros, cada uno representado como un diccionario 
            que contiene las claves 'ANO4' y 'TRIMESTRE'.

    """
    # A partir de un anio tomamos la data del ultimo trimestre

    # estructura a guardar datos

    resultado = []
    ultimo_trimestre = -1
    anio_encontrado = False
    try:
        anio = int(anio)
    except:
        return None

    # se anade este booleano en caso que no exista el anio en el data set

    for row in data:

        try:
            anio_row_actual = int(row['ANO4'])
            trimestre_actual = int(row['TRIMESTRE'])
        except:
            continue  # si contiene valores no normativos pasa al siguiente

        if anio_row_actual == anio:
            anio_encontrado = True
            if trimestre_actual > ultimo_trimestre:
                ultimo_trimestre = trimestre_actual
                resultado = [row]
            elif trimestre_actual == ultimo_trimestre:
                resultado.append(row)

    if not anio_encontrado:
        return None
    return resultado


def aglomerado_mayor_menor_vivienda_precario(anio, data):
    """
    Se ingresa un anio y se busca el ultimo trimestre en ese anio, del cual obtendremos 
    el aglomerado con mayor y menor porcentaje de viviendas con 'Material precario'

    Args:
        anio (int or str): Año del cual se desea obtener los datos.
        data (list[dict]): Lista de registros, cada uno representado como un diccionario
            que debe contener las claves 'AGLOMERADO' y 'MATERIAL_TECHUMBRE'.

    """

    dats_ultimo_trimestre = obtener_datos_ultimo_trimestre(anio, data)

    # si el data set no tiene datos de ese anio o directamente no hay anio
    if not dats_ultimo_trimestre:
        return None, None

    # estructura donde se guardaran los aglomerados y su porcentaje
    result = {}

    conteo_total = Counter()
    conteo_precario = Counter()
    for row in dats_ultimo_trimestre:
        try:
            aglomerado = int(row['AGLOMERADO'])
            material = str(row['MATERIAL_TECHUMBRE'])
        except:
            continue  # si no hay la columna o datos erroneos

        conteo_total[aglomerado] += 1

        if material == 'Material precario':
            conteo_precario[aglomerado] += 1

    # Calcular porcentajes
    porcentajes = {
        aglo: round((conteo_precario[aglo]/conteo_total[aglo])*100, 2) for aglo in conteo_total
    }

    if not porcentajes:
        return None, None  # si no hay datos validos

    # con .get max y min se basan en el valor de cada aglomerado
    aglo_max = max(porcentajes, key=porcentajes.get)
    aglo_min = min(porcentajes, key=porcentajes.get)

    return (aglo_max, porcentajes[aglo_max]), (aglo_min, porcentajes[aglo_min])


def mostrar_datos_porcentajes(aglo_porcentaje_max, aglo_porcentaje_min):

    """
    Muestra en consola el aglomerado con mayor y menor porcentaje de viviendas 
    de material precario.

    Parámetros:
    aglo_porcentaje_max :
        Tupla que contiene el nombre del aglomerado y su porcentaje máximo 
        de viviendas de material precario.

    aglo_porcentaje_min :
        Tupla que contiene el nombre del aglomerado y su porcentaje mínimo 
        de viviendas de material precario.
    """
    if not aglo_porcentaje_max or not aglo_porcentaje_min:
        print("No se encontraron datos de viviendas con material precario para ese año.")
    else:
        print('-'*50)
        print('El aglomerado con mayor porcentaje de viviendas de material precario es: ',
              aglo_porcentaje_max[0], 'con', aglo_porcentaje_max[1],'%')
        print('El aglomerado con menor porcentaje de vivientas de material precario es: ',
              aglo_porcentaje_min[0], 'con', aglo_porcentaje_min[1],'%')

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 12 (ANÁLISIS) - HOGAR
# -----------------------------------------------------------------------------------


def buscar_anios_disponibles(data):
    """
    Devuelve un conjunto de años disponibles en los datos.
    """
    anios = set()
    for fila in data:
        try:
            anio = int(fila["ANO4"])
            anios.add(anio)
        except (KeyError, ValueError):
            continue
    return anios


def porcentaje_jubilados_habitabilidad_insuficiente(data_hog, data_ind):

    # Busco el ultimo anio disponible para reutilizar
    # la funcion de obtener_datos_ultimo_trimestre
    """
    Calcula el porcentaje de jubilados que viven en un hogar con habitabilidad insuficiente
    por cada aglomerado del ultimo trimestre del año disponible

    Return:
        Dict: diccionario con aglomerados como claves y porcentajes de jubilados
        en hogares con habitabilidad insuficiente 
    """

    # Buscar años disponibles en ambos datasets
    anios_hog = buscar_anios_disponibles(data_hog)
    anios_ind = buscar_anios_disponibles(data_ind)

    anios_comunes = anios_hog & anios_ind

    if not anios_comunes:
        return "No compatibles"

    anio_max = max(anios_comunes)

    datos_proc_hog = obtener_datos_ultimo_trimestre(anio_max, data_hog)
    datos_proc_ind = obtener_datos_ultimo_trimestre(anio_max, data_ind)

    if not datos_proc_hog or not datos_proc_ind:
        return None

    # Verificar que ambos conjuntos de datos correspondan al mismo trimestre

    try:
        trimestre_hog = max(int(row['TRIMESTRE']) for row in datos_proc_hog)
        trimestre_ind = max(int(row['TRIMESTRE']) for row in datos_proc_ind)
    except (KeyError, ValueError):
        return None

    if trimestre_hog != trimestre_ind:
        return "No compatibles"  # Trimestres distintos, no se puede calcular correctamente

    # estructura donde guardaremos los hogares con habitabilidad insuficiente

    hogares_habitabilidad_insuficiente = set()
    # lo hacemos set para evitar datos repetidos

    # generamos un diccionario de par codosu, hogar y valor cantidad de miembros del hogar
    for row in datos_proc_hog:
        try:
            if row['CONDICION_DE_HABITABILIDAD'].strip().lower() == 'insuficiente':
                clave = (row['CODUSU'], row['NRO_HOGAR'])
                hogares_habitabilidad_insuficiente.add(clave)
        except (KeyError, ValueError):
            continue  # ante cualquier dato mal ingresado o vacio

    # ahora con el diccionario de hogares de habitabilidad insuficientes

    if not hogares_habitabilidad_insuficiente:
        return "NO_HOGARES_INSUFICIENTES"

    # estructura para calcular % de jubilados

    datos_jubilados = {}

    # recorremos individuos

    for fila in datos_proc_ind:

        # sabemos que jubilados en CAT_INAC corresponde a 1

        try:
            clave = (fila['CODUSU'], fila['NRO_HOGAR'])

            if int(fila['CAT_INAC']) == 1:

                # obtener el aglomerado actual
                aglomerado = fila['AGLOMERADO']

                if aglomerado not in datos_jubilados:
                    datos_jubilados[aglomerado] = {
                        'total': 0,
                        'habitabilidad_insuficiente': 0
                    }
                datos_jubilados[aglomerado]['total'] += int(fila['PONDERA'])

                # si el jubilado esta en un hogar de habitabilidad insuficiente
                if clave in hogares_habitabilidad_insuficiente:
                    datos_jubilados[aglomerado]['habitabilidad_insuficiente'] += int(
                        fila['PONDERA'])

        except (KeyError, ValueError):
            continue

    resultado = {}

    for aglomerado, valores in datos_jubilados.items():
        total = valores['total']
        insuficiente = valores['habitabilidad_insuficiente']
        if total > 0:
            porcentaje = (insuficiente / total) * 100
        else:
            porcentaje = 0.0
        resultado[aglomerado] = round(porcentaje, 2)

    return resultado


def imprimir_datos_jubilados(resultados):
    """
        Imprime de forma ordenada por aglomerados el porcentaje de jubilados
        en viviendas de habitabilidad insuficiente
    """

    if resultados == "NO_HOGARES_INSUFICIENTES":
        print("No existen jubilados en hogares con habitabilidad insuficiente.")
        return
    elif resultados == "No compatibles":
        print("No son compatibles los archivos hogares - individuos")
        return
    elif not resultados:
        print("Datos faltantes.")
        return

    print("-" * 45)
    print(f"{'Aglomerado':<15} | {'% Jubilados en Hab. Insuf.':>27}")
    print("-" * 45)

    for aglomerado, porcentaje in sorted(resultados.items(), key=lambda x: int(x[0])):
        print(f"{aglomerado:<15} | {porcentaje:>27.2f}%")
    print("-" * 45)


# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 13 (ANÁLISIS) - INDIVIDUOS Nota: se puede usar la funciones del PUNTO 9 y 12!
# -----------------------------------------------------------------------------------
def buscar_ultimo_trimestre_disponible(anio: int, filas_csv: list[dict], tipo_archivo: str) -> int:
    """
    Busca el último trimestre disponible en los datos CSV cargados para un año dado
    e imprime un mensaje indicando el tipo de archivo.

    Parámetros:
        anio (int): Año a consultar.
        filas_csv (list[dict]): Lista de filas del archivo CSV.
        tipo_archivo (str): 'individuos' o 'hogares' para imprimir el mensaje.

    Retorna:
        int: Trimestre más alto disponible, o None si no hay datos.
    """
    trimestres = set()

    for fila in filas_csv:
        try:
            if int(fila["ANO4"]) == anio:
                trimestres.add(int(fila["TRIMESTRE"]))
        except (KeyError, ValueError):
            continue

    if trimestres:
        print(
            f"Trimestres disponibles en el archivo de {tipo_archivo} para el {anio}: {trimestres}")
        return max(trimestres)
    else:
        print(
            f"No hay trimestres disponibles en el archivo de {tipo_archivo} para el {anio}.")
        return None


def contar_personas_educadas_en_viviendas_insuficientes(data_indiv: list[dict], data_hog: list[dict], anio: int, trimestre: int) -> int:
    """
    Se contabilizan las personas con nivel educativo universitario o superior
    que vivan en viviendas con condición de habitabilidad insuficiente, en un 
    año y trimestre específicos.

    Los datos se toman directamente de las listas de registros de
    individuos y hogares, sin armar estructuras intermedias.
    """

    # Armo un conjunto con las claves de los hogares cuya habitabilidad es insuficiente
    claves_hogares_insuficientes = set()

    for hogar in data_hog:
        try:
            # Verifico que el hogar corresponda al año y trimestre indicados
            if int(hogar["ANO4"]) == anio and int(hogar["TRIMESTRE"]) == trimestre:
                # Verifico si la condición de habitabilidad es "insuficiente"
                if hogar["CONDICION_DE_HABITABILIDAD"].strip().lower() == "insuficiente":
                    # Armo la clave que identifica al hogar
                    clave = (
                        hogar["CODUSU"],
                        hogar["NRO_HOGAR"],
                        hogar["ANO4"],
                        hogar["TRIMESTRE"],
                        hogar["AGLOMERADO"]
                    )
                    claves_hogares_insuficientes.add(clave)
        except (KeyError, ValueError):
            continue  # Ignoro filas con errores

    # Inicializo el total ponderado
    total_ponderado = 0

    for persona in data_indiv:
        try:
            # Verifico que la persona corresponda al año y trimestre indicados
            if int(persona["ANO4"]) == anio and int(persona["TRIMESTRE"]) == trimestre:
                # Verifico si tiene nivel educativo superior o universitario
                if persona["NIVEL_ED_str"].strip().lower() == "superior o universitario":
                    # Armo la clave del hogar donde vive la persona
                    clave = (
                        persona["CODUSU"],
                        persona["NRO_HOGAR"],
                        persona["ANO4"],
                        persona["TRIMESTRE"],
                        persona["AGLOMERADO"]
                    )
                    # Sumo la ponderación si vive en un hogar con habitabilidad insuficiente
                    if clave in claves_hogares_insuficientes:
                        total_ponderado += float(persona["PONDERA"])
        except (KeyError, ValueError):
            continue  # Ignoro filas con errores

    # Devuelvo el total ponderado redondeado
    return round(total_ponderado)


def informe_universitarios_en_viviendas_insuficientes(data_indiv: list[dict], data_hog: list[dict], anio: int) -> None:
    """
    Mostramos un informe de la cantidad de personas con estudios universitarios o superiores
    que viven en viviendas con condición de habitabilidad insuficiente, en el último trimestre
    disponible del año indicado.
    """

    # Busco el último trimestre disponible para cada archivo
    trimestre_indiv = buscar_ultimo_trimestre_disponible(
        anio, data_indiv, "individuos")
    trimestre_hog = buscar_ultimo_trimestre_disponible(
        anio, data_hog, "hogares")

    # Verifico que haya datos disponibles en ambos archivos
    if trimestre_indiv is None or trimestre_hog is None:
        print(
            f"No hay información suficiente para el año {anio} en ambos archivos.")
        return

    # Verifico que los archivos correspondan al mismo trimestre
    if trimestre_indiv != trimestre_hog:
        print(
            f"Error: los archivos no corresponden al mismo trimestre (individuos: {trimestre_indiv}, hogares: {trimestre_hog}).")
        return

    # Contamos personas directamente, sin armar diccionarios
    cantidad_ponderada = contar_personas_educadas_en_viviendas_insuficientes(
        data_indiv, data_hog, anio, trimestre_indiv
    )

    print(
        f"\nCantidad de personas con estudios superiores/universitarios en viviendas insuficientes: {cantidad_ponderada}")
