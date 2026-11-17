"""Mapa de Progreso Galáctico (pop-up con ruta curva y estrellas .5 reales por sala)."""

import math
import tkinter as tk
from typing import Callable, Optional
from .tema import obtener_paleta, obtener_salas
from .estrellas import dibujar_estrella_canvas
from ..juego.estado import EstadoJuego


class MapaProgresoUI(tk.Toplevel):
    """Ventana modal con animación pop-up y ruta curva de las 7 salas con estrellas (.5)."""

    def __init__(self, master, estado: EstadoJuego, al_seleccionar_sala: Callable[[int], None]):
        super().__init__(master)
        pal = obtener_paleta()
        self.title("Mapa de Progreso Galactico")
        self.configure(bg=pal["fondo"])
        self.transient(master)
        self.grab_set()
        self.estado = estado
        self.al_seleccionar_sala = al_seleccionar_sala
        self._anim_id: Optional[str] = None

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.ancho_meta = max(680, min(int(sw * 0.86), 1140))
        self.alto_meta = max(460, min(int(sh * 0.80), 660))
        self.minsize(min(660, max(540, sw - 60)), min(440, max(380, sh - 80)))
        self._escala = 0.78
        self._actualizar_geometria()

        fuente_top = ("Segoe UI", max(13, min(20, self.ancho_meta // 52)), "bold")
        top = tk.Frame(self, bg=pal["panel"], highlightbackground=pal["titulo"], highlightthickness=2)
        top.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(
            top, text=f"RUTA GALACTICA // {estado.total_estrellas():.1f}/96.0 ESTRELLAS",
            bg=pal["panel"], fg=pal["titulo"], font=fuente_top,
        ).pack(side="left", padx=14, pady=8)
        tk.Button(
            top, text="CERRAR", command=self.destroy,
            bg=pal["acento"], fg=pal["texto_en_acento"], font=("Segoe UI", 12, "bold"), bd=0, padx=14, pady=6, cursor="hand2",
        ).pack(side="right", padx=12, pady=8)

        self.canvas = tk.Canvas(self, bg=pal["fondo"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.canvas.bind("<Configure>", lambda _e: self._dibujar_ruta())
        self.canvas.bind("<Button-1>", self._clic_nodo)
        self.bind("<Destroy>", lambda _e: self._cancelar_anim(), add="+")

        self._animar_popup()

    def _cancelar_anim(self):
        if self._anim_id is not None:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None

    def _actualizar_geometria(self):
        w = int(self.ancho_meta * self._escala)
        h = int(self.alto_meta * self._escala)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _animar_popup(self):
        self._anim_id = None
        if not self.winfo_exists():
            return
        if self._escala < 1.0:
            self._escala = min(1.0, self._escala + 0.08)
            self._actualizar_geometria()
            self._anim_id = self.after(18, self._animar_popup)

    def _posiciones(self, w: int, h: int):
        pts = []
        salas = obtener_salas()
        n = len(salas)
        for i in range(n):
            px = int(w * (0.10 + 0.80 * (i / (n - 1))))
            py = int(h * (0.52 + 0.22 * math.sin(i * 1.15)))
            pts.append((px, py))
        return pts

    def _dibujar_ruta(self):
        pal = obtener_paleta()
        salas = obtener_salas()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 120 or h < 120:
            w, h = max(w, self.ancho_meta - 32), max(h, self.alto_meta - 90)
        self.canvas.configure(bg=pal["fondo"])
        self.canvas.delete("all")
        self._nodos = []
        pts = self._posiciones(w, h)

        flat = []
        for px, py in pts:
            flat.extend([px, py])
        self.canvas.create_line(*flat, smooth=True, fill=pal["borde"], width=max(3, int(w / 180)), dash=(10, 6))

        radio = max(22, min(36, int(min(w / 22.0, h / 11.0))))
        star_r = max(6.5, min(10.0, radio * 0.28))
        star_dx = int(star_r * 2.5)
        f_num = ("Segoe UI", max(12, int(radio * 0.48)), "bold")
        f_nom = ("Segoe UI", max(9, min(12, int(w / 88))), "bold")
        f_sub = ("Segoe UI", max(8, min(11, int(w / 96))), "bold")

        for sid, nombre, color, metodos in salas:
            comp = sum(1 for m in metodos if self.estado.completados.get(m))
            sum_est = sum(self.estado.obtener_estrellas(m) for m in metodos)
            max_est = 3.0 * len(metodos)
            prom_est = self.estado.promedio_estrellas_sala(metodos)
            idx = next(i for i, s in enumerate(salas) if s[0] == sid)
            px, py = pts[idx]

            fill_nodo = color if comp > 0 else pal["mapa_nodo_inactivo"]
            borde = pal["titulo"] if comp == len(metodos) and prom_est == 3.0 else (pal["exito"] if comp == len(metodos) else pal["texto"])

            self.canvas.create_oval(px - radio, py - radio, px + radio, py + radio, fill=fill_nodo, outline=borde, width=3)
            self.canvas.create_text(
                px, py, text=f"0{sid}",
                fill=pal["mapa_texto_activo"] if comp > 0 else pal["texto"],
                font=f_num,
            )

            for s in range(3):
                sx = px + (s - 1) * star_dx
                sy = py - radio - max(14, int(star_r * 1.8))
                if prom_est >= s + 1.0:
                    est_str = "llena"
                elif prom_est >= s + 0.5:
                    est_str = "media"
                else:
                    est_str = "vacia"
                dibujar_estrella_canvas(self.canvas, sx, sy, star_r, est_str)

            self.canvas.create_text(px, py + radio + 16, text=nombre[:16], fill=pal["texto"], font=f_nom)
            self.canvas.create_text(
                px, py + radio + 34,
                text=f"{comp}/{len(metodos)} | {sum_est:.1f}/{max_est:.0f}",
                fill=pal["exito"] if comp == len(metodos) else pal["texto_sec"], font=f_sub,
            )
            self._nodos.append((sid, px, py, radio))

    def _clic_nodo(self, event):
        for sid, px, py, radio in getattr(self, "_nodos", []):
            if (event.x - px) ** 2 + (event.y - py) ** 2 <= (radio + 8) ** 2:
                self.destroy()
                self.al_seleccionar_sala(sid)
                return
