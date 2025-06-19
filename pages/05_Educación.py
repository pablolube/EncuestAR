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

st.info("""Se presentan distintas representaciones gráficas relativas al nivel educativo alcanzado, con base en la Encuesta Permanente de Hogares (EPH).""")


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

    Args:
        df_ind (pd.DataFrame): DataFrame que contiene la información de los individuos.

    Returns:
        None: Muestra un gráfico y una tabla con el nivel educativo alcanzado por año.

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
        st.markdown("**📊 Distribución del nivel educativo alcanzado**")
        st.altair_chart(pie)

    with col2:
        st.markdown("**📋 Detalle por nivel educativo**")
        st.dataframe(df_educ[['Nivel educativo', 'Cantidad']], hide_index=True)

    st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)


# ---------------------- EDUCACIÓN - PUNTO 2 ----------------------

def punto_educacion_2(df_ind):
    """ Muestra el nivel educativo alcanzado por grupo etario.   
        Args:
        df_ind (pd.DataFrame): DataFrame que contiene la información de los individuos.

    Returns:
        None: Muestra un gráfico y una tabla con el nivel educativo alcanzado por grupo etario.

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

    st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

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

    Args:
        df_ind (pd.DataFrame): DataFrame que contiene la información de los individuos.
    Returns:
        None: Muestra un ranking de aglomerados con mayor porcentaje de hogares con universitarios

    """

    st.markdown("### 🎓 Ranking de aglomerados con mayor % de hogares con nivel universitario completo")

    st.info("En esta sección podés filtrar los datos según la cantidad de universitarios por hogar y el número de aglomerados a mostrar, para su posterior visualización y descarga.")

    # Selector cantidad de universitarios por hogar
    cant_universitarios = st.slider(
        "**Seleccioná la cantidad de universitarios por hogar a filtrar**",
        min_value=0,
        max_value=10,
        value=2,
        step=1,
        help="Usá el deslizador para elegir un valor. Va de naranja (bajo) a rojo (alto)."
    )

    # Selector cantidad de aglomerados a mostrar
    cant_aglomerados = st.slider(
        "**🔍 ¿Cuántos aglomerados querés visualizar y descargar?**",
        min_value=0,
        max_value=45,
        value=10,
        step=1,
        help="Usá el deslizador para elegir un valor. Va de naranja (bajo) a rojo (alto)."
    )

    # Convertir DataFrame a lista de diccionarios (porque así lo espera la función)
    data_dict = df_ind.astype(str).to_dict(orient='records')

    # Obtener ranking
    ranking_list = generar_ranking_hogares_universitarios(data_dict, cant_universitarios, cant_aglomerados)

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
        label="**📥 Descargar ranking en CSV**",
        data=csv_bytes,
        file_name="ranking_aglomerados.csv",
        mime="text/csv"
    )

    # Gráfico de barras por aglomerado

    st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

    st.markdown("**📊 Visualización del ranking de aglomerados**")

    # Convertir columna de porcentaje a numérico (quitando el símbolo % si está)
    df_ranking['% Numérico'] = df_ranking['% Hogares con Nivel Universitario/Superior'].str.replace('%', '').astype(float)

    # Ordenar para gráfico
    df_ranking = df_ranking.sort_values('% Numérico', ascending=True)

    # Gráfico de barras horizontales
    barras = alt.Chart(df_ranking).mark_bar().encode(
        x=alt.X('% Numérico:Q', title='Porcentaje de hogares con nivel universitario o superior'),
        y=alt.Y('Nombre Aglomerado:N', sort='-x', title='Aglomerado'),
        color=alt.Color('% Numérico:Q', scale=alt.Scale(scheme='orangered'), legend=None),
        tooltip=['Nombre Aglomerado', '% Hogares con Nivel Universitario/Superior']
    ).properties(width=600, height=400)

    st.altair_chart(barras, use_container_width=True)

# ------------------------PUNTO 4---------------------------------
def alfabetismo_porcentaje(df_ind):
    """
    Calcula el % de alfabetizados y no alfabetizados por año y trimestre para personas de 6 años o más.
    Retorna un DataFrame con columnas: Año, Trimestre, Alfabetos, No Alfabetos, Total, % Alfabetos, % No Alfabetos
    """
    df = df_ind.copy()
    df = df[df['CH06'].astype(int) >= 6]
    df = df[df['CH09'].isin([1, 2])]

    df['CH09'] = df['CH09'].replace({1: 'Alfabetos', 2: 'No Alfabetos'})
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
    """
    Muestra el porcentaje de alfabetización en personas mayores a 6 años por año y trimestre.
    Permite seleccionar años y muestra un gráfico de barras horizontales apiladas.   

    Args:
        df_ind (pd.DataFrame): DataFrame que contiene la información de los individuos.
    
    Returns:
        None: Muestra un gráfico y una tabla con el porcentaje de alfabetización.
    """
    # Título de la sección
    st.markdown("### 📖 Porcentaje de alfabetización en personas mayores a 6 años")

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
        st.warning("⚠ No hay datos disponibles para los años seleccionados.")
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
                                        range=['#1f77b4', '#ff7f0e']),
                        legend=alt.Legend(title="Condición")),
        tooltip=['Año', 'Condición', 'Porcentaje']
    ).properties(width=350, height=150)

    st.altair_chart(chart, use_container_width=True)

    st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

#grafico de evolucion temporal
    df_lineas = df_filtrado.melt(
        id_vars=['Año', 'TRIMESTRE'],
        value_vars=['% Alfabetos', '% No Alfabetos'],
        var_name='Condición',
        value_name='Porcentaje'
    )
    df_lineas['Periodo'] = df_lineas['Año'].astype(str) + 'T' + df_lineas['TRIMESTRE'].astype(str)

    lineas = alt.Chart(df_lineas).mark_line(point=True).encode(
        x=alt.X('Periodo:N', title='Periodo (Año-Trimestre)', sort=None),
        y=alt.Y('Porcentaje:Q', title='Porcentaje'),
        color=alt.Color(
            'Condición:N',
            scale=alt.Scale(domain=['% Alfabetos', '% No Alfabetos'],
                            range=['#1f77b4', '#ff7f0e']),
            legend=alt.Legend(title="Condición")
        ),
        tooltip=['Periodo', 'Condición', alt.Tooltip('Porcentaje:Q', format=".2f")]
    ).properties(
        width=350,
        height=350,
        title='	📉 Evolución trimestral del porcentaje de alfabetización'
    )

    # Organizacion grafico evolutivo y tabla
    col1, col2 = st.columns(2)

    with col1:
        st.altair_chart(lineas, use_container_width=True)

    with col2:
        st.markdown("📋 **Tabla de alfabetización por año**")
        st.dataframe(df_alf[['Año', 'Alfabetos', 'No Alfabetos']], hide_index=True)

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

#---------------------------------------------------------------------------------------------

st.markdown("---")
st.caption("📊 Fuente: Encuesta Permanente de Hogares (EPH) - INDEC")