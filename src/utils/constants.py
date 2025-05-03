from pathlib import Path


# Dirección del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

DATA_DIR = PROJECT_ROOT / "data"
DATA_SOURCE_DIR = DATA_DIR / "raw"
<<<<<<< HEAD
DATA_PROCESSED_DIR = DATA_DIR / "processed"

FILENAME_HOGARES_PROCESSED = "hogares_procesados.txt"
FILENAME_INDIVIDUOS_PROCESSED = "individuos_procesados.txt"

=======
# DATA_CLEAN_DIR = DATA_DIR / "clean"
DATA_PROCESSED_DIR = DATA_DIR / "processed"

# FILENAME_HOGARES_UNIFIED = "hogares_unificado.txt"
# FILENAME_INDIVIDUOS_UNIFIED = "individuos_unificado.txt"
FILENAME_HOGARES_PROCESSED = "hogares_procesados.txt"
FILENAME_INDIVIDUOS_PROCESSED = "individuos_procesados.txt"

# Direcciones para los archivos unificados
# HOGARES_UNIFIED_DIR = DATA_CLEAN_DIR / FILENAME_HOGARES_UNIFIED
# INDIVIDUOS_UNIFIED_DIR = DATA_CLEAN_DIR / FILENAME_INDIVIDUOS_UNIFIED

>>>>>>> 641066cb6d733f0aa361a0094036dcbb6392a1dd
# Direcciones para los archivos procesados
HOGARES_PROCESSED_DIR = DATA_PROCESSED_DIR / FILENAME_HOGARES_PROCESSED
INDIVIDUOS_PROCESSED_DIR = DATA_PROCESSED_DIR / FILENAME_INDIVIDUOS_PROCESSED

# Este diccionario contiene los nombres de los aglomerados según su número
AGLOMERADOS_NOMBRES = {
    2: "Gran La Plata",
    3: "Bahía Blanca - Cerri",
    4: "Gran Rosario",
    5: "Gran Santa Fe",
    6: "Gran Paraná",
    7: "Posadas",
    8: "Gran Resistencia",
    9: "Comodoro Rivadavia - Rada Tilly",
    10: "Gran Mendoza",
    12: "Corrientes",
    13: "Gran Córdoba",
    14: "Concordia",
    15: "Formosa",
    17: "Neuquén - Plottier",
    18: "Santiago del Estero - La Banda",
    19: "Jujuy - Palpalá",
    20: "Río Gallegos",
    22: "Gran Catamarca",
    23: "Gran Salta",
    25: "La Rioja",
    26: "Gran San Luis",
    27: "Gran San Juan",
    29: "Gran Tucumán - Tafí Viejo",
    30: "Santa Rosa - Toay",
    31: "Ushuaia - Río Grande",
    32: "Ciudad Autónoma de Buenos Aires",
    33: "Partidos del GBA",
    34: "Mar del Plata",
    36: "Río Cuarto",
    38: "San Nicolás - Villa Constitución",
    91: "Rawson - Trelew",
    93: "Viedma - Carmen de Patagones",
}

# Este diccionario contiene los nombres de los aglomerados según su número
REGIONES_NOMBRES = {
    1: "Gran Buenos Aires",
    40: "Noroeste",
    41: "Noreste",
    42: "Cuyo",
    43: "Pampeana",
    44: "Patagonia"}

# Definición de los niveles educativos
NIVELES_EDUCATIVOS = {
    1: "Primario incompleto / Ed. especial",
    2: "Primario completo",
    3: "Secundario incompleto",
    4: "Secundario completo",
    5: "Superior universitario incompleto",
    6: "Superior universitario completo",
    7: "Sin instrucción"
}
