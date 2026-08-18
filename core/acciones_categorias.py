"""Acciones del controlador relacionadas con las categorías (editar, crear y eliminar personalizadas)"""

from core.utils import normalizar_extensiones, generar_id_categoria
from core.persistencia import guardar_categorias_personalizadas


class CategoriasMixin:
    """Mezclado en AppController: gestión de categorías predeterminadas y personalizadas"""

    def editar_extensiones_categoria(self, categoria_id, nuevas_extensiones):
        """Actualiza las extensiones soportadas de una categoría"""
        extensiones = normalizar_extensiones(nuevas_extensiones)
        for categoria in self.categorias:
            if categoria["id"] == categoria_id:
                categoria["extensiones"] = extensiones
                nombre = categoria["nombre"]
                break
        else:
            return

        self.ventana.actualizar_extensiones_categoria(categoria_id, extensiones)
        self.agregar_log(f"Extensiones de '{nombre}' actualizadas: {', '.join(extensiones)}", "INFO")

        if categoria.get("personalizada"):
            self.persistir_categorias_personalizadas()

    def crear_categoria_personalizada(self, nombre, prefijo, extensiones):
        """Crea una nueva categoría personalizada definida por el usuario"""
        nombre = nombre.strip()
        prefijo = prefijo.strip()
        extensiones = normalizar_extensiones(extensiones)

        if not nombre:
            return False, "El nombre de la categoría no puede estar vacío"
        if not prefijo:
            return False, "El prefijo de carpeta no puede estar vacío"
        if not extensiones:
            return False, "Agrega al menos una extensión de archivo"

        categoria_id = generar_id_categoria(nombre, [c["id"] for c in self.categorias])
        categoria = {
            "id": categoria_id,
            "nombre": nombre,
            "prefijo": prefijo,
            "extensiones": extensiones,
            "activa": True,
            "personalizada": True,
        }
        self.categorias.append(categoria)
        self.ventana.agregar_fila_categoria(categoria)
        self.persistir_categorias_personalizadas()
        self.agregar_log(f"Categoría personalizada '{nombre}' creada", "SUCCESS")
        return True, None

    def eliminar_categoria_personalizada(self, categoria_id):
        """Elimina una categoría personalizada existente"""
        categoria = next((c for c in self.categorias if c["id"] == categoria_id), None)
        if not categoria or not categoria.get("personalizada"):
            return

        self.categorias.remove(categoria)
        self.ventana.eliminar_fila_categoria(categoria_id)
        self.persistir_categorias_personalizadas()
        self.agregar_log(f"Categoría personalizada '{categoria['nombre']}' eliminada", "INFO")

    def persistir_categorias_personalizadas(self):
        """Guarda en disco el estado actual de las categorías personalizadas"""
        personalizadas = []
        for categoria in self.categorias:
            if not categoria.get("personalizada"):
                continue
            personalizadas.append({
                "id": categoria["id"],
                "nombre": categoria["nombre"],
                "prefijo": self.ventana.categoria_prefijo(categoria["id"]) or categoria["prefijo"],
                "extensiones": categoria["extensiones"],
                "activa": self.ventana.categoria_activa(categoria["id"]),
            })
        guardar_categorias_personalizadas(personalizadas)
