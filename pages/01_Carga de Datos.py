import streamlit as st
from src.utils.helpers import data_date_range

# Guarda el rango de fechas en la session state
if "date_range" not in st.session_state:
    st.session_state.date_range = data_date_range()
elif st.session_state.date_range is None:
    st.session_state.date_range = data_date_range()


st.write(
    f"El sistema contiene información desde el {st.session_state.date_range[0]} hasta el {st.session_state.date_range[1]}.")

uploaded_files = st.file_uploader(
    "Seleccione un archivo CSV", accept_multiple_files=True
)

st.write("Si desea actualizar los datos, haga clic en el botón de abajo.")
st.button("Actualizar datos")
