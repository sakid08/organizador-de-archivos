import tkinter as tk
from tkinter import ttk

from gui.estilos import aplicar_estilos, COLOR_BG, COLOR_BORDER, FONT_FAMILY
from gui.secciones.configuracion import ConfiguracionMixin
from gui.secciones.categorias import CategoriasMixin
from gui.secciones.opciones import OpcionesMixin
from gui.secciones.botones import BotonesMixin
from gui.secciones.progreso import ProgresoMixin
from gui.secciones.log import LogMixin


class VentanaPrincipal(ConfiguracionMixin, CategoriasMixin, OpcionesMixin,
                        BotonesMixin, ProgresoMixin, LogMixin):
    """Ventana principal de la aplicación"""

    def __init__(self, root: tk.Tk, app_controller=None):
        self.root = root
        self.app_controller = app_controller

        self.root.configure(bg=COLOR_BG)

        # Variables de configuración generales
        self.ruta_base = tk.StringVar(value="")
        self.digitos = tk.IntVar(value=4)
        self.archivos_por_carpeta = tk.IntVar(value=600)
        self.mostrar_detalle = tk.BooleanVar(value=True)

        # Qué elementos organizar: "carpetas" (por defecto), "sueltos" o "todos".
        # Son mutuamente excluyentes.
        self.modo_origen = tk.StringVar(value="carpetas")

        # Orden para distribuir los archivos en las carpetas numeradas:
        # "fecha" (por defecto), "nombre_az" o "nombre_za". Mutuamente excluyentes.
        self.orden_archivos = tk.StringVar(value="fecha")

        # Método de agrupamiento de las carpetas numeradas: "cantidad" (por defecto),
        # "anio", "mes" o "letra". Mutuamente excluyentes.
        self.agrupamiento = tk.StringVar(value="cantidad")

        # Variable de la categoría elegida para "Solo renombrar carpetas"
        self.categoria_renombrado = tk.StringVar(value="")

        # Prefijo para agrupar TODOS los archivos sin distinguir tipo
        self.prefijo_general = tk.StringVar(value="Archivos")

        # Estado por categoría: id -> {"activa": BooleanVar, "prefijo": StringVar,
        #                              "nombre": str, "extensiones": list, "ext_label": ttk.Label}
        self.categorias_estado = {}
        self.categorias_frame = None
        self._categorias_orden = []
        self.btn_agregar_categoria = None

        # Almacenar referencias a widgets que necesitan el controlador
        self.btn_organizar = None
        self.btn_renombrar = None
        self.btn_detener = None
        self.btn_agrupar_todo = None

        # Crear interfaz
        aplicar_estilos(self.root)
        self._setup_ui()

    def set_controller(self, controller):
        """Establece el controlador después de la creación"""
        self.app_controller = controller
        # Actualizar comandos de los botones
        if self.btn_organizar:
            self.btn_organizar.config(command=self.app_controller.iniciar_organizacion)
        if self.btn_renombrar:
            self.btn_renombrar.config(command=self.app_controller.iniciar_renombrado)
        if self.btn_detener:
            self.btn_detener.config(command=self.app_controller.detener_proceso)
        if self.btn_agrupar_todo:
            self.btn_agrupar_todo.config(command=self.app_controller.iniciar_organizacion_general)

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Canvas + scrollbar para que la ventana sea desplazable con muchas categorías
        canvas = tk.Canvas(self.root, bg=COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        main_frame = ttk.Frame(canvas, padding="24", style="TFrame")
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def _actualizar_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _ajustar_ancho(event):
            canvas.itemconfig(canvas_window, width=event.width)

        main_frame.bind("<Configure>", _actualizar_scrollregion)
        canvas.bind("<Configure>", _ajustar_ancho)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        main_frame.columnconfigure(0, weight=1)

        # Encabezado
        header_frame = ttk.Frame(main_frame, style="TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 18))
        ttk.Label(header_frame, text="Organizador de Archivos",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text="Organiza imágenes, videos, documentos y más, automáticamente",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        # Frame de configuración general
        config_frame = self._crear_frame_configuracion(main_frame)
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 16))

        # Frame de categorías
        self.categorias_frame = self._crear_frame_categorias(main_frame)
        self.categorias_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 16))

        # Opciones de organización (modo, orden, agrupamiento)
        self._crear_frame_opciones(main_frame).grid(row=3, column=0, sticky=tk.W, pady=(0, 16))

        # Frame de botones de acción
        self._crear_botones_accion(main_frame).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 16))

        # Frame de progreso
        self._crear_frame_progreso(main_frame).grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 16))

        # Área de log
        self._crear_area_log(main_frame).grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 16))

        # Barra de estado
        status_frame = ttk.Frame(main_frame, style="Card.TFrame")
        status_frame.grid(row=7, column=0, sticky=(tk.W, tk.E))
        self.status_bar = ttk.Label(status_frame, text="  Listo", style="Card.TLabel",
                                     font=(FONT_FAMILY, 9), anchor="w")
        self.status_bar.pack(fill="x", padx=4, pady=6)

    def _crear_card(self, parent, titulo=None):
        """Crea un contenedor tipo 'card' con borde sutil. Compartido por todas las secciones"""
        outer = tk.Frame(parent, bg=COLOR_BORDER)
        inner = ttk.Frame(outer, padding="16", style="Card.TFrame")
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        if titulo:
            ttk.Label(inner, text=titulo, style="SectionTitle.Card.TLabel").grid(
                row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 12))
        return outer, inner

    def set_status(self, mensaje):
        """Actualiza la barra de estado"""
        self.status_bar.config(text=f"  {mensaje}")

    def habilitar_botones(self, habilitados):
        """Habilita o deshabilita los botones de acción"""
        estado = tk.NORMAL if habilitados else tk.DISABLED
        if self.btn_organizar:
            self.btn_organizar.config(state=estado)
        if self.btn_renombrar:
            self.btn_renombrar.config(state=estado)
        if self.btn_agrupar_todo:
            self.btn_agrupar_todo.config(state=estado)
        if self.btn_detener:
            self.btn_detener.config(state=tk.DISABLED if habilitados else tk.NORMAL)
