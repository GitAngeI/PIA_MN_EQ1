"""Renderizador de fórmulas matemáticas estilo libro/papel usando matplotlib (sin archivos temporales)."""

from collections import OrderedDict
import io
import logging
import tkinter as tk
from typing import Dict, Optional, Tuple
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

LOGGER = logging.getLogger(__name__)
MAX_CACHE_FORMULAS = 64

LATEX_METODOS: Dict[str, str] = {
    "Interpolación lineal": r"$g(x) = \frac{f(b) - f(a)}{b - a}(x - a) + f(a), \quad \varepsilon = |f(x) - g(x)|$",
    "Newton hacia adelante": r"$s = \frac{x - x_1}{h}, \quad g(x) = y_1 + \Delta^1 y_1\, s + \Delta^2 y_1 \frac{s(s-1)}{2!} + \cdots$",
    "Newton hacia atrás": r"$s = \frac{x - x_n}{h}, \quad g(x) = y_n + \nabla^1 y_n\, s + \nabla^2 y_n \frac{s(s+1)}{2!} + \cdots$",
    "Lagrange": r"$g(x) = \sum_{i=1}^{n} y_i \prod_{j=1,\, j \neq i}^{n} \frac{x - x_j}{x_i - x_j}$",
    "Newton con diferencias divididas": r"$D_{k,i} = \frac{D_{k-1,i+1} - D_{k-1,i}}{x_{i+k} - x_i}, \quad g(x) = y_1 + D_{1,1}(x-x_1) + D_{2,1}(x-x_1)(x-x_2)$",
    "Metodo Grafico": r"$\mathrm{Tabulación:}\; f(x_k)\cdot f(x_{k+1}) \leq 0 \;\Rightarrow\; \mathrm{raíz\; en\;} [x_k, x_{k+1}]$",
    "Metodo Bisectriz": r"$x_i = \frac{a + b}{2}, \quad \varepsilon = |x_{i+1} - x_i| \leq 0.001$",
    "Metodo Newton-Raphson": r"$x_{i+1} = x_i - \frac{f(x_i)}{f'(x_i)}, \quad \varepsilon = |x_{i+1} - x_i| \leq 0.001$",
    "Metodo de la Falsa Posicion o Regula": r"$x_i = a - \frac{f(a)(b - a)}{f(b) - f(a)}, \quad \varepsilon = |x_{i+1} - x_i| \leq 0.001$",
    "Secante": r"$x_{i+1} = x_i - \frac{f(x_i)(x_i - x_{i-1})}{f(x_i) - f(x_{i-1})}, \quad \varepsilon = |x_{i+1} - x_i| \leq 0.001$",
    "Punto Fijo": r"$f(x) = 0 \;\Rightarrow\; x = g(x), \quad x_{i+1} = g(x_i), \quad \varepsilon = |x_{i+1} - x_i|$",
    "Montante": r"$a'_{ij} = \frac{a_{kk}\,a_{ij} - a_{ik}\,a_{kj}}{p_{\mathrm{ant}}}, \quad x_i = \frac{b'_i}{\det(A)}$",
    "Gauss - Jordan": r"$[A \mid b] \longrightarrow [I \mid x] \quad (\text{pivoteo completo arriba y abajo})$",
    "Eliminacion gaussiana": r"$[A \mid b] \longrightarrow [U \mid b'], \quad x_i = \frac{b'_i - \sum_{j=i+1}^{n} U_{ij} x_j}{U_{ii}}$",
    "Gauss-Seidel": r"$|a_{ii}| > \sum_{j \neq i}|a_{ij}|, \quad x_i^{(k+1)} = \frac{b_i - \sum_{j<i} a_{ij}x_j^{(k+1)} - \sum_{j>i} a_{ij}x_j^{(k)}}{a_{ii}}$",
    "Jacobi": r"$|a_{ii}| > \sum_{j \neq i}|a_{ij}|, \quad x_i^{(k+1)} = \frac{b_i - \sum_{j \neq i} a_{ij} x_j^{(k)}}{a_{ii}}$",
    "Linea Recta": r"$g(x) = a_0 + a_1 x, \quad n\,a_0 + (\sum x)\,a_1 = \sum y, \quad (\sum x)\,a_0 + (\sum x^2)\,a_1 = \sum xy$",
    "Cuadratica": r"$g(x) = a_0 + a_1 x + a_2 x^2 \quad (\text{sistema normal } 3 \times 3\text{ hasta }\sum x^4)$",
    "Cubica": r"$g(x) = a_0 + a_1 x + a_2 x^2 + a_3 x^3 \quad (\text{sistema normal } 4 \times 4\text{ hasta }\sum x^6)$",
    "Lineal con Funcion": r"$g(x) = a_0 + a_1 x + a_2 \phi(x), \quad \phi(x) \in \{e^x, \sin x, \cos x, \tan x, \ln x\}$",
    "Cuadratica con Funcion": r"$g(x) = a_0 + a_1 x + a_2 x^2 + a_3 \phi(x), \quad \phi(x) \in \{e^x, \sin x, \cos x, \tan x, \ln x\}$",
    "Regla Trapezoidal": r"$h = \frac{b - a}{n}, \quad I = \frac{h}{2}\left[f(a) + 2\sum_{i=1}^{n-1} f(a + ih) + f(b)\right]$",
    "Regla de 1/3 de Simpson": r"$n\text{ par}, \quad I = \frac{h}{3}\left[f(a) + 4\sum_{\mathrm{impar}} f(x_i) + 2\sum_{\mathrm{par}} f(x_i) + f(b)\right]$",
    "Regla de 3/8 de Simpson": r"$n = 3k, \quad I = \frac{3h}{8}\left[f(x_0) + 3f(x_1) + 3f(x_2) + f(x_3)\right]$",
    "Newton – Cotes Abiertas": r"$h = \frac{b - a}{n + 2}, \quad I = \alpha_n\, h \sum_{i=1}^{n+1} c_i\, f(a + ih)$",
    "Newton - Cotes Cerradas": r"$h = \frac{b - a}{n}, \quad I = \alpha_n\, h \sum_{i=0}^{n} c_i\, f(a + ih)$",
    "Euler Modificado": r"$y'_{n+1} = y_n + \frac{h}{2}\left[f(y_n, t_n) + f(y_{n+1}, t_{n+1})\right]$",
    "Runge - Kutta 2ndo Orden": r"$k_1 = h f(y_n, t_n), \quad k_2 = h f(y_n + k_1, t_n + h), \quad y_{n+1} = y_n + \frac{1}{2}(k_1 + k_2)$",
    "Runge - Kutta 3er Orden": r"$k_1, k_2, k_3 = h f(\dots) \;\Rightarrow\; y_{n+1} = y_n + \frac{1}{6}(k_1 + 4k_2 + k_3)$",
    "Runge - Kutta 4rto Orden por 1/3 de Simpson": r"$y_{n+1} = y_n + \frac{1}{6}(k_1 + 2k_2 + 2k_3 + k_4)$",
    "Runge - Kutta 4rto Orden por 3/8 de Simpson": r"$y_{n+1} = y_n + \frac{1}{8}(k_1 + 3k_2 + 3k_3 + k_4)$",
    "Runge - Kutta de Orden Superior": r"$y_{n+1} = U_n + \frac{1}{2}(k_1 + k_2), \quad y'_{n+1} = V_n + \frac{1}{2}(m_1 + m_2)$",
}


_CACHE_IMAGENES: "OrderedDict[Tuple[int, str, str, int, int], ImageTk.PhotoImage]" = OrderedDict()


def limpiar_cache_formulas() -> None:
    """Limpia explícitamente el caché de imágenes LaTeX."""
    _CACHE_IMAGENES.clear()


def renderizar_formula_tk(
    latex_expr: str,
    color_texto: str = "#FFD166",
    tamano_pt: int = 16,
    max_ancho: int = 640,
) -> Optional[ImageTk.PhotoImage]:
    """Renderiza una expresión LaTeX en memoria (transparente) como PhotoImage para Tkinter."""
    root_actual = tk._default_root
    root_id = id(root_actual) if root_actual is not None else 0

    # Purgar entradas ligadas a intérpretes Tcl cerrados para evitar TclError y fugas
    if root_id != 0 and any(k[0] != root_id for k in _CACHE_IMAGENES):
        for k in [k for k in _CACHE_IMAGENES if k[0] != root_id]:
            _CACHE_IMAGENES.pop(k, None)

    clave = (root_id, latex_expr, color_texto, tamano_pt, max_ancho)
    if clave in _CACHE_IMAGENES:
        _CACHE_IMAGENES.move_to_end(clave)
        return _CACHE_IMAGENES[clave]

    try:
        fig = Figure(figsize=(10.5, 1.3), dpi=130)
        fig.patch.set_alpha(0.0)
        canvas = FigureCanvasAgg(fig)
        fig.text(
            0.01,
            0.5,
            latex_expr,
            fontsize=tamano_pt,
            color=color_texto,
            va="center",
            ha="left",
        )
        with io.BytesIO() as buf:
            canvas.print_png(buf)
            buf.seek(0)
            with Image.open(buf) as raw:
                img = raw.convert("RGBA")
        fig.clear()

        bbox = img.getbbox()
        if bbox:
            pad = 8
            x0 = max(0, bbox[0] - pad)
            y0 = max(0, bbox[1] - pad)
            x1 = min(img.width, bbox[2] + pad)
            y1 = min(img.height, bbox[3] + pad)
            img = img.crop((x0, y0, x1, y1))
        if img.width > max_ancho:
            ratio = max_ancho / img.width
            img = img.resize((max_ancho, max(24, int(img.height * ratio))), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(img)
        _CACHE_IMAGENES[clave] = photo
        while len(_CACHE_IMAGENES) > MAX_CACHE_FORMULAS:
            _CACHE_IMAGENES.popitem(last=False)
        return photo
    except Exception as exc:
        LOGGER.warning("No se pudo renderizar LaTeX %r: %s", latex_expr, exc)
        return None
