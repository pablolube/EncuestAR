#-----------------------------------------------------------------------------------------------------------------------------
# Librerías para el análisis de datos
#-----------------------------------------------------------------------------------------------------------------------------
import sys
import os
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import streamlit as st

# Agrega la carpeta raíz al path si estás corriendo desde fuera del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


#-----------------------------------------------------------------------------------------------------------------------------
# FUNCIONES
#-----------------------------------------------------------------------------------------------------------------------------

def grafica_barras(df, titulo="Desocupados por nivel educativo",
                   xlabel="Cantidad de personas desocupadas",
                   ylabel="Nivel educativo", color="#E67E22"):
    fig, ax = plt.subplots()
    df.plot(kind='barh', ax=ax, color=color)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    plt.tight_layout()
    return fig

#Funciones
def mapear_nombres_aglomerados(df) :
    print(df[['AGLOMERADO']].head())
    print(type(AGLOMERADOS_NOMBRES))
    print(type(df['AGLOMERADO']))
    df['AGLOMERADO_NOMBRE'] = df['AGLOMERADO'].map(AGLOMERADOS_NOMBRES)
    print(type(AGLOMERADOS_NOMBRES))

    return df

def calcular_tasa_emp_desemp(df, condicion='Desocupado', agrupacion=['ANO4', 'TRIMESTRE']):
    """
    Calcula la tasa de empleo o desempleo por las columnas que se pasen en 'agrupacion'.

    Parámetros:
    - df: DataFrame con las columnas 'CONDICION_LABORAL', 'PONDERA' y las que se agrupen
    - condicion: 'Desocupado' o 'Ocupado'
    - agrupacion: lista de columnas para agrupar dinámicamente (ej. ['ANO4', 'TRIMESTRE'], o ['REGION'])

    Devuelve:
    - DataFrame con la tasa calculada por grupo
    """
    nombre_tasa = "Desempleo" if condicion == 'Desocupado' else "Empleo"

    # Asegurarse de que agrupacion es lista (por si pasan string)
    if isinstance(agrupacion, str):
        agrupacion = [agrupacion]

    # Agrupar dinámicamente
    grupo = df.groupby(agrupacion)

    # Calcular la suma de ponderados por grupo para cada condición
    df_tasa = grupo.apply(lambda g: pd.Series({
        'Desocupado': g[g['CONDICION_LABORAL'] == 'Desocupado']['PONDERA'].sum(),
        'Ocupado': g[g['CONDICION_LABORAL'].str.contains('Ocupado', na=False)]['PONDERA'].sum()
    })).reset_index()

    # Calcular total
    total = df_tasa['Desocupado'] + df_tasa['Ocupado']

    # Calcular tasa
    df_tasa[f'Tasa de {nombre_tasa}'] = round((df_tasa[condicion] / total) * 100, 2)

    return df_tasa.sort_values(by=agrupacion)

def listar(df, columna):
    """Devuelve una lista de valores únicos de una columna del DataFrame."""
    return df[columna].unique().tolist()

def agregar_columna_fecha(df):
    """
    Agrega una columna 'Fecha' combinando ANO4 y TRIMESTRE para graficar series temporales.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'ANO4' y 'TRIMESTRE'.

    Returns:
        pd.DataFrame: DataFrame con la columna 'Fecha' como datetime.
    """
    df = df.copy()
    df['Fecha'] = df['ANO4'].astype(str) + '-T' + df['TRIMESTRE'].astype(str)
    return df

def graficar_tasa(df, columna_tasa, titulo):
    """
    Grafica la evolución temporal de una tasa usando Plotly.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'Fecha' y una tasa.
        columna_tasa (str): Nombre de la columna que contiene la tasa a graficar.
        titulo (str): Título del gráfico.
    """
    fig = px.line(df, x='Fecha', y=columna_tasa, title=titulo)
    fig.show()
    st.plotly_chart(fig)

#-----------------------------------------------------------------------------------------------------------------------------
# STREAMLIT APP
#-----------------------------------------------------------------------------------------------------------------------------

st.set_page_config(page_title='Actividad y Empleo', page_icon='💼')
st.header('Actividad y Empleo')
st.markdown(' ## ')

# Dataset cargado desde session_state
if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:
    df_empleo = st.session_state.df_ind[['AGLOMERADO', 'ANO4', 'TRIMESTRE', 'NIVEL_ED_str', 'CONDICION_LABORAL', 'PONDERA','PP04A']].copy()

    # Procesos previos
    anio_trim = df_empleo.groupby('ANO4')['TRIMESTRE'].unique().apply(list).to_dict()

    #-------------------------------------------------------------------------------------------------------------------------
    # 1.5.1 Desocupación según nivel educativo
    #-------------------------------------------------------------------------------------------------------------------------
    st.subheader("📊 Desocupación según Nivel Educativo")
    st.markdown("Seleccioná un **año** y **trimestre** para visualizar cómo se distribuye la desocupación según el nivel educativo alcanzado.")

    col1, col2 = st.columns(2)
    with col1:
        anio = st.selectbox("🗓️ Año", list(anio_trim.keys()), key="select_anio")
    with col2:
        trimestre = st.selectbox("📆 Trimestre", anio_trim.get(anio, []), key="select_trim")

    df_filtrado = df_empleo[
        (df_empleo['ANO4'] == anio) &
        (df_empleo['TRIMESTRE'] == trimestre) &
        (df_empleo['CONDICION_LABORAL'] == 'Desocupado')
    ]

    df_educacion_desocupado = df_filtrado.groupby('NIVEL_ED_str')['PONDERA'].sum().sort_values(ascending=False)

    st.divider()
    st.subheader("Tabla de cantidad de desocupados por nivel educativo")
    if df_educacion_desocupado.empty:
        st.warning("⚠️ No se encontraron datos de personas desocupadas para el año y trimestre seleccionados.")
    else:
        st.pyplot(grafica_barras(df_educacion_desocupado,
                                 titulo=f"Desocupados por Nivel Educativo ({anio} - T{trimestre})",
                                 xlabel="Cantidad estimada de personas",
                                 ylabel="Nivel educativo"))

    #-------------------------------------------------------------------------------------------------------------------------
    # 1.5.2 Evolución de la tasa de desempleo
    #-------------------------------------------------------------------------------------------------------------------------
    from src.utils.constants import AGLOMERADOS_NOMBRES

    st.title("📈 Evolución de la tasa de desempleo")


    #Listar Aglomerados
    df_empleo=mapear_nombres_aglomerados(df_empleo)


    aglomerados = listar(df_empleo, 'AGLOMERADO_NOMBRE')

    # Mostrar el multiselect con los nombres de los aglomerados
    seleccionados = st.multiselect("Seleccioná uno o más aglomerados (opcional)",options=aglomerados,default=aglomerados)

    # Filtrar los datos solo con condiciones laborales válidas
    df_filtrados = df_empleo[df_empleo['AGLOMERADO_NOMBRE'].isin(seleccionados)]   

    # Filtrar las condiciones laborales válidas
    condicion_valida =['Ocupado autónomo', 'Ocupado dependiente', 'Desocupado']
    df_filtrado = df_filtrados[df_filtrados['CONDICION_LABORAL'].isin(condicion_valida)]

    # Calcular suma de ponderaciones por grupo
    df_tasa_desempleo = calcular_tasa_emp_desemp(df_filtrado, condicion='Desocupado')

    st.table(df_tasa_desempleo)