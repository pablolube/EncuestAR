#-----------------------------------------------------------------------------------------------------------------------------
# Librerías 
#-----------------------------------------------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from src.utils.constants import AGLOMERADOS_NOMBRES,COORDENADAS_AGLOMERADOS



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
    df['AGLOMERADO_NOMBRE'] = df['AGLOMERADO'].map(AGLOMERADOS_NOMBRES)
    return df

def calcular_tasa_emp_desemp(df, condicion=None, agrupacion=['ANO4', 'TRIMESTRE']):
    """
    Calcula la tasa de empleo y/o desempleo por las columnas que se pasen en 'agrupacion'.

    Parámetros:
    - df: DataFrame con las columnas 'CONDICION_LABORAL', 'PONDERA' y las que se agrupen.
    - condicion: 'Desocupado', 'Ocupado' o None (para ambas tasas).
    - agrupacion: lista de columnas para agrupar dinámicamente.

    Devuelve:
    - DataFrame con la(s) tasa(s) calculada(s) por grupo.
    """

    # Me aseguro que se una lista
    if isinstance(agrupacion, str):
        agrupacion = [agrupacion]

    # Agrupo y  calculo  sumatorias ponderadas por tipo de empleo
    df_tasa = df.groupby(agrupacion).apply(lambda g: pd.Series({
        'Desocupado': g[g['CONDICION_LABORAL'] == 'Desocupado']['PONDERA'].sum(),
        'Ocupado': g[g['CONDICION_LABORAL'].str.contains('Ocupado', na=False)]['PONDERA'].sum()
    })).reset_index()

    # Del agrupado calculo el total
    total = df_tasa['Desocupado'] + df_tasa['Ocupado']

    # Calcular tasas
    df_tasa['Tasa de Desempleo'] = round((df_tasa['Desocupado'] / total) * 100, 2)
    df_tasa['Tasa de Empleo'] = round((df_tasa['Ocupado'] / total) * 100, 2)

    # Armar columnas a devolver según parámetro
    if condicion == 'Desocupado':
        columnas = agrupacion + ['Tasa de Desempleo']
    elif condicion == 'Ocupado':
        columnas = agrupacion + ['Tasa de Empleo']
    elif condicion ==None or 'ambas':
        columnas = agrupacion + ['Tasa de Desempleo', 'Tasa de Empleo']

    return df_tasa[columnas].sort_values(by=agrupacion)

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

def graficar_tasa(df,eje_x ,eje_y, titulo):
    """
    Grafica la evolución temporal de una tasa usando Plotly.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'Fecha' y una tasa.
        columna_tasa (str): Nombre de la columna que contiene la tasa a graficar.
        titulo (str): Título del gráfico.
    """
    fig = px.line(df, x=eje_x, y=eje_y, title=titulo)
    fig.show()
    st.plotly_chart(fig)


#-----------------------------------------------------------------------------------------------------------------------------
# STREAMLIT APP: ACTIVIDAD Y EMPLEO
#-----------------------------------------------------------------------------------------------------------------------------

# Configuración de la página
st.set_page_config(page_title='Actividad y Empleo', layout="wide")

# Cabecera
st.title('📊 Actividad y Empleo en Argentina')
st.markdown("Análisis exploratorio de datos del mercado laboral basado en la Encuesta Permanente de Hogares (EPH).")
st.markdown('---')

# Dataset cargado desde session_state
if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:
    df_empleo = st.session_state.df_ind[
        ['AGLOMERADO', 'ANO4', 'TRIMESTRE', 'NIVEL_ED_str', 'CONDICION_LABORAL', 'PONDERA', 'PP04A']
    ].copy()

    anio_trim = df_empleo.groupby('ANO4')['TRIMESTRE'].unique().apply(list).to_dict()

    # ----------------------------------------
    # 1. Desocupación según nivel educativo
    # ----------------------------------------
    st.header("1. 📉 Desocupación según Nivel Educativo")
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

    st.markdown("### 📊 Gráfico: Distribución de la desocupación por nivel educativo")
    if df_educacion_desocupado.empty:
        st.warning("⚠️ No se encontraron datos de personas desocupadas para el año y trimestre seleccionados.")
    else:
        st.pyplot(grafica_barras(
            df_educacion_desocupado,
            titulo=f"Desocupados por Nivel Educativo ({anio} - T{trimestre})",
            xlabel="Cantidad estimada de personas",
            ylabel="Nivel educativo")
        )

    # ----------------------------------------
    # 2. Evolución de la tasa de desempleo
    # ----------------------------------------
    st.markdown('---')
    st.header("2. 📈 Evolución de la Tasa de Desempleo")
    st.markdown("Observá cómo evoluciona la tasa de desempleo a lo largo del tiempo para diferentes aglomerados urbanos.")

    df_empleo = mapear_nombres_aglomerados(df_empleo)
    aglomerados = listar(df_empleo, 'AGLOMERADO_NOMBRE')

    seleccionados = st.multiselect(
        "🗺️ Seleccioná uno o más aglomerados",
        options=aglomerados,
        default=aglomerados,
        key="desempleo_aglomerados"
    )

    df_filtrados = df_empleo[df_empleo['AGLOMERADO_NOMBRE'].isin(seleccionados)]
    condicion_valida = ['Ocupado autónomo', 'Ocupado dependiente', 'Desocupado']
    df_filtrado = df_filtrados[df_filtrados['CONDICION_LABORAL'].isin(condicion_valida)]

    df_tasa_desempleo = calcular_tasa_emp_desemp(df_filtrado, condicion='Desocupado')

    st.markdown("### 📄 Tabla: Tasa de Desempleo")
    st.dataframe(df_tasa_desempleo, use_container_width=True)
    
    df_tasa_desempleo = agregar_columna_fecha(df_tasa_desempleo)
    graficar_tasa(df_tasa_desempleo,'Fecha', 'Tasa de Desempleo', '📊 Evolución de la Tasa de Desempleo')

    # ----------------------------------------
    # 3. Evolución de la tasa de empleo
    # ----------------------------------------
    st.markdown('---')
    st.header("3. 💼 Evolución de la Tasa de Empleo")
    st.markdown("Visualizá cómo varía la tasa de empleo a lo largo del tiempo para los aglomerados seleccionados.")

    seleccionados_empleo = st.multiselect(
        "🗺️ Seleccioná uno o más aglomerados",
        options=aglomerados,
        default=aglomerados,
        key="multiselect_empleo"    )

    df_filtrados_empleo = df_empleo[df_empleo['AGLOMERADO_NOMBRE'].isin(seleccionados_empleo)]
    df_filtrados_empleo = df_filtrados_empleo[df_filtrados_empleo['CONDICION_LABORAL'].isin(condicion_valida)]

    df_tasa_ocupado = calcular_tasa_emp_desemp(df_filtrados_empleo, condicion='Ocupado')

    st.markdown("### 📄 Tabla: Tasa de Empleo")
    st.dataframe(df_tasa_ocupado, use_container_width=True)

    df_tasa_ocupado = agregar_columna_fecha(df_tasa_ocupado)
    graficar_tasa(df_tasa_ocupado,'Fecha', 'Tasa de Empleo', '📊 Evolución de la Tasa Empleo')

    # ----------------------------------------
    # 4. Distribución del Empleo por Sector
    # ----------------------------------------
    st.markdown('---')
    st.header("4. 🏛️ Distribución del Empleo por Sector (Estatal, Privado u Otro)")
    st.markdown("Explorá cómo se distribuyen los empleos según el sector dentro de cada aglomerado urbano.")

    df_empleo.rename(columns={'PP04A': 'Tipo_empleo'}, inplace=True)
    tipo_empleo_dict = {1: 'Estatal', 2: 'Privado', 3: 'Otro tipo'}
    df_empleo['Tipo_empleo'] = df_empleo['Tipo_empleo'].map(tipo_empleo_dict)

    df_ocupado = df_empleo[df_empleo['CONDICION_LABORAL'].str.contains('Ocupado', na=False)]
    tabla = df_ocupado.groupby(['AGLOMERADO_NOMBRE', 'Tipo_empleo'])['PONDERA'].sum().unstack(fill_value=0)
    tabla['Total_ocupados'] = tabla.sum(axis=1)

    tabla['% Estatal'] = round((tabla['Estatal'] / tabla['Total_ocupados']) * 100, 2)
    tabla['% Privado'] = round((tabla['Privado'] / tabla['Total_ocupados']) * 100, 2)
    tabla['% Otro tipo'] = round((tabla['Otro tipo'] / tabla['Total_ocupados']) * 100, 2)

    df_ocupados_aglomerado = tabla[['Total_ocupados', '% Estatal', '% Privado', '% Otro tipo']].reset_index()

    st.markdown("### 📄 Tabla: Porcentaje de Empleo por Sector y Aglomerado")
    st.dataframe(df_ocupados_aglomerado, use_container_width=True)

    
    # ----------------------------------------
    # 5. Mapa comparativo - PROCESAMIENTO
    # ----------------------------------------

    # Aplico función de tasa de empleo y desempleo
    df_emp_des = calcular_tasa_emp_desemp(df_empleo, condicion=None, agrupacion=['AGLOMERADO_NOMBRE', 'ANO4', 'TRIMESTRE'])

    # Ordeno y obtengo primeros y últimos registros por aglomerado
    df_sorted = df_emp_des.sort_values(by=['AGLOMERADO_NOMBRE', 'ANO4', 'TRIMESTRE'])
    min_date = df_sorted.drop_duplicates(subset='AGLOMERADO_NOMBRE', keep='first')
    max_date = df_sorted.drop_duplicates(subset='AGLOMERADO_NOMBRE', keep='last')

    # Merge entre el primer y último registro de cada aglomerado
    df_emp_des = pd.merge(min_date, max_date, on='AGLOMERADO_NOMBRE', suffixes=('_MIN', '_MAX'))

    # Cálculo de variaciones
    df_emp_des['var_tasa_Empleo'] = df_emp_des['Tasa de Empleo_MAX'] - df_emp_des['Tasa de Empleo_MIN']
    df_emp_des['var_tasa_Desempleo'] = df_emp_des['Tasa de Desempleo_MAX'] - df_emp_des['Tasa de Desempleo_MIN']

    # Selecciono de columnas
    df_emp_des = df_emp_des[['AGLOMERADO_NOMBRE','Tasa de Empleo_MIN', 'Tasa de Empleo_MAX', 'var_tasa_Empleo','Tasa de Desempleo_MIN', 'Tasa de Desempleo_MAX', 'var_tasa_Desempleo']]

    # Lectura y limpieza del archivo de coordenadas
    df_coord = pd.read_json(COORDENADAS_AGLOMERADOS).T
    df_coord['nombre'] = df_coord['nombre'].str.replace('–', '-', regex=False)

    # Merge con coordenadas
    df_emp_des = pd.merge(df_emp_des,df_coord,left_on='AGLOMERADO_NOMBRE',right_on='nombre',how='inner').drop(columns='nombre')
    
    # ----------------------------------------
    # 5. Mapa comparativo - STREAMLIT
    # ----------------------------------------
    # Elección del usuario
    opcion = st.radio("Seleccioná la tasa a visualizar", ["Tasa de Empleo", "Tasa de Desempleo"])

    #Creo mapa
    mapa = folium.Map(location=[-34.5, -58], zoom_start=5)

    # Recorro el df agrego los puntos 
    for _, row in df_emp_des.iterrows():
        lat, lon = row['coordenadas']

        if opcion == "Tasa de Empleo":
            color = "green" if row['var_tasa_Empleo'] > 0 else "red"
            popup_text = f"{row['AGLOMERADO_NOMBRE']}<br>Variación empleo: {row['var_tasa_Empleo']:.2f}%"
        else:
            color = "red" if row['var_tasa_Desempleo'] > 0 else "green"
            popup_text = f"{row['AGLOMERADO_NOMBRE']}<br>Variación desempleo: {row['var_tasa_Desempleo']:.2f}%"

        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=200)
        ).add_to(mapa)

        # Mostrar el mapa en Streamlit
    st_folium(mapa, width=700, height=500)
else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')
