"""Criterios de orden para distribuir archivos entre carpetas numeradas"""

from pathlib import Path
from typing import List, Tuple

ORDEN_FECHA = "fecha"
ORDEN_NOMBRE_AZ = "nombre_az"
ORDEN_NOMBRE_ZA = "nombre_za"

DESCRIPCION_ORDEN = {
    ORDEN_FECHA: "Fecha (más antiguo primero)",
    ORDEN_NOMBRE_AZ: "Nombre (A-Z)",
    ORDEN_NOMBRE_ZA: "Nombre (Z-A)",
}


def descripcion_orden(orden: str) -> str:
    return DESCRIPCION_ORDEN.get(orden, orden)


def ordenar_archivos(archivos: List[Tuple[Path, float]], orden: str) -> None:
    """Ordena in-place la lista de archivos (ruta, mtime) según el criterio indicado"""
    if orden == ORDEN_NOMBRE_AZ:
        archivos.sort(key=lambda x: x[0].name.lower())
    elif orden == ORDEN_NOMBRE_ZA:
        archivos.sort(key=lambda x: x[0].name.lower(), reverse=True)
    else:
        archivos.sort(key=lambda x: x[1])
