import sys
import os
import csv
from pathlib import Path

# Agregamos el path si se necesitan módulos de ../data
sys.path.append(os.path.abspath("../data")) # --------------------->  esto es necesario?

#LEER  ARCHIVOS 

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
    """
    Procesa archivos de texto en una ruta dada, unificando datos de archivos que contienen una categoría específica en su nombre.

    Parameters:
        source_path (Path): Ruta al directorio que contiene los archivos.
        category (str): Categoría a filtrar en los nombres de archivo. Solo se procesan archivos que incluyan esta cadena. Valor por defecto: "hogar".

    Returns:
        list: Una lista de listas, donde la primera sublista es la cabecera y las siguientes contienen los datos unificados
              de los archivos coincidentes. Si no se encuentra ninguna cabecera, se devuelve una lista vacía.

    Notas:
        - Solo se procesan archivos con extensión `.txt`  y aquellos que coincide la categoria en el numero de archivo.
        - Se imprime un aviso si la cabecera de un archivo difiere de la primera encontrada.
    """

    unified_data = []
    header = None

    for file in source_path.glob("*.txt"):
        print(file)
        if category in file.name:
            row = read_file(file)

            if not row:
                continue

            
            if header is None:
                header = row[0]
                unified_data.extend(row[1:])
            else:
                if row[0] == header:
                    unified_data.extend(row[1:])
                else:
                    print(f"⚠️ Cabecera diferente en: {file}")

    return [header] + unified_data if header else []


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

def save_to_csv(file_path,header,data, delimiter=";"):
    """
    Guarda los datos en un archivo CSV en el formato especificado.

    Parameters:
    - data: Lista de diccionarios con los datos a guardar.
    - file_path: Ruta del archivo donde se guardarán los datos.
    - header: Lista de nombres de las columnas (encabezado) para el CSV.
    - delimiter: Delimitador de los campos en el CSV (por defecto ";").
    """
    file_path = Path(file_path)  # Aseguramos que la ruta sea un objeto Path
    file_path.parent.mkdir(parents=True, exist_ok=True)  # Crea el directorio si no existe

    with file_path.open(mode="w", encoding="UTF-8", newline="") as file:
        csv_writer = csv.DictWriter(file, delimiter=delimiter, fieldnames=header)
        csv_writer.writeheader()  # Escribe el encabezado
        csv_writer.writerows(data)  # Escribe los datos

