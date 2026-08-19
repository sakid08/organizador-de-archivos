"""Sección de botones de acción: organizar, renombrar, agrupar todo y detener"""

import tkinter as tk
from tkinter import ttk

from gui import estilos


class BotonesMixin:
    """Mezclado en VentanaPrincipal: botones de acción y sus filas asociadas"""

    def _crear_botones_accion(self, parent):
        """Crea los botones de acción"""
        buttons_frame = ttk.Frame(parent, style="TFrame")
        buttons_frame.columnconfigure(0, weight=1)

        fila_botones = ttk.Frame(buttons_frame, style="TFrame")
        fila_botones.grid(row=0, column=0, sticky=tk.W)

        self.btn_organizar = ttk.Button(
            fila_botones, text=f"{estilos.ICONO_ORGANIZAR}  Organizar archivos",
            style="Primary.TButton")
        self.btn_organizar.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_renombrar = ttk.Button(
            fila_botones, text=f"{estilos.ICONO_EDITAR}  Solo renombrar carpetas",
            style="Secondary.TButton")
        self.btn_renombrar.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_detener = ttk.Button(
            fila_botones, text=f"{estilos.ICONO_DETENER}  Detener",
            state=tk.DISABLED, style="Danger.TButton")
        self.btn_detener.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(fila_botones, text=f"{estilos.ICONO_ELIMINAR}  Limpiar log",
                   style="Ghost.TButton", command=self._limpiar_log).pack(side=tk.LEFT, padx=(0, 10))

        self.btn_quitar_marcadores = ttk.Button(
            fila_botones, text=f"{estilos.ICONO_ELIMINAR}  Quitar archivos ocultos",
            style="Ghost.TButton")
        self.btn_quitar_marcadores.pack(side=tk.LEFT)

        fila_renombrado = ttk.Frame(buttons_frame, style="TFrame")
        fila_renombrado.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Label(fila_renombrado, text="Categoría a renombrar:", style="TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.combo_renombrado = ttk.Combobox(fila_renombrado, textvariable=self.categoria_renombrado,
                                              state="readonly", width=28)
        self.combo_renombrado.pack(side=tk.LEFT)

        # Fila para agrupar TODOS los archivos sin distinguir tipo/extensión
        fila_general = ttk.Frame(buttons_frame, style="TFrame")
        fila_general.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Label(fila_general, text="Prefijo para agrupar todo:", style="TLabel").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Entry(fila_general, textvariable=self.prefijo_general, width=20).pack(side=tk.LEFT, padx=(0, 10))
        self.btn_agrupar_todo = ttk.Button(
            fila_general, text=f"{estilos.ICONO_CARPETA}  Agrupar todos los archivos (sin distinguir tipo)",
            style="Secondary.TButton")
        self.btn_agrupar_todo.pack(side=tk.LEFT)

        return buttons_frame
