"""Métodos de agrupamiento: cómo se reparten los archivos ya ordenados entre carpetas numeradas"""

import datetime
from pathlib import Path
from typing import Optional

AGRUPAR_CANTIDAD = "cantidad"
AGRUPAR_ANIO = "anio"
AGRUPAR_MES = "mes"
AGRUPAR_LETRA = "letra"

DESCRIPCION_AGRUPAMIENTO = {
    AGRUPAR_CANTIDAD: "Por cantidad (según 'Archivos por carpeta')",
    AGRUPAR_ANIO: "Por año",
    AGRUPAR_MES: "Por mes",
    AGRUPAR_LETRA: "Por letra inicial del nombre",
}


def descripcion_agrupamiento(agrupamiento: str) -> str:
    return DESCRIPCION_AGRUPAMIENTO.get(agrupamiento, agrupamiento)


def clave_anio(mtime: float) -> str:
    return datetime.datetime.fromtimestamp(mtime).strftime("%Y")


def clave_mes(mtime: float) -> str:
    return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m")


def clave_letra(nombre_archivo: str) -> str:
    primer_caracter = nombre_archivo[:1].upper()
    return primer_caracter if primer_caracter.isalpha() else "#"


def clave_grupo(agrupamiento: str, ruta_archivo: Path, mtime: float) -> Optional[str]:
    """Devuelve la clave de agrupamiento de un archivo, o None si es agrupamiento por cantidad"""
    if agrupamiento == AGRUPAR_ANIO:
        return clave_anio(mtime)
    if agrupamiento == AGRUPAR_MES:
        return clave_mes(mtime)
    if agrupamiento == AGRUPAR_LETRA:
        return clave_letra(ruta_archivo.name)
    return None
