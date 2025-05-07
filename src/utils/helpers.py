from src.utils.constants import DATA_SOURCE_DIR,  DATA_PROCESSED_DIR, FILENAME_HOGARES_PROCESSED, FILENAME_INDIVIDUOS_PROCESSED, HOGARES_PROCESSED_DIR, INDIVIDUOS_PROCESSED_DIR
import streamlit as st
import csv
from pathlib import Path
from src.procesamientos.individuos import add_extra_data
from src.procesamientos.hogares import procesar_hogares

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
# STREAMLIT
# -------------------------------------------------------------------------------

# ACTUALIZAR


def actualizar():
    """
    Procesa y guarda archivos de hogares e individuos. Pensado para ser usado en una app de Streamlit.

    Utiliza las rutas y nombres de archivo definidos en constantes globales. Muestra mensajes de éxito
    o error según el resultado del procesamiento.

    """
    if "mensajes_actualizacion" in st.session_state:
        del st.session_state["mensajes_actualizacion"]

    try:
        # Verificar si hay archivos para procesar
        archivos_existentes = list(Path(DATA_SOURCE_DIR).glob("*.txt"))
        if not archivos_existentes:
            # Si no hay archivos, guardo el mensaje de advertencia
            st.session_state["mensaje_actualizacion"] = (
                "warning", "⚠️ No hay archivos en la carpeta para actualizar. Verifique si agregó los archivos.")
            return
        # -------------------------------------------------------------------------------
        # PROCESAMIENTO DE HOGARES
        # -------------------------------------------------------------------------------

        # Unificar archivos de hogares desde la fuente
        encabezados_h, hogares = process_file(DATA_SOURCE_DIR, category="hogar")

        # Agregar columnas derivadas y calcular fechas mínima y máxima para hogares
        min_fecha_hog, max_fecha_hog = procesar_hogares(encabezados_h, hogares)

        # Guardar los hogares procesados en un archivo intermedio
        save_to_file(DATA_PROCESSED_DIR, FILENAME_HOGARES_PROCESSED, encabezados_h, hogares)

        # -------------------------------------------------------------------------------
        # PROCESAMIENTO DE INDIVIDUOS
        # -------------------------------------------------------------------------------

        # Unificar archivos de individuos desde la fuente
        encabezados_i, individuos = process_file(DATA_SOURCE_DIR, category="individual")

        # Agregar columnas derivadas y calcular fechas mínima y máxima para individuos
        min_fecha_indiv, max_fecha_indiv= add_extra_data(encabezados_i, individuos)

        # Guardar los individuos procesados en un archivo intermedio
        save_to_file(DATA_PROCESSED_DIR, FILENAME_INDIVIDUOS_PROCESSED, encabezados_i, individuos)

        # Calcular la fecha mínima y máxima global entre hogares e individuos
    
        fechas_validas = [f for f in [min_fecha_hog, min_fecha_indiv,max_fecha_hog, max_fecha_indiv] if f is not None]
        fecha_min_global = min(fechas_validas) if fechas_validas else None
        fecha_max_global = max(fechas_validas) if fechas_validas else None

        # Resetear el rango de fechas en el estado de la aplicación (Streamlit)
        st.session_state.date_range = fecha_min_global, fecha_max_global

        
        # Mensaje de éxito
        st.session_state["mensaje_actualizacion"] = ("success", "✅ Archivos actualizados correctamente.")

    except Exception as e:
        # Si ocurre un error, guardo el mensaje de error
        st.session_state["mensaje_actualizacion"] = ("error", f"❌ Error al actualizar archivos: {e}")


def cargar_archivos(archivos):
    """
    Carga archivos en el directorio de datos especificado. Si el archivo ya existe, muestra un mensaje de advertencia.
    Args:
        archivos (list): Lista de archivos subidos por el usuario.
    """
    if "mensajes_carga" in st.session_state:
        del st.session_state["mensajes_carga"]

    mensajes = []

    if archivos:
        for uploaded_file in archivos:
            file_name = uploaded_file.name
            file_path = Path(DATA_SOURCE_DIR) / file_name

            if file_path.exists():
                # Si el archivo ya existe, guardo el mensaje de advertencia
                mensajes.append(
                    ("warning", f"⚠️ El archivo '{file_name}' ya existe. No se guardó."))
                continue

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Guardo el mensaje de éxito
            mensajes.append(
                ("success", f"✅ {file_name} guardado en {file_path}"))
    else:
        # Si no se seleccionaron archivos, guardo el mensaje de advertencia
        mensajes.append(
            ("warning", "⚠️ No se seleccionaron archivos para cargar."))

    st.session_state["mensajes_carga"] = mensajes

from pathlib import Path
import streamlit as st

def eliminar_archivos():
    """
    Elimina todos los archivos .txt del directorio de origen de datos y del directorio procesado.
    """
    # Limpiar mensajes previos
    st.session_state.pop("mensaje_eliminacion", None)

    try:
        carpetas = [Path(DATA_SOURCE_DIR), Path(DATA_PROCESSED_DIR)]
        total_eliminados = 0
        archivos_encontrados = False

        for carpeta in carpetas:
            archivos = list(carpeta.glob("*.txt"))
            if archivos:
                archivos_encontrados = True
                for archivo in archivos:
                    archivo.unlink()
                total_eliminados += len(archivos)

        if not archivos_encontrados:
            st.session_state["mensaje_eliminacion"] = (
                "warning", "⚠️ No hay archivos para eliminar.")
        else:
            st.session_state["mensaje_eliminacion"] = (
                "success", f"🗑️ {total_eliminados} archivo(s) eliminados correctamente.")

    except Exception as e:
        st.session_state["mensaje_eliminacion"] = (
            "error", f"❌ Error al eliminar archivos: {e}")
