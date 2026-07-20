"""Lógica de organización y renombrado de archivos"""

from pathlib import Path
import shutil
from typing import List, Tuple, Callable, Optional
from core.utils import crear_nombre_unico, obtener_archivos_carpeta

class OrganizadorArchivos:
    """Clase encargada de la lógica de organización de archivos"""
    
    def __init__(self, 
                 ruta_base: Path,
                 prefijo: str,
                 digitos: int,
                 imagenes_por_carpeta: int,
                 extensiones: List[str],
                 callback_log: Optional[Callable] = None,
                 callback_progreso: Optional[Callable] = None,
                 detener_callback: Optional[Callable[[], bool]] = None,
                 mostrar_detalle: bool = True):
        """
        Inicializa el organizador
        
        Args:
            ruta_base: Ruta base donde trabajar
            prefijo: Prefijo para nombrar carpetas
            digitos: Número de dígitos para la numeración
            imagenes_por_carpeta: Máximo de imágenes por carpeta
            extensiones: Lista de extensiones soportadas
            callback_log: Función para logging
            callback_progreso: Función para actualizar progreso
            detener_callback: Función que retorna True si se debe detener
            mostrar_detalle: Si se deben mostrar logs detallados
        """
        self.ruta_base = ruta_base
        self.prefijo = prefijo
        self.digitos = digitos
        self.imagenes_por_carpeta = imagenes_por_carpeta
        self.extensiones = extensiones
        self.callback_log = callback_log or print
        self.callback_progreso = callback_progreso or (lambda msg: None)
        self.detener_callback = detener_callback or (lambda: False)
        self.mostrar_detalle = mostrar_detalle
        
        self.estadisticas = {
            "imagenes": 0,
            "otros": 0,
            "carpetas_eliminadas": 0
        }
    
    def renombrar_carpetas(self) -> Tuple[int, int]:
        """
        Renombra carpetas existentes con el prefijo especificado
        
        Returns:
            (carpetas_procesadas, carpetas_renombradas)
        """
        carpetas = sorted([
            c for c in self.ruta_base.iterdir() 
            if c.is_dir() and not c.name.startswith(self.prefijo)
        ])
        
        self._log(f"Encontradas {len(carpetas)} carpetas para renombrar")
        
        procesadas = 0
        renombradas = 0
        
        for i, carpeta in enumerate(carpetas, start=1):
            if self._debe_detener():
                break
                
            numero = str(i).zfill(self.digitos)
            nuevo_nombre = f"{self.prefijo} {numero}"
            ruta_nueva = self.ruta_base / nuevo_nombre
            
            if carpeta != ruta_nueva:
                try:
                    carpeta.rename(ruta_nueva)
                    self._log(f"✓ {carpeta.name} → {nuevo_nombre}", "SUCCESS")
                    renombradas += 1
                except Exception as e:
                    self._log(f"✗ Error renombrando {carpeta.name}: {e}", "ERROR")
            
            procesadas += 1
            self._actualizar_progreso(f"Renombrando carpeta {i} de {len(carpetas)}")
        
        return procesadas, renombradas
    
    def organizar_archivos(self) -> dict:
        """
        Organiza archivos en carpetas según extensión y fecha
        
        Returns:
            Diccionario con estadísticas del proceso
        """
        self._log("Iniciando organización de archivos")
        self._actualizar_progreso("Buscando archivos...")
        
        # Recolectar archivos
        imagenes = []
        otros_archivos = []
        carpetas_revisar = []
        
        for carpeta in sorted(self.ruta_base.iterdir()):
            if self._debe_detener():
                break
            if not carpeta.is_dir() or carpeta.name.startswith(self.prefijo) or carpeta.name == "otros_formatos":
                continue
            
            carpetas_revisar.append(carpeta)
            imagenes_carpeta, otros_carpeta = obtener_archivos_carpeta(carpeta, self.extensiones)
            
            # Añadir fecha de modificación para ordenar
            for img in imagenes_carpeta:
                imagenes.append((img, img.stat().st_mtime))
            otros_archivos.extend(otros_carpeta)
        
        if self._debe_detener():
            return self.estadisticas
        
        self.estadisticas["imagenes"] = len(imagenes)
        self.estadisticas["otros"] = len(otros_archivos)
        
        self._log(f"📸 Imágenes encontradas: {len(imagenes)}")
        self._log(f"📄 Otros archivos: {len(otros_archivos)}")
        
        # Mover otros archivos
        if otros_archivos:
            self._mover_otros_archivos(otros_archivos)
        
        # Mover imágenes
        if imagenes:
            self._mover_imagenes(imagenes)
        
        # Limpiar carpetas vacías
        self._limpiar_carpetas_vacias(carpetas_revisar)
        
        return self.estadisticas
    
    def _mover_otros_archivos(self, archivos: List[Path]):
        """Mueve archivos no imagen a 'otros_formatos/'"""
        carpeta_otros = self.ruta_base / "otros_formatos"
        carpeta_otros.mkdir(exist_ok=True)
        
        self._log(f"\n📁 Moviendo {len(archivos)} archivos a 'otros_formatos/'...")
        
        for i, archivo in enumerate(archivos):
            if self._debe_detener():
                break
            
            destino = crear_nombre_unico(carpeta_otros / archivo.name)
            try:
                shutil.move(str(archivo), str(destino))
                if self.mostrar_detalle:
                    self._log(f"   ✓ {archivo.name} → otros_formatos/", "SUCCESS")
            except Exception as e:
                self._log(f"   ✗ Error con {archivo.name}: {e}", "ERROR")
            
            self._actualizar_progreso(f"Moviendo otros archivos: {i+1}/{len(archivos)}")
    
    def _mover_imagenes(self, imagenes: List[Tuple[Path, float]]):
        """Organiza imágenes en carpetas numeradas"""
        # Ordenar por fecha
        imagenes.sort(key=lambda x: x[1])
        
        self._log(f"\n🖼️  Organizando {len(imagenes)} imágenes...")
        
        idx_carpeta = 1
        contador = 0
        
        for i, (ruta_archivo, _) in enumerate(imagenes):
            if self._debe_detener():
                break
            
            nombre_carpeta = f"{self.prefijo} {str(idx_carpeta).zfill(self.digitos)}"
            ruta_destino = self.ruta_base / nombre_carpeta
            ruta_destino.mkdir(exist_ok=True)
            
            destino_final = crear_nombre_unico(ruta_destino / ruta_archivo.name)
            
            try:
                shutil.move(str(ruta_archivo), str(destino_final))
                if self.mostrar_detalle and i % 10 == 0:  # Mostrar cada 10 para no saturar
                    self._log(f"   ✓ {ruta_archivo.name} → {nombre_carpeta}/", "SUCCESS")
            except Exception as e:
                self._log(f"   ✗ Error con {ruta_archivo.name}: {e}", "ERROR")
                continue
            
            contador += 1
            if contador == self.imagenes_por_carpeta:
                contador = 0
                idx_carpeta += 1
            
            if i % 50 == 0:  # Actualizar cada 50 imágenes
                self._actualizar_progreso(f"Organizando imágenes: {i+1}/{len(imagenes)}")
    
    def _limpiar_carpetas_vacias(self, carpetas: List[Path]):
        """Elimina carpetas vacías"""
        self._log("\n🧹 Limpiando carpetas vacías...")
        
        for carpeta in carpetas:
            if carpeta.exists() and not any(carpeta.iterdir()):
                try:
                    carpeta.rmdir()
                    self._log(f"   ✓ Eliminada: {carpeta.name}", "SUCCESS")
                    self.estadisticas["carpetas_eliminadas"] += 1
                except OSError as e:
                    self._log(f"   ✗ No se pudo eliminar {carpeta.name}: {e}", "ERROR")
    
    def _log(self, mensaje: str, tipo: str = "INFO"):
        """Registra un mensaje en el log"""
        if self.callback_log:
            self.callback_log(mensaje, tipo)
    
    def _actualizar_progreso(self, mensaje: str):
        """Actualiza el mensaje de progreso"""
        if self.callback_progreso:
            self.callback_progreso(mensaje)
    
    def _debe_detener(self) -> bool:
        """Verifica si el proceso debe detenerse"""
        return self.detener_callback() if self.detener_callback else False