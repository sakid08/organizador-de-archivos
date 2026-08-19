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

# Fuente de iconos del sistema (Windows 10/11): da un set de glifos consistente
# en vez de mezclar emoji de distintas familias visuales. Se usa incrustando
# el carácter directamente en el texto de labels/botones con la fuente normal:
# Windows resuelve el glifo por reemplazo de fuente automáticamente.
ICONO_ORGANIZAR = chr(0xE768)  # Play
ICONO_EDITAR = chr(0xE70F)  # Edit (lápiz)
ICONO_DETENER = chr(0xE71A)  # Stop
ICONO_ELIMINAR = chr(0xE74D)  # Delete (papelera)
ICONO_CARPETA = chr(0xE8B7)  # Folder
ICONO_ARCHIVO = chr(0xE8A5)  # Page (documento)
ICONO_AGREGAR = chr(0xE710)  # Add (+)
ICONO_TEMA = chr(0xE713)  # Settings (engranaje)
ICONO_INFO = chr(0xE946)  # Info
ICONO_ADVERTENCIA = chr(0xE7BA)  # Warning (triángulo)
ICONO_ERROR = chr(0xE711)  # Cancel (X)
ICONO_PREGUNTA = chr(0xE897)  # Help (?)

TEMAS = {
    "claro": {
        "BG": "#eef1f5",
        "CARD": "#ffffff",
        "BORDER": "#e5e7eb",
        "BORDER_SUBTLE": "#e9ecf1",
        "TEXT": "#1f2937",
        "TEXT_MUTED": "#6b7280",
        "ACCENT": "#38bdf8",
        "ACCENT_HOVER": "#0ea5e9",
        "ACCENT_LIGHT": "#e0f2fe",
        "SUCCESS": "#16a34a",
        "ERROR": "#dc2626",
        "WARNING": "#d97706",
        "INFO": "#2563eb",
        "DANGER_BG": "#fef2f2",
    },
    "gris": {
        "BG": "#94a3b8",
        "CARD": "#cbd5e1",
        "BORDER": "#64748b",
        "BORDER_SUBTLE": "#aab6c4",
        "TEXT": "#0f172a",
        "TEXT_MUTED": "#334155",
        "ACCENT": "#0284c7",
        "ACCENT_HOVER": "#0369a1",
        "ACCENT_LIGHT": "#dff3fd",
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
        "BORDER_SUBTLE": "#293241",
        "TEXT": "#f3f4f6",
        "TEXT_MUTED": "#9ca3af",
        "ACCENT": "#38bdf8",
        "ACCENT_HOVER": "#7dd3fc",
        "ACCENT_LIGHT": "#0c4a6e",
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
                     font=(FONT_FAMILY, 9))
    style.configure("SectionTitle.Card.TLabel", background=COLOR_CARD,
                     foreground=COLOR_TEXT, font=(FONT_FAMILY, 13, "bold"))

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

    style.configure("Primary.TButton", background=COLOR_ACCENT, foreground="#ffffff",
                     font=(FONT_FAMILY, 10, "bold"), padding=(16, 9))
    style.map("Primary.TButton",
               background=[("disabled", "#bae6fd"), ("active", COLOR_ACCENT_HOVER)],
               foreground=[("disabled", "#ffffff")])

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

    style.configure("Card.TRadiobutton", background=COLOR_CARD, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 9))
    style.map("Card.TRadiobutton", background=[("active", COLOR_CARD)])

    # Filas de opciones seleccionables (radiobuttons con fondo resaltado si están activas)
    style.configure("Option.TFrame", background=COLOR_BG)
    style.configure("OptionSelected.TFrame", background=COLOR_ACCENT_LIGHT)

    # Layout sin el punto/indicador: el fondo de la fila ya indica la selección
    _layout_radio_sin_indicador = [
        ("Radiobutton.padding", {"sticky": "nswe", "children": [
            ("Radiobutton.label", {"sticky": "nswe"}),
        ]}),
    ]
    style.layout("Option.TRadiobutton", _layout_radio_sin_indicador)
    style.layout("OptionSelected.TRadiobutton", _layout_radio_sin_indicador)

    style.configure("Option.TRadiobutton", background=COLOR_BG, foreground=COLOR_TEXT,
                     font=(FONT_FAMILY, 9), padding=(8, 6), relief="flat", borderwidth=0)
    style.map("Option.TRadiobutton", background=[("active", COLOR_BG)])

    style.configure("OptionSelected.TRadiobutton", background=COLOR_ACCENT_LIGHT,
                     foreground=COLOR_TEXT, font=(FONT_FAMILY, 9, "bold"), padding=(8, 6),
                     relief="flat", borderwidth=0)
    style.map("OptionSelected.TRadiobutton", background=[("active", COLOR_ACCENT_LIGHT)])

    # Progressbar
    style.configure("Modern.Horizontal.TProgressbar", troughcolor=COLOR_ACCENT_LIGHT,
                     background=COLOR_ACCENT, bordercolor=COLOR_ACCENT_LIGHT,
                     lightcolor=COLOR_ACCENT, darkcolor=COLOR_ACCENT, thickness=8)

    # Separator
    style.configure("TSeparator", background=COLOR_BORDER)

    return style
