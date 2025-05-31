import streamlit as st
import altair as alt
import pandas as pd
from src.utils.constants import AGLOMERADOS_NOMBRES

st.set_page_config(page_title='Características Demográficas',
                   page_icon=':busts_in_silhouette:')

st.header('Características Demográficas')
st.markdown(' ### ')

if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:

    # Configuración del Sidebar
    secciones = ['Distribución por sexo y edad', 'Edad media por aglomerado',
                 'Dependencia demográfica', 'Media y mediana total']

    st.sidebar.markdown("### Secciones")
    tab = st.sidebar.radio("Seleccionar sección:", secciones)

    with st.sidebar:
        if tab == secciones[0]:
            st.markdown("### Filtros")
            anio_opcion = st.selectbox(
                "Año:", st.session_state.df_ind['ANO4'].unique())
            if anio_opcion is not None:
                trim_opcion = st.selectbox(
                    "Trimestre:", st.session_state.df_ind[st.session_state.df_ind['ANO4'] == anio_opcion]['TRIMESTRE'].unique())
        elif tab == secciones[2]:
            st.info("Sin filtros disponibles")

    # Contenido Central
    # Punto 1.3.1
    if tab == secciones[0]:
        df_filtrado = st.session_state.df_ind.loc[(st.session_state.df_ind['ANO4'] == anio_opcion) & (
            st.session_state.df_ind['TRIMESTRE'] == trim_opcion) & (st.session_state.df_ind['CH06'] > 0), ['CH06', 'CH04_str']].dropna()
        df_filtrado = df_filtrado.rename(
            columns={'CH06': 'EDAD', 'CH04_str': 'SEXO_STR'})
        df_filtrado["GRUPO_EDAD"] = df_filtrado["EDAD"] // 10 * 10
        df_filtrado["GRUPO_EDAD_STR"] = df_filtrado["GRUPO_EDAD"].astype(
            str) + "-" + (df_filtrado["GRUPO_EDAD"] + 9).astype(str)
        df_filtrado = df_filtrado.groupby(
            ['GRUPO_EDAD', 'GRUPO_EDAD_STR', 'SEXO_STR']).size().reset_index(name='CANTIDAD')
        etiquetas_ejex = df_filtrado['GRUPO_EDAD_STR'].unique().tolist()

        # Parametros Gráfico
        chart = alt.Chart(df_filtrado).mark_bar().encode(
            x=alt.X('GRUPO_EDAD_STR:N', title="RANGO DE EDAD", scale=alt.Scale(
                domain=etiquetas_ejex), axis=alt.Axis(labelAngle=0)),
            y=alt.Y('CANTIDAD:Q', title='# de PERSONAS'),
            color=alt.Color('SEXO_STR:N', title=''),
            xOffset='SEXO_STR:N'
        ).configure_axisY(
            titleAnchor='end'  # Ajusta la posición vertical
        ).interactive()

        st.markdown('### Distribución por sexo y edad')
        st.markdown(
            f'_Datos correspondientes al **Año: {anio_opcion} - Trimestre: {trim_opcion}**_')
        st.altair_chart(chart, use_container_width=True)

    # Punto 1.3.2
    if tab == secciones[1]:

        # Detección del ultimo año y trimestre cargado
        periodo_ind = st.session_state.df_ind[['ANO4', 'TRIMESTRE']].drop_duplicates(
        ).sort_values(['ANO4', 'TRIMESTRE']).values.tolist()
        ultimo_anio = periodo_ind[-1][0]
        ultimo_trimestre = periodo_ind[-1][1]
        st.markdown('### Edad media por Aglomerado')
        st.markdown(
            f'_Datos correspondientes al **Año: {ultimo_anio} - Trimestre: {ultimo_trimestre}**_')

        # Filtrado del dataframe
        columnas = ['CH06', 'AGLOMERADO', 'PONDERA']
        df_filtrado = st.session_state.df_ind.loc[(st.session_state.df_ind['ANO4'] == ultimo_anio) & (
            st.session_state.df_ind['TRIMESTRE'] == ultimo_trimestre) & (st.session_state.df_ind['CH06'] > 0), columnas].dropna()
        df_filtrado['MEDIA_TOTAL'] = round((
            df_filtrado['CH06'] * df_filtrado['PONDERA']).sum() / df_filtrado['PONDERA'].sum(), 2)
        df_filtrado = df_filtrado.groupby(['AGLOMERADO', 'MEDIA_TOTAL']).apply(
            lambda x: round(
                (x['CH06'] * x['PONDERA']).sum() / x['PONDERA'].sum(), 2)
        ).reset_index(name='EDAD_MEDIA')
        df_filtrado['NOMBRE_AGLOMERADO'] = df_filtrado['AGLOMERADO'].map(
            AGLOMERADOS_NOMBRES)
        df_filtrado['DESVIACION'] = df_filtrado['EDAD_MEDIA'] - \
            df_filtrado['MEDIA_TOTAL']
        df_filtrado = df_filtrado.loc[:, ['NOMBRE_AGLOMERADO', 'EDAD_MEDIA', 'MEDIA_TOTAL', 'DESVIACION']].sort_values(
            by='DESVIACION', ascending=False)

        # Parametrización del gráfico de barras horizontales
        barras = alt.Chart(df_filtrado).mark_bar().encode(
            x=alt.X('EDAD_MEDIA:Q', title='EDAD MEDIA'),
            y=alt.Y('NOMBRE_AGLOMERADO:N', sort='-x', title=''),
            color=alt.Color('EDAD_MEDIA:Q', scale=alt.Scale(
                scheme='blues'), legend=None),
            tooltip=[alt.Tooltip('EDAD_MEDIA:Q', title='EDAD MEDIA:'), alt.Tooltip(
                'NOMBRE_AGLOMERADO:N', title='AGLOMERADO:')]
        ).interactive()

        # Parametrización del gráfico de linea vertical
        linea_media = alt.Chart(df_filtrado).mark_rule(
            strokeDash=[5, 5],
            size=1.5
        ).encode(
            x=alt.X('MEDIA_TOTAL:Q', title=''),
            color=alt.Color('MEDIA_TOTAL:N', title='MEDIA TOTAL')
        )
        grafico = barras+linea_media

        grafico = grafico.configure_axis(
            labelAngle=0,
            labelLimit=500
        )
        st.altair_chart(grafico)

        # Tabla detalle de Datos
        st.markdown('### Detalle')
        st.dataframe(df_filtrado, hide_index=True)

else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')
