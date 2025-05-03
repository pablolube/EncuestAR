import streamlit as st
from src.utils.helpers import data_date_range, actualizar, cargar_archivos

# Guarda el rango de fechas en la session state
if "date_range" not in st.session_state:
    st.session_state.date_range = data_date_range()
elif st.session_state.date_range is None:
    st.session_state.date_range = data_date_range()


st.header("Carga de Datos")

# Información del Dataset
st.subheader("Información del Dataset")
st.write(
    f"El sistema contiene información desde el {st.session_state.date_range[0]} hasta el {st.session_state.date_range[1]}.")

# Carga de Archivos
st.subheader("Carga de Archivos")
# Complemento de carga de archivos
uploaded_files = st.file_uploader(
    "Seleccione uno o más archivos", accept_multiple_files=True, type=["txt"]
)
st.button("Cargar Archivos", key="b_cargar_archivos",
          on_click=cargar_archivos, args=(uploaded_files,), icon="📤")

# Actualización de Datos
st.subheader("Actualización de Datos")
st.write("Si desea actualizar los datos, haga clic en el botón de abajo.")
st.button("Actualizar", key="b_actualizar", on_click=actualizar, icon="🔄")
