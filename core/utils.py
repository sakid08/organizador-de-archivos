from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import os
import re
import unicodedata

def clasificar_archivos_carpeta(carpeta: Path, mapa_extensiones: Dict[str, str]) -> Tuple[Dict[str, List[Path]], List[Path]]:
    """
    Separa los archivos de una carpeta según la categoría a la que pertenece su extensión

    Args:
        carpeta: Path de la carpeta a procesar
        mapa_extensiones: Diccionario {extension: id_categoria} de categorías activas

    Returns:
        (dict {id_categoria: [archivos]}, lista_sin_categoria)
    """
    por_categoria: Dict[str, List[Path]] = {}
    sin_categoria = []

    for archivo in carpeta.iterdir():
        if not archivo.is_file():
            continue

        id_categoria = mapa_extensiones.get(archivo.suffix.lower())
        if id_categoria:
            por_categoria.setdefault(id_categoria, []).append(archivo)
        else:
            sin_categoria.append(archivo)

    return por_categoria, sin_categoria

def crear_nombre_unico(destino: Path) -> Path:
    """
    Crea un nombre único para evitar duplicados
    
    Args:
        destino: Path base del archivo
    
    Returns:
        Path con nombre único
    """
    if not destino.exists():
        return destino
    
    contador = 1
    stem = destino.stem
    suffix = destino.suffix
    directorio = destino.parent
    
    while True:
        nuevo_nombre = f"{stem}_{contador}{suffix}"
        nueva_ruta = directorio / nuevo_nombre
        if not nueva_ruta.exists():
            return nueva_ruta
        contador += 1

def obtener_timestamp() -> str:
    """Obtiene timestamp actual para logs"""
    return datetime.now().strftime("%H:%M:%S")

def normalizar_extensiones(extensiones: List[str]) -> List[str]:
    """Normaliza extensiones asegurando que tengan punto"""
    return [ext if ext.startswith(".") else f".{ext}" for ext in extensiones]

def carpeta_pertenece_a_prefijo(nombre_carpeta: str, prefijo: str) -> bool:
    """
    Indica si una carpeta fue generada por el organizador con el prefijo dado,
    es decir si su nombre es exactamente "prefijo numero", o "prefijo <grupo> numero"
    cuando se usó un método de agrupamiento (año "2020", mes "2020-05" o letra "A"/"#").

    Se usa en vez de un simple startswith() porque dos prefijos distintos pueden
    ser subcadena uno del otro (p. ej. "Capturas de pantalla" es substring de
    "Capturas de pantallaaa"), lo que con startswith() hacia que carpetas de un
    prefijo se confundieran con las de otro y se saltearan por error.
    """
    grupo = r"( \d{4}(-\d{2})?| [A-Z#])?"
    patron = r"^" + re.escape(prefijo) + grupo + r" \d+$"
    return re.match(patron, nombre_carpeta) is not None


def generar_id_categoria(nombre: str, ids_existentes: List[str]) -> str:
    """Genera un id único (slug) a partir del nombre de una categoría"""
    normalizado = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "_", normalizado.lower()).strip("_") or "categoria"

    id_candidato = slug
    contador = 1
    while id_candidato in ids_existentes:
        contador += 1
        id_candidato = f"{slug}_{contador}"

    return id_candidato


def validar_ruta(ruta: str) -> bool:
    """Valida si una ruta existe y es accesible"""
    try:
        return Path(ruta).exists()
    except Exception:
        return False