
# -------------------------------------------------------------------------------------------------------------------------
# PROCESADO DE INDIVIDUOS DETALLE
# -------------------------------------------------------------------------------------------------------------------------

from src.utils.helpers import extraer_fecha, actualizarmaxmin_fechas

def get_gender(gender_num):
    """
    Devuelve la clasificación Masculino/Femenino

    Args:
    :param gender_num: Valor del genero correspondiente a la col CH04.

    Returns:
        string: gender_str: Masculino o Femenino
    """

    gender_map = {'1': 'Masculino', '2': 'Femenino'}
    return gender_map.get(gender_num, 'S/D')

def get_ed_level(ed_level):
    """
    Devuelve la clasificación de nivel educativo.

    Args:
    :param ed_level: Valor correspondiente a la col NIVEL_ED.
    """
    match ed_level:
        case '1':
            return 'Primario incompleto'
        case '2':
            return 'Primario completo'
        case '3':
            return 'Secundario incompleto'
        case '4':
            return 'Secundario completo'
        case '5' | '6':
            return 'Superior o universitario'
        case '7' | '9':
            return 'Sin Información'
        case _:
            return 'S/D'

def get_work_cond(state,category):
    """
    Devuelve la clasificación de condición laboral 

    Args:
    :param state: Condición de actividad
    :param category: Categoría ocupacional
    """

    if state == '1' and category in ('1', '2'):
        return "Ocupado autónomo"
    elif state == '1' and category in ('3', '4', '9'):
        return "Ocupado dependiente"
    elif state == '2':
        return "Desocupado"
    elif state == '3':
        return "Inactivo"
    else:
        return "Fuera de categoría/sin información"

def get_university_level(age,ed_level,ed_level_completed):
    """
    Devuelve la clasificación de nivel universitario.

    Args:
    :param 
        age: edad
        ed_level: nivel más alto que cursa o cursó
        ed_level_completed: finalizo ese nivel
    """

    if int(age) < 18:
        return 2

    return 1 if ed_level == '8' or (ed_level == '7' and ed_level_completed == '1') else 0

# -------------------------------------------------------------------------------
# PROCESAMIENTO DE INDIVIDUOS
# -------------------------------------------------------------------------------


def add_extra_data(header, data):
    """
    Agrega columnas adicionales al header y procesa los datos para cada fila.
    Args:
    :param header: Lista de encabezados del archivo CSV.
    :param data: Lista de filas del archivo CSV.
    """
    min_fecha = None
    max_fecha = None

    # Agrego las nuevas columnas al header
    header.extend(['CH04_str', 'NIVEL_ED_str','CONDICION_LABORAL', 'UNIVERSITARIO'])

    for row in data:
        row['CH04_str']=get_gender(row['CH04'])
        row['NIVEL_ED_str']=get_ed_level(row['NIVEL_ED'])
        row['CONDICION_LABORAL']=get_work_cond(row['ESTADO'],row['CAT_OCUP'])
        row['UNIVERSITARIO']=get_university_level(row['CH06'],row['CH12'],row['CH13'])
        
        fecha_actual = extraer_fecha(row)
        if fecha_actual:
            min_fecha, max_fecha = actualizarmaxmin_fechas(fecha_actual, min_fecha, max_fecha)

    return min_fecha, max_fecha
