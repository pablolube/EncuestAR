import streamlit as st
import altair as alt
import pandas as pd
from src.utils.constants import *
from src.utils.streamlit import get_nombre_aglomerado

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

    pie = alt.Chart(df_educ).mark_arc().encode(
        theta=alt.Theta(field="Cantidad", type="quantitative"),
        color=alt.Color("Nivel educativo:N", 
                        scale=alt.Scale(scheme='orangered'),  
                        legend=alt.Legend(title="Nivel educativo")),
        tooltip=['Nivel educativo', 'Cantidad']).properties(width=350, height=350)

    # Pie y tabla uno al lado del otro
    col1, col2 = st.columns(2)

    with col1:
        st.altair_chart(pie, use_container_width=True)

    with col2:
        st.dataframe(df_educ, hide_index=True)

# ---------------------- EDUCACIÓN - PUNTO 2 ----------------------
def punto_educacion_2(df_ind):
    st.markdown("### Nivel educativo más común alcanzado por grupo etario")

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
            (df_ind['CH06'] >= edad_min) & (df_ind['CH06'] < edad_max) & df_ind['NIVEL_ED_str'].notna()
        ]
        if not df_filtro.empty:
            df_educ = df_filtro.groupby('NIVEL_ED_str', as_index=False).agg({'PONDERA': 'sum'})
            df_educ['Grupo etario'] = grupo
            df_todos.append(df_educ)

    if df_todos:
        df_todos = pd.concat(df_todos, ignore_index=True)
        df_todos.rename(columns={'NIVEL_ED_str': 'Nivel educativo', 'PONDERA': 'Cantidad'}, inplace=True)

        # Marcar el más común con ✔️
        idx_max = df_todos.groupby('Grupo etario')['Cantidad'].idxmax()
        df_destacados = df_todos.loc[idx_max]

        # Colorear: azul para más común, grises para el resto
        niveles = sorted(df_todos['Nivel educativo'].unique())
        grises = ['#b0b0b0', '#a0a0a0', '#909090', '#808080', '#707070', '#606060', '#505050', '#404040']
        gris_map = {niv: grises[i % len(grises)] for i, niv in enumerate(niveles)}
        azul = '#1f77b4'

        # Crear set de combinaciones destacadas
        combinaciones_destacadas = set(zip(df_destacados['Grupo etario'], df_destacados['Nivel educativo']))

        # Asignar color según combinación
        def asignar_color(grupo, nivel):
            return azul if (grupo, nivel) in combinaciones_destacadas else gris_map.get(nivel, 'gray')

        df_todos['Color'] = df_todos.apply(
            lambda row: asignar_color(row['Grupo etario'], row['Nivel educativo']),
            axis=1
        )

        # Gráfico
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

    # Determinar cuántas columnas por fila (por ejemplo, 3)
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
                st.dataframe(
                    df_grupo[['Nivel educativo', 'Cantidad', 'Porcentaje']].reset_index(drop=True),
                    hide_index=True)


# ------------------------ESTRUCTURA DE LA PAGINA------------------

if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:

    df_ind = pd.DataFrame(st.session_state.df_ind)

    # Configuración del Sidebar
    secciones = ['Nivel educativo alcanzado por año', 'Nivel educativo más común alcanzado por grupo etario', '3', '4']
    st.sidebar.markdown("### Secciones")
    tab = st.sidebar.radio("Seleccionar sección:", secciones)

    # Derivación del contenido central según la sección seleccionada
    if tab == secciones[0]:
        punto_educacion_1(df_ind)
    
    if tab == secciones[1]:
        punto_educacion_2(df_ind)

else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')

