# Proyecto Grupo 18 // Encuest.AR 🧮

Versión 0.0.0 - Mayo 2025

Aplicación para la exploración de datos de la Encuesta Permanente de Hogares (EPH), desarrollada como trabajo integrador en la UNLP.

Integrantes: 

Dario Micheli, Delfina González, Esteeven Andres Gallegos Calle, Noemí Amalia Gudiño, Pablo Nicolás Luberriaga

---

## 📊 Descripción y Estructura del proyecto

Este proyecto permite:
- Procesar archivos csv, con un formato unificado y especifico.
- Realizar consultas y visualizar resultados.

Organización (estructura):

```plaintext
code/
├── data/
│   ├── raw/                      # Archivos de datos originales en formato .txt.
│   └── processed/                # Archivos de datos procesados en formato .txt.
├── notebooks/                    # Carpeta para almacenar notebooks Jupyter para análisis exploratorio.
│   ├── hogares-individuos.ipynb  # Análisis y exploración de datos relacionados con hogares e individuos.                
│   ├── individuos.ipynb          # Análisis y exploración de datos relacionados con individuos.
│   └── hogares.ipynb             # Análisis y exploración de datos relacionados con hogares.
├── pages/
│   ├── 01_Carga de Datos.py      # Interfaz para cargar y procesar los datos.
│   ├── 02_Busqueda por Tema.py   # Página para realizar búsquedas sobre los datos procesados.
│   └── 03_Visualizacion.py       # Página para visualizar los resultados.
├── src/
│   ├── consultas/                # Funciones para realizar consultas sobre los datos.
│   │   └── consultas.py          # Contiene las funciones para realizar consultas sobre los datos de la EPH.
│   ├── utils/                    # Funciones auxiliares para tareas comunes.
│   │   ├── constants.py          # Contiene las constantes necesarias para el proyecto, datos de uso común.
│   │   ├── helpers.py            # Funciones auxiliares reutilizables para tareas comunes.
│   │   └── streamlit.py          # Funciones para Streamlit.
│   └── procesamientos/           # Archivos con scripts para procesar y transformar los datos.
│       ├── individuos.py         # Funciones específicas para procesar datos de individuos.
│       └── hogares.py            # Funciones específicas para procesar datos de hogares.
├── .gitignore                    # Archivos y carpetas que deben ser ignorados por Git.
├── Inicio.py                     # Interfaz de inicio para app streamlit
├── LICENSE                       # Licencia de uso del código fuente del proyecto.
├── README.md                     # Descripción general del proyecto, cómo instalarlo y ejecutarlo.
└── requirements.txt              # Lista de dependencias del proyecto (librerías de Python necesarias).
```
---

## 🚀 Cómo abrir y ejecutar el proyecto

Sigue estos pasos para ejecutar el proyecto en tu máquina local:

### 1. **Clonar el repositorio**
Primero, clona este repositorio a tu máquina local usando Git. Abre tu terminal y ejecuta:

```bash
git clone https://gitlab.catedras.linti.unlp.edu.ar/python-2025/proyectos/grupo18/code.git 
```

Ingresá tus credenciales de GitLab

### 2. **Instalar las dependencias**
Accede al directorio del proyecto: 
```bash
cd code
```

Crear entorno virtual:
```bash
python3 -m venv venv
```

Activar entorno virtual:
Windows: 
```bash
source venv\Scripts\activate
pip install -r requirements.txt
```
Linux/Mac: 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. **Ejecutar la aplicación STREAMLIT**
```bash
streamlit run Inicio.py
```

Para cargar uno o más archivos que requieran procesarse, navegar por el menú de la web hasta la sección "Carga de Datos".

Luego, actualizar.

### 4. **Ejecutar notebooks**

Cargar los archivos que se quieran analizar dentro de la carpeta: Data/raw

Ejecutar los notebooks:     
```bash
jupyter notebook
```

Esto abrirá una interfaz web en tu navegador, donde podrás ver todos los notebooks en la carpeta notebooks/.


