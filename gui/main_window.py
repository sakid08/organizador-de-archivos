import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path

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


class VentanaPrincipal:
    """Ventana principal de la aplicación"""

    def __init__(self, root: tk.Tk, app_controller=None):
        self.root = root
        self.app_controller = app_controller

        self.root.configure(bg=COLOR_BG)

        # Variables de configuración generales
        self.ruta_base = tk.StringVar(value="./")
        self.digitos = tk.IntVar(value=4)
        self.archivos_por_carpeta = tk.IntVar(value=600)
        self.mostrar_detalle = tk.BooleanVar(value=True)

        # Qué elementos organizar: "carpetas" (por defecto), "sueltos" o "todos".
        # Son mutuamente excluyentes.
        self.modo_origen = tk.StringVar(value="carpetas")

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
        self._setup_estilos()
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

    def _setup_estilos(self):
        """Configura un tema claro y moderno para los widgets ttk"""
        style = ttk.Style(self.root)
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

        # Checkboxes de opciones generales
        opciones_frame = ttk.Frame(main_frame, style="TFrame")
        opciones_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 16))

        ttk.Checkbutton(opciones_frame, text="Mostrar detalles del proceso",
                         variable=self.mostrar_detalle).pack(anchor="w")

        ttk.Label(opciones_frame, text="¿Qué elementos organizar?",
                  style="TLabel", font=(FONT_FAMILY, 10, "bold")).pack(anchor="w", pady=(12, 4))
        ttk.Radiobutton(opciones_frame, text="Solo lo que está dentro de carpetas (ignora archivos sueltos)",
                         variable=self.modo_origen, value="carpetas").pack(anchor="w")
        ttk.Radiobutton(opciones_frame, text="Solo archivos sueltos en la ruta base (ignora carpetas)",
                         variable=self.modo_origen, value="sueltos").pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(opciones_frame, text="Todos los archivos (carpetas y sueltos)",
                         variable=self.modo_origen, value="todos").pack(anchor="w", pady=(4, 0))

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
        """Crea un contenedor tipo 'card' con borde sutil"""
        outer = tk.Frame(parent, bg=COLOR_BORDER)
        inner = ttk.Frame(outer, padding="16", style="Card.TFrame")
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        if titulo:
            ttk.Label(inner, text=titulo, style="SectionTitle.Card.TLabel").grid(
                row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 12))
        return outer, inner

    def _crear_frame_configuracion(self, parent):
        """Crea el frame de configuración general"""
        outer, inner = self._crear_card(parent, "Configuración general")
        inner.columnconfigure(1, weight=1)

        # Ruta base
        ttk.Label(inner, text="Ruta base", style="Card.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=8)
        ruta_entry = ttk.Entry(inner, textvariable=self.ruta_base)
        ruta_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(12, 8), pady=8)
        ttk.Button(inner, text="Examinar", style="Secondary.TButton",
                   command=self._seleccionar_ruta).grid(row=1, column=2, pady=8)

        # Dígitos
        ttk.Label(inner, text="Dígitos (0001)", style="Card.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=8)
        ttk.Spinbox(inner, from_=1, to=6, textvariable=self.digitos, width=10).grid(
            row=2, column=1, sticky=tk.W, padx=(12, 8), pady=8)

        # Archivos por carpeta
        ttk.Label(inner, text="Archivos por carpeta", style="Card.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=8)
        ttk.Spinbox(inner, from_=100, to=2000, increment=100,
                    textvariable=self.archivos_por_carpeta, width=10).grid(
            row=3, column=1, sticky=tk.W, padx=(12, 8), pady=8)

        return outer

    def _crear_frame_categorias(self, parent):
        """Crea el frame donde se listan las categorías configurables"""
        outer, inner = self._crear_card(parent, "Categorías")
        ttk.Label(inner, text="Elige qué tipos de archivo organizar y con qué nombre de carpeta",
                  style="Muted.Card.TLabel").grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(0, 12))
        inner.columnconfigure(1, weight=1)
        self._categorias_inner = inner
        self._categorias_siguiente_fila = 2
        return outer

    def inicializar_categorias(self, categorias):
        """Construye las filas de la interfaz de categorías a partir de la lista del controlador"""
        self._categorias_orden = []

        for categoria in categorias:
            self._crear_fila_categoria(categoria)

        # Botón para agregar categorías personalizadas nuevas
        self.btn_agregar_categoria = ttk.Button(
            self._categorias_inner, text="+ Nueva categoría personalizada",
            style="GhostCard.TButton", command=self._agregar_categoria_personalizada)

        self._reposicionar_boton_agregar()
        self._actualizar_combobox_renombrado()

    def _crear_fila_categoria(self, categoria):
        """Crea los widgets de una fila de categoría y la registra en el estado"""
        inner = self._categorias_inner
        fila = self._categorias_siguiente_fila
        categoria_id = categoria["id"]
        es_personalizada = categoria.get("personalizada", False)

        activa_var = tk.BooleanVar(value=categoria.get("activa", True))
        prefijo_var = tk.StringVar(value=categoria["prefijo"])

        chk = ttk.Checkbutton(inner, text=categoria["nombre"], variable=activa_var,
                               style="Card.TCheckbutton",
                               command=self._actualizar_combobox_renombrado)
        chk.grid(row=fila, column=0, sticky=tk.W, pady=6)
        activa_var.trace_add("write", lambda *_: self._persistir_si_personalizada(categoria_id))

        prefijo_entry = ttk.Entry(inner, textvariable=prefijo_var)
        prefijo_entry.grid(row=fila, column=1, sticky=(tk.W, tk.E), padx=(12, 8), pady=6)
        prefijo_var.trace_add("write", lambda *_: (
            self._actualizar_combobox_renombrado(),
            self._persistir_si_personalizada(categoria_id)
        ))

        ext_label = ttk.Label(inner, text=", ".join(categoria["extensiones"]),
                               style="Muted.Card.TLabel")
        ext_label.grid(row=fila, column=2, sticky=tk.W, padx=(0, 8), pady=6)

        btn_editar = ttk.Button(inner, text="Editar", style="GhostCard.TButton",
                                 command=lambda cid=categoria_id: self._editar_extensiones_categoria(cid))
        btn_editar.grid(row=fila, column=3, sticky=tk.W, pady=6)

        btn_eliminar = None
        if es_personalizada:
            btn_eliminar = ttk.Button(inner, text="Eliminar", style="GhostCard.TButton",
                                       command=lambda cid=categoria_id: self._eliminar_categoria_personalizada(cid))
            btn_eliminar.grid(row=fila, column=4, sticky=tk.W, padx=(4, 0), pady=6)

        self.categorias_estado[categoria_id] = {
            "activa": activa_var,
            "prefijo": prefijo_var,
            "nombre": categoria["nombre"],
            "extensiones": list(categoria["extensiones"]),
            "ext_label": ext_label,
            "personalizada": es_personalizada,
            "widgets": {
                "chk": chk,
                "prefijo_entry": prefijo_entry,
                "ext_label": ext_label,
                "btn_editar": btn_editar,
                "btn_eliminar": btn_eliminar,
            },
        }
        self._categorias_orden.append(categoria_id)
        self._categorias_siguiente_fila = fila + 1

    def _reposicionar_boton_agregar(self):
        """Ubica el botón de 'agregar categoría' justo debajo de la última fila"""
        if self.btn_agregar_categoria:
            self.btn_agregar_categoria.grid(
                row=self._categorias_siguiente_fila, column=0, columnspan=4,
                sticky=tk.W, pady=(10, 0))

    def _persistir_si_personalizada(self, categoria_id):
        """Persiste el estado de una categoría personalizada cuando cambia en la UI"""
        estado = self.categorias_estado.get(categoria_id)
        if estado and estado.get("personalizada") and self.app_controller:
            self.app_controller.persistir_categorias_personalizadas()

    def agregar_fila_categoria(self, categoria):
        """Agrega una nueva fila de categoría a la interfaz (usado al crear una personalizada)"""
        self._crear_fila_categoria(categoria)
        self._reposicionar_boton_agregar()
        self._actualizar_combobox_renombrado()

    def eliminar_fila_categoria(self, categoria_id):
        """Elimina la fila de una categoría y reordena las restantes"""
        estado = self.categorias_estado.pop(categoria_id, None)
        if not estado:
            return
        for widget in estado["widgets"].values():
            if widget is not None:
                widget.destroy()
        self._categorias_orden.remove(categoria_id)

        # Reconstruir las filas restantes para evitar huecos en la grilla
        orden_actual = list(self._categorias_orden)
        self._categorias_orden = []
        self._categorias_siguiente_fila = 2
        for cid in orden_actual:
            estado_fila = self.categorias_estado[cid]
            fila = self._categorias_siguiente_fila
            for widget in estado_fila["widgets"].values():
                if widget is None:
                    continue
                info = widget.grid_info()
                widget.grid(row=fila, column=info["column"], sticky=info.get("sticky", ""),
                            padx=info.get("padx", 0), pady=info.get("pady", 0))
            self._categorias_orden.append(cid)
            self._categorias_siguiente_fila = fila + 1

        self._reposicionar_boton_agregar()
        self._actualizar_combobox_renombrado()

    def _agregar_categoria_personalizada(self):
        """Abre el diálogo para crear una nueva categoría personalizada"""
        if not self.app_controller:
            return
        from gui.dialogs import DialogoNuevaCategoria
        DialogoNuevaCategoria(self.root, self.app_controller.crear_categoria_personalizada)

    def _eliminar_categoria_personalizada(self, categoria_id):
        """Pide confirmación y elimina una categoría personalizada"""
        if not self.app_controller:
            return
        estado = self.categorias_estado.get(categoria_id)
        nombre = estado["nombre"] if estado else categoria_id
        if messagebox.askyesno("Eliminar categoría",
                                f"¿Eliminar la categoría personalizada '{nombre}'?"):
            self.app_controller.eliminar_categoria_personalizada(categoria_id)

    def categoria_activa(self, categoria_id) -> bool:
        """Indica si una categoría está marcada como activa"""
        estado = self.categorias_estado.get(categoria_id)
        return bool(estado and estado["activa"].get())

    def categoria_prefijo(self, categoria_id) -> str:
        """Obtiene el prefijo actual configurado para una categoría"""
        estado = self.categorias_estado.get(categoria_id)
        return estado["prefijo"].get() if estado else ""

    def categoria_renombrado_seleccionada(self) -> str:
        """Devuelve el prefijo elegido en el combo de renombrado"""
        return self.categoria_renombrado.get()

    def actualizar_extensiones_categoria(self, categoria_id, extensiones):
        """Actualiza la etiqueta de extensiones de una categoría"""
        estado = self.categorias_estado.get(categoria_id)
        if estado:
            estado["extensiones"] = list(extensiones)
            estado["ext_label"].config(text=", ".join(extensiones))

    def _actualizar_combobox_renombrado(self):
        """Refresca las opciones del combo de renombrado con las categorías activas"""
        opciones = [estado["prefijo"].get() for estado in self.categorias_estado.values()
                    if estado["activa"].get() and estado["prefijo"].get()]
        if hasattr(self, "combo_renombrado"):
            self.combo_renombrado.config(values=opciones)
        if opciones and self.categoria_renombrado.get() not in opciones:
            self.categoria_renombrado.set(opciones[0])
        elif not opciones:
            self.categoria_renombrado.set("")

    def _crear_botones_accion(self, parent):
        """Crea los botones de acción"""
        buttons_frame = ttk.Frame(parent, style="TFrame")
        buttons_frame.columnconfigure(0, weight=1)

        fila_botones = ttk.Frame(buttons_frame, style="TFrame")
        fila_botones.grid(row=0, column=0, sticky=tk.W)

        self.btn_organizar = ttk.Button(fila_botones, text="▶  Organizar archivos",
                                         style="Primary.TButton")
        self.btn_organizar.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_renombrar = ttk.Button(fila_botones, text="✏  Solo renombrar carpetas",
                                         style="Secondary.TButton")
        self.btn_renombrar.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_detener = ttk.Button(fila_botones, text="⏹  Detener",
                                       state=tk.DISABLED, style="Danger.TButton")
        self.btn_detener.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(fila_botones, text="🗑  Limpiar log", style="Ghost.TButton",
                   command=self._limpiar_log).pack(side=tk.LEFT)

        fila_renombrado = ttk.Frame(buttons_frame, style="TFrame")
        fila_renombrado.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Label(fila_renombrado, text="Categoría a renombrar:", style="TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.combo_renombrado = ttk.Combobox(fila_renombrado, textvariable=self.categoria_renombrado,
                                              state="readonly", width=28)
        self.combo_renombrado.pack(side=tk.LEFT)

        # Fila para agrupar TODOS los archivos sin distinguir tipo/extensión
        fila_general = ttk.Frame(buttons_frame, style="TFrame")
        fila_general.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Label(fila_general, text="Prefijo para agrupar todo:", style="TLabel").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Entry(fila_general, textvariable=self.prefijo_general, width=20).pack(side=tk.LEFT, padx=(0, 10))
        self.btn_agrupar_todo = ttk.Button(fila_general, text="📁  Agrupar todos los archivos (sin distinguir tipo)",
                                            style="Secondary.TButton")
        self.btn_agrupar_todo.pack(side=tk.LEFT)

        return buttons_frame

    def _crear_frame_progreso(self, parent):
        """Crea el frame de progreso"""
        outer, inner = self._crear_card(parent, "Progreso")
        inner.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(inner, mode='indeterminate',
                                             style="Modern.Horizontal.TProgressbar")
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))

        self.progress_label = ttk.Label(inner, text="Esperando inicio...",
                                         style="Muted.Card.TLabel")
        self.progress_label.grid(row=2, column=0, sticky=tk.W)

        return outer

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

    def _seleccionar_ruta(self):
        """Abre diálogo para seleccionar ruta"""
        ruta = filedialog.askdirectory(title="Seleccionar carpeta base")
        if ruta:
            self.ruta_base.set(ruta)
            if self.app_controller:
                self.app_controller.agregar_log(f"Ruta base cambiada a: {ruta}", "INFO")

    def _editar_extensiones_categoria(self, categoria_id):
        """Abre diálogo para editar las extensiones de una categoría"""
        if not self.app_controller:
            return
        estado = self.categorias_estado[categoria_id]
        from gui.dialogs import DialogoExtensiones
        DialogoExtensiones(
            self.root,
            estado["extensiones"],
            lambda nuevas: self.app_controller.editar_extensiones_categoria(categoria_id, nuevas),
            titulo=f"Extensiones de {estado['nombre']}"
        )

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

    def set_progreso(self, estado):
        """Actualiza el estado del progreso"""
        if estado == "iniciando":
            self.progress_bar.start(10)
        elif estado == "detenido":
            self.progress_bar.stop()

    def set_progress_label(self, mensaje):
        """Actualiza la etiqueta de progreso"""
        self.progress_label.config(text=mensaje)

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
