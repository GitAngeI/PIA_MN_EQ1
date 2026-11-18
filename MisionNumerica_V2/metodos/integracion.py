"""Sala 5: Integración Numérica (tablas y fórmulas de OR/Integración)."""

from typing import Callable, Dict, Any, List, Tuple


# Tabla oficial de ConstantesN-CotesAC.pdf
CERRADAS_TABLA: Dict[int, Tuple[float, List[int]]] = {
    1: (1 / 2, [1, 1]),
    2: (1 / 3, [1, 4, 1]),
    3: (3 / 8, [1, 3, 3, 1]),
    4: (2 / 45, [7, 32, 12, 32, 7]),
    5: (5 / 288, [19, 75, 50, 50, 75, 19]),
    6: (1 / 140, [41, 216, 27, 272, 27, 216, 41]),
    7: (7 / 17280, [751, 3577, 1323, 2989, 2989, 1323, 3577, 751]),
    8: (4 / 14175, [989, 5888, -928, 10496, -4540, 10496, -928, 5888, 989]),
    9: (9 / 89600, [2857, 15741, 1080, 19344, 5778, 5778, 19344, 1080, 15741, 2857]),
    10: (5 / 299376, [16067, 106300, -48525, 272400, -260550, 427368, -260550, 272400, -48525, 106300, 16067]),
}

ABIERTAS_TABLA: Dict[int, Tuple[float, List[int]]] = {
    1: (3 / 2, [0, 1, 1, 0]),
    2: (4 / 3, [0, 2, -1, 2, 0]),
    3: (5 / 24, [0, 11, 1, 1, 11, 0]),
    4: (6 / 20, [0, 11, -14, 26, -14, 11, 0]),
    5: (7 / 1440, [0, 611, -453, 562, 562, -453, 611, 0]),
    6: (8 / 945, [0, 460, -954, 2196, -2459, 2196, -954, 460, 0]),
}


def _validar_tabla_uniforme(xs: List[float], fs: List[float]) -> tuple[List[float], List[float], float]:
    """Valida malla uniforme equiespaciada y estrictamente creciente."""
    if len(xs) != len(fs) or len(xs) < 2:
        raise ValueError("La tabla de integración debe tener la misma longitud (>= 2 puntos).")
    xs_f = [float(x) for x in xs]
    fs_f = [float(y) for y in fs]
    h = xs_f[1] - xs_f[0]
    if h <= 0:
        raise ValueError("Los valores de x deben ser estrictamente crecientes.")
    tol = max(1e-7, 1e-6 * abs(h))
    for i in range(1, len(xs_f)):
        if abs((xs_f[i] - xs_f[i - 1]) - h) > tol:
            raise ValueError("La tabla de integración debe tener paso uniforme h.")
    return xs_f, fs_f, h


def _integrar_desde_pesos(xs: List[float], fs: List[float], metodo_clave: str) -> Dict[str, Any]:
    xs_f, fs_f, h = _validar_tabla_uniforme(xs, fs)
    n_seg = len(xs_f) - 1
    clave = metodo_clave.strip().lower().replace("–", "-")

    if "trapezoidal" in clave:
        integral = (h / 2.0) * (fs_f[0] + 2.0 * sum(fs_f[1:-1]) + fs_f[-1])
        return {"h": h, "n": n_seg, "xs": xs_f, "fs": fs_f, "integral": integral}

    if "1/3" in clave:
        if n_seg < 2 or n_seg % 2 != 0:
            raise ValueError("En 1/3 de Simpson, n debe ser un número par >= 2.")
        impares = sum(fs_f[i] for i in range(1, n_seg, 2))
        pares = sum(fs_f[i] for i in range(2, n_seg, 2))
        integral = (h / 3.0) * (fs_f[0] + 4.0 * impares + 2.0 * pares + fs_f[-1])
        return {"h": h, "n": n_seg, "xs": xs_f, "fs": fs_f, "integral": integral}

    if "3/8" in clave:
        if n_seg < 3 or n_seg % 3 != 0:
            raise ValueError("En 3/8 de Simpson, n debe ser múltiplo de 3 (ej. 3, 6, 9).")
        suma = fs_f[0] + fs_f[-1]
        for i in range(1, n_seg):
            suma += (2.0 if i % 3 == 0 else 3.0) * fs_f[i]
        integral = (3.0 * h / 8.0) * suma
        return {"h": h, "n": n_seg, "xs": xs_f, "fs": fs_f, "integral": integral}

    if "abierta" in clave:
        n_nc = len(xs_f) - 3
        if n_nc not in ABIERTAS_TABLA:
            raise ValueError("n debe estar entre 1 y 6 para Newton-Cotes Abiertas.")
        alpha, pesos = ABIERTAS_TABLA[n_nc]
        integral = alpha * h * sum(c * fx for c, fx in zip(pesos, fs_f))
        return {"h": h, "n": n_nc, "alpha": alpha, "pesos": pesos, "xs": xs_f, "fs": fs_f, "integral": integral}

    if "cerrada" in clave:
        n_nc = n_seg
        if n_nc not in CERRADAS_TABLA:
            raise ValueError("n debe estar entre 1 y 10 para Newton-Cotes Cerradas.")
        alpha, pesos = CERRADAS_TABLA[n_nc]
        integral = alpha * h * sum(c * fx for c, fx in zip(pesos, fs_f))
        return {"h": h, "n": n_nc, "alpha": alpha, "pesos": pesos, "xs": xs_f, "fs": fs_f, "integral": integral}

    raise ValueError(f"Método de integración tabular no soportado: {metodo_clave}")


def integrar_tabla(metodo: str, xs: List[float], fs: List[float]) -> Dict[str, Any]:
    """Integra numéricamente una tabla discreta (x_i, f(x_i)) con paso uniforme h."""
    return _integrar_desde_pesos(xs, fs, metodo)


def regla_trapezoidal(f: Callable[[float], float], a: float, b: float, n: int) -> Dict[str, Any]:
    """I = (h/2) * [f(a) + 2*sum f(a+ih) + f(b)]."""
    if n < 1:
        raise ValueError("n debe ser >= 1.")
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    fs = [f(x) for x in xs]
    return _integrar_desde_pesos(xs, fs, "Regla Trapezoidal")


def simpson_un_tercio(f: Callable[[float], float], a: float, b: float, n: int) -> Dict[str, Any]:
    """Regla 1/3 Simpson: n siempre par."""
    if n < 2 or n % 2 != 0:
        raise ValueError("En 1/3 de Simpson, n debe ser un número par >= 2.")
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    fs = [f(x) for x in xs]
    return _integrar_desde_pesos(xs, fs, "1/3 Simpson")


def simpson_tres_octavos(f: Callable[[float], float], a: float, b: float, n: int = 3) -> Dict[str, Any]:
    """Regla 3/8 Simpson: n múltiplo de 3."""
    if n < 3 or n % 3 != 0:
        raise ValueError("En 3/8 de Simpson, n debe ser múltiplo de 3 (ej. 3, 6, 9).")
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    fs = [f(x) for x in xs]
    return _integrar_desde_pesos(xs, fs, "3/8 Simpson")


def newton_cotes_abiertas(f: Callable[[float], float], a: float, b: float, n: int = 4) -> Dict[str, Any]:
    """Newton-Cotes Abiertas con h = (b-a)/(n+2) y coeficientes oficiales."""
    if n not in ABIERTAS_TABLA:
        raise ValueError("n debe estar entre 1 y 6 para Newton-Cotes Abiertas.")
    h = (b - a) / (n + 2)
    xs = [a + i * h for i in range(n + 3)]
    fs = [f(x) for x in xs]
    return _integrar_desde_pesos(xs, fs, "Newton - Cotes Abiertas")


def newton_cotes_cerradas(f: Callable[[float], float], a: float, b: float, n: int = 4) -> Dict[str, Any]:
    """Newton-Cotes Cerradas con h = (b-a)/n y coeficientes oficiales."""
    if n not in CERRADAS_TABLA:
        raise ValueError("n debe estar entre 1 y 10 para Newton-Cotes Cerradas.")
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    fs = [f(x) for x in xs]
    return _integrar_desde_pesos(xs, fs, "Newton - Cotes Cerradas")
