import csv
from pathlib import Path

# -------------------------------------------------------------------------------
# LEER  ARCHIVOS
# -------------------------------------------------------------------------------
def read_file(file_path):
    """
    Lee un archivo txt que tiene formato csv separado por punto y coma (;) y lo convierte en una lista de filas.

    Parameters:
        file_path (str): Ruta del archivo CSV a leer.

    Returns:
        list: Una lista de listas, donde cada sublista representa una fila del archivo CSV.
    """
    try:
        with open(file_path, encoding='utf-8') as file_csv:
            csv_reader = csv.reader(file_csv, delimiter=";")
            return list(csv_reader)
    except FileNotFoundError:
        print(f"❌ Error: El archivo {file_path} no existe.")
        return []

def read_file_dic(file_path):
    """
    Lee un archivo CSV y devuelve el encabezado y los datos como una lista de diccionarios.
    Args:
    param: file_path: Ruta del archivo CSV a leer.
    Returns:
    :return: Una lista con el encabezado y una lista de diccionarios con los datos.
    """
    try:
        with open(file_path, encoding='utf-8') as file_csv:
            csv_reader = csv.DictReader(file_csv, delimiter=";")
            return csv_reader.fieldnames, list(csv_reader)
    except FileNotFoundError:
        print(f"❌ Error: El archivo {file_path} no existe.")
        return [], []
# -------------------------------------------------------------------------------
# PROCESAR ARCHIVOS
# -------------------------------------------------------------------------------

def process_file(source_path, category="hogar"):
    """
    Procesa archivos de texto en un path, filtrando por categoría, y unifica sus datos en una estructura común.

    Args:
        source_path (Path): Ruta al directorio que contiene los archivos `.txt` a procesar.
        category (str, optional): Categoría a buscar dentro del nombre de los archivos. Por defecto es "hogar".

    Returns:
        tuple:
            - all_headers (list): Lista con todos los encabezados únicos encontrados en los archivos.
            - unified_data (list of dict): Lista de diccionarios, cada uno representando una fila de datos unificada.
    """
    headers_set = set()
    raw_rows = []

    # Procesar archivos en una sola pasada
    for file in source_path.glob("*.txt"):
        if category in file.name:
            headers, rows = read_file_dic(file)
            headers_set.update(headers)
            raw_rows.extend(rows)

    all_headers = list(headers_set)

    # Unificar filas
    unified_data = [{key: row.get(key, None) for key in all_headers} for row in raw_rows]

    return all_headers, unified_data
# -------------------------------------------------------------------------------
# GUARDAR ARCHIVOS
# -------------------------------------------------------------------------------

def save_to_file(file_path, file_name, header, data, separator=";"):
    """
    Guarda los datos en un archivo CSV en el formato especificado.

    Parameters:
    - data: Lista de diccionarios con los datos a guardar.
    - file_path: Ruta del archivo donde se guardarán los datos.
    - file_name: Nombre del archivo a guardar.
    - header: Lista de nombres de las columnas (encabezado) para el CSV.
    - delimiter: Delimitador de los campos en el CSV (por defecto ";").
    """
    if not data:
        print("❌ Error: No hay datos para guardar.")
        return

    # Crea la ruta completa del archivo
    file_path = Path(file_path) / file_name

    # Crea el directorio si no existe
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open(mode="w", encoding="UTF-8", newline="") as file:
        csv_writer = csv.DictWriter(
            file, delimiter=separator, fieldnames=header)

        # Escribe el encabezado y los datos en el archivo CSV
        csv_writer.writeheader()
        csv_writer.writerows(data)

    print(f"✅ Archivo guardado en: {file_path}")

# -------------------------------------------------------------------------------
# CALCULOS MAXIMOS Y MINIMOS FECHA
# -------------------------------------------------------------------------------

def extraer_fecha(row):
    """
    Intenta extraer y devolver una tupla (año, trimestre) desde un diccionario.
    Devuelve None si los datos son inválidos o faltan.
    """
    try:
        año = int(row["ANO4"])
        trimestre = int(row["TRIMESTRE"])
        return (año, trimestre)
    except (KeyError, ValueError, TypeError):
        return None

def actualizarmaxmin_fechas(fecha_actual, min_fecha, max_fecha):
    """
    Actualiza las fechas mínima y máxima comparando con una nueva fecha actual.

    Args:
        fecha_actual (tuple): Tupla (año, trimestre) actual.
        min_fecha (tuple or None): Fecha mínima actual.
        max_fecha (tuple or None): Fecha máxima actual.

    Returns:
        tuple: (min_fecha_actualizada, max_fecha_actualizada)
    """
    if min_fecha is None or fecha_actual < min_fecha:
        min_fecha = fecha_actual
    if max_fecha is None or fecha_actual > max_fecha:
        max_fecha = fecha_actual
    return min_fecha, max_fecha


