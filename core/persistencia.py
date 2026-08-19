"""Persistencia en disco de las categorías personalizadas creadas por el usuario"""

import json
from pathlib import Path
from typing import List, Dict

RUTA_DATOS = Path(__file__).resolve().parent.parent / "data"
RUTA_CATEGORIAS_USUARIO = RUTA_DATOS / "categorias_personalizadas.json"
RUTA_EXCLUSIONES = RUTA_DATOS / "exclusiones.json"


def cargar_categorias_personalizadas() -> List[Dict]:
    """Carga las categorías personalizadas guardadas por el usuario, si existen"""
    if not RUTA_CATEGORIAS_USUARIO.exists():
        return []
    try:
        with open(RUTA_CATEGORIAS_USUARIO, "r", encoding="utf-8") as f:
            categorias = json.load(f)
        for categoria in categorias:
            categoria["personalizada"] = True
        return categorias
    except (json.JSONDecodeError, OSError):
        return []


def guardar_categorias_personalizadas(categorias: List[Dict]) -> None:
    """Guarda la lista de categorías personalizadas en disco"""
    RUTA_DATOS.mkdir(parents=True, exist_ok=True)
    with open(RUTA_CATEGORIAS_USUARIO, "w", encoding="utf-8") as f:
        json.dump(categorias, f, ensure_ascii=False, indent=2)


def cargar_exclusiones() -> List[str]:
    """Carga la lista de nombres de carpetas/archivos excluidos de la organización"""
    if not RUTA_EXCLUSIONES.exists():
        return []
    try:
        with open(RUTA_EXCLUSIONES, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def guardar_exclusiones(nombres: List[str]) -> None:
    """Guarda la lista de nombres excluidos en disco"""
    RUTA_DATOS.mkdir(parents=True, exist_ok=True)
    with open(RUTA_EXCLUSIONES, "w", encoding="utf-8") as f:
        json.dump(nombres, f, ensure_ascii=False, indent=2)
