"""Sala 2: Raíces de Ecuaciones (criterios y fórmulas de la Ing. Oralia Zamora)."""

import math
from typing import Callable, List, Dict, Any, Optional


def metodo_grafico(
    f: Callable[[float], float],
    x_min: float,
    x_max: float,
    paso: float = 0.5,
) -> Dict[str, Any]:
    """Tabula f(x) y detecta los intervalos [a, b] donde ocurre cambio de signo."""
    if paso <= 0 or x_max <= x_min:
        raise ValueError("Rango o paso inválido para el método gráfico.")
    tabla = []
    n_pasos = int(math.floor((x_max - x_min) / paso + 1e-9))
    for k in range(n_pasos + 1):
        x = round(x_min + k * paso, 6)
        if x > x_max + 1e-9:
            break
        tabla.append((x, f(x)))
    intervalos = []
    for i in range(len(tabla) - 1):
        x1, y1 = tabla[i]
        x2, y2 = tabla[i + 1]
        if y1 == 0:
            intervalos.append((x1, x1))
        elif y1 * y2 < 0:
            intervalos.append((x1, x2))
    if tabla and tabla[-1][1] == 0:
        intervalos.append((tabla[-1][0], tabla[-1][0]))
    return {
        "tabla": tabla,
        "intervalos": intervalos,
    }


def metodo_bisectriz(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 0.001,
    max_iter: int = 100,
) -> Dict[str, Any]:
    """Bisectriz: x_i = (a+b)/2, criterio ε = |x_{i+1} - x_i| <= tol."""
    fa = f(a)
    fb = f(b)
    if abs(fa) < 1e-12:
        return {"raiz": a, "iteraciones": [{"iter": 1, "a": a, "b": b, "x": a, "fa": fa, "fb": fb, "fx": fa, "error": 0.0}]}
    if abs(fb) < 1e-12:
        return {"raiz": b, "iteraciones": [{"iter": 1, "a": a, "b": b, "x": b, "fa": fa, "fb": fb, "fx": fb, "error": 0.0}]}
    if fa * fb > 0:
        raise ValueError("f(a) y f(b) deben tener signos opuestos.")
    iteraciones: List[Dict[str, Any]] = []
    x_prev: Optional[float] = None
    x_act = (a + b) / 2.0
    for it in range(1, max_iter + 1):
        x_act = (a + b) / 2.0
        fx = f(x_act)
        error = abs(x_act - x_prev) if x_prev is not None else None
        iteraciones.append({
            "iter": it,
            "a": a,
            "b": b,
            "x": x_act,
            "fa": fa,
            "fb": fb,
            "fx": fx,
            "error": error,
        })
        if fx == 0 or (error is not None and error <= tol):
            break
        if fa * fx < 0:
            b = x_act
            fb = fx
        else:
            a = x_act
            fa = fx
        x_prev = x_act
    return {"raiz": x_act, "iteraciones": iteraciones}


def metodo_newton_raphson(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    tol: float = 0.001,
    max_iter: int = 100,
) -> Dict[str, Any]:
    """Newton-Raphson: x_{i+1} = x_i - f(x_i)/f'(x_i), ε = |x_{i+1} - x_i|."""
    iteraciones: List[Dict[str, Any]] = []
    x_act = x0
    for it in range(1, max_iter + 1):
        fx = f(x_act)
        dfx = df(x_act)
        if abs(dfx) < 1e-12:
            raise ValueError("Derivada cercana a cero en Newton-Raphson.")
        x_sig = x_act - fx / dfx
        error = abs(x_sig - x_act)
        iteraciones.append({
            "iter": it,
            "x_i": x_act,
            "fx": fx,
            "dfx": dfx,
            "x_sig": x_sig,
            "error": error,
        })
        x_act = x_sig
        if error <= tol:
            break
    return {"raiz": x_act, "iteraciones": iteraciones}


def metodo_falsa_posicion(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 0.001,
    max_iter: int = 100,
) -> Dict[str, Any]:
    """Falsa Posición: x = a - f(a)(b - a)/(f(b) - f(a)), ε = |x_{i+1} - x_i|."""
    fa = f(a)
    fb = f(b)
    if abs(fa) < 1e-12:
        return {"raiz": a, "iteraciones": [{"iter": 1, "a": a, "b": b, "x": a, "fa": fa, "fb": fb, "fx": fa, "error": 0.0}]}
    if abs(fb) < 1e-12:
        return {"raiz": b, "iteraciones": [{"iter": 1, "a": a, "b": b, "x": b, "fa": fa, "fb": fb, "fx": fb, "error": 0.0}]}
    if fa * fb > 0:
        raise ValueError("f(a) y f(b) deben tener signos opuestos.")
    iteraciones: List[Dict[str, Any]] = []
    x_prev: Optional[float] = None
    x_act = a
    for it in range(1, max_iter + 1):
        denom = fb - fa
        if abs(denom) < 1e-12:
            raise ValueError("División entre cero en Falsa Posición.")
        x_act = a - fa * (b - a) / denom
        fx = f(x_act)
        error = abs(x_act - x_prev) if x_prev is not None else None
        iteraciones.append({
            "iter": it,
            "a": a,
            "b": b,
            "x": x_act,
            "fa": fa,
            "fb": fb,
            "fx": fx,
            "error": error,
        })
        if abs(fx) < 1e-12 or (error is not None and error <= tol):
            break
        if fa * fx < 0:
            b = x_act
            fb = fx
        else:
            a = x_act
            fa = fx
        x_prev = x_act
    return {"raiz": x_act, "iteraciones": iteraciones}


def metodo_secante(
    f: Callable[[float], float],
    x0: float,
    x1: float,
    tol: float = 0.001,
    max_iter: int = 100,
) -> Dict[str, Any]:
    """Secante: x_{i+1} = x_i - f(x_i)(x_i - x_{i-1})/(f(x_i) - f(x_{i-1})), ε = |x_{i+1}-x_i|."""
    iteraciones: List[Dict[str, Any]] = []
    x_ant, x_act = x0, x1
    for it in range(1, max_iter + 1):
        f_ant = f(x_ant)
        f_act = f(x_act)
        denom = f_act - f_ant
        if abs(denom) < 1e-12:
            raise ValueError("División entre cero en el método de la Secante.")
        x_sig = x_act - f_act * (x_act - x_ant) / denom
        error = abs(x_sig - x_act)
        iteraciones.append({
            "iter": it,
            "x_ant": x_ant,
            "x_act": x_act,
            "f_ant": f_ant,
            "f_act": f_act,
            "x_sig": x_sig,
            "error": error,
        })
        x_ant, x_act = x_act, x_sig
        if error <= tol:
            break
    return {"raiz": x_act, "iteraciones": iteraciones}


def metodo_punto_fijo(
    g: Callable[[float], float],
    x0: float,
    tol: float = 0.001,
    max_iter: int = 100,
) -> Dict[str, Any]:
    """Punto Fijo: x_{i+1} = g(x_i), ε = |x_{i+1} - x_i|."""
    iteraciones: List[Dict[str, Any]] = []
    x_act = x0
    for it in range(1, max_iter + 1):
        x_sig = g(x_act)
        if not math.isfinite(x_sig) or abs(x_sig) > 1e9:
            raise ValueError("Punto fijo diverge para este valor inicial.")
        error = abs(x_sig - x_act)
        iteraciones.append({
            "iter": it,
            "x_i": x_act,
            "gx": x_sig,
            "error": error,
        })
        x_act = x_sig
        if error <= tol:
            break
    return {"raiz": x_act, "iteraciones": iteraciones}
