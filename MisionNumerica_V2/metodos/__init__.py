"""Motor numérico oficial de Misión Numérica v3.0 (32 métodos en 7 salas)."""

from .interpolacion import (
    interpolacion_lineal,
    newton_adelante,
    newton_atras,
    lagrange,
    newton_diferencias_divididas,
)
from .raices import (
    metodo_grafico,
    metodo_bisectriz,
    metodo_newton_raphson,
    metodo_falsa_posicion,
    metodo_secante,
    metodo_punto_fijo,
)
from .sistemas import (
    metodo_montante,
    metodo_gauss_jordan,
    eliminacion_gaussiana,
    metodo_gauss_seidel,
    metodo_jacobi,
)
from .ajuste import (
    minimos_cuadrados_recta,
    minimos_cuadrados_cuadratica,
    minimos_cuadrados_cubica,
    minimos_cuadrados_lineal_funcion,
    minimos_cuadrados_cuadratica_funcion,
)
from .integracion import (
    regla_trapezoidal,
    simpson_un_tercio,
    simpson_tres_octavos,
    newton_cotes_abiertas,
    newton_cotes_cerradas,
)
from .edo import (
    euler_modificado,
    runge_kutta_2,
    runge_kutta_3,
    runge_kutta_4_simpson_1_3,
    runge_kutta_4_simpson_3_8,
    runge_kutta_orden_superior,
)

__all__ = [
    "interpolacion_lineal",
    "newton_adelante",
    "newton_atras",
    "lagrange",
    "newton_diferencias_divididas",
    "metodo_grafico",
    "metodo_bisectriz",
    "metodo_newton_raphson",
    "metodo_falsa_posicion",
    "metodo_secante",
    "metodo_punto_fijo",
    "metodo_montante",
    "metodo_gauss_jordan",
    "eliminacion_gaussiana",
    "metodo_gauss_seidel",
    "metodo_jacobi",
    "minimos_cuadrados_recta",
    "minimos_cuadrados_cuadratica",
    "minimos_cuadrados_cubica",
    "minimos_cuadrados_lineal_funcion",
    "minimos_cuadrados_cuadratica_funcion",
    "regla_trapezoidal",
    "simpson_un_tercio",
    "simpson_tres_octavos",
    "newton_cotes_abiertas",
    "newton_cotes_cerradas",
    "euler_modificado",
    "runge_kutta_2",
    "runge_kutta_3",
    "runge_kutta_4_simpson_1_3",
    "runge_kutta_4_simpson_3_8",
    "runge_kutta_orden_superior",
]
