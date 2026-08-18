"""Sección 'Log de ejecución': área de texto con colores por tipo de mensaje"""

import tkinter as tk
from tkinter import scrolledtext

from gui.estilos import COLOR_BORDER, COLOR_CARD, COLOR_TEXT, COLOR_INFO, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING


class LogMixin:
    """Mezclado en VentanaPrincipal: card del log de ejecución"""

    def _crear_area_log(self, parent):
        """Crea el área de log"""
        outer, inner = self._crear_card(parent, "Log de ejecución")
        inner.columnconfigure(0, weight=1)

        log_border = tk.Frame(inner, bg=COLOR_BORDER)
        log_border.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.log_text = scrolledtext.ScrolledText(
            log_border, height=14, width=80, font=("Consolas", 9),
            bg=COLOR_CARD, fg=COLOR_TEXT, insertbackground=COLOR_TEXT,
            relief="flat", borderwidth=0, padx=10, pady=8)
        self.log_text.pack(fill="both", expand=True, padx=1, pady=1)

        # Configurar colores para el log
        self.log_text.tag_config("INFO", foreground=COLOR_INFO)
        self.log_text.tag_config("SUCCESS", foreground=COLOR_SUCCESS)
        self.log_text.tag_config("ERROR", foreground=COLOR_ERROR)
        self.log_text.tag_config("WARNING", foreground=COLOR_WARNING)

        return outer

    def _limpiar_log(self):
        """Limpia el área de log"""
        self.log_text.delete("1.0", tk.END)
        if self.app_controller:
            self.app_controller.agregar_log("Log limpiado", "INFO")

    def agregar_log(self, mensaje, tipo="INFO"):
        """Agrega un mensaje al log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        texto_log = f"[{timestamp}] {mensaje}\n"

        self.log_text.insert(tk.END, texto_log, tipo)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
