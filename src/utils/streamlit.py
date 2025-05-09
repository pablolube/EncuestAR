from src.utils.constants import DATA_SOURCE_DIR,  DATA_PROCESSED_DIR, FILENAME_HOGARES_PROCESSED, FILENAME_INDIVIDUOS_PROCESSED, HOGARES_PROCESSED_DIR, INDIVIDUOS_PROCESSED_DIR
import streamlit as st
from pathlib import Path
from src.procesamientos.individuos import add_extra_data
from src.procesamientos.hogares import procesar_hogares
from src.utils.helpers import save_to_file,process_file

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
        # Verificar si hay archivos .txt en la carpeta
        archivos_txt = list(Path(DATA_SOURCE_DIR).glob("*.txt"))

        # Si no hay archivos .txt, lanzar advertencia
        if not archivos_txt:
            st.session_state["mensaje_actualizacion"] = (
                "warning", "⚠️ No hay archivos en la carpeta para actualizar. Verifique si agregó los archivos.")
            st.session_state.date_range = None
            return
        else:

            # Filtrar los archivos que contienen 'hogares' o 'individuos' en el nombre
            archivos_validos = [
                archivo for archivo in archivos_txt
                if "hogar" in archivo.name.lower() or "individual" in archivo.name.lower()
            ]

            # Si hay archivos .txt pero ninguno válido, lanzar otra advertencia
            if not archivos_validos:
                st.session_state["mensaje_actualizacion"] = (
                    "warning", "⚠️ Los archivos encontrados no son de la EPH. Verifique los nombres.")
                st.session_state.date_range = None
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
    Carga archivos en el directorio de datos especificado. Solo se permiten archivos .txt que contengan
    'hogares' o 'individuos' en el nombre. Si el archivo ya existe, muestra un mensaje de advertencia.
    
    Args:
        archivos (list): Lista de archivos subidos por el usuario.
    """
    if "mensajes_carga" in st.session_state:
        del st.session_state["mensajes_carga"]

    mensajes = []

    if archivos:
        for uploaded_file in archivos:
            file_name = uploaded_file.name
            lower_name = file_name.lower()
            
            # Verifica si es .txt y contiene 'hogares' o 'individuos'
            if not (file_name.endswith(".txt") and ("hogar" in lower_name or "individual" in lower_name)):
                mensajes.append(
                    ("warning", f"⚠️ El archivo '{file_name}' fue ignorado. Solo se aceptan archivos .txt de la EPH.")
                )
                continue

            file_path = Path(DATA_SOURCE_DIR) / file_name

            if file_path.exists():
                mensajes.append(
                    ("warning", f"⚠️ El archivo '{file_name}' ya existe. No se guardó.")
                )
                continue

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            mensajes.append(
                ("success", f"✅ {file_name} guardado en {file_path}")
            )
    else:
        mensajes.append(
            ("warning", "⚠️ No se seleccionaron archivos para cargar.")
        )

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
            archivos = list(carpeta)
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
