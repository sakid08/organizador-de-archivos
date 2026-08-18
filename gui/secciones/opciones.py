"""Sección de opciones: qué elementos organizar, en qué orden y cómo agruparlos"""

import tkinter as tk
from tkinter import ttk

from gui.estilos import FONT_FAMILY


class OpcionesMixin:
    """Mezclado en VentanaPrincipal: radiobuttons de modo/orden/agrupamiento"""

    def _crear_frame_opciones(self, parent):
        """Crea el frame con las opciones de organización (mostrar detalles, modo, orden, agrupamiento)"""
        opciones_frame = ttk.Frame(parent, style="TFrame")

        ttk.Checkbutton(opciones_frame, text="Mostrar detalles del proceso",
                         variable=self.mostrar_detalle).pack(anchor="w")

        ttk.Label(opciones_frame, text="¿Qué elementos organizar?",
                  style="TLabel", font=(FONT_FAMILY, 10, "bold")).pack(anchor="w", pady=(12, 4))
        ttk.Radiobutton(opciones_frame, text="Solo lo que está dentro de carpetas (ignora archivos sueltos)",
                         variable=self.modo_origen, value="carpetas").pack(anchor="w")
        ttk.Radiobutton(opciones_frame, text="Solo archivos sueltos en la ruta base (ignora carpetas)",
                         variable=self.modo_origen, value="sueltos").pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(opciones_frame, text="Todos los archivos (carpetas y sueltos)",
                         variable=self.modo_origen, value="todos").pack(anchor="w", pady=(4, 0))

        ttk.Label(opciones_frame, text="¿En qué orden agrupar los archivos?",
                  style="TLabel", font=(FONT_FAMILY, 10, "bold")).pack(anchor="w", pady=(12, 4))
        ttk.Radiobutton(opciones_frame, text="Fecha (más antiguo primero)",
                         variable=self.orden_archivos, value="fecha").pack(anchor="w")
        ttk.Radiobutton(opciones_frame, text="Nombre (A-Z)",
                         variable=self.orden_archivos, value="nombre_az").pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(opciones_frame, text="Nombre (Z-A)",
                         variable=self.orden_archivos, value="nombre_za").pack(anchor="w", pady=(4, 0))

        ttk.Label(opciones_frame, text="¿Cómo agrupar las carpetas?",
                  style="TLabel", font=(FONT_FAMILY, 10, "bold")).pack(anchor="w", pady=(12, 4))
        ttk.Radiobutton(opciones_frame, text="Por cantidad (según 'Archivos por carpeta')",
                         variable=self.agrupamiento, value="cantidad").pack(anchor="w")
        ttk.Radiobutton(opciones_frame, text="Por año (ej: Prefijo 2020 0001)",
                         variable=self.agrupamiento, value="anio").pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(opciones_frame, text="Por mes (ej: Prefijo 2020-05 0001)",
                         variable=self.agrupamiento, value="mes").pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(opciones_frame, text="Por letra inicial del nombre (ej: Prefijo A 0001)",
                         variable=self.agrupamiento, value="letra").pack(anchor="w", pady=(4, 0))

        return opciones_frame
