"""Lógica de organización y renombrado de archivos"""

from pathlib import Path
import shutil
from typing import List, Tuple, Callable, Optional, Dict
from core.utils import crear_nombre_unico, clasificar_archivos_carpeta, carpeta_pertenece_a_prefijo
from core.config import CARPETA_OTROS

class OrganizadorArchivos:
    """Clase encargada de la lógica de organización de archivos por categorías"""

    def __init__(self,
                 ruta_base: Path,
                 categorias: List[dict],
                 digitos: int,
                 archivos_por_carpeta: int,
                 callback_log: Optional[Callable] = None,
                 callback_progreso: Optional[Callable] = None,
                 detener_callback: Optional[Callable[[], bool]] = None,
                 mostrar_detalle: bool = True,
                 incluir_archivos_sueltos: bool = False):
        """
        Inicializa el organizador

        Args:
            ruta_base: Ruta base donde trabajar
            categorias: Lista de categorías activas, cada una con
                        'id', 'nombre', 'prefijo' y 'extensiones'
            digitos: Número de dígitos para la numeración de carpetas
            archivos_por_carpeta: Máximo de archivos por carpeta numerada
            callback_log: Función para logging
            callback_progreso: Función para actualizar progreso
            detener_callback: Función que retorna True si se debe detener
            mostrar_detalle: Si se deben mostrar logs detallados
            incluir_archivos_sueltos: Si se deben organizar también los archivos
                                       sueltos directamente en la ruta base (no
                                       dentro de ninguna carpeta)
        """
        self.ruta_base = ruta_base
        self.categorias = categorias
        self.digitos = digitos
        self.archivos_por_carpeta = archivos_por_carpeta
        self.callback_log = callback_log or print
        self.callback_progreso = callback_progreso or (lambda msg: None)
        self.detener_callback = detener_callback or (lambda: False)
        self.mostrar_detalle = mostrar_detalle
        self.incluir_archivos_sueltos = incluir_archivos_sueltos

        # Mapa extensión -> id de categoría, para clasificar en una sola pasada
        self.mapa_extensiones: Dict[str, str] = {}
        for categoria in self.categorias:
            for ext in categoria["extensiones"]:
                self.mapa_extensiones[ext.lower()] = categoria["id"]

        self.estadisticas = {"otros": 0, "carpetas_eliminadas": 0}
        for categoria in self.categorias:
            self.estadisticas[categoria["id"]] = 0

    def _prefijos_activos(self) -> List[str]:
        return [c["prefijo"] for c in self.categorias]

    def renombrar_carpetas(self, prefijo: str) -> Tuple[int, int]:
        """
        Renombra carpetas existentes con el prefijo especificado

        Args:
            prefijo: Prefijo de la categoría a usar para renumerar

        Returns:
            (carpetas_procesadas, carpetas_renombradas)
        """
        carpetas = sorted([
            c for c in self.ruta_base.iterdir()
            if c.is_dir() and not carpeta_pertenece_a_prefijo(c.name, prefijo)
        ])

        self._log(f"Encontradas {len(carpetas)} carpetas para renombrar")

        procesadas = 0
        renombradas = 0

        for i, carpeta in enumerate(carpetas, start=1):
            if self._debe_detener():
                break

            numero = str(i).zfill(self.digitos)
            nuevo_nombre = f"{prefijo} {numero}"
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
        Organiza archivos en carpetas según categoría (extensión) y fecha.
        Todas las categorías activas se procesan en la misma pasada; los
        archivos que no encajen en ninguna van a la carpeta de "otros formatos".

        Returns:
            Diccionario con estadísticas del proceso
        """
        self._log("Iniciando organización de archivos")
        self._actualizar_progreso("Buscando archivos...")

        prefijos_activos = self._prefijos_activos()

        archivos_por_categoria: Dict[str, List[Tuple[Path, float]]] = {c["id"]: [] for c in self.categorias}
        otros_archivos: List[Path] = []
        carpetas_revisar = []

        if self.incluir_archivos_sueltos:
            self._log("📄 Incluyendo también los archivos sueltos en la ruta base")

        for item in sorted(self.ruta_base.iterdir()):
            if self._debe_detener():
                break

            if item.is_dir():
                carpeta = item
                if carpeta.name == CARPETA_OTROS or any(
                        carpeta_pertenece_a_prefijo(carpeta.name, p) for p in prefijos_activos):
                    continue

                carpetas_revisar.append(carpeta)
                clasificados, sin_categoria = clasificar_archivos_carpeta(carpeta, self.mapa_extensiones)

                for id_categoria, archivos in clasificados.items():
                    for archivo in archivos:
                        archivos_por_categoria[id_categoria].append((archivo, archivo.stat().st_mtime))
                otros_archivos.extend(sin_categoria)

            elif self.incluir_archivos_sueltos and item.is_file():
                id_categoria = self.mapa_extensiones.get(item.suffix.lower())
                if id_categoria:
                    archivos_por_categoria[id_categoria].append((item, item.stat().st_mtime))
                else:
                    otros_archivos.append(item)

        if self._debe_detener():
            return self.estadisticas

        self.estadisticas["otros"] = len(otros_archivos)
        for categoria in self.categorias:
            self.estadisticas[categoria["id"]] = len(archivos_por_categoria[categoria["id"]])
            self._log(f"📦 {categoria['nombre']} encontrados: {len(archivos_por_categoria[categoria['id']])}")
        self._log(f"📄 Sin categoría: {len(otros_archivos)}")

        # Mover archivos sin categoría
        if otros_archivos:
            self._mover_otros_archivos(otros_archivos)

        # Mover cada categoría a sus carpetas numeradas
        for categoria in self.categorias:
            if self._debe_detener():
                break
            archivos = archivos_por_categoria[categoria["id"]]
            if archivos:
                self._mover_categoria(categoria, archivos)

        # Limpiar carpetas vacías
        self._limpiar_carpetas_vacias(carpetas_revisar)

        return self.estadisticas

    def _mover_otros_archivos(self, archivos: List[Path]):
        """Mueve archivos sin categoría reconocida a 'otros_formatos/'"""
        carpeta_otros = self.ruta_base / CARPETA_OTROS
        carpeta_otros.mkdir(exist_ok=True)

        self._log(f"\n📁 Moviendo {len(archivos)} archivos a '{CARPETA_OTROS}/'...")

        for i, archivo in enumerate(archivos):
            if self._debe_detener():
                break

            destino = crear_nombre_unico(carpeta_otros / archivo.name)
            try:
                shutil.move(str(archivo), str(destino))
                if self.mostrar_detalle:
                    self._log(f"   ✓ {archivo.name} → {CARPETA_OTROS}/", "SUCCESS")
            except Exception as e:
                self._log(f"   ✗ Error con {archivo.name}: {e}", "ERROR")

            self._actualizar_progreso(f"Moviendo otros archivos: {i+1}/{len(archivos)}")

    def _mover_categoria(self, categoria: dict, archivos: List[Tuple[Path, float]]):
        """Organiza los archivos de una categoría en carpetas numeradas con su propio prefijo"""
        # Ordenar por fecha
        archivos.sort(key=lambda x: x[1])

        nombre = categoria["nombre"]
        prefijo = categoria["prefijo"]

        self._log(f"\n📦 Organizando {len(archivos)} archivos de '{nombre}'...")

        idx_carpeta = 1
        contador = 0

        for i, (ruta_archivo, _) in enumerate(archivos):
            if self._debe_detener():
                break

            nombre_carpeta = f"{prefijo} {str(idx_carpeta).zfill(self.digitos)}"
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
            if contador == self.archivos_por_carpeta:
                contador = 0
                idx_carpeta += 1

            if i % 50 == 0:  # Actualizar cada 50 archivos
                self._actualizar_progreso(f"Organizando {nombre}: {i+1}/{len(archivos)}")

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
