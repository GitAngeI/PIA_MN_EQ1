"""Gestor de Escenarios Dinámicos según la Sala / Módulo activo y tema visual."""

from typing import Dict, Any, Optional

from .tema import obtener_paleta, obtener_tema_actual


ESCENARIOS_POR_SALA: Dict[int, Dict[str, Any]] = {
    1: {
        "nombre": "Ruta Estelar Dorada",
        "fondo": "#141026",
        "panel": "#20193A",
        "acento": "#FFD166",
        "tipo_efecto": "nebulosa",
        "descripcion": "Sector de navegacion estelar con estrellas de referencia.",
    },
    2: {
        "nombre": "Camara de Propulsores",
        "fondo": "#1B1020",
        "panel": "#2A1830",
        "acento": "#F4A261",
        "tipo_efecto": "propulsion",
        "descripcion": "Zona termica de los motores principales.",
    },
    3: {
        "nombre": "Cinturon de Asteroides",
        "fondo": "#18111E",
        "panel": "#261B2E",
        "acento": "#E76F51",
        "tipo_efecto": "asteroides",
        "descripcion": "Campo de asteroides interfiriendo con la red electrica.",
    },
    4: {
        "nombre": "Orbita Esmeralda",
        "fondo": "#0F1B22",
        "panel": "#172A33",
        "acento": "#5CE0A0",
        "tipo_efecto": "escudos",
        "descripcion": "Planeta esmeralda protegido por campo deflector.",
    },
    5: {
        "nombre": "Planeta Azul Criogenico",
        "fondo": "#10162B",
        "panel": "#192340",
        "acento": "#C09CFF",
        "tipo_efecto": "planeta_azul",
        "descripcion": "Planeta azul y escudos de combustible activados.",
    },
    6: {
        "nombre": "Sector de Radar Profundo",
        "fondo": "#1C1022",
        "panel": "#2B1833",
        "acento": "#FF7B89",
        "tipo_efecto": "radar",
        "descripcion": "Ondas de telemetria y barrido de largo alcance.",
    },
    7: {
        "nombre": "Nucleo Cuantico Central",
        "fondo": "#0E1926",
        "panel": "#16263A",
        "acento": "#7CE0D3",
        "tipo_efecto": "nodos",
        "descripcion": "Red orbital de la computadora central.",
    },
}

ESCENARIOS_POR_SALA_CLARO: Dict[int, Dict[str, Any]] = {
    1: {
        "nombre": "Ruta Estelar Dorada",
        "fondo": "#EEF0F4",
        "panel": "#F7F8FA",
        "acento": "#9A5B00",
        "tipo_efecto": "nebulosa",
        "descripcion": "Sector de navegacion estelar con estrellas de referencia.",
    },
    2: {
        "nombre": "Camara de Propulsores",
        "fondo": "#F0EEF2",
        "panel": "#F8F7FA",
        "acento": "#C25E00",
        "tipo_efecto": "propulsion",
        "descripcion": "Zona termica de los motores principales.",
    },
    3: {
        "nombre": "Cinturon de Asteroides",
        "fondo": "#F1EEF1",
        "panel": "#F9F7F8",
        "acento": "#C84B31",
        "tipo_efecto": "asteroides",
        "descripcion": "Campo de asteroides interfiriendo con la red electrica.",
    },
    4: {
        "nombre": "Orbita Esmeralda",
        "fondo": "#EAEFF1",
        "panel": "#F5F8F9",
        "acento": "#0D7A5F",
        "tipo_efecto": "escudos",
        "descripcion": "Planeta esmeralda protegido por campo deflector.",
    },
    5: {
        "nombre": "Planeta Azul Criogenico",
        "fondo": "#ECEFF5",
        "panel": "#F6F8FB",
        "acento": "#6D3FC0",
        "tipo_efecto": "planeta_azul",
        "descripcion": "Planeta azul y escudos de combustible activados.",
    },
    6: {
        "nombre": "Sector de Radar Profundo",
        "fondo": "#F1EDF2",
        "panel": "#F9F7FA",
        "acento": "#BE2B45",
        "tipo_efecto": "radar",
        "descripcion": "Ondas de telemetria y barrido de largo alcance.",
    },
    7: {
        "nombre": "Nucleo Cuantico Central",
        "fondo": "#EBF0F5",
        "panel": "#F6F9FC",
        "acento": "#0E7490",
        "tipo_efecto": "nodos",
        "descripcion": "Red orbital de la computadora central.",
    },
}


def obtener_escenario(sala_id: int, tema: Optional[str] = None) -> Dict[str, Any]:
    clave = obtener_tema_actual() if tema is None else ("claro" if str(tema).lower() == "claro" else "oscuro")
    if clave == "claro":
        base = ESCENARIOS_POR_SALA_CLARO.get(sala_id, ESCENARIOS_POR_SALA_CLARO[1])
        return dict(base)
    return dict(ESCENARIOS_POR_SALA.get(sala_id, ESCENARIOS_POR_SALA[1]))
