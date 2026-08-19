"""Acciones del controlador que disparan un proceso de organización/renombrado"""

import threading
from pathlib import Path

from core.organizador import OrganizadorArchivos, eliminar_marcadores
from core.modos import DESCRIPCION_MODOS
from core.orden import DESCRIPCION_ORDEN
from core.agrupamiento import DESCRIPCION_AGRUPAMIENTO
from gui.dialogs import mostrar_advertencia, mostrar_error, mostrar_info, confirmar


class OrganizarMixin:
    """Mezclado en AppController: acciones de organizar, renombrar y agrupar todo"""

    def _preguntar_eliminar_marcadores(self, ruta_base: Path):
        """Ofrece borrar los archivos ocultos marcadores recién dejados en las carpetas"""
        if confirmar(
            self.ventana.root, "Archivos ocultos marcadores",
            "El organizador dejó un archivo oculto dentro de cada carpeta que creó o "
            "renombró, para reconocerlas en corridas futuras y no volver a mezclar su "
            "contenido.\n\n¿Deseas eliminar esos archivos ocultos ahora?\n\n"
            "Si los eliminas, una futura organización sobre esta misma ruta podría "
            "volver a escanear esas carpetas."
        ):
            eliminados = eliminar_marcadores(ruta_base)
            self.agregar_log(f"🗑 Archivos ocultos marcadores eliminados: {eliminados}", "INFO")

    def iniciar_renombrado(self):
        """Inicia el proceso de renombrado de carpetas de una categoría"""
        if self.proceso_activo:
            mostrar_advertencia(self.ventana.root, "Proceso activo", "Ya hay un proceso en ejecución")
            return

        if not self._validar_ruta_base():
            return

        prefijo = self.ventana.categoria_renombrado_seleccionada()
        if not prefijo:
            mostrar_advertencia(self.ventana.root, "Sin categoría", "Selecciona una categoría activa para renombrar")
            return

        ruta_base = self.ventana.ruta_base.get()
        if not confirmar(
            self.ventana.root, "Confirmar renombrado",
            f"Se renombrarán las carpetas existentes en:\n{ruta_base}\n\n"
            f"usando el prefijo '{prefijo}'.\n\n¿Deseas continuar?"
        ):
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
                    mostrar_detalle=self.ventana.mostrar_detalle.get(),
                    exclusiones=self.ventana.exclusiones_lista()
                )

                procesadas, renombradas = organizador.renombrar_carpetas(prefijo)

                self.agregar_log(f"\n✅ Renombrado completado. {renombradas} carpetas renombradas.", "SUCCESS")
                self.agregar_log("="*50, "INFO")

                if not self.proceso_activo:
                    self.agregar_log("⚠ Proceso detenido por el usuario", "WARNING")
                elif renombradas:
                    self._preguntar_eliminar_marcadores(ruta_base)

            except Exception as e:
                self.agregar_log(f"❌ Error fatal: {e}", "ERROR")
                mostrar_error(self.ventana.root, "Error", f"Ocurrió un error:\n{e}")
            finally:
                self._finalizar_proceso()

        threading.Thread(target=ejecutar_renombrado, daemon=True).start()

    def iniciar_organizacion(self):
        """Inicia el proceso de organización de archivos"""
        if self.proceso_activo:
            mostrar_advertencia(self.ventana.root, "Proceso activo", "Ya hay un proceso en ejecución")
            return

        if not self._validar_ruta_base():
            return

        categorias_activas = self._categorias_activas()
        if not categorias_activas:
            mostrar_advertencia(self.ventana.root, "Sin categorías", "Activa al menos una categoría para organizar")
            return

        ruta_base = self.ventana.ruta_base.get()
        nombres_categorias = ", ".join(c["nombre"] for c in categorias_activas)
        modo_origen = self.ventana.modo_origen.get()
        orden = self.ventana.orden_archivos.get()
        agrupamiento = self.ventana.agrupamiento.get()
        if not confirmar(
            self.ventana.root, "Confirmar organización",
            f"Se organizarán los archivos en:\n{ruta_base}\n\n"
            f"Categorías activas: {nombres_categorias}\n"
            f"Elementos a organizar: {DESCRIPCION_MODOS.get(modo_origen, modo_origen)}\n"
            f"Orden: {DESCRIPCION_ORDEN.get(orden, orden)}\n"
            f"Agrupamiento: {DESCRIPCION_AGRUPAMIENTO.get(agrupamiento, agrupamiento)}\n\n"
            f"Esta acción moverá archivos y carpetas. ¿Deseas continuar?"
        ):
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
                orden = self.ventana.orden_archivos.get()
                agrupamiento = self.ventana.agrupamiento.get()

                self.agregar_log(f"Ruta base: {ruta_base}")
                self.agregar_log(f"Categorías activas: {', '.join(c['nombre'] for c in categorias_activas)}")
                self.agregar_log(f"Archivos por carpeta: {archivos_por_carpeta}")
                self.agregar_log(f"Mostrar detalles: {mostrar_detalle}")
                self.agregar_log(f"Elementos a organizar: {DESCRIPCION_MODOS.get(modo_origen, modo_origen)}")
                self.agregar_log(f"Orden: {DESCRIPCION_ORDEN.get(orden, orden)}")
                self.agregar_log(f"Agrupamiento: {DESCRIPCION_AGRUPAMIENTO.get(agrupamiento, agrupamiento)}")

                organizador = OrganizadorArchivos(
                    ruta_base=ruta_base,
                    categorias=categorias_activas,
                    digitos=digitos,
                    archivos_por_carpeta=archivos_por_carpeta,
                    callback_log=self.agregar_log,
                    callback_progreso=self._actualizar_progreso,
                    detener_callback=self._debe_detener,
                    mostrar_detalle=mostrar_detalle,
                    modo_origen=modo_origen,
                    orden=orden,
                    agrupamiento=agrupamiento,
                    exclusiones=self.ventana.exclusiones_lista()
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
                    mostrar_info(self.ventana.root, "Completado",
                        f"Proceso finalizado exitosamente!\n\n"
                        f"{resumen}\n"
                        f"Otros formatos: {estadisticas['otros']}")
                    self._preguntar_eliminar_marcadores(ruta_base)

            except Exception as e:
                self.agregar_log(f"❌ Error fatal: {e}", "ERROR")
                mostrar_error(self.ventana.root, "Error", f"Ocurrió un error:\n{e}")
            finally:
                self._finalizar_proceso()

        threading.Thread(target=ejecutar_organizacion, daemon=True).start()

    def iniciar_organizacion_general(self):
        """Agrupa TODOS los archivos en carpetas numeradas con un único prefijo,
        sin distinguir por tipo/extensión ni usar las categorías configuradas"""
        if self.proceso_activo:
            mostrar_advertencia(self.ventana.root, "Proceso activo", "Ya hay un proceso en ejecución")
            return

        if not self._validar_ruta_base():
            return

        prefijo = self.ventana.prefijo_general.get().strip()
        if not prefijo:
            mostrar_advertencia(self.ventana.root, "Sin prefijo", "Ingresa un prefijo para las carpetas")
            return

        ruta_base = self.ventana.ruta_base.get()
        modo_origen = self.ventana.modo_origen.get()
        orden = self.ventana.orden_archivos.get()
        agrupamiento = self.ventana.agrupamiento.get()
        if not confirmar(
            self.ventana.root, "Confirmar agrupación general",
            f"Se agruparán TODOS los tipos de archivo en:\n{ruta_base}\n\n"
            f"Prefijo de carpeta: '{prefijo}'\n"
            f"Elementos a organizar: {DESCRIPCION_MODOS.get(modo_origen, modo_origen)}\n"
            f"Orden: {DESCRIPCION_ORDEN.get(orden, orden)}\n"
            f"Agrupamiento: {DESCRIPCION_AGRUPAMIENTO.get(agrupamiento, agrupamiento)}\n\n"
            f"Esta acción moverá archivos de todos los tipos. ¿Deseas continuar?"
        ):
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
                orden = self.ventana.orden_archivos.get()
                agrupamiento = self.ventana.agrupamiento.get()

                self.agregar_log(f"Ruta base: {ruta_base}")
                self.agregar_log(f"Prefijo de carpeta: {prefijo}")
                self.agregar_log(f"Archivos por carpeta: {archivos_por_carpeta}")
                self.agregar_log(f"Elementos a organizar: {DESCRIPCION_MODOS.get(modo_origen, modo_origen)}")
                self.agregar_log(f"Orden: {DESCRIPCION_ORDEN.get(orden, orden)}")
                self.agregar_log(f"Agrupamiento: {DESCRIPCION_AGRUPAMIENTO.get(agrupamiento, agrupamiento)}")

                organizador = OrganizadorArchivos(
                    ruta_base=ruta_base,
                    categorias=[],
                    digitos=digitos,
                    archivos_por_carpeta=archivos_por_carpeta,
                    callback_log=self.agregar_log,
                    callback_progreso=self._actualizar_progreso,
                    detener_callback=self._debe_detener,
                    mostrar_detalle=mostrar_detalle,
                    modo_origen=modo_origen,
                    orden=orden,
                    agrupamiento=agrupamiento,
                    exclusiones=self.ventana.exclusiones_lista()
                )

                resultado = organizador.organizar_todo(prefijo)

                self.agregar_log(f"\n✅ PROCESO FINALIZADO", "SUCCESS")
                self.agregar_log(f"   📦 Archivos organizados: {resultado['total']}", "SUCCESS")
                self.agregar_log(f"   🧹 Carpetas eliminadas: {resultado['carpetas_eliminadas']}", "SUCCESS")
                self.agregar_log("="*50, "INFO")

                if not self.proceso_activo:
                    self.agregar_log("⚠ Proceso detenido por el usuario", "WARNING")
                else:
                    mostrar_info(self.ventana.root, "Completado",
                        f"Proceso finalizado exitosamente!\n\n"
                        f"Archivos organizados: {resultado['total']}")
                    self._preguntar_eliminar_marcadores(ruta_base)

            except Exception as e:
                self.agregar_log(f"❌ Error fatal: {e}", "ERROR")
                mostrar_error(self.ventana.root, "Error", f"Ocurrió un error:\n{e}")
            finally:
                self._finalizar_proceso()

        threading.Thread(target=ejecutar_organizacion_general, daemon=True).start()
