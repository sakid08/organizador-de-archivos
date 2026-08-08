# gui/dialogs.py
"""Diálogos personalizados para la interfaz"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional

from gui.main_window import COLOR_BG, COLOR_CARD, COLOR_BORDER, COLOR_TEXT, FONT_FAMILY

class DialogoExtensiones:
    """Diálogo para editar extensiones de archivos"""

    def __init__(self, parent: tk.Tk, extensiones_actuales: List[str], callback_guardar,
                 titulo: str = "Editar extensiones"):
        self.parent = parent
        self.extensiones = extensiones_actuales
        self.callback_guardar = callback_guardar

        self.ventana = tk.Toplevel(parent)
        self.ventana.title(titulo)
        self.ventana.geometry("420x320")
        self.ventana.configure(bg=COLOR_BG)
        self.ventana.transient(parent)
        self.ventana.grab_set()

        self._titulo = titulo
        self._crear_interfaz()

    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        frame = ttk.Frame(self.ventana, padding="20", style="TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=self._titulo, style="Title.TLabel",
                  font=(FONT_FAMILY, 14, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Separadas por comas", style="Subtitle.TLabel").pack(
            anchor="w", pady=(2, 16))

        text_border = tk.Frame(frame, bg=COLOR_BORDER)
        text_border.pack(fill="both", expand=True, pady=(0, 16))
        self.texto_ext = tk.Text(text_border, height=5, width=40, font=(FONT_FAMILY, 10),
                                  bg=COLOR_CARD, fg=COLOR_TEXT, relief="flat",
                                  borderwidth=0, padx=10, pady=8)
        self.texto_ext.pack(fill="both", expand=True, padx=1, pady=1)
        self.texto_ext.insert("1.0", ", ".join(self.extensiones))

        frame_botones = ttk.Frame(frame, style="TFrame")
        frame_botones.pack(anchor="e")

        ttk.Button(frame_botones, text="Cancelar", style="Secondary.TButton",
                   command=self.ventana.destroy).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(frame_botones, text="Guardar", style="Primary.TButton",
                   command=self._guardar).pack(side=tk.LEFT)
    
    def _guardar(self):
        """Guarda las extensiones editadas"""
        try:
            texto = self.texto_ext.get("1.0", tk.END).strip()
            nuevas_ext = [ext.strip().lower() for ext in texto.split(",") if ext.strip()]
            # Normalizar extensiones
            nuevas_ext = [ext if ext.startswith(".") else f".{ext}" for ext in nuevas_ext]
            
            self.callback_guardar(nuevas_ext)
            self.ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las extensiones: {e}")