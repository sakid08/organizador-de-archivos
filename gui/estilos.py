"""Paleta de colores y estilos ttk compartidos por toda la interfaz"""

import tkinter as tk
from tkinter import ttk

# Paleta de colores - diseño claro y moderno
COLOR_BG = "#f7f8fa"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#e5e7eb"
COLOR_TEXT = "#1f2937"
COLOR_TEXT_MUTED = "#6b7280"
COLOR_ACCENT = "#4f46e5"
COLOR_ACCENT_HOVER = "#4338ca"
COLOR_ACCENT_LIGHT = "#eef2ff"
COLOR_SUCCESS = "#16a34a"
COLOR_ERROR = "#dc2626"
COLOR_WARNING = "#d97706"
COLOR_INFO = "#2563eb"
COLOR_DANGER_BG = "#fef2f2"

FONT_FAMILY = "Segoe UI"


def aplicar_estilos(root: tk.Tk) -> ttk.Style:
    """Configura un tema claro y moderno para los widgets ttk de la ventana"""
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

    # Botones
    style.configure("TButton", font=(FONT_FAMILY, 10), padding=(14, 8),
                     relief="flat", borderwidth=0)

    style.configure("Primary.TButton", background=COLOR_ACCENT, foreground="#ffffff",
                     font=(FONT_FAMILY, 10, "bold"), padding=(16, 9))
    style.map("Primary.TButton",
               background=[("disabled", "#c7c9f5"), ("active", COLOR_ACCENT_HOVER)],
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

    # Progressbar
    style.configure("Modern.Horizontal.TProgressbar", troughcolor=COLOR_ACCENT_LIGHT,
                     background=COLOR_ACCENT, bordercolor=COLOR_ACCENT_LIGHT,
                     lightcolor=COLOR_ACCENT, darkcolor=COLOR_ACCENT, thickness=8)

    # Separator
    style.configure("TSeparator", background=COLOR_BORDER)

    return style
