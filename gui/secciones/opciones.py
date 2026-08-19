"""Sección de opciones: qué elementos organizar, en qué orden y cómo agruparlos"""

import tkinter as tk
from tkinter import ttk

from gui import estilos
from gui.estilos import FONT_FAMILY


class OpcionesMixin:
    """Mezclado en VentanaPrincipal: radiobuttons de modo/orden/agrupamiento"""

    def _crear_frame_opciones(self, parent):
        """Crea el frame con las opciones de organización (mostrar detalles, modo, orden, agrupamiento).

        Cada grupo de opciones (qué organizar / orden / agrupamiento) se muestra
        en su propia caja separada, lado a lado, para que no se confundan entre sí."""
        outer, inner = self._crear_card(parent, "Opciones de organización")

        ttk.Checkbutton(inner, text="Mostrar detalles del proceso",
                         variable=self.mostrar_detalle,
                         style="Card.TCheckbutton").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))

        inner.columnconfigure(0, weight=1, uniform="opciones")
        inner.columnconfigure(1, weight=1, uniform="opciones")
        inner.columnconfigure(2, weight=1, uniform="opciones")

        self._crear_grupo_opciones(
            inner, columna=0,
            titulo="¿Qué elementos organizar?",
            variable=self.modo_origen,
            opciones=[
                ("Solo lo que está dentro de carpetas\n(ignora archivos sueltos)", "carpetas"),
                ("Solo archivos sueltos en la ruta base\n(ignora carpetas)", "sueltos"),
                ("Todos los archivos\n(carpetas y sueltos)", "todos"),
            ])

        self._crear_grupo_opciones(
            inner, columna=1,
            titulo="¿En qué orden agrupar?",
            variable=self.orden_archivos,
            opciones=[
                ("Fecha (más antiguo primero)", "fecha"),
                ("Nombre (A-Z)", "nombre_az"),
                ("Nombre (Z-A)", "nombre_za"),
            ])

        self._crear_grupo_opciones(
            inner, columna=2,
            titulo="¿Cómo agrupar las carpetas?",
            variable=self.agrupamiento,
            opciones=[
                ("Por cantidad\n(según 'Archivos por carpeta')", "cantidad"),
                ("Por año (ej: Prefijo 2020 0001)", "anio"),
                ("Por mes (ej: Prefijo 2020-05 0001)", "mes"),
                ("Por letra inicial del nombre\n(ej: Prefijo A 0001)", "letra"),
            ])

        return outer

    def _crear_grupo_opciones(self, inner, columna, titulo, variable, opciones):
        """Crea una caja independiente con un título y su grupo de radiobuttons.

        Cada opción se resalta con un fondo de color cuando está seleccionada."""
        caja_borde = tk.Frame(inner, bg=estilos.COLOR_BORDER_SUBTLE)
        estilos.registrar_widget(caja_borde, bg="BORDER_SUBTLE")
        caja_borde.grid(row=2, column=columna, sticky="new", padx=(0, 12) if columna < 2 else 0)

        caja = ttk.Frame(caja_borde, style="TFrame", padding=(12, 10))
        caja.pack(fill="both", expand=True, padx=1, pady=1)

        ttk.Label(caja, text=titulo, font=(FONT_FAMILY, 10, "bold")).pack(
            anchor="w", pady=(0, 8))

        filas = []

        def _actualizar_seleccion(*_args):
            valor_actual = variable.get()
            for fila, radio, valor in filas:
                seleccionada = valor == valor_actual
                fila.configure(style="OptionSelected.TFrame" if seleccionada else "Option.TFrame")
                radio.configure(style="OptionSelected.TRadiobutton" if seleccionada else "Option.TRadiobutton")

        for texto, valor in opciones:
            fila = ttk.Frame(caja, style="Option.TFrame")
            fila.pack(fill="x", pady=(0, 4))
            radio = ttk.Radiobutton(fila, text=texto, variable=variable, value=valor,
                                     style="Option.TRadiobutton")
            radio.pack(fill="x", anchor="w")
            fila.bind("<Button-1>", lambda _e, v=valor: variable.set(v))
            filas.append((fila, radio, valor))

        variable.trace_add("write", _actualizar_seleccion)
        _actualizar_seleccion()
