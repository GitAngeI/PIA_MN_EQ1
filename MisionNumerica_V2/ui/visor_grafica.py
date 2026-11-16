"""Visor grafico analitico graduado para representar curvas, areas, trayectorias EDO y sistemas."""

import math
import tkinter as tk
from typing import Any, Dict, List, Tuple

from .tema import AMBAR, CORAL, CREMA, DORADO, ESMERALDA, FONDO_GALAXIA, GRIS_CALIDO


def _ticks_bonitos(vmin: float, vmax: float, max_ticks: int = 5) -> Tuple[float, float, List[float]]:
    if not math.isfinite(vmin) or not math.isfinite(vmax):
        return 0.0, 1.0, [0.0, 0.5, 1.0]
    span = vmax - vmin
    if abs(span) < 1e-9:
        pad = max(1.0, abs(vmin) * 0.25)
        vmin -= pad
        vmax += pad
        span = vmax - vmin
    else:
        vmin -= span * 0.08
        vmax += span * 0.08
        span = vmax - vmin

    raw_step = span / max(2, max_ticks - 1)
    mag = 10 ** math.floor(math.log10(raw_step))
    norm = raw_step / mag
    if norm <= 1.2:
        step = 1.0 * mag
    elif norm <= 2.2:
        step = 2.0 * mag
    elif norm <= 5.5:
        step = 5.0 * mag
    else:
        step = 10.0 * mag

    start = math.floor(vmin / step) * step
    end = math.ceil(vmax / step) * step
    ticks: List[float] = []
    val = start
    while val <= end + step * 1e-6 and len(ticks) < 16:
        ticks.append(0.0 if abs(val) < step * 1e-9 else val)
        val += step
    return start, max(end, start + step), ticks


def _fmt_tick(val: float) -> str:
    if abs(val) < 1e-9:
        return "0"
    if abs(val) >= 1000 or (0 < abs(val) < 0.01):
        return f"{val:.2g}"
    txt = f"{val:.2f}".rstrip("0").rstrip(".")
    return txt


class VisorGraficaHUD(tk.Canvas):
    """Canvas analitico con ejes reales graduados y revelacion progresiva sin spoilers."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("bg", "#0F0B1B")
        kwargs.setdefault("height", 220)
        kwargs.setdefault("highlightbackground", "#3B2E58")
        kwargs.setdefault("highlightthickness", 1)
        super().__init__(master, **kwargs)
        self._mision: Dict[str, Any] = {}
        self._acento = DORADO
        self._paso_idx = 0
        self._completado = False
        self.bind("<Configure>", lambda _e: self._redibujar())

    def actualizar(
        self,
        mision: Dict[str, Any],
        acento: str,
        paso_idx: int = 0,
        completado: bool = False,
    ) -> None:
        self._mision = mision or {}
        self._acento = acento or DORADO
        self._paso_idx = int(paso_idx)
        self._completado = bool(completado)
        self._redibujar()

    def _extraer_puntos_fallback(self) -> List[Tuple[float, float]]:
        tabla = self._mision.get("datos_tabla")
        if not tabla:
            return []
        _, filas = tabla
        pts: List[Tuple[float, float]] = []
        for fila in filas:
            if len(fila) >= 3:
                try:
                    pts.append((float(fila[1]), float(fila[2])))
                except (ValueError, TypeError):
                    continue
            elif len(fila) == 2:
                try:
                    pts.append((float(fila[0]), float(fila[1])))
                except (ValueError, TypeError):
                    continue
        return pts

    def _redibujar(self) -> None:
        self.delete("all")
        w = max(self.winfo_width(), 380)
        h = max(self.winfo_height(), 190)

        grafica = self._mision.get("grafica") or {}
        metodo = self._mision.get("metodo", "GRAFICA")
        titulo = grafica.get("titulo") or f"VISOR ANALITICO // {metodo.upper()}"
        paso_ef = 999 if self._completado else self._paso_idx

        self.create_text(
            14, 13, anchor="w",
            text=titulo,
            fill=GRIS_CALIDO,
            font=("Consolas", 9, "bold"),
        )

        pad_izq, pad_der, pad_sup, pad_inf = 56, 20, 30, 34
        plot_w = max(80, w - pad_izq - pad_der)
        plot_h = max(60, h - pad_sup - pad_inf)

        tipo = grafica.get("tipo", "funcion")
        if tipo == "sistema":
            self._dibujar_sistema(grafica, w, h, pad_izq, pad_der, pad_sup, pad_inf, plot_w, plot_h, paso_ef)
            return

        # Recolectar unicamente geometria ya revelada en paso_ef para evitar spoilers
        curva_pts = [
            (float(x), float(y))
            for x, y in (grafica.get("curva_pts") or [])
            if math.isfinite(float(x)) and math.isfinite(float(y))
        ]
        puntos_datos = [
            (float(x), float(y))
            for x, y in (grafica.get("puntos_datos") or [])
            if math.isfinite(float(x)) and math.isfinite(float(y))
        ]
        if not curva_pts and not puntos_datos:
            puntos_datos = self._extraer_puntos_fallback()

        modelo_pts: List[Tuple[float, float]] = []
        if paso_ef >= int(grafica.get("curva_modelo_paso_min", 2)):
            modelo_pts = [
                (float(x), float(y))
                for x, y in (grafica.get("curva_modelo_pts") or [])
                if math.isfinite(float(x)) and math.isfinite(float(y))
            ]

        marcadores_visibles = [
            m for m in (grafica.get("marcadores") or [])
            if paso_ef >= int(m.get("paso_min", 0))
        ]

        if tipo == "edo":
            # En EDOs conectar trayectorias unicamente con nodos ya desbloqueados
            edo_visibles: List[Tuple[float, float]] = list(puntos_datos[:1])
            for mk in marcadores_visibles:
                edo_visibles.append((float(mk["x"]), float(mk["y"])))
            curva_pts_visible = sorted(edo_visibles, key=lambda p: p[0]) if len(edo_visibles) >= 2 else []
        else:
            curva_pts_visible = curva_pts

        area_cfg = grafica.get("area_integracion")
        xs_area: List[float] = []
        fs_area: List[float] = []
        if area_cfg:
            xs_area = [float(v) for v in (area_cfg.get("xs") or [])]
            fs_area = [float(v) for v in (area_cfg.get("fs") or [])]

        todos_pts = list(curva_pts_visible) + list(puntos_datos) + list(modelo_pts)
        for mk in marcadores_visibles:
            todos_pts.append((float(mk["x"]), float(mk["y"])))
        for xv, fv in zip(xs_area, fs_area):
            todos_pts.append((xv, fv))

        if not todos_pts:
            self.create_rectangle(pad_izq, pad_sup, w - pad_der, h - pad_inf, outline="#3B2E58")
            self.create_text(
                pad_izq + plot_w / 2, pad_sup + plot_h / 2,
                text="Completa los pasos de verificacion para trazar la curva.",
                fill=GRIS_CALIDO, font=("Consolas", 10),
            )
            return

        xs_all = [p[0] for p in todos_pts]
        ys_all = [p[1] for p in todos_pts]
        if area_cfg:
            ys_all.append(0.0)
        if tipo == "edo" and len(todos_pts) == 1:
            # Dar contexto de escala inicial en Paso 0 sin revelar y1/y2
            xs_all.append(todos_pts[0][0] + 0.5)
            ys_all.append(todos_pts[0][1] + 1.0)
            ys_all.append(todos_pts[0][1] - 0.5)

        xmin, xmax, xticks = _ticks_bonitos(min(xs_all), max(xs_all), max_ticks=6)
        ymin, ymax, yticks = _ticks_bonitos(min(ys_all), max(ys_all), max_ticks=5)
        span_x = (xmax - xmin) or 1.0
        span_y = (ymax - ymin) or 1.0

        def a_px(vx: float, vy: float) -> Tuple[float, float]:
            px = pad_izq + ((vx - xmin) / span_x) * plot_w
            py = (pad_sup + plot_h) - ((vy - ymin) / span_y) * plot_h
            return px, py

        # Cuadricula y ticks graduados
        for xt in xticks:
            px, _ = a_px(xt, ymin)
            if pad_izq - 1 <= px <= w - pad_der + 1:
                self.create_line(px, pad_sup, px, pad_sup + plot_h, fill="#1B1530")
                self.create_line(px, pad_sup + plot_h, px, pad_sup + plot_h + 4, fill="#6C5B99")
                self.create_text(px, pad_sup + plot_h + 13, text=_fmt_tick(xt), fill=GRIS_CALIDO, font=("Consolas", 8))

        for yt in yticks:
            _, py = a_px(xmin, yt)
            if pad_sup - 1 <= py <= pad_sup + plot_h + 1:
                self.create_line(pad_izq, py, w - pad_der, py, fill="#1B1530")
                self.create_line(pad_izq - 4, py, pad_izq, py, fill="#6C5B99")
                self.create_text(pad_izq - 7, py, text=_fmt_tick(yt), anchor="e", fill=GRIS_CALIDO, font=("Consolas", 8))

        # Marco de ejes y lineas y=0 / x=0 punteadas
        self.create_rectangle(pad_izq, pad_sup, w - pad_der, pad_sup + plot_h, outline="#584780", width=1)
        if ymin <= 0.0 <= ymax:
            _, y0_px = a_px(xmin, 0.0)
            self.create_line(pad_izq, y0_px, w - pad_der, y0_px, fill="#7E6BB3", width=1, dash=(4, 3))
        if xmin <= 0.0 <= xmax:
            x0_px, _ = a_px(0.0, ymin)
            self.create_line(x0_px, pad_sup, x0_px, pad_sup + plot_h, fill="#7E6BB3", width=1, dash=(4, 3))

        # Sombreado progresivo de trapecios / franjas en Integracion (Sala 5)
        if area_cfg and len(xs_area) >= 2 and paso_ef >= 1:
            for i in range(len(xs_area) - 1):
                x1, x2 = xs_area[i], xs_area[i + 1]
                f1, f2 = fs_area[i], fs_area[i + 1]
                p1 = a_px(x1, 0.0)
                p2 = a_px(x1, f1)
                p3 = a_px(x2, f2)
                p4 = a_px(x2, 0.0)
                fill_trap = "#1C4D3E" if (self._completado or paso_ef >= 2) else "#282046"
                self.create_polygon(
                    p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1],
                    fill=fill_trap, outline="#4DA688", width=1, stipple="gray25",
                )

        # Curva base f(x) o trayectoria EDO revelada
        if len(curva_pts_visible) >= 2:
            coords: List[float] = []
            for vx, vy in curva_pts_visible:
                px, py = a_px(vx, vy)
                coords.extend([px, py])
            self.create_line(*coords, fill=self._acento, width=2, smooth=(tipo != "edo"))

        # Curva secundaria o modelo ajustado (solo cuando paso_ef >= curva_modelo_paso_min)
        if len(modelo_pts) >= 2:
            coords_m: List[float] = []
            for vx, vy in modelo_pts:
                px, py = a_px(vx, vy)
                coords_m.extend([px, py])
            self.create_line(*coords_m, fill=DORADO, width=2, dash=(6, 3))

        # Puntos de entrada de tabla
        for vx, vy in puntos_datos:
            px, py = a_px(vx, vy)
            self.create_oval(px - 4, py - 4, px + 4, py + 4, fill=ESMERALDA, outline=CREMA, width=1)

        # Marcadores progresivos desbloqueados
        for idx, mk in enumerate(marcadores_visibles):
            vx, vy = float(mk["x"]), float(mk["y"])
            px, py = a_px(vx, vy)
            col = mk.get("color", DORADO)
            self.create_oval(px - 5, py - 5, px + 5, py + 5, fill=col, outline=FONDO_GALAXIA, width=1)
            et = str(mk.get("etiqueta", ""))
            if et:
                dy = -12 if py > pad_sup + 24 else 12
                self.create_text(px, py + dy, text=et, fill=col, font=("Consolas", 8, "bold"))

        # Etiquetas de ejes
        xlabel = str(grafica.get("xlabel", "x"))
        ylabel = str(grafica.get("ylabel", "y"))
        self.create_text(w - pad_der, pad_sup + plot_h + 24, anchor="e", text=xlabel, fill=AMBAR, font=("Consolas", 8, "bold"))
        self.create_text(pad_izq + 4, pad_sup + 8, anchor="w", text=ylabel, fill=AMBAR, font=("Consolas", 8, "bold"))

    def _dibujar_sistema(
        self,
        grafica: Dict[str, Any],
        w: int,
        h: int,
        pad_izq: int,
        pad_der: int,
        pad_sup: int,
        pad_inf: int,
        plot_w: int,
        plot_h: int,
        paso_ef: int,
    ) -> None:
        barras = grafica.get("barras") or {}
        paso_min = int(barras.get("paso_min", 2))
        etiquetas = barras.get("etiquetas") or []
        valores = [float(v) for v in (barras.get("valores") or [])]

        self.create_rectangle(pad_izq, pad_sup, w - pad_der, pad_sup + plot_h, outline="#584780", width=1)
        if paso_ef < paso_min or not etiquetas or not valores:
            self.create_text(
                pad_izq + plot_w / 2,
                pad_sup + plot_h / 2,
                text="GRAFICA DE INCOGNITAS EN ESPERA\nCompleta el Paso 2 para revelar magnitudes x1, x2, x3",
                fill=GRIS_CALIDO,
                font=("Consolas", 9),
                justify=tk.CENTER,
            )
            return

        ymin, ymax, yticks = _ticks_bonitos(min(0.0, min(valores)), max(0.0, max(valores)), max_ticks=5)
        span_y = (ymax - ymin) or 1.0

        def y_px(vy: float) -> float:
            return (pad_sup + plot_h) - ((vy - ymin) / span_y) * plot_h

        for yt in yticks:
            py = y_px(yt)
            self.create_line(pad_izq, py, w - pad_der, py, fill="#1B1530")
            self.create_text(pad_izq - 7, py, text=_fmt_tick(yt), anchor="e", fill=GRIS_CALIDO, font=("Consolas", 8))

        y0 = y_px(0.0)
        self.create_line(pad_izq, y0, w - pad_der, y0, fill="#8D79C7", width=1, dash=(4, 3))

        n = len(etiquetas)
        ancho_slot = plot_w / max(1, n)
        ancho_barra = min(56.0, ancho_slot * 0.52)
        for i, (et, val) in enumerate(zip(etiquetas, valores)):
            cx = pad_izq + (i + 0.5) * ancho_slot
            yb = y_px(val)
            top, bot = min(y0, yb), max(y0, yb)
            col = ESMERALDA if val >= 0 else CORAL
            self.create_rectangle(
                cx - ancho_barra / 2, top, cx + ancho_barra / 2, bot,
                fill=col, outline=CREMA, width=1,
            )
            self.create_text(cx, pad_sup + plot_h + 14, text=str(et), fill=CREMA, font=("Consolas", 9, "bold"))
            dy_val = -10 if val >= 0 else 10
            self.create_text(cx, yb + dy_val, text=_fmt_tick(val), fill=DORADO, font=("Consolas", 8, "bold"))
