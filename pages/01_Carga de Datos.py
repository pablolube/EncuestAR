import streamlit as st
from src.utils.helpers import data_date_range, actualizar
from src.utils.constants import DATA_SOURCE_DIR
from pathlib import Path

# Guarda el rango de fechas en la session state
if "date_range" not in st.session_state:
    st.session_state.date_range = data_date_range()
elif st.session_state.date_range is None:
    st.session_state.date_range = data_date_range()

st.header("Carga de Datos")
st.subheader("Información del Dataset")
st.write(
    f"El sistema contiene información desde el {st.session_state.date_range[0]} hasta el {st.session_state.date_range[1]}.")

st.subheader("Carga de Archivos")
# Complemento de carga de archivos
uploaded_files = st.file_uploader(
    "Seleccione uno o más archivos", accept_multiple_files=True, type=["txt"]
)

# Carga de archivos en el directorio de datos
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_path = Path(DATA_SOURCE_DIR) / file_name

        if file_path.exists():
            st.warning(f"⚠️ El archivo '{file_name}' ya existe. No se guardó.")
            continue

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ {file_name} guardado en {file_path}")

st.subheader("Actualización de Datos")
st.write("Si desea actualizar los datos, haga clic en el botón de abajo.")
st.button("Actualizar", key="b_actualizar", on_click=actualizar, icon="🔄")
