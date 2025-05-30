import streamlit as st
import altair as alt

st.set_page_config(page_title='Características Demográficas',
                   page_icon=':busts_in_silhouette:')

st.header('Características Demográficas')
st.markdown(' ## ')

if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:

    df_ind = st.session_state.df_ind.copy()
    df_ind = df_ind.rename(columns={'CH06': 'EDAD', 'CH04': 'SEXO'})

    # Configuración del Sidebar
    secciones = ['Distribución por Sexo y Edad', 'Edad Media por Aglomerado',
                 'Dependencia Demográfica', 'Media y Mediana Total']

    st.sidebar.markdown("### Secciones")
    tab = st.sidebar.radio("Seleccionar sección:", secciones)

    with st.sidebar:
        if tab == secciones[0]:
            st.markdown("### Filtros")
            anio_opcion = st.selectbox("Año:", df_ind['ANO4'].unique())
            if anio_opcion is not None:
                trim_opcion = st.selectbox(
                    "Trimestre:", df_ind[df_ind['ANO4'] == anio_opcion]['TRIMESTRE'].unique())
        elif tab == secciones[2]:
            st.info("Sin filtros disponibles")

    # Contenido Central
    # Punto 1.3.1
    if tab == secciones[0]:
        df_filtrado = df_ind.loc[(df_ind['ANO4'] == anio_opcion) & (
            df_ind['TRIMESTRE'] == trim_opcion) & (df_ind['EDAD'] > 0), ['EDAD', 'SEXO']].dropna()
        df_filtrado["GRUPO_EDAD"] = df_filtrado["EDAD"] // 10 * 10
        df_filtrado["GRUPO_EDAD_STR"] = df_filtrado["GRUPO_EDAD"].astype(
            str) + "-" + (df_filtrado["GRUPO_EDAD"] + 9).astype(str)
        df_filtrado['SEXO_STR'] = df_filtrado['SEXO'].apply(
            lambda x: 'Varón' if x == 1 else 'Mujer')
        df_filtrado = df_filtrado.groupby(
            ['GRUPO_EDAD', 'GRUPO_EDAD_STR', 'SEXO_STR']).size().reset_index(name='CANTIDAD')
        etiquetas_ejex = df_filtrado['GRUPO_EDAD_STR'].unique().tolist()

        # Parametros Gráfico
        chart = alt.Chart(df_filtrado).mark_bar().encode(
            x=alt.X('GRUPO_EDAD_STR:N', title="RANGO DE EDAD", scale=alt.Scale(
                domain=etiquetas_ejex), axis=alt.Axis(labelAngle=0)),
            y=alt.Y('CANTIDAD:Q', title="CANTIDAD"),
            color=alt.Color('SEXO_STR:N', title=''),
            xOffset='SEXO_STR:N'
        ).properties(
            title='Distribución por sexo y edad'
        )
        st.altair_chart(chart, use_container_width=True)

    # Punto 1.3.2


else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')
