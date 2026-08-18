"""Paleta de colores y estilos ttk compartidos por toda la interfaz.

Soporta tres temas intercambiables en caliente: "claro" (por defecto,
diseño original), "gris" (intermedio) y "oscuro". Los widgets ttk se
re-colorean solo con volver a llamar aplicar_estilos(); los widgets tk
"crudos" (Frame/Canvas/Text con bg/fg fijos) deben registrarse con
registrar_widget() para actualizarse automáticamente al cambiar de tema.
"""

import tkinter as tk
from tkinter import ttk

FONT_FAMILY = "Segoe UI"

TEMAS = {
    "claro": {
        "BG": "#f7f8fa",
        "CARD": "#ffffff",
        "BORDER": "#e5e7eb",
        "TEXT": "#1f2937",
        "TEXT_MUTED": "#6b7280",
        "ACCENT": "#b8fb2b",
        "ACCENT_HOVER": "#a3e619",
        "ACCENT_LIGHT": "#eefccb",
        "SUCCESS": "#16a34a",
        "ERROR": "#dc2626",
        "WARNING": "#d97706",
        "INFO": "#2563eb",
        "DANGER_BG": "#fef2f2",
    },
    "gris": {
        "BG": "#c9ced6",
        "CARD": "#e3e6eb",
        "BORDER": "#9aa2ad",
        "TEXT": "#1f2937",
        "TEXT_MUTED": "#454e5c",
        "ACCENT": "#b8fb2b",
        "ACCENT_HOVER": "#a3e619",
        "ACCENT_LIGHT": "#dff0a8",
        "SUCCESS": "#15803d",
        "ERROR": "#b91c1c",
        "WARNING": "#b45309",
        "INFO": "#1d4ed8",
        "DANGER_BG": "#e6c9c9",
    },
    "oscuro": {
        "BG": "#111827",
        "CARD": "#1f2937",
        "BORDER": "#374151",
        "TEXT": "#f3f4f6",
        "TEXT_MUTED": "#9ca3af",
        "ACCENT": "#b8fb2b",
        "ACCENT_HOVER": "#c6ff4d",
        "ACCENT_LIGHT": "#2e3b12",
        "SUCCESS": "#22c55e",
        "ERROR": "#f87171",
        "WARNING": "#fbbf24",
        "INFO": "#60a5fa",
        "DANGER_BG": "#3f1d1d",
    },
}

NOMBRES_TEMAS = {"claro": "Claro", "gris": "Gris", "oscuro": "Oscuro"}

TEMA_ACTUAL = "gris"


def _fijar_colores(nombre: str) -> None:
    """Actualiza las variables COLOR_* del módulo según el tema indicado"""
    paleta = TEMAS[nombre]
    globals().update({f"COLOR_{clave}": valor for clave, valor in paleta.items()})


_fijar_colores(TEMA_ACTUAL)

# Widgets tk "crudos" registrados para re-colorear en cambios de tema:
# lista de (widget, {opcion_tk: "NOMBRE_COLOR"})
_widgets_registrados = []
# Tags de Text registrados: lista de (text_widget, tag, "NOMBRE_COLOR")
_tags_registrados = []


def registrar_widget(widget, **opciones):
    """Registra un widget tk crudo para que sus opciones de color (bg, fg,
    insertbackground, etc.) se actualicen automáticamente al cambiar de tema.

    Uso: registrar_widget(frame, bg="BORDER")
    """
    _widgets_registrados.append((widget, opciones))
    _aplicar_a_widget(widget, opciones)


def registrar_tag(text_widget, tag, color):
    """Registra un tag de un widget Text para recolorear su 'foreground'"""
    _tags_registrados.append((text_widget, tag, color))
    _aplicar_a_tag(text_widget, tag, color)


def _color(nombre_color):
    return globals()[f"COLOR_{nombre_color}"]


def _aplicar_a_widget(widget, opciones):
    try:
        widget.configure(**{opcion: _color(color) for opcion, color in opciones.items()})
    except tk.TclError:
        pass


def _aplicar_a_tag(text_widget, tag, color):
    try:
        text_widget.tag_config(tag, foreground=_color(color))
    except tk.TclError:
        pass


def cambiar_tema(root: tk.Tk, nombre: str) -> None:
    """Cambia el tema activo, re-aplica los estilos ttk y actualiza los
    widgets tk crudos registrados"""
    global TEMA_ACTUAL
    if nombre not in TEMAS:
        return
    TEMA_ACTUAL = nombre
    _fijar_colores(nombre)

    aplicar_estilos(root)

    widgets_vivos = []
    for widget, opciones in _widgets_registrados:
        if widget.winfo_exists():
            _aplicar_a_widget(widget, opciones)
            widgets_vivos.append((widget, opciones))
    _widgets_registrados[:] = widgets_vivos

    tags_vivos = []
    for text_widget, tag, color in _tags_registrados:
        if text_widget.winfo_exists():
            _aplicar_a_tag(text_widget, tag, color)
            tags_vivos.append((text_widget, tag, color))
    _tags_registrados[:] = tags_vivos


def aplicar_estilos(root: tk.Tk) -> ttk.Style:
    """Configura los widgets ttk de la ventana según el tema activo"""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 10))

    style.configure("TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")

    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 10))
    style.configure("Card.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 10))
    style.configure("Muted.Card.TLabel", background=COLOR_CARD,
                     foreground=COLOR_TEXT_MUTED, font=(FONT_FAMILY, 9))
    style.configure("Title.TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 18, "bold"))
    style.configure("Subtitle.TLabel", background=COLOR_BG, foreground=COLOR_TEXT_MUTED,
                     font=(FONT_FAMILY, 10))
    style.configure("SectionTitle.Card.TLabel", background=COLOR_CARD,
                     foreground=COLOR_TEXT, font=(FONT_FAMILY, 11, "bold"))

    # Entradas
    style.configure("TEntry", fieldbackground=COLOR_CARD, background=COLOR_CARD,
                     foreground=COLOR_TEXT, bordercolor=COLOR_BORDER,
                     lightcolor=COLOR_BORDER, darkcolor=COLOR_BORDER,
                     relief="solid", borderwidth=1, padding=6)
    style.map("TEntry", bordercolor=[("focus", COLOR_ACCENT)])

    style.configure("TSpinbox", fieldbackground=COLOR_CARD, background=COLOR_CARD,
                     foreground=COLOR_TEXT, bordercolor=COLOR_BORDER,
                     arrowsize=14, relief="solid", borderwidth=1, padding=4)
    style.map("TSpinbox", bordercolor=[("focus", COLOR_ACCENT)])

    style.configure("TCombobox", fieldbackground=COLOR_CARD, background=COLOR_CARD,
                     foreground=COLOR_TEXT, bordercolor=COLOR_BORDER,
                     arrowsize=14, relief="solid", padding=6)
    style.map("TCombobox", fieldbackground=[("readonly", COLOR_CARD)],
               bordercolor=[("focus", COLOR_ACCENT)])

    root.option_add("*TCombobox*Listbox.background", COLOR_CARD)
    root.option_add("*TCombobox*Listbox.foreground", COLOR_TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", COLOR_ACCENT_LIGHT)
    root.option_add("*TCombobox*Listbox.selectForeground", COLOR_TEXT)

    # Botones
    style.configure("TButton", font=(FONT_FAMILY, 10), padding=(14, 8),
                     relief="flat", borderwidth=0)

    style.configure("Primary.TButton", background=COLOR_ACCENT, foreground="#1a2e05",
                     font=(FONT_FAMILY, 10, "bold"), padding=(16, 9))
    style.map("Primary.TButton",
               background=[("disabled", "#dcf7a6"), ("active", COLOR_ACCENT_HOVER)],
               foreground=[("disabled", "#6b7d4a")])

    style.configure("Secondary.TButton", background=COLOR_CARD, foreground=COLOR_TEXT,
                     bordercolor=COLOR_BORDER, relief="solid", borderwidth=1,
                     padding=(14, 8))
    style.map("Secondary.TButton",
               background=[("disabled", COLOR_BG), ("active", COLOR_ACCENT_LIGHT)],
               foreground=[("disabled", COLOR_TEXT_MUTED)])

    style.configure("Danger.TButton", background=COLOR_CARD, foreground=COLOR_ERROR,
                     bordercolor="#fecaca", relief="solid", borderwidth=1,
                     padding=(14, 8))
    style.map("Danger.TButton",
               background=[("disabled", COLOR_BG), ("active", COLOR_DANGER_BG)],
               foreground=[("disabled", "#f3a6a6")])

    style.configure("Ghost.TButton", background=COLOR_BG, foreground=COLOR_TEXT_MUTED,
                     relief="flat", padding=(10, 6))
    style.map("Ghost.TButton", background=[("active", COLOR_ACCENT_LIGHT)],
               foreground=[("active", COLOR_ACCENT)])

    style.configure("GhostCard.TButton", background=COLOR_CARD, foreground=COLOR_TEXT_MUTED,
                     relief="flat", padding=(10, 5), font=(FONT_FAMILY, 9))
    style.map("GhostCard.TButton", background=[("active", COLOR_ACCENT_LIGHT)],
               foreground=[("active", COLOR_ACCENT)])

    style.configure("Small.TButton", padding=(10, 5), font=(FONT_FAMILY, 9))

    # Checkbutton
    style.configure("TCheckbutton", background=COLOR_BG, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 10))
    style.map("TCheckbutton", background=[("active", COLOR_BG)])

    style.configure("Card.TCheckbutton", background=COLOR_CARD, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 10, "bold"))
    style.map("Card.TCheckbutton", background=[("active", COLOR_CARD)])

    # Radiobutton
    style.configure("TRadiobutton", background=COLOR_BG, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 10))
    style.map("TRadiobutton", background=[("active", COLOR_BG)])

    # Progressbar
    style.configure("Modern.Horizontal.TProgressbar", troughcolor=COLOR_ACCENT_LIGHT,
                     background=COLOR_ACCENT, bordercolor=COLOR_ACCENT_LIGHT,
                     lightcolor=COLOR_ACCENT, darkcolor=COLOR_ACCENT, thickness=8)

    # Separator
    style.configure("TSeparator", background=COLOR_BORDER)

    return style
