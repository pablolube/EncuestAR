import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
from src.utils.constants import AGLOMERADOS_NOMBRES
from src.utils.streamlit import cargar_df_hogares  
import plotly.express as px
import altair as alt




st.set_page_config(page_title='Características de la Vivienda', layout="wide")
st.title('🏠 Características de la Vivienda en Argentina')
st.markdown("Análisis basado en datos de la EPH")
st.markdown('---')
#------------------------------------------------------------------------------------------------------
#  Funciones auxiliares 
#-------------------------------------------------------------------------------------------------------

# Items 1.4.1 y 1.4.2
#def contar_viviendas_por_anio(df, anio):
#    df_anio = df[df["ANO4"] == anio]
#    if df_anio.empty:
#        return None
#    df_unicos = df_anio.drop_duplicates(subset="CODUSU")
#    total_viviendas = df_unicos["PONDERA"].sum()
#    return total_viviendas
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

     Returns:
         float: Cantidad total de viviendas ponderadas (suma de 'PONDERA' para hogares únicos).
     """
    if anio is not None:
        df = df[df["ANO4"] == anio]
    # Eliminamos duplicados por CODUSU y nos quedamos con la primera fila como representante
    df_unicos = df.drop_duplicates(subset="CODUSU", keep="first")
    # Sumamos los ponderadores de esas viviendas únicas
    total_viviendas_ponderadas = df_unicos["PONDERA"].sum()
    return total_viviendas_ponderadas




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

    Returns:
        pandas.Series or None: Serie con las proporciones de cada tipo de hogar. Devuelve `None` 
        si no hay datos disponibles tras el filtrado.
    """
    if anio is not None:
       df = df[df["ANO4"] == anio]
    if df.empty:
        return None
    return df["TIPO_HOGAR"].value_counts(normalize=True).sort_values(ascending=False)

# Item 1.4.3 
def material_piso_por_aglomerado_detallado(df_hogares, anio=None):
    """
    Determina el material predominante del piso por aglomerado, para un año específico o considerando todos los años.

    Para cada aglomerado, se agrupan las viviendas únicas (por CODUSU) y se calcula cuál es el material de piso
    con mayor cantidad ponderada de viviendas, y qué porcentaje representa respecto al total de viviendas del aglomerado.

    Args:
        df_hogares (pd.DataFrame): DataFrame con los datos de hogares provenientes de la EPH.
        anio (int or None): Año a filtrar. Si es None, se incluyen todos los años disponibles.

    Returns:
        pd.DataFrame or None: DataFrame con columnas:
            - "Aglomerado": nombre del aglomerado
            - "Material": material predominante del piso
            - "Cantidad de viviendas con el material predominante": cantidad ponderada de viviendas
            - "Porcentaje": porcentaje sobre el total de viviendas del aglomerado (con dos decimales)
        Devuelve None si no hay datos válidos disponibles.
    """
    if anio is not None:
        df_hogares = df_hogares[df_hogares["ANO4"] == anio]

    if df_hogares.empty or "IV3" not in df_hogares.columns or "AGLOMERADO" not in df_hogares.columns or "PONDERA" not in df_hogares.columns:
        return None

    # Eliminar duplicados por vivienda
    df_hogares = df_hogares.drop_duplicates(subset=["CODUSU"])

    # Mapear materiales del piso
    material_map = {
        1: "Mosaico/Baldosa/Madera/Cerámica/Alfombra",
        2: "Cemento/Ladrillo fijo",
        3: "Ladrillo suelto/Tierra"
    }
    df_hogares = df_hogares.copy()
    df_hogares["Material"] = df_hogares["IV3"].map(material_map)

    # Total de viviendas ponderadas por aglomerado
    total_por_aglomerado = df_hogares.groupby("AGLOMERADO")["PONDERA"].sum().rename("Total_viviendas")

    # Cantidad por material por aglomerado
    conteo = df_hogares.groupby(["AGLOMERADO", "Material"])["PONDERA"].sum().reset_index(name="Cantidad")

    # Obtener el material predominante por aglomerado
    idx_max = conteo.groupby("AGLOMERADO")["Cantidad"].idxmax()
    resultado = conteo.loc[idx_max].set_index("AGLOMERADO")

    # Agregar nombres legibles de aglomerados
    resultado["Aglomerado"] = resultado.index.map(AGLOMERADOS_NOMBRES)

    # Agregar total de viviendas y calcular porcentaje por aglomerado
    resultado["Total_viviendas"] = resultado.index.map(total_por_aglomerado)
    resultado["Porcentaje"] = (resultado["Cantidad"] / resultado["Total_viviendas"] * 100).round(2)

    # Renombrar columna de cantidad
    resultado = resultado.rename(columns={"Cantidad": "Cantidad de viviendas con el material predominante"})

    return resultado[["Aglomerado", "Material", "Cantidad de viviendas con el material predominante", "Porcentaje"]]


#------------------------------------------------------------------------------------------------------

# Item 1.4.4
def calcular_proporcion_bano_por_aglomerado(df_hogar, AGLOMERADOS_NOMBRES, anio=None):
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
#-----------------------------------------------------------------------------------------------------
# Item 1.4.5
def evolucion_regimen_tenencia(df, anio, aglomerado_seleccionado, tipos_tenencia):
    """
    Muestra la evolución trimestral del régimen de tenencia de viviendas para un aglomerado específico
    en un año determinado, utilizando datos ponderados por hogar.

    Args:
        df (pd.DataFrame): DataFrame de hogares de la EPH.
        anio (int): Año seleccionado por el usuario.
        aglomerado_seleccionado (int): Código del aglomerado a analizar.
        tipos_tenencia (list[str] or None): Lista de tipos de tenencia a incluir. Si es None, se usan todos.
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

    st.dataframe(resumen.rename(columns={
        'PONDERA': 'Cantidad ponderada de viviendas',
        'Porcentaje': 'Porcentaje (%)'
    }))

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




#------------------------------------------------------------------------------------------------------

# --- Cargar datos si no están en session_state ---
if 'df_hogares' not in st.session_state:
    st.session_state.df_hogares = cargar_df_hogares()

# --- Verificar datos cargados ---
if 'df_hogares' in st.session_state and not st.session_state.df_hogares.empty:
    df = st.session_state.df_hogares.copy()

    min_anio = int(df["ANO4"].min())
    max_anio = int(df["ANO4"].max())

    st.markdown("### Ingrese un año para el análisis")
    #anio_opcion = st.number_input("Año", min_value=min_anio, max_value=max_anio, step=1)
    
    secciones = [
        "1.4.1 Cantidad total de viviendas",
        "1.4.2 Tipo de vivienda (gráfico de torta)",
        "1.4.3 Material del piso por aglomerado",
        "1.4.4 Baño dentro del hogar",
        "1.4.5 Evolución del régimen de tenencia",
        "1.4.6 Viviendas en villa de emergencia",
        "1.4.7 Condición de habitabilidad"
    ]
    
    seleccion = st.sidebar.radio("Seleccionar sección:", secciones)

    permitir_todos_los_anios = seleccion != "1.4.5 Evolución del régimen de tenencia"

    # Construir lista de opciones de año
    opciones_anio = sorted(df["ANO4"].unique())
    if permitir_todos_los_anios:
       opciones_anio = ["Todos los años"] + opciones_anio

   # Mostrar selector
    anio_opcion_raw = st.selectbox("Año", options=opciones_anio)

   # Convertir a int o None
    anio_opcion = None if anio_opcion_raw == "Todos los años" else int(anio_opcion_raw)

    # --- 1.4.1 Cantidad total de viviendas ---
    if seleccion == "1.4.1 Cantidad total de viviendas":
        total = contar_viviendas_por_anio(df, anio_opcion)
        if total is None:
            st.warning(f"⚠️ No hay datos disponibles para el año {anio_opcion}.")
        else:
            total_formateado = f"{total:,.0f}".replace(",", ".")
            st.metric("Cantidad total de viviendas (ponderadas)", total_formateado)

    # --- 1.4.2 Tipo de vivienda ---
    elif seleccion == "1.4.2 Tipo de vivienda (gráfico de torta)":
         dist = tipo_vivienda_proporcion(df, anio_opcion)
         if dist is None or dist.empty:
             mensaje_anio = f"el año {anio_opcion}" if anio_opcion is not None else "los datos seleccionados"
             st.warning(f"⚠️ No hay datos disponibles para {mensaje_anio}.")
         else:
              def autopct_con_coma(pct):
                  return f"{pct:.1f}".replace('.', ',') + '%'

              titulo_anio = f"Año {anio_opcion}" if anio_opcion is not None else "Todos los años"

              fig, ax = plt.subplots()
              ax.pie(dist.values, labels=dist.index, autopct=autopct_con_coma)
              ax.set_title(f"Distribución por tipo de vivienda ({titulo_anio})")
              st.pyplot(fig)

    
    # --- 1.4.3 Material del piso por aglomerado ---
    elif seleccion == "1.4.3 Material del piso por aglomerado":
        if df is not None and not df.empty:
            resultado = material_piso_por_aglomerado_detallado(df, anio_opcion)

            if resultado is None or resultado.empty:
                mensaje_anio = f"el año {anio_opcion}" if anio_opcion is not None else "los datos seleccionados"
                st.warning(f"⚠️ No hay datos disponibles para {mensaje_anio}.")
            else:
                # Título con año o "Todos los años"
                titulo_anio = f"Año {anio_opcion}" if anio_opcion is not None else "Todos los años"
                st.markdown(f"#### Material predominante del piso por aglomerado ({titulo_anio})")

                 # Ordenar por porcentaje descendente
                resultado_ordenado = resultado.sort_values(by="Porcentaje", ascending=False).copy()

                # Formatear texto del porcentaje con coma
                #resultado_ordenado["Texto porcentaje"] = resultado_ordenado["Porcentaje"].apply(
                #    lambda x: f"{x:.2f}".replace(".", ",") + "%"
                #)

                # Mostrar tabla
                st.dataframe(resultado_ordenado)

                # Gráfico con porcentaje
                fig = px.bar(
                    resultado_ordenado,
                    x="Porcentaje",
                    y="Aglomerado",
                    orientation='h',
                    color="Material",
                    title="Material predominante por aglomerado",
                    labels={
                        "Material": "Material predominante",
                        "Aglomerado": "Aglomerado",
                        "Porcentaje": "Porcentaje"
                     
                    }
                    #text="Texto porcentaje"
                )

                fig.update_traces(textposition='outside')

                fig.update_layout(
                    height=20 * len(resultado_ordenado),
                    xaxis_tickformat=".2f",
                    xaxis_ticksuffix=" %",
                )

                st.plotly_chart(fig, use_container_width=True)

            # Botón para descargar CSV
           # csv = resultado_ordenado.to_csv(index=False).encode("utf-8")
           # st.download_button(
           #            label="⬇️ Descargar datos como CSV",
           #            data=csv,
           #            file_name=f"material_piso_aglomerado_{anio_opcion}.csv",
           #            mime="text/csv"
           # )
            
    # Item 1.4.4 Baño dentro del hogar ---
    
    elif seleccion == "1.4.4 Baño dentro del hogar":
          resultado = calcular_proporcion_bano_por_aglomerado(df, AGLOMERADOS_NOMBRES, anio_opcion)

          if resultado.empty:
             mensaje_anio = f"el año {anio_opcion}" if anio_opcion is not None else "los datos seleccionados"
             st.warning(f"⚠️ No hay datos disponibles para {mensaje_anio}.")
          else:
             # Título con año o "Todos los años"
             titulo_anio = f"Año {anio_opcion}" if anio_opcion is not None else "Todos los años"
             st.markdown(f"#### Proporción de viviendas con baño dentro del hogar ({titulo_anio})")

             # Gráfico de barras horizontales
             fig = px.bar(
                 resultado.sort_values(by="proporcion", ascending=False),
                 x="proporcion",
                 y="nombre_aglomerado",
                 orientation="h",
                 labels={
                     "proporcion": "Proporción",
                     "nombre_aglomerado": "Aglomerado"
                 },
                 title="Proporción de viviendas con baño dentro del hogar por aglomerado"
            )

             fig.update_layout(
                height=20 * len(resultado),
                xaxis_tickformat=".2f",
              #  xaxis_ticksuffix=" %",
             )

             st.plotly_chart(fig, use_container_width=True)

            
    # Item 1.4.5 Evolución del régimen de tenencia ---
    elif seleccion == "1.4.5 Evolución del régimen de tenencia":
        aglomerado_opcion = st.selectbox("Seleccione un aglomerado", options=sorted(df['AGLOMERADO'].unique()))

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

        seleccion_tenencia = st.multiselect(
            "Seleccione el/los tipos de tenencia a mostrar:", list(tipos_disponibles.values()), default=list(tipos_disponibles.values())
        )

        resultado = evolucion_regimen_tenencia(df, anio_opcion, aglomerado_opcion, seleccion_tenencia)




else:
   st.warning("⚠️ No hay datos cargados. Por favor, cargue los datos desde la pestaña correspondiente.")
   st.markdown("[Ir a Carga de Datos](pages/01_Carga_de_Datos.py)")

