"""Mapa interactivo vectorial de la Nave Aurora (sin dependencia de imagen raster)."""

import math
import random
import tkinter as tk
from typing import Callable, Dict, List, Optional, Tuple

from ..juego.estado import EstadoJuego
from .astronauta_sprite import generar_frames_astronauta
from .estrellas import dibujar_estrella_canvas
from .tema import (
    FUENTE_MONO,
    FUENTE_UI,
    obtener_paleta,
    obtener_salas,
)

# Coordenadas normalizadas (cx, cy, rw, rh) dentro del plano vector 16:9 de la Nave Aurora
SALAS_LAYOUT: Dict[int, Tuple[float, float, float, float]] = {
    2: (0.240, 0.285, 0.088, 0.125),  # 02. Motores Principales
    3: (0.240, 0.715, 0.088, 0.125),  # 03. Red Eléctrica
    7: (0.455, 0.500, 0.086, 0.130),  # 07. Computadora Central
    6: (0.640, 0.275, 0.086, 0.122),  # 06. Telemetría y Radares
    5: (0.625, 0.735, 0.086, 0.122),  # 05. Tanques de Combustible
    4: (0.798, 0.715, 0.076, 0.118),  # 04. Escudos Defensivos
    1: (0.860, 0.440, 0.080, 0.120),  # 01. Sistema de Navegación
}

NOMBRES_CORTOS_MAPA: Dict[int, str] = {
    1: "01. NAVEGACION",
    2: "02. MOTORES",
    3: "03. RED ELECT.",
    4: "04. ESCUDOS",
    5: "05. COMBUSTIBLE",
    6: "06. TELEMETRIA",
    7: "07. COMPUTADORA",
}

PASILLOS_NAVE: Tuple[Tuple[int, int], ...] = (
    (2, 7),
    (3, 7),
    (2, 6),
    (3, 5),
    (7, 6),
    (7, 5),
    (7, 1),
    (6, 1),
    (5, 4),
    (4, 1),
)


class MapaNaveAurora(tk.Canvas):
    """Canvas interactivo con el plano arquitectónico vectorial de la Nave Aurora."""

    def __init__(
        self,
        master,
        estado: EstadoJuego,
        al_entrar_sala: Callable[[int], None],
        al_cambiar_sala: Optional[Callable[[int], None]] = None,
        **kwargs,
    ):
        pal = obtener_paleta()
        kwargs.setdefault("bg", pal["mapa_bg"])
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)
        self.estado = estado
        self.al_entrar_sala = al_entrar_sala
        self.al_cambiar_sala = al_cambiar_sala

        self.sala_actual = 7
        self.sala_hover: Optional[int] = None
        self.caminando = False
        self.paso_anim = 0
        self.px = 0.0
        self.py = 0.0
        self.tx = 0.0
        self.ty = 0.0
        self._abrir_al_llegar = False
        self._anim_id: Optional[str] = None
        self._tick_fx = 0
        self._ultimo_tamano: Tuple[int, int] = (0, 0)

        # Estrellas/nodos de fondo deterministas (normalizadas 0..1)
        rng = random.Random(42)
        self._estrellas_bg: List[Tuple[float, float, float, int]] = [
            (
                rng.random(),
                rng.random(),
                rng.choice([1.0, 1.3, 1.8, 2.3]),
                rng.randrange(5),
            )
            for _ in range(95)
        ]

        # Caché de frames del astronauta indexado por tamaño entero
        self._frames_cache: Dict[int, list] = {}
        self._tam_sprite_actual = 0
        self._sprite_size_base = 56
        self.frames = self._obtener_frames(self._sprite_size_base)

        self.bind("<Configure>", self._al_redimensionar)
        self.bind("<Map>", lambda _e: self._al_redimensionar(), add="+")
        self.bind("<Motion>", self._al_mover)
        self.bind("<Leave>", self._al_salir_cursor)
        self.bind("<Button-1>", self._al_clic)
        self.bind("<Destroy>", lambda _e: self._cancelar_anim(), add="+")
        self._bucle_animacion()

    def _cancelar_anim(self):
        if self._anim_id is not None:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None

    def _obtener_frames(self, tamano: int):
        bucket = max(38, min(72, (tamano // 6) * 6))
        if bucket not in self._frames_cache:
            self._frames_cache[bucket] = generar_frames_astronauta(bucket)
        self._tam_sprite_actual = bucket
        return self._frames_cache[bucket]

    def _al_redimensionar(self, event=None):
        w = event.width if event else self.winfo_width()
        h = event.height if event else self.winfo_height()
        if w < 60 or h < 60:
            return
        if (w, h) != self._ultimo_tamano:
            self._ultimo_tamano = (w, h)
            self._redibujar()

    def _al_salir_cursor(self, _event=None):
        if self.sala_hover is not None:
            self.sala_hover = None
            self.config(cursor="")
            self._redibujar()

    def _caja_nave(self) -> Tuple[float, float, float, float]:
        """Calcula la caja centrada 16:9 aprovechando el espacio superior liberado."""
        w = max(self.winfo_width(), 320)
        h = max(self.winfo_height(), 220)
        pad_x = max(10.0, w * 0.015)
        pad_top = max(14.0, h * 0.025)
        pad_bot = max(44.0, h * 0.082)
        disp_w = max(240.0, w - 2.0 * pad_x)
        disp_h = max(160.0, h - pad_top - pad_bot)

        aspecto = 16.0 / 9.0
        if disp_w / disp_h > aspecto:
            bh = disp_h
            bw = bh * aspecto
        else:
            bw = disp_w
            bh = bw / aspecto

        ox = (w - bw) / 2.0
        oy = pad_top + (disp_h - bh) / 2.0
        return ox, oy, bw, bh

    def _pt(self, nx: float, ny: float, ox: float, oy: float, bw: float, bh: float) -> Tuple[float, float]:
        return ox + nx * bw, oy + ny * bh

    def _poly(self, coords_norm: List[Tuple[float, float]], ox: float, oy: float, bw: float, bh: float) -> List[float]:
        out: List[float] = []
        for nx, ny in coords_norm:
            out.extend((ox + nx * bw, oy + ny * bh))
        return out

    def _rect_sala(self, sala_id: int) -> Tuple[float, float, float, float, float, float]:
        ox, oy, bw, bh = self._caja_nave()
        nx, ny, rw, rh = SALAS_LAYOUT[sala_id]
        cx, cy = ox + nx * bw, oy + ny * bh
        hx, hy = rw * bw, rh * bh
        return cx, cy, cx - hx, cy - hy, cx + hx, cy + hy

    def aplicar_tema(self):
        pal = obtener_paleta()
        self.configure(bg=pal["mapa_bg"])
        self._redibujar()

    def _redibujar(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 60 or h < 60:
            return
        pal = obtener_paleta()
        self.configure(bg=pal["mapa_bg"])
        self.delete("all")

        ox, oy, bw, bh = self._caja_nave()
        sprite_tam = max(40, min(68, int(min(bw, bh) * 0.115)))
        self.frames = self._obtener_frames(sprite_tam)

        self._dibujar_espacio(w, h)
        self._dibujar_casco_nave(ox, oy, bw, bh)
        self._dibujar_pasillos(ox, oy, bw, bh)
        self._dibujar_efectos_animados(ox, oy, bw, bh)
        self._dibujar_salas_vectoriales(ox, oy, bw, bh)
        self._dibujar_barra_progreso(w, h)

        cx, cy, _, _, _, _ = self._rect_sala(self.sala_actual)
        if not self.caminando or self.px == 0.0:
            self.px, self.py = cx, cy
            self.tx, self.ty = cx, cy
        else:
            self.tx, self.ty = cx, cy
        self._dibujar_ingeniero(self.px, self.py)

    def _dibujar_espacio(self, w: int, h: int):
        pal = obtener_paleta()
        est_pal = pal["mapa_estrellas"]
        # Halos sutiles de nebulosa
        self.create_oval(
            w * 0.06, h * 0.08, w * 0.55, h * 0.72,
            fill=pal["mapa_neb1"], outline="", tags="ship_static",
        )
        self.create_oval(
            w * 0.48, h * 0.25, w * 0.96, h * 0.94,
            fill=pal["mapa_neb2"], outline="", tags="ship_static",
        )
        for sx, sy, sr, col_idx in self._estrellas_bg:
            x, y = sx * w, sy * h
            col = est_pal[col_idx % len(est_pal)] if isinstance(col_idx, int) else col_idx
            self.create_oval(x - sr, y - sr, x + sr, y + sr, fill=col, outline="", tags="ship_static")

    def _dibujar_casco_nave(self, ox: float, oy: float, bw: float, bh: float):
        pal = obtener_paleta()
        # Aletas estabilizadoras superior e inferior
        aleta_sup = [
            (0.28, 0.12), (0.37, 0.03), (0.60, 0.03), (0.66, 0.11),
        ]
        aleta_inf = [
            (0.28, 0.88), (0.37, 0.97), (0.60, 0.97), (0.66, 0.89),
        ]
        self.create_polygon(
            *self._poly(aleta_sup, ox, oy, bw, bh),
            fill=pal["mapa_aleta"], outline=pal["borde"], width=2, tags="ship_static",
        )
        self.create_polygon(
            *self._poly(aleta_inf, ox, oy, bw, bh),
            fill=pal["mapa_aleta"], outline=pal["borde"], width=2, tags="ship_static",
        )
        # Luces de navegación en puntas de ala (rojo babor / esmeralda estribor)
        lx1, ly1 = self._pt(0.375, 0.035, ox, oy, bw, bh)
        lx2, ly2 = self._pt(0.375, 0.965, ox, oy, bw, bh)
        self.create_oval(lx1 - 4, ly1 - 4, lx1 + 4, ly1 + 4, fill=pal["alerta"], outline="", tags="ship_static")
        self.create_oval(lx2 - 4, ly2 - 4, lx2 + 4, ly2 + 4, fill=pal["exito"], outline="", tags="ship_static")

        # Silueta principal del casco exterior de la Nave Aurora
        casco_ext = [
            (0.112, 0.245),
            (0.145, 0.128),
            (0.230, 0.095),
            (0.680, 0.092),
            (0.840, 0.165),
            (0.945, 0.285),
            (0.980, 0.440),
            (0.962, 0.580),
            (0.912, 0.785),
            (0.855, 0.885),
            (0.665, 0.912),
            (0.220, 0.905),
            (0.142, 0.870),
            (0.112, 0.755),
            (0.096, 0.500),
        ]
        self.create_polygon(
            *self._poly(casco_ext, ox, oy, bw, bh),
            smooth=True, fill=pal["mapa_casco_fill"], outline=pal["mapa_casco_borde"], width=3, tags="ship_static",
        )

        # Cubierta interior presurizada (zona de trabajo)
        casco_int = [
            (0.132, 0.260),
            (0.160, 0.152),
            (0.240, 0.122),
            (0.675, 0.120),
            (0.825, 0.190),
            (0.928, 0.305),
            (0.960, 0.445),
            (0.940, 0.575),
            (0.892, 0.768),
            (0.838, 0.858),
            (0.660, 0.882),
            (0.235, 0.878),
            (0.160, 0.845),
            (0.132, 0.740),
            (0.118, 0.500),
        ]
        self.create_polygon(
            *self._poly(casco_int, ox, oy, bw, bh),
            smooth=True, fill=pal["mapa_cubierta_fill"], outline=pal["borde"], width=2, tags="ship_static",
        )

        # Rejilla metálica sutil dentro del piso de la cubierta
        for i in range(1, 14):
            gx = 0.14 + i * 0.056
            x0, y0 = self._pt(gx, 0.17, ox, oy, bw, bh)
            x1, y1 = self._pt(gx, 0.83, ox, oy, bw, bh)
            self.create_line(x0, y0, x1, y1, fill=pal["mapa_rejilla"], width=1, tags="ship_static")
        for j in range(1, 7):
            gy = 0.16 + j * 0.11
            x0, y0 = self._pt(0.16, gy, ox, oy, bw, bh)
            x1, y1 = self._pt(0.89, gy, ox, oy, bw, bh)
            self.create_line(x0, y0, x1, y1, fill=pal["mapa_rejilla"], width=1, tags="ship_static")

        # Bloque de proa / cúpula de observación
        visera = [
            (0.950, 0.375), (0.976, 0.442), (0.955, 0.515), (0.942, 0.445),
        ]
        self.create_polygon(
            *self._poly(visera, ox, oy, bw, bh),
            smooth=True, fill=pal["mapa_visera_fill"], outline=pal["mapa_visera_borde"], width=1, tags="ship_static",
        )

        # 3 toberas metálicas traseras en popa (izquierda)
        for ty in (0.295, 0.500, 0.705):
            nx0, ny0 = self._pt(0.058, ty - 0.068, ox, oy, bw, bh)
            nx1, ny1 = self._pt(0.116, ty + 0.068, ox, oy, bw, bh)
            self.create_rectangle(
                nx0, ny0, nx1, ny1,
                fill=pal["mapa_tobera_fill"], outline=pal["mapa_tobera_borde"], width=2, tags="ship_static",
            )
            rx0, ry0 = self._pt(0.054, ty - 0.052, ox, oy, bw, bh)
            rx1, ry1 = self._pt(0.068, ty + 0.052, ox, oy, bw, bh)
            self.create_oval(
                rx0, ry0, rx1, ry1,
                fill=pal["mapa_tobera_core"], outline=pal["mapa_tobera_core_borde"], width=1, tags="ship_static",
            )

    def _dibujar_pasillos(self, ox: float, oy: float, bw: float, bh: float):
        pal = obtener_paleta()
        ancho_ext = max(10, int(min(bw, bh) * 0.036))
        ancho_int = max(6, int(ancho_ext * 0.62))
        ancho_luz = max(2, int(ancho_ext * 0.14))

        for a, b in PASILLOS_NAVE:
            ax, ay = self._pt(SALAS_LAYOUT[a][0], SALAS_LAYOUT[a][1], ox, oy, bw, bh)
            bx, by = self._pt(SALAS_LAYOUT[b][0], SALAS_LAYOUT[b][1], ox, oy, bw, bh)
            self.create_line(ax, ay, bx, by, fill=pal["mapa_pasillo_ext"], width=ancho_ext, capstyle="round", tags="ship_static")
            self.create_line(ax, ay, bx, by, fill=pal["mapa_pasillo_int"], width=ancho_int, capstyle="round", tags="ship_static")
            self.create_line(
                ax, ay, bx, by,
                fill=pal["mapa_pasillo_luz"], width=ancho_luz, dash=(8, 8), capstyle="round", tags="ship_static",
            )

    def _dibujar_efectos_animados(self, ox: float, oy: float, bw: float, bh: float):
        """Dibuja llamas de plasma en los propulsores y barrido radar sin regenerar todo el casco."""
        self.delete("fx_anim")
        if bw <= 0 or bh <= 0:
            return
        pal = obtener_paleta()
        pulso = 0.015 * math.sin(self._tick_fx * 0.35)
        for idx, ty in enumerate((0.295, 0.500, 0.705)):
            largo = 0.068 + (0.012 if idx == 1 else 0.0) + pulso * (1.2 if idx % 2 == 0 else -1.0)
            cola_ext = [
                (0.054, ty - 0.052),
                (max(0.002, 0.054 - largo * 1.15), ty),
                (0.054, ty + 0.052),
            ]
            cola_int = [
                (0.056, ty - 0.028),
                (max(0.010, 0.056 - largo * 0.72), ty),
                (0.056, ty + 0.028),
            ]
            self.create_polygon(
                *self._poly(cola_ext, ox, oy, bw, bh),
                smooth=True, fill=pal["mapa_llama_ext"], outline="", tags="fx_anim",
            )
            self.create_polygon(
                *self._poly(cola_int, ox, oy, bw, bh),
                smooth=True, fill=pal["mapa_llama_int"], outline="", tags="fx_anim",
            )

        # Rayo sutil rotatorio en sala 6 (Telemetría) si existe en canvas
        cx6, cy6, _, _, _, _ = self._rect_sala(6)
        radio_radar = max(10.0, min(bw, bh) * 0.042)
        ang = (self._tick_fx * 0.14) % (2 * math.pi)
        rx = cx6 + radio_radar * math.cos(ang)
        ry = cy6 + radio_radar * math.sin(ang)
        self.create_line(cx6, cy6, rx, ry, fill=pal["salas_acento"][6], width=2, tags="fx_anim")

        # Mantener orden de capas limpio: espacio/casco/pasillos -> fx -> salas/estrellas -> ingeniero
        try:
            self.tag_lower("fx_anim")
            self.tag_lower("ship_static")
            self.tag_raise("fx_anim", "ship_static")
            self.tag_raise("ingeniero")
        except tk.TclError:
            pass

    def _dibujar_interior_sala(
        self, sid: int, x0: float, y0: float, x1: float, y1: float, acento: str, completa: bool
    ):
        """Dibuja detalle esquemático de ingeniería dentro de cada módulo."""
        pal = obtener_paleta()
        w_box = x1 - x0
        h_box = y1 - y0
        cx = (x0 + x1) / 2.0
        cy = y0 + h_box * 0.56
        dim = min(w_box, h_box)

        if sid == 1:  # Navegación: consola puente semicircular
            r = dim * 0.34
            self.create_arc(
                cx - r, cy - r * 0.7, cx + r, cy + r * 0.7,
                start=-75, extent=150, style="arc", outline=pal["mapa_interior_1_arc"], width=max(2, int(dim * 0.045)),
                tags="sala_layer",
            )
            self.create_oval(
                cx - r * 0.28, cy - r * 0.22, cx + r * 0.28, cy + r * 0.22,
                fill=pal["mapa_interior_1"], outline=acento, width=2, tags="sala_layer",
            )
        elif sid == 2:  # Motores: doble núcleo de reactor térmico
            rw = dim * 0.21
            for dx in (-dim * 0.22, dim * 0.22):
                self.create_oval(
                    cx + dx - rw, cy - rw, cx + dx + rw, cy + rw,
                    fill=pal["mapa_interior_2"], outline=pal["acento"], width=2, tags="sala_layer",
                )
                self.create_oval(
                    cx + dx - rw * 0.45, cy - rw * 0.45, cx + dx + rw * 0.45, cy + rw * 0.45,
                    fill=pal["titulo"], outline="", tags="sala_layer",
                )
        elif sid == 3:  # Red Eléctrica: cables trifásicos + nodo voltios
            for idx, col in enumerate((pal["alerta"], pal["acento"], pal["mapa_visera_fill"])):
                lx = cx + (idx - 1) * dim * 0.22
                self.create_line(
                    lx, cy - dim * 0.26, lx, cy + dim * 0.26,
                    fill=col, width=max(2, int(dim * 0.04)), tags="sala_layer",
                )
            self.create_rectangle(
                cx - dim * 0.28, cy - dim * 0.14, cx + dim * 0.28, cy + dim * 0.14,
                fill=pal["mapa_interior_3"], outline=acento, width=2, tags="sala_layer",
            )
        elif sid == 4:  # Escudos Defensivos: emisor hexagonal esmeralda
            r = dim * 0.30
            pts_hex = []
            for k in range(6):
                a = math.radians(60 * k)
                pts_hex.extend((cx + r * math.cos(a), cy + r * math.sin(a)))
            self.create_polygon(
                *pts_hex, fill=pal["mapa_interior_4"], outline=pal["exito"], width=2, tags="sala_layer",
            )
            self.create_oval(
                cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35,
                fill=pal["exito"] if completa else pal["mapa_interior_1_arc"], outline="", tags="sala_layer",
            )
        elif sid == 5:  # Tanques de Combustible: celdas criogénicas verticales
            tw = dim * 0.18
            th = dim * 0.27
            for dx in (-dim * 0.22, dim * 0.22):
                self.create_rectangle(
                    cx + dx - tw, cy - th, cx + dx + tw, cy + th,
                    fill=pal["mapa_interior_5"], outline=pal["violeta"], width=2, tags="sala_layer",
                )
                self.create_rectangle(
                    cx + dx - tw * 0.65, cy, cx + dx + tw * 0.65, cy + th * 0.78,
                    fill=pal["violeta"], outline="", tags="sala_layer",
                )
        elif sid == 6:  # Telemetría: plato de radar concéntrico
            r = dim * 0.32
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=pal["mapa_interior_6"], outline=pal["salas_acento"][6], width=2, tags="sala_layer")
            self.create_oval(
                cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5,
                fill="", outline=pal["mapa_interior_6_ring"], width=1, tags="sala_layer",
            )
        elif sid == 7:  # Computadora Central: núcleo de servidores y terminal central
            sw = dim * 0.15
            sh = dim * 0.26
            self.create_rectangle(
                cx - dim * 0.36, cy - sh, cx - dim * 0.20, cy + sh,
                fill=pal["mapa_interior_7a"], outline=pal["mapa_pasillo_luz"], width=1, tags="sala_layer",
            )
            self.create_rectangle(
                cx + dim * 0.20, cy - sh, cx + dim * 0.36, cy + sh,
                fill=pal["mapa_interior_7a"], outline=pal["mapa_pasillo_luz"], width=1, tags="sala_layer",
            )
            self.create_rectangle(
                cx - sw, cy - sw * 0.85, cx + sw, cy + sw * 0.85,
                fill=pal["mapa_interior_7b"], outline=pal["salas_acento"][7], width=2, tags="sala_layer",
            )

    def _dibujar_salas_vectoriales(self, ox: float, oy: float, bw: float, bh: float):
        pal = obtener_paleta()
        salas = obtener_salas()
        tam_titulo = max(9, min(12, int(bw / 92)))
        tam_sub = max(9, min(11, int(bw / 102)))

        for sid, nombre, color_sala, metodos in salas:
            cx, cy, x0, y0, x1, y1 = self._rect_sala(sid)
            comp = sum(1 for m in metodos if self.estado.completados.get(m))
            tot = len(metodos)
            completa = comp == tot
            prom_est = self.estado.promedio_estrellas_sala(metodos)
            sum_est = sum(self.estado.obtener_estrellas(m) for m in metodos)
            max_est = 3.0 * tot

            es_actual = sid == self.sala_actual
            es_hover = sid == self.sala_hover

            if es_actual:
                borde = pal["titulo"]
                grosor = 3
            elif es_hover:
                borde = pal["acento"]
                grosor = 2
            elif completa:
                borde = pal["exito"]
                grosor = 2
            else:
                borde = pal["mapa_sala_borde_idle"]
                grosor = 2

            if es_actual or es_hover:
                pad = 5 if es_actual else 3
                self.create_rectangle(
                    x0 - pad, y0 - pad, x1 + pad, y1 + pad,
                    fill="", outline=pal["titulo"] if es_actual else pal["acento"], width=1, dash=(5, 4), tags="sala_layer",
                )

            self.create_rectangle(
                x0, y0, x1, y1,
                fill=pal["mapa_sala_fill"] if not completa else pal["mapa_sala_ok_fill"],
                outline=borde,
                width=grosor,
                tags="sala_layer",
            )

            self._dibujar_interior_sala(sid, x0, y0, x1, y1, color_sala, completa)

            h_head = max(20.0, (y1 - y0) * 0.24)
            self.create_rectangle(
                x0 + 1, y0 + 1, x1 - 1, y0 + h_head,
                fill=pal["titulo"] if es_actual else (pal["mapa_sala_head_ok"] if completa else pal["mapa_sala_head"]),
                outline="",
                tags="sala_layer",
            )
            self.create_text(
                cx,
                y0 + h_head * 0.5,
                text=NOMBRES_CORTOS_MAPA[sid],
                fill=pal["mapa_texto_activo"] if es_actual else (pal["exito"] if completa else pal["texto"]),
                font=(FUENTE_UI, tam_titulo, "bold"),
                tags="sala_layer",
            )

            h_foot = max(18.0, (y1 - y0) * 0.22)
            self.create_rectangle(
                x0 + 1, y1 - h_foot, x1 - 1, y1 - 1,
                fill=pal["mapa_sala_foot"], outline="", tags="sala_layer",
            )
            color_est = pal["titulo"] if (es_actual or prom_est >= 2.95) else (pal["exito"] if completa else pal["texto_sec"])
            self.create_text(
                x0 + (x1 - x0) * 0.28,
                y1 - h_foot * 0.5,
                text=f"{comp}/{tot}",
                fill=color_est,
                font=(FUENTE_MONO, tam_sub, "bold"),
                tags="sala_layer",
            )

            star_r = max(4.6, min(6.6, (x1 - x0) * 0.044))
            base_sx = x0 + (x1 - x0) * 0.60
            step_sx = star_r * 2.35
            for s in range(3):
                if prom_est >= s + 1.0:
                    est_str = "llena"
                elif prom_est >= s + 0.5:
                    est_str = "media"
                else:
                    est_str = "vacia"
                dibujar_estrella_canvas(
                    self,
                    base_sx + s * step_sx,
                    y1 - h_foot * 0.5,
                    star_r,
                    est_str,
                )

            if es_hover:
                self.create_text(
                    cx,
                    y0 - 11,
                    text=f"{sum_est:.1f}/{max_est:.0f} EST.  •  CLIC PARA ABRIR",
                    fill=pal["titulo"],
                    font=(FUENTE_MONO, tam_sub, "bold"),
                    tags="sala_layer",
                )

    def _dibujar_barra_progreso(self, w: int, h: int):
        pal = obtener_paleta()
        salas = obtener_salas()
        ox = 12
        bx1 = w - 12
        fuente_hud = max(10, min(12, int(w / 76)))

        nombre_sel = next((s[1] for s in salas if s[0] == self.sala_actual), "")
        y_bot = h - max(34, int(h * 0.062))
        self.create_rectangle(ox, y_bot, bx1, h - 6, fill=pal["superficie"], outline=pal["borde"], width=1)
        self.create_text(
            ox + 16,
            (y_bot + h - 6) / 2,
            anchor="w",
            text=f"SECTOR ACTIVO: 0{self.sala_actual} — {nombre_sel}",
            fill=pal["titulo"],
            font=(FUENTE_UI, fuente_hud, "bold"),
        )
        if w >= 640:
            self.create_text(
                bx1 - 16,
                (y_bot + h - 6) / 2,
                anchor="e",
                text="WASD / Flechas para mover   •   ENTER o Clic para ingresar",
                fill=pal["texto"],
                font=(FUENTE_UI, max(9, fuente_hud - 1)),
            )

    def _dibujar_ingeniero(self, x: float, y: float):
        self.delete("ingeniero")
        idx = (self.paso_anim // 2) % len(self.frames) if self.caminando else 0
        self._img_ref = self.frames[idx]
        self.create_image(x, y + 4, image=self._img_ref, tags="ingeniero")
        try:
            self.tag_raise("ingeniero")
        except tk.TclError:
            pass

    def mover_a_sala(self, sala_id: int, abrir_al_llegar: bool = False):
        if sala_id not in SALAS_LAYOUT:
            return
        self.sala_actual = sala_id
        self._abrir_al_llegar = abrir_al_llegar
        cx, cy, _, _, _, _ = self._rect_sala(sala_id)
        self.tx, self.ty = cx, cy
        self.caminando = True
        self._redibujar()
        if self.al_cambiar_sala:
            self.al_cambiar_sala(sala_id)

    def mover_tecla(self, dx: int, dy: int):
        """Mueve al ingeniero hacia la sala vecina más cercana en la dirección (dx, dy)."""
        cx_act, cy_act, _, _ = SALAS_LAYOUT[self.sala_actual]
        mejor_id = None
        mejor_score = 999.0
        for sid, (cx, cy, _, _) in SALAS_LAYOUT.items():
            if sid == self.sala_actual:
                continue
            vx = cx - cx_act
            vy = cy - cy_act
            dot = vx * dx + vy * dy
            if dot <= 0.05:
                continue
            dist = (vx * vx + vy * vy) ** 0.5
            alineacion = dot / max(dist, 0.01)
            if alineacion < 0.35:
                continue
            score = dist / alineacion
            if score < mejor_score:
                mejor_score = score
                mejor_id = sid
        if mejor_id is not None:
            self.mover_a_sala(mejor_id, abrir_al_llegar=False)

    def _al_mover(self, event):
        nuevo_hover = None
        for sid in SALAS_LAYOUT:
            _, _, x0, y0, x1, y1 = self._rect_sala(sid)
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                nuevo_hover = sid
                break
        if nuevo_hover != self.sala_hover:
            self.sala_hover = nuevo_hover
            self.config(cursor="hand2" if nuevo_hover else "")
            self._redibujar()

    def _al_clic(self, event):
        self.focus_set()
        for sid in SALAS_LAYOUT:
            _, _, x0, y0, x1, y1 = self._rect_sala(sid)
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                if sid == self.sala_actual:
                    self.al_entrar_sala(sid)
                else:
                    self.mover_a_sala(sid, abrir_al_llegar=True)
                return

    def _bucle_animacion(self):
        if not self.winfo_exists():
            return
        self._tick_fx = (self._tick_fx + 1) % 3600
        if self.caminando:
            dx = self.tx - self.px
            dy = self.ty - self.py
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 10:
                self.px, self.py = self.tx, self.ty
                self.caminando = False
                self._redibujar()
                if getattr(self, "_abrir_al_llegar", False):
                    self._abrir_al_llegar = False
                    self.al_entrar_sala(self.sala_actual)
            else:
                vel = 16.0
                self.px += vel * dx / dist
                self.py += vel * dy / dist
                self.paso_anim += 1
                self._dibujar_ingeniero(self.px, self.py)
        elif self._tick_fx % 3 == 0 and self._ultimo_tamano[0] >= 60:
            ox, oy, bw, bh = self._caja_nave()
            self._dibujar_efectos_animados(ox, oy, bw, bh)
        self._anim_id = self.after(30, self._bucle_animacion)
