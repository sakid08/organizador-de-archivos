# core/app.py
"""Controlador principal de la aplicación"""

import threading
from pathlib import Path
from tkinter import messagebox

from core.organizador import OrganizadorArchivos
from core.config import EXTENSIONES_POR_DEFECTO
from core.utils import normalizar_extensiones

class AppController:
    """Controlador de la aplicación"""
    
    def __init__(self, ventana):
        self.ventana = ventana
        self.proceso_activo = False
        self.extensiones = EXTENSIONES_POR_DEFECTO.copy()
        
        # Actualizar extensiones en la interfaz
        self.ventana.actualizar_extensiones(self.extensiones)
    
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
    
    def iniciar_renombrado(self):
        """Inicia el proceso de renombrado de carpetas"""
        if self.proceso_activo:
            messagebox.showwarning("Proceso activo", "Ya hay un proceso en ejecución")
            return
        
        def ejecutar_renombrado():
            try:
                self._iniciar_proceso()
                self.agregar_log("="*50, "INFO")
                self.agregar_log("INICIANDO RENOMBRADO DE CARPETAS", "INFO")
                
                ruta_base = Path(self.ventana.ruta_base.get())
                prefijo = self.ventana.prefijo.get()
                digitos = self.ventana.digitos.get()
                
                self.agregar_log(f"Ruta base: {ruta_base}")
                self.agregar_log(f"Prefijo: {prefijo}")
                
                # Instanciar organizador
                organizador = OrganizadorArchivos(
                    ruta_base=ruta_base,
                    prefijo=prefijo,
                    digitos=digitos,
                    imagenes_por_carpeta=self.ventana.imagenes_por_carpeta.get(),
                    extensiones=self.extensiones,
                    callback_log=self.agregar_log,
                    callback_progreso=self._actualizar_progreso,
                    detener_callback=self._debe_detener,
                    mostrar_detalle=self.ventana.mostrar_detalle.get()
                )
                
                # Ejecutar renombrado
                procesadas, renombradas = organizador.renombrar_carpetas()
                
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
        
        def ejecutar_organizacion():
            try:
                self._iniciar_proceso()
                self.agregar_log("="*50, "INFO")
                self.agregar_log("INICIANDO ORGANIZACIÓN DE ARCHIVOS", "INFO")
                
                ruta_base = Path(self.ventana.ruta_base.get())
                prefijo = self.ventana.prefijo.get()
                digitos = self.ventana.digitos.get()
                imagenes_por_carpeta = self.ventana.imagenes_por_carpeta.get()
                mostrar_detalle = self.ventana.mostrar_detalle.get()
                
                self.agregar_log(f"Ruta base: {ruta_base}")
                self.agregar_log(f"Prefijo: {prefijo}")
                self.agregar_log(f"Imágenes por carpeta: {imagenes_por_carpeta}")
                self.agregar_log(f"Extensiones: {', '.join(self.extensiones)}")
                self.agregar_log(f"Mostrar detalles: {mostrar_detalle}")
                
                # Instanciar organizador
                organizador = OrganizadorArchivos(
                    ruta_base=ruta_base,
                    prefijo=prefijo,
                    digitos=digitos,
                    imagenes_por_carpeta=imagenes_por_carpeta,
                    extensiones=self.extensiones,
                    callback_log=self.agregar_log,
                    callback_progreso=self._actualizar_progreso,
                    detener_callback=self._debe_detener,
                    mostrar_detalle=mostrar_detalle
                )
                
                # Ejecutar organización
                estadisticas = organizador.organizar_archivos()
                
                self.agregar_log(f"\n✅ PROCESO FINALIZADO", "SUCCESS")
                self.agregar_log(f"   📸 Imágenes organizadas: {estadisticas['imagenes']}", "SUCCESS")
                self.agregar_log(f"   📄 Otros archivos movidos: {estadisticas['otros']}", "SUCCESS")
                self.agregar_log(f"   📁 Carpetas eliminadas: {estadisticas['carpetas_eliminadas']}", "SUCCESS")
                self.agregar_log("="*50, "INFO")
                
                if not self.proceso_activo:
                    self.agregar_log("⚠ Proceso detenido por el usuario", "WARNING")
                else:
                    messagebox.showinfo("Completado", 
                        f"Proceso finalizado exitosamente!\n\n"
                        f"Imágenes organizadas: {estadisticas['imagenes']}\n"
                        f"Otros archivos: {estadisticas['otros']}")
                
            except Exception as e:
                self.agregar_log(f"❌ Error fatal: {e}", "ERROR")
                messagebox.showerror("Error", f"Ocurrió un error:\n{e}")
            finally:
                self._finalizar_proceso()
        
        threading.Thread(target=ejecutar_organizacion, daemon=True).start()
    
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
    
    def editar_extensiones(self, nuevas_extensiones):
        """Actualiza las extensiones soportadas"""
        self.extensiones = normalizar_extensiones(nuevas_extensiones)
        self.ventana.actualizar_extensiones(self.extensiones)
        self.agregar_log(f"Extensiones actualizadas: {', '.join(self.extensiones)}", "INFO")