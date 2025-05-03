from src.utils.constants import PROJECT_ROOT, DATA_SOURCE_DIR, DATA_CLEAN_DIR, FILENAME_INDIVIDUOS_UNIFIED, FILENAME_HOGARES_UNIFIED
import streamlit as st
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


# PROCESAR ARCHIVOS
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
    all_headers = []  # Aca voy  a acumular los headers
    # En esta lista voy  a unificar las filas de los archivos(encabezados y filas)
    unified_data = []

    # PRIMER FOR: recolectar todos los encabezados
    for file in source_path.glob("*.txt"):
        if category in file.name:  # Condición si el archivo tiene la categoría elegida
            headers, _ = read_file_dic(file)  # solo me interesa el header
            for header in headers:  # Recorro los encabezados del archivo
                if header not in all_headers:  # Solo lo agrego si no está en la lista
                    all_headers.append(header)

     # SEGUNDO FOR: Unificar filas
    for file in source_path.glob("*.txt"):
        if category in file.name:
            _, rows = read_file_dic(file)  # Ahora solo me importan las filas

            for row in rows:  # Recorro las filas
                unified_row = {}
                for key in all_headers:  # Para cada fila voy recorriendo por header
                    # Si no existe en el header agregar None, sino guarda el dato en esa key
                    unified_row[key] = row.get(key, None)

                # Este debe ir fuera del loop de las columnas, agregando toda la fila a unified_data
                unified_data.append(unified_row)

    return all_headers, unified_data


# GUARDAR ARCHIVOS

# PROPUESTA -  Esta funcion puede unificar a save_to_txt y save_to_csv
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


def save_to_txt(headers, data, destination_path, file_name="hogares_unificados.txt"):
    """
    Guarda una lista de diccionarios en un archivo de texto con formato CSV delimitado por punto y coma (;).

    Parameters:
        headers (list): Lista de encabezados para las columnas.
        data (list): Lista de diccionarios que representa las filas a guardar en el archivo.
        destination_path (str | Path): Ruta del directorio donde se guardará el archivo.
        file_name (str): Nombre del archivo de salida.
    """

    file_path = Path(destination_path) / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open(mode='w', encoding='utf-8', newline='') as file_txt:
        writer = csv.DictWriter(file_txt, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Archivo TXT guardado en: {file_path}")


def save_to_csv(file_path, header, data, delimiter=";"):
    """
    Guarda los datos en un archivo CSV en el formato especificado.

    Parameters:
    - data: Lista de diccionarios con los datos a guardar.
    - file_path: Ruta del archivo donde se guardarán los datos.
    - header: Lista de nombres de las columnas (encabezado) para el CSV.
    - delimiter: Delimitador de los campos en el CSV (por defecto ";").
    """
    file_path = Path(file_path)
    # Crea el directorio si no existe
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open(mode="w", encoding="UTF-8", newline="") as file:
        csv_writer = csv.DictWriter(
            file, delimiter=delimiter, fieldnames=header)
        csv_writer.writeheader()  # Escribe el encabezado
        csv_writer.writerows(data)  # Escribe los datos


# STREAMLIT
"""
def max_min_date(data):
    
    Calcula el rango de fechas (año y trimestre) a partir de los datos proporcionados.

    Parameters:
        data (list): Lista de diccionarios que contiene los datos con las claves "ANO4" y "TRIMESTRE".

    Returns:
        tuple: Una tupla que contiene la fecha máxima y mínima en formato "TRIMESTRE/YYYY".
    
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
"""


def max_min_date(data):
    """
    Calcula la fecha mínima y máxima (año y trimestre) a partir de una lista de diccionarios.
    Cada diccionario debe contener las claves "ANO4" (año) y "TRIMESTRE" (número de trimestre).
    Args:
        data (list of dict): Lista de diccionarios con claves "ANO4" y "TRIMESTRE".
    Returns:
        tuple: Una tupla con la fecha máxima y mínima en formato "TRIMESTRE/YYYY".
    Raises:
        ValueError: Si la lista está vacía o los datos no contienen las claves requeridas.
    """
    if not data:
        raise ValueError("La lista de datos está vacía.")

    try:
        fechas = [(int(row["ANO4"]), int(row["TRIMESTRE"])) for row in data]
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Error al procesar las fechas: {e}")

    max_fecha = max(fechas)
    min_fecha = min(fechas)

    max_date = f"{max_fecha[1]}/{max_fecha[0]}"
    min_date = f"{min_fecha[1]}/{min_fecha[0]}"

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
    try:
        date_list = sorted(max_min_date(
            dataset_hog[1]) + max_min_date(dataset_ind[1]))
    except ValueError:
        st.error("❌ Error: No se encontraron datos en los archivos procesados.")
        return None, None

    # devuelve la fecha minima y maxima de los dos archivos
    return date_list[0], date_list[-1]


# ACTUALIZAR


def actualizar():
    """
    Procesa y guarda archivos de hogares e individuos. Pensado para ser usado en una app de Streamlit.

    Utiliza las rutas y nombres de archivo definidos en constantes globales. Muestra mensajes de éxito
    o error según el resultado del procesamiento.
    """
    try:
        # Procesar hogares
        encabezados_h, hogares = process_file(
            DATA_SOURCE_DIR, category="hogar")
        save_to_txt(encabezados_h, hogares, DATA_CLEAN_DIR,
                    FILENAME_HOGARES_UNIFIED)

        # Procesar individuos
        encabezados_i, individuos = process_file(
            DATA_SOURCE_DIR, category="individual")
        save_to_txt(encabezados_i, individuos, DATA_CLEAN_DIR,
                    FILENAME_INDIVIDUOS_UNIFIED)

        # Sirve para que se resetee el rango de fechas en la app
        st.session_state.date_range = None

        st.success(f"✔ Archivos actualizados correctamente.\n")

    except Exception as e:
        st.error(f"❌ Error al actualizar archivos: {e}")
