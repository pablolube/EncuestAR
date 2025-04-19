from pathlib import Path

# Dirección del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

DATA_DIR = PROJECT_ROOT / "data"
DATA_SOURCE_DIR = DATA_DIR / "raw"
DATA_CLEAN_DIR = DATA_DIR / "clean"
DATA_PROCESSED_DIR = DATA_DIR / "processed"

FILENAME_HOGARES_UNIFIED = "hogares_unificado.txt"
FILENAME_INDIVIDUOS_UNIFIED = "individuos_unificado.txt"
FILENAME_HOGARES_PROCESSED = "hogares_procesados.txt"
FILENAME_INDIVIDUOS_PROCESSED = "individuos_procesados.txt"

# Direcciones para los archivos unificados
HOGARES_UNIFIED_DIR = DATA_CLEAN_DIR / FILENAME_HOGARES_UNIFIED
INDIVIDUOS_UNIFIED_DIR = DATA_CLEAN_DIR / FILENAME_INDIVIDUOS_UNIFIED

# Direcciones para los archivos procesados
HOGARES_PROCESSED_DIR = DATA_PROCESSED_DIR / FILENAME_HOGARES_PROCESSED
INDIVIDUOS_PROCESSED_DIR = DATA_PROCESSED_DIR / FILENAME_INDIVIDUOS_PROCESSED
