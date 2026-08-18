"""Modos mutuamente excluyentes para decidir qué elementos procesar (carpetas y/o sueltos)"""

MODO_SOLO_CARPETAS = "carpetas"
MODO_SOLO_SUELTOS = "sueltos"
MODO_TODOS = "todos"

DESCRIPCION_MODOS = {
    MODO_SOLO_CARPETAS: "Solo lo que está dentro de carpetas",
    MODO_SOLO_SUELTOS: "Solo archivos sueltos en la ruta base",
    MODO_TODOS: "Todos los archivos (carpetas y sueltos)",
}


def descripcion_modo(modo: str) -> str:
    return DESCRIPCION_MODOS.get(modo, modo)
