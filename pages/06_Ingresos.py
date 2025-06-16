import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime


st.set_page_config(page_title='Ingresos', layout="wide")
st.title('Cantidad y porcentajes de hogares que se encuentran por debajo de la línea de pobreza y por debajo de la línea de indigencia')
st.markdown("Análisis basado en datos de la EPH")
st.markdown('---')


# Funciones Auxiliares

anios_muestra = ('2016','2017','2018','2019','2020','2021','2022','2023','2024')

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