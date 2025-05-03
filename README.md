# Proyecto Grupo 18 // Encuest.AR 🧮

Aplicación para la exploración de datos de la Encuesta Permanente de Hogares (EPH), desarrollada como trabajo integrador en la UNLP.

Integrantes: 

Dario Micheli, Delfina González, Esteeven Andres Gallegos Calle, Noemí Amalia Gudiño, Pablo Nicolás Luberriaga

---

## 📊 Descripción y Estructura del proyecto

Este proyecto permite:
- Procesar archivos csv, con un formato unificado y especifico.
- Realizar consultas y visualizar resultados.

Organización (estructura):

code/
├── data/
│ ├── raw/ # Archivos de datos originales en formato .txt.
│ └── processed/ # Archivos de datos procesados en formato .txt.
├── notebooks/ # Notebooks Jupyter para análisis exploratorio.
│ ├── individuos.ipynb # Análisis de datos individuales.
│ └── hogares.ipynb # Análisis de datos de hogares.
├── pages/
│ ├── 01_Carga de Datos.py # Carga y procesamiento de archivos.
│ ├── busqueda.py # Página para búsquedas.
│ └── visualizacion.py # Página de visualización.
├── src/
│ ├── consultas/
│ │ └── consultas.py # Funciones para consultas.
│ ├── utils/
│ │ ├── constants.py # Constantes del proyecto.
│ │ └── helpers.py # Funciones auxiliares.
│ └── procesamientos/
│ ├── individuos.py # Procesamiento de datos individuales.
│ └── hogares.py # Procesamiento de datos de hogares.
├── .gitignore # Exclusiones de Git.
├── LICENSE # Licencia del proyecto.
├── README.md # Instrucciones generales.
└── requirements.txt # Dependencias del proyecto.
---

## 🚀 Cómo abrir y ejecutar el proyecto

Sigue estos pasos para ejecutar el proyecto en tu máquina local:

### 1. **Clonar el repositorio**
Primero, clona este repositorio a tu máquina local usando Git. Abre tu terminal y ejecuta:

bash git clone https://gitlab.catedras.linti.unlp.edu.ar/python-2025/proyectos/grupo18/code.git 

### 2. **Instalar las dependencias**
Accede al directorio del proyecto: cd code

Crear entorno virtual:
bash python3 -m venv venv

Activar entorno virtual:
Windows: bash .\venv\Scripts\activate
Linux/Mac: bash source venv/bin/activate

pip install -r requirements.txt

## 3. **Ejecutar la aplicación STREAMLIT**
streamlit run Inicio.py

Para cargar uno o más archivos que requieran procesarse, navegar por el menú de la web hasta la sección "Carga de Datos".

Luego, actualizar.

### 4. **Ejecutar notebooks **

Ejecutar los notebooks:     
bash jupyter notebook

Esto abrirá una interfaz web en tu navegador, donde podrás ver todos los notebooks en la carpeta notebooks/.


