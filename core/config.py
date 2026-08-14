# Categorías de archivos soportadas. Cada una puede activarse/desactivarse
# de forma independiente y todas se procesan en la misma pasada.
# Los archivos que no encajen en ninguna categoría activa van a CARPETA_OTROS.
CATEGORIAS_DEFAULT = [
    {
        "id": "imagenes",
        "nombre": "Imágenes",
        "prefijo": "Imagenes",
        "extensiones": [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".svg"],
        "activa": True,
        "personalizada": False,
    },
    {
        "id": "videos",
        "nombre": "Videos",
        "prefijo": "Películas",
        "extensiones": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        "activa": True,
        "personalizada": False,
    },
    {
        "id": "documentos",
        "nombre": "Documentos",
        "prefijo": "Documentos",
        "extensiones": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".csv"],
        "activa": True,
        "personalizada": False,
    },
    {
        "id": "musica",
        "nombre": "Música",
        "prefijo": "Música",
        "extensiones": [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"],
        "activa": True,
        "personalizada": False,
    },
]

CARPETA_OTROS = "otros_formatos"

# Configuración por defecto
CONFIG_DEFAULT = {
    "digitos": 4,
    "archivos_por_carpeta": 600,
    "mostrar_detalle": True
}

# Colores para el log
LOG_COLORS = {
    "INFO": "blue",
    "SUCCESS": "green",
    "ERROR": "red",
    "WARNING": "orange"
}

# Tamaños y dimensiones de la ventana
VENTANA_TITULO = "Organizador de Imágenes y Archivos"
VENTANA_DIMENSIONES = "960x780"