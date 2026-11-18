"""Guía metodológica oficial de los 32 métodos (fórmulas completas de Ing. Oralia Zamora + resumen en 3 pasos)."""

from typing import Any, Dict

GUIAS_METODOS: Dict[str, Dict[str, Any]] = {
    "Interpolación lineal": {
        "fuente": "MC/Interpolacion/InterpolacionLineal.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "m = [f(b) - f(a)] / (b - a)\n"
            "g(x) = m * (x - a) + f(a)\n"
            "Error absoluto: e = |f(x) - g(x)|"
        ),
        "variables": "a, b: extremos conocidos; f(a), f(b): valores conocidos en los extremos; x: punto a interpolar; f(x): valor real (solo para calcular el error en el Paso 3).",
        "pasos_guia": [
            "1. Calcula la pendiente de la recta secante usando f(a) y f(b): m = [f(b) - f(a)] / (b - a).",
            "2. Sustituye en el modelo lineal g(x) = m*(x - a) + f(a) usando el extremo a y f(a).",
            "3. Compara g(x) contra el valor real f(x) únicamente en este último inciso: e = |f(x) - g(x)|.",
        ],
    },
    "Newton hacia adelante": {
        "fuente": "MC/Interpolacion/NewtonHaciaAdelante.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "h = |x_{i+1} - x_i| (paso uniforme),   s = (x - x1) / h   (s > 0)\n"
            "D1_i = y_{i+1} - y_i,   D2_i = D1_{i+1} - D1_i,   D3_i = D2_{i+1} - D2_i\n"
            "g(x) = y1 + D1_1*s + D2_1*s*(s - 1)/2! + D3_1*s*(s - 1)*(s - 2)/3!"
        ),
        "variables": "x1, y1: primer punto de la tabla; h: incremento constante; Dk_1: diferencias iniciales.",
        "pasos_guia": [
            "1. Verifica que x avance con paso constante h y calcula s = (x - x1) / h.",
            "2. Construye la tabla de diferencias progresivas por restas (fila abajo menos arriba).",
            "3. Sustituye s y la diagonal superior (y1, D1_1, D2_1) en la serie.",
        ],
    },
    "Newton hacia atrás": {
        "fuente": "MC/Interpolacion/NewtonHaciaAtras.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "h = |x_{i+1} - x_i| (paso uniforme),   s = (x - xn) / h   (s < 0)\n"
            "V1_n = y_n - y_{n-1},   V2_n = V1_n - V1_{n-1},   V3_n = V2_n - V2_{n-1}\n"
            "g(x) = yn + V1*s + V2*s*(s + 1)/2! + V3*s*(s + 1)*(s + 2)/3!"
        ),
        "variables": "xn, yn: último punto de la tabla; s < 0 por medir desde el final; Vk: diagonal inferior.",
        "pasos_guia": [
            "1. Identifica el último nodo xn y calcula s = (x - xn) / h (será negativo).",
            "2. Calcula las diferencias finitas regresivas y toma la diagonal inferior.",
            "3. Evalúa g(x) usando signos positivos (s + 1), (s + 2) en los factores.",
        ],
    },
    "Lagrange": {
        "fuente": "MC/Interpolacion/Lagrange.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "g(x) = sum_{i=1..n} y_i * L_i(x)\n"
            "L1(x) = [(x - x2)(x - x3)] / [(x1 - x2)(x1 - x3)]\n"
            "L2(x) = [(x - x1)(x - x3)] / [(x2 - x1)(x2 - x3)]\n"
            "L3(x) = [(x - x1)(x - x2)] / [(x3 - x1)(x3 - x2)]"
        ),
        "variables": "i = 1, 2, 3 (base 1); L_i(x): multiplicador base de Lagrange; suma L_i(x) = 1.",
        "pasos_guia": [
            "1. Forma cada base L_i(x) omitiendo x_i en el producto del numerador y denominador.",
            "2. Verifica que L1(x) + L2(x) + L3(x) = 1 para detectar errores de signo.",
            "3. Multiplica cada y_i por su L_i(x) y suma todo para obtener g(x).",
        ],
    },
    "Newton con diferencias divididas": {
        "fuente": "MC/Interpolacion/NewtonconDiferenciasDivididas.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "D0 = y1,   D1,1 = (y2 - y1) / (x2 - x1),   D1,2 = (y3 - y2) / (x3 - x2)\n"
            "D2,1 = (D1,2 - D1,1) / (x3 - x1)\n"
            "g(x) = D0 + D1,1*(x - x1) + D2,1*(x - x1)*(x - x2)"
        ),
        "variables": "Aplica a nodos no equidistantes (base 1). D1,1 y D2,1 toman los coeficientes superiores.",
        "pasos_guia": [
            "1. Calcula las primeras diferencias divididas D1,1 y D1,2 entre pares adyacentes.",
            "2. Calcula D2,1 dividiendo (D1,2 - D1,1) entre el rango amplio (x3 - x1).",
            "3. Arma g(x) = y1 + D1,1*(x - x1) + D2,1*(x - x1)*(x - x2).",
        ],
    },
    "Gráfico": {
        "fuente": "MC/EcuacionesNoLineales/EcNoLGraficoBisectriz.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Tabla x_k = x_ini + k * delta_x -> f(x_k)\n"
            "Cambio de signo: f(x_k) * f(x_{k+1}) <= 0  =>  raíz en [x_k, x_{k+1}]"
        ),
        "variables": "delta_x: incremento constante de tabulación; [a, b]: primer subintervalo con cambio de signo.",
        "pasos_guia": [
            "1. Evalúa f(x) en cada nodo equiespaciado dentro del rango pedido.",
            "2. Localiza dos valores consecutivos donde f(x_k) y f(x_{k+1}) cambien de signo.",
            "3. Estima la raíz promediando los extremos del subintervalo: (a + b) / 2.",
        ],
    },
    "Bisectriz": {
        "fuente": "MC/EcuacionesNoLineales/EcNoLGraficoBisectriz.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Condición inicial: f(a) * f(b) < 0\n"
            "xr = (a + b) / 2\n"
            "Si f(a)*f(xr) < 0 -> b = xr;   en caso contrario -> a = xr\n"
            "Error: e = |x_{i+1} - x_i| <= 0.001"
        ),
        "variables": "[a, b]: intervalo actual encerrando la raíz; xr: punto medio de la iteración.",
        "pasos_guia": [
            "1. Verifica f(a)*f(b) < 0 y calcula el punto medio xr1 = (a + b) / 2.",
            "2. Evalúa f(xr1) y conserva la mitad cuyo producto de signos siga siendo negativo.",
            "3. Repite (a + b) / 2 con el nuevo intervalo reducido.",
        ],
    },
    "Newton-Raphson": {
        "fuente": "MC/EcuacionesNoLineales/NR.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "x_{i+1} = x_i - f(x_i) / f'(x_i)\n"
            "Error: e = |x_{i+1} - x_i| <= 0.001"
        ),
        "variables": "x0: punto inicial cercano a la raíz; f'(x): primera derivada analítica de f(x).",
        "pasos_guia": [
            "1. Obtén simbólicamente la derivada f'(x) (si hay trig/exp, evalúa en radianes).",
            "2. Calcula x1 = x0 - f(x0) / f'(x0).",
            "3. Usa x1 como nuevo punto para calcular f(x1), f'(x1) y x2.",
        ],
    },
    "Falsa Posición o Regula": {
        "fuente": "MC/EcuacionesNoLineales/FPosicion.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Condición inicial: f(a) * f(b) < 0\n"
            "xr = a - [f(a)*(b - a)] / [f(b) - f(a)]  (equiv. b - f(b)*(a-b)/(f(a)-f(b)))\n"
            "Reemplazo por signo: si f(a)*f(xr) < 0 -> b = xr; si no -> a = xr"
        ),
        "variables": "a, b: extremos actuales con signos opuestos en f.",
        "pasos_guia": [
            "1. Evalúa f(a) y f(b) y aplica la fórmula de intersección secante xr1.",
            "2. Revisa el signo de f(a)*f(xr1) para actualizar a o b.",
            "3. Recalcula f en el extremo nuevo y halla xr2.",
        ],
    },
    "Secante": {
        "fuente": "MC/EcuacionesNoLineales/Secante.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "x_{i+1} = x_i - [f(x_i) * (x_i - x_{i-1})] / [f(x_i) - f(x_{i-1})]\n"
            "Iniciando con x0 y x1 para obtener x2 y luego x3.\n"
            "Error: e = |x_{i+1} - x_i| <= 0.001"
        ),
        "variables": "x0, x1: dos puntos iniciales (no requieren signo opuesto).",
        "pasos_guia": [
            "1. Evalúa f(x0) y f(x1) y aplica la fórmula secante para obtener x2.",
            "2. Evalúa f(x2) y recorre los dos últimos puntos (x1, x2) para hallar x3.",
            "3. Calcula el error aproximado e = |x3 - x2|.",
        ],
    },
    "Punto Fijo": {
        "fuente": "MC/EcuacionesNoLineales/PFIJO.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "De f(x) = 0 despejar x = g(x) con |g'(x0)| < 1\n"
            "x_{i+1} = g(x_i),   Error: e = |x_{i+1} - x_i| <= 0.001"
        ),
        "variables": "g(x): forma iterativa contractiva ya despejada; x0: estimación inicial.",
        "pasos_guia": [
            "1. Sustituye x0 directo en g(x) para obtener x1 = g(x0).",
            "2. Alimenta x1 nuevamente en g para hallar x2 = g(x1).",
            "3. Repite una tercera vez para x3 = g(x2) y observa la convergencia.",
        ],
    },
    "Montante": {
        "fuente": "MC/EcuacionesLineales/EcuacionesLineales.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "N.E = [(E.P)(E.A) - (E.C.F.P)(E.C.C.P)] / P.A\n\n"
            "Donde:\n"
            "N.E = Nuevo Elemento\n"
            "E.P = Elemento Pivote\n"
            "E.A = Elemento Actual\n"
            "E.C.F.P = Elemento Correspondiente Fila Pivote\n"
            "E.C.C.P = Elemento Correspondiente Columna Pivote\n"
            "P.A = Pivote Anterior (inicia en 1)"
        ),
        "variables": "E.P no puede ser cero. Columnas del pivote se hacen cero; la fila pasa igual.",
        "pasos_guia": [
            "1. Define el E.P. La fila del pivote pasa igual y la columna se hace ceros.",
            "2. Calcula cada N.E con la fórmula dividiendo entre P.A (el pivote del paso anterior).",
            "3. El último pivote es el determinante. Divide los términos independientes entre este para hallar las variables.",
        ],
    },
    "Gauss - Jordan": {
        "fuente": "MC/EcuacionesLineales/EcuacionesLineales.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Pasos del método:\n"
            "1) La fila pivote se divide entre el elemento pivote y la columna se hace ceros.\n"
            "2) El elemento actual menos el elemento correspondiente en la columna pivote por el elemento correspondiente en la fila pivote.\n\n"
            "N.E = E.A - (E.C.C.P * E.C.F.P)"
        ),
        "variables": "Reducción hasta obtener la matriz identidad. La última columna contiene las soluciones.",
        "pasos_guia": [
            "1. Divide la fila pivote entre el elemento pivote y haz ceros la columna del pivote.",
            "2. Genera los demás términos restando al elemento actual el producto de los correspondientes en columna y fila pivote.",
            "3. Repite hasta formar la matriz identidad y lee los valores de las variables en la última columna.",
        ],
    },
    "Eliminación gaussiana": {
        "fuente": "MC/EcuacionesLineales/EcuacionesLineales.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "1) Operaciones de renglón para reducir a forma triangular.\n"
            "2) Sustitución hacia atrás para calcular progresivamente los valores."
        ),
        "variables": "Reducción a matriz triangular superior. No hay fórmula estricta, solo operaciones de filas.",
        "pasos_guia": [
            "1. Multiplica filas por constantes y suma o resta para hacer ceros debajo de la diagonal principal.",
            "2. Una vez en forma triangular, despeja la última incógnita en la última ecuación.",
            "3. Aplica sustitución hacia atrás progresivamente para encontrar el resto de variables.",
        ],
    },
    "Gauss-Seidel": {
        "fuente": "MC/EcuacionesLineales/Gauss-Seidel.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Pasos del método:\n"
            "1) Del sistema de ecuaciones se despeja una variable de cada una.\n"
            "2) Iniciar con un valor de cero todas las variables.\n"
            "3) El nuevo valor de la variable se obtiene y se usa inmediatamente en la siguiente ecuación."
        ),
        "variables": "Al calcular una variable, úsala enseguida para despejar la siguiente en la iteración.",
        "pasos_guia": [
            "1. Verifica que la matriz sea diagonal dominante (considerando valores absolutos).",
            "2. Despeja una variable por ecuación e inicialízalas en cero.",
            "3. Itera calculando cada variable y usando su nuevo valor de inmediato hasta que e <= 0.001.",
        ],
    },
    "Jacobi": {
        "fuente": "MC/EcuacionesLineales/Jacobi.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Pasos del método:\n"
            "1) Del sistema de ecuaciones se despeja una variable de cada una.\n"
            "2) Iniciar con un valor de uno todas las variables.\n"
            "3) Calcular el nuevo valor considerando estrictamente los valores de la iteración anterior."
        ),
        "variables": "Inicia todas las variables con valor uno. No actualices variables hasta terminar la iteración completa.",
        "pasos_guia": [
            "1. Verifica que la matriz sea diagonal dominante (considerando valores absolutos).",
            "2. Despeja una variable por ecuación e inicialízalas en uno.",
            "3. Itera calculando cada variable con los valores del paso anterior hasta que e <= 0.001.",
        ],
    },
    "Línea Recta": {
        "fuente": "OR/MCuadrados/LineaRecta.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Modelo de la clase:  g(x) = a0 + a1 * x\n"
            "Sistema normal 2x2:\n"
            "  1) n*a0 + (sum x)*a1 = sum y\n"
            "  2) (sum x)*a0 + (sum x^2)*a1 = sum xy\n"
            "Despeje directo:\n"
            "  a1 = [n*(sum xy) - (sum x)*(sum y)] / [n*(sum x^2) - (sum x)^2]\n"
            "  a0 = [sum y - a1*(sum x)] / n"
        ),
        "variables": "Requiere: n (cantidad de puntos), sum x, sum y, sum x^2 y sum xy. Aquí a1=pendiente, a0=ordenada.",
        "pasos_guia": [
            "1. Forma las columnas x, y, x^2, xy y calcula n, sum x, sum y, sum x^2 y sum xy.",
            "2. Resuelve el sistema normal 2x2 (o fórmula de a1) para obtener la pendiente a1.",
            "3. Sustituye a1 en ec. 1 para despejar a0 = (sum y - a1*sum x) / n.",
        ],
    },
    "Cuadrática": {
        "fuente": "OR/MCuadrados/CuadraticaCubica.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Modelo: g(x) = a0 + a1*x + a2*x^2\n"
            "Sistema normal 3x3:\n"
            "  [ n,      sum x,   sum x^2 | sum y    ]\n"
            "  [ sum x,  sum x^2, sum x^3 | sum xy   ]\n"
            "  [ sum x^2,sum x^3, sum x^4 | sum x^2y ]"
        ),
        "variables": "n, sum x, sum x^2, sum x^3, sum x^4, sum y, sum xy, sum x^2*y.",
        "pasos_guia": [
            "1. Calcula sumatorias de potencias x..x^4 y productos sum y, sum xy, sum x^2*y.",
            "2. Resuelve el sistema lineal 3x3 por Gauss/Montante para hallar a0, a1, a2.",
            "3. Evalúa el polinomio ajustado g(x) = a0 + a1*x + a2*x^2 en el x solicitado.",
        ],
    },
    "Cúbica": {
        "fuente": "OR/MCuadrados/CuadraticaCubica.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Modelo: g(x) = a0 + a1*x + a2*x^2 + a3*x^3\n"
            "Matriz normal 4x4 simétrica con sumatorias desde n hasta sum x^6,\n"
            "vector derecho [sum y, sum xy, sum x^2*y, sum x^3*y]."
        ),
        "variables": "a0, a1, a2, a3: coeficientes del ajuste polinómico de 3er grado.",
        "pasos_guia": [
            "1. Calcula sum x^k (k=1..6) y momentos con y hasta sum x^3*y.",
            "2. Resuelve el sistema normal 4x4 para extraer a3 (y los demás coeficientes).",
            "3. Evalúa g(x) = a0 + a1*x + a2*x^2 + a3*x^3 en el x pedido.",
        ],
    },
    "Lineal con Función": {
        "fuente": "OR/MCuadrados/LinealCuadraticaFuncion.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Modelo: g(x) = a0 + a1*x + a2*f(x)   (f: ln, exp, sin, cos, tan)\n"
            "Sistema normal 3x3:\n"
            "  [ n,     sum x,   sum f(x)   | sum y   ]\n"
            "  [ sum x, sum x^2, sum x*f(x) | sum xy  ]\n"
            "  [ sum f(x), sum x*f(x), sum f(x)^2 | sum y*f(x) ]"
        ),
        "variables": "f(x) en radianes si es trigonométrica. Se calculan columnas extra: f, x*f, f^2, y*f.",
        "pasos_guia": [
            "1. Evalúa f(x_i) en cada punto y calcula sum f(x_i).",
            "2. Arma la matriz 3x3 normal y resuélvela para despejar a0, a1 y a2.",
            "3. Sustituye el valor objetivo en g(x) = a0 + a1*x + a2*f(x).",
        ],
    },
    "Cuadrática con Función": {
        "fuente": "OR/MCuadrados/LinealCuadraticaFuncion.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Modelo: g(x) = a0 + a1*x + a2*x^2 + a3*f(x)   (f: ln, exp, sin, cos, tan)\n"
            "Sistema normal 4x4:\n"
            "  [ n,       sum x,     sum x^2,   sum f(x)     | sum y     ]\n"
            "  [ sum x,   sum x^2,   sum x^3,   sum x*f(x)   | sum xy    ]\n"
            "  [ sum x^2, sum x^3,   sum x^4,   sum x^2*f(x) | sum x^2*y ]\n"
            "  [ sum f(x), sum x*f(x), sum x^2*f(x), sum f(x)^2   | sum y*f(x)   ]"
        ),
        "variables": "f(x) en radianes si es trigonométrica. Se calculan columnas extra: f(x), x*f(x), x^2*f(x), f(x)^2, y*f(x).",
        "pasos_guia": [
            "1. Evalúa f(x_i) en cada punto y calcula sum f(x_i).",
            "2. Arma la matriz 4x4 normal y resuélvela para despejar a0, a1, a2 y a3.",
            "3. Sustituye el valor objetivo en g(x) = a0 + a1*x + a2*x^2 + a3*f(x).",
        ],
    },
    "Regla Trapezoidal": {
        "fuente": "OR/Integracion/RTMN.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "h = (b - a) / n,   x_i = a + i*h   (i = 0..n)\n"
            "I = (h / 2) * [ f(a) + 2 * sum_{i=1}^{n-1} f(x_i) + f(b) ]"
        ),
        "variables": "a, b: límites de integración; n: número de subintervalos; h: ancho de cada trapecio.",
        "pasos_guia": [
            "1. Calcula h = (b - a) / n y genera los n+1 nodos x_i = a + i*h.",
            "2. Evalúa f(x_i) en extremos (peso 1) y nodos internos (peso 2).",
            "3. Multiplica la suma ponderada por (h / 2).",
        ],
    },
    "Regla de 1/3 de Simpson": {
        "fuente": "OR/Integracion/R1tercioSimpson.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Requisito: n PAR.   h = (b - a) / n\n"
            "I = (h / 3) * [ f(x0) + 4*sum_{i impar} f(x_i) + 2*sum_{i par, 0<i<n} f(x_i) + f(xn) ]"
        ),
        "variables": "n siempre par; índices impares x1,x3,.. llevan peso 4; pares internos x2,x4,.. peso 2.",
        "pasos_guia": [
            "1. Calcula h = (b - a) / n (verificando n par) y ubica x1 = a + h.",
            "2. Asigna peso 1 a extremos, 4 a índices impares y 2 a índices pares interiores.",
            "3. Multiplica la suma total por (h / 3).",
        ],
    },
    "Regla de 3/8 de Simpson": {
        "fuente": "OR/Integracion/R3octavosSimpson.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Requisito: n múltiplo de 3.   h = (b - a) / n\n"
            "Simple (n=3): I = (3/8)h * [ f(a) + 3 * sum_{i=1}^{n-1} f(a + i*h) + f(b) ]\n"
            "Compuesta: pesos [1, 3, 3, 2, 3, 3, ..., 1]"
        ),
        "variables": "n múltiplo de 3; nodos internos no múltiplos de 3 llevan peso 3; múltiplos internos de 3 llevan peso 2.",
        "pasos_guia": [
            "1. Calcula h = (b - a) / n y evalúa los puntos x_i = a + i*h.",
            "2. Aplica pesos [1, 3, 3, 1] (si n=3) o peso 2 en uniones múltiplos de 3 (si n=6).",
            "3. Multiplica la suma ponderada por (3*h / 8).",
        ],
    },
    "Newton – Cotes Abiertas": {
        "fuente": "OR/Integracion/TNewtonCotesAyC.pdf & ConstantesN-CotesAC.pdf",
        "ecuaciones": (
            "h = (b - a) / (n + 2)     (¡SIEMPRE dividir entre n + 2 en Abiertas!)\n"
            "x_i = a + i*h   para i = 0, 1, ..., n+2\n"
            "I = alpha_n * h * sum_{i=1}^{n+1} c_i * f(x_i)   (extremos x0 y x_{n+2} tienen peso c=0)"
        ),
        "variables": "n es la cantidad de puntos interiores activos (el paso total tiene n+2 segmentos).",
        "pasos_guia": [
            "1. Calcula h = (b - a) / (n + 2) (NO entre n) y genera los nodos x1 = a+h .. x_{n+1}.",
            "2. Busca alpha_n y pesos c_i en la tabla oficial (extremos 0 no contribuyen).",
            "3. Multiplica alpha_n * h * sum(c_i * f(x_i)).",
        ],
        "tabla_extra": (
            "Constantes Abiertas Oficiales (Ing. Oralia Zamora):\n"
            "  n=1: alpha = 3/2     | c = [0, 1, 1, 0]\n"
            "  n=2: alpha = 4/3     | c = [0, 2, -1, 2, 0]\n"
            "  n=3: alpha = 5/24    | c = [0, 11, 1, 1, 11, 0]\n"
            "  n=4: alpha = 6/20    | c = [0, 11, -14, 26, -14, 11, 0]\n"
            "  n=5: alpha = 7/1440  | c = [0, 611, -453, 562, 562, -453, 611, 0]\n"
            "  n=6: alpha = 8/945   | c = [0, 460, -954, 2196, -2459, 2196, -954, 460, 0]"
        ),
    },
    "Newton - Cotes Cerradas": {
        "fuente": "OR/Integracion/RNewtonC-Cerradas.pdf & ConstantesN-CotesAC.pdf",
        "ecuaciones": (
            "h = (b - a) / n,   x_i = a + i*h   para i = 0, 1, ..., n\n"
            "I = alpha_n * h * sum_{i=0}^{n} c_i * f(x_i)   (incluye ambos extremos a y b)"
        ),
        "variables": "n: número de subintervalos en [a, b]. Incluye los n+1 puntos desde x0=a hasta xn=b.",
        "pasos_guia": [
            "1. Calcula h = (b - a) / n y evalúa f(x_i) en los n+1 puntos desde i=0 hasta n.",
            "2. Toma alpha_n y pesos c_i de la tabla cerrada para n.",
            "3. Calcula I = alpha_n * h * sum_{i=0..n} (c_i * f(x_i)).",
        ],
        "tabla_extra": (
            "Constantes Cerradas Oficiales (Ing. Oralia Zamora):\n"
            "  n=1: alpha = 1/2     | c = [1, 1]\n"
            "  n=2: alpha = 1/3     | c = [1, 4, 1]\n"
            "  n=3: alpha = 3/8     | c = [1, 3, 3, 1]\n"
            "  n=4: alpha = 2/45    | c = [7, 32, 12, 32, 7]\n"
            "  n=5: alpha = 5/288   | c = [19, 75, 50, 50, 75, 19]\n"
            "  n=6: alpha = 1/140   | c = [41, 216, 27, 272, 27, 216, 41]"
        ),
    },
    "Euler Modificado": {
        "fuente": "OR/EDO/EulerModificado.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "1) Despejar la EDO en la forma: y' = f(y, t)\n"
            "2) t_{n+1} = t_n + h,   y*_{n+1} = y_n + h * f(y_n, t_n)   (o y_1 estimado dado)\n"
            "3) Fase de Corrección:\n"
            "     y'_{n+1} = y_n + (h / 2) * [ f(y_n, t_n) + f(y_{n+1}, t_{n+1}) ]"
        ),
        "variables": "Ojo con el orden de Ing. Oralia: f(y, t) evalúa y primero y t después. t1 = t0 + h.",
        "pasos_guia": [
            "1. Con y0 y t0 en y' = f(y, t), evalúa la pendiente inicial f(y0, t0).",
            "2. Con t1 = t0 + h y el valor y1 estimado, evalúa la pendiente f(y1, t1).",
            "3. Calcula el valor corregido y'1 = y0 + (h/2)*[f(y0, t0) + f(y1, t1)].",
        ],
    },
    "Runge - Kutta 2ndo Orden": {
        "fuente": "OR/EDO/R-K2doOrd.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "y' = f(y, t)\n"
            "k1 = h * f(yn, tn)\n"
            "k2 = h * f(yn + k1, tn + h)\n"
            "y_{n+1} = yn + (1/2) * (k1 + k2)"
        ),
        "variables": "k1 y k2 son incrementos ya multiplicados por h.",
        "pasos_guia": [
            "1. Evalúa f(y0, t0) y multiplica por h para hallar k1.",
            "2. Calcula k2 evaluando h * f(y0 + k1, t0 + h).",
            "3. Promedia: y1 = y0 + 0.5 * (k1 + k2).",
        ],
    },
    "Runge - Kutta 3er Orden": {
        "fuente": "OR/EDO/R-K3erOrd.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "y' = f(y, t)\n"
            "k1 = h * f(yn, tn)\n"
            "k2 = h * f(yn + k1/2, tn + h/2)\n"
            "k3 = h * f(yn - k1 + 2*k2, tn + h)\n"
            "y_{n+1} = yn + (1/6) * (k1 + 4*k2 + k3)"
        ),
        "variables": "k1 se evalúa al inicio; k2 en el punto medio t+h/2; k3 al final t+h.",
        "pasos_guia": [
            "1. Calcula primero k1 = h * f(y0, t0).",
            "2. Con k1 halla k2 = h * f(y0 + k1/2, t0 + h/2) y k3 = h * f(y0 - k1 + 2*k2, t0 + h).",
            "3. Combina con regla 1/6: y1 = y0 + (k1 + 4*k2 + k3) / 6.",
        ],
    },
    "Runge - Kutta 4rto Orden por 1/3 de Simpson": {
        "fuente": "OR/EDO/R-K4toOrd1tercioS.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "y' = f(y, t)\n"
            "k1 = h * f(yn, tn)\n"
            "k2 = h * f(yn + k1/2, tn + h/2)\n"
            "k3 = h * f(yn + k2/2, tn + h/2)\n"
            "k4 = h * f(yn + k3, tn + h)\n"
            "y_{n+1} = yn + (1/6) * (k1 + 2*k2 + 2*k3 + k4)"
        ),
        "variables": "Ambos k2 y k3 usan t + h/2, pero k3 reemplaza k1 por k2.",
        "pasos_guia": [
            "1. Calcula k1 = h * f(y0, t0) en el punto inicial.",
            "2. Calcula k2 y k3 en el punto medio (h/2) y luego k4 = h * f(y0 + k3, t0 + h).",
            "3. Obtén y1 = y0 + (k1 + 2*k2 + 2*k3 + k4) / 6.",
        ],
    },
    "Runge - Kutta 4rto Orden por 3/8 de Simpson": {
        "fuente": "OR/EDO/R-K4toOrd3OctavosS.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "y' = f(y, t)\n"
            "k1 = h * f(yn, tn)\n"
            "k2 = h * f(yn + k1/3, tn + h/3)\n"
            "k3 = h * f(yn + k1/3 + k2/3, tn + 2h/3)\n"
            "k4 = h * f(yn + k1 - k2 + k3, tn + h)\n"
            "y_{n+1} = yn + (1/8) * (k1 + 3*k2 + 3*k3 + k4)"
        ),
        "variables": "Divide el paso en tercios (h/3 y 2h/3) y pondera 1-3-3-1 entre 8.",
        "pasos_guia": [
            "1. Calcula k1 = h * f(y0, t0).",
            "2. Evalúa k2 en t0 + h/3, k3 en t0 + 2h/3 y k4 en t0 + h con (y0 + k1 - k2 + k3).",
            "3. Aplica ponderación 3/8: y1 = y0 + (k1 + 3*k2 + 3*k3 + k4) / 8.",
        ],
    },
    "Runge - Kutta de Orden Superior": {
        "fuente": "OR/EDO/R-KOrdenSuperior.pdf (Ing. Oralia Zamora)",
        "ecuaciones": (
            "Vn = y'_n,   Un = y_n,   qn = t_n\n"
            "k1 = h * Vn,             m1 = h * [±a*Vn ± b*Un, qn]\n"
            "k2 = h * (Vn + m1),      m2 = h * [±a*(Vn + m1) ± b*(Un + k1), qn + h]\n"
            "y_{n+1}  = y_n + (1/2)*(k1 + k2)\n"
            "y'_{n+1} = y'_n + (1/2)*(m1 + m2)"
        ),
        "variables": "U representa a y, V representa a y'. k avanza a y; m avanza a y'.",
        "pasos_guia": [
            "1. Convierte y'' en V' = g(V, U, t) y calcula k1 = h*V0 y m1 = h*g(V0, U0, t0).",
            "2. Calcula k2 = h*(V0 + m1) y m2 = h*g(V0 + m1, U0 + k1, t0 + h).",
            "3. Promedia (k1, k2) para hallar y1 y (m1, m2) para hallar y'1.",
        ],
    },
}
