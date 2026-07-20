from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import os

def obtener_archivos_carpeta(carpeta: Path, extensiones: List[str]) -> Tuple[List[Path], List[Path]]:
    """
    Separa archivos de una carpeta en imágenes y otros archivos
    
    Args:
        carpeta: Path de la carpeta a procesar
        extensiones: Lista de extensiones de imágenes
    
    Returns:
        (lista_imagenes, lista_otros)
    """
    imagenes = []
    otros = []
    
    for archivo in carpeta.iterdir():
        if archivo.is_file():
            if archivo.suffix.lower() in extensiones:
                imagenes.append(archivo)
            else:
                otros.append(archivo)
    
    return imagenes, otros

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

def validar_ruta(ruta: str) -> bool:
    """Valida si una ruta existe y es accesible"""
    try:
        return Path(ruta).exists()
    except Exception:
        return False