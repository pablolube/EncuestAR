import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
from src.utils.constants import AGLOMERADOS_NOMBRES
from src.utils.streamlit import  get_nombre_aglomerado, get_nro_aglomerado
import plotly.express as px
import altair as alt


#------------------------------------------------------------------------------------------------------
#  Funciones auxiliares 
#-------------------------------------------------------------------------------------------------------

# Item 1.4.1
def contar_viviendas_por_anio(df, anio=None):
    """
     Calcula la cantidad total de viviendas ponderadas para un año determinado, 
     eliminando duplicados por hogar.

     Se considera una única fila por hogar (identificado por 'CODUSU') y se suman 
     los valores de la columna 'PONDERA', que representa la expansión muestral 
     del hogar.

     Args:
         df (pandas.DataFrame): DataFrame que contiene los datos de hogares o individuos,
             incluyendo las columnas 'CODUSU', 'ANO4' y 'PONDERA'.
         anio (int, opcional): Año para el cual se desea calcular la cantidad de viviendas.
             Si se omite, se consideran todos los años presentes en el DataFrame.

     Retorna:
         float: Cantidad total de viviendas ponderadas (suma de 'PONDERA' para hogares únicos).
     """
    if anio is not None:
        df = df[df["ANO4"] == anio]
    # Eliminamos duplicados por CODUSU y nos quedamos con la primera fila como representante
    df_unicos = df.drop_duplicates(subset="CODUSU", keep="first")
    # Sumamos los ponderadores de esas viviendas únicas
    total_viviendas_ponderadas = df_unicos["PONDERA"].sum()
    return total_viviendas_ponderadas
#-----------------------------------------------------------------------------------------------------------

# Item 1.4.2
def tipo_vivienda_proporcion(df, anio= None):
    """
    Calcula la proporción de cada tipo de hogar en un DataFrame, para un año específico si se indica.

    La función filtra el DataFrame por año (si se proporciona), y luego calcula la distribución 
    relativa (proporciones) de los valores en la columna 'TIPO_HOGAR', ordenados de mayor a menor.

    Args:
        df (pandas.DataFrame): DataFrame con los datos de hogares, que debe contener las columnas 
            'ANO4' (año) y 'TIPO_HOGAR' (tipo de hogar).
        anio (int, opcional): Año para el cual se desea calcular la proporción. Si se omite, 
            se consideran todos los años presentes en el DataFrame.

    Retorna:
        pandas.Series or None: Serie con las proporciones de cada tipo de hogar. Devuelve `None` 
        si no hay datos disponibles tras el filtrado.
    """
    if anio is not None:
       df = df[df["ANO4"] == anio]
    if df.empty:
        return None
    return df["TIPO_HOGAR"].value_counts(normalize=True).sort_values(ascending=False)
#-----------------------------------------------------------------------------------------------------------

# Item 1.4.3 
def material_piso_por_aglomerado_detallado(df_hogares, anio=None):
    """
    Determina el material predominante del piso por aglomerado, para un año específico o considerando todos los años.

    Para cada aglomerado, se agrupan las viviendas únicas (por CODUSU) y se calcula cuál es el material de piso
    con mayor cantidad ponderada de viviendas, y qué porcentaje representa respecto al total de viviendas del aglomerado.

    Args:
        df_hogares (pd.DataFrame): DataFrame con los datos de hogares provenientes de la EPH.
        anio (int or None): Año a filtrar. Si es None, se incluyen todos los años disponibles.

    Retorna:
        pd.DataFrame or None: DataFrame con columnas:
            - "AGLOMERADO": código del aglomerado
            - "nombre_aglomerado": nombre legible del aglomerado
            - "Material": material predominante del piso
            - "Cantidad de viviendas con el material predominante": cantidad ponderada
            - "Porcentaje": proporción sobre el total de viviendas del aglomerado
        Devuelve None si no hay datos válidos disponibles.
    """
    if anio is not None:
        df_hogares = df_hogares[df_hogares["ANO4"] == anio]

    if df_hogares.empty or "IV3" not in df_hogares.columns or "AGLOMERADO" not in df_hogares.columns or "PONDERA" not in df_hogares.columns:
        return None

    df_hogares = df_hogares.drop_duplicates(subset=["CODUSU"])

    # Mapeo materiales del piso
    material_map = {
        1: "Mosaico/Baldosa/Madera/Cerámica/Alfombra",
        2: "Cemento/Ladrillo fijo",
        3: "Ladrillo suelto/Tierra"
    }
    df_hogares = df_hogares.copy()
    df_hogares["Material"] = df_hogares["IV3"].map(material_map)

    # Total de viviendas ponderadas por aglomerado
    total_por_aglomerado = df_hogares.groupby("AGLOMERADO")["PONDERA"].sum()

    # Cantidad por material por aglomerado
    conteo = df_hogares.groupby(["AGLOMERADO", "Material"])["PONDERA"].sum().reset_index(name="Cantidad")

    # Material predominante por aglomerado
    idx_max = conteo.groupby("AGLOMERADO")["Cantidad"].idxmax()
    resultado = conteo.loc[idx_max].copy()

    # Agrego nombre legible del aglomerado
    resultado["nombre_aglomerado"] = resultado["AGLOMERADO"].map(AGLOMERADOS_NOMBRES)

    resultado["Total_viviendas"] = resultado["AGLOMERADO"].map(total_por_aglomerado)
    resultado["Porcentaje"] = (resultado["Cantidad"] / resultado["Total_viviendas"] * 100).round(2)

    # Renombro columna
    resultado = resultado.rename(columns={
        "Cantidad": "Cantidad de viviendas con el material predominante",
        "Material": "Material"
    })

    return resultado[[
        "AGLOMERADO",
        "nombre_aglomerado",
        "Material",
        "Cantidad de viviendas con el material predominante",
        "Porcentaje"
    ]]

#-----------------------------------------------------------------------------------------------------------

# Item 1.4.4
def calcular_proporcion_bano_por_aglomerado(df_hogar, AGLOMERADOS_NOMBRES, anio=None):
    """
    Calcula la proporción de viviendas con baño por aglomerado para un año dado o para todos los años.

    Este cálculo se realiza sobre los hogares únicos (por 'CODUSU' y 'NRO_HOGAR'), considerando
    la variable 'IV9' que indica si la vivienda cuenta con baño (1 = sí). Si se especifica un año,
    se filtran los datos para ese año; de lo contrario, se usa todo el DataFrame.

    Parámetros
    ----------
    df_hogar : pandas.DataFrame
        DataFrame que contiene los datos de hogares provenientes de la EPH, con al menos las columnas
        'CODUSU', 'NRO_HOGAR', 'ANO4', 'AGLOMERADO' y 'IV9'.
    
    AGLOMERADOS_NOMBRES : dict
        Diccionario que mapea los códigos de aglomerado (int) a sus nombres (str).
        Si se provee, se agrega una columna con los nombres de aglomerados al resultado.

    anio : int, optional
        Año específico para filtrar los datos (por la columna 'ANO4').
        Si se omite, se calculan las proporciones usando todos los años disponibles.

    Retorna
    -------
    pandas.DataFrame
        DataFrame con las columnas:
        - 'AGLOMERADO': código del aglomerado
        - 'total_viviendas': cantidad total de viviendas relevadas en ese aglomerado
        - 'viviendas_con_bano': cantidad de viviendas con baño (IV9 == 1)
        - 'proporcion': proporción de viviendas con baño (cantidad por aglomerado con baño/cantidad total de viviendas del aglomerado)
        - 'nombre_aglomerado': nombre del aglomerado (si se proporciona el diccionario de nombres)
    """
    
    if anio is not None:
        df = df_hogar[df_hogar['ANO4'] == anio].copy()
    else:
        df = df_hogar.copy()
    df = df.drop_duplicates(subset=['CODUSU', 'NRO_HOGAR'])
    df['IV9'] = pd.to_numeric(df['IV9'], errors='coerce')

    resumen = df.groupby('AGLOMERADO').agg(
        total_viviendas=('IV9', 'count'),
        viviendas_con_bano=('IV9', lambda x: (x == 1).sum())
    )
    resumen['proporcion'] = resumen['viviendas_con_bano'] / resumen['total_viviendas']
    resumen = resumen.reset_index()
    
    if AGLOMERADOS_NOMBRES:
        resumen['nombre_aglomerado'] = resumen['AGLOMERADO'].map(AGLOMERADOS_NOMBRES)

    return resumen

def mostrar_grafico_proporcion_bano(resumen, usar_nombres=True):
    """
    Muestra un gráfico de barras con la proporción de viviendas con baño dentro por aglomerado.
    """
    st.subheader("Proporción de viviendas con baño dentro por aglomerado")

    x_labels = resumen['nombre_aglomerado'] if usar_nombres and 'nombre_aglomerado' in resumen.columns else resumen['AGLOMERADO'].astype(str)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x_labels, resumen['proporcion'], color='seagreen')
    ax.set_ylabel('Proporción')
    ax.set_xlabel('Aglomerado')
    ax.set_title('Proporción de viviendas con baño dentro por aglomerado')
    ax.set_ylim(0, 1)
    plt.xticks(rotation=45)
    st.pyplot(fig)
#------------------------------------------------------------------------------------------------------

# Item 1.4.5
def evolucion_regimen_tenencia(df, anio, aglomerado_seleccionado, tipos_tenencia):
    """
    Muestra la evolución trimestral del régimen de tenencia de viviendas para un aglomerado
    específico en un año determinado, utilizando datos ponderados.

    La función filtra los datos del DataFrame de hogares según el aglomerado y el año indicados,
    y clasifica las viviendas según el régimen de tenencia (propietario, inquilino, etc.). Luego,
    agrupa los datos por trimestre y tipo de tenencia, suma los valores ponderados, y calcula
    la proporción relativa de cada tipo dentro de cada trimestre. Finalmente, muestra una tabla
    y un gráfico de barras con los resultados.

    Parámetros
    ----------
    df : pandas.DataFrame
        DataFrame con los datos de hogares de la EPH, debe contener las columnas:
        'AGLOMERADO', 'ANO4', 'TRIMESTRE', 'II7', 'II7_ESP', 'PONDERA'.

    anio : int
        Año a analizar (por ejemplo, 2023).

    aglomerado_seleccionado : int
        Código del aglomerado a mostrar.

    tipos_tenencia : list of str or None
        Lista con los nombres de los tipos de tenencia a incluir en el análisis.
        Si es None, se incluyen todos los tipos posibles.

    Retorna
    -------
    None
        La función no retorna nada explícitamente, pero muestra un gráfico
        en pantalla usando Streamlit.

    Notas
    -----
    - Los valores de la variable II7 indican el régimen de tenencia y se mapean a etiquetas legibles.
    - Si no hay datos ponderados disponibles para el filtro aplicado, se muestra un mensaje de advertencia.
    """

    if anio is None:
        st.error("Debe seleccionar un año específico para ver la evolución trimestral.")
        return

    # Filtro por aglomerado, año y datos válidos de tenencia
    df = df[
        (df['AGLOMERADO'] == aglomerado_seleccionado) &
        (df['ANO4'] == anio) &
        (df['II7'].notna())
    ].copy()

    # Agrego columna 'Periodo'
    df['Periodo'] = df['ANO4'].astype(str) + "T" + df['TRIMESTRE'].astype(str)

    # Mapeo de tenencias
    mapa_tenencia = {
        1: "Propietario vivienda y terreno",
        2: "Propietario solo vivienda",
        3: "Inquilino",
        4: "Ocupante por expensas",
        5: "Ocupante en relación dependencia",
        6: "Ocupante gratuito",
        7: "Ocupante de hecho",
        8: "Sucesión",
        9: "Otra situación"
    }

    # Completo con II7_ESP si II7 es nulo
    df['TENENCIA'] = df['II7'].fillna(df['II7_ESP']).astype(int)
    df['TENENCIA_STR'] = df['TENENCIA'].map(mapa_tenencia)

    # Filtrado por tipos de tenencia seleccionados
    if tipos_tenencia:
        df = df[df['TENENCIA_STR'].isin(tipos_tenencia)]
    else:
        tipos_tenencia = list(mapa_tenencia.values())

    # Agrupar por trimestre y tipo de tenencia, sumando PONDERA
    resumen = df.groupby(['Periodo', 'TENENCIA_STR'])['PONDERA'].sum().reset_index()

    # Asegurar todos los trimestres y tenencias estén representados
    trimestres = [f"{anio}T{i}" for i in range(1, 5)]
    full_index = pd.MultiIndex.from_product(
        [trimestres, tipos_tenencia],
        names=['Periodo', 'TENENCIA_STR']
    )
    resumen = resumen.set_index(['Periodo', 'TENENCIA_STR']).reindex(full_index, fill_value=0).reset_index()

    # Calcular proporciones
    total_por_trimestre = resumen.groupby('Periodo')['PONDERA'].transform('sum')
    resumen['Porcentaje'] = (resumen['PONDERA'] / total_por_trimestre * 100).round(2)

    # Verificación
    if resumen['PONDERA'].sum() == 0:
        st.warning("No hay datos disponibles para la selección realizada.")
        return

    # Mostrar tabla
    nombre_aglomerado = AGLOMERADOS_NOMBRES.get(aglomerado_opcion, aglomerado_opcion)
    #st.markdown(f"#### Evolución del régimen de tenencia - Año {anio}, Aglomerado {aglomerado_seleccionado}")
    st.markdown(f"#### Evolución del régimen de tenencia - Año {anio}, {nombre_aglomerado}")

    # Gráfico
    chart = alt.Chart(resumen).mark_bar().encode(
        x=alt.X('Periodo:N', title='Trimestre', sort=trimestres),
        y=alt.Y('PONDERA:Q', title='Cantidad ponderada de viviendas'),
        color=alt.Color('TENENCIA_STR:N', title='Tipo de tenencia'),
        tooltip=[
            alt.Tooltip('TENENCIA_STR:N', title='Tipo de tenencia'),
            alt.Tooltip('Periodo:N', title='Trimestre'),
            alt.Tooltip('PONDERA:Q', title='Cantidad ponderada', format=','),
            alt.Tooltip('Porcentaje:Q', title='Porcentaje (%)', format='.2f')
        ]
    ).properties(
        width=700,
        height=400,
        title='Evolución del régimen de tenencia'
    )

    st.altair_chart(chart, use_container_width=True)

# ----------------------------------------------------------------------------------------------------
# Item 1.4.6 Viviendas en villa de emergencia
def calcular_viviendas_en_villa_por_aglomerado(df, anio=None):
    """
    Calcula la cantidad y el porcentaje de viviendas ubicadas en villa de emergencia,
    agrupadas por aglomerado, para un año específico o para todos los años.

    Parámetros:
    -----------
    df : pandas.DataFrame
        DataFrame que contiene los datos de viviendas, incluyendo las columnas:
        - 'CODUSU': identificador único de vivienda
        - 'TRIMESTRE': trimestre de la encuesta
        - 'ANO4': año
        - 'IV12_3': indicador de si la vivienda está en una villa de emergencia (1 = sí)
        - 'AGLOMERADO': identificador del aglomerado

    anio : int o None, opcional
        Año a filtrar (por ejemplo, 2023). Si se deja en None, se utilizan todos los años disponibles.

    Retorna:
    --------
    pandas.DataFrame
        DataFrame con las columnas:
        - 'AGLOMERADO': código del aglomerado
        - 'Viviendas en villa': cantidad de viviendas en villa de emergencia
        - 'Total viviendas': cantidad total de viviendas únicas en ese aglomerado
        - 'Porcentaje': porcentaje de viviendas en villa sobre el total, redondeado a 2 decimales,
          ordenado de forma decreciente por cantidad.
    """
    if anio is not None:
        df = df[df["ANO4"] == anio]

    df_sorted = df.sort_values(by=["CODUSU", "TRIMESTRE"])
    df_unicos = df_sorted.drop_duplicates(subset="CODUSU", keep="first")

    total_por_aglomerado = df_unicos.groupby("AGLOMERADO")["CODUSU"].count()
    en_villa = df_unicos[df_unicos["IV12_3"] == 1]
    cantidad_en_villa = en_villa.groupby("AGLOMERADO")["CODUSU"].count()

    df_resultado = pd.DataFrame({
        "Viviendas en villa": cantidad_en_villa,
        "Total viviendas": total_por_aglomerado
    }).fillna(0)

    df_resultado["Porcentaje"] = (df_resultado["Viviendas en villa"] / df_resultado["Total viviendas"]) * 100
    df_resultado = df_resultado.round(2).sort_values(by="Viviendas en villa", ascending=False)

    return df_resultado.reset_index()

# ----------------------------------------------------------------------------------------------------
# Item 1.4.7 Condición de habitabilidad
def calcular_porcentaje_habitabilidad_larga(df, AGLOMERADOS_NOMBRES, anio=None):
    """
    Calcula el porcentaje ponderado de viviendas por condición de habitabilidad en cada aglomerado.
    Devuelve un DataFrame listo para visualización.

    Parámetros:
    -----------
    df : pd.DataFrame
    AGLOMERADOS_NOMBRES : dict
        Mapea códigos de aglomerado a nombres legibles
    anio : int o None
        Año a filtrar (opcional)

    Retorna:
    --------
    DataFrame con columnas: Aglomerado, Condición de habitabilidad, Porcentaje
    """
    if anio is not None:
        df = df[df["ANO4"] == anio]

    df = df.copy()
    df['CONDICION_DE_HABITABILIDAD'] = df['CONDICION_DE_HABITABILIDAD'].str.strip().str.lower().str.capitalize()
    df = df.drop_duplicates(subset="CODUSU", keep="first")

    condiciones_posibles = ["Insuficiente", "Regular", "Saludable", "Buena"]
    aglos = df["AGLOMERADO"].unique()
    combinaciones = pd.MultiIndex.from_product([aglos, condiciones_posibles], names=["AGLOMERADO", "CONDICION_DE_HABITABILIDAD"])

    conteo = df.groupby(["AGLOMERADO", "CONDICION_DE_HABITABILIDAD"])["PONDERA"].sum()
    conteo = conteo.reindex(combinaciones, fill_value=0).reset_index(name="Cantidad")

    total = df.groupby("AGLOMERADO")["PONDERA"].sum().reset_index(name="Total")
    resultado = pd.merge(conteo, total, on="AGLOMERADO", how="left")
    resultado["Porcentaje"] = (resultado["Cantidad"] / resultado["Total"] * 100).round(2)

    resultado["Aglomerado"] = resultado["AGLOMERADO"].map(AGLOMERADOS_NOMBRES)
    resultado["Condición de habitabilidad"] = resultado["CONDICION_DE_HABITABILIDAD"]

    return resultado[["Aglomerado", "Condición de habitabilidad", "Porcentaje"]]

#-----------------------------------------------------------------------------------------------------------------------------
# STREAMLIT : Características de la Vivienda
#-----------------------------------------------------------------------------------------------------------------------------

# Configuración de página
st.set_page_config(page_title='Características de la Vivienda', layout="wide")
st.title('🏠 Características de la Vivienda')
#st.markdown("Análisis basado en datos de la EPH")
st.markdown('---')

# --- Verificar datos cargados ---
if 'df_hogares' in st.session_state and not st.session_state.df_hogares.empty:
    df = st.session_state.df_hogares.copy()

    min_anio = int(df["ANO4"].min())
    max_anio = int(df["ANO4"].max())

    
    secciones = [
        "Cantidad total de viviendas",
        "Tipo de vivienda",
        "Material del piso por aglomerado",
        "Baño dentro del hogar",
        "Evolución del régimen de tenencia",
        "Viviendas en villa de emergencia",
        "Condición de habitabilidad"
    ]
    
    seleccion = st.sidebar.radio("Seleccionar sección:", secciones)

    permitir_todos_los_anios = seleccion != "Evolución del régimen de tenencia"

    # Construir lista de opciones de año
    opciones_anio = sorted(df["ANO4"].unique())
    if permitir_todos_los_anios:
        opciones_anio = ["Todos los años"] + opciones_anio

   # Mostrar selector
    anio_opcion_raw = st.selectbox("Seleccione un año", options=opciones_anio)
 
   # Convertir a int o None
    anio_opcion = None if anio_opcion_raw == "Todos los años" else int(anio_opcion_raw)

    # --- 1.4.1 Cantidad total de viviendas ---
    if seleccion == "Cantidad total de viviendas":
        total = contar_viviendas_por_anio(df, anio_opcion)
        if total is None:
            st.warning(f"⚠️ No hay datos disponibles para el año {anio_opcion}.")
        else:
            total_formateado = f"{total:,.0f}".replace(",", ".")
            #st.metric("Cantidad total de viviendas (ponderadas)", total_formateado)
            st.markdown(f"### 🏠 Cantidad total de viviendas: **{total_formateado}**")

    # --- 1.4.2 Tipo de vivienda ---
    elif seleccion == "Tipo de vivienda":
        dist = tipo_vivienda_proporcion(df, anio_opcion)
    
        if dist is None or dist.empty:
            mensaje_anio = f"el año {anio_opcion}" if anio_opcion is not None else "los datos seleccionados"
            st.warning(f"⚠️ No hay datos disponibles para {mensaje_anio}.")
        else:
            def autopct_con_coma(pct):
                return f"{pct:.1f}".replace('.', ',') + '%'

            titulo_anio = f"Año {anio_opcion}" if anio_opcion is not None else "Todos los años"

            # Ordeno dist de mayor a menor para mejor visualización
            dist = dist.sort_values(ascending=False)

            fig, ax = plt.subplots(figsize=(2.5, 2.5))  # Tamaño ajustado
            colors = plt.cm.Pastel1.colors  # Paleta suave

            wedges, texts, autotexts = ax.pie(
                dist.values,
                labels=dist.index,
                autopct=autopct_con_coma,
                startangle=90,
                colors=colors,
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
                textprops={'fontsize': 10}
            )

            ax.set_title(f"Distribución por tipo de vivienda ({titulo_anio})", fontsize=12)
               
            plt.subplots_adjust(top=0.75)
               
            ax.axis('equal')  # Asegura forma circular

            st.pyplot(fig)

    # 1.4.3 Material del piso por aglomerado 
    elif seleccion == "Material del piso por aglomerado":
        if df is not None and not df.empty:
            resultado = material_piso_por_aglomerado_detallado(df, anio_opcion)

        if resultado is None or resultado.empty:
            mensaje_anio = f"el año {anio_opcion}" if anio_opcion is not None else "los datos seleccionados"
            st.warning(f"⚠️ No hay datos disponibles para {mensaje_anio}.")
        else:
            titulo_anio = f"Año {anio_opcion}" if anio_opcion is not None else "Todos los años"
            st.markdown(f"#### Material predominante del piso por aglomerado ({titulo_anio})")

            resultado_ordenado = resultado.sort_values(by="Porcentaje", ascending=False).copy()

            # Formateo texto porcentaje para el gráfico
            resultado_ordenado["Texto porcentaje"] = resultado_ordenado["Porcentaje"].apply(
                lambda x: f"{x:.2f}".replace(".", ",") + "%"
            )

             
            fig = px.bar(
                resultado_ordenado,
                x="Porcentaje",
                y="nombre_aglomerado",
                orientation='h',
                color="Material",
                title="Material predominante por aglomerado",
                labels={
                         "Material": "Material predominante",
                         "nombre_aglomerado": "Aglomerado",
                         "Porcentaje": "Porcentaje"
                },
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
             
             # Calcular la coordenada x común para alinear todos los textos a la misma distancia
            x_text = resultado_ordenado["Porcentaje"].max() + 3  # espacio fijo a la derecha

            for _, row in resultado_ordenado.iterrows():
                fig.add_annotation(
                    x=x_text,  # misma posición x para todos
                    y=row["nombre_aglomerado"],
                    text=f"{row['Porcentaje']:.2f}%",
                    showarrow=False,
                    font=dict(size=12, color="black"),
                    xanchor="left",
                    yanchor="middle"
                )


            # Ajustes de diseño
            fig.update_layout(
                height=20 * len(resultado_ordenado),  # alto dinámico según cantidad de barras
                margin=dict(l=80, r=160),             # margen derecho ampliado para textos
                xaxis_tickformat=".2f",               # formato de los ticks del eje x
                xaxis_ticksuffix=" %"                 # sufijo de porcentaje
            )

            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)

            
    # Item 1.4.4 Baño dentro del hogar 
    
    elif seleccion == "Baño dentro del hogar":
        resultado = calcular_proporcion_bano_por_aglomerado(df, AGLOMERADOS_NOMBRES, anio_opcion)

        if resultado.empty:
            mensaje_anio = f"el año {anio_opcion}" if anio_opcion is not None else "los datos seleccionados"
            st.warning(f"⚠️ No hay datos disponibles para {mensaje_anio}.")
        else:
            # Título con año o "Todos los años"
            titulo_anio = f"Año {anio_opcion}" if anio_opcion is not None else "Todos los años"
            st.markdown(f"#### Proporción de viviendas con baño dentro del hogar ({titulo_anio})")

            resultado_ordenado = resultado.sort_values(by="proporcion", ascending=False).copy()
            resultado_ordenado["Texto"] = resultado_ordenado["proporcion"].apply(lambda x: f"{x:.2f}")

            fig = px.bar(
                resultado_ordenado,
                x="proporcion",
                y="nombre_aglomerado",
                orientation="h",
                color_discrete_sequence=["#8FD9A8"],  # un solo color pastel
                labels={
                    "proporcion": "Proporción",
                    "nombre_aglomerado": "Aglomerado"
                },
                title="Proporción de viviendas con baño dentro del hogar por aglomerado"
            )
             
            # Anotaciones a la derecha de cada barra
            for _, row in resultado_ordenado.iterrows():
                fig.add_annotation(
                    x=row["proporcion"] + 0.01,
                    y=row["nombre_aglomerado"],
                    text=f"{row['proporcion']:.2f}",
                    showarrow=False,
                    font=dict(size=12, color="black"),
                    xanchor="left",
                    yanchor="middle"
            )
             
            fig.update_layout(
                height=20 * len(resultado_ordenado),
                margin=dict(l=80, r=160),
                xaxis_tickformat=".2f",
                showlegend=False  # oculta leyenda
            )  

            st.plotly_chart(fig, use_container_width=True)


    # Item 1.4.5 Evolución del régimen de tenencia 
    
    elif seleccion == "Evolución del régimen de tenencia":
        # Mostrar nombres legibles de aglomerados
        opciones_aglomerados = get_nombre_aglomerado(df["AGLOMERADO"])
        aglomerado_nombre = st.selectbox("Seleccione un aglomerado", options=opciones_aglomerados)

        # Obtener el código numérico correspondiente
        aglomerado_opcion = get_nro_aglomerado(aglomerado_nombre)
        
        # Diccionario de tipos de tenencia
        tipos_disponibles = {
            1: "Propietario vivienda y terreno",
            2: "Propietario solo vivienda",
            3: "Inquilino",
            4: "Ocupante por expensas",
            5: "Ocupante en relación dependencia",
            6: "Ocupante gratuito",
            7: "Ocupante de hecho",
            8: "Sucesión",
            9: "Otra situación"
        }

        # Multiselección de tipos de tenencia
        seleccion_tenencia = st.multiselect(
            "Seleccione el/los tipos de tenencia a mostrar:",
            options=list(tipos_disponibles.values()),
            default=list(tipos_disponibles.values())
        )

        # Mostrar resultado con función existente
        resultado = evolucion_regimen_tenencia(df, anio_opcion, aglomerado_opcion, seleccion_tenencia)
    
    # Item 1.4.6 Viviendas en villa de emergencia por aglomerado 
    
    elif seleccion == "Viviendas en villa de emergencia":
        resultado = calcular_viviendas_en_villa_por_aglomerado(df, anio=anio_opcion)

        if resultado.empty:
            mensaje_anio = f"el año {anio_opcion}" if anio_opcion is not None else "los datos seleccionados"
            st.warning(f"⚠️ No hay datos disponibles para {mensaje_anio}.")
        else:
             
            resultado["nombre_aglomerado"] = resultado["AGLOMERADO"].map(AGLOMERADOS_NOMBRES)

            # Título dinámico según el año
            titulo_anio = f"Año {anio_opcion}" if anio_opcion is not None else "Todos los años"
            st.markdown(f"#### Viviendas ubicadas en villa de emergencia ({titulo_anio})")

            resultado_ordenado = resultado.sort_values(by="Viviendas en villa", ascending=True).copy()

            # Crear gráfico de barras horizontales
            fig = px.bar(
                resultado_ordenado,
                x="Viviendas en villa",
                y="nombre_aglomerado",
                orientation="h",
                labels={
                    "Viviendas en villa": "Cantidad",
                    "nombre_aglomerado": "Aglomerado"
                },
                title="Cantidad de viviendas en villa de emergencia por aglomerado",
                color_discrete_sequence=["#1f77b4"],  # azul uniforme
                hover_data=["Porcentaje"]
            )

            # Ajustes de diseño
            fig.update_layout(
                height=20 * len(resultado_ordenado),
                margin=dict(l=100, r=80, t=50, b=50)
            )   
             
            st.plotly_chart(fig, use_container_width=True)
    
    # Item 1.4.7 Condición de habitabilidad
    elif seleccion == "Condición de habitabilidad":
        resultado = calcular_porcentaje_habitabilidad_larga(df, AGLOMERADOS_NOMBRES, anio_opcion)

        if resultado.empty:
            st.warning("⚠️ No hay datos disponibles.")
        else:
            st.markdown("#### Porcentaje ponderado de viviendas por condición de habitabilidad por aglomerado")

            # Quitar índice numérico para mostrar tabla sin numeración
            tabla = resultado.copy()
            tabla.index = [''] * len(tabla)
            st.dataframe(tabla)

            # Separo por condición usando el nuevo nombre de columna
            saludable = resultado[resultado["Condición de habitabilidad"] == "Saludable"]
            otras = resultado[resultado["Condición de habitabilidad"] != "Saludable"]

            # Gráfico 1: Solo "Saludable"
            st.markdown("##### Porcentaje de viviendas saludables por aglomerado")
            fig1 = px.bar(
                saludable,
                x="Aglomerado",
                y="Porcentaje",
                color_discrete_sequence=["seagreen"],
                labels={"Aglomerado": "Aglomerado", "Porcentaje": "Porcentaje (%)"},
                title="Viviendas con condición saludable",
            )
            fig1.update_layout(
                height=17 * saludable["Aglomerado"].nunique(),
                xaxis_tickangle=-45,
                xaxis=dict(tickfont=dict(size=9))
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Gráfico 2: Otras condiciones
            st.markdown("##### Porcentaje de viviendas en otras condiciones por aglomerado")
            fig2 = px.bar(
                otras,
                x="Aglomerado",
                y="Porcentaje",
                color="Condición de habitabilidad",
                labels={"Aglomerado": "Aglomerado", "Porcentaje": "Porcentaje (%)"},
                title="Viviendas con condición buena, regular e insuficiente",
            )
            fig2.update_layout(
                height=17 * otras["Aglomerado"].nunique(),
                barmode='stack',
                xaxis_tickangle=-45,
                xaxis=dict(tickfont=dict(size=9))
            )

            st.plotly_chart(fig2, use_container_width=True)

            # Botón de descarga CSV
            csv = resultado.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Descargar resultados como CSV",
                data=csv,
                file_name="habitabilidad_por_aglomerado.csv",
                mime="text/csv"
            )

else:
    st.markdown(
        '**Sin datos para mostrar**. Por favor cargue las fuentes en la pestaña:')
    st.page_link('pages/01_Carga de Datos.py',
        label='Carga de Datos', icon='📂')

#---------------------------------------------------------------------------------------------

st.markdown("---")
st.caption("📊 Fuente: Encuesta Permanente de Hogares (EPH) - INDEC")