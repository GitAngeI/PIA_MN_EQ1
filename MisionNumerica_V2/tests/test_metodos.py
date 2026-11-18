"""Suite de validación contra los PDFs oficiales de la Ing. Oralia Zamora Pequeño."""

import csv
import json
import math
import os
import random
import sys
import tempfile
import tkinter as tk
import unittest

# Permite ejecutar test_metodos.py directamente desde cualquier CWD
_BASE_TEST = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BASE_TEST not in sys.path:
    sys.path.insert(0, _BASE_TEST)

from MisionNumerica_V2.juego.estado import EstadoJuego, calcular_estrellas
from MisionNumerica_V2.metodos import (
    interpolacion_lineal,
    newton_adelante,
    newton_atras,
    lagrange,
    newton_diferencias_divididas,
    metodo_grafico,
    metodo_bisectriz,
    metodo_newton_raphson,
    metodo_falsa_posicion,
    metodo_secante,
    metodo_punto_fijo,
    metodo_montante,
    metodo_gauss_jordan,
    eliminacion_gaussiana,
    metodo_gauss_seidel,
    metodo_jacobi,
    minimos_cuadrados_recta,
    minimos_cuadrados_cuadratica,
    minimos_cuadrados_cubica,
    minimos_cuadrados_lineal_funcion,
    minimos_cuadrados_cuadratica_funcion,
    regla_trapezoidal,
    simpson_un_tercio,
    simpson_tres_octavos,
    newton_cotes_abiertas,
    newton_cotes_cerradas,
    euler_modificado,
    runge_kutta_2,
    runge_kutta_3,
    runge_kutta_4_simpson_1_3,
    runge_kutta_4_simpson_3_8,
    runge_kutta_orden_superior,
)
from MisionNumerica_V2.metodos.integracion import ABIERTAS_TABLA, CERRADAS_TABLA, integrar_tabla
from MisionNumerica_V2.metodos.generadores import generar_mision, obtener_plantillas_metodo, _fmt
from MisionNumerica_V2.ui.calculadora import CalculadoraCientifica, evaluar_expresion_segura
from MisionNumerica_V2.ui.consola_mision import ConsolaMision
from MisionNumerica_V2.ui.estrellas import EstrellasCanvas
from MisionNumerica_V2.ui.formulas_latex import LATEX_METODOS, renderizar_formula_tk, limpiar_cache_formulas
from MisionNumerica_V2.ui.tema import TODOS_LOS_METODOS, SALAS, TEMAS_SALAS, FUNDAMENTOS_METODOS
from MisionNumerica_V2.ui.visor_grafica import VisorGraficaHUD


class TestMetodosOficiales(unittest.TestCase):
    def test_sala1_interpolacion_pdfs(self):
        # Interpolación Lineal PDF: Ln(3) entre Ln(2) y Ln(5)
        r_lin = interpolacion_lineal(2, 0.69314718, 5, 1.609437912, 3, 1.098612289)
        self.assertAlmostEqual(r_lin["gx"], 0.998577424, places=7)
        self.assertAlmostEqual(r_lin["error"], 0.100034865, places=7)

        # Newton hacia Adelante PDF
        xs_u = [1.7, 2.4, 3.1]
        ys_u = [0.35, 0.87, 1.03]
        r_na = newton_adelante(xs_u, ys_u, 3.0)
        self.assertAlmostEqual(r_na["s"], 1.857142857, places=6)
        self.assertAlmostEqual(r_na["gx"], 1.029183673, places=6)

        # Newton hacia Atrás PDF
        r_nat = newton_atras(xs_u, ys_u, 3.0)
        self.assertAlmostEqual(r_nat["s"], -0.142857142, places=6)
        self.assertAlmostEqual(r_nat["gx"], 1.029183673, places=6)

        # Lagrange con los mismos 3 puntos debe dar exactamente el mismo polinomio
        r_lag = lagrange(xs_u, ys_u, 3.0)
        self.assertAlmostEqual(r_lag["gx"], 1.029183673, places=6)

        # Newton con Diferencias Divididas PDF: x=7
        r_ndd = newton_diferencias_divididas([7.3, 6.5, 6.1], [-0.28, -1.35, -1.96], 7.0)
        self.assertAlmostEqual(r_ndd["gx"], -0.6578125, places=6)

    def test_sala2_raices(self):
        f = lambda x: x * x - 4.0
        df = lambda x: 2.0 * x
        self.assertIn((2.0, 2.0), metodo_grafico(f, 0.0, 4.0, 1.0)["intervalos"])
        self.assertIn((2.0, 3.0), metodo_grafico(lambda x: x * x - 5.0, 0.0, 4.0, 1.0)["intervalos"])
        self.assertAlmostEqual(metodo_bisectriz(f, 1.0, 3.0, 0.001)["raiz"], 2.0, places=2)
        self.assertAlmostEqual(metodo_falsa_posicion(f, 1.0, 3.0, 0.001)["raiz"], 2.0, places=3)
        self.assertAlmostEqual(metodo_newton_raphson(f, df, 3.0, 0.001)["raiz"], 2.0, places=4)
        self.assertAlmostEqual(metodo_secante(f, 1.0, 3.0, 0.001)["raiz"], 2.0, places=3)
        self.assertAlmostEqual(metodo_punto_fijo(lambda x: 0.5 * (x + 4.0 / x), 1.5, 0.001)["raiz"], 2.0, places=4)

    def test_sala3_sistemas(self):
        A = [[6.0, 1.0, 1.0], [1.0, 7.0, -1.0], [1.0, -1.0, 5.0]]
        b = [8.0, 7.0, 5.0]  # solución exacta [1, 1, 1]
        for fn in (metodo_montante, metodo_gauss_jordan, eliminacion_gaussiana):
            sol = fn(A, b)["solucion"]
            for v in sol:
                self.assertAlmostEqual(v, 1.0, places=5)
        for fn in (metodo_gauss_seidel, metodo_jacobi):
            res = fn(A, b, tol=0.0005)
            self.assertTrue(res["diagonal_dominante"])
            for v in res["solucion"]:
                self.assertAlmostEqual(v, 1.0, places=3)

    def test_sala4_ajuste_curvas_pdfs(self):
        # Línea Recta PDF
        xs = [1.1, 1.9, 2.4, 4.8, 5.1, 10.5]
        ys = [2.5, 2.7, 3.7, 5.2, 6.0, 8.3]
        r_rect = minimos_cuadrados_recta(xs, ys)
        self.assertAlmostEqual(r_rect["coeficientes"][0], 2.008443615, places=6)
        self.assertAlmostEqual(r_rect["coeficientes"][1], 0.633695283, places=6)

        # Cuadrática, Cúbica, Lineal+Función, Cuadrática+Función
        xs2 = [1.0, 2.0, 3.0, 4.0, 5.0]
        ys_q = [1.0 + 2.0 * x + 0.5 * x * x for x in xs2]
        c_q = minimos_cuadrados_cuadratica(xs2, ys_q)["coeficientes"]
        self.assertAlmostEqual(c_q[2], 0.5, places=5)

        ys_c = [1.0 + x - 0.2 * x * x + 0.1 * (x ** 3) for x in xs2]
        c_c = minimos_cuadrados_cubica(xs2, ys_c)["coeficientes"]
        self.assertAlmostEqual(c_c[3], 0.1, places=5)

        ys_lf = [1.0 + 0.5 * x + 2.0 * math.sin(x) for x in xs2]
        c_lf = minimos_cuadrados_lineal_funcion(xs2, ys_lf, math.sin)["coeficientes"]
        self.assertAlmostEqual(c_lf[2], 2.0, places=5)

        ys_cf = [1.0 + 0.5 * x + 0.2 * x * x + 1.5 * math.log(x) for x in xs2]
        c_cf = minimos_cuadrados_cuadratica_funcion(xs2, ys_cf, math.log)["coeficientes"]
        self.assertAlmostEqual(c_cf[3], 1.5, places=4)

    def test_sala5_integracion_pdfs(self):
        # Integral de 1 - x^2 en [0, 1] -> exacto 2/3 = 0.6666666667
        f = lambda x: 1.0 - x * x
        self.assertAlmostEqual(regla_trapezoidal(f, 0.0, 1.0, 4)["integral"], 0.65625, places=6)
        self.assertAlmostEqual(simpson_un_tercio(f, 0.0, 1.0, 4)["integral"], 2.0 / 3.0, places=7)
        self.assertAlmostEqual(simpson_tres_octavos(f, 0.0, 1.0, 3)["integral"], 2.0 / 3.0, places=7)
        self.assertAlmostEqual(newton_cotes_abiertas(f, 0.0, 1.0, 4)["integral"], 2.0 / 3.0, places=7)
        self.assertAlmostEqual(newton_cotes_cerradas(f, 0.0, 1.0, 4)["integral"], 2.0 / 3.0, places=7)

    def test_salas6_y_7_edo_pdfs(self):
        # Euler Modificado PDF: 3y' - 5yt + 1 = 0, y0=1.2, h=0.2, y1=2 => y'1 = 1.2
        r_em = euler_modificado(lambda y, t: (5.0 * y * t - 1.0) / 3.0, 1.2, 0.0, 0.2, pasos=1, y1_estimado=2.0)
        self.assertAlmostEqual(r_em["y_final"], 1.2, places=7)

        f = lambda y, t: 5.0 * y * t - 1.0
        # RK2 PDF: y0=2, h=0.2 => y1 = 1.98
        self.assertAlmostEqual(runge_kutta_2(f, 2.0, 0.0, 0.2, 1)["y_final"], 1.98, places=7)
        # RK3
        r_rk3 = runge_kutta_3(f, 2.0, 0.0, 0.2, 1)
        self.assertEqual(len(r_rk3["historial"]), 1)
        # RK4 1/3 Simpson PDF: y0=2, h=0.2 => y1 = 1.996483333
        self.assertAlmostEqual(runge_kutta_4_simpson_1_3(f, 2.0, 0.0, 0.2, 1)["y_final"], 1.996483333, places=7)
        # RK4 3/8 Simpson (fórmula exacta del PDF OR/EDO/R-K4toOrd3OctavosS.pdf)
        r_rk4_38 = runge_kutta_4_simpson_3_8(f, 2.0, 0.0, 0.2, 1)
        self.assertAlmostEqual(r_rk4_38["y_final"], 1.9919580247, places=6)
        # RK Orden Superior PDF: y'' - y't - y = 0, y0=1, y'0=2, h=0.5 => y1=2.125, y'1=3.0625
        r_os = runge_kutta_orden_superior(lambda v, u, q: v * q + u, 1.0, 2.0, 0.0, 0.5, 1)
        self.assertAlmostEqual(r_os["y_final"], 2.125, places=6)
        self.assertAlmostEqual(r_os["yp_final"], 3.0625, places=6)

    def test_generadores_32_metodos_y_temario(self):
        self.assertEqual(len(TODOS_LOS_METODOS), 32)
        self.assertEqual(len(SALAS), 7)
        self.assertEqual(sum(len(s[3]) for s in SALAS), 32)
        for i, m in enumerate(TODOS_LOS_METODOS):
            m1 = generar_mision(m, random.Random(100 + i))
            m2 = generar_mision(m, random.Random(200 + i))
            self.assertEqual(m1["metodo"], m)
            self.assertGreaterEqual(len(m1["pasos"]), 2)
            self.assertTrue(m1["formula"])
            # Verifica que los datos sean aleatorios entre intentos
            self.assertNotEqual((m1["enunciado"], m1["datos_tabla"]), (m2["enunciado"], m2["datos_tabla"]))
            # Verificar que ningún paso revele la respuesta numérica literal en la pista
            for paso in m1["pasos"]:
                if paso["tipo"] == "numero":
                    self.assertNotIn(f"= {_fmt(paso['esperado'])}", paso["pista"])
                    self.assertIn("tolerancia", paso)

    def test_newton_cotes_todas_las_tablas_y_bugs_num(self):
        # Todas las reglas abiertas (1..6) y cerradas (1..10) deben integrar polinómica de grado <= 2 exactamente
        f_const = lambda _x: 1.0
        f_quad = lambda x: 3.0 * x * x + 2.0
        for n in ABIERTAS_TABLA:
            self.assertAlmostEqual(newton_cotes_abiertas(f_const, 0.0, 2.0, n)["integral"], 2.0, places=7)
            if n >= 2:
                self.assertAlmostEqual(newton_cotes_abiertas(f_quad, 0.0, 2.0, n)["integral"], 12.0, places=6)
        for n in CERRADAS_TABLA:
            self.assertAlmostEqual(newton_cotes_cerradas(f_const, 0.0, float(n), n)["integral"], float(n), places=7)
            if n >= 2:
                self.assertAlmostEqual(newton_cotes_cerradas(f_quad, 0.0, 3.0, n)["integral"], 33.0, places=6)

        # Edge cases corregidos
        self.assertIn((4.0, 4.0), metodo_grafico(lambda x: x - 4.0, 0.0, 4.0, 1.0)["intervalos"])
        self.assertAlmostEqual(metodo_bisectriz(lambda x: x - 1.0, 1.0, 3.0)["raiz"], 1.0, places=6)
        self.assertAlmostEqual(metodo_falsa_posicion(lambda x: x - 3.0, 1.0, 3.0)["raiz"], 3.0, places=6)
        with self.assertRaises(ValueError):
            metodo_punto_fijo(lambda _x: float("nan"), 1.0)
        with self.assertRaises(ValueError):
            newton_adelante([1.0, 2.0, 1.0], [1.0, 2.0, 1.0], 1.5)
        with self.assertRaises(ValueError):
            lagrange([1.0, 1.0, 2.0], [2.0, 3.0, 4.0], 1.5)
        with self.assertRaises(ValueError):
            minimos_cuadrados_recta([1.0, 2.0, 3.0], [1.0, 2.0])

        # Montante con pivote inicial nulo debe intercambiar filas y conservar solución y signo de determinante
        A_p0 = [[0.0, 2.0, 1.0], [1.0, 1.0, 1.0], [2.0, -1.0, 3.0]]
        b_p0 = [5.0, 6.0, 9.0]
        r_mon = metodo_montante(A_p0, b_p0)
        r_gj = metodo_gauss_jordan(A_p0, b_p0)
        for xm, xj in zip(r_mon["solucion"], r_gj["solucion"]):
            self.assertAlmostEqual(xm, xj, places=6)
        self.assertAlmostEqual(r_mon["determinante"], -5.0, places=6)

    def test_generadores_invariantes_y_validaciones(self):
        with self.assertRaises(ValueError):
            generar_mision("Metodo Inventado")

        # Cobertura 100% entre catálogos de tema y formulas_latex
        self.assertEqual(set(TODOS_LOS_METODOS), set(LATEX_METODOS.keys()))
        self.assertEqual(set(TODOS_LOS_METODOS), set(FUNDAMENTOS_METODOS.keys()))

        # Punto Fijo debe cumplir estrictamente |g'(x0)| < 1 (ambas plantillas) y RK Orden Superior debe incluir t0
        for s in range(40):
            m_pf = generar_mision("Punto Fijo", random.Random(s))
            tabla = dict(m_pf["datos_tabla"][1])
            expr = tabla["g(x)"].strip()
            x0 = float(tabla["x0"])
            if expr.startswith("e^(-"):
                a_pf = float(expr[len("e^(-"):-2])
                dg = abs(-a_pf * math.exp(-a_pf * x0))
            else:
                # Formato "c / (x + k)"
                partes = expr.split("/")
                c_pf = float(partes[0].strip())
                k_pf = float(partes[1].replace("(x +", "").replace(")", "").strip())
                dg = abs(-c_pf / ((x0 + k_pf) ** 2))
            self.assertLess(dg, 1.0)

            m_rkos = generar_mision("Runge - Kutta de Orden Superior", random.Random(s))
            self.assertIn("t0", m_rkos["enunciado"])
            self.assertIn("t0", dict(m_rkos["datos_tabla"][1]))

        # Gauss-Seidel / Jacobi debe ejercitar tanto diagonal dominante como reordenamiento en 20 semillas
        opciones_gs = {
            generar_mision("Gauss-Seidel", random.Random(s))["pasos"][0]["indice_correcto"]
            for s in range(20)
        }
        self.assertEqual(opciones_gs, {0, 1})

    def test_estado_juego_estrellas_y_tolerancia(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "prog.json")
            # JSON corrupto debe respaldarse en .corrupt.bak sin crashear
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("{corrupto")
            est = EstadoJuego(ruta=ruta)
            self.assertIsNotNone(est.ultimo_error_carga)
            baks = [n for n in os.listdir(tmp) if ".corrupt.bak" in n]
            self.assertEqual(len(baks), 1)

            # Verificar estrellas .5 y piso 0.5 al completar vs 0.0 pendiente
            self.assertEqual(calcular_estrellas(0), 3.0)
            self.assertEqual(calcular_estrellas(1), 2.5)
            self.assertEqual(calcular_estrellas(5), 0.5)
            self.assertEqual(calcular_estrellas(9), 0.5)
            self.assertEqual(est.obtener_estrellas("Lagrange"), 0.0)

            self.assertTrue(est.registrar_victoria("Lagrange", 10.0, errores_intento=2))
            self.assertEqual(est.obtener_estrellas("Lagrange"), 2.0)
            # 9.97 redondea a 10.0: NO debe marcar falso récord
            self.assertFalse(est.registrar_victoria("Lagrange", 9.97, errores_intento=0))
            self.assertEqual(est.obtener_estrellas("Lagrange"), 3.0)

            est.completados["ClaveFalsa"] = True
            self.assertEqual(est.total_completados(), 1)
            est.reiniciar()
            self.assertEqual(est.total_completados(), 0)
            self.assertEqual(est.total_estrellas(), 0.0)

        # Tolerancia combinada: acepta redondeo en magnitud grande, rechaza 0 en magnitud pequeña
        self.assertTrue(ConsolaMision.es_respuesta_numerica_valida(1253.0, 1250.0, 0.02))
        self.assertFalse(ConsolaMision.es_respuesta_numerica_valida(0.0, 0.005, 0.001))

    def test_cache_formulas_multi_tk(self):
        limpiar_cache_formulas()
        for _ in range(2):
            root = tk.Tk()
            root.withdraw()
            try:
                img = renderizar_formula_tk(LATEX_METODOS["Interpolación lineal"], max_ancho=400)
                self.assertIsNotNone(img)
            finally:
                root.destroy()

    def test_v4_calculadora_cientifica_ast_segura(self):
        from MisionNumerica_V2.ui.calculadora import CalculadoraCientifica

        self.assertAlmostEqual(evaluar_expresion_segura("2^3 + sqrt(16) - ln(e)"), 11.0, places=9)
        self.assertAlmostEqual(evaluar_expresion_segura("sin(30) + cos(60)", modo_grados=True), 1.0, places=9)
        self.assertAlmostEqual(evaluar_expresion_segura("ans * 2 + log(100)", ans=4.5), 11.0, places=9)
        self.assertAlmostEqual(evaluar_expresion_segura("sen(pi/2)", modo_grados=False), 1.0, places=9)

        # Factorial postfijo (!), expresiones agrupadas y fact()/factorial() para Newton
        self.assertEqual(evaluar_expresion_segura("0!"), 1.0)
        self.assertEqual(evaluar_expresion_segura("5!"), 120.0)
        self.assertEqual(evaluar_expresion_segura("(2+3)!"), 120.0)
        self.assertEqual(evaluar_expresion_segura("-3!"), -6.0)
        self.assertEqual(evaluar_expresion_segura("3!!"), 720.0)
        self.assertEqual(evaluar_expresion_segura("fact(4) + factorial(3)"), 30.0)
        self.assertAlmostEqual(evaluar_expresion_segura("1.5 * (1.5 - 1) * (1.5 - 2) / 3!"), -0.0625, places=9)

        root = tk.Tk()
        root.withdraw()
        try:
            calc = CalculadoraCientifica(root)
            calc.entry_expr.insert(0, "4")
            calc._insertar("!")
            self.assertEqual(calc.calcular(), 24.0)
            calc.destroy()
        finally:
            root.destroy()

        for peligrosa in (
            "__import__('os').system('echo x')",
            "open('x.txt').read()",
            "9**9**9",
            "(-1)**0.5",
            "ln(-2)",
            "sqrt(-9)",
            "1/0",
            "3.5!",
            "(-3)!",
            "171!",
            "!5",
        ):
            with self.assertRaises((ValueError, OverflowError, ZeroDivisionError)):
                evaluar_expresion_segura(peligrosa)

    def test_v4_integracion_tabular_y_banco_64_plantillas(self):
        # Integracion sobre tabla discreta uniforme
        xs = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        fs = [x * x for x in xs]
        r_trap = integrar_tabla("Regla Trapezoidal", xs, fs)
        r_s13 = integrar_tabla("Regla de 1/3 de Simpson", xs, fs)
        r_s38 = integrar_tabla("Regla de 3/8 de Simpson", xs, fs)
        self.assertAlmostEqual(r_s13["integral"], 9.0, places=9)
        self.assertAlmostEqual(r_s38["integral"], 9.0, places=9)
        self.assertAlmostEqual(r_trap["integral"], 9.125, places=9)

        # Rechazar paso no uniforme
        with self.assertRaises(ValueError):
            integrar_tabla("Regla Trapezoidal", [0.0, 0.5, 1.4], [1.0, 2.0, 3.0])

        # Validar >= 2 plantillas de libro por cada uno de los 32 metodos y reproducibilidad por seed_id
        total_plantillas = 0
        for idx, m in enumerate(TODOS_LOS_METODOS):
            pls = obtener_plantillas_metodo(m)
            self.assertGreaterEqual(len(pls), 2, msg=f"Faltan plantillas en {m}")
            total_plantillas += len(pls)
            sid = f"P{idx % len(pls)}-{200000 + idx * 31}"
            a = generar_mision(m, seed_id=sid)
            b = generar_mision(m, seed_id=sid)
            self.assertEqual(a["seed_id"], sid)
            self.assertEqual(a["enunciado"], b["enunciado"])
            self.assertEqual(a["datos_tabla"], b["datos_tabla"])
            self.assertTrue(a["referencia"])
            self.assertIn("grafica", a)
            self.assertIn("tabla_progresiva", a)

            alt = generar_mision(m, rng=random.Random(99), excluir_plantilla_id=pls[0]["id"])
            self.assertNotEqual(alt["plantilla_id"], pls[0]["id"])
        self.assertGreaterEqual(total_plantillas, 64)

    def test_v4_estado_perfiles_hmac_y_reportes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "estado_v4.json")
            est = EstadoJuego(ruta=ruta)
            est.establecer_modo("practica", "Luis Perez", "1900111")
            est.registrar_victoria("Lagrange", 18.4, errores_intento=0, seed_id="P0-111111", plantilla_id="S1_LAG_CHAPRA_18_6")
            self.assertEqual(est.total_completados(), 1)

            # Perfil examen completamente aislado de practica
            est.establecer_modo("examen", "Luis Perez", "1900111")
            self.assertEqual(est.total_completados(), 0)
            est.registrar_victoria("Montante", 24.0, errores_intento=1, seed_id="P1-222222", plantilla_id="S3_MON_CHAPRA_REACT")
            est.registrar_micro_pausa("Montante", seed_id="P1-222222", duracion_s=0.9, paso=1)
            est.registrar_incidente_foco("Montante", seed_id="P1-222222", tipo="minimizado", duracion_s=4.2, paso=2)

            # Relectura verifica firma HMAC intacta
            est2 = EstadoJuego(ruta=ruta)
            self.assertTrue(est2.integridad_verificada)
            self.assertEqual(est2.incidentes_foco, 1)
            self.assertEqual(est2.micro_pausas_so, 1)

            # Exportacion TXT, CSV y JSON
            r_txt = os.path.join(tmp, "rep.txt")
            r_csv = os.path.join(tmp, "rep.csv")
            r_json = os.path.join(tmp, "rep.json")
            est2.exportar_reporte(r_txt, "txt", modo="examen")
            est2.exportar_reporte(r_csv, "csv", modo="examen")
            est2.exportar_reporte(r_json, "json", modo="examen")
            with open(r_txt, "r", encoding="utf-8") as ft:
                self.assertIn("Montante", ft.read())
            with open(r_csv, "r", encoding="utf-8-sig") as fc:
                filas = list(csv.reader(fc))
                self.assertEqual(len(filas), 36)
                self.assertTrue(any(len(f) >= 4 and f[1] == "Montante" and f[3] == "2.5" for f in filas))
            with open(r_json, "r", encoding="utf-8") as fj:
                payload = json.load(fj)
                self.assertEqual(payload["incidentes_foco"], 1)

            # Manipulacion externa debe romper verificacion HMAC
            with open(ruta, "r", encoding="utf-8") as f_raw:
                data = json.load(f_raw)
            data["examen"]["errores_totales"] = 999
            with open(ruta, "w", encoding="utf-8") as f_raw:
                json.dump(data, f_raw)
            est_tampered = EstadoJuego(ruta=ruta)
            self.assertFalse(est_tampered.integridad_verificada)

            # Reinicio selectivo vs total
            est_tampered.reiniciar(alcance="activo")
            self.assertEqual(est_tampered.total_completados(), 0)
            est_tampered.establecer_modo("practica")
            self.assertEqual(est_tampered.total_completados(), 1)
            est_tampered.reiniciar(alcance="todo")
            self.assertEqual(est_tampered.total_completados(), 0)

    def test_v4_estrellas_visor_y_seguridad_examen_tk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = tk.Tk()
            root.withdraw()
            try:
                ec = EstrellasCanvas(root, valor=2.5)
                ec.actualizar(1.5)
                ec.actualizar(0.5)

                vg = VisorGraficaHUD(root)
                for met in ("Lagrange", "Bisectriz", "Montante", "Regla Trapezoidal", "Euler Modificado"):
                    mis = generar_mision(met, random.Random(7))
                    vg.actualizar(mis, "#F4A261", paso_idx=0, completado=False)
                    vg.actualizar(mis, "#F4A261", paso_idx=2, completado=True)

                est = EstadoJuego(ruta=os.path.join(tmp, "ex.json"))
                est.establecer_modo("examen", "Carlos Ruiz", "2055511")
                vuelto = []
                con = ConsolaMision(root, "Bisectriz", est, al_volver=lambda: vuelto.append(True))
                root.update_idletasks()

                # Boton NUEVOS DATOS deshabilitado y pistas ocultas en examen
                self.assertEqual(str(con.btn_nuevos_datos.boton.cget("state")), "disabled")
                con.entry_resp.insert(0, "999999")
                con._verificar_paso()
                self.assertIn("deshabilitadas en Modo Examen", con.lbl_feedback.cget("text"))
                self.assertEqual(con.errores_intento, 1)

                # Simular perdida por minimizacion y regeneracion forzada de plantilla distinta
                seed_ini = con.mision["seed_id"]
                pl_ini = con.mision["plantilla_id"]
                con._confirmar_incidente_foco("minimizado", "VENTANA MINIMIZADA DETECTADA")
                self.assertTrue(con._breach_confirmado)
                self.assertIsNotNone(con._cortina_overlay)
                self.assertEqual(est.incidentes_foco, 1)
                con._reiniciar_por_incidente_foco()
                self.assertFalse(con._breach_confirmado)
                self.assertNotEqual(con.mision["plantilla_id"], pl_ini)
                self.assertNotEqual(con.mision["seed_id"], seed_ini)

                con._salir()
                self.assertEqual(vuelto, [True])
            finally:
                root.destroy()

    def test_v4_mapa_vectorial_responsivo_y_fuentes_grandes(self):
        import tkinter.font as tkfont
        from MisionNumerica_V2.ui import mapa_nave as mod_mapa
        from MisionNumerica_V2.ui.mapa_nave import MapaNaveAurora, SALAS_LAYOUT
        from MisionNumerica_V2.nave import NaveAuroraApp

        # Sin dependencia raster ni atributo RUTA_MAPA_IMG
        self.assertFalse(hasattr(mod_mapa, "RUTA_MAPA_IMG"))
        self.assertEqual(set(SALAS_LAYOUT.keys()), {1, 2, 3, 4, 5, 6, 7})

        with tempfile.TemporaryDirectory() as tmp:
            root = tk.Tk()
            root.attributes("-alpha", 0.0)
            root.geometry("1280x800+-4000+-4000")
            try:
                est = EstadoJuego(ruta=os.path.join(tmp, "ui_resp.json"))

                # 1) Mapa vectorial dibujado en canvas y navegacion WASD/salas
                entrados = []
                cambiados = []
                mapa = MapaNaveAurora(
                    root, est,
                    al_entrar_sala=lambda s: entrados.append(s),
                    al_cambiar_sala=lambda s: cambiados.append(s),
                    width=880, height=560,
                )
                mapa.pack(fill="both", expand=True)
                root.update()
                items_chico = len(mapa.find_all())
                self.assertGreater(items_chico, 40)

                root.geometry("1440x860+-4000+-4000")
                root.update()
                self.assertGreater(len(mapa.find_all()), 40)

                mapa.mover_tecla(1, 0)
                self.assertIn(mapa.sala_actual, {1, 4, 5, 6})
                self.assertGreaterEqual(len(cambiados), 1)
                mapa.destroy()

                # 2) ConsolaMision con letras grandes >= 12pt y 3 pestanas dedicadas
                con = ConsolaMision(root, "Lagrange", est, al_volver=lambda: None)
                con.pack(fill="both", expand=True)
                root.update()

                tam_enun = tkfont.Font(root=root, font=con.lbl_enunciado.cget("font")).cget("size")
                tam_tabla = tkfont.Font(root=root, font=con.txt_tabla.cget("font")).cget("size")
                tam_preg = tkfont.Font(root=root, font=con.lbl_pregunta.cget("font")).cget("size")
                self.assertGreaterEqual(abs(tam_enun), 12)
                self.assertGreaterEqual(abs(tam_tabla), 12)
                self.assertGreaterEqual(abs(tam_preg), 12)

                con._cambiar_tab_izq("progresiva")
                self.assertEqual(con._tab_izq_actual, "progresiva")
                con._cambiar_tab_izq("grafica")
                self.assertEqual(con._tab_izq_actual, "grafica")
                con._cambiar_tab_izq("tablas")
                self.assertEqual(con._tab_izq_actual, "datos")
                con.destroy()
            finally:
                root.destroy()

            # 3) Navegacion multi-resolucion en ventana real (compacta 940x600 y amplia 1440x880)
            app = NaveAuroraApp(estado=EstadoJuego(ruta=os.path.join(tmp, "app_resp.json")))
            app.attributes("-alpha", 0.0)
            try:
                for geom in ("940x600+-4000+-4000", "1440x880+-4000+-4000"):
                    app.geometry(geom)
                    app.mostrar_inicio()
                    app.update()
                    app.mostrar_historia()
                    app.update()
                    app.mostrar_mapa_nave()
                    app.update()
                    app.mostrar_sala(2)  # Sala con 6 metodos (la mas alta)
                    app.update()
                    app.mostrar_entorno_metodo("Bisectriz", 2)
                    app.update()
                    app.mostrar_mision("Bisectriz", 2)
                    app.update()
                    app.mostrar_certificado_final()
                    app.update()
            finally:
                app.destroy()

    def test_v4_1_mejoras_pia_y_formulas_oralia(self):
        from MisionNumerica_V2.ui.guias_metodos import GUIAS_METODOS
        from MisionNumerica_V2.ui.formulas_latex import LATEX_METODOS, renderizar_formula_tk

        # Cobertura completa de guias 3 pasos y LaTeX sin puntos suspensivos
        self.assertEqual(set(TODOS_LOS_METODOS), set(GUIAS_METODOS.keys()))
        self.assertEqual(set(TODOS_LOS_METODOS), set(LATEX_METODOS.keys()))
        for met, guia in GUIAS_METODOS.items():
            self.assertEqual(len(guia["pasos_guia"]), 3, met)
            self.assertTrue(guia["ecuaciones"].strip(), met)
        self.assertNotIn(r"\cdots", LATEX_METODOS["Newton hacia adelante"])
        self.assertNotIn(r"\dots", LATEX_METODOS["Runge - Kutta 3er Orden"])

        # Temporizadores escalonados (240s basico, 360s intermedio, 480-600s avanzado)
        self.assertEqual(generar_mision("Interpolación lineal", random.Random(1))["oxigeno_seg"], 240)
        self.assertEqual(generar_mision("Línea Recta", random.Random(1))["oxigeno_seg"], 360)
        self.assertEqual(generar_mision("Montante", random.Random(1))["oxigeno_seg"], 480)
        self.assertEqual(generar_mision("Newton – Cotes Abiertas", random.Random(1))["oxigeno_seg"], 540)
        self.assertEqual(generar_mision("Euler Modificado", random.Random(1))["oxigeno_seg"], 540)
        self.assertEqual(generar_mision("Runge - Kutta 3er Orden", random.Random(1))["oxigeno_seg"], 600)

        # Linea Recta: notacion Ing. Oralia g(x)=a0+a1*x + todas las sumatorias (n, sum x, sum y, sum x^2, sum xy)
        m_lr = generar_mision("Línea Recta", random.Random(3))
        self.assertIn("a0 + a1*x", m_lr["formula"])
        self.assertIn("sum x^2", m_lr["formula"])
        tp_lr_txt = " ".join(str(x) for fila in m_lr["tabla_progresiva"]["filas"] for x in fila["valores"])
        for token in ("sum x_i", "sum y_i", "sum x_i^2", "sum (x_i*y_i)"):
            self.assertIn(token, tp_lr_txt)

        # Newton-Cotes Abiertas muestra (b - a) / (n + 2) y pesos c_i en datos_tabla
        m_nca = generar_mision("Newton – Cotes Abiertas", random.Random(2))
        self.assertIn("n + 2", m_nca["formula"])
        datos_nca_txt = " ".join(str(x) for row in m_nca["datos_tabla"][1] for x in row)
        self.assertIn("n + 2", datos_nca_txt.replace("+2", " + 2"))

        # EDO muestra f(y, t) explicitamente y RK3 inicia por k1
        m_em = generar_mision("Euler Modificado", seed_id="P0-100001")
        self.assertIn("f(y, t)", m_em["pasos"][0]["pregunta"])
        self.assertIn("y*_{n+1}", m_em["formula"])
        self.assertIn("y'_{n+1}", m_em["formula"])
        m_rk3 = generar_mision("Runge - Kutta 3er Orden", random.Random(5))
        self.assertIn("k1", m_rk3["pasos"][0]["titulo"])
        self.assertIn("f(y, t)", m_rk3["pasos"][0]["pregunta"])

        # Modo Sin Tiempo solo permitido fuera de Modo Examen y UI embebida segura (? GUIA + Tooltips)
        with tempfile.TemporaryDirectory() as tmp:
            est = EstadoJuego(ruta=os.path.join(tmp, "rev.json"))
            self.assertTrue(est.establecer_sin_limite_tiempo(True))
            self.assertTrue(est.sin_limite_tiempo)
            est.establecer_modo("examen", "Ana Lopez", "2099888")
            self.assertFalse(est.sin_limite_tiempo)
            self.assertFalse(est.establecer_sin_limite_tiempo(True))

            est.establecer_modo("practica")
            est.establecer_sin_limite_tiempo(True)
            root = tk.Tk()
            root.attributes("-alpha", 0.0)
            root.geometry("980x640+-4000+-4000")
            try:
                for m in ("Línea Recta", "Euler Modificado", "Newton – Cotes Abiertas"):
                    self.assertIsNotNone(renderizar_formula_tk(LATEX_METODOS[m], "#FFD166"))

                con = ConsolaMision(root, "Euler Modificado", est, al_volver=lambda: None)
                con.pack(fill="both", expand=True)
                root.update()

                self.assertIn("LIBRE", con.lbl_oxigeno.cget("text"))
                self.assertTrue(con.lbl_tooltip_input.cget("text"))

                # Modal ? GUIA embebido (sin crear ningun Toplevel hijo!)
                con._abrir_modal_guia()
                root.update()
                self.assertIsNotNone(con._guia_overlay)
                self.assertEqual([c for c in root.winfo_children() if isinstance(c, tk.Toplevel)], [])
                con._cerrar_modal_guia()
                root.update()
                self.assertIsNone(con._guia_overlay)

                # Verificar sin tiempo sigue deduciendo -0.5 estrellas sin abortar
                con.entry_resp.insert(0, "99999")
                con._verificar_paso()
                self.assertEqual(con.errores_intento, 1)
                self.assertTrue(con.activo)

                con.destroy()
            finally:
                root.destroy()

    def test_v4_2_tema_claro_oscuro_y_persistencia(self):
        from MisionNumerica_V2.ui.tema import (
            PALETAS_TEMA,
            establecer_tema_actual,
            obtener_paleta,
            obtener_tema_actual,
        )
        from MisionNumerica_V2.ui.escenarios import obtener_escenario
        from MisionNumerica_V2.ui.formulas_latex import LATEX_METODOS, renderizar_formula_tk
        from MisionNumerica_V2.ui.mapa_progreso import MapaProgresoUI
        from MisionNumerica_V2.nave import NaveAuroraApp

        self.assertIn("claro", PALETAS_TEMA)
        self.assertIn("oscuro", PALETAS_TEMA)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                ruta = os.path.join(tmp, "tema_estado.json")
                est = EstadoJuego(ruta=ruta)
                self.assertEqual(est.tema_visual, "oscuro")
                est.registrar_victoria("Lagrange", 12.5, 0, seed_id="P0-111111", plantilla_id="S1_LAG_CHAPRA_18_6")
                est.establecer_tema_visual("claro")

                # Recargar desde disco conserva tema claro e integridad HMAC
                est2 = EstadoJuego(ruta=ruta)
                self.assertEqual(est2.tema_visual, "claro")
                self.assertTrue(est2.integridad_verificada)

                app = NaveAuroraApp(estado=est2)
                app.attributes("-alpha", 0.0)
                app.geometry("1200x760+-4000+-4000")
                try:
                    self.assertEqual(obtener_tema_actual(), "claro")
                    pal_c = obtener_paleta()
                    self.assertEqual(app.cget("bg"), pal_c["fondo"])

                    # Navegar todas las vistas en modo claro y luego alternar en vivo en mision
                    app.mostrar_inicio()
                    app.update()
                    app.mostrar_historia()
                    app.update()
                    app.mostrar_mapa_nave()
                    app.update()
                    app.mostrar_sala(1)
                    app.update()
                    app.mostrar_entorno_metodo("Interpolación lineal", 1)
                    app.update()
                    app.mostrar_certificado_final()
                    app.update()

                    # ConsolaMision: alternar tema claro <-> oscuro sin perder problema ni paso ni calc
                    con = ConsolaMision(app, "Newton-Raphson", est2, al_volver=lambda: None)
                    con.pack(fill="both", expand=True)
                    app.update()

                    seed_antes = con.mision["seed_id"]
                    con.entry_resp.insert(0, "1.234")
                    con.calculadora.entry_expr.insert(0, "4!")
                    con.calculadora.calcular()

                    # Cambiar a oscuro en vivo
                    con._alternar_tema()
                    app.update()
                    self.assertEqual(obtener_tema_actual(), "oscuro")
                    self.assertEqual(est2.tema_visual, "oscuro")
                    self.assertEqual(con.mision["seed_id"], seed_antes)
                    self.assertEqual(con.entry_resp.get(), "1.234")
                    self.assertEqual(con.calculadora.ans, 24.0)
                    self.assertEqual(con.lbl_enunciado.cget("fg"), obtener_paleta("oscuro")["texto"])

                    # Volver a claro en vivo y verificar renderizado LaTeX y escenarios legibles
                    con._alternar_tema()
                    app.update()
                    self.assertEqual(obtener_tema_actual(), "claro")
                    esc_c = obtener_escenario(1, "claro")
                    self.assertIsNotNone(renderizar_formula_tk(LATEX_METODOS["Interpolación lineal"], esc_c["acento"]))
                    self.assertEqual(con.txt_tabla.cget("bg"), pal_c["superficie"])
                    self.assertEqual(con.txt_tabla.cget("fg"), pal_c["texto"])
                    con._abrir_modal_guia()
                    app.update()
                    self.assertIsNotNone(con._guia_overlay)
                    con._cerrar_modal_guia()
                    con.destroy()

                    mp = MapaProgresoUI(app, est2, lambda _s: None)
                    app.update()
                    self.assertEqual(mp.cget("bg"), pal_c["fondo"])
                    mp.destroy()
                finally:
                    app.destroy()
        finally:
            establecer_tema_actual("oscuro")

    def test_v4_3_correcciones_revision_clase(self):
        # 1. Tema de Sala 1 debe decir solo "Interpolación"
        self.assertEqual(TEMAS_SALAS[1], "Interpolación")

        # 2. Ningun metodo individual debe iniciar con "Metodo" o "Método"
        for m in TODOS_LOS_METODOS:
            self.assertFalse(m.lower().startswith("metodo"), m)
            self.assertFalse(m.lower().startswith("método"), m)

        # 3. Todas las 32 formulas LaTeX deben renderizar sin fallos
        root = tk.Tk()
        root.withdraw()
        try:
            for m in TODOS_LOS_METODOS:
                self.assertIsNotNone(renderizar_formula_tk(LATEX_METODOS[m], "#FFD166"), msg=f"LaTeX fallo en {m}")
        finally:
            root.destroy()

        # 4. Claridad f(a), f(b) y f(x) real en Interpolación lineal (ambas plantillas)
        for seed in ("P0-101", "P1-101"):
            m_il = generar_mision("Interpolación lineal", seed_id=seed)
            encab, filas = m_il["datos_tabla"]
            self.assertNotIn("f(x)", encab)
            txt_filas = " ".join(str(c) for fila in filas for c in fila)
            self.assertIn("f(a)", txt_filas)
            self.assertIn("f(b)", txt_filas)
            self.assertIn("f(x) real", txt_filas)
            self.assertIn("1)", m_il["enunciado"])
            self.assertIn("2)", m_il["enunciado"])
            self.assertIn("3)", m_il["enunciado"])

        # 5. Migracion de nombres legados en EstadoJuego y alias en generar_mision
        m_alias = generar_mision("Metodo Bisectriz", seed_id="P0-202")
        self.assertEqual(m_alias["metodo"], "Bisectriz")
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "legacy.json")
            payload_legado = {
                "completados": {"Metodo Bisectriz": True, "Linea Recta": True},
                "estrellas": {"Metodo Bisectriz": 2.5, "Linea Recta": 3.0},
                "mejores_tiempos": {"Metodo Bisectriz": 42.3},
            }
            with open(ruta, "w", encoding="utf-8") as fh:
                json.dump(payload_legado, fh)
            est_mig = EstadoJuego(ruta=ruta)
            self.assertTrue(est_mig.completados.get("Bisectriz"))
            self.assertTrue(est_mig.completados.get("Línea Recta"))
            self.assertEqual(est_mig.obtener_estrellas("Bisectriz"), 2.5)
            self.assertEqual(est_mig.obtener_record("Bisectriz"), 42.3)


if __name__ == "__main__":
    unittest.main()
