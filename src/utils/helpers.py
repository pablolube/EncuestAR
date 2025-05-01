import sys
import os
import csv
from pathlib import Path
from src.utils.constants import HOGARES_PROCESSED_DIR, INDIVIDUOS_PROCESSED_DIR

# Agregamos el path si se necesitan módulos de ../data
sys.path.append(os.path.abspath("../data"))

# LEER  ARCHIVOS


def read_file(file_path):
    """
    Lee un archivo txt que tiene formato csv separado por punto y coma (;) y lo convierte en una lista de filas.

    Parameters:
        file_path (str): Ruta del archivo CSV a leer.

    Returns:
        list: Una lista de listas, donde cada sublista representa una fila del archivo CSV.
    """
    with open(file_path, encoding='utf-8') as file_csv:
        csv_reader = csv.reader(file_csv, delimiter=";")
        return list(csv_reader)


def read_file_dic(file_path):
    """
    Lee un archivo CSV y devuelve el encabezado y los datos como una lista de diccionarios.
    Args:
    param: file_path: Ruta del archivo CSV a leer.
    Returns:
    :return: Una lista con el encabezado y una lista de diccionarios con los datos.
    """
    with open(file_path, encoding='utf-8') as file_csv:
        csv_reader = csv.DictReader(file_csv, delimiter=";")
        return csv_reader.fieldnames, list(csv_reader)


# PROCESAR ARCHIVOS


def process_file(source_path, category="hogar"):
    all_headers = set()
    unified_data = []

    # PRIMER FOR: recolectar todos los encabezados
    for file in source_path.glob("*.txt"):
        if category in file.name:
            headers, _ = read_file_dic(file)  # solo me interesa el header
            all_headers.update(headers)

    all_headers = list(all_headers)  # convertir a lista para orden y uso posterior

    # SEGUNDO FOR: normalizar y guardar filas
    for file in source_path.glob("*.txt"):
        if category in file.name:
            _, rows = read_file_dic(file)

            for row in rows:
                normalized_row = {}
                for key in all_headers:
                    normalized_row[key] = row.get(key, None)
                unified_data.append(normalized_row)

    return all_headers, unified_data



# GUARDAR ARCHIVOS

def save_to_txt(data, destination_path, file_name="hogares_unificados.txt"):
    """
    Guarda una lista de datos en un archivo de texto con formato CSV delimitado por punto y coma (;).

    Parameters:
        data (list): Lista de listas que representa las filas a guardar en el archivo.
        destination_path (str): Ruta del directorio donde se guardará el archivo.
        file_name (str): Nombre del archivo de salida. Valor por defecto: "hogares_unificados.txt".

    Notas :
        - Crea el directorio de destino si no existe.
        - Escribe un archivo de texto en la ubicación especificada.
        - Imprime una confirmación con la ruta del archivo guardado.
    """

    destination_file = os.path.join(destination_path, file_name)
    os.makedirs(destination_path, exist_ok=True)

    with open(destination_file, mode='w', encoding='utf-8', newline='') as file_txt:
        writer = csv.writer(file_txt, delimiter=";")
        writer.writerows(data)

    print(f"✅ Archivo TXT guardado en: {destination_file}")


def save_to_csv(file_path, header, data, delimiter=";"):
    """
    Guarda los datos en un archivo CSV en el formato especificado.

    Parameters:
    - data: Lista de diccionarios con los datos a guardar.
    - file_path: Ruta del archivo donde se guardarán los datos.
    - header: Lista de nombres de las columnas (encabezado) para el CSV.
    - delimiter: Delimitador de los campos en el CSV (por defecto ";").
    """
    file_path = Path(file_path)  # Aseguramos que la ruta sea un objeto Path
    # Crea el directorio si no existe
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open(mode="w", encoding="UTF-8", newline="") as file:
        csv_writer = csv.DictWriter(
            file, delimiter=delimiter, fieldnames=header)
        csv_writer.writeheader()  # Escribe el encabezado
        csv_writer.writerows(data)  # Escribe los datos


def max_min_date(data):
    """
    Calcula el rango de fechas (año y trimestre) a partir de los datos proporcionados.

    Parameters:
        data (list): Lista de diccionarios que contiene los datos con las claves "ANO4" y "TRIMESTRE".

    Returns:
        tuple: Una tupla que contiene la fecha máxima y mínima en formato "TRIMESTRE/YYYY".
    """
    max_year = min_year = None
    max_trim = min_trim = None

    for row in data:
        year = int(row["ANO4"])
        trim = int(row["TRIMESTRE"])

        if max_year is None or year > max_year:
            max_year = year
            max_trim = trim
        elif year == max_year:
            if trim > max_trim:
                max_trim = trim

        if min_year is None or year < min_year:
            min_year = year
            min_trim = trim
        elif year == min_year:
            if trim < min_trim:
                min_trim = trim

    max_date = f"{max_trim}/{max_year}"
    min_date = f"{min_trim}/{min_year}"

    return max_date, min_date


def data_date_range():
    """
    Devuelve el rango de fechas (mínima y máxima) de los archivos de hogares e individuos procesados.
    """
    # Lee los archivos procesados de hogares e individuos
    dataset_hog = read_file_dic(HOGARES_PROCESSED_DIR)
    dataset_ind = read_file_dic(INDIVIDUOS_PROCESSED_DIR)

    # Obtiene las fechas mínimas y máximas de ambos conjuntos de datos
    # y las ordena
    date_list = sorted(max_min_date(
        dataset_hog[1]) + max_min_date(dataset_ind[1]))

    # devuelve la fecha minima y maxima de los dos archivos
    return date_list[0], date_list[-1]

# STREAMLIT 

# ACTUALIZAR
from src.utils.constants import PROJECT_ROOT, DATA_SOURCE_DIR,DATA_CLEAN_DIR,FILENAME_INDIVIDUOS_UNIFIED,FILENAME_HOGARES_UNIFIED
from src.procesamientos.hogares import procesar_hogares

def actualizar():
#Reunifica Individuos y Hogares
    hogares = process_file(DATA_SOURCE_DIR, category="hogar")
    save_to_txt(hogares, DATA_CLEAN_DIR , FILENAME_HOGARES_UNIFIED)
    individual=process_file(DATA_SOURCE_DIR, "individual")
    save_to_txt(individual, DATA_CLEAN_DIR, FILENAME_INDIVIDUOS_UNIFIED)
#Reprocesa Individuos y Hogares
    procesar_hogares()

