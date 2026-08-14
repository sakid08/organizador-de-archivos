# core/app.py
"""Controlador principal de la aplicación"""

import copy
import threading
from pathlib import Path
from tkinter import messagebox

from core.organizador import OrganizadorArchivos
from core.config import CATEGORIAS_DEFAULT
from core.utils import normalizar_extensiones, generar_id_categoria
from core.persistencia import cargar_categorias_personalizadas, guardar_categorias_personalizadas

DESCRIPCION_MODOS_ORIGEN = {
    "carpetas": "Solo lo que está dentro de carpetas",
    "sueltos": "Solo archivos sueltos en la ruta base",
    "todos": "Todos los archivos (carpetas y sueltos)",
}

class AppController:
    """Controlador de la aplicación"""

    def __init__(self, ventana):
        self.ventana = ventana
        self.proceso_activo = False
        self.categorias = copy.deepcopy(CATEGORIAS_DEFAULT) + cargar_categorias_personalizadas()

        # Inicializar la interfaz con las categorías disponibles
        self.ventana.inicializar_categorias(self.categorias)

    def agregar_log(self, mensaje, tipo="INFO"):
        """Agrega mensaje al log a través de la ventana"""
        self.ventana.agregar_log(mensaje, tipo)

    def _debe_detener(self) -> bool:
        """Verifica si el proceso debe detenerse"""
        return not self.proceso_activo

    def _actualizar_progreso(self, mensaje):
        """Actualiza mensaje de progreso"""
        self.ventana.set_progress_label(mensaje)

    def _finalizar_proceso(self):
        """Finaliza el proceso y limpia el estado"""
        self.proceso_activo = False
        self.ventana.habilitar_botones(True)
        self.ventana.set_progreso("detenido")
        self.ventana.set_progress_label("Proceso finalizado")
        self.ventana.set_status("Listo")

    def _categorias_activas(self):
        """Construye la lista de categorías activas con sus prefijos actuales"""
        activas = []
        for categoria in self.categorias:
            if not self.ventana.categoria_activa(categoria["id"]):
                continue
            activas.append({
                "id": categoria["id"],
                "nombre": categoria["nombre"],
                "prefijo": self.ventana.categoria_prefijo(categoria["id"]),
                "extensiones": categoria["extensiones"],
            })
        return activas

    def iniciar_renombrado(self):
        """Inicia el proceso de renombrado de carpetas de una categoría"""
        if self.proceso_activo:
            messagebox.showwarning("Proceso activo", "Ya hay un proceso en ejecución")
            return

        prefijo = self.ventana.categoria_renombrado_seleccionada()
        if not prefijo:
            messagebox.showwarning("Sin categoría", "Selecciona una categoría activa para renombrar")
            return

        ruta_base = self.ventana.ruta_base.get()
        confirmar = messagebox.askyesno(
            "Confirmar renombrado",
            f"Se renombrarán las carpetas existentes en:\n{ruta_base}\n\n"
            f"usando el prefijo '{prefijo}'.\n\n¿Deseas continuar?"
        )
        if not confirmar:
            return

        def ejecutar_renombrado():
            try:
                self._iniciar_proceso()
                self.agregar_log("="*50, "INFO")
                self.agregar_log("INICIANDO RENOMBRADO DE CARPETAS", "INFO")

                ruta_base = Path(self.ventana.ruta_base.get())
                digitos = self.ventana.digitos.get()

                self.agregar_log(f"Ruta base: {ruta_base}")
                self.agregar_log(f"Prefijo: {prefijo}")

                organizador = OrganizadorArchivos(
                    ruta_base=ruta_base,
                    categorias=self._categorias_activas(),
                    digitos=digitos,
                    archivos_por_carpeta=self.ventana.archivos_por_carpeta.get(),
                    callback_log=self.agregar_log,
                    callback_progreso=self._actualizar_progreso,
                    detener_callback=self._debe_detener,
                    mostrar_detalle=self.ventana.mostrar_detalle.get()
                )

                procesadas, renombradas = organizador.renombrar_carpetas(prefijo)

                self.agregar_log(f"\n✅ Renombrado completado. {renombradas} carpetas renombradas.", "SUCCESS")
                self.agregar_log("="*50, "INFO")

                if not self.proceso_activo:
                    self.agregar_log("⚠ Proceso detenido por el usuario", "WARNING")

            except Exception as e:
                self.agregar_log(f"❌ Error fatal: {e}", "ERROR")
                messagebox.showerror("Error", f"Ocurrió un error:\n{e}")
            finally:
                self._finalizar_proceso()

        threading.Thread(target=ejecutar_renombrado, daemon=True).start()

    def iniciar_organizacion(self):
        """Inicia el proceso de organización de archivos"""
        if self.proceso_activo:
            messagebox.showwarning("Proceso activo", "Ya hay un proceso en ejecución")
            return

        categorias_activas = self._categorias_activas()
        if not categorias_activas:
            messagebox.showwarning("Sin categorías", "Activa al menos una categoría para organizar")
            return

        ruta_base = self.ventana.ruta_base.get()
        nombres_categorias = ", ".join(c["nombre"] for c in categorias_activas)
        modo_origen = self.ventana.modo_origen.get()
        confirmar = messagebox.askyesno(
            "Confirmar organización",
            f"Se organizarán los archivos en:\n{ruta_base}\n\n"
            f"Categorías activas: {nombres_categorias}\n"
            f"Elementos a organizar: {DESCRIPCION_MODOS_ORIGEN.get(modo_origen, modo_origen)}\n\n"
            f"Esta acción moverá archivos y carpetas. ¿Deseas continuar?"
        )
        if not confirmar:
            return

        def ejecutar_organizacion():
            try:
                self._iniciar_proceso()
                self.agregar_log("="*50, "INFO")
                self.agregar_log("INICIANDO ORGANIZACIÓN DE ARCHIVOS", "INFO")

                ruta_base = Path(self.ventana.ruta_base.get())
                digitos = self.ventana.digitos.get()
                archivos_por_carpeta = self.ventana.archivos_por_carpeta.get()
                mostrar_detalle = self.ventana.mostrar_detalle.get()
                modo_origen = self.ventana.modo_origen.get()

                self.agregar_log(f"Ruta base: {ruta_base}")
                self.agregar_log(f"Categorías activas: {', '.join(c['nombre'] for c in categorias_activas)}")
                self.agregar_log(f"Archivos por carpeta: {archivos_por_carpeta}")
                self.agregar_log(f"Mostrar detalles: {mostrar_detalle}")
                self.agregar_log(f"Elementos a organizar: {DESCRIPCION_MODOS_ORIGEN.get(modo_origen, modo_origen)}")

                organizador = OrganizadorArchivos(
                    ruta_base=ruta_base,
                    categorias=categorias_activas,
                    digitos=digitos,
                    archivos_por_carpeta=archivos_por_carpeta,
                    callback_log=self.agregar_log,
                    callback_progreso=self._actualizar_progreso,
                    detener_callback=self._debe_detener,
                    mostrar_detalle=mostrar_detalle,
                    modo_origen=modo_origen
                )

                estadisticas = organizador.organizar_archivos()

                self.agregar_log(f"\n✅ PROCESO FINALIZADO", "SUCCESS")
                for categoria in categorias_activas:
                    total = estadisticas.get(categoria["id"], 0)
                    self.agregar_log(f"   📦 {categoria['nombre']}: {total}", "SUCCESS")
                self.agregar_log(f"   📄 Sin categoría (otros formatos): {estadisticas['otros']}", "SUCCESS")
                self.agregar_log(f"   🧹 Carpetas eliminadas: {estadisticas['carpetas_eliminadas']}", "SUCCESS")
                self.agregar_log("="*50, "INFO")

                if not self.proceso_activo:
                    self.agregar_log("⚠ Proceso detenido por el usuario", "WARNING")
                else:
                    resumen = "\n".join(
                        f"{c['nombre']}: {estadisticas.get(c['id'], 0)}" for c in categorias_activas
                    )
                    messagebox.showinfo("Completado",
                        f"Proceso finalizado exitosamente!\n\n"
                        f"{resumen}\n"
                        f"Otros formatos: {estadisticas['otros']}")

            except Exception as e:
                self.agregar_log(f"❌ Error fatal: {e}", "ERROR")
                messagebox.showerror("Error", f"Ocurrió un error:\n{e}")
            finally:
                self._finalizar_proceso()

        threading.Thread(target=ejecutar_organizacion, daemon=True).start()

    def iniciar_organizacion_general(self):
        """Agrupa TODOS los archivos en carpetas numeradas con un único prefijo,
        sin distinguir por tipo/extensión ni usar las categorías configuradas"""
        if self.proceso_activo:
            messagebox.showwarning("Proceso activo", "Ya hay un proceso en ejecución")
            return

        prefijo = self.ventana.prefijo_general.get().strip()
        if not prefijo:
            messagebox.showwarning("Sin prefijo", "Ingresa un prefijo para las carpetas")
            return

        ruta_base = self.ventana.ruta_base.get()
        modo_origen = self.ventana.modo_origen.get()
        confirmar = messagebox.askyesno(
            "Confirmar agrupación general",
            f"Se agruparán TODOS los tipos de archivo en:\n{ruta_base}\n\n"
            f"Prefijo de carpeta: '{prefijo}'\n"
            f"Elementos a organizar: {DESCRIPCION_MODOS_ORIGEN.get(modo_origen, modo_origen)}\n\n"
            f"Esta acción moverá archivos de todos los tipos. ¿Deseas continuar?"
        )
        if not confirmar:
            return

        def ejecutar_organizacion_general():
            try:
                self._iniciar_proceso()
                self.agregar_log("="*50, "INFO")
                self.agregar_log("INICIANDO ORGANIZACIÓN GENERAL (TODOS LOS TIPOS DE ARCHIVO)", "INFO")

                ruta_base = Path(self.ventana.ruta_base.get())
                digitos = self.ventana.digitos.get()
                archivos_por_carpeta = self.ventana.archivos_por_carpeta.get()
                mostrar_detalle = self.ventana.mostrar_detalle.get()
                modo_origen = self.ventana.modo_origen.get()

                self.agregar_log(f"Ruta base: {ruta_base}")
                self.agregar_log(f"Prefijo de carpeta: {prefijo}")
                self.agregar_log(f"Archivos por carpeta: {archivos_por_carpeta}")
                self.agregar_log(f"Elementos a organizar: {DESCRIPCION_MODOS_ORIGEN.get(modo_origen, modo_origen)}")

                organizador = OrganizadorArchivos(
                    ruta_base=ruta_base,
                    categorias=[],
                    digitos=digitos,
                    archivos_por_carpeta=archivos_por_carpeta,
                    callback_log=self.agregar_log,
                    callback_progreso=self._actualizar_progreso,
                    detener_callback=self._debe_detener,
                    mostrar_detalle=mostrar_detalle,
                    modo_origen=modo_origen
                )

                resultado = organizador.organizar_todo(prefijo)

                self.agregar_log(f"\n✅ PROCESO FINALIZADO", "SUCCESS")
                self.agregar_log(f"   📦 Archivos organizados: {resultado['total']}", "SUCCESS")
                self.agregar_log(f"   🧹 Carpetas eliminadas: {resultado['carpetas_eliminadas']}", "SUCCESS")
                self.agregar_log("="*50, "INFO")

                if not self.proceso_activo:
                    self.agregar_log("⚠ Proceso detenido por el usuario", "WARNING")
                else:
                    messagebox.showinfo("Completado",
                        f"Proceso finalizado exitosamente!\n\n"
                        f"Archivos organizados: {resultado['total']}")

            except Exception as e:
                self.agregar_log(f"❌ Error fatal: {e}", "ERROR")
                messagebox.showerror("Error", f"Ocurrió un error:\n{e}")
            finally:
                self._finalizar_proceso()

        threading.Thread(target=ejecutar_organizacion_general, daemon=True).start()

    def detener_proceso(self):
        """Detiene el proceso en ejecución"""
        self.proceso_activo = False
        self.agregar_log("⚠ Deteniendo proceso...", "WARNING")

    def _iniciar_proceso(self):
        """Prepara la interfaz para iniciar un proceso"""
        self.proceso_activo = True
        self.ventana.habilitar_botones(False)
        self.ventana.set_progreso("iniciando")
        self.ventana.set_status("Procesando...")

    def editar_extensiones_categoria(self, categoria_id, nuevas_extensiones):
        """Actualiza las extensiones soportadas de una categoría"""
        extensiones = normalizar_extensiones(nuevas_extensiones)
        for categoria in self.categorias:
            if categoria["id"] == categoria_id:
                categoria["extensiones"] = extensiones
                nombre = categoria["nombre"]
                break
        else:
            return

        self.ventana.actualizar_extensiones_categoria(categoria_id, extensiones)
        self.agregar_log(f"Extensiones de '{nombre}' actualizadas: {', '.join(extensiones)}", "INFO")

        if categoria.get("personalizada"):
            self.persistir_categorias_personalizadas()

    def crear_categoria_personalizada(self, nombre, prefijo, extensiones):
        """Crea una nueva categoría personalizada definida por el usuario"""
        nombre = nombre.strip()
        prefijo = prefijo.strip()
        extensiones = normalizar_extensiones(extensiones)

        if not nombre:
            return False, "El nombre de la categoría no puede estar vacío"
        if not prefijo:
            return False, "El prefijo de carpeta no puede estar vacío"
        if not extensiones:
            return False, "Agrega al menos una extensión de archivo"

        categoria_id = generar_id_categoria(nombre, [c["id"] for c in self.categorias])
        categoria = {
            "id": categoria_id,
            "nombre": nombre,
            "prefijo": prefijo,
            "extensiones": extensiones,
            "activa": True,
            "personalizada": True,
        }
        self.categorias.append(categoria)
        self.ventana.agregar_fila_categoria(categoria)
        self.persistir_categorias_personalizadas()
        self.agregar_log(f"Categoría personalizada '{nombre}' creada", "SUCCESS")
        return True, None

    def eliminar_categoria_personalizada(self, categoria_id):
        """Elimina una categoría personalizada existente"""
        categoria = next((c for c in self.categorias if c["id"] == categoria_id), None)
        if not categoria or not categoria.get("personalizada"):
            return

        self.categorias.remove(categoria)
        self.ventana.eliminar_fila_categoria(categoria_id)
        self.persistir_categorias_personalizadas()
        self.agregar_log(f"Categoría personalizada '{categoria['nombre']}' eliminada", "INFO")

    def persistir_categorias_personalizadas(self):
        """Guarda en disco el estado actual de las categorías personalizadas"""
        personalizadas = []
        for categoria in self.categorias:
            if not categoria.get("personalizada"):
                continue
            personalizadas.append({
                "id": categoria["id"],
                "nombre": categoria["nombre"],
                "prefijo": self.ventana.categoria_prefijo(categoria["id"]) or categoria["prefijo"],
                "extensiones": categoria["extensiones"],
                "activa": self.ventana.categoria_activa(categoria["id"]),
            })
        guardar_categorias_personalizadas(personalizadas)
