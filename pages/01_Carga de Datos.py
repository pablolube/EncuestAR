import streamlit as st
from src.utils.streamlit import actualizar, cargar_archivos, eliminar_archivos

# Cargar Font Awesome desde CDN
st.markdown("""
<head>
    <link rel="style=sheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
""", unsafe_allow_html=True)

# Guarda el rango de fechas en la session state
if "date_range" not in st.session_state:
    st.session_state.date_range = actualizar()



# Sección principal
st.markdown('<h2 style"color:#D35400;">🗂️ Carga de Datos</h2>',
            unsafe_allow_html=True)

# Separador
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

# Información del Dataset
st.markdown('<h4><i class="fas fa-calendar-alt" style="color:#E67E22;"></i> Información del Dataset</h4>',
            unsafe_allow_html=True)

if  st.session_state.date_range is None:
    st.warning(
        "No se encontraron archivos procesados. Intenta cargarlos primero, y luego actualizar", icon="⚠️")
else:
    fecha_inicio = st.session_state.date_range[0]
    fecha_fin = st.session_state.date_range[1]
    st.markdown(
        f"El sistema contiene información desde el **{fecha_inicio[1]}/{fecha_inicio[0]}** hasta el **{fecha_fin[1]}/{fecha_fin[0]}** (trimestre/año).")

# Separador
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

# Carga de Archivos
st.markdown('<h4><i class="fas fa-upload" style="color:#E67E22;"></i> Carga de Archivos</h4>',
            unsafe_allow_html=True)

# Complemento de carga de archivos
uploaded_files = st.file_uploader(
    "Seleccione uno o más archivos", accept_multiple_files=True, type=["txt"])

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
    st.button("🗑️ Eliminar Todos los Archivos Cargados", key="b_eliminar", on_click=eliminar_archivos)
with col2:
    st.button("🔄 Actualizar", key="b_actualizar", on_click=actualizar)

# Mensaje de eliminación
if "mensaje_eliminacion" in st.session_state:
    tipo, texto = st.session_state["mensaje_eliminacion"]
    getattr(st, tipo)(texto)
    del st.session_state["mensaje_eliminacion"]


# Separador
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

# Actualización de Datos
st.markdown('<h4><i class="fas fa-sync-alt" style="color:#CA6F1E;"></i> Actualización de Datos</h4>',
            unsafe_allow_html=True)
st.write("Haga clic en el botón para sincronizar y procesar los archivos cargados.")

# Mensaje de actualización
if "mensaje_actualizacion" in st.session_state:
    tipo, texto = st.session_state["mensaje_actualizacion"]
    getattr(st, tipo)(texto)
    del st.session_state["mensaje_actualizacion"]