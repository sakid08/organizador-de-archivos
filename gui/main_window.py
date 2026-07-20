import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path

class VentanaPrincipal:
    """Ventana principal de la aplicación"""
    
    def __init__(self, root: tk.Tk, app_controller=None):
        self.root = root
        self.app_controller = app_controller
        
        # Variables de configuración
        self.ruta_base = tk.StringVar(value="./")
        self.prefijo = tk.StringVar(value="Fondos de pantalla")
        self.digitos = tk.IntVar(value=4)
        self.imagenes_por_carpeta = tk.IntVar(value=600)
        self.mostrar_detalle = tk.BooleanVar(value=True)
        
        # Almacenar referencias a widgets que necesitan el controlador
        self.btn_organizar = None
        self.btn_renombrar = None
        self.btn_detener = None
        
        # Crear interfaz
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
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Organizador de Imágenes", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Frame de configuración
        config_frame = self._crear_frame_configuracion(main_frame)
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Checkbox mostrar detalles
        ttk.Checkbutton(main_frame, text="Mostrar detalles del proceso", 
                       variable=self.mostrar_detalle).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Frame de botones de acción
        self._crear_botones_accion(main_frame).grid(row=3, column=0, pady=10)
        
        # Frame de progreso
        self._crear_frame_progreso(main_frame).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Área de log
        self._crear_area_log(main_frame).grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Barra de estado
        self.status_bar = ttk.Label(main_frame, text="Listo", relief=tk.SUNKEN)
        self.status_bar.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def _crear_frame_configuracion(self, parent):
        """Crea el frame de configuración"""
        config_frame = ttk.LabelFrame(parent, text="Configuración", padding="10")
        config_frame.columnconfigure(1, weight=1)
        
        # Ruta base
        ttk.Label(config_frame, text="Ruta base:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ruta_entry = ttk.Entry(config_frame, textvariable=self.ruta_base, width=50)
        ruta_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(config_frame, text="Examinar", command=self._seleccionar_ruta).grid(row=0, column=2, pady=5)
        
        # Prefijo
        ttk.Label(config_frame, text="Prefijo de carpeta:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(config_frame, textvariable=self.prefijo, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Dígitos
        ttk.Label(config_frame, text="Dígitos (0001):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(config_frame, from_=1, to=6, textvariable=self.digitos, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Imágenes por carpeta
        ttk.Label(config_frame, text="Imágenes por carpeta:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(config_frame, from_=100, to=2000, increment=100, 
                   textvariable=self.imagenes_por_carpeta, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Extensiones
        ttk.Label(config_frame, text="Extensiones soportadas:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ext_frame = ttk.Frame(config_frame)
        ext_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        self.extensiones_label = ttk.Label(ext_frame, text="")
        self.extensiones_label.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(ext_frame, text="Editar", command=self._editar_extensiones, width=8).pack(side=tk.LEFT, padx=(10, 0))
        
        return config_frame
    
    def _crear_botones_accion(self, parent):
        """Crea los botones de acción"""
        buttons_frame = ttk.Frame(parent)
        
        # Crear botones sin comandos (se asignarán después)
        self.btn_organizar = ttk.Button(buttons_frame, text="▶ Organizar Archivos", 
                                        width=20)
        self.btn_organizar.pack(side=tk.LEFT, padx=5)
        
        self.btn_renombrar = ttk.Button(buttons_frame, text="✏ Solo Renombrar Carpetas", 
                                        width=25)
        self.btn_renombrar.pack(side=tk.LEFT, padx=5)
        
        self.btn_detener = ttk.Button(buttons_frame, text="⏹ Detener", 
                                      state=tk.DISABLED, width=15)
        self.btn_detener.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="🗑 Limpiar Log", 
                  command=self._limpiar_log, width=12).pack(side=tk.LEFT, padx=5)
        
        return buttons_frame
    
    def _crear_frame_progreso(self, parent):
        """Crea el frame de progreso"""
        progress_frame = ttk.LabelFrame(parent, text="Progreso", padding="10")
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Esperando inicio...")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        return progress_frame
    
    def _crear_area_log(self, parent):
        """Crea el área de log"""
        log_frame = ttk.LabelFrame(parent, text="Log de ejecución", padding="10")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80, 
                                                   font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar colores para el log
        self.log_text.tag_config("INFO", foreground="blue")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("WARNING", foreground="orange")
        
        return log_frame
    
    def _seleccionar_ruta(self):
        """Abre diálogo para seleccionar ruta"""
        ruta = filedialog.askdirectory(title="Seleccionar carpeta base")
        if ruta:
            self.ruta_base.set(ruta)
            if self.app_controller:
                self.app_controller.agregar_log(f"Ruta base cambiada a: {ruta}", "INFO")
    
    def _editar_extensiones(self):
        """Abre diálogo para editar extensiones"""
        if self.app_controller:
            from gui.dialogs import DialogoExtensiones
            DialogoExtensiones(
                self.root, 
                self.app_controller.extensiones,
                self.app_controller.editar_extensiones
            )
    
    def _limpiar_log(self):
        """Limpia el área de log"""
        self.log_text.delete("1.0", tk.END)
        if self.app_controller:
            self.app_controller.agregar_log("Log limpiado", "INFO")
    
    def actualizar_extensiones(self, extensiones):
        """Actualiza la etiqueta de extensiones"""
        self.extensiones_label.config(text=", ".join(extensiones))
    
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
        self.status_bar.config(text=mensaje)
    
    def habilitar_botones(self, habilitados):
        """Habilita o deshabilita los botones de acción"""
        estado = tk.NORMAL if habilitados else tk.DISABLED
        if self.btn_organizar:
            self.btn_organizar.config(state=estado)
        if self.btn_renombrar:
            self.btn_renombrar.config(state=estado)
        if self.btn_detener:
            self.btn_detener.config(state=tk.DISABLED if habilitados else tk.NORMAL)