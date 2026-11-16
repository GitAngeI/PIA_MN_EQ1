"""Sprite animado 24fps del personaje Tiny Astronaut basado en la textura Meshy AI del usuario."""

import os
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageTk


from ..rutas import obtener_ruta_asset


RUTA_TEXTURA_MESHY = obtener_ruta_asset(
    "tiny_astronaut_meshy.png",
    "Meshy_AI_Tiny_Astronaut_20261113_animated_meshyrig_24fps_Walking_Woman",
    "Meshy_AI_Tiny_Astronaut_20261113_animated_meshyrig_24fps_Walking_Woman.png",
)


def _extraer_paleta_meshy() -> Tuple[str, str, str, str]:
    """Extrae colores base de la textura PNG de Meshy AI con fallback seguro."""
    default = ("#C8BCBA", "#978279", "#886047", "#1F1F21")
    if not os.path.exists(RUTA_TEXTURA_MESHY):
        return default
    try:
        with Image.open(RUTA_TEXTURA_MESHY) as origen:
            img = origen.convert("RGB").resize((48, 48))
        q = img.quantize(colors=6).convert("RGB")
        cols = sorted(q.getcolors(48 * 48), reverse=True)
        hexes = [f"#{r:02X}{g:02X}{b:02X}" for _, (r, g, b) in cols]
        claro = next((c for c in hexes if int(c[1:3], 16) > 170), default[0])
        medio = next((c for c in hexes if 120 <= int(c[1:3], 16) <= 170), default[1])
        cobre = next((c for c in hexes if int(c[1:3], 16) > int(c[5:7], 16) + 25), default[2])
        oscuro = next((c for c in hexes if int(c[1:3], 16) < 60), default[3])
        return claro, medio, cobre, oscuro
    except Exception:
        return default


def generar_frames_astronauta(tam: int = 76) -> List[ImageTk.PhotoImage]:
    """Genera 4 frames de caminata de la Ingeniera Espacial (diseño Tiny Astronaut Woman de Meshy)."""
    traje, sombra, cobre, oscuro = _extraer_paleta_meshy()
    frames: List[ImageTk.PhotoImage] = []
    desplazamientos = [(0, 0, 0), (-3, 4, -4), (0, 0, 0), (-2, -4, 4)]

    for bob, pie_izq, pie_der in desplazamientos:
        img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx = tam // 2
        cy = tam // 2 + 4 + bob

        # Sombra en el piso
        d.ellipse([cx - 18, tam - 12, cx + 18, tam - 3], fill=(10, 8, 20, 170))
        # Mochila espacial cobre (Meshy)
        d.rounded_rectangle([cx - 24, cy - 10, cx - 10, cy + 16], radius=5, fill=cobre, outline=oscuro, width=2)
        # Piernas animadas con botas oscuras
        d.rounded_rectangle([cx - 12, cy + 12, cx - 2, cy + 28 + pie_izq], radius=4, fill=sombra, outline=oscuro, width=2)
        d.rounded_rectangle([cx + 2, cy + 12, cx + 12, cy + 28 + pie_der], radius=4, fill=sombra, outline=oscuro, width=2)
        d.rectangle([cx - 13, cy + 22 + pie_izq, cx - 1, cy + 28 + pie_izq], fill=oscuro)
        d.rectangle([cx + 1, cy + 22 + pie_der, cx + 13, cy + 28 + pie_der], fill=oscuro)
        # Cuerpo/traje femenino estilizado (paleta Meshy)
        d.ellipse([cx - 16, cy - 14, cx + 16, cy + 20], fill=traje, outline=oscuro, width=2)
        # Cinturon cobre de ingeniera
        d.rectangle([cx - 14, cy + 4, cx + 14, cy + 9], fill=cobre, outline=oscuro, width=1)
        # Casco espacial redondo + visor
        d.ellipse([cx - 17, cy - 30, cx + 17, cy - 2], fill=traje, outline=oscuro, width=2)
        d.ellipse([cx - 2, cy - 23, cx + 15, cy - 10], fill="#89E5FF", outline=oscuro, width=2)
        d.ellipse([cx + 3, cy - 21, cx + 11, cy - 16], fill="#FFFFFF")
        # Casco de ingeniera amarillo sobre el casco espacial
        d.chord([cx - 17, cy - 36, cx + 17, cy - 14], start=180, end=360, fill="#FFD166", outline=oscuro, width=2)
        d.rectangle([cx - 19, cy - 26, cx + 19, cy - 22], fill="#F4A261", outline=oscuro, width=1)

        frames.append(ImageTk.PhotoImage(img))
    return frames
