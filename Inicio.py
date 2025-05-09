import streamlit as st

# Cargar Font Awesome desde CDN
st.markdown("""
<head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 >Bienvenidos 👋</h1>', unsafe_allow_html=True)
st.markdown('<h1 >📊 Encuest.AR</h1>', unsafe_allow_html=True)
st.markdown('<h3 > Proyecto colectivo: Trabajo integrador UNLP </h3>', unsafe_allow_html=True)

# Línea gris clara
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

# Sección: ¿En qué consiste?
st.markdown('<h3><i class="fa-arrow-down" style="color:#E67E22;"></i> ¿En qué consiste?</h3>', unsafe_allow_html=True)
st.markdown("""<p
            style="text-align: justify;"><strong>Encuest.AR</strong> es una aplicación diseñada para cargar, visualizar y obtener información resumida y jerarquizada. Utilizamos sets de datos brindados por la  <a href="https://www.indec.gob.ar/ftp/cuadros/sociedad/Gacetilla_EPHContinua.pdf" target="_blank"><strong>EPH</strong></a> (Encuesta Permanente de Hogares), los cuales son facilitados de forma pública por el Estado Nacional.
</p>
""" , unsafe_allow_html=True)

# Link archivo descargable
st.markdown("""<div style="text-align: justify;">
    <i class="fas fa-arrow-right" style="color:#CA6F1E; margin-right: 8px;"></i>
    <strong>Podés acceder a los archivos descargables en:</strong>
    <a href="https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos" target="_blank">
        <strong>Descargar Set de Datos</strong>
    </a>
</div>
""", unsafe_allow_html=True)

# Línea gris clara
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)

# Sección: ¿Qué es la EPH?
st.markdown('<h3><i class="fas fa-users" style="color:#CA6F1E;"></i> ¿Qué es la EPH?</h3>', unsafe_allow_html=True)
st.markdown("""<p
            style="text-align: justify;">La <strong>EPH</strong> es un programa nacional de producción permanente de indicadores sociales con actualizaciones <strong>trimestrales</strong>  cuyo objetivo es conocer las características socioeconómicas de la población.
            
Es realizada en forma conjunta por el Instituto Nacional de Estadística y Censos (<strong>INDEC</strong>) y las Direcciones Provinciales de Estadísticas (<strong>DPE</strong>).

Los datos recolectados son fundamentales para el diseño y monitoreo de políticas públicas, análisis de pobreza, empleo, ingresos, y otros indicadores clave para el desarrollo social y económico del país.    
</p>
""", unsafe_allow_html=True)

st.video("https://www.youtube.com/watch?v=cQXHWMnaY2A")

# Línea divisoria cálida
st.markdown('<hr style="border: 1px solid #dddddd;">', unsafe_allow_html=True)


