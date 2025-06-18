import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from src.utils.streamlit import cargar_df_hogares 
from src.utils.constants import DATA_SOURCE_DIR
from src.utils.constants import TRIMESTRES
from src.utils.constants import RUTA_ARCHIVO_CANASTA
import re

# Funciones Auxiliares

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

    meses_trimestre = TRIMESTRES[trimestre_ingresado]
    
    df_canasta_basica['indice_tiempo'] = pd.to_datetime(df_canasta_basica.indice_tiempo)
    df_filtrado = df_canasta_basica[(df_canasta_basica.indice_tiempo.dt.year == anio_ingresado) & (df_canasta_basica.indice_tiempo.dt.month.isin(meses_trimestre))]
    
    if df_filtrado.empty:
        raise ValueError(f"No hay datos para el trimestre {trimestre_ingresado} del año {anio_ingresado}.")

    prom_indigencia = round(df_filtrado['linea_indigencia'].mean(), 2)
    prom_pobreza = round(df_filtrado['linea_pobreza'].mean(), 2)
 
    return {
        'linea_pobreza': float(prom_pobreza),
        'linea_indigencia': float(prom_indigencia)
    }


def extraer_anios_trimestres_hogares(df):
    """
        Filtra el dataframe procesado de hogares buscando los (anios, trimestres) disponibles
        
        Parametro:
            df: dataframe procesado en carga de datos que une los archivos cargados
    """
    #Listado año_trimestre
    anio_trim = df.groupby('ANO4')['TRIMESTRE'].unique().apply(list).to_dict() 
    
    return [(anio, trim) for anio, trimestres in anio_trim.items() for trim in trimestres]
    

def cantidad_porcentaje_pobreza(df_hogares, anio, trimestre, promedio_canasta_actual):
    
    filtro_fecha_cantidad_personas = [(df_hogares['ANO4'] == anio) & (df_hogares['TRIMESTRE']) & (int(df_hogares['IX_Tot']) == 4)]
    df_filtrado = df_hogares[filtro_fecha_cantidad_personas]
    
    # Eliminar CODUSU duplicados
    df_filtrado = df_filtrado.drop_duplicates(subset='CODUSU', keep='first')
    
    hogares_totales = df_filtrado['PONDERA'].sum()
    hogares_pobreza = df_filtrado[df_filtrado['ITF'] > promedio_canasta_actual['linea_pobreza']]['PONDERA'].sum()
    hogares_indigencia = df_filtrado[df_filtrado['ITF'] > promedio_canasta_actual['linea_indigencia']]['PONDERA'].sum()

    # Porcentajes
    
#--------------STREAMLIT-------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

st.set_page_config(page_title='Ingresos', layout="wide")
st.title('Ingresos')
st.markdown("Análisis basado en datos de la EPH: Pobreza e indigencia")
st.markdown('---')

# --- Verificar datos cargados ---
if 'df_hogares' in st.session_state and not st.session_state.df_hogares.empty:
    df_hg = st.session_state.df_hogares.copy()
    
    st.markdown("📊 Análisis de Archivo - Selección de Período")
    
    opciones_disponibles = extraer_anios_trimestres_hogares(df_hg)
    if not opciones_disponibles:
        st.warning("No se encontraron archivos válidos con información de año y trimestre.")
    else:   
        # Uso format_func para que se muestre en un formato mas claro ya que se utilizara su formato original de tupla despues
        seleccion = st.selectbox("📅 Seleccioná un período disponible (año y trimestre):", opciones_disponibles, format_func=lambda x: f"{x[0]} - Trimestre {x[1]}") 
        
        anio, trimestre = seleccion
        
        st.session_state["anio_P7"] = anio
        st.session_state["trimestre_P7"] = trimestre

        st.session_state.promedio_canasta = calculo_promedio_canasta_trimestre(int(trimestre), int(anio), RUTA_ARCHIVO_CANASTA)
        st.write(st.session_state.get('promedio_canasta'))     
           
        
#--------Si no existen datos cargados------------------------------------------------------------------
else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')