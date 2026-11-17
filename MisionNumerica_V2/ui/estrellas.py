"""Renderizado vectorial de estrellas (completa, media .5 y vacía) en Tkinter Canvas."""

import math
import tkinter as tk
from typing import Optional
from .tema import PANEL_OSCURO, obtener_paleta


def dibujar_estrella_canvas(
    canvas: tk.Canvas,
    cx: float,
    cy: float,
    radio: float,
    estado: str,
    tema: Optional[str] = None,
) -> None:
    """Dibuja en `canvas` una estrella 'llena', 'media' (.5 izquierda) o 'vacia'."""
    pal = obtener_paleta(tema)
    col_llena = pal["estrella_llena"]
    col_borde = pal["estrella_borde"]
    col_vacia_fill = pal["estrella_vacia_fill"]
    col_vacia_borde = pal["estrella_vacia_borde"]

    r_int = radio * 0.44
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r_act = radio if i % 2 == 0 else r_int
        pts.extend([cx + r_act * math.cos(ang), cy + r_act * math.sin(ang)])

    if estado == "llena":
        canvas.create_polygon(pts, fill=col_llena, outline=col_borde, width=1.5)
        return

    # Base vacía (también sirve de mitad derecha apagada en modo 'media')
    canvas.create_polygon(pts, fill=col_vacia_fill, outline=col_vacia_borde, width=1.4)
    if estado != "media":
        return

    # Vértices exactos de la mitad izquierda de la estrella (corte vertical por cx)
    # Orden: 0 (arriba centro), 9 (valles sup-izq), 8 (punta sup-izq), 7 (valles med-izq),
    #        6 (punta inf-izq), 5 (valle inf centro) -> cierra exacto por eje x=cx.
    pts_izq = []
    for idx in (0, 9, 8, 7, 6, 5):
        pts_izq.extend([pts[2 * idx], pts[2 * idx + 1]])
    canvas.create_polygon(pts_izq, fill=col_llena, outline=col_borde, width=1.4)


class EstrellasCanvas(tk.Canvas):
    """Widget compacto que muestra de 0.0 a 3.0 estrellas con incrementos de 0.5."""

    def __init__(
        self,
        master,
        valor: float = 0.0,
        maximo: int = 3,
        radio: int = 11,
        espaciado: int = 26,
        bg: Optional[str] = None,
        **kwargs,
    ):
        pal = obtener_paleta()
        bg_eff = bg if bg is not None else pal["panel"]
        ancho = max(maximo * espaciado + 8, 60)
        alto = max(radio * 2 + 10, 28)
        super().__init__(master, width=ancho, height=alto, bg=bg_eff, highlightthickness=0, **kwargs)
        self.maximo = maximo
        self.radio = radio
        self.espaciado = espaciado
        self.valor = 0.0
        self.actualizar(valor)

    def aplicar_tema(self, bg: Optional[str] = None) -> None:
        pal = obtener_paleta()
        self.configure(bg=bg if bg is not None else pal["panel"])
        self.actualizar(self.valor)

    def actualizar(self, valor: float) -> None:
        val_cuant = round(max(0.0, min(float(self.maximo), float(valor))) * 2.0) / 2.0
        self.valor = val_cuant
        self.delete("all")
        cy = self.radio + 4
        inicio_x = self.radio + 5
        for i in range(self.maximo):
            cx = inicio_x + i * self.espaciado
            if val_cuant >= i + 1.0:
                estado = "llena"
            elif val_cuant >= i + 0.5:
                estado = "media"
            else:
                estado = "vacia"
            dibujar_estrella_canvas(self, cx, cy, self.radio, estado)
