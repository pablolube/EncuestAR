
# -------------------------------------------------------------------------------------------------------------------------
# PROCESADO DE INDIVIDUOS
# -------------------------------------------------------------------------------------------------------------------------

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


def add_extra_data(header, data):

    # Agrego las nuevas columnas al header
    header.extend(["CH04_str", "NIVEL_ED_str",
                  "CONDICION_LABORAL", "UNIVERSITARIO"])

    # Proceso las nuevas columnas por cada fila
    for row in data:
        add_data_ch04str(row)
        add_data_nivel_ed_str(row)
        add_data_cond_lab(row)
        add_data_universitario(row)
