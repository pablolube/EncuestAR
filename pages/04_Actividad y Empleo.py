#-----------------------------------------------------------------------------------------------------------------------------
# Librerías para el análisis de datos
##-----------------------------------------------------------------------------------------------------------------------------
# Cargar de archivos de datos y librerías necesarias
import sys
from src.utils.constants import AGLOMERADOS_NOMBRES
from src.utils.constants import INDIVIDUOS_PROCESSED_DIR, HOGARES_PROCESSED_DIR
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import streamlit as st

# Carga de Archivos
sys.path.append("..")

#-----------------------------------------------------------------------------------------------------------------------------
# PROCESOS
##-----------------------------------------------------------------------------------------------------------------------------
### 1.5.1 Para las personas desocupadas, informar la cantidad de ellas según sus estudios alcanzados. Se debe informar para un año y trimestre elegido por el usuario.

def grafica_barras(df, titulo="Desocupados por nivel educativo",
                   xlabel="Cantidad de personas desocupadas",
                   ylabel="Nivel educativo", color="#E67E22"):
    """
    Dibuja un gráfico de barras horizontal en una app de Streamlit.

    Parámetros:
    - df: DataFrame con los datos a graficar (index = categorías, valores = cantidades)
    - titulo: título del gráfico
    - xlabel: etiqueta del eje X
    - ylabel: etiqueta del eje Y
    - color: color de las barras (por defecto naranja)
    """
    fig, ax = plt.subplots()
    df.plot(kind='barh', ax=ax, color=color)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)

    plt.tight_layout()
    return fig



#-----------------------------------------------------------------------------------------------------------------------------
# STREAMLIT
##-----------------------------------------------------------------------------------------------------------------------------

### Configuro pagina
st.set_page_config(page_title='Actividad y Empleo', page_icon='💼')

st.header('Actividad y Empleo')
st.markdown(' ## ')

### CARGO DATASET
if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:
    df_empleo = st.session_state.df_ind[['AGLOMERADO', 'ANO4', 'TRIMESTRE', 'NIVEL_ED_str', 'CONDICION_LABORAL', 'PONDERA','PP04A']].copy()

    #Filtro año
    anio_trim = df_empleo.groupby('ANO4')['TRIMESTRE'].unique().apply(list).to_dict()
    
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1.5.1 Para las personas desocupadas, informar la cantidad de ellas según sus estudios alcanzados.
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
st.subheader("📊 Desocupación según Nivel Educativo")
st.markdown("Seleccioná un **año** y **trimestre** para visualizar cómo se distribuye la desocupación según el nivel educativo alcanzado.")
st.divider()

# FILTRO POR AÑO / TRIMESTRE
col1, col2 = st.columns(2)

with col1:
    anio = st.selectbox("🗓️ Año", list(anio_trim.keys()), key="select_anio")

with col2:
    trimestres = anio_trim.get(anio, [])
    trimestre = st.selectbox("📆 Trimestre", trimestres, key="select_trim")

# PROCESO ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Filtro Dataset
df_filtrado = df_empleo[
    (df_empleo['ANO4'] == anio) &
    (df_empleo['TRIMESTRE'] == trimestre) &
    (df_empleo['CONDICION_LABORAL'] == 'Desocupado')]

# Agrupo Dataset
df_educacion_desocupado = df_filtrado.groupby('NIVEL_ED_str')['PONDERA'].sum().sort_values(ascending=False)


# GRAFICO ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Gráfico
if df_educacion_desocupado.empty:
    st.warning("⚠️ No se encontraron datos de personas desocupadas para el año y trimestre seleccionados.")
else:
    st.pyplot(grafica_barras(df_educacion_desocupado,
                              titulo=f"Desocupados por Nivel Educativo ({anio} - T{trimestre})",
                              xlabel="Cantidad estimada de personas",
                              ylabel="Nivel educativo"))

