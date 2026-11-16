"""Fondo animado de galaxia cálida con estrellas y nebulosas en Canvas."""

import random
import tkinter as tk
from .tema import FONDO_GALAXIA, DORADO, AMBAR, CORAL, VIOLETA_SUAVE


class FondoGalaxia(tk.Canvas):
    def __init__(self, master, con_planetas: bool = False, **kwargs):
        super().__init__(master, bg=FONDO_GALAXIA, highlightthickness=0, **kwargs)
        self.con_planetas = con_planetas
        self.estrellas = []
        self.nebulosas = []
        self._iniciado = False
        self.bind("<Configure>", self._al_redimensionar)

    def _al_redimensionar(self, event):
        if event.width < 100 or event.height < 100:
            return
        if not self._iniciado:
            self._iniciado = True
            self._crear_cielo(event.width, event.height)
            self._animar()
        if self.con_planetas:
            self._dibujar_planeta(event.width, event.height)

    def _dibujar_planeta(self, w: int, h: int):
        self.delete("planeta")
        self.create_oval(
            w * 0.62, h * 0.52, w * 1.28, h * 1.32,
            fill="#C8553D", outline="#8B3A20", width=4, tags=("fondo", "planeta"),
        )
        self.create_oval(w * 0.68, h * 0.68, w * 0.77, h * 0.77, fill="#9E3F24", outline="", tags=("fondo", "planeta"))
        self.create_oval(w * 0.82, h * 0.58, w * 0.90, h * 0.66, fill="#9E3F24", outline="", tags=("fondo", "planeta"))
        self.tag_lower("planeta")

    def _crear_cielo(self, w: int, h: int):
        self.delete("fondo")
        rng = random.Random(42)
        colores_neb = ["#2A193D", "#331D38", "#2B1E3E", "#3B2135"]
        for _ in range(7):
            cx = rng.randint(0, max(w, 800))
            cy = rng.randint(0, max(h, 600))
            rx = rng.randint(140, 260)
            ry = rng.randint(90, 180)
            nid = self.create_oval(
                cx - rx, cy - ry, cx + rx, cy + ry,
                fill=rng.choice(colores_neb), outline="", tags="fondo",
            )
            self.nebulosas.append((nid, rng.uniform(0.15, 0.35)))

        paleta_est = ["#FFF5E4", DORADO, AMBAR, CORAL, VIOLETA_SUAVE]
        for _ in range(95):
            x = rng.randint(0, max(w, 1280))
            y = rng.randint(0, max(h, 800))
            r = rng.choice([1, 1, 2, 2, 3])
            vel = rng.uniform(0.2, 0.8)
            eid = self.create_oval(
                x - r, y - r, x + r, y + r,
                fill=rng.choice(paleta_est), outline="", tags="fondo",
            )
            self.estrellas.append((eid, vel, r))

    def _animar(self):
        if not self.winfo_exists():
            return
        w = max(self.winfo_width(), 1200)
        h = max(self.winfo_height(), 800)
        for eid, vel, _ in self.estrellas:
            self.move(eid, -vel, vel * 0.15)
            coords = self.coords(eid)
            if coords and (coords[2] < 0 or coords[1] > h):
                nx = w + 5
                ny = random.randint(0, h)
                tam = coords[2] - coords[0]
                self.coords(eid, nx, ny, nx + tam, ny + tam)
        self.after(45, self._animar)
