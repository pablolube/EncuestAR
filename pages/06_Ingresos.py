import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from src.utils.streamlit import cargar_df_hogares 
from src.utils.constants import DATA_SOURCE_DIR
import re

# Funciones Auxiliares

TRIMESTRES = {
    1: (1,2,3),
    2: (4,5,6),
    3: (7,8,9),
    4: (10,11,12)
}

ruta_archivo = Path('data') / 'Extras' / 'valores-canasta-basica-alimentos-canasta-basica-total-mensual-2016.csv'

def calculo_promedio_canasta_trimestre(trimestre_ingresado, anio_ingresado, ruta):
    
    """
    Calcula los promedios trimestrales de las líneas de indigencia y pobreza.

    Parámetros:
        trimestre (int): Número de trimestre (1 al 4).
        anio (int): Año deseado.
        ruta (Path): Ruta al archivo CSV.

    Retorna:
        dict: Diccionario con los valores promedio de 'linea_pobreza' y 'linea_indigencia'.
    """
    
    df_canasta_basica = pd.read_csv(ruta)

    if trimestre_ingresado not in TRIMESTRES:
        raise ValueError("Trimestre inválido. Debe ser 1, 2, 3 o 4.")
    meses_trimestre = TRIMESTRES[trimestre_ingresado]
    
    df_canasta_basica['indice_tiempo'] = pd.to_datetime(df_canasta_basica.indice_tiempo)
    df_filtrado = df_canasta_basica[(df_canasta_basica.indice_tiempo.dt.year == anio_ingresado) & (df_canasta_basica.indice_tiempo.dt.month.isin(meses_trimestre))]
    
    if df_filtrado.empty():
        raise ValueError(f"No hay datos para el trimestre {trimestre_ingresado} del año {anio_ingresado}.")

    prom_indigencia = round(df_filtrado['linea_indigencia'].mean(), 2)
    prom_pobreza = round(df_filtrado['linea_pobreza'].mean(), 2)
 
    return {
        'linea_pobreza': float(prom_pobreza),
        'linea_indigencia': float(prom_indigencia)
    }

def extraer_anios_trimestres_hogares():
    """Extrae combinaciones (año, trimestre) de nombres de los archivos disponibles."""
    
    archivos_hogar = []
    
    # Listar los archivos en el directorio, no verificamos si esta vacio, porque siempre tiene al menos .gitkeep
    for archivo in DATA_SOURCE_DIR.iterdir():
        if archivo.name.endswith(".txt"):
            nombre = archivo.name.lower()
            if "hogar" in nombre:
                archivos_hogar.append(archivo)
    # no reviso individuos ya que ya se revisa si existen los pares y solo necesito del archivo hogares
    
    patron = re.compile(r'T([1-4])(\d{2})')
    anios_trimestres = set()

    for archivo in archivos_hogar:
        coincidencia = patron.search(archivo.name.upper())
        if coincidencia:
            trimestre, anio_dos_digitos = coincidencia.groups()
            anio = 2000 + int(anio_dos_digitos)
            anios_trimestres.add((anio, int(trimestre)))

    return sorted(anios_trimestres)

#--------------STREAMLIT-------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

st.set_page_config(page_title='Ingresos', layout="wide")
st.title('Ingresos')
st.markdown("Análisis basado en datos de la EPH: Pobreza e indigencia")
st.markdown('---')


if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:

    df_ind = pd.DataFrame(st.session_state.df_ind)
    
    st.markdown("📊 Análisis de Archivo - Selección de Período")
    
    opciones_disponibles = extraer_anios_trimestres_hogares()
    if not opciones_disponibles:
        st.warning("No se encontraron archivos válidos con información de año y trimestre.")
        
    # Uso format_func para que se muestre en un formato mas claro 
    seleccion = st.selectbox("📅 Seleccioná un período disponible (año y trimestre):", opciones_disponibles, format_func=lambda x: f"{x[0]} - Trimestre {x[1]}") 
    
    anio, trimestre = seleccion
    
    st.session_state["anio"] = anio
    st.session_state["trimestre"] = trimestre
    
    st.success(f"Seleccionaste: Año {anio}, Trimestre {trimestre}")
#--------Si no existen datos cargados------------------------------------------------------------------
else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')