#-----------------------------------------------------------------------------------------------------------------------------
# Librerías 
#-----------------------------------------------------------------------------------------------------------------------------
#Constantes
from src.utils.constants import AGLOMERADOS_NOMBRES,COORDENADAS_AGLOMERADOS

#Manejo de datos
import pandas as pd

#Graficos

import plotly.express as px

#Visualizacion Streamlit 
import streamlit as st
import altair as alt


#Mapas
import folium
from streamlit_folium import st_folium
#-----------------------------------------------------------------------------------------------------------------------------
# FUNCIONES
#-----------------------------------------------------------------------------------------------------------------------------

#Funciones
def mapear_nombres_aglomerados(df) :
    """
    Asigna los nombres correspondientes a los códigos de aglomerados en el DataFrame.

    Utiliza un diccionario (AGLOMERADOS_NOMBRES) para mapear los valores de la columna
    'AGLOMERADO' a una nueva columna 'AGLOMERADO_NOMBRE'.

    Parámetros:
        df (pd.DataFrame): DataFrame que contiene una columna 'AGLOMERADO' con códigos numéricos.

    Retorna:
        pd.DataFrame: El mismo DataFrame con una nueva columna 'AGLOMERADO_NOMBRE' que contiene
                      los nombres descriptivos de los aglomerados.
    """  
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

#Graficos
def grafica_pie(df,title="Distribución de personas desocupadas por nivel educativo"):
    """
    Genera un gráfico de torta (pie chart) o de dona (donut chart) que muestra la distribución 
    de personas desocupadas según su nivel educativo.

    Parámetros:
        df (pd.DataFrame): DataFrame que debe contener las columnas 'PONDERA' (peso de cada persona)
                           y 'NIVEL_ED_str' (nivel educativo en formato texto).
        title (str, opcional): Título del gráfico. Por defecto es 
                               "Distribución de personas desocupadas por nivel educativo".

    Retorna:
        plotly.graph_objs._figure.Figure: Figura interactiva de Plotly representando 
                                          la distribución de personas por nivel educativo.
    """
    
    fig = px.pie(
        df,
        values='PONDERA',
        names='NIVEL_ED_str',
        hole=0.3  # Si querés un donut chart
    )

    fig.update_traces(
        textinfo='label+percent',
        hovertemplate='%{label}<br>Personas: %{value:,.0f}<extra></extra>',
        textfont_size=14,
        pull=[0.02]*len(df)  # pequeño desplazamiento para todas
    )

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        showlegend=False,
        margin=dict(t=60, b=30, l=20, r=20)
    )

    return fig

def grafica_barra(df,
                       xlabel="Cantidad estimada de personas",
                       ylabel="Nivel educativo",
                       title="Distribución de personas desocupadas por nivel educativo"):
    

    """
    Genera un gráfico de barras horizontales que muestra la cantidad estimada de personas 
    desocupadas según su nivel educativo. También incluye una línea vertical indicando 
    el valor medio de la variable 'PONDERA'.

    Parámetros:
        df (pd.DataFrame): DataFrame que debe contener las columnas 'PONDERA' 
                           (peso o cantidad estimada de personas) y 'NIVEL_ED_str' 
                           (nivel educativo en formato texto).
        xlabel (str, opcional): Etiqueta del eje X. Por defecto es "Cantidad estimada de personas".
        ylabel (str, opcional): Etiqueta del eje Y. Por defecto es "Nivel educativo".
        title (str, opcional): Título del gráfico. Por defecto es 
                               "Distribución de personas desocupadas por nivel educativo".

    Retorna:
        plotly.graph_objs._figure.Figure: Figura interactiva de Plotly con las barras 
                                          y la línea de promedio.
    """

    media_valor = df['PONDERA'].mean()

    fig = px.bar(
        df,
        x='PONDERA',
        y='NIVEL_ED_str',
        orientation='h',
        text='PONDERA',
       
    )

    fig.add_vline(
        x=media_valor,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Media: {media_valor:,.0f}",
        annotation_position="top right",
        annotation_font_size=12
    )

    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        hovertemplate='%{y}<br>Personas: %{x:,.0f}<extra></extra>'
    )

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=18)),
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        margin=dict(l=60, r=20, t=60, b=30),
        height=450
    )

    return fig

def graficar_tasa(df, eje_x, eje_y, titulo, dominio_y=None, color_linea="#000000", color=None):
    """
    Grafica la evolución temporal de una tasa usando Altair.

    Args:
        df (pd.DataFrame): DataFrame con columnas de fecha/tasa.
        eje_x (str): Nombre de la columna para el eje X.
        eje_y (str): Nombre de la columna con la tasa.
        titulo (str): Título del gráfico.
        dominio_y (tuple, optional): Rango del eje Y (min, max).
        color_linea (str, optional): Color fijo para la línea.
        color (str, optional): Columna para diferenciar líneas por grupo (ej. 'AGLOMERADO_NOMBRE').
    """

    # Tooltip base
    tooltip = [alt.Tooltip(eje_x, title="Período"),
               alt.Tooltip(eje_y, title="Tasa (%)", format=".2f")]
    if color:
        tooltip.append(alt.Tooltip(color, title="Aglomerado"))

    # Base de codificación común
    base = alt.Chart(df).encode(
        x=alt.X(f'{eje_x}:N', title='AÑO-TRIMESTRE', axis=alt.Axis(labelAngle=0)),
        y=alt.Y(f'{eje_y}:Q', title=eje_y,
                scale=alt.Scale(domain=dominio_y) if dominio_y else alt.Undefined,
                axis=alt.Axis(titleAnchor='end')),
        tooltip=tooltip
    )

    if color:
        # Gráfico con agrupamiento por color
        line = base.mark_line(strokeWidth=2).encode(color=alt.Color(f'{color}:N', title="Aglomerado"))
        points = base.mark_point(filled=True, size=50).encode(color=alt.Color(f'{color}:N'))
        chart = line + points

        text = base.mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=14,
            color='black'
        ).encode(
            text=alt.Text(f'{eje_y}:Q', format='.1f'),
            detail=f'{color}:N'
        )
    else:
        # Gráfico simple con color fijo
        chart = alt.Chart(df).mark_line(
            point=alt.OverlayMarkDef(color=color_linea),
            color=color_linea,
            strokeWidth=2
        ).encode(
            x=alt.X(f'{eje_x}:N', title='AÑO-TRIMESTRE', axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f'{eje_y}:Q', title=eje_y,
                    scale=alt.Scale(domain=dominio_y) if dominio_y else alt.Undefined,
                    axis=alt.Axis(titleAnchor='end')),
            tooltip=tooltip
        )

        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=14,
            color='black'
        ).encode(
            text=alt.Text(f'{eje_y}:Q', format='.1f')
        )

    # Mostrar en Streamlit
    st.markdown(f"### {titulo}")
    st.altair_chart(chart + text, use_container_width=True)



def graficar_empleo_por_sector(df, titulo="Distribución del Empleo por Sector en Aglomerados"):
    """
    Genera un gráfico de barras apiladas horizontales que muestra la distribución porcentual 
    del empleo por sector (Estatal, Privado, Otro tipo) en diferentes aglomerados urbanos. 
    Además, incluye anotaciones con el total absoluto de personas ocupadas por aglomerado.

    Parámetros:
        df (pd.DataFrame): DataFrame que debe contener las siguientes columnas:
            - 'AGLOMERADO_NOMBRE': Nombre del aglomerado urbano.
            - '% Estatal': Porcentaje de empleo en el sector estatal.
            - '% Privado': Porcentaje de empleo en el sector privado.
            - '% Otro tipo': Porcentaje de empleo en otros tipos de ocupación.
            - 'Total_ocupados': Cantidad absoluta de personas ocupadas en el aglomerado.

        titulo (str, opcional): Título principal del gráfico. Por defecto es 
                                "Distribución del Empleo por Sector en Aglomerados".

    Retorna:
        plotly.graph_objs._figure.Figure: Objeto Plotly con el gráfico generado, listo 
                                          para visualizarse en Streamlit o cualquier frontend.
    """

    # Calcula dinámicamente la altura del gráfico según la cantidad de filas
    alto = max(400, min(40 * len(df) + 100, 800))

    # Crea un gráfico de barras apiladas horizontales con Plotly Express
    fig = px.bar(
        df,
        y="AGLOMERADO_NOMBRE",          # Eje Y: nombres de los aglomerados
        x=["% Estatal", "% Privado", "% Otro tipo"],  # Eje X: los porcentajes para cada tipo de empleo
        orientation='h',                # Barra horizontal
        title=titulo,                  # Título del gráfico
        labels={"value": "Porcentaje", "AGLOMERADO_NOMBRE": "Aglomerado"},  # Etiquetas de ejes
        height=alto,                   # Altura dinámica calculada
        color_discrete_map={           # Colores específicos para cada tipo de empleo
            "% Estatal": "#636EFA",
            "% Privado": "#EF553B",
            "% Otro tipo": "#00CC96"
        }
    )

    # Configura el layout del gráfico
    fig.update_layout(
        barmode='stack',              # Apila las barras para mostrar la suma total por aglomerado
        xaxis_title="Porcentaje de Empleo",  # Título eje X
        yaxis_title="",               # Sin título eje Y para mejor estética
        legend_title="Tipo de Empleo",# Título de la leyenda
        template="plotly_white",      # Tema blanco limpio
        margin=dict(l=160, r=100, t=80, b=40),  # Márgenes (más margen derecho para texto adicional)
        xaxis=dict(range=[0, 110])    # Rango extendido en X para mostrar texto fuera de la barra (102%)
    )

    # Configura el texto dentro de las barras apiladas
    fig.update_traces(
        texttemplate='%{x:.1f}%',      # Muestra porcentaje con un decimal
        textposition='inside',         # Texto dentro de la barra
        insidetextanchor='middle',     # Centrado en la barra
        cliponaxis=False,              # Permite que el texto salga del área del eje sin cortarse
    )

    # Obtiene la columna con total de ocupados absolutos para cada aglomerado
    totales_ocupados = df["Total_ocupados"]

    anotaciones = []
    # Recorre cada aglomerado para crear anotaciones con el total absoluto
    for i, total in enumerate(totales_ocupados):
        anotaciones.append(dict(
            x=102,                   # Posición fija un poco a la derecha del 100% para el texto
            y=df["AGLOMERADO_NOMBRE"].iloc[i],  # Aglomerado correspondiente (eje Y)
            text=f"{int(total):,}",      # Texto con total formateado con separadores de miles
            showarrow=False,          # Sin flechas apuntando
            font=dict(color="black", size=12, family="Arial"),  # Estilo de la fuente
            xanchor='left',           # Ancla el texto a la izquierda para que empiece justo en x=102
            yanchor='middle',         # Centrado vertical respecto al eje Y
        ))

    # Añade las anotaciones al layout del gráfico
    fig.update_layout(annotations=anotaciones)

    # Devuelve la figura lista para mostrarse en Streamlit o en cualquier interfaz Plotly
    return fig

#-----------------------------------------------------------------------------------------------------------------------------
# STREAMLIT APP: ACTIVIDAD Y EMPLEO
#-----------------------------------------------------------------------------------------------------------------------------

# Configuración de la página
st.set_page_config(page_title="Actividad y Empleo", page_icon="📊",layout="wide")

# Cabecera
st.title('Actividad y Empleo en Argentina')
st.markdown('---')

if 'df_ind' in st.session_state and not st.session_state.df_ind.empty:

    #-----------------------------------------------------------------------------------------------------------------------------
    # ARMADO DATASET
    #-----------------------------------------------------------------------------------------------------------------------------
    # Filtro el Dataset con las variables que voy a utilizar
    df_empleo = st.session_state.df_ind[['AGLOMERADO', 'ANO4', 'TRIMESTRE', 'NIVEL_ED_str', 'CONDICION_LABORAL', 'PONDERA', 'PP04A']].copy()

    df_empleo = mapear_nombres_aglomerados(df_empleo)
    aglomerados = listar(df_empleo, 'AGLOMERADO_NOMBRE')
                                   
    # Listados
    anio_trim = df_empleo.groupby('ANO4')['TRIMESTRE'].unique().apply(list).to_dict() #Listado año_trimestre
          
    #-----------------------------------------------------------------------------------------------------------------------------
    # Barra lateral (Sidebar)
    #-----------------------------------------------------------------------------------------------------------------------------

    st.sidebar.markdown("### Secciones")
    secciones_emp = ['🎓 Educación y Desempleo', '📈 Evolución Laboral', '🏢 Sectores de Empleo', '🗺️ Mapa de variación empleabilidad']
    tab = st.sidebar.radio("Seleccionar sección:", secciones_emp)

    with st.sidebar:
        if tab == secciones_emp[0]:
            st.markdown("### Filtros")
            anio = st.selectbox("Año:", sorted(df_empleo['ANO4'].unique()))
            if anio is not None:
                trimestre = st.selectbox("Trimestre:", sorted(df_empleo[df_empleo['ANO4'] == anio]['TRIMESTRE'].unique()))
        
        if tab == secciones_emp[1]:
            seleccionados = st.multiselect("🗺️ Seleccioná uno o más aglomerados",options=aglomerados,default=aglomerados,key="desempleo_aglomerados")
            if not seleccionados:
                seleccionados = aglomerados

    #-----------------------------------------------------------------------------------------------------------------------------
    # Sección 1: Educación y Desempleo
    #-----------------------------------------------------------------------------------------------------------------------------

    if tab == secciones_emp[0]:

        #-----------------------------------------------------------------------------------------------------------------------------
        # PROCESAMIENTO DE LA INFORMACION
        #-----------------------------------------------------------------------------------------------------------------------------
        
        # Filtro por año, trimestre y condición de desocupación
        
        df_anio_trimestre = df_empleo[
            (df_empleo['ANO4'] == anio) &
            (df_empleo['TRIMESTRE'] == trimestre)
        ]

        # Filtro específico: personas desocupadas dentro del período seleccionado
        df_desocupados = df_anio_trimestre[
            df_anio_trimestre['CONDICION_LABORAL'] == 'Desocupado'
        ]

        # Limpio valores nulos 
        df_desocupados = df_desocupados.dropna(subset=['NIVEL_ED_str'])

        # Agrupo por nivel de ocupación
        df_educacion_desocupado = (df_desocupados.groupby('NIVEL_ED_str')['PONDERA'].sum().reset_index())

        # Ordeno por nivel educativo
        orden_educativo = ['Primario incompleto','Primario completo','Secundario incompleto','Secundario completo','Superior o universitario','Sin Información','S/D']
        df_educacion_desocupado['NIVEL_ED_str'] = pd.Categorical(df_educacion_desocupado['NIVEL_ED_str'],categories=orden_educativo,ordered=True)
        df_educacion_desocupado = df_educacion_desocupado.sort_values('NIVEL_ED_str')

        # Agregar columna de porcentaje
        df_educacion_desocupado['Porcentaje'] = (df_educacion_desocupado['PONDERA'] / df_educacion_desocupado['PONDERA'].sum() * 100)

        #KPIS
        total_poblacion = df_anio_trimestre['PONDERA'].sum()
        total_= df_educacion_desocupado['PONDERA'].sum()
        total_desocupados = df_educacion_desocupado['PONDERA'].sum()
        
        #-----------------------------------------------------------------------------------------------------------------------------
        # Armo Gráficos
        #-----------------------------------------------------------------------------------------------------------------------------
        grafica_barras=grafica_barra(df=df_educacion_desocupado,xlabel="Cantidad estimada de personas", ylabel="Nivel educativo",title="Distribución de personas desocupadas por nivel educativo")
        grafica_torta=grafica_pie(df_educacion_desocupado)
       
        #-----------------------------------------------------------------------------------------------------------------------------
        # Steamlit
        #-----------------------------------------------------------------------------------------------------------------------------
        st.header("🎓 Educación y Desempleo")
        st.info(f"""Para el **año {anio} y trimestre {trimestre}**, se presenta la distribución estimada de personas **desocupadas** según el nivel educativo alcanzado, con base en la Encuesta Permanente de Hogares (EPH).""")

        # KPIS
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="🔢 Total de personas",value=f"{total_poblacion:,.0f}")

        with col2:
            st.metric(label="🔢 Total estimado de personas desocupadas",value=f"{total_desocupados:,.0f}")  

        # Selector de tipo de gráfico
        tipo_grafico = st.segmented_control(label="Seleccioná el tipo de gráfico", options=["Torta", "Barras"], selection_mode='single')

        
        # Gráfico
        col1, col2 = st.columns(2)
        with col1:
            if tipo_grafico == "Torta":
                st.plotly_chart(grafica_torta)
            else:
                st.plotly_chart(grafica_barras,use_container_width=True)
    
    # Tabla resumen
        with col2:
            with st.expander("📋 Tabla detalle: Desocupación por nivel educativo"):
                st.dataframe(df_educacion_desocupado.style.format({
                    "Cantidad de Personas": "{:,.0f}",
                    "Porcentaje": "{:.2f}%"
                }))
        
        st.markdown("---")
        st.caption("📊 Fuente: Encuesta Permanente de Hogares (EPH) - INDEC")
     
    # ========================================================================================================================================================================================================================
    # Sección 2 y 3: Evolución del empleo y desempleo
    # ========================================================================================================================================================================================================================
    if tab == secciones_emp[1]:

        # ========================================================================================
        # PROCESAMIENTO DE LA INFORMACIÓN
        # ========================================================================================

        # Filtrar por aglomerados seleccionados
        df_aglomerados = df_empleo[df_empleo['AGLOMERADO_NOMBRE'].isin(seleccionados)]

        # Mantener solo población económicamente activa
        condiciones_activas = ['Ocupado autónomo', 'Ocupado dependiente', 'Desocupado']
        df_activos = df_aglomerados[df_aglomerados['CONDICION_LABORAL'].isin(condiciones_activas)]

        # Calcular tasa de DESOCUPACIÓN (total y por aglomerado)
        df_desemp_total = agregar_columna_fecha(calcular_tasa_emp_desemp(df_activos, condicion='Desocupado'))
        df_desemp_aglomerado = agregar_columna_fecha(
            calcular_tasa_emp_desemp(df_activos, condicion='Desocupado',
                                    agrupacion=['ANO4', 'TRIMESTRE', 'AGLOMERADO_NOMBRE'])
        )

        # Calcular tasa de EMPLEO (total y por aglomerado)
        df_ocupados_total = agregar_columna_fecha(calcular_tasa_emp_desemp(df_activos, condicion='Ocupado'))
        df_ocupados_aglomerado = agregar_columna_fecha(
            calcular_tasa_emp_desemp(df_activos, condicion='Ocupado',
                                    agrupacion=['ANO4', 'TRIMESTRE', 'AGLOMERADO_NOMBRE'])
        )
        # ========================================================================================
        # VISUALIZACIÓN CON STREAMLIT
        # ========================================================================================

        st.header("📈 Evolución de la Tasa de Empleo y Desempleo")
        st.info("Esta sección permite analizar la evolución del **mercado laboral argentino** "
                    "según la Encuesta Permanente de Hogares (EPH). Podés comparar la información a nivel nacional "
                    "y desagregada por aglomerados.")

        st.markdown("---")

        # ---------- DESOCUPACIÓN ----------
        st.subheader("Evolución de Desempleo")
        st.info("Explorá cómo evoluciona la tasa de desempleo por cada aglomerado seleccionado.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 🔹 Promedio por aglomerados")
            graficar_tasa(df_desemp_total, 'Fecha', 'Tasa de Desempleo',
                        'Tasa de Desempleo (Promedio)', color_linea="#b41f1f") 

        with col2:
            st.markdown("##### 🔸 Detallada Por aglomerado")
            graficar_tasa(df_desemp_aglomerado, 'Fecha', 'Tasa de Desempleo',
                        'Tasa de Desempleo por Aglomerado', color='AGLOMERADO_NOMBRE')

        st.markdown("---")

        # ---------- EMPLEO ----------
        st.subheader("💼 Evolución Tasa de Empleo")
        st.info("Explorá cómo evoluciona la tasa de empleo por cada aglomerado  seleccionado.")

        col1, col2 = st.columns(2)
        
        #Hago que ajuste mejor el grafico

        with col1:
            st.markdown("##### 🔹 Promedio por aglomerados")
            graficar_tasa(df_ocupados_total, 'Fecha', 'Tasa de Empleo',
                        'Tasa de Empleo (Promedio)', dominio_y=(90, 100),color_linea="#279710")  

        with col2:
            st.markdown("##### 🔸 Detallada Por Aglomerado")
            graficar_tasa(df_ocupados_aglomerado, 'Fecha', 'Tasa de Empleo',
                        'Tasa de Empleo por Aglomerado',dominio_y=(90, 100), color='AGLOMERADO_NOMBRE')

        st.markdown("---")
        st.caption("📊 Fuente: Encuesta Permanente de Hogares (EPH) - INDEC")

    # ========================================================================================================================================================================================================================
    # Sección 4: Distribución del Empleo por Sector
    # ========================================================================================================================================================================================================================
    
    if tab == secciones_emp[2] :
        
        # ========================================================================================
        # PROCESAMIENTO DE LA INFORMACIÓN
        # ========================================================================================
        
        #Renombro columna  a 'Tipo de empleo
        df_empleo.rename(columns={'PP04A': 'Tipo_empleo'}, inplace=True)

        #Renombro  valores con diccionario
        tipo_empleo_dict = {1: 'Estatal', 2: 'Privado', 3: 'Otro tipo'}
        df_empleo['Tipo_empleo'] = df_empleo['Tipo_empleo'].map(tipo_empleo_dict)

        #Filtro por ocupados
        df_ocupado = df_empleo[df_empleo['CONDICION_LABORAL'].str.contains('Ocupado', na=False)]

        #Armo mi tabla Estatal,Privado, Otro Tipo
        tabla = df_ocupado.groupby(['AGLOMERADO_NOMBRE', 'Tipo_empleo'])['PONDERA'].sum().unstack(fill_value=0)
        tabla['Total_ocupados'] = tabla.sum(axis=1)
        tabla['% Estatal'] = round((tabla['Estatal'] / tabla['Total_ocupados']) * 100, 2)
        tabla['% Privado'] = round((tabla['Privado'] / tabla['Total_ocupados']) * 100, 2)
        tabla['% Otro tipo'] = round((tabla['Otro tipo'] / tabla['Total_ocupados']) * 100, 2)
        df_ocupados_aglomerado = tabla[['Total_ocupados', '% Estatal', '% Privado', '% Otro tipo']].reset_index()


        # ========================================================================================
        # PRESENTACION STREAMLIT
        # ========================================================================================
        st.header("🏛️ Distribución del Empleo por Sector (Estatal, Privado u Otro)")
        st.info("Explorá cómo se distribuyen los empleo según el sector dentro de cada aglomerado.")

        #Muestro Tabla 
        st.markdown("### 📄 Tabla: Porcentaje de Empleo por Sector y Aglomerado")       
        st.dataframe(df_ocupados_aglomerado, use_container_width=True)
        
        #Muestro Gráfico
        fig = graficar_empleo_por_sector(df_ocupados_aglomerado)
        st.markdown('<div style="max-height:700px; overflow-y:auto;">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("---")
        st.caption("📊 Fuente: Encuesta Permanente de Hogares (EPH) - INDEC")
    
    # ----------------------------------------
    # 5. Mapa comparativo - PROCESAMIENTO
    # ----------------------------------------
    if tab == secciones_emp[3]:
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

          # Agrego columnas de fecha para el popup
        df_emp_des['anio_ini'] = df_emp_des['ANO4_MIN']
        df_emp_des['trim_ini'] = df_emp_des['TRIMESTRE_MIN']
        df_emp_des['anio_fin'] = df_emp_des['ANO4_MAX']
        df_emp_des['trim_fin'] = df_emp_des['TRIMESTRE_MAX']

        # Selección de columnas
        df_emp_des = df_emp_des[[
            'AGLOMERADO_NOMBRE', 'Tasa de Empleo_MIN', 'Tasa de Empleo_MAX', 'var_tasa_Empleo',
            'Tasa de Desempleo_MIN', 'Tasa de Desempleo_MAX', 'var_tasa_Desempleo',
            'anio_ini', 'trim_ini', 'anio_fin', 'trim_fin'
        ]]

        # Lectura y limpieza del archivo de coordenadas
        df_coord = pd.read_json(COORDENADAS_AGLOMERADOS).T
        df_coord['nombre'] = df_coord['nombre'].str.replace('–', '-', regex=False)

        # Merge con coordenadas
        df_emp_des = pd.merge(df_emp_des, df_coord, left_on='AGLOMERADO_NOMBRE', right_on='nombre', how='inner').drop(columns='nombre')

        # ----------------------------------------
        # 5. Mapa comparativo - STREAMLIT
        # ----------------------------------------
        opcion = st.segmented_control(
            label="Seleccioná Tasa",
            options=["Tasa de Empleo", "Tasa de Desempleo"],
            default="Tasa de Empleo"
        )

        st.markdown(f"**🗺️ Mapa de variación de {opcion.lower()} entre los extremos temporales disponibles**")

        mapa = folium.Map(location=[-34.5, -58], zoom_start=5)

        # Recorro el df y agrego los puntos
        for _, row in df_emp_des.iterrows():
            lat, lon = row['coordenadas']
            inicio = f"{row['anio_ini']} T{row['trim_ini']}"
            fin = f"{row['anio_fin']} T{row['trim_fin']}"

            if opcion == "Tasa de Empleo":
                variacion = row['var_tasa_Empleo']
                tasa_ini = row['Tasa de Empleo_MIN']
                tasa_fin = row['Tasa de Empleo_MAX']
                color = "green" if variacion > 0 else "red"
                titulo = "📊 Variación Empleo"
            else:
                variacion = row['var_tasa_Desempleo']
                tasa_ini = row['Tasa de Desempleo_MIN']
                tasa_fin = row['Tasa de Desempleo_MAX']
                color = "red" if variacion > 0 else "green"
                titulo = "📉 Variación Desempleo"

            # Escalar tamaño del círculo
            radio = max(4, min(15, abs(variacion) * 2))

            # Formato del popup
            popup_html = f"""
            <div style="font-family: Arial; font-size: 13px;">
                <strong>📍 {row['AGLOMERADO_NOMBRE']}</strong><br>
                <strong>{titulo}</strong><br>
                Periodo: <em>{inicio} → {fin}</em><br>
                Tasa inicial: {tasa_ini:.2f}%<br>
                Tasa final: {tasa_fin:.2f}%<br>
                Variación: <span style="color:{color}; font-weight:bold;">{variacion:.2f}%</span>
            </div>
            """
            folium.CircleMarker(
                location=[lat, lon],
                radius=radio,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(mapa)

        # Mostrar el mapa fuera del bucle
        st_folium(mapa, width=700, height=500)
        st.markdown("---")
        st.caption("📊 Fuente: Encuesta Permanente de Hogares (EPH) - INDEC")
else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
                 label='Carga de Datos', icon='📂')