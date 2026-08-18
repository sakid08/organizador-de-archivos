"""Sección 'Configuración general': ruta base, dígitos y archivos por carpeta"""

import tkinter as tk
from tkinter import ttk, filedialog


class ConfiguracionMixin:
    """Mezclado en VentanaPrincipal: card de configuración general"""

    def _crear_frame_configuracion(self, parent):
        """Crea el frame de configuración general"""
        outer, inner = self._crear_card(parent, "Configuración general")
        inner.columnconfigure(1, weight=1)

        # Ruta base (obligatoria, sin valor por defecto)
        ttk.Label(inner, text="Ruta base *", style="Card.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=8)
        ruta_entry = ttk.Entry(inner, textvariable=self.ruta_base)
        ruta_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(12, 8), pady=8)
        ttk.Button(inner, text="Examinar", style="Secondary.TButton",
                   command=self._seleccionar_ruta).grid(row=1, column=2, pady=8)
        ttk.Label(inner, text="Obligatorio: debes seleccionar o escribir una ruta antes de organizar",
                  style="Muted.Card.TLabel").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, padx=(0, 0), pady=(0, 4))

        # Dígitos
        ttk.Label(inner, text="Dígitos (0001)", style="Card.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=8)
        ttk.Spinbox(inner, from_=1, to=6, textvariable=self.digitos, width=10).grid(
            row=3, column=1, sticky=tk.W, padx=(12, 8), pady=8)

        # Archivos por carpeta
        ttk.Label(inner, text="Archivos por carpeta", style="Card.TLabel").grid(
            row=4, column=0, sticky=tk.W, pady=8)
        ttk.Spinbox(inner, from_=100, to=2000, increment=100,
                    textvariable=self.archivos_por_carpeta, width=10).grid(
            row=4, column=1, sticky=tk.W, padx=(12, 8), pady=8)

        return outer

    def _seleccionar_ruta(self):
        """Abre diálogo para seleccionar ruta"""
        ruta = filedialog.askdirectory(title="Seleccionar carpeta base")
        if ruta:
            self.ruta_base.set(ruta)
            if self.app_controller:
                self.app_controller.agregar_log(f"Ruta base cambiada a: {ruta}", "INFO")
