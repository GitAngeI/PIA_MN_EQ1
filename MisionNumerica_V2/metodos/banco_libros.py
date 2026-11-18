"""Banco académico parametrizado (>= 2 plantillas de libro por cada uno de los 32 métodos oficiales)."""

import math
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..ui.tema import normalizar_nombre_metodo

from .ajuste import (
    minimos_cuadrados_cubica,
    minimos_cuadrados_cuadratica,
    minimos_cuadrados_cuadratica_funcion,
    minimos_cuadrados_lineal_funcion,
    minimos_cuadrados_recta,
)
from .edo import (
    euler_modificado,
    runge_kutta_2,
    runge_kutta_3,
    runge_kutta_4_simpson_1_3,
    runge_kutta_4_simpson_3_8,
    runge_kutta_orden_superior,
)
from .integracion import (
    ABIERTAS_TABLA,
    CERRADAS_TABLA,
    integrar_tabla,
    newton_cotes_abiertas,
    newton_cotes_cerradas,
    regla_trapezoidal,
    simpson_tres_octavos,
    simpson_un_tercio,
)
from .interpolacion import (
    interpolacion_lineal,
    lagrange,
    newton_adelante,
    newton_atras,
    newton_diferencias_divididas,
)
from .raices import (
    metodo_bisectriz,
    metodo_falsa_posicion,
    metodo_grafico,
    metodo_newton_raphson,
    metodo_punto_fijo,
    metodo_secante,
)
from .sistemas import (
    eliminacion_gaussiana,
    es_diagonal_dominante,
    metodo_gauss_jordan,
    metodo_gauss_seidel,
    metodo_jacobi,
    metodo_montante,
)


def _paso_num(
    titulo: str,
    pregunta: str,
    esperado: float,
    pista: str,
    tolerancia: float = 0.02,
    tooltip: str = "",
) -> Dict[str, Any]:
    return {
        "tipo": "numero",
        "titulo": titulo,
        "pregunta": pregunta,
        "esperado": float(esperado),
        "tolerancia": float(tolerancia),
        "pista": pista,
        "tooltip": tooltip or f"Ingresa el valor numérico de {titulo.split(':')[-1].strip()} (tol. +- {tolerancia}).",
    }


def _paso_opcion(
    titulo: str,
    pregunta: str,
    opciones: List[str],
    indice_correcto: int,
    pista: str,
    tooltip: str = "",
) -> Dict[str, Any]:
    return {
        "tipo": "opcion",
        "titulo": titulo,
        "pregunta": pregunta,
        "opciones": opciones,
        "indice_correcto": int(indice_correcto),
        "pista": pista,
        "tooltip": tooltip or f"Elige la opción correcta para {titulo.split(':')[-1].strip()}.",
    }


def _red(v: float, dec: int = 4) -> float:
    return round(float(v), dec)


def _muestrear_curva(
    fn: Callable[[float], float],
    x_min: float,
    x_max: float,
    n_pts: int = 85,
) -> List[Tuple[float, float]]:
    if x_max <= x_min or n_pts < 2:
        return []
    pts: List[Tuple[float, float]] = []
    paso = (x_max - x_min) / (n_pts - 1)
    for i in range(n_pts):
        x = x_min + i * paso
        try:
            y = float(fn(x))
            if math.isfinite(y) and abs(y) < 1e7:
                pts.append((round(x, 6), round(y, 6)))
        except Exception:
            continue
    return pts


def _matriz_a_filas_texto(A: List[List[float]], b: List[float]) -> List[List[Any]]:
    filas = []
    for i, fila in enumerate(A):
        eq = " + ".join(
            f"{coef:g}*x{j+1}" if coef >= 0 else f"({coef:g})*x{j+1}"
            for j, coef in enumerate(fila)
        )
        filas.append([f"Ec.{i+1}", f"{eq} = {b[i]:g}"])
    return filas


def _resolver_3x3_para_solucion(r: random.Random, diag_dom: bool = False) -> Tuple[List[List[float]], List[float], List[int]]:
    sol = [r.choice([-3, -2, -1, 1, 2, 3, 4]) for _ in range(3)]
    for _ in range(80):
        if diag_dom:
            A = []
            for i in range(3):
                fila = [r.choice([-2, -1, 1, 2]) for _ in range(3)]
                suma_otros = sum(abs(fila[j]) for j in range(3) if j != i)
                fila[i] = r.choice([1, -1]) * (suma_otros + r.randint(2, 4))
                A.append(fila)
            if not es_diagonal_dominante(A):
                continue
        else:
            A = [[r.choice([-3, -2, -1, 1, 2, 3, 4]) for _ in range(3)] for _ in range(3)]
            for i in range(3):
                if A[i][i] == 0:
                    A[i][i] = 2
        try:
            res_mon = metodo_montante([f[:] for f in A], [sum(A[i][j] * sol[j] for j in range(3)) for i in range(3)])
            pivotes_ok = all(abs(p["pivote"]) > 1e-6 for p in res_mon["pasos"])
            if abs(res_mon["determinante"]) >= 1.0 and pivotes_ok:
                b = [sum(A[i][j] * sol[j] for j in range(3)) for i in range(3)]
                return A, b, sol
        except Exception:
            continue
    A_fb = [[4, 1, -1], [1, 5, 1], [-1, 1, 4]]
    b_fb = [sum(A_fb[i][j] * sol[j] for j in range(3)) for i in range(3)]
    return A_fb, b_fb, sol


# ==============================================================================
# SALA 1: INTERPOLACIÓN
# ==============================================================================

def _s1_il_chapra_ln(r: random.Random) -> Dict[str, Any]:
    a = r.choice([1, 2, 3, 4])
    b = a + r.choice([2, 3, 4])
    x = a + r.randint(1, b - a - 1)
    c1 = round(r.uniform(1.0, 2.5), 2)
    c0 = round(r.uniform(0.0, 2.0), 2)
    f_true = lambda t: c0 + c1 * math.log(t)
    fa = _red(f_true(a), 4)
    fb = _red(f_true(b), 4)
    fx_real = _red(f_true(x), 4)
    res = interpolacion_lineal(a, fa, b, fb, x, fx_real)
    curva_real = _muestrear_curva(f_true, max(0.5, a - 0.5), b + 0.5)
    curva_recta = [(a, fa), (b, fb)]
    return {
        "metodo": "Interpolación lineal",
        "sala_id": 1,
        "oxigeno_seg": 240,
        "formula": "g(x) = [(f(b) - f(a)) / (b - a)] * (x - a) + f(a)   |   e = |f(x) - g(x)|",
        "enunciado": (
            f"Calibración térmica de sensor por interpolación lineal. Se dan los extremos conocidos a = {a} con f(a) = {fa}, "
            f"y b = {b} con f(b) = {fb}. Para el punto objetivo x = {x}, también se da el valor medido real f({x}) = {fx_real} "
            f"(este f({x}) solo se usa al final para el error). Calcula en orden: "
            f"1) la pendiente m con f(a) y f(b), 2) la estimación g({x}), y 3) el error absoluto e = |f({x}) - g({x})|."
        ),
        "datos_tabla": (
            ["Rol del dato", "Abscisa x", "Valor conocido"],
            [
                ["Extremo inferior (a)", f"a = {a}", f"f(a) = {fa}"],
                ["Extremo superior (b)", f"b = {b}", f"f(b) = {fb}"],
                ["Objetivo a estimar (x)", f"x = {x}", f"f(x) real = {fx_real} (solo inciso 3: error)"],
            ],
        ),
        "tabla_progresiva": {
            "titulo": "Resumen de Interpolación Lineal",
            "columnas": ["Magnitud", "Expresión", "Valor"],
            "filas": [
                {"paso_min": 0, "valores": ["Extremo a", f"a = {a}, f(a)", fa]},
                {"paso_min": 0, "valores": ["Extremo b", f"b = {b}, f(b)", fb]},
                {"paso_min": 1, "valores": ["Pendiente m", "(f(b)-f(a))/(b-a)", _red(res["pendiente"], 4)]},
                {"paso_min": 2, "valores": [f"Estimación g({x})", f"m*({x}-{a})+f({a})", _red(res["gx"], 4)]},
                {"paso_min": 3, "valores": ["Error absoluto", f"|f({x}) - g({x})|", _red(res["error"], 4)]},
            ],
        },
        "grafica": {
            "tipo": "funcion",
            "titulo": f"Interpolación Lineal en [{a}, {b}]",
            "xlabel": "x",
            "ylabel": "f(x)",
            "curva_pts": curva_real,
            "curva_modelo_pts": curva_recta,
            "curva_modelo_paso_min": 1,
            "puntos_datos": [(a, fa), (b, fb)],
            "marcadores": [
                {"x": x, "y": fx_real, "etiqueta": f"f({x})={fx_real}", "color": "#5CE0A0", "paso_min": 0},
                {"x": x, "y": res["gx"], "etiqueta": f"g({x})={_red(res['gx'],3)}", "color": "#FFD166", "paso_min": 2},
            ],
        },
        "pasos": [
            _paso_num(
                "Paso 1: Pendiente m",
                f"Con f(b) = {fb}, f(a) = {fa}, b = {b} y a = {a}, calcula m = (f(b) - f(a)) / (b - a):",
                res["pendiente"],
                f"Sustituye f(b)={fb} y f(a)={fa}: ({fb} - {fa}) / ({b} - {a}). No uses f({x}) aquí.",
                0.015,
                tooltip=f"Pendiente secante entre a={a} [f(a)={fa}] y b={b} [f(b)={fb}].",
            ),
            _paso_num(
                "Paso 2: Estimación g(x)",
                f"Usando m, x = {x}, a = {a} y f(a) = {fa}, calcula g({x}) = m * ({x} - {a}) + {fa}:",
                res["gx"],
                f"Multiplica la pendiente m por (x - a) = ({x} - {a}) y suma f(a) = {fa}.",
                0.015,
                tooltip=f"Valor interpolado g({x}) evaluado en la recta entre f(a) y f(b).",
            ),
            _paso_num(
                "Paso 3: Error absoluto e",
                f"Usando el valor real dado f({x}) = {fx_real} y g({x}) del Paso 2, calcula e = |{fx_real} - g({x})|:",
                res["error"],
                f"Solo en este paso se utiliza f({x}) real = {fx_real}: resta g({x}) y toma el valor absoluto.",
                0.015,
                tooltip=f"Diferencia absoluta |f({x}) - g({x})| respecto al dato real medido f({x})={fx_real}.",
            ),
        ],
        "resultado_final": res["gx"],
    }


def _s1_il_nieves_densidad(r: random.Random) -> Dict[str, Any]:
    t0 = r.choice([10, 15, 20, 25])
    dt = r.choice([10, 15])
    t1 = t0 + dt
    t_obj = t0 + r.choice([3, 4, 5, 6, 7])
    alpha = round(r.uniform(0.003, 0.006), 4)
    base = round(r.uniform(995.0, 999.0), 2)
    f_dens = lambda T: base - alpha * (T - 4.0) ** 1.85
    fa = _red(f_dens(t0), 4)
    fb = _red(f_dens(t1), 4)
    fx_real = _red(f_dens(t_obj), 4)
    res = interpolacion_lineal(t0, fa, t1, fb, t_obj, fx_real)
    curva_real = _muestrear_curva(f_dens, t0 - 2.0, t1 + 2.0)
    return {
        "metodo": "Interpolación lineal",
        "sala_id": 1,
        "oxigeno_seg": 240,
        "formula": "g(x) = [(f(b) - f(a)) / (b - a)] * (x - a) + f(a)   |   e = |f(x) - g(x)|",
        "enunciado": (
            f"Tabla termodinámica de densidad rho(T) [kg/m³] del refrigerante: se conocen los extremos a = {t0} °C con f(a) = {fa}, "
            f"y b = {t1} °C con f(b) = {fb}. Se busca estimar en x = {t_obj} °C sabiendo que el valor medido real es f({t_obj}) = {fx_real} "
            f"(solo para el error del Paso 3). Calcula: 1) la pendiente m, 2) la densidad interpolada g({t_obj}), y 3) el error absoluto e."
        ),
        "datos_tabla": (
            ["Rol del dato", "T (°C) [x]", "Densidad rho [kg/m³]"],
            [
                ["Extremo inferior (a)", f"a = {t0}", f"f(a) = {fa}"],
                ["Extremo superior (b)", f"b = {t1}", f"f(b) = {fb}"],
                ["Objetivo a estimar (x)", f"x = {t_obj}", f"f(x) real = {fx_real} (solo inciso 3: error)"],
            ],
        ),
        "tabla_progresiva": {
            "titulo": "Interpolación Termodinámica",
            "columnas": ["Variable", "Cálculo", "Resultado"],
            "filas": [
                {"paso_min": 1, "valores": ["Pendiente m", f"({fb}-{fa})/({t1}-{t0})", _red(res["pendiente"], 4)]},
                {"paso_min": 2, "valores": [f"Estimación g({t_obj})", "recta secante", _red(res["gx"], 4)]},
                {"paso_min": 3, "valores": [f"Error |f({t_obj}) - g({t_obj})|", "|real - g|", _red(res["error"], 4)]},
            ],
        },
        "grafica": {
            "tipo": "funcion",
            "titulo": "Densidad vs Temperatura",
            "xlabel": "T (°C)",
            "ylabel": "rho (kg/m³)",
            "curva_pts": curva_real,
            "curva_modelo_pts": [(t0, fa), (t1, fb)],
            "curva_modelo_paso_min": 1,
            "puntos_datos": [(t0, fa), (t1, fb)],
            "marcadores": [
                {"x": t_obj, "y": fx_real, "etiqueta": f"f({t_obj}) real", "color": "#5CE0A0", "paso_min": 0},
                {"x": t_obj, "y": res["gx"], "etiqueta": f"g({t_obj}) est.", "color": "#FFD166", "paso_min": 2},
            ],
        },
        "pasos": [
            _paso_num(
                "Paso 1: Razón de cambio m",
                f"Con f(b) = {fb}, f(a) = {fa}, b = {t1} y a = {t0}, calcula m = (f(b) - f(a)) / (b - a):",
                res["pendiente"],
                f"Aplica la pendiente entre los extremos: ({fb} - {fa}) / ({t1} - {t0}). No uses f({t_obj}) aquí.",
                0.02,
                tooltip=f"Pendiente m entre a={t0} [f(a)={fa}] y b={t1} [f(b)={fb}].",
            ),
            _paso_num(
                "Paso 2: Densidad estimada g(x)",
                f"Usando m, x = {t_obj}, a = {t0} y f(a) = {fa}, calcula g({t_obj}) = m * ({t_obj} - {t0}) + {fa}:",
                res["gx"],
                f"Sustituye T = {t_obj} en g(T) = m*(T - {t0}) + {fa}.",
                0.03,
                tooltip=f"Valor interpolado de densidad g({t_obj}).",
            ),
            _paso_num(
                "Paso 3: Error absoluto e",
                f"Con el valor real dado f({t_obj}) = {fx_real} y g({t_obj}), calcula e = |{fx_real} - g({t_obj})|:",
                res["error"],
                f"Solo aquí usas el dato de laboratorio f({t_obj}) = {fx_real}: calcula la magnitud |f(x) - g(x)|.",
                0.02,
                tooltip="Diferencia absoluta frente al valor medido de laboratorio.",
            ),
        ],
        "resultado_final": res["gx"],
    }


def _construir_newton_finitas(r: random.Random, adelante: bool, contexto: str) -> Dict[str, Any]:
    h = r.choice([0.5, 1.0, 2.0]) if "vapor" in contexto else r.choice([0.2, 0.5, 1.0])
    x0 = r.choice([1.0, 2.0, 4.0, 10.0]) if "vapor" in contexto else r.choice([0.5, 1.0, 1.5])
    
    # CAMBIO 1: Generamos solo 3 puntos en vez de 4
    xs = [round(x0 + i * h, 4) for i in range(3)]
    
    c2 = r.choice([0.3, -0.25, 0.4])
    c1 = round(r.uniform(0.8, 2.2), 2)
    c0 = round(r.uniform(1.0, 6.0), 2)
    pol = lambda t: c2 * (t - x0) ** 2 + c1 * (t - x0) + c0
    ys = [_red(pol(x), 4) for x in xs]
    
    if adelante:
        frac = r.choice([0.35, 0.55, 0.75])
        x_eval = round(xs[0] + frac * h, 4)
        res = newton_adelante(xs, ys, x_eval)
        metodo = "Newton hacia adelante"
        
        # CAMBIO 2: La fórmula solo llega hasta la segunda diferencia (D2)
        formula = "s = (x - x1)/h   |   g(x) = y1 + D1*s + D2*s*(s-1)/2!"
        d_list = res["diferencias_iniciales"]
        simb = "D"
        nota_s = f"s = ({x_eval} - {xs[0]}) / {h}"
        pista_s = "Usa x1 (el primer nodo de la tabla): s = (x - x1) / h."
        pista_dif = "Calcula las diferencias finitas progresivas D1 = y2 - y1 y D2 = (y3 - y2) - (y2 - y1)."
        dif_pedida = d_list[2]
        preg_dif = "Calcula la segunda diferencia progresiva inicial D2 (Delta^2 y1):"
    else:
        frac = r.choice([0.35, 0.55, 0.75])
        x_eval = round(xs[-1] - frac * h, 4)
        res = newton_atras(xs, ys, x_eval)
        metodo = "Newton hacia atrás"
        
        # CAMBIO 3: La fórmula solo llega hasta la segunda diferencia (V2)
        formula = "s = (x - xn)/h   |   g(x) = yn + V1*s + V2*s*(s+1)/2!"
        d_list = res["diferencias_finales"]
        simb = "V"
        nota_s = f"s = ({x_eval} - {xs[-1]}) / {h}"
        pista_s = "Usa xn (el último nodo de la tabla): s será negativo."
        pista_dif = "Calcula las diferencias regresivas desde el extremo inferior: V1 = yn - y(n-1), V2 = V1(n) - V1(n-1)."
        dif_pedida = d_list[2]
        preg_dif = "Calcula la segunda diferencia regresiva final V2 (Nabla^2 yn):"

    filas_tabla = [
        {"paso_min": 0, "valores": ["Nodos", f"{xs}", f"{ys}"]},
        {"paso_min": 1, "valores": ["Parámetro s", nota_s, _red(res["s"], 4)]},
        {"paso_min": 2, "valores": [f"Diferencias ({simb}1, {simb}2)", "orden 1 y 2", f"{_red(d_list[1],4)}, {_red(d_list[2],4)}"]},
        {"paso_min": 3, "valores": [f"Polinomio g({x_eval})", "evaluación Newton", _red(res["gx"], 4)]},
    ]

    def g_poly(xq: float) -> float:
        r_tmp = newton_adelante(xs, ys, xq) if adelante else newton_atras(xs, ys, xq)
        return r_tmp["gx"]

    curva = _muestrear_curva(g_poly, xs[0] - 0.15 * h, xs[-1] + 0.15 * h)
    
    # CAMBIO 4: Actualizamos el enunciado para decir "3 nodos" y los 3 incisos pedidos
    enunc = (
        f"Tabla equiespaciada de {contexto} (paso uniforme h = {h}). "
        f"Con los 3 nodos tabulados y para x = {x_eval}, calcula en orden: "
        f"1) el parámetro s, 2) la segunda diferencia {simb}2, y 3) el valor interpolado g({x_eval}) mediante {metodo}."
    )
    
    return {
        "metodo": metodo,
        "sala_id": 1,
        "oxigeno_seg": 180,
        "formula": formula,
        "enunciado": enunc,
        
        # CAMBIO 5: Rango de la tabla de datos ajustado a 3
        "datos_tabla": (["i", "x_i", "y_i"], [[i + 1, xs[i], ys[i]] for i in range(3)]),
        "tabla_progresiva": {
            "titulo": f"Tabla de Trabajo ({metodo})",
            "columnas": ["Etapa", "Detalle", "Valor"],
            "filas": filas_tabla,
        },
        "grafica": {
            "tipo": "funcion",
            "titulo": f"{metodo} ({contexto})",
            "xlabel": "x",
            "ylabel": "y(x)",
            "curva_pts": [],
            "curva_modelo_pts": curva,
            "curva_modelo_paso_min": 2,
            "puntos_datos": list(zip(xs, ys)),
            "marcadores": [
                {"x": x_eval, "y": res["gx"], "etiqueta": f"g({x_eval})", "color": "#FFD166", "paso_min": 3},
            ],
        },
        "pasos": [
            _paso_num("Paso 1: Coordenada local s", f"Con h = {h}, calcula {nota_s}:", res["s"], pista_s, 0.015),
            _paso_num(f"Paso 2: Diferencia de orden 2 ({simb}2)", preg_dif, dif_pedida, pista_dif, 0.025),
            
            # CAMBIO 6: Pista actualizada para no mencionar D3
            _paso_num("Paso 3: Evaluar g(x)", f"Calcula g({x_eval}) sustituyendo en la serie de Newton:", res["gx"], f"Combina y_base + {simb}1*s + {simb}2*s*(s{'-' if adelante else '+'}1)/2.", 0.025),
        ],
        "resultado_final": res["gx"],
    }


def _construir_no_uniforme(r: random.Random, usar_lagrange: bool, tema: str) -> Dict[str, Any]:
    if tema == "log":
        base_x = r.choice([1.0, 2.0])
        xs = [base_x, round(base_x + r.choice([1.5, 2.0]), 2), round(base_x + r.choice([4.0, 5.0]), 2)]
        k = round(r.uniform(1.2, 2.5), 2)
        ys = [_red(k * math.log(x) + 1.0, 4) for x in xs]
        x_eval = round((xs[0] + xs[1]) / 2.0, 2)
        if x_eval in xs:
            x_eval = round(xs[0] + 0.6, 2)
        titulo_ctx = "calibración logarítmica (nodos desiguales)"
    else:
        xs = [r.choice([0.5, 1.0]), r.choice([2.0, 2.5]), r.choice([4.5, 5.0])]
        a_p = r.choice([0.3, -0.25, 0.4])
        b_p = round(r.uniform(0.8, 1.8), 2)
        c_p = round(r.uniform(1.0, 4.0), 2)
        ys = [_red(a_p * x * x + b_p * x + c_p, 4) for x in xs]
        x_eval = round(r.choice([1.4, 3.0, 3.4]), 2)
        titulo_ctx = "respuesta de sensor no equidistante"

    if usar_lagrange:
        res = lagrange(xs, ys, x_eval)
        metodo = "Lagrange"
        formula = "g(x) = sum_{i=1..n} y_i * L_i(x),   L_i(x) = prod_{j!=i} (x - x_j)/(x_i - x_j)"
        g_fn = lambda t: lagrange(xs, ys, t)["gx"]
        filas_tp = [
            {"paso_min": 1, "valores": ["L1(x)", f"Producto sin x1={xs[0]}", _red(res["bases"][0], 4)]},
            {"paso_min": 2, "valores": ["L2(x)", f"Producto sin x2={xs[1]}", _red(res["bases"][1], 4)]},
            {"paso_min": 2, "valores": ["L3(x)", f"Producto sin x3={xs[2]}", _red(res["bases"][2], 4)]},
            {"paso_min": 3, "valores": [f"g({x_eval})", "sum y_i * L_i(x)", _red(res["gx"], 4)]},
        ]
        enunc = (
            f"Muestreo de {titulo_ctx} con 3 nodos no equidistantes. Mediante {metodo}, calcula para x = {x_eval}: "
            f"1) el multiplicador base L1({x_eval}), 2) la base L2({x_eval}), y 3) el valor interpolado g({x_eval})."
        )
        pasos = [
            _paso_num(
                "Paso 1: Base L1(x)",
                f"Calcula L1({x_eval}) = [({x_eval}-x2)({x_eval}-x3)] / [(x1-x2)(x1-x3)]:",
                res["bases"][0],
                "Sustituye x2, x3 en el numerador y divide entre (x1-x2)*(x1-x3).",
                0.02,
                tooltip="Multiplicador L1(x) de Lagrange (adimensional; i=1 usa nodos x2 y x3).",
            ),
            _paso_num(
                "Paso 2: Base L2(x)",
                f"Calcula L2({x_eval}) = [({x_eval}-x1)({x_eval}-x3)] / [(x2-x1)(x2-x3)]:",
                res["bases"][1],
                "Cuida el signo de (x2 - x1) y (x2 - x3) en el denominador.",
                0.02,
                tooltip="Multiplicador L2(x) (nota: siempre se cumple L1 + L2 + L3 = 1).",
            ),
            _paso_num(
                "Paso 3: Polinomio g(x)",
                f"Calcula g({x_eval}) = y1*L1 + y2*L2 + y3*L3:",
                res["gx"],
                "Calcula L3 = 1 - L1 - L2 y suma los productos y_i * L_i.",
                0.03,
                tooltip=f"Valor interpolado g({x_eval}) combinando los 3 nodos tabulados.",
            ),
        ]
    else:
        res = newton_diferencias_divididas(xs, ys, x_eval)
        metodo = "Newton con diferencias divididas"
        formula = "D1,i=(y_{i+1}-y_i)/(x_{i+1}-x_i)   |   g(x)=y1 + D1,1*(x-x1) + D2,1*(x-x1)*(x-x2)"
        g_fn = lambda t: newton_diferencias_divididas(xs, ys, t)["gx"]
        d0, d1, d2 = res["coeficientes"]
        d1_2 = res["tabla"][1][1]
        filas_tp = [
            {"paso_min": 0, "valores": ["D0 = y1", f"y1 en x1={xs[0]}", _red(d0, 4)]},
            {"paso_min": 1, "valores": ["D1,1", f"(y2-y1)/({xs[1]}-{xs[0]})", _red(d1, 4)]},
            {"paso_min": 1, "valores": ["D1,2", f"(y3-y2)/({xs[2]}-{xs[1]})", _red(d1_2, 4)]},
            {"paso_min": 2, "valores": ["D2,1", "(D1,2 - D1,1)/(x3 - x1)", _red(d2, 4)]},
            {"paso_min": 3, "valores": [f"g({x_eval})", "polinomio Newton", _red(res["gx"], 4)]},
        ]
        enunc = (
            f"Muestreo de {titulo_ctx} con 3 nodos no equidistantes. Mediante {metodo}, calcula para x = {x_eval}: "
            f"1) la primera diferencia dividida D1,1, 2) la segunda diferencia dividida D2,1, y 3) el valor interpolado g({x_eval})."
        )
        pasos = [
            _paso_num(
                "Paso 1: Primera diferencia D1,1",
                "Calcula D1,1 = (y2 - y1) / (x2 - x1):",
                d1,
                "Divide el incremento (y2 - y1) entre (x2 - x1) usando fila 1 y fila 2.",
                0.02,
                tooltip="Pendiente dividida de primer orden D1,1 entre el primer par de puntos.",
            ),
            _paso_num(
                "Paso 2: Segunda diferencia D2,1",
                "Calcula D2,1 = (D1,2 - D1,1) / (x3 - x1):",
                d2,
                "Calcula primero D1,2 = (y3-y2)/(x3-x2) y luego divide (D1,2 - D1,1) entre (x3 - x1).",
                0.02,
                tooltip="Segunda diferencia dividida D2,1 (divisor externo x3 - x1).",
            ),
            _paso_num(
                "Paso 3: Estimación g(x)",
                f"Calcula g({x_eval}) = D0 + D1,1*(x-x1) + D2,1*(x-x1)*(x-x2):",
                res["gx"],
                "Sustituye D0=y1, D1,1, D2,1 y evalúa en el valor objetivo x.",
                0.03,
                tooltip=f"Aproximación polinomial g({x_eval}) por diferencias divididas.",
            ),
        ]

    curva = _muestrear_curva(g_fn, min(xs) - 0.3, max(xs) + 0.3)
    return {
        "metodo": metodo,
        "sala_id": 1,
        "oxigeno_seg": 360,
        "formula": formula,
        "enunciado": enunc,
        "datos_tabla": (["i", "x_i", "y_i"], [[i + 1, xs[i], ys[i]] for i in range(3)]),
        "tabla_progresiva": {"titulo": f"Construcción ({metodo})", "columnas": ["Término", "Fórmula", "Valor"], "filas": filas_tp},
        "grafica": {
            "tipo": "funcion",
            "titulo": f"{metodo} en x={x_eval}",
            "xlabel": "x",
            "ylabel": "g(x)",
            "curva_pts": [],
            "curva_modelo_pts": curva,
            "curva_modelo_paso_min": 2,
            "puntos_datos": list(zip(xs, ys)),
            "marcadores": [{"x": x_eval, "y": res["gx"], "etiqueta": f"g({x_eval})", "color": "#FFD166", "paso_min": 3}],
        },
        "pasos": pasos,
        "resultado_final": res["gx"],
    }


# ==============================================================================
# SALA 2: RAÍCES DE ECUACIONES
# ==============================================================================

def _s2_grafico_gen(r: random.Random, modo: str) -> Dict[str, Any]:
    if modo == "paracaidas":
        k = round(r.uniform(0.35, 0.65), 2)
        c = round(r.uniform(0.25, 0.55), 2)
        f = lambda x: math.exp(-k * x) - c
        f_txt = f"e^(-{k}x) - {c}"
        x_ini, x_fin, paso = 0.0, 3.0, 0.5
        ctx = "coeficiente de arrastre en descenso de cápsula"
    else:
        p = r.choice([3, 4, 5])
        q = r.choice([2, 3])
        f = lambda x: x ** 3 - p * x - q
        f_txt = f"x^3 - {p}x - {q}"
        x_ini, x_fin, paso = 0.0, 3.5, 0.5
        ctx = "ecuación cúbica de volumen en tanque esférico"

    res = metodo_grafico(f, x_ini, x_fin, paso)
    if not res["intervalos"]:
        # Garantizar un cambio de signo siempre válido
        f = lambda x: x ** 2 - 3.0
        f_txt = "x^2 - 3"
        x_ini, x_fin, paso = 0.0, 3.0, 0.5
        res = metodo_grafico(f, x_ini, x_fin, paso)

    iv = res["intervalos"][0]
    raiz_aprox = 0.5 * (iv[0] + iv[1])
    x_eval_ej = round(x_ini + paso * 2, 3)
    f_eval_ej = f(x_eval_ej)
    curva = _muestrear_curva(f, x_ini - 0.2, x_fin + 0.2)
    filas_tp = [
        {"paso_min": 0 if i < 2 else 1, "valores": [round(x, 3), _red(fx, 4), "+" if fx > 0 else ("-" if fx < 0 else "0")]}
        for i, (x, fx) in enumerate(res["tabla"])
    ]
    return {
        "metodo": "Gráfico",
        "sala_id": 2,
        "oxigeno_seg": 240,
        "formula": "Tabulación x_i -> f(x_i): cambio de signo f(x_i)*f(x_{i+1}) <= 0 indica raíz en [x_i, x_{i+1}]",
        "enunciado": (
            f"Para {ctx}, tabula f(x) = {f_txt} en [{x_ini}, {x_fin}] con incremento delta_x = {paso}. "
            f"Calcula en orden: 1) f({x_eval_ej}), 2) el límite inferior a del primer subintervalo [a, b] con cambio de signo, "
            f"y 3) la estimación de raíz por punto medio (a + b)/2."
        ),
        "datos_tabla": (["Parámetro", "Valor"], [["Función f(x)", f_txt], ["Rango [x_ini, x_fin]", f"[{x_ini}, {x_fin}]"], ["Incremento delta_x", paso]]),
        "tabla_progresiva": {"titulo": "Tabulación de Valores f(x)", "columnas": ["x", "f(x)", "Signo"], "filas": filas_tp},
        "grafica": {
            "tipo": "funcion",
            "titulo": f"Cruce por cero de f(x) = {f_txt}",
            "xlabel": "x",
            "ylabel": "f(x)",
            "curva_pts": curva,
            "puntos_datos": [(x, fx) for x, fx in res["tabla"]],
            "marcadores": [{"x": raiz_aprox, "y": 0.0, "etiqueta": f"Sub [{iv[0]},{iv[1]}]", "color": "#5CE0A0", "paso_min": 2}],
        },
        "pasos": [
            _paso_num("Paso 1: Evaluar nodo de tabla", f"Evalúa f({x_eval_ej}) para el nodo x = {x_eval_ej}:", f_eval_ej, f"Sustituye x = {x_eval_ej} en f(x) = {f_txt} (radianes si aplica).", 0.025),
            _paso_num("Paso 2: Límite inferior del cambio de signo", "Indica el extremo izquierdo a del primer intervalo [a, b] donde cambia el signo:", iv[0], "Busca dos filas consecutivas de la tabulación cuyo producto f(x_i)*f(x_{i+1}) <= 0.", 0.01),
            _paso_num("Paso 3: Estimación del punto medio", "Estima la raíz por punto medio (a + b) / 2 del intervalo hallado:", raiz_aprox, "Promedia los dos extremos del subintervalo de cambio de signo.", 0.02),
        ],
        "resultado_final": raiz_aprox,
    }


def _construir_raiz_bracket(r: random.Random, metodo: str, familia: str) -> Dict[str, Any]:
    if familia == "cubica":
        p = r.choice([2, 3, 4])
        q = r.choice([2, 3, 5])
        f = lambda x, p=p, q=q: x ** 3 - p * x - q
        f_txt = f"x^3 - {p}x - {q}"
        a, b = 1.0, 3.0
        while f(a) * f(b) >= 0:
            b += 0.5
        ctx = "ecuación cúbica de estado de gas / reactor"
    else:
        alpha = round(r.uniform(0.35, 0.85), 2)
        f = lambda x, al=alpha: math.exp(-x) - al * x
        f_txt = f"e^(-x) - {alpha}x"
        a, b = 0.0, 2.0
        while f(a) * f(b) >= 0:
            b += 0.5
        ctx = "balance de presión y temperatura en tobera"

    es_bis = metodo == "Bisectriz"
    res = None
    for _ in range(8):
        res = (
            metodo_bisectriz(f, a, b, tol=1e-9, max_iter=6)
            if es_bis
            else metodo_falsa_posicion(f, a, b, tol=1e-9, max_iter=6)
        )
        if len(res["iteraciones"]) >= 3:
            break
        b += 0.5
    its = res["iteraciones"]
    it1, it2 = its[0], its[1]
    fa_ini = _red(f(a), 4)
    fb_ini = _red(f(b), 4)
    curva = _muestrear_curva(f, a - 0.2, b + 0.2)
    filas_tp = [
        {"paso_min": idx, "valores": [it["iter"], _red(it["a"], 4), _red(it["b"], 4), _red(it["x"], 4), _red(it["fx"], 4)]}
        for idx, it in enumerate(its[:3], start=1)
    ]
    if es_bis:
        formula = "xr = (a + b) / 2   |   Si f(a)*f(xr) < 0 -> b=xr; si no -> a=xr"
        pista1 = "Promedia los límites iniciales a y b."
        pista3 = "Determina cuál mitad conserva el cambio de signo y calcula su nuevo punto medio."
    else:
        formula = "xr = a - [f(a)*(b - a)] / [f(b) - f(a)]"
        pista1 = "Sustituye a, b, f(a) y f(b) en xr = a - f(a)*(b - a) / (f(b) - f(a))."
        pista3 = "Evalúa f(xr1) para elegir el nuevo intervalo [a, b] y repite la fórmula de falsa posición."

    return {
        "metodo": metodo,
        "sala_id": 2,
        "oxigeno_seg": 360,
        "formula": formula,
        "enunciado": (
            f"Para {ctx}, analiza f(x) = {f_txt} en el intervalo inicial [a={a}, b={b}] (con f(a)={fa_ini} y f(b)={fb_ini}). "
            f"Con {metodo}, calcula en orden: 1) la primera aproximación xr1, 2) el subintervalo que conserva la raíz según el signo de f(a)*f(xr1), "
            f"y 3) la segunda aproximación xr2."
        ),
        "datos_tabla": (["Parámetro", "Valor"], [["Función f(x)", f_txt], ["Extremo a inicial", a], ["Extremo b inicial", b], ["f(a) inicial", fa_ini], ["f(b) inicial", fb_ini]]),
        "tabla_progresiva": {"titulo": f"Iteraciones ({metodo})", "columnas": ["Iter", "a", "b", "xr", "f(xr)"], "filas": filas_tp},
        "grafica": {
            "tipo": "funcion",
            "titulo": f"{metodo}: f(x) = {f_txt}",
            "xlabel": "x",
            "ylabel": "f(x)",
            "curva_pts": curva,
            "marcadores": [
                {"x": it1["x"], "y": it1["fx"], "etiqueta": "xr1", "color": "#F4A261", "paso_min": 1},
                {"x": it2["x"], "y": it2["fx"], "etiqueta": "xr2", "color": "#5CE0A0", "paso_min": 3},
            ],
        },
        "pasos": [
            _paso_num("Paso 1: Primera aproximación xr1", f"Calcula xr1 en [a={a}, b={b}]:", it1["x"], pista1, 0.02),
            _paso_opcion("Paso 2: Nuevo subintervalo", f"Conociendo f(xr1) = {_red(it1['fx'], 4)} y f({a}) = {_red(it1['fa'], 4)}, ¿qué intervalo contiene a la raíz?", [f"[{a}, xr1]", f"[xr1, {b}]"], 0 if it1["fa"] * it1["fx"] < 0 else 1, "Verifica en qué mitad el producto de f en los extremos es negativo."),
            _paso_num("Paso 3: Segunda aproximación xr2", "Calcula xr2 en el nuevo intervalo:", it2["x"], pista3, 0.025),
        ],
        "resultado_final": it2["x"],
    }


def _construir_raiz_abierta(r: random.Random, metodo: str, modo: str) -> Dict[str, Any]:
    if metodo == "Newton-Raphson":
        if modo == "cubica":
            p = r.choice([2, 3, 5])
            q = r.choice([3, 4, 6])
            f = lambda x, p=p, q=q: x ** 3 - p * x - q
            df = lambda x, p=p: 3.0 * x * x - p
            f_txt = f"x^3 - {p}x - {q}"
            x0 = r.choice([2.5, 3.0])
            ctx = "ecuación cúbica de velocidad orbital"
        else:
            alpha = round(r.uniform(0.4, 0.8), 2)
            f = lambda x, al=alpha: math.exp(-x) - al * x
            df = lambda x, al=alpha: -math.exp(-x) - al
            f_txt = f"e^(-x) - {alpha}x"
            x0 = r.choice([0.0, 0.5, 1.0])
            ctx = "ecuación exponencial de descarga capacitiva"
        for _ in range(10):
            if abs(f(x0)) >= 0.2 and abs(df(x0)) >= 0.35:
                break
            x0 += 0.5
        res = metodo_newton_raphson(f, df, x0, tol=1e-9, max_iter=6)
        its = res["iteraciones"]
        it1, it2 = its[0], its[1]
        curva = _muestrear_curva(f, min(x0, it2["x_sig"]) - 0.8, max(x0, it2["x_sig"]) + 0.8)
        filas_tp = [{"paso_min": idx, "valores": [it["iter"], _red(it["x_i"], 4), _red(it["fx"], 4), _red(it["dfx"], 4), _red(it["x_sig"], 4)]} for idx, it in enumerate(its, start=1)]
        return {
            "metodo": metodo,
            "sala_id": 2,
            "oxigeno_seg": 360,
            "formula": "x_{i+1} = x_i - f(x_i) / f'(x_i)",
            "enunciado": (
                f"Para {ctx}: f(x) = {f_txt} con valor inicial x0 = {x0}. "
                f"Aplicando {metodo}, calcula en orden: 1) la derivada f'({x0}), 2) la primera iteración x1, y 3) la segunda iteración x2."
            ),
            "datos_tabla": (["Parámetro", "Valor"], [["Función f(x)", f_txt], ["x0", x0], ["f(x0)", _red(f(x0), 4)]]),
            "tabla_progresiva": {"titulo": "Iteraciones Newton-Raphson", "columnas": ["Iter", "x_i", "f(x_i)", "f'(x_i)", "x_{i+1}"], "filas": filas_tp},
            "grafica": {
                "tipo": "funcion",
                "titulo": f"Newton-Raphson: {f_txt}",
                "xlabel": "x",
                "ylabel": "f(x)",
                "curva_pts": curva,
                "marcadores": [
                    {"x": x0, "y": f(x0), "etiqueta": "x0", "color": "#C5B9D6", "paso_min": 0},
                    {"x": it1["x_sig"], "y": f(it1["x_sig"]), "etiqueta": "x1", "color": "#FFD166", "paso_min": 2},
                    {"x": it2["x_sig"], "y": f(it2["x_sig"]), "etiqueta": "x2", "color": "#5CE0A0", "paso_min": 3},
                ],
            },
            "pasos": [
                _paso_num("Paso 1: Derivada f'(x0)", f"Calcula f'({x0}) evaluando la derivada de {f_txt}:", it1["dfx"], "Deriva f(x) simbólicamente y sustituye x0.", 0.025),
                _paso_num("Paso 2: Primera iteración x1", "Calcula x1 = x0 - f(x0)/f'(x0):", it1["x_sig"], "Divide f(x0) entre la derivada del Paso 1 y réstalo a x0.", 0.025),
                _paso_num("Paso 3: Segunda iteración x2", "Calcula x2 a partir de x1:", it2["x_sig"], "Evalúa f(x1) y f'(x1) y vuelve a aplicar la fórmula de Newton.", 0.025),
            ],
            "resultado_final": it2["x_sig"],
        }

    if metodo == "Secante":
        if modo == "cubica":
            p = r.choice([2, 3, 4])
            q = r.choice([2, 4, 5])
            f = lambda x, p=p, q=q: x ** 3 - p * x - q
            f_txt = f"x^3 - {p}x - {q}"
            x_0, x_1 = 1.5, 2.5
        else:
            k = round(r.uniform(0.5, 0.9), 2)
            f = lambda x, k=k: x ** 2 - k * math.cos(x) - 1.0
            f_txt = f"x^2 - {k}*cos(x) - 1   (x en rad)"
            x_0, x_1 = 1.0, 2.0
        res = metodo_secante(f, x_0, x_1, tol=1e-9, max_iter=6)
        its = res["iteraciones"]
        it1, it2 = its[0], its[1]
        fx0_v, fx1_v = _red(f(x_0), 4), _red(f(x_1), 4)
        curva = _muestrear_curva(f, min(x_0, it2["x_sig"]) - 0.5, max(x_1, it2["x_sig"]) + 0.5)
        filas_tp = [{"paso_min": idx, "valores": [it["iter"], _red(it["x_ant"], 4), _red(it["x_act"], 4), _red(it["x_sig"], 4)]} for idx, it in enumerate(its, start=1)]
        return {
            "metodo": metodo,
            "sala_id": 2,
            "oxigeno_seg": 360,
            "formula": "x_{i+1} = x_{i+1} - [f(x_{i+1})*(x_{i+1} - x_i)] / [f(x_{i+1}) - f(x_i)]",
            "enunciado": (
                f"Aplica Secante a f(x) = {f_txt} con valores iniciales x0 = {x_0} [f(x0)={fx0_v}] y x1 = {x_1} [f(x1)={fx1_v}]. "
                f"Calcula en orden: 1) la aproximación x2, 2) la aproximación x3, y 3) el error absoluto e = |x3 - x2|."
            ),
            "datos_tabla": (["Parámetro", "Valor"], [["Función f(x)", f_txt], ["x0", x_0], ["x1", x_1], ["f(x0)", fx0_v], ["f(x1)", fx1_v]]),
            "tabla_progresiva": {"titulo": "Iteraciones Secante", "columnas": ["Iter", "x_{i-1}", "x_i", "x_{i+1}"], "filas": filas_tp},
            "grafica": {
                "tipo": "funcion",
                "titulo": f"Secante: {f_txt}",
                "xlabel": "x",
                "ylabel": "f(x)",
                "curva_pts": curva,
                "marcadores": [
                    {"x": it1["x_sig"], "y": f(it1["x_sig"]), "etiqueta": "x2", "color": "#FFD166", "paso_min": 1},
                    {"x": it2["x_sig"], "y": f(it2["x_sig"]), "etiqueta": "x3", "color": "#5CE0A0", "paso_min": 2},
                ],
            },
            "pasos": [
                _paso_num("Paso 1: Calcular x2", f"Con x0={x_0}, x1={x_1} y f(x)={f_txt}, calcula x2:", it1["x_sig"], "Aplica x2 = x1 - f(x1)*(x1 - x0) / (f(x1) - f(x0)).", 0.025, tooltip="Primera raíz aproximada x2 usando la recta secante entre x0 y x1."),
                _paso_num("Paso 2: Calcular x3", f"Usa ahora x1 y x2 para calcular x3 (f(x)={f_txt}):", it2["x_sig"], "Evalúa f(x2) y aplica la secante entre x1 y x2.", 0.025, tooltip="Segunda aproximación x3 recorriendo los dos últimos puntos."),
                _paso_num("Paso 3: Error aproximado e", "Calcula e = |x3 - x2|:", it2["error"], "Toma el valor absoluto de la diferencia entre x3 y x2.", 0.02, tooltip="Error absoluto entre iteraciones consecutivas |x3 - x2|."),
            ],
            "resultado_final": it2["x_sig"],
        }

    # Punto Fijo contractivo |g'(x)| < 1 garantizado
    if modo == "exponencial":
        a = round(r.choice([0.35, 0.4, 0.45, 0.5]), 2)
        g = lambda x, a=a: math.exp(-a * x)
        g_txt = f"e^(-{a}x)"
        x0 = r.choice([0.5, 0.7, 0.8])
    else:
        k = r.choice([2, 3, 4])
        c = r.choice([2, 3, 4])
        while c / ((1.0 + k) ** 2) >= 0.75:
            k += 1
        g = lambda x, c=c, k=k: c / (x + k)
        g_txt = f"{c} / (x + {k})"
        x0 = r.choice([1.0, 1.5, 2.0])

    while abs(g(x0) - x0) < 0.2:
        x0 = round(x0 + 0.5, 2)
    res = metodo_punto_fijo(g, x0, tol=1e-9, max_iter=6)
    its = res["iteraciones"]
    it1, it2, it3 = its[0], its[1], its[2]
    xmin, xmax = min(0.0, x0, it3["gx"]) - 0.3, max(x0, it3["gx"], 1.5) + 0.5
    curva_g = _muestrear_curva(g, xmin, xmax)
    curva_id = _muestrear_curva(lambda t: t, xmin, xmax)
    filas_tp = [{"paso_min": idx, "valores": [it["iter"], _red(it["x_i"], 4), _red(it["gx"], 4), _red(it["error"], 4)]} for idx, it in enumerate(its, start=1)]
    return {
        "metodo": metodo,
        "sala_id": 2,
        "oxigeno_seg": 360,
        "formula": "x_{i+1} = g(x_i)   |   Converge si |g'(x)| < 1",
        "enunciado": (
            f"Itera Punto Fijo con la forma contractiva despejada g(x) = {g_txt} iniciando en x0 = {x0}. "
            f"Calcula las primeras 3 iteraciones: 1) x1 = g(x0), 2) x2 = g(x1), y 3) x3 = g(x2)."
        ),
        "datos_tabla": (["Parámetro", "Valor"], [["g(x)", g_txt], ["x0", x0]]),
        "tabla_progresiva": {"titulo": "Iteraciones Punto Fijo (x = g(x))", "columnas": ["Iter", "x_i", "g(x_i)", "|x_{i+1}-x_i|"], "filas": filas_tp},
        "grafica": {
            "tipo": "funcion",
            "titulo": "Cruce y=g(x) con recta y=x",
            "xlabel": "x",
            "ylabel": "g(x) y recta y=x",
            "curva_pts": curva_g,
            "curva_modelo_pts": curva_id,
            "curva_modelo_paso_min": 0,
            "marcadores": [
                {"x": x0, "y": it1["gx"], "etiqueta": "(x0, x1)", "color": "#F4A261", "paso_min": 1},
                {"x": it1["gx"], "y": it2["gx"], "etiqueta": "(x1, x2)", "color": "#5CE0A0", "paso_min": 2},
            ],
        },
        "pasos": [
            _paso_num("Paso 1: Primera iteración x1", f"Calcula x1 = g({x0}):", it1["gx"], f"Evalúa directamente x1 = {g_txt} con x={x0}.", 0.02),
            _paso_num("Paso 2: Segunda iteración x2", "Calcula x2 = g(x1):", it2["gx"], "Sustituye x1 del Paso 1 en g(x).", 0.02),
            _paso_num("Paso 3: Tercera iteración x3", "Calcula x3 = g(x2):", it3["gx"], "Sustituye x2 en g(x).", 0.02),
        ],
        "resultado_final": it3["gx"],
    }


# ==============================================================================
# SALA 3: SISTEMAS DE ECUACIONES LINEALES
# ==============================================================================

def _construir_sistema_directo(r: random.Random, metodo: str, contexto: str) -> Dict[str, Any]:
    A, b, sol_exacta = _resolver_3x3_para_solucion(r, diag_dom=False)
    if metodo == "Montante":
        res = metodo_montante(A, b)
        sol = res["solucion"]
        formula = "a_ij^(k) = (a_ij^(k-1)*p_k - a_ik^(k-1)*a_kj^(k-1)) / p_(k-1)   |   det(A) = p_n"
        filas_tp = [
            {"paso_min": idx, "valores": [f"Etapa k={p['pivote_idx']+1}", f"piv={_red(p['pivote'],3)}", f"[{_red(p['matriz'][0][0],2)}, ...]"]}
            for idx, p in enumerate(res["pasos"], start=1)
        ]
        enunc = (
            f"Sistema lineal 3x3 de {contexto}. Resuelve por {metodo} y calcula en orden: "
            f"1) el determinante del sistema (pivote final p3), 2) la incógnita x1, y 3) la incógnita x2."
        )
        pasos = [
            _paso_num("Paso 1: Determinante final", "Calcula el determinante del sistema (pivote final p3):", res["determinante"], "Aplica el algoritmo de Montante con pivote anterior inicial p0=1 hasta la 3ra columna.", 0.05),
            _paso_num("Paso 2: Incógnita x1", "Calcula x1 = Matriz[0, 3] / det(A):", sol[0], "Divide el término independiente transformado de la fila 1 entre el determinante.", 0.03),
            _paso_num("Paso 3: Incógnita x2", "Calcula x2 = Matriz[1, 3] / det(A):", sol[1], "Divide el término independiente transformado de la fila 2 entre el determinante.", 0.03),
        ]
    elif metodo == "Gauss - Jordan":
        res = metodo_gauss_jordan(A, b)
        sol = res["solucion"]
        formula = "Normalización R_i <- R_i / a_ii   y   eliminación completa arriba/abajo hasta [I | x]"
        escala = 1.0 / A[0][0]
        filas_tp = [
            {"paso_min": idx, "valores": [f"Pivote {idx}", f"fila {idx}", f"x{idx}={_red(sol[idx-1],3)}"]}
            for idx in range(1, 4)
        ]
        enunc = (
            f"Sistema lineal 3x3 de {contexto}. Resuelve mediante {metodo} e indica en orden: "
            f"1) el factor de normalización 1/a11 de la fila 1, 2) la incógnita x1, y 3) la incógnita x3."
        )
        pasos = [
            _paso_num("Paso 1: Factor de normalización", f"Calcula el multiplicador 1 / a11 para hacer 1 el primer pivote (a11={A[0][0]}):", escala, "Divide 1 entre el coeficiente a11 de la primera ecuación.", 0.02),
            _paso_num("Paso 2: Incógnita x1", "Tras transformar a [I | x], ingresa el valor exacto de x1:", sol[0], "Reduce arriba y abajo de cada columna pivote hasta obtener la matriz identidad.", 0.03),
            _paso_num("Paso 3: Incógnita x3", "Ingresa el valor exacto de x3:", sol[2], "Verifica sustituyendo x1, x2, x3 en las 3 ecuaciones originales.", 0.03),
        ]
    else:  # Eliminación gaussiana
        res = eliminacion_gaussiana(A, b)
        sol = res["solucion"]
        tri = res["triangular"]
        u22 = tri[1][1]
        formula = "Eliminación hacia adelante hasta matriz triangular superior [U | c] + sustitución regresiva"
        filas_tp = [
            {"paso_min": 1, "valores": ["U[2,2] (tras F2)", "pivote 2", _red(u22, 4)]},
            {"paso_min": 2, "valores": ["Sust. regresiva x3", "fila 3", _red(sol[2], 4)]},
            {"paso_min": 3, "valores": ["Sust. regresiva x1", "fila 1", _red(sol[0], 4)]},
        ]
        enunc = (
            f"Sistema lineal 3x3 de {contexto}. Resuelve por {metodo} y calcula en orden: "
            f"1) el coeficiente U[2,2] tras eliminar x1 de la fila 2, 2) la incógnita x3, y 3) la incógnita x1."
        )
        pasos = [
            _paso_num("Paso 1: Elemento U[2,2]", "Tras eliminar x1 de la fila 2 (usando pivote a11), calcula el nuevo coeficiente U[2,2]:", u22, "Calcula factor m21 = a21/a11 y aplica F2 <- F2 - m21*F1 en columna 2.", 0.03),
            _paso_num("Paso 2: Incógnita x3", "Mediante sustitución hacia atrás desde la última fila, calcula x3:", sol[2], "Despeja x3 = c'_3 / U[3,3] tras completar la eliminación.", 0.03),
            _paso_num("Paso 3: Incógnita x1", "Completa la sustitución hacia atrás y calcula x1:", sol[0], "Usa x3 y x2 para despejar x1 de la primera ecuación.", 0.03),
        ]

    return {
        "metodo": metodo,
        "sala_id": 3,
        "oxigeno_seg": 480,
        "formula": formula,
        "enunciado": enunc,
        "datos_tabla": (["Ecuación", "Sistema Lineal Ax = b"], _matriz_a_filas_texto(A, b)),
        "tabla_progresiva": {"titulo": f"Progreso {metodo}", "columnas": ["Paso", "Elemento", "Valor"], "filas": filas_tp},
        "grafica": {
            "tipo": "sistema",
            "titulo": f"Vector Solución x ({metodo})",
            "xlabel": "Variables",
            "ylabel": "Magnitud",
            "barras": {"etiquetas": ["x1", "x2", "x3"], "valores": [float(v) for v in sol], "paso_min": 2},
        },
        "pasos": pasos,
        "resultado_final": sol[0],
    }


def _construir_sistema_iterativo(r: random.Random, metodo: str, contexto: str, desordenado: bool) -> Dict[str, Any]:
    A_dom, b_dom, _ = _resolver_3x3_para_solucion(r, diag_dom=True)
    es_gs = metodo == "Gauss-Seidel"
    x0_vec = [0.0, 0.0, 0.0] if es_gs else [1.0, 1.0, 1.0]
    x0_txt = "(0, 0, 0)" if es_gs else "(1, 1, 1)"
    x0_corto = "(0,0,0)" if es_gs else "(1,1,1)"
    val_ini_str = "0.000" if es_gs else "1.000"
    val_num_ini = 0 if es_gs else 1

    if desordenado:
        # Permutar filas 0 y 1 para que inicialmente NO sea diagonal dominante (pregunta conceptual real!)
        A_mostrada = [A_dom[1][:], A_dom[0][:], A_dom[2][:]]
        b_mostrado = [b_dom[1], b_dom[0], b_dom[2]]
        # Aun así la solución en A_dom es diagonal dominante; pedimos detectar si la matriz dada lo es y usamos A_dom reordenada para iterar
        idx_dom = 1
        nota_reord = f"Nota: Verifica la dominancia diagonal, reordena filas si falta e inicia con x^(0) = {x0_txt}."
    else:
        A_mostrada = A_dom
        b_mostrado = b_dom
        idx_dom = 0
        nota_reord = f"Inicia con vector semilla x^(0) = {x0_txt}."

    res = (
        metodo_gauss_seidel(A_dom, b_dom, x0_vec, tol=1e-9, max_iter=6)
        if es_gs
        else metodo_jacobi(A_dom, b_dom, x0_vec, tol=1e-9, max_iter=6)
    )
    it1, it2 = res["iteraciones"][0], res["iteraciones"][1]
    formula = (
        "x_i^(k+1) = (b_i - sum_{j<i} a_ij x_j^(k+1) - sum_{j>i} a_ij x_j^(k)) / a_ii"
        if es_gs
        else "x_i^(k+1) = (b_i - sum_{j!=i} a_ij x_j^(k)) / a_ii"
    )
    filas_dom_txt = _matriz_a_filas_texto(A_dom, b_dom)
    filas_tp = [
        {"paso_min": 0, "valores": ["0", val_ini_str, val_ini_str, val_ini_str]},
    ]
    if desordenado:
        filas_tp.extend([
            {"paso_min": 1, "valores": ["Dom. Ec.1", filas_dom_txt[0][1], "fila 2 orig.", "|a11| dom"]},
            {"paso_min": 1, "valores": ["Dom. Ec.2", filas_dom_txt[1][1], "fila 1 orig.", "|a22| dom"]},
            {"paso_min": 1, "valores": ["Dom. Ec.3", filas_dom_txt[2][1], "fila 3 orig.", "|a33| dom"]},
        ])
    filas_tp.extend([
        {"paso_min": 2, "valores": ["1", _red(it1["x"][0], 4), _red(it1["x"][1], 4), _red(it1["x"][2], 4)]},
        {"paso_min": 3, "valores": ["2", _red(it2["x"][0], 4), _red(it2["x"][1], 4), _red(it2["x"][2], 4)]},
    ])
    return {
        "metodo": metodo,
        "sala_id": 3,
        "oxigeno_seg": 480,
        "formula": formula,
        "enunciado": (
            f"Análisis de {contexto} mediante {metodo}. {nota_reord} "
            f"Se pide: 1) verificar si es diagonal dominante, 2) calcular x1^(1), y 3) calcular x2^(1)."
        ),
        "datos_tabla": (["Ecuación", f"Sistema 3x3 (x^(0) = {x0_corto})"], _matriz_a_filas_texto(A_mostrada, b_mostrado)),
        "tabla_progresiva": {"titulo": f"Iteraciones {metodo}", "columnas": ["k", "x1", "x2", "x3"], "filas": filas_tp},
        "grafica": {
            "tipo": "sistema",
            "titulo": f"Aproximación x^(1) y x^(2) ({metodo})",
            "xlabel": "Variables",
            "ylabel": "Valor iterado",
            "barras": {"etiquetas": ["x1^(1)", "x2^(1)", "x3^(1)"], "valores": [float(v) for v in it1["x"]], "paso_min": 2},
        },
        "pasos": [
            _paso_opcion(
                "Paso 1: Criterio de convergencia",
                "En su orden de filas actual, ¿la matriz de coeficientes es estrictamente diagonal dominante?",
                ["Sí, cada |a_ii| > suma de los demás |a_ij|", "No, alguna fila requiere reordenamiento para cumplir |a_ii| > suma |a_ij|"],
                idx_dom,
                "Compara el valor absoluto de la diagonal contra la suma de los otros dos coeficientes en cada fila.",
            ),
            _paso_num(
                "Paso 2: Primera iteración x1^(1)",
                (
                    f"Intercambiando Ec.1 y Ec.2 para lograr diagonal dominante y con x^(0)={x0_corto}, calcula x1^(1):"
                    if desordenado
                    else f"Con el sistema en forma diagonal dominante y x^(0)={x0_corto}, calcula x1^(1):"
                ),
                it1["x"][0],
                f"Despeja x1 de la primera ecuación dominante sustituyendo x2={val_num_ini}, x3={val_num_ini}.",
                0.025,
                tooltip=f"Primer valor x1^(1) evaluado con semilla x^(0) = {x0_corto}.",
            ),
            _paso_num(
                "Paso 3: Primera iteración x2^(1)",
                f"Calcula x2^(1) usando {'el nuevo x1^(1) y x3^(0)=0' if es_gs else f'el vector previo {x0_corto}'}:",
                it1["x"][1],
                "En Gauss-Seidel sustituyes el x1 recién hallado; en Jacobi usas solo valores del paso anterior k.",
                0.025,
                tooltip="Segundo componente x2^(1) siguiendo las reglas de sustitución del método.",
            ),
        ],
        "resultado_final": it1["x"][1],
    }


# ==============================================================================
# SALA 4: AJUSTE DE CURVAS / MÍNIMOS CUADRADOS
# ==============================================================================

def _construir_ajuste(r: random.Random, metodo: str, contexto: str, tipo_fn: str = "ln") -> Dict[str, Any]:
    if metodo == "Línea Recta":
        if "clase" in contexto:
            xs = [1.1, 1.9, 2.4, 4.8, 5.1, 10.5]
        else:
            xs = [1.0, 2.0, 3.0, 4.0, 5.0]
        m = round(r.uniform(0.55, 2.2), 2)
        b = round(r.uniform(0.8, 3.0), 2)
        ys = [_red(m * x + b + r.uniform(-0.32, 0.32), 2) for x in xs]
        res = minimos_cuadrados_recta(xs, ys)
        a0, a1 = res["coeficientes"]
        sums = res["sumatorias"]
        n_pts = len(xs)
        sx, sy, sx2, sxy = sums["sx"], sums["sy"], sums["sx2"], sums["sxy"]
        g_fn = lambda t, a0=a0, a1=a1: a0 + a1 * t
        formula = (
            "g(x) = a0 + a1*x   |   Sistema: n*a0 + (sum x)*a1 = sum y;   (sum x)*a0 + (sum x^2)*a1 = sum xy\n"
            "a1 = [n*sum xy - (sum x)*(sum y)] / [n*sum x^2 - (sum x)^2],   a0 = (sum y - a1*sum x) / n"
        )
        enunc = (
            f"Ajuste experimental de {contexto} al modelo g(x) = a0 + a1*x mediante mínimos cuadrados ({metodo}). "
            f"Calcula en orden: 1) la sumatoria auxiliar sum x_i^2, 2) la pendiente a1, y 3) la ordenada al origen a0."
        )
        filas_tp = [
            {"paso_min": 0, "valores": ["n (puntos)", n_pts, "Modelo", "g(x)=a0+a1*x"]},
            {"paso_min": 1, "valores": ["sum x_i", _red(sx, 4), "sum y_i", _red(sy, 4)]},
            {"paso_min": 1, "valores": ["sum x_i^2", _red(sx2, 4), "sum (x_i*y_i)", _red(sxy, 4)]},
            {"paso_min": 2, "valores": ["Pendiente a1", _red(a1, 4), "ec. normal 1", f"{n_pts}a0+{_red(sx,2)}a1={_red(sy,2)}"]},
            {"paso_min": 3, "valores": ["Ordenada a0", _red(a0, 4), "ec. normal 2", f"{_red(sx,2)}a0+{_red(sx2,2)}a1={_red(sxy,2)}"]},
        ]
        pasos = [
            _paso_num(
                "Paso 1: Sumatoria auxiliar sum x^2",
                f"Para los n={n_pts} pares (x_i, y_i), calcula sum x_i^2 (y verifica sum x, sum y, sum xy):",
                sx2,
                "Eleva cada x_i de la tabla al cuadrado y suma los n términos.",
                0.03,
                tooltip="Suma de cuadrados de x (sum x^2), necesaria para el determinante del sistema 2x2.",
            ),
            _paso_num(
                "Paso 2: Pendiente a1",
                f"Usando n={n_pts}, sum x, sum y, sum x^2 y sum xy en a1 = [n*sum xy - (sum x)(sum y)] / [n*sum x^2 - (sum x)^2], calcula a1:",
                a1,
                "Calcula sum x, sum y, sum xy (visibles en TABLA PROGRESIVA) y despeja a1 del sistema normal.",
                0.04,
                tooltip="Coeficiente a1 de g(x) = a0 + a1*x (equivale a la pendiente de la recta).",
            ),
            _paso_num(
                "Paso 3: Ordenada al origen a0",
                f"Calcula a0 = (sum y - a1 * sum x) / n (con n={n_pts}):",
                a0,
                "Sustituye a1, sum y, sum x y n en la primera ecuación normal n*a0 + (sum x)*a1 = sum y.",
                0.04,
                tooltip="Coeficiente a0 de g(x) = a0 + a1*x (intersección con el eje y).",
            ),
        ]
        res_final = a1

    elif metodo == "Cuadrática":
        xs = [0.0, 1.0, 2.0, 3.0, 4.0]
        c0 = round(r.uniform(1.0, 3.0), 1)
        c1 = round(r.uniform(0.5, 1.5), 1)
        c2 = round(r.uniform(0.4, 0.9), 2)
        ys = [_red(c0 + c1 * x + c2 * x * x + r.uniform(-0.25, 0.25), 2) for x in xs]
        res = minimos_cuadrados_cuadratica(xs, ys)
        a0, a1, a2 = res["coeficientes"]
        sx2 = sum(x ** 2 for x in xs)
        sx4 = sum(x ** 4 for x in xs)
        x_eval = 2.5
        g_fn = lambda t, a0=a0, a1=a1, a2=a2: a0 + a1 * t + a2 * (t ** 2)
        y_eval = g_fn(x_eval)
        formula = "Sistema normal 3x3 para g(x) = a0 + a1*x + a2*x^2"
        enunc = (
            f"Ajuste experimental de {contexto} al modelo g(x) = a0 + a1*x + a2*x^2 mediante mínimos cuadrados ({metodo}). "
            f"Calcula en orden: 1) la sumatoria sum x_i^2, 2) el coeficiente cuadrático a2 del sistema normal 3x3, y 3) la estimación g({x_eval})."
        )
        filas_tp = [
            {"paso_min": 1, "valores": ["sum x^2", _red(sx2, 3), "sum x^4", _red(sx4, 3)]},
            {"paso_min": 2, "valores": ["Coef. a2", _red(a2, 4), "a1", _red(a1, 4)]},
            {"paso_min": 3, "valores": [f"g({x_eval})", _red(y_eval, 4), "a0", _red(a0, 4)]},
        ]
        pasos = [
            _paso_num("Paso 1: Sumatoria cuadrática", "Calcula sum x_i^2 de la tabla:", sx2, "Eleva cada x_i al cuadrado y suma los 5 términos.", 0.02),
            _paso_num("Paso 2: Coeficiente cuadrático a2", "Resuelve el sistema normal 3x3 y reporta a2:", a2, "Arma las sumatorias n, sum x..x^4 y sum y, sum xy, sum x^2y para resolver (a0, a1, a2).", 0.04),
            _paso_num(f"Paso 3: Predicción g({x_eval})", f"Evalúa la parábola ajustada en x = {x_eval}:", y_eval, f"Sustituye x={x_eval} en a0 + a1*x + a2*x^2.", 0.05),
        ]
        res_final = y_eval

    elif metodo == "Cúbica":
        xs = [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
        c3 = round(r.choice([0.15, -0.15, 0.2]), 2)
        c2 = round(r.uniform(-0.3, 0.4), 2)
        c1 = round(r.uniform(0.5, 1.5), 2)
        c0 = round(r.uniform(1.0, 3.0), 1)
        ys = [_red(c0 + c1 * x + c2 * x * x + c3 * x ** 3 + r.uniform(-0.15, 0.15), 2) for x in xs]
        res = minimos_cuadrados_cubica(xs, ys)
        a0, a1, a2, a3 = res["coeficientes"]
        sx2 = sum(x ** 2 for x in xs)
        sx3 = sum(x ** 3 for x in xs)
        x_eval = 1.5
        g_fn = lambda t, a0=a0, a1=a1, a2=a2, a3=a3: a0 + a1 * t + a2 * (t ** 2) + a3 * (t ** 3)
        y_eval = g_fn(x_eval)
        formula = "Sistema normal 4x4 para g(x) = a0 + a1*x + a2*x^2 + a3*x^3"
        enunc = (
            f"Ajuste experimental de {contexto} al modelo g(x) = a0 + a1*x + a2*x^2 + a3*x^3 mediante mínimos cuadrados ({metodo}). "
            f"Calcula en orden: 1) la sumatoria sum x_i^2, 2) el coeficiente cúbico a3 del sistema normal 4x4, y 3) la estimación g({x_eval})."
        )
        filas_tp = [
            {"paso_min": 1, "valores": ["sum x^2", _red(sx2, 3), "sum x^3", _red(sx3, 3)]},
            {"paso_min": 2, "valores": ["Coef. cúbico a3", _red(a3, 4), "a0", _red(a0, 4)]},
            {"paso_min": 3, "valores": [f"g({x_eval})", _red(y_eval, 4), "-", "-"]},
        ]
        pasos = [
            _paso_num("Paso 1: Elemento sum x^2", "Calcula sum x_i^2 para la matriz normal 4x4:", sx2, "Suma los cuadrados de los 6 valores de x.", 0.02),
            _paso_num("Paso 2: Coeficiente cúbico a3", "Resuelve el sistema 4x4 y reporta a3:", a3, "Construye la matriz de momentos hasta sum x^6 y vector [sum y .. sum x^3*y].", 0.04),
            _paso_num(f"Paso 3: Predicción g({x_eval})", f"Evalúa el polinomio cúbico en x = {x_eval}:", y_eval, f"Evalúa a0 + a1*x + a2*x^2 + a3*x^3 en x={x_eval}.", 0.06),
        ]
        res_final = y_eval

    elif metodo == "Lineal con Función":
        if tipo_fn == "ln":
            xs = [1.0, 2.0, 3.0, 4.0, 5.0]
            f_base = math.log
            f_str = "ln(x)"
            x_eval = 3.5
        else:
            xs = [0.2, 0.5, 0.8, 1.1, 1.4]
            f_base = math.sin
            f_str = "sin(x) [rad]"
            x_eval = 0.7
        c0 = round(r.uniform(1.0, 2.0), 1)
        c1 = round(r.uniform(0.5, 1.2), 2)
        c2 = round(r.uniform(1.0, 2.0), 2)
        ys = [_red(c0 + c1 * x + c2 * f_base(x) + r.uniform(-0.08, 0.08), 3) for x in xs]
        res = minimos_cuadrados_lineal_funcion(xs, ys, f_base)
        a0, a1, a2 = res["coeficientes"]
        sf = res["matriz"][0][2]
        sf2 = res["matriz"][2][2]
        g_fn = lambda t, a0=a0, a1=a1, a2=a2, fb=f_base: a0 + a1 * t + a2 * fb(t)
        y_eval = g_fn(x_eval)
        formula = f"g(x) = a0 + a1*x + a2*{f_str}   |   Sistema normal 3x3"
        enunc = (
            f"Ajuste experimental de {contexto} al modelo g(x) = a0 + a1*x + a2*f(x) tomando como función base f(x) = {f_str}. "
            f"Calcula en orden: 1) la sumatoria sum f(x_i), 2) el coeficiente a2 del sistema normal 3x3, y 3) el valor estimado g({x_eval})."
        )
        filas_tp = [
            {"paso_min": 1, "valores": [f"sum {f_str}", _red(sf, 4), "sum f^2", _red(sf2, 4)]},
            {"paso_min": 2, "valores": ["Coef. a2 (func.)", _red(a2, 4), "a1", _red(a1, 4)]},
            {"paso_min": 3, "valores": [f"g({x_eval})", _red(y_eval, 4), "a0", _red(a0, 4)]},
        ]
        pasos = [
            _paso_num("Paso 1: Sumatoria de la función base", f"Calcula sum f(x_i) tomando f(x) = {f_str}:", sf, "Sustituye cada x_i en f(x) y suma los 5 resultados.", 0.03),
            _paso_num("Paso 2: Coeficiente a2 (de f(x))", f"Resuelve el sistema normal 3x3 de g(x) = a0 + a1*x + a2*{f_str} y reporta a2:", a2, "Arma la matriz normal con filas [1, x, f(x)] y resuelve (a0, a1, a2).", 0.06),
            _paso_num(f"Paso 3: Estimación g({x_eval})", f"Evalúa g({x_eval}) = a0 + a1*x + a2*{f_str}:", y_eval, f"Sustituye x={x_eval} y los coeficientes hallados en g(x).", 0.06),
        ]
        res_final = y_eval

    else:  # Cuadrática con Función
        if tipo_fn == "exp":
            xs = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
            f_base = math.exp
            f_str = "e^x"
            x_eval = 1.0
        else:
            xs = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
            f_base = math.log
            f_str = "ln(x)"
            x_eval = 2.5
        c0 = round(r.uniform(0.5, 1.5), 1)
        c1 = round(r.uniform(0.6, 1.2), 2)
        c2 = round(r.uniform(0.2, 0.6), 2)
        c3 = round(r.uniform(0.5, 1.5), 2)
        ys = [_red(c0 + c1 * x + c2 * (x ** 2) + c3 * f_base(x) + r.uniform(-0.06, 0.06), 3) for x in xs]
        res = minimos_cuadrados_cuadratica_funcion(xs, ys, f_base)
        a0, a1, a2, a3 = res["coeficientes"]
        sf = res["matriz"][0][3]
        sf2 = res["matriz"][3][3]
        g_fn = lambda t, a0=a0, a1=a1, a2=a2, a3=a3, fb=f_base: a0 + a1 * t + a2 * (t ** 2) + a3 * fb(t)
        y_eval = g_fn(x_eval)
        formula = f"g(x) = a0 + a1*x + a2*x^2 + a3*{f_str}   |   Sistema normal 4x4"
        enunc = (
            f"Ajuste experimental de {contexto} al modelo g(x) = a0 + a1*x + a2*x^2 + a3*f(x) tomando f(x) = {f_str}. "
            f"Calcula en orden: 1) la sumatoria sum f(x_i), 2) el coeficiente a3 del sistema normal 4x4, y 3) el valor estimado g({x_eval})."
        )
        filas_tp = [
            {"paso_min": 1, "valores": [f"sum {f_str}", _red(sf, 4), "sum f^2", _red(sf2, 4)]},
            {"paso_min": 2, "valores": ["Coef. a3 (func.)", _red(a3, 4), "a2", _red(a2, 4)]},
            {"paso_min": 3, "valores": [f"g({x_eval})", _red(y_eval, 4), "a0", _red(a0, 4)]},
        ]
        pasos = [
            _paso_num("Paso 1: Sumatoria sum f(x_i)", f"Calcula f(x_i) = {f_str} y reporta sum f(x_i):", sf, "Evalúa f(x_i) en los 6 puntos y suma.", 0.03),
            _paso_num("Paso 2: Coeficiente a3 (de f(x))", f"Resuelve el sistema normal 4x4 y reporta a3 (coef. de {f_str}):", a3, "Arma la matriz normal 4x4 en base {1, x, x^2, f(x)} y despeja a3.", 0.08),
            _paso_num(f"Paso 3: Estimación g({x_eval})", f"Evalúa g({x_eval}):", y_eval, f"Sustituye x={x_eval} en a0 + a1*x + a2*x^2 + a3*{f_str}.", 0.08),
        ]
        res_final = y_eval

    curva_mod = _muestrear_curva(g_fn, min(xs) - 0.15, max(xs) + 0.15)
    return {
        "metodo": metodo,
        "sala_id": 4,
        "oxigeno_seg": 360 if metodo == "Línea Recta" else 480,
        "formula": formula,
        "enunciado": enunc,
        "datos_tabla": (["i", "x_i", "y_i"], [[i + 1, xs[i], ys[i]] for i in range(len(xs))]),
        "tabla_progresiva": {"titulo": f"Sumatorias y Modelo ({metodo})", "columnas": ["Medida", "Valor", "Ref 1", "Ref 2"][:3 if metodo != "Línea Recta" else 4], "filas": filas_tp},
        "grafica": {
            "tipo": "funcion",
            "titulo": f"Regresión: {metodo}",
            "xlabel": "x",
            "ylabel": "y",
            "curva_pts": [],
            "curva_modelo_pts": curva_mod,
            "curva_modelo_paso_min": 2,
            "puntos_datos": list(zip(xs, ys)),
        },
        "pasos": pasos,
        "resultado_final": res_final,
    }


# ==============================================================================
# SALA 5: INTEGRACIÓN NUMÉRICA (ANALÍTICA + TABULAR REAL)
# ==============================================================================

def _construir_integracion(r: random.Random, metodo: str, tabular: bool, contexto: str) -> Dict[str, Any]:
    abiertas_alpha = {1: "3/2", 2: "4/3", 3: "5/24", 4: "6/20", 5: "7/1440", 6: "8/945"}
    cerradas_alpha = {1: "1/2", 2: "1/3", 3: "3/8", 4: "2/45", 5: "5/288", 6: "1/140"}

    if metodo == "Regla Trapezoidal":
        n = r.choice([3, 5, 7])  # Ajustado a solo impares según criterio de clase
        formula = "h = (b - a)/n (n impar)   |   I = (h/2) * [f(a) + 2*sum_{i=1}^{n-1} f(xi) + f(b)]"
    elif metodo == "Regla de 1/3 de Simpson":
        n = r.choice([4, 6])
        formula = "h = (b - a)/n (n par)   |   I = (h/3) * [f0 + 4*sum impares + 2*sum pares + fn]"
    elif metodo == "Regla de 3/8 de Simpson":
        n = r.choice([3, 6])
        formula = "h = (b - a)/n (n múlt. 3)   |   I = (3/8)h * [f(a) + 3*sum_{i=1}^{n-1} f(a+ih) + f(b)]"
    elif "Abiertas" in metodo:
        n = r.choice([2, 3, 4])
        alpha_txt = abiertas_alpha[n]
        pesos_txt = str(ABIERTAS_TABLA[n][1])
        formula = (
            f"h = (b - a)/(n + 2)   |   n={n}: alpha = {alpha_txt}, pesos c_i = {pesos_txt}\n"
            "I = alpha * h * sum_{i=1}^{n+1} c_i * f(x_i)   (x_i = a + i*h, extremos con peso 0)"
        )
    else:
        n = r.choice([4, 5])
        alpha_txt = cerradas_alpha[n]
        pesos_txt = str(CERRADAS_TABLA[n][1])
        formula = (
            f"h = (b - a)/n   |   n={n}: alpha = {alpha_txt}, pesos c_i = {pesos_txt}\n"
            "I = alpha * h * sum_{i=0}^{n} c_i * f(x_i)   (x_i = a + i*h)"
        )

    a = float(r.choice([0, 1]))
    h_base = r.choice([0.25, 0.5]) if "Abiertas" not in metodo else 0.5
    if "Abiertas" in metodo:
        b = a + (n + 2) * h_base
    else:
        b = a + n * h_base

    c_e = round(r.uniform(0.3, 0.8), 2)
    c_x = round(r.uniform(0.5, 1.5), 2)
    f = lambda x, ce=c_e, cx=c_x: math.exp(ce * x) + cx * x
    f_txt = f"e^({c_e}x) + {c_x}x"

    if tabular:
        h_tab = (b - a) / (n + 2) if "Abiertas" in metodo else (b - a) / n
        total_pts = (n + 3) if "Abiertas" in metodo else (n + 1)
        xs = [round(a + i * h_tab, 4) for i in range(total_pts)]
        fs = [_red(f(x), 3) for x in xs]
        res = integrar_tabla(metodo, xs, fs)
        enunc = (
            f"Tabla experimental discreta de {contexto} en [a={a}, b={b}] (n={n}). "
            f"Integra aplicando {metodo} y calcula en orden: 1) el tamaño de paso h, "
            f"2) el valor f(x1) del nodo i=1 (x1 = a + h), y 3) la integral aproximada I."
        )
        filas_dat = [[i, res["xs"][i], res["fs"][i]] for i in range(len(res["xs"]))]
        if "Abiertas" in metodo:
            filas_dat.append(["Fórmula h", "(b-a)/(n+2)", f"alpha={abiertas_alpha[n]}, c={res['pesos']}"])
        elif "Cerradas" in metodo:
            filas_dat.append(["Fórmula h", "(b-a)/n", f"alpha={cerradas_alpha[n]}, c={res['pesos']}"])
        tabla_datos = (["i", "x_i", "f(x_i) / Regla"], filas_dat)
        curva_pts = list(zip(res["xs"], res["fs"]))
    else:
        if metodo == "Regla Trapezoidal":
            res = regla_trapezoidal(f, a, b, n)
        elif metodo == "Regla de 1/3 de Simpson":
            res = simpson_un_tercio(f, a, b, n)
        elif metodo == "Regla de 3/8 de Simpson":
            res = simpson_tres_octavos(f, a, b, n)
        elif "Abiertas" in metodo:
            res = newton_cotes_abiertas(f, a, b, n)
        else:
            res = newton_cotes_cerradas(f, a, b, n)
        enunc = (
            f"Cálculo de {contexto} mediante la integral en [a={a}, b={b}] de f(x) = {f_txt} con {metodo} (n={n}). "
            f"Calcula en orden: 1) el tamaño de paso h, 2) f(x1) evaluado en x1 = a + h, y 3) la integral aproximada I."
        )
        filas_dat = [["Función f(x)", f_txt], ["Intervalo [a, b]", f"[{a}, {b}]"], ["Subintervalos n", n]]
        if "Abiertas" in metodo:
            filas_dat.extend([
                ["Fórmula paso h", "(b - a) / (n + 2)"],
                ["Constante alpha_n", abiertas_alpha[n]],
                ["Pesos c_i (extremos 0)", str(res["pesos"])],
            ])
        elif "Cerradas" in metodo:
            filas_dat.extend([
                ["Fórmula paso h", "(b - a) / n"],
                ["Constante alpha_n", cerradas_alpha[n]],
                ["Pesos c_i", str(res["pesos"])],
            ])
        tabla_datos = (["Parámetro", "Valor"], filas_dat)
        curva_pts = _muestrear_curva(f, a - 0.1, b + 0.1)

    h = res["h"]
    f1 = res["fs"][1]
    integral = res["integral"]
    filas_tp = [
        {"paso_min": 0 if i < 2 else 2, "valores": [i, _red(res["xs"][i], 4), _red(res["fs"][i], 4)]}
        for i in range(len(res["xs"]))
    ]
    preg_p2 = (
        f"Lee de la tabla el valor f(x1) para x1 = {_red(res['xs'][1], 4)}:"
        if tabular
        else f"Calcula f(x1) evaluando f(x) en x1 = a + h = {_red(res['xs'][1], 4)}:"
    )
    pista_p2 = (
        "Busca en la tabla el valor de f(x) en la fila donde i=1."
        if tabular
        else "Evalúa f en el primer nodo interior x1 = a + h."
    )
    if "Newton" in metodo:
        denom_txt = f"n + 2 = {n + 2}" if "Abiertas" in metodo else f"n = {n}"
        paso1 = _paso_num(
            "Paso 1: Tamaño de paso h",
            f"Calcula h = (b - a) / ({denom_txt}) en [{a}, {b}]:",
            h,
            f"Divide ({b} - {a}) entre ({denom_txt}).",
            0.02,
            tooltip=f"Incremento h = (b - a) / ({denom_txt}) entre puntos x_i = a + i*h.",
        )
        paso2 = _paso_num(
            "Paso 2: Valor del nodo interior f(x1)",
            preg_p2,
            f1,
            pista_p2,
            0.03,
            tooltip="Ordenada f(x1) en el primer punto interior de la malla.",
        )
        alpha_str = abiertas_alpha[n] if "Abiertas" in metodo else cerradas_alpha[n]
        pista3 = f"Aplica I = ({alpha_str}) * h * sum(c_i * f(x_i)) usando pesos {res['pesos']}."
        paso3 = _paso_num(
            "Paso 3: Integral aproximada I",
            f"Calcula I = ({alpha_str}) * h * sum(c_i * f(x_i)) con pesos {res['pesos']}:",
            integral,
            pista3,
            0.06,
            tooltip=f"Valor total de la integral aproximada usando alpha={alpha_str} y pesos {res['pesos']}.",
        )
    else:
        paso1 = _paso_num(
            "Paso 1: Tamaño de paso h",
            f"Calcula h = ({b} - {a}) / {n}:",
            h,
            "Divide el ancho (b - a) entre n subintervalos.",
            0.02,
            tooltip="Ancho h de cada subintervalo en [a, b].",
        )
        paso2 = _paso_num(
            "Paso 2: Valor del nodo interior f(x1)",
            preg_p2,
            f1,
            pista_p2,
            0.03,
            tooltip="Ordenada f(a + h) en el primer punto interior de la malla.",
        )
        pista3 = "Aplica la regla oficial sumando extremos y nodos interiores con sus multiplicadores correspondientes."
        paso3 = _paso_num(
            "Paso 3: Integral aproximada I",
            "Calcula el valor final de la integral I:",
            integral,
            pista3,
            0.06,
            tooltip="Aproximación final de la integral definida I.",
        )

    return {
        "metodo": metodo,
        "sala_id": 5,
        "oxigeno_seg": 540 if "Abiertas" in metodo else (480 if "Cerradas" in metodo else 360),
        "formula": formula,
        "enunciado": enunc,
        "datos_tabla": tabla_datos,
        "tabla_progresiva": {"titulo": f"Nodos de Integración (h={_red(h,4)})", "columnas": ["i", "x_i", "f(x_i)"], "filas": filas_tp},
        "grafica": {
            "tipo": "integracion",
            "titulo": f"Área aproximada ({metodo})",
            "xlabel": "x",
            "ylabel": "f(x)",
            "curva_pts": curva_pts,
            "puntos_datos": list(zip(res["xs"], res["fs"])),
            "area_integracion": {"xs": res["xs"], "fs": res["fs"], "a": a, "b": b},
        },
        "pasos": [paso1, paso2, paso3],
        "resultado_final": integral,
    }


# ==============================================================================
# SALAS 6 Y 7: ECUACIONES DIFERENCIALES ORDINARIAS
# ==============================================================================

def _construir_edo_1er(r: random.Random, metodo: str, tipo_edo: str, contexto: str) -> Dict[str, Any]:
    a_c = r.choice([1, 2, 3])
    b_c = r.choice([1, 2])
    h = r.choice([0.1, 0.2, 0.25])
    if tipo_edo == "clase_implicita":
        d_c = r.choice([2, 3])
        c_0 = r.choice([1, 2])
        y0, t0 = float(r.choice([1, 2])), 0.0
        f_edo = lambda y, t, a=a_c, b=c_0, d=d_c: (a * y * t - b) / d
        edo_orig = f"{d_c}*y' - {a_c}*y*t + {c_0} = 0"
        f_txt = f"({a_c}*y*t - {c_0}) / {d_c}"
    elif tipo_edo == "bilineal":
        y0, t0 = float(r.choice([1, 2])), float(r.choice([0, 1]))
        f_edo = lambda y, t, a=a_c, b=b_c: a * y * t + b
        edo_orig = f"y' = {a_c}*y*t + {b_c}"
        f_txt = f"{a_c}*y*t + {b_c}"
    else:
        y0, t0 = float(r.choice([1, 2])), 0.0
        f_edo = lambda y, t, a=a_c, b=b_c: b_c * t - a * y + 2.0
        edo_orig = f"y' + {a_c}*y - {b_c}*t - 2 = 0"
        f_txt = f"{b_c}*t - {a_c}*y + 2"

    t1 = round(t0 + h, 4)
    t2 = round(t0 + 2 * h, 4)
    sala_id = 6 if metodo in ("Euler Modificado", "Runge - Kutta 2ndo Orden") else 7
    tabla_edo = [["Ecuación original", edo_orig], ["Despeje y' = f(y, t)", f_txt], ["y0", y0], ["t0", t0], ["h", h]]

    if metodo == "Euler Modificado":
        y1_dato = round(y0 + h * f_edo(y0, t0), 2)
        tabla_edo.append(["y1 (estimado)", y1_dato])
        res = euler_modificado(f_edo, y0, t0, h, pasos=2, y1_estimado=y1_dato)
        p1, p2 = res["historial"][0], res["historial"][1]
        formula = (
            f"Despeje: y' = f(y, t) = {f_txt}   |   t_{{n+1}} = t_n + h\n"
            "y*_{n+1} = y_n + h*f(y_n, t_n) (o y1 estimado)   |   y'_{n+1} = y_n + (h/2)*[f(y_n, t_n) + f(y_{n+1}, t_{n+1})]"
        )
        detalle_ped = f"1) f(y0, t0), 2) f(y1={y1_dato}, t1={t1}), y 3) el valor corregido y'1."
        pasos = [
            _paso_num(
                "Paso 1: Evaluar f(y0, t0)",
                f"Con y' = f(y, t) = {f_txt}, y0={y0} y t0={t0}, calcula f(y0, t0):",
                p1["f_n"],
                f"Sustituye los valores iniciales (y0={y0}, t0={t0}) en la expresión {f_txt}.",
                0.025,
                tooltip=f"Pendiente inicial f(y0, t0) evaluando {f_txt} en ({y0}, {t0}).",
            ),
            _paso_num(
                "Paso 2: Evaluar f(y1, t1)",
                f"Con y' = f(y, t) = {f_txt}, t1 = {t1} y el dato estimado y1 = {y1_dato}, calcula f(y1, t1):",
                p1["f_sig"],
                f"Sustituye el dato estimado y1 ({y1_dato}) y t1 = t0 + h ({t1}) en la expresión {f_txt}.",
                0.025,
                tooltip=f"Pendiente estimada f(y1, t1) evaluando {f_txt} en ({y1_dato}, {t1}).",
            ),
            _paso_num(
                "Paso 3: Valor corregido y'1",
                "Calcula y'1 = y0 + (h/2)*[f(y0, t0) + f(y1, t1)]:",
                p1["y_sig"],
                "Multiplica (h/2) por la suma de los Pasos 1 y 2, y súmalo a y0.",
                0.03,
                tooltip=f"Valor corregido y'1 en t1 = {t1} mediante Euler Modificado.",
            ),
        ]
        y1_val = p1["y_sig"]
        filas_tp = [
            {"paso_min": 0, "valores": [0, t0, y0, f"y1(dato)={y1_dato}"]},
            {"paso_min": 1, "valores": ["f(y0,t0)", _red(t0, 3), _red(y0, 4), f"f0={_red(p1['f_n'], 4)}"]},
            {"paso_min": 2, "valores": ["f(y1,t1)", t1, y1_dato, f"f1={_red(p1['f_sig'], 4)}"]},
            {"paso_min": 3, "valores": [1, t1, _red(y1_val, 4), "y'1 corregido"]},
        ]
    elif metodo == "Runge - Kutta 2ndo Orden":
        res = runge_kutta_2(f_edo, y0, t0, h, pasos=2)
        p1, p2 = res["historial"][0], res["historial"][1]
        formula = (
            f"y' = f(y, t) = {f_txt}\n"
            "k1 = h*f(yn, tn),   k2 = h*f(yn + k1, tn + h),   y_{n+1} = yn + (1/2)*(k1 + k2)"
        )
        detalle_ped = "1) k1, 2) k2, y 3) y1."
        pasos = [
            _paso_num(
                "Paso 1: Pendiente k1",
                f"Con f(y, t) = {f_txt}, calcula k1 = h * f(y0={y0}, t0={t0}):",
                p1["k1"],
                f"Sustituye y={y0}, t={t0} en {f_txt} y multiplica por h={h}.",
                0.025,
                tooltip=f"Primer incremento k1 = h * f(y0, t0) con f(y, t) = {f_txt}.",
            ),
            _paso_num(
                "Paso 2: Pendiente k2",
                f"Con f(y, t) = {f_txt}, calcula k2 = h * f(y0 + k1, t0 + h) en t1={t1}:",
                p1["k2"],
                f"Usa y0+k1 y t0+h={t1} en {f_txt} y multiplica por h={h}.",
                0.03,
                tooltip="Segundo incremento k2 evaluado en (y0 + k1, t0 + h).",
            ),
            _paso_num(
                "Paso 3: Resultado y1",
                "Calcula y1 = y0 + (1/2) * (k1 + k2):",
                p1["y_sig"],
                "Suma a y0 el promedio (k1 + k2) / 2.",
                0.03,
                tooltip=f"Aproximación y1 en t1 = {t1}.",
            ),
        ]
        y1_val = p1["y_sig"]
        filas_tp = [
            {"paso_min": 0, "valores": [0, t0, y0, f"f(y,t)={f_txt}"]},
            {"paso_min": 1, "valores": [1, t1, "(pendiente)", f"k1={_red(p1['k1'], 4)}"]},
            {"paso_min": 2, "valores": [1, t1, "(pendiente)", f"k2={_red(p1['k2'], 4)}"]},
            {"paso_min": 3, "valores": [1, t1, _red(y1_val, 4), "y1 calculado"]},
        ]
    elif metodo == "Runge - Kutta 3er Orden":
        res = runge_kutta_3(f_edo, y0, t0, h, pasos=2)
        p1, p2 = res["historial"][0], res["historial"][1]
        formula = (
            f"y' = f(y, t) = {f_txt}   |   k1 = h*f(yn, tn)\n"
            "k2 = h*f(yn + k1/2, tn + h/2),   k3 = h*f(yn - k1 + 2*k2, tn + h),   y_{n+1} = yn + (k1 + 4*k2 + k3)/6"
        )
        detalle_ped = "1) k1, 2) k2, y 3) y1 (calculando k3)."
        pasos = [
            _paso_num(
                "Paso 1: Pendiente k1",
                f"Con f(y, t) = {f_txt}, calcula k1 = h * f(y0={y0}, t0={t0}):",
                p1["k1"],
                f"Sustituye y={y0}, t={t0} en f(y, t) = {f_txt} y multiplica por h={h}.",
                0.025,
                tooltip="Calcula k1 primero; luego aparecerá en TABLA PROGRESIVA para k2.",
            ),
            _paso_num(
                "Paso 2: Pendiente k2",
                f"Con f(y, t) = {f_txt} y k1 previo, calcula k2 = h * f(y0 + k1/2, t0 + h/2):",
                p1["k2"],
                "Evalúa f en el punto medio (y0 + k1/2, t0 + h/2) y multiplica por h.",
                0.025,
                tooltip="Pendiente intermedia k2 en t0 + h/2.",
            ),
            _paso_num(
                "Paso 3: Resultado y1",
                f"Calcula k3 = h*f(y0 - k1 + 2*k2, t0 + h) con f(y,t)={f_txt} y reporta y1 = y0 + (k1 + 4*k2 + k3)/6:",
                p1["y_sig"],
                "Halla k3 en (y0 - k1 + 2*k2, t0 + h) y aplica la ponderación (1, 4, 1)/6.",
                0.03,
                tooltip=f"Solución y1 en t1 = {t1}.",
            ),
        ]
        y1_val = p1["y_sig"]
        filas_tp = [
            {"paso_min": 0, "valores": [0, t0, y0, f"f(y,t)={f_txt}"]},
            {"paso_min": 1, "valores": [1, t1, "(en proceso)", f"k1={_red(p1['k1'], 4)}"]},
            {"paso_min": 2, "valores": [1, t1, "(en proceso)", f"k2={_red(p1['k2'], 4)}, k3={_red(p1['k3'], 4)}"]},
            {"paso_min": 3, "valores": [1, t1, _red(y1_val, 4), "y1 calculado"]},
        ]
    else:
        es_1_3 = "1/3" in metodo
        res = runge_kutta_4_simpson_1_3(f_edo, y0, t0, h, pasos=2) if es_1_3 else runge_kutta_4_simpson_3_8(f_edo, y0, t0, h, pasos=2)
        p1, p2 = res["historial"][0], res["historial"][1]
        detalle_ped = "1) k1, 2) k4 (calculando k2 y k3), y 3) y1."
        if es_1_3:
            formula = (
                f"y' = f(y,t) = {f_txt}   |   k1=h*f(yn,tn), k2=h*f(yn+k1/2,tn+h/2)\n"
                "k3=h*f(yn+k2/2,tn+h/2), k4=h*f(yn+k3,tn+h)   |   y_{n+1}=yn+(k1+2k2+2k3+k4)/6"
            )
            preg_k4 = f"Con f(y,t)={f_txt}, calcula k2, k3 y reporta k4 = h*f(y0+k3, t0+h):"
            pista_k4 = "Calcula k2, k3 en t0+h/2 y luego k4 = h*f(y0+k3, t0+h)."
            preg_y1 = "Calcula y1 = y0 + (k1 + 2*k2 + 2*k3 + k4) / 6:"
        else:
            formula = (
                f"y' = f(y,t) = {f_txt}   |   k1=h*f(yn,tn), k2=h*f(yn+k1/3,tn+h/3)\n"
                "k3=h*f(yn+k1/3+k2/3,tn+2h/3), k4=h*f(yn+k1-k2+k3,tn+h)   |   y_{n+1}=yn+(k1+3k2+3k3+k4)/8"
            )
            preg_k4 = f"Con f(y,t)={f_txt}, calcula k2, k3 y reporta k4 = h*f(y0+k1-k2+k3, t0+h):"
            pista_k4 = "Calcula k2 en h/3, k3 en 2h/3 y k4 = h*f(y0+k1-k2+k3, t0+h)."
            preg_y1 = "Calcula y1 = y0 + (k1 + 3*k2 + 3*k3 + k4) / 8:"
        pasos = [
            _paso_num("Paso 1: Pendiente k1", f"Con f(y, t) = {f_txt}, calcula k1 = h * f(y0={y0}, t0={t0}):", p1["k1"], f"Multiplica h={h} por f({y0}, {t0}).", 0.025, tooltip=f"Primer incremento k1 usando f(y,t)={f_txt}."),
            _paso_num("Paso 2: Pendiente k4", preg_k4, p1["k4"], pista_k4, 0.035, tooltip="Cuarto incremento k4 de la fórmula de Runge-Kutta."),
            _paso_num("Paso 3: Resultado y1", preg_y1, p1["y_sig"], "Aplica exactamente los coeficientes de 1/3 o 3/8 de Simpson según el método.", 0.035, tooltip=f"Solución y1 en t1 = {t1}."),
        ]
        y1_val = p1["y_sig"]
        filas_tp = [
            {"paso_min": 0, "valores": [0, t0, y0, f"f(y,t)={f_txt}"]},
            {"paso_min": 1, "valores": [1, t1, "(en proceso)", f"k1={_red(p1['k1'], 4)}"]},
            {"paso_min": 2, "valores": [1, t1, "(en proceso)", f"k2={_red(p1['k2'], 4)}, k3={_red(p1['k3'], 4)}, k4={_red(p1['k4'], 4)}"]},
            {"paso_min": 3, "valores": [1, t1, _red(y1_val, 4), "y1 calculado"]},
        ]

    y2_val = res["y_final"]
    return {
        "metodo": metodo,
        "sala_id": sala_id,
        "oxigeno_seg": 540 if sala_id == 6 else 600,
        "formula": formula,
        "enunciado": (
            f"Modelado de {contexto} para la EDO {edo_orig} (y' = f(y,t) = {f_txt}), con y({t0}) = {y0} y paso h = {h}. "
            f"Mediante {metodo}, calcula en orden: {detalle_ped}"
        ),
        "datos_tabla": (["Parámetro", "Valor"], tabla_edo),
        "tabla_progresiva": {"titulo": f"Trayectoria Numérica ({metodo})", "columnas": ["Paso n", "t_n", "y_n", "Pendientes"], "filas": filas_tp},
        "grafica": {
            "tipo": "edo",
            "titulo": f"Trayectoria y(t) ({metodo})",
            "xlabel": "t",
            "ylabel": "y(t)",
            "curva_pts": [(t0, y0), (t1, y1_val), (t2, y2_val)],
            "puntos_datos": [(t0, y0)],
            "marcadores": [
                {"x": t1, "y": y1_val, "etiqueta": "y1", "color": "#FFD166", "paso_min": 2},
                {"x": t2, "y": y2_val, "etiqueta": "y2", "color": "#5CE0A0", "paso_min": 3},
            ],
        },
        "pasos": pasos,
        "resultado_final": y1_val,
    }


def _construir_edo_2do(r: random.Random, tipo: str, contexto: str) -> Dict[str, Any]:
    h_os = r.choice([0.25, 0.5])
    if tipo == "variable":
        a2, b2 = r.choice([1, 2]), r.choice([1, 2])
        y0_os, yp0_os, t0_os = 1.0, float(r.choice([1, 2])), 0.0
        g_os = lambda v, u, q, a2=a2, b2=b2: a2 * v * q + b2 * u
        edo_txt = f"y'' - {a2}y't - {b2}y = 0"
        desp_txt = f"{a2}V*t + {b2}U"
        enunc_m1 = f"calcula m1 = h * ({a2}*V0*t0 + {b2}*U0):"
    else:
        c, k = r.choice([1, 2]), r.choice([2, 3])
        y0_os, yp0_os, t0_os = 1.0, 0.0, 0.0
        g_os = lambda v, u, q, c=c, k=k: -c * v - k * u
        edo_txt = f"y'' + {c}y' + {k}y = 0"
        desp_txt = f"-{c}V - {k}U"
        enunc_m1 = f"calcula m1 = h * (-{c}*V0 - {k}*U0):"

    res = runge_kutta_orden_superior(g_os, y0_os, yp0_os, t0_os, h_os, pasos=2)
    p1, p2 = res["historial"][0], res["historial"][1]
    return {
        "metodo": "Runge - Kutta de Orden Superior",
        "sala_id": 7,
        "oxigeno_seg": 600,
        "formula": (
            f"U=y, V=y', V'=g(V,U,t)={desp_txt}\n"
            "k1=h*V, m1=h*g(V,U,t), k2=h*(V+m1), m2=h*g(V+m1,U+k1,t+h)   |   y1=y0+0.5(k1+k2), y'1=y'0+0.5(m1+m2)"
        ),
        "enunciado": (
            f"Sistema de {contexto}: {edo_txt} (V'=g(V,U,t)={desp_txt}), con y({t0_os})={y0_os}, y'({t0_os})={yp0_os}, t0={t0_os} y paso h={h_os}. "
            f"Calcula en orden para el primer paso: 1) la pendiente m1, 2) el desplazamiento y1, y 3) la velocidad y'1."
        ),
        "datos_tabla": (["Parámetro", "Valor"], [["EDO", edo_txt], ["V' = g(V,U,t)", desp_txt], ["U0 = y0", y0_os], ["V0 = y'0", yp0_os], ["t0", t0_os], ["h", h_os]]),
        "tabla_progresiva": {
            "titulo": "Sistema Equivalente 2do Orden",
            "columnas": ["Paso", "t_n", "y_n (U)", "y'_n (V)"],
            "filas": [
                {"paso_min": 0, "valores": [0, t0_os, y0_os, yp0_os]},
                {"paso_min": 1, "valores": ["k1,m1", t0_os, f"k1={_red(p1['k1'],4)}", f"m1={_red(p1['m1'],4)}"]},
                {"paso_min": 2, "valores": [1, _red(t0_os + h_os, 3), _red(p1["y_sig"], 4), _red(p1["yp_sig"], 4)]},
                {"paso_min": 3, "valores": [2, _red(t0_os + 2 * h_os, 3), _red(p2["y_sig"], 4), _red(p2["yp_sig"], 4)]},
            ],
        },
        "grafica": {
            "tipo": "edo",
            "titulo": "Respuesta y(t) de 2do Orden",
            "xlabel": "t",
            "ylabel": "y(t)",
            "curva_pts": [(t0_os, y0_os), (t0_os + h_os, p1["y_sig"]), (t0_os + 2 * h_os, p2["y_sig"])],
            "puntos_datos": [(t0_os, y0_os)],
            "marcadores": [
                {"x": t0_os + h_os, "y": p1["y_sig"], "etiqueta": "y1", "color": "#FFD166", "paso_min": 2},
                {"x": t0_os + 2 * h_os, "y": p2["y_sig"], "etiqueta": "y2", "color": "#5CE0A0", "paso_min": 3},
            ],
        },
        "pasos": [
            _paso_num("Paso 1: Pendiente m1", f"Con g(V,U,t) = {desp_txt}, " + enunc_m1, p1["m1"], f"Evalúa g(V0={yp0_os}, U0={y0_os}, t0={t0_os}) en {desp_txt} y multiplica por h={h_os}.", 0.025, tooltip=f"Primera pendiente m1 para V' = {desp_txt} en (V0, U0, t0)."),
            _paso_num("Paso 2: Desplazamiento y1", "Calcula y1 = y0 + 0.5*(k1 + k2) (k1=h*V0, k2=h*(V0+m1)):", p1["y_sig"], "Calcula k1 = h*V0 y k2 = h*(V0 + m1) y promedia con y0.", 0.03, tooltip="Posición aproximada y1 en t1 = t0 + h."),
            _paso_num("Paso 3: Velocidad y'1", f"Con g(V,U,t)={desp_txt}, calcula m2 = h*g(V0+m1, U0+k1, t0+h) y reporta y'1 = y'0 + 0.5*(m1 + m2):", p1["yp_sig"], "Evalúa g en (V0+m1, U0+k1, t0+h), multiplica por h y promedia con m1.", 0.035, tooltip="Derivada/velocidad aproximada y'1 en t1 = t0 + h."),
        ],
        "resultado_final": p1["y_sig"],
    }


# ==============================================================================
# REGISTRO OFICIAL: 64 PLANTILLAS DE LIBRO (2 POR CADA UNO DE LOS 32 MÉTODOS)
# ==============================================================================

BANCO_PLANTILLAS: Dict[str, List[Dict[str, Any]]] = {
    "Interpolación lineal": [
        {"id": "S1_IL_CHAPRA_LN", "referencia": "Chapra & Canale (7a ed.), Ej. 18.1 — Calibración ln(x)", "construir": _s1_il_chapra_ln},
        {"id": "S1_IL_NIEVES_TERM", "referencia": "Nieves & Domínguez, Cap. 5 — Propiedades Termodinámicas", "construir": _s1_il_nieves_densidad},
    ],
    "Newton hacia adelante": [
        {"id": "S1_NA_CHAPRA_VAPOR", "referencia": "Chapra & Canale (7a ed.), Sec. 18.2 — Tabla de vapor", "construir": lambda r: _construir_newton_finitas(r, True, "presión de vapor vs temperatura")},
        {"id": "S1_NA_BURDEN_TRAY", "referencia": "Burden & Faires (10a ed.), Sec. 3.3 — Telemetría uniforme", "construir": lambda r: _construir_newton_finitas(r, True, "altura orbital uniforme")},
    ],
    "Newton hacia atrás": [
        {"id": "S1_NAT_NIEVES_CAUDAL", "referencia": "Nieves & Domínguez, Cap. 5 — Diferencias Regresivas", "construir": lambda r: _construir_newton_finitas(r, False, "caudal en canal hidráulico")},
        {"id": "S1_NAT_ZAMORA_TERM", "referencia": "Apuntes Ing. Oralia Zamora — Unidad Interpolación", "construir": lambda r: _construir_newton_finitas(r, False, "enfriamiento en cámara térmica")},
    ],
    "Lagrange": [
        {"id": "S1_LAG_CHAPRA_18_6", "referencia": "Chapra & Canale (7a ed.), Ej. 18.6 — Interpolación de Lagrange", "construir": lambda r: _construir_no_uniforme(r, True, "log")},
        {"id": "S1_LAG_BURDEN_3_1", "referencia": "Burden & Faires (10a ed.), Sec. 3.1 — Curva voltaje-corriente", "construir": lambda r: _construir_no_uniforme(r, True, "poly")},
    ],
    "Newton con diferencias divididas": [
        {"id": "S1_NDD_CHAPRA_18_5", "referencia": "Chapra & Canale (7a ed.), Ej. 18.5 — Diferencias divididas", "construir": lambda r: _construir_no_uniforme(r, False, "log")},
        {"id": "S1_NDD_BURDEN_3_3", "referencia": "Burden & Faires (10a ed.), Sec. 3.3 — Malla irregular", "construir": lambda r: _construir_no_uniforme(r, False, "poly")},
    ],
    "Gráfico": [
        {"id": "S2_MG_CHAPRA_5_1", "referencia": "Chapra & Canale (7a ed.), Ej. 5.1 — Descenso y arrastre", "construir": lambda r: _s2_grafico_gen(r, "paracaidas")},
        {"id": "S2_MG_NIEVES_TANQUE", "referencia": "Nieves & Domínguez, Cap. 2 — Localización de raíces", "construir": lambda r: _s2_grafico_gen(r, "cubica")},
    ],
    "Bisectriz": [
        {"id": "S2_BIS_CHAPRA_5_3", "referencia": "Chapra & Canale (7a ed.), Ej. 5.3 — Bisección", "construir": lambda r: _construir_raiz_bracket(r, "Bisectriz", "cubica")},
        {"id": "S2_BIS_BURDEN_2_1", "referencia": "Burden & Faires (10a ed.), Sec. 2.1 — Ecuación trascendente", "construir": lambda r: _construir_raiz_bracket(r, "Bisectriz", "exp")},
    ],
    "Newton-Raphson": [
        {"id": "S2_NR_CHAPRA_6_3", "referencia": "Chapra & Canale (7a ed.), Ej. 6.3 — Newton-Raphson", "construir": lambda r: _construir_raiz_abierta(r, "Newton-Raphson", "cubica")},
        {"id": "S2_NR_BURDEN_2_3", "referencia": "Burden & Faires (10a ed.), Sec. 2.3 — Descarga no lineal", "construir": lambda r: _construir_raiz_abierta(r, "Newton-Raphson", "exp")},
    ],
    "Falsa Posición o Regula": [
        {"id": "S2_FP_CHAPRA_5_5", "referencia": "Chapra & Canale (7a ed.), Ej. 5.5 — Regula Falsi", "construir": lambda r: _construir_raiz_bracket(r, "Falsa Posición o Regula", "cubica")},
        {"id": "S2_FP_NIEVES_2_3", "referencia": "Nieves & Domínguez, Cap. 2 — Falsa posición trascendente", "construir": lambda r: _construir_raiz_bracket(r, "Falsa Posición o Regula", "exp")},
    ],
    "Secante": [
        {"id": "S2_SEC_CHAPRA_6_6", "referencia": "Chapra & Canale (7a ed.), Ej. 6.6 — Secante", "construir": lambda r: _construir_raiz_abierta(r, "Secante", "cubica")},
        {"id": "S2_SEC_BURDEN_PEND", "referencia": "Burden & Faires (10a ed.), Sec. 2.3 — Oscilador no lineal", "construir": lambda r: _construir_raiz_abierta(r, "Secante", "trig")},
    ],
    "Punto Fijo": [
        {"id": "S2_PF_CHAPRA_6_1", "referencia": "Chapra & Canale (7a ed.), Ej. 6.1 — Iteración simple", "construir": lambda r: _construir_raiz_abierta(r, "Punto Fijo", "exponencial")},
        {"id": "S2_PF_BURDEN_2_2", "referencia": "Burden & Faires (10a ed.), Sec. 2.2 — Mapeo contractivo", "construir": lambda r: _construir_raiz_abierta(r, "Punto Fijo", "algebraica")},
    ],
    "Montante": [
        {"id": "S3_MON_ZAMORA_CIRC", "referencia": "Apuntes Ing. Oralia Zamora — Redes Eléctricas (Montante)", "construir": lambda r: _construir_sistema_directo(r, "Montante", "corrientes de malla en red eléctrica")},
        {"id": "S3_MON_CHAPRA_REACT", "referencia": "Chapra & Canale (7a ed.), Cap. 12 — Balance de reactores", "construir": lambda r: _construir_sistema_directo(r, "Montante", "concentraciones en 3 reactores acoplados")},
    ],
    "Gauss - Jordan": [
        {"id": "S3_GJ_CHAPRA_9_5", "referencia": "Chapra & Canale (7a ed.), Sec. 9.7 — Gauss-Jordan", "construir": lambda r: _construir_sistema_directo(r, "Gauss - Jordan", "tensiones en armadura estructural")},
        {"id": "S3_GJ_NIEVES_FLUJ", "referencia": "Nieves & Domínguez, Cap. 3 — Red de tuberías", "construir": lambda r: _construir_sistema_directo(r, "Gauss - Jordan", "caudales en red hidráulica")},
    ],
    "Eliminación gaussiana": [
        {"id": "S3_EG_CHAPRA_9_9", "referencia": "Chapra & Canale (7a ed.), Ej. 9.9 — Paracaidistas acoplados", "construir": lambda r: _construir_sistema_directo(r, "Eliminación gaussiana", "sistema dinámico de 3 cuerpos")},
        {"id": "S3_EG_BURDEN_6_1", "referencia": "Burden & Faires (10a ed.), Sec. 6.1 — Equilibrio estático", "construir": lambda r: _construir_sistema_directo(r, "Eliminación gaussiana", "equilibrio de fuerzas nodales")},
    ],
    "Gauss-Seidel": [
        {"id": "S3_GS_CHAPRA_11_1", "referencia": "Chapra & Canale (7a ed.), Ej. 11.1 — Gauss-Seidel", "construir": lambda r: _construir_sistema_iterativo(r, "Gauss-Seidel", "malla nodal diagonal dominante", False)},
        {"id": "S3_GS_BURDEN_REORD", "referencia": "Burden & Faires (10a ed.), Sec. 7.3 — Criterio de dominancia", "construir": lambda r: _construir_sistema_iterativo(r, "Gauss-Seidel", "sistema iterativo con filas permutadas", True)},
    ],
    "Jacobi": [
        {"id": "S3_JAC_BURDEN_7_1", "referencia": "Burden & Faires (10a ed.), Sec. 7.3 — Jacobi", "construir": lambda r: _construir_sistema_iterativo(r, "Jacobi", "potenciales eléctricos nodales", False)},
        {"id": "S3_JAC_NIEVES_TERM", "referencia": "Nieves & Domínguez, Cap. 3 — Placa térmica estacionaria", "construir": lambda r: _construir_sistema_iterativo(r, "Jacobi", "distribución de temperaturas en placa", True)},
    ],
    "Línea Recta": [
        {"id": "S4_LR_ZAMORA_OF", "referencia": "Apuntes Ing. Oralia Zamora — Línea Recta (OR/MCuadrados)", "construir": lambda r: _construir_ajuste(r, "Línea Recta", "datos experimentales de clase (6 puntos)")},
        {"id": "S4_LR_CHAPRA_17_1", "referencia": "Chapra & Canale (7a ed.), Ej. 17.1 — Regresión lineal", "construir": lambda r: _construir_ajuste(r, "Línea Recta", "velocidad terminal experimental")},
    ],
    "Cuadrática": [
        {"id": "S4_CUAD_CHAPRA_17_4", "referencia": "Chapra & Canale (7a ed.), Ej. 17.4 — Regresión polinomial", "construir": lambda r: _construir_ajuste(r, "Cuadrática", "curva de calibración parabólica")},
        {"id": "S4_CUAD_BURDEN_8_1", "referencia": "Burden & Faires (10a ed.), Sec. 8.1 — Trayectoria balística", "construir": lambda r: _construir_ajuste(r, "Cuadrática", "trayectoria vertical de sonda")},
    ],
    "Cúbica": [
        {"id": "S4_CUB_CHAPRA_17_B", "referencia": "Chapra & Canale (7a ed.), Cap. 17 — Curva de bomba", "construir": lambda r: _construir_ajuste(r, "Cúbica", "carga dinámica de bomba hidráulica")},
        {"id": "S4_CUB_ZAMORA_LAB", "referencia": "Apuntes Ing. Oralia Zamora — Ajuste Polinomial Cúbico", "construir": lambda r: _construir_ajuste(r, "Cúbica", "calor específico vs temperatura")},
    ],
    "Lineal con Función": [
        {"id": "S4_LF_CHAPRA_LN", "referencia": "Chapra & Canale (7a ed.), Sec. 17.1.5 — Linealización log.", "construir": lambda r: _construir_ajuste(r, "Lineal con Función", "caída de presión logarítmica", "ln")},
        {"id": "S4_LF_ZAMORA_SIN", "referencia": "Apuntes Ing. Oralia Zamora — Mínimos Cuadrados con Función", "construir": lambda r: _construir_ajuste(r, "Lineal con Función", "respuesta armónica de actuador", "sin")},
    ],
    "Cuadrática con Función": [
        {"id": "S4_CF_ZAMORA_EXP", "referencia": "Apuntes Ing. Oralia Zamora — Cuadrática con Función", "construir": lambda r: _construir_ajuste(r, "Cuadrática con Función", "crecimiento térmico exponencial", "exp")},
        {"id": "S4_CF_NIEVES_SQRT", "referencia": "Nieves & Domínguez, Cap. 6 — Ajuste en base logarítmica", "construir": lambda r: _construir_ajuste(r, "Cuadrática con Función", "descarga en base ln(x)", "ln")},
    ],
    "Regla Trapezoidal": [
        {"id": "S5_TRAP_CHAPRA_21_2", "referencia": "Chapra & Canale (7a ed.), Ej. 21.2 — Regla del trapecio", "construir": lambda r: _construir_integracion(r, "Regla Trapezoidal", False, "energía disipada analítica")},
        {"id": "S5_TRAP_TABLA", "referencia": "Nieves & Domínguez, Cap. 7 — Integración tabular discreta", "construir": lambda r: _construir_integracion(r, "Regla Trapezoidal", True, "flujo volumétrico tabular")},
    ],
    "Regla de 1/3 de Simpson": [
        {"id": "S5_S13_CHAPRA_21_4", "referencia": "Chapra & Canale (7a ed.), Ej. 21.4 — Simpson 1/3", "construir": lambda r: _construir_integracion(r, "Regla de 1/3 de Simpson", False, "impulso total del propulsor")},
        {"id": "S5_S13_TABLA", "referencia": "Burden & Faires (10a ed.), Sec. 4.4 — Tabla de potencia", "construir": lambda r: _construir_integracion(r, "Regla de 1/3 de Simpson", True, "potencia eléctrica registrada")},
    ],
    "Regla de 3/8 de Simpson": [
        {"id": "S5_S38_CHAPRA_21_5", "referencia": "Chapra & Canale (7a ed.), Ej. 21.5 — Simpson 3/8", "construir": lambda r: _construir_integracion(r, "Regla de 3/8 de Simpson", False, "transferencia de calor")},
        {"id": "S5_S38_TABLA", "referencia": "Nieves & Domínguez, Cap. 7 — Tabla de fuerza variable", "construir": lambda r: _construir_integracion(r, "Regla de 3/8 de Simpson", True, "trabajo mecánico en tabla")},
    ],
    "Newton – Cotes Abiertas": [
        {"id": "S5_NCA_ZAMORA_OF", "referencia": "Apuntes Ing. Oralia Zamora — Tabla Oficial Newton-Cotes Abiertas", "construir": lambda r: _construir_integracion(r, "Newton – Cotes Abiertas", False, "integral con extremos singulares")},
        {"id": "S5_NCA_BURDEN_4_3", "referencia": "Burden & Faires (10a ed.), Sec. 4.3 — Fórmulas abiertas", "construir": lambda r: _construir_integracion(r, "Newton – Cotes Abiertas", True, "nodos interiores abiertos en tabla")},
    ],
    "Newton - Cotes Cerradas": [
        {"id": "S5_NCC_ZAMORA_OF", "referencia": "Apuntes Ing. Oralia Zamora — Tabla Oficial Newton-Cotes Cerradas", "construir": lambda r: _construir_integracion(r, "Newton - Cotes Cerradas", False, "flujo magnético en intervalo cerrado")},
        {"id": "S5_NCC_TABLA", "referencia": "Chapra & Canale (7a ed.), Sec. 21.3 — Cuadratura cerrada tabular", "construir": lambda r: _construir_integracion(r, "Newton - Cotes Cerradas", True, "consumo térmico tabular")},
    ],
    "Euler Modificado": [
        {"id": "S6_EM_ZAMORA_RL", "referencia": "Apuntes Ing. Oralia Zamora — Euler Modificado (OR/EDO)", "construir": lambda r: _construir_edo_1er(r, "Euler Modificado", "clase_implicita", "despeje y'=f(y,t) en reactor/circuito")},
        {"id": "S6_EM_CHAPRA_25_5", "referencia": "Chapra & Canale (7a ed.), Ej. 25.5 — Heun", "construir": lambda r: _construir_edo_1er(r, "Euler Modificado", "lineal", "concentración química en reactor")},
    ],
    "Runge - Kutta 2ndo Orden": [
        {"id": "S6_RK2_CHAPRA_25_6", "referencia": "Chapra & Canale (7a ed.), Sec. 25.3 — Runge-Kutta 2do Orden", "construir": lambda r: _construir_edo_1er(r, "Runge - Kutta 2ndo Orden", "bilineal", "balance de masa transitorio")},
        {"id": "S6_RK2_BURDEN_5_4", "referencia": "Burden & Faires (10a ed.), Sec. 5.4 — Enfriamiento transitorio", "construir": lambda r: _construir_edo_1er(r, "Runge - Kutta 2ndo Orden", "lineal", "enfriamiento en módulo orbital")},
    ],
    "Runge - Kutta 3er Orden": [
        {"id": "S7_RK3_CHAPRA_25_8", "referencia": "Chapra & Canale (7a ed.), Sec. 25.3.2 — RK3 Clásico", "construir": lambda r: _construir_edo_1er(r, "Runge - Kutta 3er Orden", "bilineal", "descompresión controlada")},
        {"id": "S7_RK3_ZAMORA_EDO", "referencia": "Apuntes Ing. Oralia Zamora — Runge-Kutta 3er Orden", "construir": lambda r: _construir_edo_1er(r, "Runge - Kutta 3er Orden", "lineal", "dinámica de presión en tanque")},
    ],
    "Runge - Kutta 4rto Orden por 1/3 de Simpson": [
        {"id": "S7_RK4_13_CHAPRA_25_7", "referencia": "Chapra & Canale (7a ed.), Ej. 25.7 — RK4 Clásico (1/3)", "construir": lambda r: _construir_edo_1er(r, "Runge - Kutta 4rto Orden por 1/3 de Simpson", "bilineal", "propulsión orbital en ascenso")},
        {"id": "S7_RK4_13_BURDEN_5_4", "referencia": "Burden & Faires (10a ed.), Sec. 5.4 — RK4 de alta precisión", "construir": lambda r: _construir_edo_1er(r, "Runge - Kutta 4rto Orden por 1/3 de Simpson", "lineal", "disipación térmica de escudo")},
    ],
    "Runge - Kutta 4rto Orden por 3/8 de Simpson": [
        {"id": "S7_RK4_38_ZAMORA_OF", "referencia": "Apuntes Ing. Oralia Zamora — RK4 Regla 3/8 Oficial", "construir": lambda r: _construir_edo_1er(r, "Runge - Kutta 4rto Orden por 3/8 de Simpson", "bilineal", "trayectoria con coeficientes 3/8")},
        {"id": "S7_RK4_38_NIEVES_DIN", "referencia": "Nieves & Domínguez / Formulario Oficial — RK4 3/8", "construir": lambda r: _construir_edo_1er(r, "Runge - Kutta 4rto Orden por 3/8 de Simpson", "lineal", "respuesta transitoria amortiguada")},
    ],
    "Runge - Kutta de Orden Superior": [
        {"id": "S7_RKOS_ZAMORA_2DO", "referencia": "Apuntes Ing. Oralia Zamora — EDO 2do Orden", "construir": lambda r: _construir_edo_2do(r, "variable", "vibración forzada variable")},
        {"id": "S7_RKOS_CHAPRA_25_8", "referencia": "Chapra & Canale (7a ed.), Ej. 25.8 — Oscilador masa-resorte", "construir": lambda r: _construir_edo_2do(r, "amortiguado", "oscilador masa-resorte-amortiguador")},
    ],
}


# Tiempos escalonados por dificultad (Básico 240s, Intermedio 360s, Avanzado 480-600s)
TIEMPOS_METODO: Dict[str, int] = {
    "Interpolación lineal": 240,
    "Newton hacia adelante": 360,
    "Newton hacia atrás": 360,
    "Lagrange": 360,
    "Newton con diferencias divididas": 360,
    "Gráfico": 240,
    "Bisectriz": 360,
    "Newton-Raphson": 360,
    "Falsa Posición o Regula": 360,
    "Secante": 360,
    "Punto Fijo": 360,
    "Montante": 480,
    "Gauss - Jordan": 480,
    "Eliminación gaussiana": 480,
    "Gauss-Seidel": 480,
    "Jacobi": 480,
    "Línea Recta": 360,
    "Cuadrática": 480,
    "Cúbica": 540,
    "Lineal con Función": 480,
    "Cuadrática con Función": 540,
    "Regla Trapezoidal": 360,
    "Regla de 1/3 de Simpson": 360,
    "Regla de 3/8 de Simpson": 360,
    "Newton – Cotes Abiertas": 540,
    "Newton - Cotes Cerradas": 480,
    "Euler Modificado": 540,
    "Runge - Kutta 2ndo Orden": 540,
    "Runge - Kutta 3er Orden": 600,
    "Runge - Kutta 4rto Orden por 1/3 de Simpson": 600,
    "Runge - Kutta 4rto Orden por 3/8 de Simpson": 600,
    "Runge - Kutta de Orden Superior": 600,
}


def obtener_plantillas_metodo(nombre_metodo: str) -> List[Dict[str, Any]]:
    return BANCO_PLANTILLAS.get(normalizar_nombre_metodo(nombre_metodo), [])


def listar_metodos_con_plantillas() -> List[str]:
    return list(BANCO_PLANTILLAS.keys())


def generar_desde_banco(
    nombre_metodo: str,
    rng: Optional[random.Random] = None,
    seed_id: Optional[str] = None,
    excluir_plantilla_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Genera un problema reproducible desde una plantilla académica de libro."""
    nombre_norm = normalizar_nombre_metodo(nombre_metodo)
    plantillas = BANCO_PLANTILLAS.get(nombre_norm)
    if not plantillas:
        raise ValueError(f"Método no soportado en el generador: {nombre_metodo!r}")

    if seed_id is not None:
        idx, seed_num = _parsear_seed_id(seed_id, len(plantillas))
        plantilla = plantillas[idx]
        r_local = random.Random(seed_num)
        seed_final = str(seed_id)
    else:
        r = rng or random.Random()
        indices = [i for i, p in enumerate(plantillas) if p["id"] != excluir_plantilla_id]
        if not indices:
            indices = list(range(len(plantillas)))
        idx = r.choice(indices)
        seed_num = r.randint(100000, 999999)
        plantilla = plantillas[idx]
        r_local = random.Random(seed_num)
        seed_final = f"P{idx}-{seed_num}"

    mision = plantilla["construir"](r_local)
    mision["plantilla_id"] = plantilla["id"]
    mision["referencia"] = plantilla["referencia"]
    mision["seed_id"] = seed_final
    mision["oxigeno_seg"] = int(TIEMPOS_METODO.get(nombre_norm, mision.get("oxigeno_seg", 360)))
    return mision


def _parsear_seed_id(seed_id: str, total_plantillas: int) -> Tuple[int, int]:
    texto = str(seed_id).strip()
    if texto.startswith("P") and "-" in texto:
        pref, rest = texto[1:].split("-", 1)
        if pref.isdigit() and rest.isdigit():
            return int(pref) % max(1, total_plantillas), int(rest)
    if texto.isdigit():
        num = int(texto)
        return num % max(1, total_plantillas), num
    # Fallback determinista por hash simple estable
    h = 0
    for ch in texto:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return h % max(1, total_plantillas), h
