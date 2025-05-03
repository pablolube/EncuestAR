from src.utils.constants import AGLOMERADOS_NOMBRES, REGIONES_NOMBRES, NIVELES_EDUCATIVOS


# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 1 (ANÁLISIS) - INDIVIDUOS
# -----------------------------------------------------------------------------------


def imprimir_alfabetizadas(diccionario):
    """
    Realiza calculos porcentuales 

    Imprime el % de personas alfabetizadas por año.

    Args:
    :param diccionario: Diccionario con los datos de alfabetización.
    """
    print(f"{'Año':<10}{'% Alfabetos':>15}{'% No Alfabetos':>20}")
    print("-" * 45)

    # Calculo resultados porcentuales por año
    for anio in sorted(diccionario.keys(), reverse=True):

        # Recorro los trimestres de mayor a menor
        for trimestre in sorted(diccionario[anio].keys(), reverse=True):
            # Si hay personas alfabetizadas o no alfabetizadas, calculo los porcentajes
            if diccionario[anio][trimestre]["A"] > 0 or diccionario[anio][trimestre]["NA"] > 0:
                valor_alf = diccionario[anio][trimestre]["A"]
                valor_nalf = diccionario[anio][trimestre]["NA"]

                # Calculo el total de personas
                total = valor_alf + valor_nalf

                # Calculo los porcentajes
                porcentaje_alf = round((valor_alf / total) * 100, 2)
                porcentaje_Nalf = round((valor_nalf / total) * 100, 2)

                # Imprimo resultados
                print(f"{anio:<10}{porcentaje_alf:>15.2f}{porcentaje_Nalf:>20.2f}")

                # Paso al siguiente año
                break


def cant_personas_alfabetizadas(data):
    """
    Cuenta la cantidad de personas alfabetizadas en el archivo CSV por el último trimestre de cada año.
    Se clasifican a las personas que tengan 6 años o más.

    Args:
    :param data: lista de datos del dataset.
    """

    count = {}

    for row in data:
        # Si el año no existe, lo crea
        if row["ANO4"] not in count:
            count[row["ANO4"]] = {"1": {"A": 0, "NA": 0}, "2": {
                "A": 0, "NA": 0}, "3": {"A": 0, "NA": 0}, "4": {"A": 0, "NA": 0}}

        # Analiza si la edad (CH06) mayor a 6 años y que la persona no sea menor de 2 años (CH09=3)
        if row["CH06"] > "6" and row["CH09"] != "3":
            # Si la persona es alfabetizada (CH09 == 1), suma al contador de alfabetizados
            if row["CH09"] == "1":
                count[row["ANO4"]][row["TRIMESTRE"]
                                   ]["A"] += int(row["PONDERA"])
            # Si la persona no es alfabetizada (CH09 == 2), suma al contador de no alfabetizados
            elif row["CH09"] == "2":
                count[row["ANO4"]][row["TRIMESTRE"]
                                   ]["NA"] += int(row["PONDERA"])

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
        print(
            f"El % de personas extranjeras que han cursado el nivel superior o universitario en el trimestre {trim} del año {anio} es del: {porcentaje:.2f}%")

    except ZeroDivisionError:
        print(f"No hay datos para el trimestre {trim} del año {anio}")


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

    # Se guarda si hubo otros años y trimestres con el mismo valor que el minimo.
    resultados = []
    for anio, trimestres in total_trim.items():
        for trimestre, valor in trimestres.items():
            if valor == min_valor:
                resultados.append((anio, trimestre))

    # Se imprime resultado
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
# FUNCIONES PUNTO 5 (ANÁLISIS) - HOGAR
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 6 (ANÁLISIS) - HOGAR
# -----------------------------------------------------------------------------------

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
        clave_aglo = next((cod for cod, nombre in AGLOMERADOS_NOMBRES.items() if nombre.lower() == aglomerado_normalizado), None)
        if clave_aglo is None:
            raise ValueError(f"No se encontró un aglomerado con el nombre '{aglomerado}'.")

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
                conteo[aglo][(anio, trimestre)] = {nivel: 0 for nivel in range(1, 8)}

            conteo[aglo][(anio, trimestre)][nivel_ed] += pondera

    if not aglomerado_encontrado:
        print(f"No se encontraron registros para el aglomerado '{aglomerado}'.")
    else:
        imprimo_tabla_nivel_educativo(conteo)

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 10 (ANÁLISIS) - INDIVIDUOS Nota: podes usar la funcion PUNTO 9!
# -----------------------------------------------------------------------------------

def crear_estructura_datos():
    return {
        "Cumplen_aglom_1": 0,
        "Todos_aglom1_18": 0,
        "Cumplen_aglom_2": 0,
        "Todos_aglom2_18": 0
    }

def personas_secundario_incompleto_anio_trimestre(aglomerado1, aglomerado2,  data):

    dats = {}
    """

    """
    
    for row in data: 
        # guardo el aglomerado y nivel educativo de la persona actual
        try:
            aglo = int(row['AGLOMERADO'])
            nivel_ed = str(row['NIVEL_ED_str'])
            
            # creamos una clave anio trimestre que los vaya guardando en su respectivo bloque
            clave = (row['ANO4'], row['TRIMESTRE'])
            
            # cargamos el pondera de cada individuo
            Pondera = int(row['PONDERA'])
            
        except (ValueError, KeyError):
            continue # ignora filas con valores erroneos o incompletos
        
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
    
def imprimir_porcentaje_secundario_incompleto(datos):
    
    # Encabezado
        
    print(f"{'Año':^8} {'Trimestre':^8} {'Aglomerado A':^20} {'Aglomerado B':^20}")
    print("-" * 60)
    
    # sorted lo usa para ir imprimendo ordenando por el par anio, trimestre
    for (anio, trimestre), valores in sorted(datos.items()):
        
        # guardamos los valores de cada anio trimestre
        cumplen1 = valores["Cumplen_aglom_1"]
        total1 = valores["Todos_aglom1_18"]
        cumplen2 = valores["Cumplen_aglom_2"]
        total2 = valores["Todos_aglom2_18"]
        
        # Calculamos porcentaje
        
        porcentaje1 = (cumplen1 / total1) * 100 if total1 > 0 else 0
        porcentaje2 = (cumplen2 / total2) * 100 if total2 > 0 else 0
        
        # Mejoramos el formato para la impresion
        
        porcentaje1 = f"{porcentaje1:.2f} %"
        porcentaje2 = f"{porcentaje2:.2f} %"
        
        # Imprimimos fila
        
        print(f"{anio:^8} {trimestre:^8} {porcentaje1:^20} {porcentaje2:^20}")
        

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 11 (ANÁLISIS) - HOGAR
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# FUNCIONES PUNTO 12 (ANÁLISIS) - HOGAR
# -----------------------------------------------------------------------------------

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
        print(f"Trimestres disponibles en el archivo de {tipo_archivo} para el {anio}: {trimestres}")
        return max(trimestres)
    else:
        print(f"No hay trimestres disponibles en el archivo de {tipo_archivo} para el {anio}.")
        return None

def armar_diccionario(datos: list[dict], tipo: str, anio: int, trimestre: int) -> dict:
    """
    Construye un diccionario de individuos o hogares filtrado por año y trimestre.

    Retorna:
        dict: Diccionario indexado por clave compuesta.
    """
    resultado = {}

    for fila in datos:
        try:
            if int(fila["ANO4"]) != anio or int(fila["TRIMESTRE"]) != trimestre:
                continue

            if tipo == "individuos":
                clave = (
                    fila["CODUSU"],
                    fila["NRO_HOGAR"],
                    fila["COMPONENTE"],
                    fila["ANO4"],
                    fila["TRIMESTRE"],
                    fila["AGLOMERADO"]
                )
                valor = {
                    "NIVEL_ED_str": fila["NIVEL_ED_str"].strip(),
                    "PONDERA": float(fila["PONDERA"])
                }

            elif tipo == "hogares":
                clave = (
                    fila["CODUSU"],
                    fila["NRO_HOGAR"],
                    fila["ANO4"],
                    fila["TRIMESTRE"],
                    fila["AGLOMERADO"]
                )
                valor = {
                    "CONDICION_DE_HABITABILIDAD": fila["CONDICION_DE_HABITABILIDAD"].strip(),
                    "PONDERA": float(fila["PONDERA"])
                }

            else:
                continue

            resultado[clave] = valor

        except (KeyError, ValueError):
            continue

    return resultado
def contar_personas_en_viviendas_insuficientes(dic_indiv: dict, dic_hogares: dict) -> int:
    """
    Cuenta personas con educación superior/universitaria en viviendas insuficientes.

    Retorna:
        int: Cantidad ponderada de personas.
    """
    total_ponderado = 0

    for clave_indiv, datos_indiv in dic_indiv.items():
        clave_hogar = clave_indiv[:2] + clave_indiv[3:]  # Eliminar COMPONENTE

        hogar = dic_hogares.get(clave_hogar)
        if hogar:
            condicion = hogar["CONDICION_DE_HABITABILIDAD"].strip().lower()
            nivel_ed = datos_indiv["NIVEL_ED_str"].strip().lower()

            if condicion == "insuficiente" and nivel_ed == "superior o universitario":
                total_ponderado += datos_indiv["PONDERA"]

    return round(total_ponderado)


def informe_personas_en_viviendas_insuficientes(data_indiv: list[dict], data_hog: list[dict], anio: int) -> None:
    """
    Muestra un informe de personas con estudios superiores viviendo en viviendas insuficientes.
    """
    # Buscar trimestres disponibles
    trimestre_indiv = buscar_ultimo_trimestre_disponible(anio, data_indiv, "individuos")
    trimestre_hog = buscar_ultimo_trimestre_disponible(anio, data_hog, "hogares")

    if trimestre_indiv is None or trimestre_hog is None:
        print(f"No hay información suficiente para el año {anio} en ambos archivos.")
        return

    # Construir diccionarios filtrados
    personas = armar_diccionario(data_indiv, "individuos", anio, trimestre_indiv)
    hogares = armar_diccionario(data_hog, "hogares", anio, trimestre_hog)

    # Calcular resultado
    cantidad_ponderada = contar_personas_en_viviendas_insuficientes(personas, hogares)

    # Mostrar resultado
    print(f"\nCantidad de personas con estudios superiores/universitarios en viviendas insuficientes: {cantidad_ponderada}")
