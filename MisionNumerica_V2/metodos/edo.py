"""Salas 6 y 7: Ecuaciones Diferenciales y Sistemas Runge-Kutta (OR/EDO)."""

from typing import Callable, Dict, Any, List, Optional


def euler_modificado(
    f: Callable[[float, float], float],
    y0: float,
    t0: float,
    h: float,
    pasos: int = 1,
    y1_estimado: Optional[float] = None,
) -> Dict[str, Any]:
    """Euler Modificado: y'_{n+1} = y_n + (h/2)*[f(y_n, t_n) + f(y_{n+1}, t_{n+1})]."""
    y = y0
    t = t0
    historial: List[Dict[str, Any]] = []
    for p in range(1, pasos + 1):
        t_sig = t + h
        f_act = f(y, t)
        y_pred = y1_estimado if (p == 1 and y1_estimado is not None) else (y + h * f_act)
        f_sig = f(y_pred, t_sig)
        y_sig = y + (h / 2.0) * (f_act + f_sig)
        historial.append({
            "paso": p,
            "t_n": t,
            "y_n": y,
            "t_sig": t_sig,
            "y_pred": y_pred,
            "f_n": f_act,
            "f_sig": f_sig,
            "y_sig": y_sig,
        })
        y, t = y_sig, t_sig
    return {"y_final": y, "historial": historial}


def runge_kutta_2(
    f: Callable[[float, float], float],
    y0: float,
    t0: float,
    h: float,
    pasos: int = 1,
) -> Dict[str, Any]:
    """RK2: k1 = h f(yn, tn), k2 = h f(yn+k1, tn+h), y_{n+1} = yn + 1/2 (k1 + k2)."""
    y, t = y0, t0
    historial = []
    for p in range(1, pasos + 1):
        k1 = h * f(y, t)
        k2 = h * f(y + k1, t + h)
        y_sig = y + 0.5 * (k1 + k2)
        historial.append({"paso": p, "t": t, "y": y, "k1": k1, "k2": k2, "y_sig": y_sig})
        y, t = y_sig, t + h
    return {"y_final": y, "historial": historial}


def runge_kutta_3(
    f: Callable[[float, float], float],
    y0: float,
    t0: float,
    h: float,
    pasos: int = 1,
) -> Dict[str, Any]:
    """RK3: k1=h f(yn,tn), k2=h f(yn+k1/2, tn+h/2), k3=h f(yn-k1+2k2, tn+h)."""
    y, t = y0, t0
    historial = []
    for p in range(1, pasos + 1):
        k1 = h * f(y, t)
        k2 = h * f(y + k1 / 2.0, t + h / 2.0)
        k3 = h * f(y - k1 + 2.0 * k2, t + h)
        y_sig = y + (k1 + 4.0 * k2 + k3) / 6.0
        historial.append({"paso": p, "t": t, "y": y, "k1": k1, "k2": k2, "k3": k3, "y_sig": y_sig})
        y, t = y_sig, t + h
    return {"y_final": y, "historial": historial}


def runge_kutta_4_simpson_1_3(
    f: Callable[[float, float], float],
    y0: float,
    t0: float,
    h: float,
    pasos: int = 1,
) -> Dict[str, Any]:
    """RK4 por 1/3 de Simpson."""
    y, t = y0, t0
    historial = []
    for p in range(1, pasos + 1):
        k1 = h * f(y, t)
        k2 = h * f(y + k1 / 2.0, t + h / 2.0)
        k3 = h * f(y + k2 / 2.0, t + h / 2.0)
        k4 = h * f(y + k3, t + h)
        y_sig = y + (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        historial.append({"paso": p, "t": t, "y": y, "k1": k1, "k2": k2, "k3": k3, "k4": k4, "y_sig": y_sig})
        y, t = y_sig, t + h
    return {"y_final": y, "historial": historial}


def runge_kutta_4_simpson_3_8(
    f: Callable[[float, float], float],
    y0: float,
    t0: float,
    h: float,
    pasos: int = 1,
) -> Dict[str, Any]:
    """RK4 por 3/8 de Simpson: 1/3, 2/3, h y pesos (k1 + 3k2 + 3k3 + k4)/8."""
    y, t = y0, t0
    historial = []
    for p in range(1, pasos + 1):
        k1 = h * f(y, t)
        k2 = h * f(y + k1 / 3.0, t + h / 3.0)
        k3 = h * f(y + k1 / 3.0 + k2 / 3.0, t + 2.0 * h / 3.0)
        k4 = h * f(y + k1 - k2 + k3, t + h)
        y_sig = y + (k1 + 3.0 * k2 + 3.0 * k3 + k4) / 8.0
        historial.append({"paso": p, "t": t, "y": y, "k1": k1, "k2": k2, "k3": k3, "k4": k4, "y_sig": y_sig})
        y, t = y_sig, t + h
    return {"y_final": y, "historial": historial}


def runge_kutta_orden_superior(
    g: Callable[[float, float, float], float],
    y0: float,
    yp0: float,
    t0: float,
    h: float,
    pasos: int = 1,
) -> Dict[str, Any]:
    """RK Orden Superior (2.º orden y'' = g(y', y, t)) con V_n = y'_n, U_n = y_n, q_n = t_n."""
    u, v, q = y0, yp0, t0
    historial = []
    for p in range(1, pasos + 1):
        k1 = h * v
        m1 = h * g(v, u, q)
        k2 = h * (v + m1)
        m2 = h * g(v + m1, u + k1, q + h)
        u_sig = u + 0.5 * (k1 + k2)
        v_sig = v + 0.5 * (m1 + m2)
        historial.append({
            "paso": p,
            "t": q,
            "y": u,
            "yp": v,
            "k1": k1,
            "m1": m1,
            "k2": k2,
            "m2": m2,
            "y_sig": u_sig,
            "yp_sig": v_sig,
        })
        u, v, q = u_sig, v_sig, q + h
    return {"y_final": u, "yp_final": v, "historial": historial}
