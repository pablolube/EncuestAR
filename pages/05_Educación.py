import streamlit as st
import altair as alt
import pandas as pd
from src.utils.streamlit import *
from src.utils.constants import *
from src.consultas.consultas import generar_ranking_hogares_universitarios
import io

#----------------------------------------titulo----------------------

st.set_page_config(page_title="Educación", page_icon="🎓", layout="wide")

st.title('🎓 Educación')
st.markdown(
    """
    <hr style="height:3px;border:none;border-radius:3px;
                background-color:#FF8C00;margin-top:0.5rem;margin-bottom:1.5rem;" />
    """,
    unsafe_allow_html=True
)

# ---------------------- EDUCACIÓN - PUNTO 1 ----------------------

def punto_educacion_1(df_ind):
    """
    Muestra el nivel educativo alcanzado por año.

    """
    st.markdown("### Nivel educativo alcanzado por año")
    
    opciones_anio = sorted(df_ind["ANO4"].dropna().unique())

    # Mostrar selector directamente
    anio_opcion = st.selectbox("Seleccioná el año:", options=opciones_anio)

    if anio_opcion:
        st.markdown(f"**Año seleccionado:** {anio_opcion}")
        # Filtrar
        df_filtrado = df_ind.loc[
            (df_ind['ANO4'] == anio_opcion) & df_ind['NIVEL_ED_str'].notna(),['NIVEL_ED_str', 'PONDERA']]

    if df_filtrado.empty:
        st.warning("No hay datos disponibles para el año seleccionado.")
        return

    # Agrupar y ordenar
    df_educ = df_filtrado.groupby('NIVEL_ED_str', as_index=False).agg({'PONDERA': 'sum'})
    df_educ = df_educ.rename(columns={'NIVEL_ED_str': 'Nivel educativo', 'PONDERA': 'Cantidad'})
    df_educ = df_educ.sort_values(by='Cantidad', ascending=False)

    # Gráfico
    chart = alt.Chart(df_educ).mark_bar().encode(
        x=alt.X('Cantidad:Q', title='Cantidad de personas'),
        y=alt.Y('Nivel educativo:N', sort='-x', title='Nivel educativo'),
        color=alt.Color('Cantidad:Q', scale=alt.Scale(scheme='oranges'), legend=None),
        tooltip=['Nivel educativo', 'Cantidad']
    ).properties(width=600, height=200)

    st.markdown(f'_Distribución para el año **{anio_opcion}**_')
    st.altair_chart(chart, use_container_width=True)

    # Calcular porcentajes antes del gráfico
    df_educ['Porcentaje'] = (df_educ['Cantidad'] / df_educ['Cantidad'].sum() * 100).round(2)

    # Crear una columna con el texto 'Nivel educativo (xx%)'
    df_educ['Etiqueta'] = df_educ.apply(
        lambda row: f"{row['Nivel educativo']} ({row['Porcentaje']}%)", axis=1
    )

    # Gráfico de torta con etiquetas en tooltip
    pie = alt.Chart(df_educ).mark_arc().encode(
        theta=alt.Theta(field="Cantidad", type="quantitative"),
        color=alt.Color("Etiqueta:N", 
                        scale=alt.Scale(scheme='orangered'),  
                        legend=alt.Legend(title="Nivel educativo")),
        tooltip=['Nivel educativo', 'Porcentaje']
    ).properties(width=300, height=300)
    
    # Pie y tabla uno al lado del otro
    col1, col2 = st.columns(2)

    with col1:
        st.altair_chart(pie)

    with col2:
        st.dataframe(df_educ[['Nivel educativo', 'Cantidad']], hide_index=True)

# ---------------------- EDUCACIÓN - PUNTO 2 ----------------------

def punto_educacion_2(df_ind):
    """ Muestra el nivel educativo alcanzado por grupo etario.      
    """

    st.markdown("### Nivel educativo mayormente alcanzado por grupo etario")

    anio_min = df_ind["ANO4"].min()
    anio_max = df_ind["ANO4"].max()
    st.markdown(f"**Se analiza la información del año {anio_min} a {anio_max}**")

    grupos_etarios = {
        '20–30': (20, 30),
        '30–40': (30, 40),
        '40–50': (40, 50),
        '50–60': (50, 60),
        '60+': (60, 150)
    }

    seleccion = st.multiselect(
        "Seleccioná grupo(s) etario(s):",
        options=list(grupos_etarios.keys()),
        default=list(grupos_etarios.keys())
    )

    df_todos = []

    for grupo in seleccion:
        edad_min, edad_max = grupos_etarios[grupo]
        df_filtro = df_ind[
            (df_ind['CH06'] >= edad_min) &
            (df_ind['CH06'] < edad_max) &
            df_ind['NIVEL_ED_str'].notna()
        ]
        if not df_filtro.empty:
            df_educ = df_filtro.groupby('NIVEL_ED_str', as_index=False)['PONDERA'].sum()
            df_educ['Grupo etario'] = grupo
            df_todos.append(df_educ)

    if df_todos:
        df_todos = pd.concat(df_todos, ignore_index=True)
        df_todos.rename(columns={'NIVEL_ED_str': 'Nivel educativo', 'PONDERA': 'Cantidad'}, inplace=True)

        chart = alt.Chart(df_todos).mark_bar().encode(
            x=alt.X('Grupo etario:N',
                    sort=list(grupos_etarios.keys()),
                    title='Grupo etario',
                    axis=alt.Axis(labelAngle=0, labelFontWeight='bold', titleFontWeight='bold')),
            y=alt.Y('Nivel educativo:N',
                    sort='-x',
                    title='Nivel educativo',
                    axis=alt.Axis(labelFontSize=9, labelFontWeight='bold', titleFontWeight='bold')),
            color=alt.Color('Cantidad:Q',
                            scale=alt.Scale(scheme='oranges'),
                            legend=alt.Legend(title="Cantidad")),
            tooltip=['Grupo etario', 'Nivel educativo', 'Cantidad']
        ).properties(width=650, height=300)

        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para los grupos seleccionados.")

    st.markdown("### 📋 Detalle por grupo etario")

    columnas_por_fila = 3
    grupo_chunks = [seleccion[i:i + columnas_por_fila] for i in range(0, len(seleccion), columnas_por_fila)]

    for fila in grupo_chunks:
        cols = st.columns(len(fila))
        for col, grupo in zip(cols, fila):
            df_grupo = df_todos[df_todos['Grupo etario'] == grupo].copy()
            df_grupo = df_grupo.sort_values(by='Cantidad', ascending=False)
            df_grupo['Porcentaje'] = (df_grupo['Cantidad'] / df_grupo['Cantidad'].sum() * 100).round(2)
            with col:
                st.markdown(f"**Grupo {grupo}**")
                st.dataframe(df_grupo[['Nivel educativo', 'Cantidad', 'Porcentaje']], hide_index=True)


# ------------------------PUNTO 3---------------------------------

def punto_educacion_3(df_ind):
    """ 
    Esta función utiliza la función generar_ranking_hogares_universitarios para obtener el ranking.
    Muestra el ranking en una tabla y permite descargarlo como CSV.

    """

    st.markdown("### 🏆 Ranking de aglomerados con mayor % de hogares con universitarios completos")

    # Barra de selección para cantidad de filas a mostrar
    cantidad = st.selectbox(
        "¿Cuántos aglomerados querés visualizar y descargar?",
        options = [5, 10, 15, 20, 25, 30],
        index = 0
    )

    # Convertir DataFrame a lista de diccionarios (porque así lo espera la función)
    data_dict = df_ind.astype(str).to_dict(orient='records')

    # Obtener ranking
    ranking_list = generar_ranking_hogares_universitarios(data_dict, top_n=cantidad)

    # Verificamos que el resultado no esté vacío
    if not ranking_list:
        st.warning("⚠️ El ranking no contiene datos.")
        return

    # Convertir a DataFrame
    df_ranking = pd.DataFrame(ranking_list, columns=[
    'Código Aglomerado',
    'Nombre Aglomerado',
    '% Hogares con Nivel Universitario/Superior'
    ])

    # Formateo a dos decimales para impresion
    df_ranking['% Hogares con Nivel Universitario/Superior'] = df_ranking['% Hogares con Nivel Universitario/Superior'].map(lambda x: f"{x:.2f}").astype(str) + '%'

    # Mostrar tabla
    st.dataframe(df_ranking.style.set_properties(**{
        'text-align': 'center'
    }), hide_index=True)
    
    # Exportar a CSV con UTF-8 con BOM para que Excel lea bien los tildes
    csv_buffer = io.StringIO()
    df_ranking.to_csv(csv_buffer, index=False, encoding='utf-8-sig') 
    csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")  

    # Botón de descarga
    st.download_button(
        label="📥 Descargar ranking en CSV",
        data=csv_bytes,
        file_name="ranking_aglomerados.csv",
        mime="text/csv"
    )


# ------------------------PUNTO 4---------------------------------
def alfabetismo_porcentaje(df_ind):
    """
    Calcula el % de alfabetizados y no alfabetizados por año y trimestre para personas de 6 años o más.
    Retorna un DataFrame con columnas: Año, Trimestre, Alfabetos, No Alfabetos, Total, % Alfabetos, % No Alfabetos
    """
    df = df_ind.copy()
    df = df[df['CH06'].astype(int) >= 6]
    df = df[df['CH09'].isin(['1', '2'])]

    df['CH09'] = df['CH09'].replace({'1': 'Alfabetos', '2': 'No Alfabetos'})
    df['PONDERA'] = df['PONDERA'].astype(int)

    agrupado = (
        df.groupby(['ANO4', 'TRIMESTRE', 'CH09'])['PONDERA']
        .sum()
        .reset_index()
        .pivot_table(index=['ANO4', 'TRIMESTRE'], columns='CH09', values='PONDERA', fill_value=0)
        .reset_index()
    )

    if 'Alfabetos' not in agrupado.columns:
        agrupado['Alfabetos'] = 0
    if 'No Alfabetos' not in agrupado.columns:
        agrupado['No Alfabetos'] = 0

    agrupado['Total'] = agrupado['Alfabetos'] + agrupado['No Alfabetos']
    agrupado['% Alfabetos'] = (agrupado['Alfabetos'] / agrupado['Total'] * 100).round(2)
    agrupado['% No Alfabetos'] = (agrupado['No Alfabetos'] / agrupado['Total'] * 100).round(2)

    return agrupado

def punto_educacion_4(df_ind):
    st.markdown("### 📊 Porcentaje de alfabetización en personas mayores a 6 años")

    # Procesamiento de datos
    df_alf = alfabetismo_porcentaje(df_ind)
    df_alf.rename(columns={'ANO4': 'Año'}, inplace=True)

    # Selección de años
    anios_disponibles = sorted(df_ind['ANO4'].dropna().unique())
    seleccion = st.multiselect(
        "Seleccioná los años a visualizar:",
        options=anios_disponibles,
        default=anios_disponibles
    )

    df_filtrado = df_alf[df_alf['Año'].isin(seleccion)].copy()

    if df_filtrado.empty:
        st.warning("⚠️ No hay datos disponibles para los años seleccionados.")
        return

    # Convertir a formato largo
    df_largo = df_filtrado.melt(
        id_vars=['Año'],
        value_vars=['% Alfabetos', '% No Alfabetos'],
        var_name='Condición',
        value_name='Porcentaje'
    )

    # Asegurarse de que Porcentaje es numérico
    df_largo['Porcentaje'] = pd.to_numeric(df_largo['Porcentaje'], errors='coerce')
    df_largo.dropna(subset=['Porcentaje'], inplace=True)

    # Ordenar años descendente (opcional)
    df_largo['Año'] = df_largo['Año'].astype(str)
    df_largo.sort_values(by='Año', ascending=False, inplace=True)

    # Gráfico de barras horizontales apiladas
    chart = alt.Chart(df_largo).mark_bar().encode(
        x=alt.X('Porcentaje:Q', title='Porcentaje'),
        y=alt.Y('Año:N', sort='-x', title='Año'),
        color=alt.Color('Condición:N',
                        scale=alt.Scale(domain=['% Alfabetos', '% No Alfabetos'],
                                        range=['#2ca02c', '#d62728']),
                        legend=alt.Legend(title="Condición")),
        tooltip=['Año', 'Condición', 'Porcentaje']
    ).properties(width=600, height=300) 

    st.altair_chart(chart, use_container_width=True)


# ------------------------ESTRUCTURA DE LA PAGINA---------------------------------------------------

if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:

    df_ind = pd.DataFrame(st.session_state.df_ind)

    # Configuración del Sidebar
    secciones = ['Nivel educativo por año', 'Nivel educativo por grupo etario', 'Ranking hogares con estudios superiores' ,'Alfabetización en personas mayores a 6 años']
    st.sidebar.markdown("### Secciones")
    tab = st.sidebar.radio("Seleccionar sección:", secciones)

    # Derivación del contenido central según la sección seleccionada
    if tab == secciones[0]:
        punto_educacion_1(df_ind)
    
    if tab == secciones[1]:
        punto_educacion_2(df_ind)
    
    if tab == secciones[2]:
        punto_educacion_3(df_ind)
    
    if tab == secciones[3]:
        punto_educacion_4(df_ind)

else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')

