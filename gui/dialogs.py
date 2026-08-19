# gui/dialogs.py
"""Diálogos personalizados para la interfaz"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from gui import estilos
from gui.estilos import FONT_FAMILY


def _centrar_sobre_padre(ventana, parent):
    """Centra una ventana de diálogo sobre su ventana padre"""
    ventana.update_idletasks()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    vw, vh = ventana.winfo_width(), ventana.winfo_height()
    x = px + max(0, (pw - vw) // 2)
    y = py + max(0, (ph - vh) // 3)
    ventana.geometry(f"+{x}+{y}")


def aplicar_icono(ventana):
    """Aplica el icono de la aplicación (assets/icono.ico) a una ventana.

    Importa core.config de forma diferida (no al nivel de módulo) para evitar
    un import circular: core/__init__.py importa AppController, que importa
    funciones de este módulo, así que gui.dialogs no puede depender de core
    en el momento en que se carga."""
    from core.config import RUTA_ICONO
    if RUTA_ICONO.exists():
        try:
            ventana.iconbitmap(str(RUTA_ICONO))
        except tk.TclError:
            pass


def _crear_ventana_dialogo(parent, titulo):
    ventana = tk.Toplevel(parent)
    ventana.title(titulo)
    ventana.configure(bg=estilos.COLOR_BG)
    ventana.transient(parent)
    ventana.resizable(False, False)
    aplicar_icono(ventana)
    return ventana


def _cuerpo_mensaje(ventana, icono, color_icono, titulo, mensaje):
    frame = ttk.Frame(ventana, padding="20", style="TFrame")
    frame.pack(fill="both", expand=True)

    fila = ttk.Frame(frame, style="TFrame")
    fila.pack(fill="both", expand=True)

    ttk.Label(fila, text=icono, font=(FONT_FAMILY, 22), foreground=color_icono,
              background=estilos.COLOR_BG).grid(row=0, column=0, sticky="n", padx=(0, 14))

    contenido = ttk.Frame(fila, style="TFrame")
    contenido.grid(row=0, column=1, sticky="nsew")
    fila.columnconfigure(1, weight=1)

    ttk.Label(contenido, text=titulo, style="Title.TLabel", font=(FONT_FAMILY, 12, "bold"),
              wraplength=340, justify="left").pack(anchor="w")
    ttk.Label(contenido, text=mensaje, style="Subtitle.TLabel", wraplength=340,
              justify="left").pack(anchor="w", pady=(6, 0))

    frame_botones = ttk.Frame(frame, style="TFrame")
    frame_botones.pack(fill="x", pady=(18, 0))
    return frame_botones


def _mostrar_mensaje(parent, titulo, mensaje, icono, color_icono, boton_texto="Aceptar"):
    """Muestra un diálogo modal de un solo botón (info/advertencia/error) con el
    estilo visual de la aplicación, en vez de la ventana nativa de Windows"""
    ventana = _crear_ventana_dialogo(parent, titulo)
    frame_botones = _cuerpo_mensaje(ventana, icono, color_icono, titulo, mensaje)

    ttk.Button(frame_botones, text=boton_texto, style="Primary.TButton",
               command=ventana.destroy).pack(side=tk.RIGHT)

    ventana.bind("<Return>", lambda e: ventana.destroy())
    ventana.bind("<Escape>", lambda e: ventana.destroy())
    ventana.protocol("WM_DELETE_WINDOW", ventana.destroy)

    _centrar_sobre_padre(ventana, parent)
    ventana.grab_set()
    ventana.focus_set()
    ventana.wait_window()


def mostrar_info(parent, titulo, mensaje):
    """Reemplazo temático de tkinter.messagebox.showinfo"""
    _mostrar_mensaje(parent, titulo, mensaje, estilos.ICONO_INFO, estilos.COLOR_INFO)


def mostrar_advertencia(parent, titulo, mensaje):
    """Reemplazo temático de tkinter.messagebox.showwarning"""
    _mostrar_mensaje(parent, titulo, mensaje, estilos.ICONO_ADVERTENCIA, estilos.COLOR_WARNING)


def mostrar_error(parent, titulo, mensaje):
    """Reemplazo temático de tkinter.messagebox.showerror"""
    _mostrar_mensaje(parent, titulo, mensaje, estilos.ICONO_ERROR, estilos.COLOR_ERROR)


def confirmar(parent, titulo, mensaje) -> bool:
    """Reemplazo temático de tkinter.messagebox.askyesno. Devuelve True si el
    usuario confirma la acción"""
    ventana = _crear_ventana_dialogo(parent, titulo)
    frame_botones = _cuerpo_mensaje(ventana, estilos.ICONO_PREGUNTA, estilos.COLOR_ACCENT, titulo, mensaje)

    resultado = {"valor": False}

    def _cerrar(valor):
        resultado["valor"] = valor
        ventana.destroy()

    ttk.Button(frame_botones, text="Sí, continuar", style="Primary.TButton",
               command=lambda: _cerrar(True)).pack(side=tk.RIGHT)
    ttk.Button(frame_botones, text="Cancelar", style="Secondary.TButton",
               command=lambda: _cerrar(False)).pack(side=tk.RIGHT, padx=(0, 8))

    ventana.bind("<Return>", lambda e: _cerrar(True))
    ventana.bind("<Escape>", lambda e: _cerrar(False))
    ventana.protocol("WM_DELETE_WINDOW", lambda: _cerrar(False))

    _centrar_sobre_padre(ventana, parent)
    ventana.grab_set()
    ventana.focus_set()
    ventana.wait_window()
    return resultado["valor"]


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
        self.ventana.configure(bg=estilos.COLOR_BG)
        self.ventana.transient(parent)
        aplicar_icono(self.ventana)
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

        text_border = tk.Frame(frame, bg=estilos.COLOR_BORDER)
        text_border.pack(fill="both", expand=True, pady=(0, 16))
        self.texto_ext = tk.Text(text_border, height=5, width=40, font=(FONT_FAMILY, 10),
                                  bg=estilos.COLOR_CARD, fg=estilos.COLOR_TEXT, relief="flat",
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
            mostrar_error(self.ventana, "Error", f"No se pudieron guardar las extensiones: {e}")


class DialogoNuevaCategoria:
    """Diálogo para crear una categoría totalmente personalizada"""

    def __init__(self, parent: tk.Tk, callback_crear):
        self.parent = parent
        self.callback_crear = callback_crear

        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Nueva categoría personalizada")
        self.ventana.geometry("440x400")
        self.ventana.configure(bg=estilos.COLOR_BG)
        self.ventana.transient(parent)
        aplicar_icono(self.ventana)
        self.ventana.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        frame = ttk.Frame(self.ventana, padding="20", style="TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nueva categoría", style="Title.TLabel",
                  font=(FONT_FAMILY, 14, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Define un nombre, el prefijo de carpeta y las extensiones a organizar",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 16))

        ttk.Label(frame, text="Nombre de la categoría", style="TLabel").pack(anchor="w")
        self.nombre_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.nombre_var).pack(fill="x", pady=(4, 12))

        ttk.Label(frame, text="Prefijo de carpeta (ej: Comics)", style="TLabel").pack(anchor="w")
        self.prefijo_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.prefijo_var).pack(fill="x", pady=(4, 12))

        ttk.Label(frame, text="Extensiones (separadas por comas)", style="TLabel").pack(anchor="w")
        text_border = tk.Frame(frame, bg=estilos.COLOR_BORDER)
        text_border.pack(fill="both", expand=True, pady=(4, 16))
        self.texto_ext = tk.Text(text_border, height=4, width=40, font=(FONT_FAMILY, 10),
                                  bg=estilos.COLOR_CARD, fg=estilos.COLOR_TEXT, relief="flat",
                                  borderwidth=0, padx=10, pady=8)
        self.texto_ext.pack(fill="both", expand=True, padx=1, pady=1)

        frame_botones = ttk.Frame(frame, style="TFrame")
        frame_botones.pack(anchor="e")

        ttk.Button(frame_botones, text="Cancelar", style="Secondary.TButton",
                   command=self.ventana.destroy).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(frame_botones, text="Crear categoría", style="Primary.TButton",
                   command=self._crear).pack(side=tk.LEFT)

    def _crear(self):
        """Valida y crea la nueva categoría"""
        nombre = self.nombre_var.get().strip()
        prefijo = self.prefijo_var.get().strip()
        texto = self.texto_ext.get("1.0", tk.END).strip()
        extensiones = [ext.strip() for ext in texto.split(",") if ext.strip()]

        exito, error = self.callback_crear(nombre, prefijo, extensiones)
        if exito:
            self.ventana.destroy()
        else:
            mostrar_error(self.ventana, "No se pudo crear la categoría", error)