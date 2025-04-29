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
