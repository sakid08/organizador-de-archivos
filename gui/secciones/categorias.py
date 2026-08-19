"""Sección 'Categorías': filas dinámicas (predeterminadas y personalizadas)"""

import tkinter as tk
from tkinter import ttk

from gui import estilos
from gui.dialogs import confirmar


class CategoriasMixin:
    """Mezclado en VentanaPrincipal: card de categorías y su estado dinámico"""

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
            self._categorias_inner, text=f"{estilos.ICONO_AGREGAR}  Nueva categoría personalizada",
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
        if confirmar(self.root, "Eliminar categoría",
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
