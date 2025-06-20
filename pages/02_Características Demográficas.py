import streamlit as st
import altair as alt
import pandas as pd
from src.utils.constants import AGLOMERADOS_NOMBRES
from src.utils.streamlit import get_nombre_aglomerado, get_nro_aglomerado, suma_activa, suma_dependiente, get_media_ponderada, get_mediana_ponderada

st.set_page_config(page_title='Características Demográficas',
                   page_icon=':busts_in_silhouette:',
                   layout='wide')

st.header('Características Demográficas', divider=True)

if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:

    df_ind = pd.DataFrame(st.session_state.df_ind)

    # --------------------- Configuración del Sidebar ---------------------------------------------
    secciones = ['Distribución por sexo y edad', 'Edad media por aglomerado',
                 'Dependencia demográfica', 'Media y mediana total']

    st.sidebar.markdown("### Secciones")
    tab = st.sidebar.radio("Seleccionar sección:", secciones)

    with st.sidebar:
        if tab == secciones[0]:
            st.markdown("### Filtros")
            anio_opcion = st.selectbox(
                "Año:", df_ind['ANO4'].unique())
            if anio_opcion is not None:
                trim_opcion = st.selectbox(
                    "Trimestre:", df_ind[df_ind['ANO4'] == anio_opcion]['TRIMESTRE'].unique())
        elif tab == secciones[2]:
            aglomerado_opcion = st.selectbox(
                'Aglomerado:', get_nombre_aglomerado(df_ind['AGLOMERADO']))

    # ------------------------------ CONTENIDO CENTRAL ---------------------------------------------
    # -------------------------------- Punto 1.3.1 -------------------------------------------------
    if tab == secciones[0]:
        df_filtrado = df_ind.loc[(df_ind['ANO4'] == anio_opcion) & (
            df_ind['TRIMESTRE'] == trim_opcion) & (df_ind['CH06'] > 0), ['CH06', 'CH04_str']].dropna()
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
            y=alt.Y('CANTIDAD:Q', title='# de PERSONAS',
                    axis=alt.Axis(titleAnchor='end')),
            color=alt.Color('SEXO_STR:N', title=''),
            xOffset='SEXO_STR:N'
        ).interactive()

        st.markdown('### Distribución por sexo y edad')
        st.markdown(
            f'_Datos correspondientes al **Año: {anio_opcion} - Trimestre: {trim_opcion}**_')
        st.altair_chart(chart, use_container_width=True)

    # ------------------------------ Punto 1.3.2 -----------------------------------------------
    if tab == secciones[1]:

        # Detección del ultimo año y trimestre cargado
        periodo_ind = df_ind[['ANO4', 'TRIMESTRE']].drop_duplicates(
        ).sort_values(['ANO4', 'TRIMESTRE']).values.tolist()
        ultimo_anio = periodo_ind[-1][0]
        ultimo_trimestre = periodo_ind[-1][1]
        st.markdown('### Edad media por Aglomerado')
        st.markdown(
            f'_Datos correspondientes al **Año: {ultimo_anio} - Trimestre: {ultimo_trimestre}**_')

        # Filtrado del dataframe
        columnas = ['CH06', 'AGLOMERADO', 'PONDERA']
        df_filtrado = df_ind.loc[(df_ind['ANO4'] == ultimo_anio) & (
            df_ind['TRIMESTRE'] == ultimo_trimestre) & (df_ind['CH06'] > 0), columnas].dropna()
        df_filtrado['MEDIA_TOTAL'] = round((
            df_filtrado['CH06'] * df_filtrado['PONDERA']).sum() / df_filtrado['PONDERA'].sum(), 2)
        df_filtrado = df_filtrado.groupby(['AGLOMERADO', 'MEDIA_TOTAL'], group_keys=False).apply(
            get_media_ponderada, include_groups=False).reset_index(name='EDAD_MEDIA')
        df_filtrado['NOMBRE_AGLOMERADO'] = df_filtrado['AGLOMERADO'].map(
            AGLOMERADOS_NOMBRES)
        df_filtrado['DESVIACION'] = df_filtrado['EDAD_MEDIA'] - \
            df_filtrado['MEDIA_TOTAL']
        df_filtrado = df_filtrado.loc[:, ['NOMBRE_AGLOMERADO', 'EDAD_MEDIA', 'MEDIA_TOTAL', 'DESVIACION']].sort_values(
            by='DESVIACION', ascending=False)

        # Parametrización del gráfico de barras horizontales
        barras = alt.Chart(df_filtrado).mark_bar().encode(
            x=alt.X('EDAD_MEDIA:Q', title='EDAD MEDIA (AÑOS)'),
            y=alt.Y('NOMBRE_AGLOMERADO:N', sort='-x', title=''),
            color=alt.Color('EDAD_MEDIA:Q', scale=alt.Scale(
                scheme='blues'), legend=None),
            tooltip=[alt.Tooltip('NOMBRE_AGLOMERADO:N', title='AGLOMERADO:'), alt.Tooltip(
                'EDAD_MEDIA:Q', title='EDAD MEDIA:'), alt.Tooltip('MEDIA_TOTAL', title='MEDIA TOTAL'), alt.Tooltip('DESVIACION:Q')]
        ).interactive()

        # Parametrización del gráfico de linea vertical
        linea_media = alt.Chart(df_filtrado).mark_rule(
            strokeDash=[5, 5],
            size=1.5
        ).encode(
            x=alt.X('MEDIA_TOTAL:Q', title=''),
            color=alt.Color('MEDIA_TOTAL:N', title='MEDIA TOTAL',
                            scale=alt.Scale(range=['#FF4B4B']))
        )
        grafico = barras+linea_media

        grafico = grafico.configure_axis(
            labelLimit=500
        )
        st.altair_chart(grafico)

        # Tabla detalle de Datos
        st.markdown('### Detalle')
        st.dataframe(df_filtrado, hide_index=True)

    # --------------------------- Punto 1.3.3 ------------------------------------------------------
    if tab == secciones[2]:
        columnas = ['CH06', 'AGLOMERADO', 'ANO4', 'TRIMESTRE', 'PONDERA']
        df_filtrado = df_ind.loc[((df_ind['AGLOMERADO'] == get_nro_aglomerado(aglomerado_opcion)) & (
            df_ind['CH06'] > 0), columnas)].dropna()
        df_filtrado['ANIO-TRIM'] = df_filtrado['ANO4'].astype(
            str)+"-"+df_filtrado['TRIMESTRE'].astype(str)
        df_filtrado = df_filtrado.groupby('ANIO-TRIM', group_keys=False).apply(lambda g: pd.Series({
            'DEPENDIENTE': suma_dependiente(g),
            'ACTIVA': suma_activa(g)
        }), include_groups=False).reset_index()
        df_filtrado['DEPENDENCIA_DEMOGRAFICA'] = round(
            (df_filtrado['DEPENDIENTE'] / df_filtrado['ACTIVA']) * 100, 2)
        min = df_filtrado['DEPENDENCIA_DEMOGRAFICA'].min()
        max = df_filtrado['DEPENDENCIA_DEMOGRAFICA'].max()

        # configuración gráfico
        chart = alt.Chart(df_filtrado).mark_line(
            point=True
        ).encode(
            x=alt.X('ANIO-TRIM:N', title='AÑO-TRIMESTRE',
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y('DEPENDENCIA_DEMOGRAFICA:Q', title='% DEPENDENCIA',
                    scale=alt.Scale(domain=[min-1, max+1]), axis=alt.Axis(titleAnchor='end')),
            tooltip=['ANIO-TRIM', 'DEPENDENCIA_DEMOGRAFICA']
        )
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            size=15,
            dy=-10,
            color='#007ACC'
        ).encode(
            text='DEPENDENCIA_DEMOGRAFICA:Q'
        )

        st.markdown('### Dependencia demográfica')
        st.markdown(
            f'_Datos para todos los años y trimestres de **{aglomerado_opcion}**_')
        st.altair_chart(chart + text, use_container_width=True)
        st.caption('La **dependencia demográfica** se define como el cociente de la cantidad de población de 0 a 14 años y mayores de 65 (se asumen jubilados) respecto a la población en edad activa (15 a 64 años) multiplicado por 100.')
        st.markdown('### Detalles')
        st.dataframe(df_filtrado, hide_index=True)

    # ------------------------ Punto 1.3.4 -------------------------------------------------------
    if tab == secciones[3]:
        columnas = ['CH06', 'ANO4', 'TRIMESTRE', 'PONDERA']
        df_filtrado = df_ind.loc[(df_ind['CH06'] > 0), columnas].dropna()
        media_ponderada = df_filtrado.groupby(['ANO4', 'TRIMESTRE'], group_keys=False).apply(
            get_media_ponderada, include_groups=False).reset_index(name='MEDIA PONDERADA')
        mediana_ponderada = df_filtrado.groupby(['ANO4', 'TRIMESTRE'], group_keys=False).apply(
            get_mediana_ponderada, include_groups=False).reset_index(name='MEDIANA PONDERADA')
        merge = media_ponderada.merge(
            mediana_ponderada, on=['ANO4', 'TRIMESTRE']).rename(columns={'ANO4': 'AÑO'})
        merge['AÑO-TRIM'] = merge['AÑO'].astype(
            str)+"-"+merge['TRIMESTRE'].astype(str)
        merge = merge.loc[:, ['AÑO-TRIM',
                              'MEDIA PONDERADA', 'MEDIANA PONDERADA']]

        merge_melted = merge.melt(id_vars='AÑO-TRIM',
                                  value_vars=['MEDIA PONDERADA',
                                              'MEDIANA PONDERADA'],
                                  var_name='Tipo',
                                  value_name='Valor')

        # configuración gráfico
        chart = alt.Chart(merge_melted).mark_line(point=True).encode(
            x=alt.X('AÑO-TRIM:N', title='AÑO-TRIMESTRE',
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Valor:Q', title='EDAD (AÑOS)',
                    axis=alt.Axis(titleAnchor='end')),
            # Aquí se define el color con leyenda
            color=alt.Color('Tipo:N', title='Medida'),
            tooltip=['AÑO-TRIM', 'Tipo', 'Valor']
        ).properties(
            title='Edad Media y Mediana de la población total'
        )

        # Muestro el dataframe
        st.markdown('### Edad Media y Mediana de la población total')
        st.markdown(
            '_Datos correspondientes a **todos** los años y trimestres del dataset_')
        st.dataframe(merge, hide_index=True)

        # Gráfico
        st.altair_chart(chart, use_container_width=True)

else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')

#---------------------------------------------------------------------------------------------

st.markdown("---")
st.caption("📊 Fuente: Encuesta Permanente de Hogares (EPH) - INDEC")