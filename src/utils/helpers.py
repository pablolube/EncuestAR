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

    Esta función busca archivos `.txt` dentro del `source_path` cuyo nombre contenga la categoría especificada.
    Primero recolecta todos los encabezados únicos presentes en los archivos filtrados. Luego, construye una lista
    unificada de diccionarios fila por fila, asegurando que todas las filas tengan las mismas claves (encabezados),
    completando con `None` si falta algún dato.

    Args:
        source_path (Path): Ruta al directorio que contiene los archivos `.txt` a procesar.
        category (str, optional): Categoría a buscar dentro del nombre de los archivos. Por defecto es "hogar".

    Returns:
        tuple:
            - all_headers (list): Lista con todos los encabezados únicos encontrados en los archivos.
            - unified_data (list of dict): Lista de diccionarios, cada uno representando una fila de datos unificada
              según los encabezados recolectados.
    """

    all_headers = []
    unified_data = []

    try:
        archivos = list(source_path.glob("*.txt"))
        if not archivos:
            raise FileNotFoundError("No hay archivos .txt en el directorio.")

        # Filtrar por categoría
        archivos_filtrados = [f for f in archivos if category in f.name]
        if not archivos_filtrados:
            raise FileNotFoundError(f"No se encontraron archivos con la categoría '{category}'.")

        # PRIMER FOR: recolectar encabezados
        for file in archivos_filtrados:
            headers, _ = read_file_dic(file)
            for header in headers:
                if header not in all_headers:
                    all_headers.append(header)

        # SEGUNDO FOR: unificar filas
        for file in archivos_filtrados:
            _, rows = read_file_dic(file)
            for row in rows:
                unified_row = {key: row.get(key, None) for key in all_headers}
                unified_data.append(unified_row)

        if not all_headers or not unified_data:
            raise ValueError("No se pudieron extraer encabezados o datos de los archivos.")

        return all_headers, unified_data

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return None,None
    except Exception as e:
        print(f"⚠️ Error inesperado al procesar archivos: {e}")
        return None,None

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


