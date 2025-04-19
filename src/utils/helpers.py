import sys
import os
import csv


# Agregamos el path si se necesitan módulos de ../data
sys.path.append(os.path.abspath("../data"))


def read_file(file_path):
    with open(file_path, encoding='utf-8') as file_csv:
        reader = csv.reader(file_csv, delimiter=";")
        return list(reader)


def process_file(source_path, category="hogar"):
    unified_data = []
    header = None

    for file_name in os.listdir(source_path):
        if category in file_name and file_name.endswith(".txt"):
            file_path = os.path.join(source_path, file_name)
            row = read_file(file_path)

            if not row:
                continue

            if header is None:
                header = row[0]
                unified_data.extend(row[1:])
            else:
                if row[0] == header:
                    unified_data.extend(row[1:])
                else:
                    print(f"⚠️ Cabecera diferente en: {file_name}")

    return [header] + unified_data if header else []


def save_to_txt(data, destination_path, file_name="hogares_unificados.txt"):
    destination_file = os.path.join(destination_path, file_name)
    os.makedirs(destination_path, exist_ok=True)

    with open(destination_file, mode='w', encoding='utf-8', newline='') as file_txt:
        writer = csv.writer(file_txt, delimiter=";")
        writer.writerows(data)

    print(f"✅ Archivo TXT guardado en: {destination_file}")

# Procesar archivos


def add_columns_header(header, *args):
    """
    Agrega columnas a una lista.

    Args:
    :param header: Lista a la que se le agregarán las columnas.
    :param *args: Columnas a agregar.
    """

    header.extend(args)
