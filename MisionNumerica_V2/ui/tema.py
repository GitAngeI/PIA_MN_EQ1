"""Paleta dual (Oscuro espacial / Claro blanco-gris suave), tipografía grande (>= 16 pt) y catálogo oficial (0% emojis)."""

from typing import Any, Dict, List, Optional, Tuple

# Paleta espacial cálida (índigo-violeta profundo + ámbar + coral + crema) — valores base Oscuro
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

SALAS_ACENTO_OSCURO: Dict[int, str] = {
    1: DORADO,
    2: AMBAR,
    3: CORAL,
    4: ESMERALDA,
    5: VIOLETA_SUAVE,
    6: "#FF7B89",
    7: "#7CE0D3",
}

SALAS_ACENTO_CLARO: Dict[int, str] = {
    1: "#9A5B00",
    2: "#C25E00",
    3: "#C84B31",
    4: "#0D7A5F",
    5: "#6D3FC0",
    6: "#BE2B45",
    7: "#0E7490",
}

PALETAS_TEMA: Dict[str, Dict[str, Any]] = {
    "oscuro": {
        "nombre": "oscuro",
        "fondo": FONDO_GALAXIA,
        "panel": PANEL_OSCURO,
        "panel_elevado": PANEL_ELEVADO,
        "superficie": "#120E20",
        "superficie_alt": "#16112B",
        "superficie_prog": "#100D1E",
        "superficie_barra": "#100C1C",
        "overlay": "#0B0816",
        "overlay_hud": "#0D0A18",
        "overlay_foco": "#090611",
        "tooltip_bg": "#0D0A1A",
        "tooltip_fg": DORADO,
        "borde": BORDE_CALIDO,
        "texto": CREMA,
        "texto_sec": GRIS_CALIDO,
        "titulo": DORADO,
        "acento": AMBAR,
        "exito": ESMERALDA,
        "peligro": ROJO_OXIGENO,
        "alerta": CORAL,
        "violeta": VIOLETA_SUAVE,
        "texto_en_acento": "#160F24",
        "texto_en_exito": FONDO_GALAXIA,
        "texto_en_peligro": CREMA,
        "sombra_acento": "#8C4E22",
        "sombra_panel": "#120E20",
        "sombra_peligro": "#5A1525",
        "sombra_modal": "#2D1E42",
        "btn_sec_exp_bg": "#1E2B3D",
        "btn_sec_exp_fg": CREMA,
        "btn_sec_reset_bg": "#4A1A28",
        "btn_sec_reset_fg": CREMA,
        "btn_guia_bg": "#262044",
        "btn_guia_fg": DORADO,
        "estrella_llena": DORADO,
        "estrella_borde": AMBAR,
        "estrella_vacia_fill": "#261F3C",
        "estrella_vacia_borde": "#5B4D80",
        "visor_bg": "#0F0B1B",
        "visor_borde": "#3B2E58",
        "visor_grid": "#1B1530",
        "visor_tick": "#6C5B99",
        "visor_marco": "#584780",
        "visor_eje": "#7E6BB3",
        "visor_eje_sys": "#8D79C7",
        "visor_trap_fill": "#1C4D3E",
        "visor_trap_wait": "#282046",
        "visor_trap_borde": "#4DA688",
        "calc_bg": "#161129",
        "calc_act_exito": "#7CF0B8",
        "calc_estilos": {
            "num": ("#2C234B", CREMA, "#3B2F63"),
            "op": ("#241B3E", DORADO, "#342859"),
            "fn": ("#1C1533", GRIS_CALIDO, "#2D234D"),
            "const": ("#20183B", AMBAR, "#32265A"),
            "ctrl": ("#3D253B", CREMA, "#543250"),
            "ctrl_danger": ("#592234", CREMA, "#7A2D46"),
            "eq": (ESMERALDA, FONDO_GALAXIA, "#7CF0B8"),
        },
        "salas_acento": SALAS_ACENTO_OSCURO,
        "mapa_bg": "#090714",
        "mapa_neb1": "#141028",
        "mapa_neb2": "#11162B",
        "mapa_estrellas": ("#FFFFFF", "#E9DFFF", "#FFE5B4", "#B8F2FF", "#9F8EC2"),
        "mapa_aleta": "#241C3D",
        "mapa_casco_fill": "#2A2246",
        "mapa_casco_borde": "#735E9E",
        "mapa_cubierta_fill": "#17122B",
        "mapa_rejilla": "#201938",
        "mapa_visera_fill": "#4EE2EC",
        "mapa_visera_borde": "#B5FCFF",
        "mapa_tobera_fill": "#2E264C",
        "mapa_tobera_borde": "#8672B2",
        "mapa_tobera_core": "#63F2EC",
        "mapa_tobera_core_borde": "#D6FFFF",
        "mapa_llama_ext": "#2AB7CA",
        "mapa_llama_int": "#B9FFF8",
        "mapa_pasillo_ext": "#4A3B70",
        "mapa_pasillo_int": "#241D3D",
        "mapa_pasillo_luz": "#6C5A99",
        "mapa_sala_fill": "#18132C",
        "mapa_sala_ok_fill": "#142426",
        "mapa_sala_borde_idle": "#5A4B7C",
        "mapa_sala_head": "#241C3D",
        "mapa_sala_head_ok": "#1B3330",
        "mapa_sala_foot": "#110D1F",
        "mapa_texto_activo": "#130F21",
        "badge_idle_bg": "#1F1835",
        "badge_ok_bg": "#132A26",
        "mapa_interior_1": "#1E3654",
        "mapa_interior_1_arc": "#4CE8E0",
        "mapa_interior_2": "#3B1D1B",
        "mapa_interior_3": "#221D3A",
        "mapa_interior_4": "#113831",
        "mapa_interior_5": "#261A42",
        "mapa_interior_6": "#2A1429",
        "mapa_interior_6_ring": "#8A4B63",
        "mapa_interior_7a": "#14293D",
        "mapa_interior_7b": "#1B4D5C",
        "mapa_nodo_inactivo": "#282040",
        "galaxia_neb": ("#2A193D", "#331D38", "#2B1E3E", "#3B2135"),
        "galaxia_est": ("#FFF5E4", DORADO, AMBAR, CORAL, VIOLETA_SUAVE),
        "btn_tema_txt": "TEMA CLARO",
        "btn_tema_bg": "#E6EBF3",
        "btn_tema_fg": "#1E2433",
    },
    "claro": {
        "nombre": "claro",
        "fondo": "#ECEFF4",           # Gris suave aperlado
        "panel": "#F7F8FA",           # Blanco suave principal
        "panel_elevado": "#E1E6EF",   # Gris suave para botones e inactivos
        "superficie": "#FFFFFF",      # Blanco limpio para cajas internas y tablas
        "superficie_alt": "#EFF2F7",  # Gris muy suave para enunciado y calculadora
        "superficie_prog": "#F9FAFC", # Blanco suave bitacora progresiva
        "superficie_barra": "#DCE2EC",
        "overlay": "#CBD2DF",
        "overlay_hud": "#D2D9E5",
        "overlay_foco": "#C7CFDD",
        "tooltip_bg": "#FAFBFD",
        "tooltip_fg": "#1E2433",
        "borde": "#B8C2D3",
        "texto": "#1E2433",           # Tinta pizarra oscura de alto contraste
        "texto_sec": "#4A5568",       # Gris pizarra medio
        "titulo": "#9A5B00",          # Dorado/ambar profundo legible en blanco
        "acento": "#C25E00",          # Naranja calido intenso
        "exito": "#0D7A5F",           # Esmeralda profundo legible
        "peligro": "#C81E3A",         # Carmesi legible
        "alerta": "#C84B31",          # Coral intenso legible
        "violeta": "#6D3FC0",         # Violeta profundo legible
        "texto_en_acento": "#FFFFFF",
        "texto_en_exito": "#FFFFFF",
        "texto_en_peligro": "#FFFFFF",
        "sombra_acento": "#8F4400",
        "sombra_panel": "#B4BFD1",
        "sombra_peligro": "#881327",
        "sombra_modal": "#9AA6BA",
        "btn_sec_exp_bg": "#DCE5F2",
        "btn_sec_exp_fg": "#1E2433",
        "btn_sec_reset_bg": "#FBE4E8",
        "btn_sec_reset_fg": "#9F1239",
        "btn_guia_bg": "#ECE6FA",
        "btn_guia_fg": "#5B21B6",
        "estrella_llena": "#EAB308",
        "estrella_borde": "#B45309",
        "estrella_vacia_fill": "#DCE2EC",
        "estrella_vacia_borde": "#94A3B8",
        "visor_bg": "#FAFBFD",
        "visor_borde": "#B8C2D3",
        "visor_grid": "#E6EAF2",
        "visor_tick": "#7E8BA3",
        "visor_marco": "#94A3B8",
        "visor_eje": "#64748B",
        "visor_eje_sys": "#64748B",
        "visor_trap_fill": "#BFE8DA",
        "visor_trap_wait": "#DFE5F0",
        "visor_trap_borde": "#0D7A5F",
        "calc_bg": "#EFF2F7",
        "calc_act_exito": "#0F9473",
        "calc_estilos": {
            "num": ("#FFFFFF", "#1E2433", "#E2E8F0"),
            "op": ("#E3E8F1", "#9A5B00", "#CFD7E6"),
            "fn": ("#EAEFF6", "#334155", "#D8DFE9"),
            "const": ("#EAE5F5", "#5B21B6", "#DDD6FE"),
            "ctrl": ("#F3E6DF", "#9A3412", "#E6D2C7"),
            "ctrl_danger": ("#FBE2E7", "#9F1239", "#F5C4CE"),
            "eq": ("#0D7A5F", "#FFFFFF", "#0F9473"),
        },
        "salas_acento": SALAS_ACENTO_CLARO,
        "mapa_bg": "#E7ECF4",
        "mapa_neb1": "#DCE3EE",
        "mapa_neb2": "#D7E0EC",
        "mapa_estrellas": ("#94A3B8", "#A3B1C6", "#C28A3A", "#5A8EA8", "#8B7CB3"),
        "mapa_aleta": "#CBD4E2",
        "mapa_casco_fill": "#D7DFEB",
        "mapa_casco_borde": "#64748B",
        "mapa_cubierta_fill": "#F3F5F9",
        "mapa_rejilla": "#E2E7F0",
        "mapa_visera_fill": "#0EA5E9",
        "mapa_visera_borde": "#0369A1",
        "mapa_tobera_fill": "#C7D0DF",
        "mapa_tobera_borde": "#64748B",
        "mapa_tobera_core": "#06B6D4",
        "mapa_tobera_core_borde": "#0E7490",
        "mapa_llama_ext": "#0284C7",
        "mapa_llama_int": "#BAE6FD",
        "mapa_pasillo_ext": "#94A3B8",
        "mapa_pasillo_int": "#E4E9F2",
        "mapa_pasillo_luz": "#64748B",
        "mapa_sala_fill": "#FAFBFE",
        "mapa_sala_ok_fill": "#E4F4EE",
        "mapa_sala_borde_idle": "#9BA7BC",
        "mapa_sala_head": "#E4E9F2",
        "mapa_sala_head_ok": "#D5EDE4",
        "mapa_sala_foot": "#E6EBF3",
        "mapa_texto_activo": "#FFFFFF",
        "badge_idle_bg": "#E6EBF3",
        "badge_ok_bg": "#DCF2EA",
        "mapa_interior_1": "#D6E8F8",
        "mapa_interior_1_arc": "#0284C7",
        "mapa_interior_2": "#F8E0DA",
        "mapa_interior_3": "#E6E2F3",
        "mapa_interior_4": "#D7F0E8",
        "mapa_interior_5": "#EAE2F8",
        "mapa_interior_6": "#F9E1E6",
        "mapa_interior_6_ring": "#C86B82",
        "mapa_interior_7a": "#DCEAF6",
        "mapa_interior_7b": "#D3EEF2",
        "mapa_nodo_inactivo": "#DCE2EC",
        "galaxia_neb": ("#DCE3EE", "#E2DFEB", "#DDE4EE", "#E6DFE8"),
        "galaxia_est": ("#94A3B8", "#9A5B00", "#C25E00", "#C84B31", "#6D3FC0"),
        "btn_tema_txt": "TEMA OSCURO",
        "btn_tema_bg": "#271F42",
        "btn_tema_fg": "#FAF3E8",
    },
}

_TEMA_ACTUAL = "oscuro"


def obtener_tema_actual() -> str:
    return _TEMA_ACTUAL


def establecer_tema_actual(tema: Optional[str] = None) -> str:
    global _TEMA_ACTUAL
    _TEMA_ACTUAL = "claro" if str(tema or "").strip().lower() == "claro" else "oscuro"
    return _TEMA_ACTUAL


def alternar_tema_actual() -> str:
    return establecer_tema_actual("claro" if _TEMA_ACTUAL == "oscuro" else "oscuro")


def obtener_paleta(tema: Optional[str] = None) -> Dict[str, Any]:
    clave = _TEMA_ACTUAL if tema is None else ("claro" if str(tema).strip().lower() == "claro" else "oscuro")
    return PALETAS_TEMA[clave]


def obtener_color_sala(sala_id: int, tema: Optional[str] = None) -> str:
    pal = obtener_paleta(tema)
    return str(pal["salas_acento"].get(sala_id, pal["titulo"]))


def obtener_salas(tema: Optional[str] = None) -> List[Tuple[int, str, str, List[str]]]:
    pal = obtener_paleta(tema)
    mapa_cols = pal["salas_acento"]
    return [(sid, nom, mapa_cols.get(sid, col), mets) for sid, nom, col, mets in SALAS]

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


def crear_boton_3d(
    parent,
    texto,
    comando,
    bg=AMBAR,
    fg="#160F24",
    sombra="#7A4922",
    fuente=F_CUERPO_BOLD,
    padx=20,
    pady=10,
    activebackground=None,
    activeforeground=None,
):
    """Botón con base/sombra 3D para dar volumen físico al HUD."""
    import tkinter as tk
    pal = obtener_paleta()
    act_bg = activebackground if activebackground is not None else pal["titulo"]
    act_fg = activeforeground if activeforeground is not None else pal["texto_en_acento"]
    contenedor = tk.Frame(parent, bg=sombra, bd=0)
    btn = tk.Button(
        contenedor, text=texto, command=comando,
        bg=bg, fg=fg, activebackground=act_bg, activeforeground=act_fg,
        font=fuente, bd=0, relief="raised", padx=padx, pady=pady, cursor="hand2",
    )
    btn.pack(padx=(0, 0), pady=(0, 4))

    def _press(_e):
        btn.pack_configure(pady=(2, 2))

    def _release(_e):
        btn.pack_configure(pady=(0, 4))

    def _actualizar_colores(nuevo_bg, nuevo_fg, nueva_sombra, act_b=None, act_f=None):
        p = obtener_paleta()
        contenedor.configure(bg=nueva_sombra)
        btn.configure(
            bg=nuevo_bg,
            fg=nuevo_fg,
            activebackground=act_b if act_b is not None else p["titulo"],
            activeforeground=act_f if act_f is not None else p["texto_en_acento"],
        )

    btn.bind("<ButtonPress-1>", _press)
    btn.bind("<ButtonRelease-1>", _release)
    contenedor.boton = btn
    contenedor.actualizar_colores = _actualizar_colores
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
    "Lineal con Funcion": "g(x) = a0 + a1*x + a2*f(x)  (f: sen, cos, exp, ln, tan)\nSistema normal 3x3 con columnas 1, x, f(x).",
    "Cuadratica con Funcion": "g(x) = a0 + a1*x + a2*x^2 + a3*f(x)\nSistema normal 4x4 con columnas 1, x, x^2, f(x).",
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
