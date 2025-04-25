import sys
import os
import csv


# Agregamos el path si se necesitan módulos de ../data
sys.path.append(os.path.abspath("../data")) # --------------------->  esto es necesario?

#LEER  ARCHIVOS 

def read_file(file_path):
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
    unified_data = []
    header = None

    for file in source_path.glob("*.txt"):
        print(file)
        if category in file:
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
    destination_file = os.path.join(destination_path, file_name)
    os.makedirs(destination_path, exist_ok=True)

    with open(destination_file, mode='w', encoding='utf-8', newline='') as file_txt:
        writer = csv.writer(file_txt, delimiter=";")
        writer.writerows(data)

    print(f"✅ Archivo TXT guardado en: {destination_file}")


# LIMPIAR ARCHIVOS

def add_columns_header(header, *args):
    """
    Agrega columnas a una lista.

    Args:
    :param header: Lista a la que se le agregarán las columnas.
    :param *args: Columnas a agregar.
    """

    header.extend(args)
