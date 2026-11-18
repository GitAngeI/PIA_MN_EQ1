"""Generador académico parametrizado y reproducible para los 32 métodos oficiales."""

import random
from typing import Any, Dict, Optional

from ..ui.tema import normalizar_nombre_metodo
from .banco_libros import (
    BANCO_PLANTILLAS,
    generar_desde_banco,
    listar_metodos_con_plantillas,
    obtener_plantillas_metodo,
)


def _fmt(v: float, dec: int = 4) -> str:
    txt = f"{v:.{dec}f}"
    return txt.rstrip("0").rstrip(".") if "." in txt else txt


def generar_mision(
    nombre_metodo: str,
    rng: Optional[random.Random] = None,
    seed_id: Optional[str] = None,
    excluir_plantilla_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Genera un problema académico parametrizado (>=2 plantillas por método) con seed_id auditable."""
    return generar_desde_banco(
        nombre_metodo=normalizar_nombre_metodo(nombre_metodo),
        rng=rng,
        seed_id=seed_id,
        excluir_plantilla_id=excluir_plantilla_id,
    )


__all__ = [
    "BANCO_PLANTILLAS",
    "generar_mision",
    "obtener_plantillas_metodo",
    "listar_metodos_con_plantillas",
]
