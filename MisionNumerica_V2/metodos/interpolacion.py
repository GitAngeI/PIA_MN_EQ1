"""Sala 1: Interpolación y Diferencias (fórmulas oficiales de la Ing. Oralia Zamora)."""

from typing import List, Optional, Dict, Any


def interpolacion_lineal(
    a: float,
    fa: float,
    b: float,
    fb: float,
    x: float,
    valor_real: Optional[float] = None,
) -> Dict[str, Any]:
    """g(x) = ((f(b) - f(a)) / (b - a)) * (x - a) + f(a), error = |f(x) - g(x)|."""
    if b == a:
        raise ValueError("a y b no pueden ser iguales en interpolación lineal.")
    pendiente = (fb - fa) / (b - a)
    gx = pendiente * (x - a) + fa
    error = abs(valor_real - gx) if valor_real is not None else None
    return {
        "pendiente": pendiente,
        "gx": gx,
        "error": error,
    }


def _tabla_diferencias_finitas(ys: List[float]) -> List[List[float]]:
    """Construye la tabla triangular de diferencias finitas Δ^k y_i."""
    tabla = [list(ys)]
    while len(tabla[-1]) > 1:
        prev = tabla[-1]
        tabla.append([prev[i + 1] - prev[i] for i in range(len(prev) - 1)])
    return tabla


def _verificar_paso_uniforme(xs: List[float]) -> float:
    if len(xs) < 2:
        raise ValueError("Se requieren al menos 2 puntos.")
    h = xs[1] - xs[0]
    if abs(h) < 1e-12:
        raise ValueError("El tamaño de paso h no puede ser 0.")
    if h < 0:
        raise ValueError("Los nodos x deben ser estrictamente crecientes para paso uniforme.")
    for i in range(1, len(xs) - 1):
        if abs((xs[i + 1] - xs[i]) - h) > 1e-6:
            raise ValueError("Los intervalos de x deben ser uniformes.")
    return h


def newton_adelante(xs: List[float], ys: List[float], x: float) -> Dict[str, Any]:
    """Newton hacia adelante con s = (x - x1) / h."""
    if len(xs) != len(ys):
        raise ValueError("xs y ys deben tener la misma longitud.")
    h = _verificar_paso_uniforme(xs)
    tabla = _tabla_diferencias_finitas(ys)
    s = (x - xs[0]) / h
    gx = ys[0]
    coef = 1.0
    terminos = [ys[0]]
    for k in range(1, len(xs)):
        coef *= (s - (k - 1)) / k
        termino = tabla[k][0] * coef
        gx += termino
        terminos.append(termino)
    return {
        "h": h,
        "s": s,
        "tabla": tabla,
        "diferencias_iniciales": [tabla[k][0] for k in range(len(xs))],
        "terminos": terminos,
        "gx": gx,
    }


def newton_atras(xs: List[float], ys: List[float], x: float) -> Dict[str, Any]:
    """Newton hacia atrás con s = (x - xn) / h."""
    if len(xs) != len(ys):
        raise ValueError("xs y ys deben tener la misma longitud.")
    h = _verificar_paso_uniforme(xs)
    tabla = _tabla_diferencias_finitas(ys)
    s = (x - xs[-1]) / h
    gx = ys[-1]
    coef = 1.0
    terminos = [ys[-1]]
    for k in range(1, len(xs)):
        coef *= (s + (k - 1)) / k
        termino = tabla[k][-1] * coef
        gx += termino
        terminos.append(termino)
    return {
        "h": h,
        "s": s,
        "tabla": tabla,
        "diferencias_finales": [tabla[k][-1] for k in range(len(xs))],
        "terminos": terminos,
        "gx": gx,
    }


def lagrange(xs: List[float], ys: List[float], x: float) -> Dict[str, Any]:
    """Polinomio de Lagrange para intervalos uniformes o no uniformes."""
    n = len(xs)
    if n != len(ys) or n < 2:
        raise ValueError("Se requieren al menos 2 puntos (xs, ys) del mismo tamaño.")
    bases = []
    terminos = []
    gx = 0.0
    for i in range(n):
        li = 1.0
        for j in range(n):
            if i != j:
                denom = xs[i] - xs[j]
                if abs(denom) < 1e-12:
                    raise ValueError("Valores de x repetidos en Lagrange.")
                li *= (x - xs[j]) / denom
        bases.append(li)
        termino = ys[i] * li
        terminos.append(termino)
        gx += termino
    return {
        "bases": bases,
        "terminos": terminos,
        "gx": gx,
    }


def newton_diferencias_divididas(xs: List[float], ys: List[float], x: float) -> Dict[str, Any]:
    """Newton con diferencias divididas para intervalos no uniformes."""
    n = len(xs)
    if n != len(ys) or n < 2:
        raise ValueError("Se requieren al menos 2 puntos (xs, ys) del mismo tamaño.")
    tabla = [list(ys)]
    for k in range(1, n):
        prev = tabla[k - 1]
        col = []
        for i in range(n - k):
            denom = xs[i + k] - xs[i]
            if denom == 0:
                raise ValueError("Valores de x repetidos en diferencias divididas.")
            col.append((prev[i + 1] - prev[i]) / denom)
        tabla.append(col)

    coefs = [tabla[k][0] for k in range(n)]
    gx = coefs[0]
    prod = 1.0
    terminos = [coefs[0]]
    for k in range(1, n):
        prod *= (x - xs[k - 1])
        termino = coefs[k] * prod
        gx += termino
        terminos.append(termino)
    return {
        "tabla": tabla,
        "coeficientes": coefs,
        "terminos": terminos,
        "gx": gx,
    }
