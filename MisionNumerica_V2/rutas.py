"""Resolución segura de rutas de recursos (assets) y persistencia de usuario."""

import os
import shutil
import sys
from typing import Optional

BASE_PAQUETE = os.path.dirname(os.path.abspath(__file__))


def _raices_busqueda() -> list[str]:
    raices: list[str] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        raices.append(os.path.join(meipass, "MisionNumerica_V2"))
        raices.append(meipass)
    raices.append(BASE_PAQUETE)
    raices.append(os.path.dirname(BASE_PAQUETE))
    return raices


def obtener_ruta_asset(nombre_archivo: str, *subrutas_extra: str) -> str:
    """Busca un asset dentro de MisionNumerica_V2/assets o en bundles PyInstaller."""
    candidatos = []
    for raiz in _raices_busqueda():
        candidatos.append(os.path.join(raiz, "assets", nombre_archivo))
        if subrutas_extra:
            candidatos.append(os.path.join(raiz, *subrutas_extra))
    for ruta in candidatos:
        if os.path.exists(ruta):
            return ruta
    return candidatos[2] if len(candidatos) > 2 else candidatos[0]


def obtener_directorio_datos() -> str:
    """Devuelve un directorio escribible para progreso y auditoría del estudiante."""
    override = os.environ.get("NAVE_AURORA_DATA_DIR", "").strip()
    if override:
        return os.path.abspath(override)

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return os.path.join(base, "NaveAurora")
    return os.path.join(os.path.expanduser("~"), ".local", "share", "NaveAurora")


def obtener_ruta_progreso(nombre_archivo: str = "progreso_v3.json", directorio: Optional[str] = None) -> str:
    """Resuelve la ruta de guardado en disco con migración automática desde legado."""
    dest_dir = os.path.abspath(directorio) if directorio else obtener_directorio_datos()
    os.makedirs(dest_dir, exist_ok=True)
    destino = os.path.join(dest_dir, nombre_archivo)

    # Si existe un archivo heredado junto al código y aún no existe en LOCALAPPDATA, migrarlo.
    legado = os.path.join(BASE_PAQUETE, nombre_archivo)
    if os.path.abspath(legado) != os.path.abspath(destino) and os.path.exists(legado) and not os.path.exists(destino):
        try:
            shutil.copy2(legado, destino)
        except OSError:
            pass
    return destino
