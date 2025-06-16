import streamlit as st
from src.utils.streamlit import actualizar, cargar_archivos, eliminar_archivos, cargar_df,cargar_df_hogares
from src.utils.constants import DATA_SOURCE_DIR
import datetime

# Cargar Font Awesome desde CDN
st.markdown("""
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
""", unsafe_allow_html=True)

# Sección principal
st.markdown('<h2 style"color:#D35400;">🗂️ Carga de Datos</h2>',
            unsafe_allow_html=True)

# Separador
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

# Complemento de carga de archivos--------------------------------------------------------------------

# Carga de Archivos
st.markdown('<h4><i class="fas fa-upload" style="color:#E67E22;"></i>  Carga y Actualización de Datos </h4>',
            unsafe_allow_html=True)

# Link a tutoriales
st.markdown("""
    <h7 style="font-weight: bold; font-size: 18px;">
        <i class="fas fa-question-circle" style="color:#E67E22; font-size: 20px;"></i>  
    ¿Necesitas ayuda? </h7>
        <p style="font-size: 16px;">¡Mirá el paso-a-paso y video tutorial! En la sección <a href=#tutoriales style="text-decoration: none; font-weight: bold; color:#E67E22;">
        <i class="fas fa-link" style="color:#E67E22;"></i> ¿Cómo cargar datos en la App? </a>.</p>
""", unsafe_allow_html=True)


uploaded_files = st.file_uploader(
    "**Seccioná el o los archivos desde tu dispositivo:**", accept_multiple_files=True)

st.button("📤 Cargar Archivos", key="b_cargar_archivos",
          on_click=cargar_archivos, args=(uploaded_files,))

# Mensajes de carga de archivos
if "mensajes_carga" in st.session_state:
    for tipo, texto in st.session_state["mensajes_carga"]:
        getattr(st, tipo)(texto)
    # Limpiar después de mostrar
    del st.session_state["mensajes_carga"]

# Botón para eliminar archivos cargados
col1, col2 = st.columns(2)
with col1:
    st.button("🗑️ Eliminar Todos los Archivos Cargados",
              key="b_eliminar", on_click=eliminar_archivos)
with col2:
    st.button("🔄 Actualizar", key="b_actualizar", on_click=actualizar)

# Mensaje de eliminación
if "mensaje_eliminacion" in st.session_state:
    tipo, texto = st.session_state["mensaje_eliminacion"]
    getattr(st, tipo)(texto)
    del st.session_state["mensaje_eliminacion"]

# Mensaje de actualización
if "mensaje_actualizacion" in st.session_state:
    tipo, texto = st.session_state["mensaje_actualizacion"]
    getattr(st, tipo)(texto)
    del st.session_state["mensaje_actualizacion"]

# Enlace al área de información del Dataset
st.markdown("""
    <h6 style="font-weight: bold; font-size: 18px;">
    </h6>
        <p style="font-size: 16px;"> Podés verificar si se actualizó correctamente la información en: <a href=#5541d523 style="text-decoration: none; font-weight: bold; color:#E67E22;">
        <i class="fas fa-link" style="color:#E67E22;"></i> Ver Información del Dataset </a> y qué archivos cargaste en: <a href=#5541d523 style="text-decoration: none; font-weight: bold; color:#E67E22;">
        <i class="fas fa-link" style="color:#E67E22;"></i> Ver Archivos en sistema </a> </p>
""", unsafe_allow_html=True)


# Separador
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

# Información del Dataset------------------------------------------------------------------------------

st.markdown('<h4><i class="fas fa-calendar-alt" style="color:#E67E22;"></i> Información del Dataset</h4>',
            unsafe_allow_html=True)

if 'date_range' in st.session_state:
    if st.session_state.date_range is None:
        st.warning(
            "No se encontraron archivos procesados. Intenta cargarlos primero, y luego actualizar", icon="⚠️")
    else:
        fecha_inicio = st.session_state.date_range[0]
        fecha_fin = st.session_state.date_range[1]
        if fecha_inicio is not None and fecha_fin is not None:
            st.markdown(
                f"El sistema contiene información desde el **{fecha_inicio[1]}/{fecha_inicio[0]}** hasta el **{fecha_fin[1]}/{fecha_fin[0]}** (trimestre/año).")
            st.session_state.df_ind = cargar_df()
            st.session_state.df_hogares = cargar_df_hogares()
        else:
            st.warning(
                "No fue posible determinar las fechas porque los archivos cargados no contienen información temporal válida", icon="⚠️")

# Separador
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

# Sección: Archivos cargados en el sistema-----------------------------------------------------------

# Sección archivos en sesión
st.markdown('<h4><i class="fas fa-file-alt" style="color:#E67E22;"></i> Archivos en sistema</h4>',
            unsafe_allow_html=True)

archivos_hogar = []
archivos_indiv = []

# Listar los archivos en el directorio, no verificamos si esta vacio, porque siempre tiene al menos .gitkeep
for archivo in DATA_SOURCE_DIR.iterdir():
    if archivo.name.endswith(".txt"):
        nombre = archivo.name.lower()
        if "hogar" in nombre:
            archivos_hogar.append(archivo)
        elif "individual" in nombre:
            archivos_indiv.append(archivo)

# Función para imprimir archivos clasificados


def imprimir_archivos(titulo, archivos):
    if archivos:
        st.markdown(f"#### {titulo}")
        for archivo in archivos:
            fecha = datetime.datetime.fromtimestamp(
                archivo.stat().st_mtime).strftime("%d/%m/%Y %H:%M:%S")
            st.markdown(
                f"- 📄 **{archivo.name}** - Fecha y Hora de carga: {fecha}")
    else:
        st.markdown(f"#### {titulo}")
        st.markdown(f"**No hay archivos de {titulo.lower()} cargados.**")


# Mostrar los archivos cargados
imprimir_archivos("🏠 Hogares", archivos_hogar)
imprimir_archivos("👤 Individuos", archivos_indiv)

# Separador opcional
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)


# Sección: Tutoriales-------------------------------------------------------------------------------

st.markdown('<h4 ><i class="fas fa-book"; style="color:#E67E22;"></i> Tutoriales</h4>',
            unsafe_allow_html=True)
st.markdown("""
            <div style="text-align: justify;"><strong>¿Cómo cargar datos en la App?</strong>  Paso a paso y Video explicativo.
</div>
""", unsafe_allow_html=True)

# Imprimo pasos para el usuario
st.markdown(
    " 1) Seleccioná el o los archivos de tu ordenador (encontrarás el link de descarga de archivos EPH en la **sección de Inicio**)")
st.markdown(
    "2) Cargá los archivos, desde el botón **Cargar Archivos**. Si ya tenés archivos cargados y necesitas cambiarlos, podés eliminarlos desde el botón **Eliminar Todos los Archivos Cargados** y repetí el paso 1).")

st.markdown(
    "3) Actualizá el sistema, desde el botón **Actualizar**. Esto permitirá que los archivos cargados se procesen.")


# Espacio
st.markdown("&nbsp;", unsafe_allow_html=True)

# Video Tutorial 1
st.video("https://www.youtube.com/watch?v=bILbA6-mzWw")


# Línea divisoria cálida
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)
