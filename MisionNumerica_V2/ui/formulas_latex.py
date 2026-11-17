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
    "Newton hacia adelante": r"$s = \frac{x - x_1}{h}, \quad g(x) = y_1 + \Delta^1 y_1\, s + \Delta^2 y_1 \frac{s(s-1)}{2!} + \Delta^3 y_1 \frac{s(s-1)(s-2)}{3!}$",
    "Newton hacia atrás": r"$s = \frac{x - x_n}{h}, \quad g(x) = y_n + \nabla^1 y_n\, s + \nabla^2 y_n \frac{s(s+1)}{2!} + \nabla^3 y_n \frac{s(s+1)(s+2)}{3!}$",
    "Lagrange": r"$g(x) = \sum_{i=1}^{n} y_i\, L_i(x), \quad L_i(x) = \prod_{j=1,\, j \neq i}^{n} \frac{x - x_j}{x_i - x_j}$",
    "Newton con diferencias divididas": "$D_{1,i} = \\frac{y_{i+1}-y_i}{x_{i+1}-x_i}, \\quad D_{k,i} = \\frac{D_{k-1,i+1} - D_{k-1,i}}{x_{i+k} - x_i}$\n$g(x) = y_1 + D_{1,1}(x-x_1) + D_{2,1}(x-x_1)(x-x_2)$",
    "Metodo Grafico": r"$\mathrm{Tabulación:}\; f(x_k)\cdot f(x_{k+1}) \leq 0 \;\Rightarrow\; \mathrm{raíz\; en\;} [x_k, x_{k+1}]$",
    "Metodo Bisectriz": r"$x_i = \frac{a + b}{2} \;\;(f(a)f(b)<0), \quad \varepsilon = |x_{i+1} - x_i| \leq 0.001$",
    "Metodo Newton-Raphson": r"$x_{i+1} = x_i - \frac{f(x_i)}{f'(x_i)}, \quad \varepsilon = |x_{i+1} - x_i| \leq 0.001$",
    "Metodo de la Falsa Posicion o Regula": r"$x_i = a - \frac{f(a)(b - a)}{f(b) - f(a)}, \quad \varepsilon = |x_{i+1} - x_i| \leq 0.001$",
    "Secante": r"$x_{i+1} = x_{i+1} - \left( \frac{f(x_{i+1})(x_{i+1} - x_i)}{f(x_{i+1}) - f(x_i)} \right), \quad \varepsilon = |x_{i+1} - x_i| \leq 0.001$",
    "Punto Fijo": r"$f(x) = 0 \;\Rightarrow\; x = g(x) \;\;(|g'(x_0)| < 1), \quad x_{i+1} = g(x_i), \quad \varepsilon = |x_{i+1} - x_i|$",
    "Montante": r"$p_{\mathrm{ant}}=1, \quad a'_{ij} = \frac{a_{kk}\,a_{ij} - a_{ik}\,a_{kj}}{p_{\mathrm{ant}}}, \quad x_i = \frac{b'_i}{\det(A)}$",
    "Gauss - Jordan": r"$[A \mid b] \longrightarrow [I \mid x] \quad (\mathrm{pivote}=1,\; \mathrm{anular\; arriba\; y\; abajo})$",
    "Eliminacion gaussiana": r"$[A \mid b] \longrightarrow [U \mid b'], \quad x_i = \frac{b'_i - \sum_{j=i+1}^{n} U_{ij} x_j}{U_{ii}}$",
    "Gauss-Seidel": r"$|a_{ii}| > \sum_{j \neq i}|a_{ij}|, \quad x_i^{(k+1)} = \frac{b_i - \sum_{j<i} a_{ij}x_j^{(k+1)} - \sum_{j>i} a_{ij}x_j^{(k)}}{a_{ii}}$",
    "Jacobi": r"$|a_{ii}| > \sum_{j \neq i}|a_{ij}|, \quad x_i^{(k+1)} = \frac{b_i - \sum_{j \neq i} a_{ij} x_j^{(k)}}{a_{ii}}$",
    "Linea Recta": "$g(x) = a_0 + a_1 x: \\quad n\\,a_0 + (\\sum x)\\,a_1 = \\sum y, \\quad (\\sum x)\\,a_0 + (\\sum x^2)\\,a_1 = \\sum xy$\n$a_1 = \\frac{n\\sum xy - (\\sum x)(\\sum y)}{n\\sum x^2 - (\\sum x)^2}, \\quad a_0 = \\frac{\\sum y - a_1 \\sum x}{n}$",
    "Cuadratica": r"$g(x) = a_0 + a_1 x + a_2 x^2 \quad (\mathrm{sistema\; normal\;} 3\times 3: \; [n, \sum x, \sum x^2 \mid \sum y], \dots, \sum x^4, \sum x^2 y)$",
    "Cubica": r"$g(x) = a_0 + a_1 x + a_2 x^2 + a_3 x^3 \quad (\mathrm{sistema\; normal\;} 4\times 4\; \mathrm{hasta}\; \sum x^6,\; \sum x^3 y)$",
    "Lineal con Funcion": r"$g(x) = a_0 + a_1 x + a_2 f(x), \quad f(x) \in \{e^x, \sin x, \cos x, \tan x, \ln x\}$",
    "Cuadratica con Funcion": r"$g(x) = a_0 + a_1 x + a_2 x^2 + a_3 f(x), \quad f(x) \in \{e^x, \sin x, \cos x, \tan x, \ln x\}$",
    "Regla Trapezoidal": r"$h = \frac{b - a}{n}, \quad I = \frac{h}{2}\left[f(a) + 2\sum_{i=1}^{n-1} f(a + ih) + f(b)\right]$",
    "Regla de 1/3 de Simpson": r"$n\;\mathrm{par},\; h = \frac{b-a}{n}, \quad I = \frac{h}{3}\left[f(a) + 4\sum_{\mathrm{impar}} f(x_i) + 2\sum_{\mathrm{par}} f(x_i) + f(b)\right]$",
    "Regla de 3/8 de Simpson": r"$h = \frac{b-a}{n}, \quad I = \frac{3}{8}h\left[f(a) + 3\sum_{i=1}^{n-1} f(a+ih) + f(b)\right]$",
    "Newton – Cotes Abiertas": r"$h = \frac{b - a}{n + 2}$" + "\n\n" + r"$I = \alpha\, h \sum_{i=0}^{n+2} w_i\, f(a + i h)$",
    "Newton - Cotes Cerradas": r"$h = \frac{b - a}{n}$" + "\n\n" + r"$I = \alpha\, h \sum_{i=0}^{n} w_i\, f(a + i h)$",
    "Euler Modificado": "$y' = f(y, t), \\quad t_{n+1} = t_n + h, \\quad y_{n+1}^* = y_n + h\\,f(y_n, t_n)$\n$y'_{n+1} = y_n + \\frac{h}{2}\\left[f(y_n, t_n) + f(y_{n+1}^*, t_{n+1})\\right]$",
    "Runge - Kutta 2ndo Orden": "$k_1 = h\\,f(y_n, t_n), \\quad k_2 = h\\,f(y_n + k_1, t_n + h)$\n$y_{n+1} = y_n + \\frac{1}{2}(k_1 + k_2)$",
    "Runge - Kutta 3er Orden": "$k_1 = h f(y_n,t_n), \\; k_2 = h f\\left(y_n + \\frac{k_1}{2}, t_n + \\frac{h}{2}\\right), \\; k_3 = h f(y_n - k_1 + 2k_2, t_n + h)$\n$y_{n+1} = y_n + \\frac{1}{6}(k_1 + 4k_2 + k_3)$",
    "Runge - Kutta 4rto Orden por 1/3 de Simpson": "$k_1 = h f(y_n,t_n), \\; k_2 = h f\\left(y_n+\\frac{k_1}{2}, t_n+\\frac{h}{2}\\right), \\; k_3 = h f\\left(y_n+\\frac{k_2}{2}, t_n+\\frac{h}{2}\\right), \\; k_4 = h f(y_n+k_3, t_n+h)$\n$y_{n+1} = y_n + \\frac{1}{6}(k_1 + 2k_2 + 2k_3 + k_4)$",
    "Runge - Kutta 4rto Orden por 3/8 de Simpson": "$k_1 = h f(y_n,t_n), \\; k_2 = h f\\left(y_n+\\frac{k_1}{3}, t_n+\\frac{h}{3}\\right), \\; k_3 = h f\\left(y_n+\\frac{k_1+k_2}{3}, t_n+\\frac{2h}{3}\\right), \\; k_4 = h f(y_n+k_1-k_2+k_3, t_n+h)$\n$y_{n+1} = y_n + \\frac{1}{8}(k_1 + 3k_2 + 3k_3 + k_4)$",
    "Runge - Kutta de Orden Superior": "$U_n=y_n,\\; V_n=y'_n,\\; q_n=t_n:\\; k_1=hV_n,\\; m_1=h\\,g(V_n,U_n,q_n),\\; k_2=h(V_n+m_1),\\; m_2=h\\,g(V_n+m_1,U_n+k_1,q_n+h)$\n$y_{n+1} = U_n + \\frac{1}{2}(k_1 + k_2), \\quad y'_{n+1} = V_n + \\frac{1}{2}(m_1 + m_2)$",
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
        multilinea = "\n" in latex_expr
        fig = Figure(figsize=(11.5, 1.95 if multilinea else 1.35), dpi=130)
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
            linespacing=1.45,
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
