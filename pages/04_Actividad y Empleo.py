import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.utils.constants import AGLOMERADOS_NOMBRES
from src.utils.constants import INDIVIDUOS_PROCESSED_DIR, HOGARES_PROCESSED_DIR
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




st.title("Evolución de la tasa de desempleo")

# --- Selector de aglomerado ---
codigos_aglomerados = df_individuos['AGLOMERADO'].unique()
aglomerados_disponibles = {
    codigo: AGLOMERADOS_NOMBRES[codigo]
    for codigo in codigos_aglomerados
    if codigo in AGLOMERADOS_NOMBRES
}
aglomerados_nombres = list(aglomerados_disponibles.values())

aglomerados_seleccionados = st.multiselect(
    "Seleccioná uno o más aglomerados (opcional)", 
    options=aglomerados_nombres
)

# --- Convertir nombres a códigos (si eligieron alguno) ---
nombre_a_codigo = {v: k for k, v in aglomerados_disponibles.items()}
if aglomerados_seleccionados:
    codigos_seleccionados = [nombre_a_codigo[nombre] for nombre in aglomerados_seleccionados]
    df_filtrado = df_individuos[df_individuos['AGLOMERADO'].isin(codigos_seleccionados)]
else:
    df_filtrado = df_individuos.copy()

# --- Crear columna fecha combinada para agrupar ---
df_filtrado['FECHA'] = df_filtrado['ANO4'].astype(str) + 'T' + df_filtrado['TRIMESTRE'].astype(str)

# --- Agrupar por fecha y condición laboral ---
tabla = df_filtrado.groupby(['FECHA', 'CONDICION_LABORAL'])['PONDERA'].sum().unstack().fillna(0)

# --- Calcular tasa de desempleo ---
tabla['Tasa_desempleo'] = tabla.get('Desocupado', 0) / (tabla.get('Ocupado', 0) + tabla.get('Desocupado', 0)) * 100

# --- Visualización ---
st.subheader("Gráfico de evolución")
fig, ax = plt.subplots(figsize=(10, 5))
tabla['Tasa_desempleo'].plot(marker='o', ax=ax, color='#C0392B')
ax.set_ylabel("Tasa de desempleo (%)")
ax.set_xlabel("Fecha (Año y Trimestre)")
ax.set_title("Tasa de desempleo a lo largo del tiempo")
ax.grid(True)
plt.xticks(rotation=45)
st.pyplot(fig)
