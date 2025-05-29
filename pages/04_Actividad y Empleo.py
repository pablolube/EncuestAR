
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from src.utils.constants import INDIVIDUOS_PROCESSED_DIR, HOGARES_PROCESSED_DIR





import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título de la sección
st.title("📊 Desocupados según estudios alcanzados")

# Cargar datos procesados (asegúrate de tener bien la ruta)
df_individuos =pd.read_csv(INDIVIDUOS_PROCESSED_DIR, sep=";", encoding="utf-8")

# Filtros de año y trimestre
anios_disponibles = sorted(df_individuos['ANO4'].dropna().unique())
trimestres_disponibles = sorted(df_individuos['TRIMESTRE'].dropna().unique())

anio = st.selectbox("Seleccioná un año", anios_disponibles)
trimestre = st.selectbox("Seleccioná un trimestre", trimestres_disponibles)

# Filtro por año, trimestre y condición laboral
df_filtrado = df_individuos[
    (df_individuos['ANO4'] == anio) &
    (df_individuos['TRIMESTRE'] == trimestre) &
    (df_individuos['CONDICION_LABORAL'] == 'Desocupado')
]

# Agrupar por nivel educativo
resultados = df_filtrado.groupby('NIVEL_ED_str')['PONDERA'].sum().sort_values(ascending=False)

# Mostrar tabla
st.subheader("Tabla de cantidad de desocupados por nivel educativo")
st.dataframe(resultados.rename("Cantidad de Personas").to_frame())

# Mostrar gráfico
st.subheader("Gráfico de barras")
fig, ax = plt.subplots()
resultados.plot(kind='barh', ax=ax, color="#E67E22")
ax.set_xlabel("Cantidad ponderada")
ax.set_ylabel("Nivel educativo")
ax.set_title("Desocupados por nivel educativo")
st.pyplot(fig)
