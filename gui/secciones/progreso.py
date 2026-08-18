"""Sección 'Progreso': barra indeterminada y etiqueta de estado del proceso"""

from tkinter import ttk


class ProgresoMixin:
    """Mezclado en VentanaPrincipal: card de progreso"""

    def _crear_frame_progreso(self, parent):
        """Crea el frame de progreso"""
        outer, inner = self._crear_card(parent, "Progreso")
        inner.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(inner, mode='indeterminate',
                                             style="Modern.Horizontal.TProgressbar")
        self.progress_bar.grid(row=1, column=0, sticky=("W", "E"), pady=(0, 8))

        self.progress_label = ttk.Label(inner, text="Esperando inicio...",
                                         style="Muted.Card.TLabel")
        self.progress_label.grid(row=2, column=0, sticky="W")

        return outer

    def set_progreso(self, estado):
        """Actualiza el estado del progreso"""
        if estado == "iniciando":
            self.progress_bar.start(10)
        elif estado == "detenido":
            self.progress_bar.stop()

    def set_progress_label(self, mensaje):
        """Actualiza la etiqueta de progreso"""
        self.progress_label.config(text=mensaje)
