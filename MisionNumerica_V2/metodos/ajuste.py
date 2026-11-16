"""Sala 4: Ajuste de Curvas - Mínimos Cuadrados (OR/MCuadrados)."""

from typing import Callable, List, Dict, Any
from .sistemas import eliminacion_gaussiana


def _validar_puntos(xs: List[float], ys: List[float], minimo: int) -> int:
    if len(xs) != len(ys):
        raise ValueError("xs y ys deben tener la misma longitud.")
    n = len(xs)
    if n < minimo:
        raise ValueError(f"Se requieren al menos {minimo} puntos para este ajuste.")
    return n


def _resolver_normal(A: List[List[float]], b: List[float]) -> List[float]:
    return eliminacion_gaussiana(A, b)["solucion"]


def minimos_cuadrados_recta(xs: List[float], ys: List[float]) -> Dict[str, Any]:
    """g(x) = a0 + a1*x."""
    n = _validar_puntos(xs, ys, 2)
    sx = sum(xs)
    sy = sum(ys)
    sx2 = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    A = [
        [float(n), sx],
        [sx, sx2],
    ]
    b = [sy, sxy]
    a0, a1 = _resolver_normal(A, b)
    gx = [a0 + a1 * x for x in xs]
    return {
        "matriz": A,
        "vector": b,
        "coeficientes": [a0, a1],
        "gx": gx,
        "sumatorias": {"n": n, "sx": sx, "sy": sy, "sx2": sx2, "sxy": sxy},
    }


def minimos_cuadrados_cuadratica(xs: List[float], ys: List[float]) -> Dict[str, Any]:
    """g(x) = a0 + a1*x + a2*x^2."""
    n = _validar_puntos(xs, ys, 3)
    sx = sum(xs)
    sx2 = sum(x ** 2 for x in xs)
    sx3 = sum(x ** 3 for x in xs)
    sx4 = sum(x ** 4 for x in xs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sx2y = sum((x ** 2) * y for x, y in zip(xs, ys))
    A = [
        [float(n), sx, sx2],
        [sx, sx2, sx3],
        [sx2, sx3, sx4],
    ]
    b = [sy, sxy, sx2y]
    a0, a1, a2 = _resolver_normal(A, b)
    gx = [a0 + a1 * x + a2 * (x ** 2) for x in xs]
    return {"matriz": A, "vector": b, "coeficientes": [a0, a1, a2], "gx": gx}


def minimos_cuadrados_cubica(xs: List[float], ys: List[float]) -> Dict[str, Any]:
    """g(x) = a0 + a1*x + a2*x^2 + a3*x^3."""
    n = _validar_puntos(xs, ys, 4)
    pows = [sum(x ** k for x in xs) for k in range(7)]
    rhs = [sum((x ** k) * y for x, y in zip(xs, ys)) for k in range(4)]
    A = [[pows[i + j] for j in range(4)] for i in range(4)]
    A[0][0] = float(n)
    a0, a1, a2, a3 = _resolver_normal(A, rhs)
    gx = [a0 + a1 * x + a2 * (x ** 2) + a3 * (x ** 3) for x in xs]
    return {"matriz": A, "vector": rhs, "coeficientes": [a0, a1, a2, a3], "gx": gx}


def minimos_cuadrados_lineal_funcion(
    xs: List[float],
    ys: List[float],
    phi: Callable[[float], float],
) -> Dict[str, Any]:
    """g(x) = a0 + a1*x + a2*phi(x)."""
    n = _validar_puntos(xs, ys, 3)
    fs = [phi(x) for x in xs]
    sx = sum(xs)
    sx2 = sum(x ** 2 for x in xs)
    sf = sum(fs)
    sxf = sum(x * f for x, f in zip(xs, fs))
    sf2 = sum(f ** 2 for f in fs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    syf = sum(y * f for y, f in zip(ys, fs))
    A = [
        [float(n), sx, sf],
        [sx, sx2, sxf],
        [sf, sxf, sf2],
    ]
    b = [sy, sxy, syf]
    a0, a1, a2 = _resolver_normal(A, b)
    gx = [a0 + a1 * x + a2 * f for x, f in zip(xs, fs)]
    return {"matriz": A, "vector": b, "coeficientes": [a0, a1, a2], "gx": gx}


def minimos_cuadrados_cuadratica_funcion(
    xs: List[float],
    ys: List[float],
    phi: Callable[[float], float],
) -> Dict[str, Any]:
    """g(x) = a0 + a1*x + a2*x^2 + a3*phi(x)."""
    n = _validar_puntos(xs, ys, 4)
    fs = [phi(x) for x in xs]
    sx = sum(xs)
    sx2 = sum(x ** 2 for x in xs)
    sx3 = sum(x ** 3 for x in xs)
    sx4 = sum(x ** 4 for x in xs)
    sf = sum(fs)
    sxf = sum(x * f for x, f in zip(xs, fs))
    sx2f = sum((x ** 2) * f for x, f in zip(xs, fs))
    sf2 = sum(f ** 2 for f in fs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sx2y = sum((x ** 2) * y for x, y in zip(xs, ys))
    syf = sum(y * f for y, f in zip(ys, fs))
    A = [
        [float(n), sx, sx2, sf],
        [sx, sx2, sx3, sxf],
        [sx2, sx3, sx4, sx2f],
        [sf, sxf, sx2f, sf2],
    ]
    b = [sy, sxy, sx2y, syf]
    a0, a1, a2, a3 = _resolver_normal(A, b)
    gx = [a0 + a1 * x + a2 * (x ** 2) + a3 * f for x, f in zip(xs, fs)]
    return {"matriz": A, "vector": b, "coeficientes": [a0, a1, a2, a3], "gx": gx}
