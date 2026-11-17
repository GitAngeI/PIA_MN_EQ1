"""Paleta espacial cálida, tipografía grande (>= 16 pt) y catálogo oficial (0% emojis)."""

# Paleta espacial cálida (índigo-violeta profundo + ámbar + coral + crema)
FONDO_GALAXIA = "#130F21"
PANEL_OSCURO = "#1D1732"
PANEL_ELEVADO = "#271F42"
BORDE_CALIDO = "#4C3B6E"

AMBAR = "#F4A261"
DORADO = "#FFD166"
CORAL = "#E76F51"
ESMERALDA = "#5CE0A0"
VIOLETA_SUAVE = "#C09CFF"
CREMA = "#FAF3E8"
GRIS_CALIDO = "#C5B9D6"
ROJO_OXIGENO = "#FF4D6D"

FUENTE_UI = "Segoe UI"
FUENTE_MONO = "Consolas"

F_TITULO_XL = (FUENTE_UI, 28, "bold")
F_TITULO = (FUENTE_UI, 22, "bold")
F_SUBTITULO = (FUENTE_UI, 18, "bold")
F_CUERPO = (FUENTE_UI, 16)
F_CUERPO_BOLD = (FUENTE_UI, 16, "bold")
F_FORMULA = (FUENTE_MONO, 16, "bold")
F_TABLA = (FUENTE_MONO, 15)

TODOS_LOS_METODOS = [
    "Interpolación lineal",
    "Newton hacia adelante",
    "Newton hacia atrás",
    "Lagrange",
    "Newton con diferencias divididas",
    "Metodo Grafico",
    "Metodo Bisectriz",
    "Metodo Newton-Raphson",
    "Metodo de la Falsa Posicion o Regula",
    "Secante",
    "Punto Fijo",
    "Montante",
    "Gauss - Jordan",
    "Eliminacion gaussiana",
    "Gauss-Seidel",
    "Jacobi",
    "Linea Recta",
    "Cuadratica",
    "Cubica",
    "Lineal con Funcion",
    "Cuadratica con Funcion",
    "Regla Trapezoidal",
    "Regla de 1/3 de Simpson",
    "Regla de 3/8 de Simpson",
    "Newton – Cotes Abiertas",
    "Newton - Cotes Cerradas",
    "Euler Modificado",
    "Runge - Kutta 2ndo Orden",
    "Runge - Kutta 3er Orden",
    "Runge - Kutta 4rto Orden por 1/3 de Simpson",
    "Runge - Kutta 4rto Orden por 3/8 de Simpson",
    "Runge - Kutta de Orden Superior",
]

SALAS = [
    (1, "SISTEMA DE NAVEGACION", DORADO, TODOS_LOS_METODOS[0:5]),
    (2, "MOTORES PRINCIPALES", AMBAR, TODOS_LOS_METODOS[5:11]),
    (3, "RED ELECTRICA", CORAL, TODOS_LOS_METODOS[11:16]),
    (4, "ESCUDOS DEFENSIVOS", ESMERALDA, TODOS_LOS_METODOS[16:21]),
    (5, "TANQUES DE COMBUSTIBLE", VIOLETA_SUAVE, TODOS_LOS_METODOS[21:26]),
    (6, "TELEMETRIA Y RADARES", "#FF7B89", TODOS_LOS_METODOS[26:27]),
    (7, "COMPUTADORA CENTRAL", "#7CE0D3", TODOS_LOS_METODOS[27:32]),
]


def crear_boton_3d(parent, texto, comando, bg=AMBAR, fg="#160F24", sombra="#7A4922", fuente=F_CUERPO_BOLD, padx=20, pady=10):
    """Botón con base/sombra 3D para dar volumen físico al HUD."""
    import tkinter as tk
    contenedor = tk.Frame(parent, bg=sombra, bd=0)
    btn = tk.Button(
        contenedor, text=texto, command=comando,
        bg=bg, fg=fg, activebackground=DORADO, activeforeground="#160F24",
        font=fuente, bd=0, relief="raised", padx=padx, pady=pady, cursor="hand2",
    )
    btn.pack(padx=(0, 0), pady=(0, 4))

    def _press(_e):
        btn.pack_configure(pady=(2, 2))

    def _release(_e):
        btn.pack_configure(pady=(0, 4))

    btn.bind("<ButtonPress-1>", _press)
    btn.bind("<ButtonRelease-1>", _release)
    contenedor.boton = btn
    return contenedor

TEMAS_SALAS = {
    1: "Interpolacion y Diferencias",
    2: "Ecuaciones No Lineales (Raices)",
    3: "Sistemas de Ecuaciones Lineales",
    4: "Minimos Cuadrados (Ajuste de Curvas)",
    5: "Integracion Numerica",
    6: "Ecuaciones Diferenciales Ordinarias (EDO)",
    7: "Sistemas Runge - Kutta",
}

FUNDAMENTOS_METODOS = {
    "Interpolación lineal": "g(x) = [(f(b) - f(a)) / (b - a)] * (x - a) + f(a)\nMargen de error: e = |f(x) - g(x)|",
    "Newton hacia adelante": "h = |x_{i+1} - x_i| (uniforme),  s = (x - x1) / h  (s > 0)\ng(x) = y1 + D1*s + D2*s*(s-1)/2! + ...",
    "Newton hacia atrás": "h = |x_{i+1} - x_i| (uniforme),  s = (x - xn) / h  (s < 0)\ng(x) = yn + N1*s + N2*s*(s+1)/2! + ...",
    "Lagrange": "g(x) = sum_{i=1..n} y_i * prod_{j!=i} (x - x_j) / (x_i - x_j)\nAplica a intervalos uniformes y no uniformes.",
    "Newton con diferencias divididas": "D1_i = (y_{i+1}-y_i)/(x_{i+1}-x_i),  D2_i = (D1_{i+1}-D1_i)/(x_{i+2}-x_i)\ng(x) = y1 + D1_1*(x-x1) + D2_1*(x-x1)*(x-x2) + ...",
    "Metodo Grafico": "Tabula f(x) con paso dx constante.\nLa raiz esta en el intervalo [a, b] donde f(a)*f(b) <= 0.",
    "Metodo Bisectriz": "x_i = (a + b) / 2   (requiere f(a)*f(b) < 0)\nCriterio de paro: e = |x_{i+1} - x_i| <= 0.001",
    "Metodo Newton-Raphson": "x_{i+1} = x_i - f(x_i) / f'(x_i)\nCriterio de paro: e = |x_{i+1} - x_i| <= 0.001",
    "Metodo de la Falsa Posicion o Regula": "x_i = a - f(a)*(b - a) / (f(b) - f(a))\nCriterio de paro: e = |x_{i+1} - x_i| <= 0.001",
    "Secante": "x_{i+1} = x_{i+1} - (f(x_{i+1})*(x_{i+1} - x_i)) / (f(x_{i+1}) - f(x_i))\nCriterio de paro: e = |x_{i+1} - x_i| <= 0.001",
    "Punto Fijo": "Despejar f(x) = 0  =>  x = g(x) con |g'(x0)| < 1\nx_{i+1} = g(x_i),  e = |x_{i+1} - x_i| <= 0.001",
    "Montante": "Pivote anterior inicial p_ant = 1.\na'_ij = (a_kk * a_ij - a_ik * a_kj) / p_ant,  x_i = b'_i / det(A).",
    "Gauss - Jordan": "Reduccion por filas hasta matriz identidad [I | x].\nNormalizar pivote y anular arriba y abajo.",
    "Eliminacion gaussiana": "Eliminacion hacia adelante hasta matriz triangular superior [U | b']\ny sustitucion hacia atras.",
    "Gauss-Seidel": "Verificar Diagonal Dominante |a_ii| > sum |a_ij|. x0 = (0, 0, ..., 0).\nUsa inmediatamente los valores recien actualizados. e <= 0.001",
    "Jacobi": "Verificar Diagonal Dominante |a_ii| > sum |a_ij|. x0 = (1, 1, ..., 1).\nCalcula cada x_i^(k+1) usando solo los valores de la iteracion k. e <= 0.001",
    "Linea Recta": "g(x) = a0 + a1*x\nSistema normal 2x2 con [n, sum(x) | sum(y)] y [sum(x), sum(x^2) | sum(xy)].",
    "Cuadratica": "g(x) = a0 + a1*x + a2*x^2\nSistema normal 3x3 con sumatorias hasta sum(x^4) y sum(x^2*y).",
    "Cubica": "g(x) = a0 + a1*x + a2*x^2 + a3*x^3\nSistema normal 4x4 con sumatorias hasta sum(x^6) y sum(x^3*y).",
    "Lineal con Funcion": "g(x) = a0 + a1*x + a2*phi(x)  (phi: sen, cos, exp, ln, tan)\nSistema normal 3x3 con columnas 1, x, phi(x).",
    "Cuadratica con Funcion": "g(x) = a0 + a1*x + a2*x^2 + a3*phi(x)\nSistema normal 4x4 con columnas 1, x, x^2, phi(x).",
    "Regla Trapezoidal": "h = (b - a) / n\nI = (h/2) * [f(a) + 2*sum_{i=1..n-1} f(a+ih) + f(b)]",
    "Regla de 1/3 de Simpson": "n siempre par, h = (b - a) / n\nI = (h/3) * [f(a) + 4*sum_impares + 2*sum_pares + f(b)]",
    "Regla de 3/8 de Simpson": "n multiplo de 3, h = (b - a) / n\nI = (3h/8) * [f(x0) + 3*f(x1) + 3*f(x2) + f(x3)]",
    "Newton – Cotes Abiertas": "h = (b - a) / (n + 2),  x_i = a + i*h  (i = 0..n+2)\nI = alpha_n * h * sum c_i * f(x_i)  (extremos con peso 0).",
    "Newton - Cotes Cerradas": "h = (b - a) / n,  x_i = a + i*h  (i = 0..n)\nI = alpha_n * h * sum_{i=0..n} c_i * f(x_i)",
    "Euler Modificado": "Despejar y' = f(y, t),  t_{n+1} = t_n + h\ny'_{n+1} = y_n + (h/2) * [f(y_n, t_n) + f(y_{n+1}, t_{n+1})]",
    "Runge - Kutta 2ndo Orden": "k1 = h * f(yn, tn)\nk2 = h * f(yn + k1, tn + h),   y_{n+1} = yn + 0.5*(k1 + k2)",
    "Runge - Kutta 3er Orden": "k1 = h*f(yn,tn), k2 = h*f(yn+k1/2, tn+h/2), k3 = h*f(yn-k1+2k2, tn+h)\ny_{n+1} = yn + (1/6)*(k1 + 4*k2 + k3)",
    "Runge - Kutta 4rto Orden por 1/3 de Simpson": "k1=h*f(yn,tn), k2=h*f(yn+k1/2,tn+h/2), k3=h*f(yn+k2/2,tn+h/2), k4=h*f(yn+k3,tn+h)\ny_{n+1} = yn + (1/6)*(k1 + 2*k2 + 2*k3 + k4)",
    "Runge - Kutta 4rto Orden por 3/8 de Simpson": "k1=h*f(yn,tn), k2=h*f(yn+k1/3,tn+h/3), k3=h*f(yn+k1/3+k2/3,tn+2h/3), k4=h*f(yn+k1-k2+k3,tn+h)\ny_{n+1} = yn + (1/8)*(k1 + 3*k2 + 3*k3 + k4)",
    "Runge - Kutta de Orden Superior": "V_n = y'_n, U_n = y_n, q_n = t_n\nk1=h*Vn, m1=h*g(Vn,Un,qn), k2=h*(Vn+m1), m2=h*g(Vn+m1,Un+k1,qn+h)",
}
