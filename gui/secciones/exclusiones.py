"""Sección 'Excluir de la organización': carpetas y archivos que nunca se tocan"""

from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog

from gui import estilos
from core.persistencia import cargar_exclusiones, guardar_exclusiones


class ExclusionesMixin:
    """Mezclado en VentanaPrincipal: card con la lista de nombres excluidos"""

    def _crear_frame_exclusiones(self, parent):
        """Crea el frame con los botones de examinar y la lista de exclusiones"""
        outer, inner = self._crear_card(parent, "Excluir de la organización")
        inner.columnconfigure(0, weight=1)

        ttk.Label(inner, text=(
            "Carpetas o archivos sueltos, dentro de la ruta base, que NO se deben mover ni "
            "renombrar."
        ), style="Muted.Card.TLabel", wraplength=760, justify="left").grid(
            row=1, column=0, sticky="w", pady=(0, 10))

        fila_botones = ttk.Frame(inner, style="Card.TFrame")
        fila_botones.grid(row=2, column=0, sticky="w", pady=(0, 10))
        ttk.Button(fila_botones, text=f"{estilos.ICONO_CARPETA}  Examinar carpetas",
                   style="Secondary.TButton",
                   command=self._examinar_carpetas_excluidas).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(fila_botones, text=f"{estilos.ICONO_ARCHIVO}  Examinar archivos",
                   style="Secondary.TButton",
                   command=self._examinar_archivos_excluidos).pack(side=tk.LEFT)

        self._exclusiones_lista_frame = ttk.Frame(inner, style="Card.TFrame")
        self._exclusiones_lista_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))

        self._exclusiones_nombres = cargar_exclusiones()
        self._renderizar_exclusiones()

        return outer

    def _examinar_carpetas_excluidas(self):
        """Abre el explorador para elegir una carpeta a excluir (se puede repetir para varias)"""
        ruta = filedialog.askdirectory(title="Elegir carpeta a excluir")
        if ruta:
            self._agregar_exclusion(Path(ruta).name)

    def _examinar_archivos_excluidos(self):
        """Abre el explorador para elegir uno o varios archivos a excluir"""
        rutas = filedialog.askopenfilenames(title="Elegir archivos a excluir")
        for ruta in rutas:
            self._agregar_exclusion(Path(ruta).name)

    def _agregar_exclusion(self, nombre):
        """Agrega un nombre a la lista de exclusiones si no estaba ya"""
        if not nombre:
            return
        ya_existe = any(n.lower() == nombre.lower() for n in self._exclusiones_nombres)
        if ya_existe:
            return
        self._exclusiones_nombres.append(nombre)
        self._persistir_exclusiones()
        self._renderizar_exclusiones()

    def _eliminar_exclusion(self, nombre):
        """Quita un nombre de la lista de exclusiones"""
        self._exclusiones_nombres = [n for n in self._exclusiones_nombres if n != nombre]
        self._persistir_exclusiones()
        self._renderizar_exclusiones()

    def _renderizar_exclusiones(self):
        """Redibuja la lista de exclusiones, una fila por nombre con su botón de borrar"""
        for widget in self._exclusiones_lista_frame.winfo_children():
            widget.destroy()

        if not self._exclusiones_nombres:
            ttk.Label(self._exclusiones_lista_frame, text="Sin exclusiones",
                      style="Muted.Card.TLabel").pack(anchor="w")
            return

        for nombre in self._exclusiones_nombres:
            fila = ttk.Frame(self._exclusiones_lista_frame, style="Card.TFrame")
            fila.pack(fill="x", pady=2)
            ttk.Label(fila, text=nombre, style="Card.TLabel").pack(
                side=tk.LEFT, padx=(0, 8))
            ttk.Button(fila, text=estilos.ICONO_ELIMINAR, style="GhostCard.TButton", width=3,
                       command=lambda n=nombre: self._eliminar_exclusion(n)).pack(side=tk.LEFT)

    def exclusiones_lista(self):
        """Devuelve la lista de nombres excluidos"""
        return list(self._exclusiones_nombres)

    def _persistir_exclusiones(self):
        """Guarda en disco la lista de exclusiones actual"""
        guardar_exclusiones(self._exclusiones_nombres)
