import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from src.utils.streamlit import cargar_df_hogares 
from src.utils.constants import DATA_SOURCE_DIR, TRIMESTRES, RUTA_ARCHIVO_CANASTA

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
        Retorna:
            Lista de tuplas de anios-trimestres disponibles
    """
    #Listado año_trimestre
    anio_trim = df.groupby('ANO4')['TRIMESTRE'].unique().apply(list).to_dict() 
    
    return [(anio, trim) for anio, trimestres in anio_trim.items() for trim in trimestres]
    

def cantidad_porcentaje_pobreza(df_hogares, anio, trimestre, promedio_canasta_actual):
    
    filtro_fecha_cantidad_personas = ((df_hogares['ANO4'] == anio) & 
                                      (df_hogares['TRIMESTRE'] == trimestre) & 
                                      (df_hogares['IX_TOT'] == 4))
    
    df_filtrado = df_hogares[filtro_fecha_cantidad_personas]
    
    # Eliminar CODUSU duplicados
    df_filtrado = df_filtrado.drop_duplicates(subset='CODUSU', keep='first')
    
    # Eliminar filas con ITF nulo antes de hacer filtros de pobreza/indigencia
    df_filtrado = df_filtrado.dropna(subset=['ITF'])
    df_filtrado = df_filtrado[df_filtrado['ITF'] > 0]
    
    hogares_totales = df_filtrado['PONDERA'].sum()

    # Clasificaciones
    filtro_pobreza = ((df_filtrado['ITF'] <= promedio_canasta_actual['linea_pobreza']) &
                      (df_filtrado['ITF'] > promedio_canasta_actual['linea_indigencia']))

    filtro_indigencia = df_filtrado['ITF'] <= promedio_canasta_actual['linea_indigencia']
    filtro_no_pobres = df_filtrado['ITF'] > promedio_canasta_actual['linea_pobreza']

    hogares_pobreza = df_filtrado[filtro_pobreza]['PONDERA'].sum()
    hogares_indigencia = df_filtrado[filtro_indigencia]['PONDERA'].sum()
    hogares_no_pobres = df_filtrado[filtro_no_pobres]['PONDERA'].sum()

    # Porcentajes
    porcentaje_pobreza = (hogares_pobreza / hogares_totales) * 100 if hogares_totales else 0
    porcentaje_indigencia = (hogares_indigencia / hogares_totales) * 100 if hogares_totales else 0
    porcentaje_no_pobres = (hogares_no_pobres / hogares_totales) * 100 if hogares_totales else 0

    # Crear DataFrame final
    df_resultado = pd.DataFrame([
        {'Categoria': 'Por encima de la línea de pobreza',
         'Cantidad': int(round(hogares_no_pobres)),   
         'Porcentaje': round(porcentaje_no_pobres, 2)},
        
        {'Categoria': 'Pobreza',          
         'Cantidad': int(round(hogares_pobreza)),     
         'Porcentaje': round(porcentaje_pobreza, 2)},
        
        {'Categoria': 'Indigencia',       
         'Cantidad': int(round(hogares_indigencia)),  
         'Porcentaje': round(porcentaje_indigencia, 2)}
    ])
    
    return df_resultado

    
#--------------STREAMLIT-------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

st.set_page_config(page_title='Ingresos', layout="wide")
st.title('💰 Ingresos')
st.markdown('---')

# --- Verificar datos cargados ---
if 'df_hogares' in st.session_state and not st.session_state.df_hogares.empty:
    df_hg = st.session_state.get('df_hogares').copy()
    
    st.markdown("📊 Análisis de Archivo - Selección de Período")
    
    opciones_disponibles = extraer_anios_trimestres_hogares(df_hg)
    if not opciones_disponibles:
        st.warning("No se encontraron archivos válidos con información de año y trimestre.")
    else:  
        # Uso format_func para que se muestre en un formato mas claro ya que se utilizara su formato original de tupla despues
        seleccion = st.selectbox("📅 Seleccioná un período disponible (año y trimestre):", opciones_disponibles, format_func=lambda x: f"{x[0]} - Trimestre {x[1]}") 
        
        anio, trimestre = seleccion

        st.info(f"""Para el **año {anio} y trimestre {trimestre}**, se presenta la cantidad y porcentaje de **hogares de 4 integrantes** con ingresos bajo la linea de pobreza e indigencia, con base en la Encuesta Permanente de Hogares (EPH).""")
        
        st.session_state["anio_P7"] = anio
        st.session_state["trimestre_P7"] = trimestre

        promedio_canasta = calculo_promedio_canasta_trimestre(
            int(trimestre), int(anio), RUTA_ARCHIVO_CANASTA
        )
        st.session_state.promedio_canasta = promedio_canasta

        df = cantidad_porcentaje_pobreza(df_hg, anio, trimestre, promedio_canasta)

        # Selector de tipo de gráfico
        tipo_grafico = st.segmented_control(label="Seleccioná el tipo de gráfico", options=["Torta", "Barras"], selection_mode='single')
        
        # Muestra de la tabla generada
        st.dataframe(df)

        # Muestra del grafico seleccionado
        if tipo_grafico == 'Torta':
            #  gráfico de torta
            figura, ax = plt.subplots()
            ax.pie(
                df['Porcentaje'], labels=df['Categoria'], 
                autopct='%1.1f%%', 
                startangle=90, 
                colors=['#4CAF50', '#FFC107', '#F44336'] 
            )
            ax.axis('equal')  
            ax.set_title("Distribución de hogares según situación económica")

            # Mostrar gráfico en Streamlit
            st.pyplot(figura)
                          
        elif tipo_grafico == 'Barras':
            # Barras
            fig, ax = plt.subplots()   
            
            ax.bar(
                df['Categoria'], 
                df['Cantidad'],
                color=['#4CAF50', '#FFC107', '#F44336'],
                width=0.4
            )
            
            ax.set_xlabel('Situacion Economica')   
            ax.set_ylabel('Cantidad de Hogares')
            ax.set_title('Distribución de hogares de 4 integrantes según situación económica')

            st.pyplot(fig) 
        st.markdown("---")
        st.caption("📊 Fuente: Encuesta Permanente de Hogares (EPH) - INDEC")


#--------Si no existen datos cargados------------------------------------------------------------------
else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')