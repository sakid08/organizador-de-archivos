# gui/dialogs.py
"""Diálogos personalizados para la interfaz"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional

class DialogoExtensiones:
    """Diálogo para editar extensiones de archivos"""
    
    def __init__(self, parent: tk.Tk, extensiones_actuales: List[str], callback_guardar):
        self.parent = parent
        self.extensiones = extensiones_actuales
        self.callback_guardar = callback_guardar
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Editar extensiones")
        self.ventana.geometry("400x300")
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        ttk.Label(self.ventana, text="Extensiones (separadas por comas):").pack(pady=10)
        
        self.texto_ext = tk.Text(self.ventana, height=5, width=40)
        self.texto_ext.pack(pady=10, padx=20)
        self.texto_ext.insert("1.0", ", ".join(self.extensiones))
        
        frame_botones = ttk.Frame(self.ventana)
        frame_botones.pack(pady=10)
        
        ttk.Button(frame_botones, text="Guardar", command=self._guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self.ventana.destroy).pack(side=tk.LEFT, padx=5)
    
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