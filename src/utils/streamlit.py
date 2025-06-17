from src.utils.constants import DATA_SOURCE_DIR,  DATA_PROCESSED_DIR, FILENAME_HOGARES_PROCESSED, FILENAME_INDIVIDUOS_PROCESSED, INDIVIDUOS_PROCESSED_DIR, AGLOMERADOS_NOMBRES,HOGARES_PROCESSED_DIR
import streamlit as st
from pathlib import Path
from src.procesamientos.individuos import add_extra_data
from src.procesamientos.hogares import procesar_hogares
from src.utils.helpers import save_to_file, process_file
import pandas as pd

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
        encabezados_h, hogares = process_file(
            DATA_SOURCE_DIR, category="hogar")

        # Agregar columnas derivadas y calcular fechas mínima y máxima para hogares
        min_fecha_hog, max_fecha_hog = procesar_hogares(encabezados_h, hogares)

        # Guardar los hogares procesados en un archivo intermedio
        save_to_file(DATA_PROCESSED_DIR,
                     FILENAME_HOGARES_PROCESSED, encabezados_h, hogares)

        # -------------------------------------------------------------------------------
        # PROCESAMIENTO DE INDIVIDUOS
        # -------------------------------------------------------------------------------

        # Unificar archivos de individuos desde la fuente
        encabezados_i, individuos = process_file(
            DATA_SOURCE_DIR, category="individual")

        # Agregar columnas derivadas y calcular fechas mínima y máxima para individuos
        min_fecha_indiv, max_fecha_indiv = add_extra_data(
            encabezados_i, individuos)

        # Guardar los individuos procesados en un archivo intermedio
        save_to_file(DATA_PROCESSED_DIR,
                     FILENAME_INDIVIDUOS_PROCESSED, encabezados_i, individuos)

        # Calcular la fecha mínima y máxima global entre hogares e individuos

        fechas_validas = [f for f in [min_fecha_hog, min_fecha_indiv,
                                      max_fecha_hog, max_fecha_indiv] if f is not None]
        fecha_min_global = min(fechas_validas) if fechas_validas else None
        fecha_max_global = max(fechas_validas) if fechas_validas else None

        # Resetear el rango de fechas en el estado de la aplicación (Streamlit)
        st.session_state.date_range = fecha_min_global, fecha_max_global

        st.session_state["mensaje_actualizacion"] = (
            "success", "✅ Archivos actualizados correctamente.")

        return fecha_min_global, fecha_max_global
    except Exception as e:
        # Si ocurre un error, guardo el mensaje de error
        st.session_state["mensaje_actualizacion"] = (
            "error", f"❌ Error al actualizar archivos: {e}")
        
def validar_y_cargar(archivos):
    """
    Valida, guarda y chequea los archivos cargados.
    - Solo permite .txt con 'hogar' o 'individual' en el nombre.
    - Verifica que cada año-trimestre tenga ambos tipos de archivo.
    - Devuelve mensajes para mostrar en Streamlit.
    """
    mensajes = []
    pares = {}  # (año, trimestre) -> set('hogar', 'individual')

    if not archivos:
        mensajes.append(("warning", "⚠️ No se seleccionaron archivos para cargar."))
        return mensajes

    for uploaded_file in archivos:
        file_name = uploaded_file.name
        lower_name = file_name.lower()
        partes = file_name.split('_')

        # Validar formato general
        if not (file_name.endswith(".txt") and ("hogar" in lower_name or "individual" in lower_name)):
            mensajes.append(("warning", f"⚠️ El archivo '{file_name}' fue ignorado (nombre o extensión incorrecta)."))
            continue

        if len(partes) != 3:
            mensajes.append(("warning", f"⚠️ El archivo '{file_name}' fue ignorado (estructura del nombre inválida)."))
            continue

        tipo = partes[1]
        fecha = partes[2].replace(".txt", "")

        if not (fecha.startswith("T") and len(fecha) == 4):
            mensajes.append(("warning", f"⚠️ El archivo '{file_name}' fue ignorado (fecha inválida: '{fecha}')."))
            continue

        try:
            trimestre = int(fecha[1])     # T124 → 1
            año = int(fecha[2:])          # T124 → 24
        except ValueError:
            mensajes.append(("warning", f"⚠️ El archivo '{file_name}' tiene una fecha inválida."))
            continue

        # Ruta de guardado
        file_path = Path(DATA_SOURCE_DIR) / file_name
        if file_path.exists():
            mensajes.append(("warning", f"⚠️ El archivo '{file_name}' ya existe."))
            continue

        # Guardar archivo
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Acumular para chequeo de pares
        clave = (año, trimestre)
        pares.setdefault(clave, set()).add(tipo)

    # Chequear consistencia de pares hogar-individual
    inconsistencias = []
    for (año, trimestre), tipos in pares.items():
        if tipos != {'hogar', 'individual'}:
            faltantes = {'hogar', 'individual'} - tipos
            for faltante in faltantes:
                mensajes.append((
                    "warning",
                    f"⚠️ Falta archivo de {faltante} para el Año {año}, Trimestre {trimestre}"
                ))
                inconsistencias.append((año, trimestre, faltante))

    if not any(mensaje[0] == "warning" for mensaje in mensajes):
        mensajes.append(("success", "✅ Archivos validados y cargados correctamente."))
    else:
        mensajes.append(("error", "❌ Algunos archivos no cumplen con los requisitos. Verifique los archivos cargados."))

    st.session_state["mensajes_carga"] = mensajes

def eliminar_archivos():
    """
    Elimina todos los archivos .txt excepto .gitkeep del directorio de origen y del directorio procesado.
    """
    st.session_state.pop("mensaje_eliminacion", None)

    try:
        carpetas = [Path(DATA_SOURCE_DIR), Path(DATA_PROCESSED_DIR)]
        total_eliminados = 0
        archivos_encontrados = False

        for carpeta in carpetas:
            archivos = [archivo for archivo in carpeta.iterdir()
                        if archivo.is_file() and archivo.name != ".gitkeep"]
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
            del st.session_state.df_ind

    except Exception as e:
        st.session_state["mensaje_eliminacion"] = (
            "error", f"❌ Error al eliminar archivos: {e}")


def cargar_df():
    """
    Carga en el sesion state un dataframe con ciertas columnas del dataset de individuos procesados
    """
    try:
        df_ind = pd.DataFrame()
        df_ind = pd.read_csv(INDIVIDUOS_PROCESSED_DIR,delimiter=';', low_memory=False)
        columnas_ind = ['CH04', 'CH06', 'ANO4', 'CH04_str', 'TRIMESTRE','PONDERA', 'AGLOMERADO', 'NIVEL_ED_str', 'CONDICION_LABORAL', 'PP04A']
        df_ind = df_ind.loc[:, columnas_ind]
    except Exception as e:
        print('No se pudo cargar el df', type(e).__name__)
    finally:
        return df_ind
    
def cargar_df_hogares():
    """
    Carga un DataFrame con ciertas columnas del dataset de hogares procesados.
    """
    try:
        df_hogar = pd.DataFrame()
        df_hogar = pd.read_csv(HOGARES_PROCESSED_DIR, delimiter=';', low_memory=False)

        # Selecciono solo las columnas necesarias para tu análisis
        columnas_hogar = [
            'CODUSU', 'NRO_HOGAR', 'ANO4', 'TRIMESTRE', 'AGLOMERADO',
            'PONDERA', 'II7', 'II7_ESP', 'IV3', 'IV9', 'IV12_3', 'TIPO_HOGAR',
            'CONDICION_DE_HABITABILIDAD'
        ]
        df_hogar = df_hogar.loc[:, columnas_hogar]

    except Exception as e:
        print('No se pudo cargar el df de hogares', type(e).__name__)
    finally:
        return df_hogar



def get_nombre_aglomerado(id_aglomerados):
    """
    Devuelve una lista de nombres unicos de algomerados 

    Args:
        id_aglomerados: serie de nros de aglomerados
    """
    return sorted([AGLOMERADOS_NOMBRES[nro] for nro in id_aglomerados.unique()])


def get_nro_aglomerado(aglomerado):
    """
    Devuelve el nro de aglomerado si existe sino None. 

    Args:
        aglomerado: nombre del aglomerado
    """
    return next((k for k, v in AGLOMERADOS_NOMBRES.items() if v == aglomerado), None)


def suma_dependiente(grupo):
    """
    Devuelve la suma de las personas dependientes, consideradas entre 0 y 14 años y mayor o igual a 65 años.
    """
    return grupo.loc[(grupo['CH06'].between(0, 14) | (grupo['CH06'] >= 65)), 'PONDERA'].sum()


def suma_activa(grupo):
    """
    Devuelve la suma de las personas activas, consideradas entre 15 y 64 años.
    """
    return grupo.loc[grupo['CH06'].between(15, 64), 'PONDERA'].sum()


def get_mediana_ponderada(x):
    """
    Devuelve el valor de la mediana ponderada
    """
    ordenado = x.sort_values('CH06')
    acumulado = ordenado['PONDERA'].cumsum()
    total = ordenado['PONDERA'].sum()
    return ordenado.loc[acumulado >= total / 2, 'CH06'].iloc[0]


def get_media_ponderada(x):
    """
    Devuelve el valor de la edad media ponderada rendondeada en 2 decimales.
    """
    media = (x['CH06']*x['PONDERA']).sum() / x['PONDERA'].sum()
    return round(media, 2)
