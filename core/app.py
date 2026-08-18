# core/app.py
"""Controlador principal de la aplicación"""

import copy
from tkinter import messagebox

from core.config import CATEGORIAS_DEFAULT
from core.utils import validar_ruta
from core.persistencia import cargar_categorias_personalizadas
from core.acciones_organizar import OrganizarMixin
from core.acciones_categorias import CategoriasMixin


class AppController(OrganizarMixin, CategoriasMixin):
    """Controlador de la aplicación"""

    def __init__(self, ventana):
        self.ventana = ventana
        self.proceso_activo = False
        self.categorias = copy.deepcopy(CATEGORIAS_DEFAULT) + cargar_categorias_personalizadas()

        # Inicializar la interfaz con las categorías disponibles
        self.ventana.inicializar_categorias(self.categorias)

    def agregar_log(self, mensaje, tipo="INFO"):
        """Agrega mensaje al log a través de la ventana"""
        self.ventana.agregar_log(mensaje, tipo)

    def _debe_detener(self) -> bool:
        """Verifica si el proceso debe detenerse"""
        return not self.proceso_activo

    def _actualizar_progreso(self, mensaje):
        """Actualiza mensaje de progreso"""
        self.ventana.set_progress_label(mensaje)

    def _finalizar_proceso(self):
        """Finaliza el proceso y limpia el estado"""
        self.proceso_activo = False
        self.ventana.habilitar_botones(True)
        self.ventana.set_progreso("detenido")
        self.ventana.set_progress_label("Proceso finalizado")
        self.ventana.set_status("Listo")

    def _iniciar_proceso(self):
        """Prepara la interfaz para iniciar un proceso"""
        self.proceso_activo = True
        self.ventana.habilitar_botones(False)
        self.ventana.set_progreso("iniciando")
        self.ventana.set_status("Procesando...")

    def _validar_ruta_base(self) -> bool:
        """Verifica que el usuario haya introducido una ruta base (no puede quedar vacía ni por defecto)"""
        ruta_texto = self.ventana.ruta_base.get().strip()
        if not ruta_texto:
            messagebox.showwarning("Ruta requerida", "Debes indicar una ruta base antes de continuar")
            return False
        if not validar_ruta(ruta_texto):
            messagebox.showwarning("Ruta inválida", f"La ruta indicada no existe o no es accesible:\n{ruta_texto}")
            return False
        return True

    def _categorias_activas(self):
        """Construye la lista de categorías activas con sus prefijos actuales"""
        activas = []
        for categoria in self.categorias:
            if not self.ventana.categoria_activa(categoria["id"]):
                continue
            activas.append({
                "id": categoria["id"],
                "nombre": categoria["nombre"],
                "prefijo": self.ventana.categoria_prefijo(categoria["id"]),
                "extensiones": categoria["extensiones"],
            })
        return activas

    def detener_proceso(self):
        """Detiene el proceso en ejecución"""
        self.proceso_activo = False
        self.agregar_log("⚠ Deteniendo proceso...", "WARNING")
