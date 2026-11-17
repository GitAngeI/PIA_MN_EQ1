import ast
import math
import operator
import tkinter as tk

from .tema import (
    AMBAR,
    BORDE_CALIDO,
    CORAL,
    CREMA,
    DORADO,
    ESMERALDA,
    FONDO_GALAXIA,
    FUENTE_MONO,
    GRIS_CALIDO,
    PANEL_ELEVADO,
    PANEL_OSCURO,
    ROJO_OXIGENO,
    obtener_paleta,
)


_OPS_BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_OPS_UNARIOS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _potencia_segura(base: float, exp: float) -> float:
    base_f = float(base)
    exp_f = float(exp)
    if base_f == 0.0 and exp_f < 0.0:
        raise ZeroDivisionError("Division por cero en potencia negativa")
    if base_f < 0.0 and not exp_f.is_integer():
        raise ValueError("Potencia fraccionaria de base negativa genera numero complejo")
    if abs(exp_f) > 500.0 and abs(base_f) > 1.0:
        raise ValueError("Exponente demasiado grande")
    if abs(base_f) > 1.0 and exp_f > 0.0:
        if exp_f * math.log10(abs(base_f)) > 300.0:
            raise OverflowError("Resultado fuera de rango numerico")
    res = base_f ** exp_f
    if isinstance(res, complex) or not math.isfinite(res):
        raise ValueError("Resultado no finito")
    return float(res)


def _expandir_factoriales(expr: str) -> str:
    """Convierte notacion postfija 'n!' y '(expr)!' en llamadas 'fact(...)'."""
    if "!" not in expr:
        return expr
    out: list[str] = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch != "!" or (i + 1 < n and expr[i + 1] == "="):
            out.append(ch)
            i += 1
            continue

        j = len(out) - 1
        while j >= 0 and out[j].isspace():
            j -= 1
        if j < 0:
            out.append(ch)
            i += 1
            continue

        if out[j] == ")":
            prof = 1
            k = j - 1
            while k >= 0 and prof > 0:
                if out[k] == ")":
                    prof += 1
                elif out[k] == "(":
                    prof -= 1
                k -= 1
            if prof != 0:
                out.append(ch)
                i += 1
                continue
            while k >= 0 and (out[k].isalnum() or out[k] == "_"):
                k -= 1
            inicio = k + 1
        elif out[j].isdigit() or out[j] == "." or out[j].isalpha() or out[j] == "_":
            k = j
            while k >= 0 and (out[k].isalnum() or out[k] in "._"):
                k -= 1
            inicio = k + 1
        else:
            out.append(ch)
            i += 1
            continue

        operando = "".join(out[inicio : j + 1])
        del out[inicio:]
        out.extend(list(f"fact({operando})"))
        i += 1
    return "".join(out)


def evaluar_expresion_segura(expr: str, ans: float = 0.0, modo_grados: bool = False) -> float:
    """Evalua una expresion matematica usando whitelist estricto sobre ast.parse."""
    if not isinstance(expr, str):
        raise ValueError("Expresion invalida")
    limpia = expr.strip()
    if not limpia:
        raise ValueError("Ingresa una expresion matematica")
    if len(limpia) > 300:
        raise ValueError("Expresion demasiado larga (maximo 300 caracteres)")

    normalizada = (
        limpia.replace("^", "**")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("–", "-")
        .replace("π", "pi")
    )
    normalizada = _expandir_factoriales(normalizada)

    try:
        arbol = ast.parse(normalizada, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Sintaxis matematica invalida") from exc

    constantes = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "ans": float(ans),
    }

    def _trig_sin(x: float) -> float:
        return math.sin(math.radians(x) if modo_grados else x)

    def _trig_cos(x: float) -> float:
        return math.cos(math.radians(x) if modo_grados else x)

    def _trig_tan(x: float) -> float:
        rad = math.radians(x) if modo_grados else x
        if abs(math.cos(rad)) < 1e-12:
            raise ValueError("Tangente indefinida en asintota")
        return math.tan(rad)

    def _trig_asin(x: float) -> float:
        if x < -1.0 or x > 1.0:
            raise ValueError("Dominio invalido para asin (requiere [-1, 1])")
        r = math.asin(x)
        return math.degrees(r) if modo_grados else r

    def _trig_acos(x: float) -> float:
        if x < -1.0 or x > 1.0:
            raise ValueError("Dominio invalido para acos (requiere [-1, 1])")
        r = math.acos(x)
        return math.degrees(r) if modo_grados else r

    def _trig_atan(x: float) -> float:
        r = math.atan(x)
        return math.degrees(r) if modo_grados else r

    def _trig_atan2(y: float, x: float) -> float:
        r = math.atan2(y, x)
        return math.degrees(r) if modo_grados else r

    def _ln(x: float) -> float:
        if x <= 0.0:
            raise ValueError("Dominio invalido para ln (requiere x > 0)")
        return math.log(x)

    def _log(x: float, base: float | None = None) -> float:
        if x <= 0.0:
            raise ValueError("Dominio invalido para log (requiere x > 0)")
        if base is None:
            return math.log10(x)
        if base <= 0.0 or base == 1.0:
            raise ValueError("Base invalida para logaritmo")
        return math.log(x, base)

    def _exp(x: float) -> float:
        if x > 700.0:
            raise OverflowError("Exponencial fuera de rango")
        return math.exp(x)

    def _sqrt(x: float) -> float:
        if x < 0.0:
            raise ValueError("Raiz cuadrada de numero negativo")
        return math.sqrt(x)

    def _factorial(x: float) -> float:
        if not math.isfinite(x):
            raise ValueError("Factorial requiere numero finito")
        if abs(x - round(x)) > 1e-9:
            raise ValueError("Factorial solo aplica a enteros no negativos")
        n = int(round(x))
        if n < 0:
            raise ValueError("Factorial requiere entero >= 0")
        if n > 170:
            raise OverflowError("Factorial maximo soportado: 170!")
        return float(math.factorial(n))

    funciones = {
        "sin": (_trig_sin, 1, 1),
        "sen": (_trig_sin, 1, 1),
        "cos": (_trig_cos, 1, 1),
        "tan": (_trig_tan, 1, 1),
        "asin": (_trig_asin, 1, 1),
        "asen": (_trig_asin, 1, 1),
        "acos": (_trig_acos, 1, 1),
        "atan": (_trig_atan, 1, 1),
        "atan2": (_trig_atan2, 2, 2),
        "sinh": (lambda x: math.sinh(x) if abs(x) <= 700 else _raise_overflow(), 1, 1),
        "cosh": (lambda x: math.cosh(x) if abs(x) <= 700 else _raise_overflow(), 1, 1),
        "tanh": (math.tanh, 1, 1),
        "ln": (_ln, 1, 1),
        "log": (_log, 1, 2),
        "log10": (lambda x: _log(x, 10.0), 1, 1),
        "exp": (_exp, 1, 1),
        "sqrt": (_sqrt, 1, 1),
        "raiz": (_sqrt, 1, 1),
        "fact": (_factorial, 1, 1),
        "factorial": (_factorial, 1, 1),
        "abs": (abs, 1, 1),
        "pow": (_potencia_segura, 2, 2),
        "round": (round, 1, 2),
        "min": (min, 1, 8),
        "max": (max, 1, 8),
    }

    def _evaluar_nodo(nodo: ast.AST) -> float:
        if isinstance(nodo, ast.Expression):
            return _evaluar_nodo(nodo.body)
        if isinstance(nodo, ast.Constant):
            if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
                raise ValueError("Solo se permiten constantes numericas reales")
            val = float(nodo.value)
            if not math.isfinite(val):
                raise ValueError("Constante no finita")
            return val
        if isinstance(nodo, ast.Name):
            if not isinstance(nodo.ctx, ast.Load):
                raise ValueError("Contexto de nombre no permitido")
            clave = nodo.id.lower()
            if clave not in constantes:
                raise ValueError(f"Identificador no permitido: {nodo.id}")
            return float(constantes[clave])
        if isinstance(nodo, ast.UnaryOp):
            op_fn = _OPS_UNARIOS.get(type(nodo.op))
            if op_fn is None:
                raise ValueError("Operador unario no permitido")
            return float(op_fn(_evaluar_nodo(nodo.operand)))
        if isinstance(nodo, ast.BinOp):
            izq = _evaluar_nodo(nodo.left)
            der = _evaluar_nodo(nodo.right)
            if isinstance(nodo.op, ast.Pow):
                return _potencia_segura(izq, der)
            op_fn = _OPS_BINARIOS.get(type(nodo.op))
            if op_fn is None:
                raise ValueError("Operador binario no permitido")
            if isinstance(nodo.op, (ast.Div, ast.FloorDiv, ast.Mod)) and der == 0.0:
                raise ZeroDivisionError("Division por cero")
            res = float(op_fn(izq, der))
            if not math.isfinite(res):
                raise ValueError("Resultado no finito")
            return res
        if isinstance(nodo, ast.Call):
            if nodo.keywords:
                raise ValueError("No se permiten argumentos con nombre")
            if not isinstance(nodo.func, ast.Name):
                raise ValueError("Solo se permiten funciones matematicas directas")
            clave_fn = nodo.func.id.lower()
            if clave_fn not in funciones:
                raise ValueError(f"Funcion no permitida: {nodo.func.id}")
            fn, min_args, max_args = funciones[clave_fn]
            n_args = len(nodo.args)
            if n_args < min_args or n_args > max_args:
                raise ValueError(f"Cantidad de argumentos invalida para {clave_fn}()")
            args_eval = [_evaluar_nodo(a) for a in nodo.args]
            res = float(fn(*args_eval))
            if not math.isfinite(res):
                raise ValueError("Resultado no finito")
            return res
        raise ValueError(f"Construccion no permitida: {type(nodo).__name__}")

    resultado = _evaluar_nodo(arbol)
    if not math.isfinite(resultado):
        raise ValueError("Resultado no finito")
    return resultado


def _raise_overflow() -> float:
    raise OverflowError("Valor hiperbolico fuera de rango")


def formatear_numero(valor: float) -> str:
    if abs(valor) < 1e-12:
        valor = 0.0
    texto = f"{valor:.10g}"
    return texto


class CalculadoraCientifica(tk.Frame):
    """Calculadora cientifica embebida dentro de ConsolaMision (no roba foco a otro TopLevel)."""

    def __init__(
        self,
        master,
        al_enviar_resultado=None,
        bg=None,
        acento=None,
        permitir_clipboard=True,
    ):
        pal = obtener_paleta()
        bg_eff = bg if bg is not None else pal["panel"]
        acento_eff = acento if acento is not None else pal["acento"]
        super().__init__(
            master,
            bg=bg_eff,
            highlightbackground=pal["borde"],
            highlightthickness=1,
            padx=6,
            pady=5,
        )
        self.al_enviar_resultado = al_enviar_resultado
        self.acento = acento_eff
        self._bg_manual = bg
        self._acento_manual = acento
        self.permitir_clipboard = bool(permitir_clipboard)
        self.modo_grados = False
        self.ans = 0.0
        self.ultimo_valor_str = ""
        self._grids = []
        self._botones_tecla = []

        self.encabezado = tk.Frame(self, bg=bg_eff)
        self.encabezado.pack(fill=tk.X, pady=(0, 3))
        self.lbl_calc_titulo = tk.Label(
            self.encabezado,
            text="CALCULADORA CIENTIFICA",
            font=("Consolas", 10, "bold"),
            fg=acento_eff,
            bg=bg_eff,
        )
        self.lbl_calc_titulo.pack(side=tk.LEFT)

        self.btn_modo_ang = tk.Button(
            self.encabezado,
            text="RAD",
            font=("Consolas", 9, "bold"),
            fg=pal["texto_en_acento"],
            bg=pal["titulo"],
            activebackground=acento_eff,
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self._alternar_angulo,
        )
        self.btn_modo_ang.pack(side=tk.RIGHT)

        self.lbl_ans = tk.Label(
            self.encabezado,
            text="ANS = 0",
            font=(FUENTE_MONO, 9),
            fg=pal["texto_sec"],
            bg=bg_eff,
        )
        self.lbl_ans.pack(side=tk.RIGHT, padx=(0, 8))

        self.visor = tk.Frame(
            self,
            bg=pal["superficie"],
            highlightbackground=pal["borde"],
            highlightthickness=1,
            padx=6,
            pady=3,
        )
        self.visor.pack(fill=tk.X, pady=(0, 3))

        self.entry_expr = tk.Entry(
            self.visor,
            font=("Consolas", 11),
            bg=pal["superficie"],
            fg=pal["texto"],
            insertbackground=acento_eff,
            bd=0,
            justify=tk.RIGHT,
        )
        self.entry_expr.pack(fill=tk.X)
        self.entry_expr.bind("<Return>", lambda e: self.calcular())

        if not self.permitir_clipboard:
            self.establecer_clipboard_bloqueado(True)

        self.lbl_resultado = tk.Label(
            self.visor,
            text="= 0",
            font=("Consolas", 11, "bold"),
            fg=pal["exito"],
            bg=pal["superficie"],
            anchor="e",
        )
        self.lbl_resultado.pack(fill=tk.X, pady=(2, 0))

        self.lbl_error = tk.Label(
            self,
            text="",
            font=("Consolas", 8),
            fg=pal["peligro"],
            bg=bg_eff,
            anchor="w",
            wraplength=340,
            justify=tk.LEFT,
        )
        self.lbl_error.pack(fill=tk.X, pady=(0, 2))

        estilos = pal["calc_estilos"]

        teclas_sci = [
            [
                ("sin", "sin(", "fn"),
                ("cos", "cos(", "fn"),
                ("tan", "tan(", "fn"),
                ("ln", "ln(", "fn"),
                ("log", "log(", "fn"),
                ("exp", "exp(", "fn"),
                ("n!", "!", "op"),
            ],
            [
                ("asin", "asin(", "fn"),
                ("acos", "acos(", "fn"),
                ("atan", "atan(", "fn"),
                ("sqrt", "sqrt(", "fn"),
                ("abs", "abs(", "fn"),
                ("(", "(", "op"),
                (")", ")", "op"),
            ],
        ]

        teclas_num = [
            [
                ("7", "7", "num"),
                ("8", "8", "num"),
                ("9", "9", "num"),
                ("/", "/", "op"),
                ("^", "^", "op"),
                ("DEL", None, "ctrl"),
            ],
            [
                ("4", "4", "num"),
                ("5", "5", "num"),
                ("6", "6", "num"),
                ("*", "*", "op"),
                ("pi", "pi", "const"),
                ("AC", None, "ctrl_danger"),
            ],
            [
                ("1", "1", "num"),
                ("2", "2", "num"),
                ("3", "3", "num"),
                ("-", "-", "op"),
                ("e", "e", "const"),
                ("ANS", "ans", "const"),
            ],
            [
                ("0", "0", "num"),
                (".", ".", "num"),
                ("x^3", "^3", "op"),
                ("+", "+", "op"),
                ("x^2", "^2", "op"),
                ("=", None, "eq"),
            ],
        ]

        self._poblar_cuadricula(bg_eff, 7, teclas_sci, estilos, expand=False, pady_grid=(0, 2))
        self._poblar_cuadricula(bg_eff, 6, teclas_num, estilos, expand=True)

        self.barra_acciones = tk.Frame(self, bg=bg_eff)
        self.barra_acciones.pack(fill=tk.X, pady=(4, 0))

        self.btn_calcular = tk.Button(
            self.barra_acciones,
            text="CALCULAR (=)",
            font=("Consolas", 9, "bold"),
            bg=pal["exito"],
            fg=pal["texto_en_exito"],
            activebackground=pal["calc_act_exito"],
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.calcular,
        )
        self.btn_calcular.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_enviar = tk.Button(
            self.barra_acciones,
            text="ENVIAR A RESPUESTA ->",
            font=("Consolas", 9, "bold"),
            bg=pal["titulo"],
            fg=pal["texto_en_acento"],
            activebackground=acento_eff,
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._enviar_actual,
        )
        self.btn_enviar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    def _poblar_cuadricula(self, bg: str, cols: int, filas, estilos: dict, expand: bool = True, pady_grid=0) -> None:
        grid = tk.Frame(self, bg=bg)
        grid.pack(fill=tk.BOTH, expand=expand, pady=pady_grid)
        self._grids.append(grid)
        for c in range(cols):
            grid.columnconfigure(c, weight=1)
        for r_idx, fila in enumerate(filas):
            grid.rowconfigure(r_idx, weight=1)
            for c_idx, (etiqueta, token, tipo) in enumerate(fila):
                bg_b, fg_b, act_b = estilos[tipo]
                if etiqueta == "DEL":
                    cmd = self._borrar_uno
                elif etiqueta == "AC":
                    cmd = self._limpiar_todo
                elif etiqueta == "=":
                    cmd = self.calcular
                else:
                    cmd = lambda t=token: self._insertar(t)

                b = tk.Button(
                    grid,
                    text=etiqueta,
                    font=("Consolas", 9, "bold"),
                    bg=bg_b,
                    fg=fg_b,
                    activebackground=act_b,
                    activeforeground=fg_b,
                    bd=0,
                    pady=3,
                    cursor="hand2",
                    command=cmd,
                )
                b.grid(row=r_idx, column=c_idx, sticky="nsew", padx=1, pady=1)
                self._botones_tecla.append((b, tipo))

    def aplicar_tema(self, bg=None, acento=None) -> None:
        pal = obtener_paleta()
        bg_eff = bg if bg is not None else pal["calc_bg"]
        acento_eff = acento if acento is not None else pal["acento"]
        self.acento = acento_eff
        self.configure(bg=bg_eff, highlightbackground=pal["borde"])
        self.encabezado.configure(bg=bg_eff)
        self.lbl_calc_titulo.configure(bg=bg_eff, fg=acento_eff)
        self.lbl_ans.configure(bg=bg_eff, fg=pal["texto_sec"])
        self.btn_modo_ang.configure(
            fg=pal["texto_en_acento"],
            bg=pal["alerta"] if self.modo_grados else pal["titulo"],
            activebackground=acento_eff,
        )
        self.visor.configure(bg=pal["superficie"], highlightbackground=pal["borde"])
        self.entry_expr.configure(bg=pal["superficie"], fg=pal["texto"], insertbackground=acento_eff)
        es_err = self.lbl_resultado.cget("text") == "= ERROR"
        self.lbl_resultado.configure(bg=pal["superficie"], fg=pal["peligro"] if es_err else pal["exito"])
        self.lbl_error.configure(bg=bg_eff, fg=pal["peligro"])
        for g in self._grids:
            g.configure(bg=bg_eff)
        estilos = pal["calc_estilos"]
        for btn, tipo in self._botones_tecla:
            bg_b, fg_b, act_b = estilos[tipo]
            btn.configure(bg=bg_b, fg=fg_b, activebackground=act_b, activeforeground=fg_b)
        self.barra_acciones.configure(bg=bg_eff)
        self.btn_calcular.configure(bg=pal["exito"], fg=pal["texto_en_exito"], activebackground=pal["calc_act_exito"])
        self.btn_enviar.configure(bg=pal["titulo"], fg=pal["texto_en_acento"], activebackground=acento_eff)

    def establecer_clipboard_bloqueado(self, bloqueado: bool) -> None:
        self.permitir_clipboard = not bloqueado
        for ev in (
            "<<Copy>>",
            "<<Paste>>",
            "<<Cut>>",
            "<Control-c>",
            "<Control-C>",
            "<Control-v>",
            "<Control-V>",
            "<Control-x>",
            "<Control-X>",
            "<Control-Insert>",
            "<Shift-Insert>",
            "<Button-3>",
        ):
            if bloqueado:
                self.entry_expr.bind(ev, lambda e: "break")
            else:
                self.entry_expr.unbind(ev)

    def _alternar_angulo(self) -> None:
        pal = obtener_paleta()
        self.modo_grados = not self.modo_grados
        self.btn_modo_ang.config(
            text="DEG" if self.modo_grados else "RAD",
            bg=pal["alerta"] if self.modo_grados else pal["titulo"],
            fg=pal["texto_en_acento"],
        )
        if self.entry_expr.get().strip():
            self.calcular()

    def _insertar(self, token: str) -> None:
        self.lbl_error.config(text="")
        pos = self.entry_expr.index(tk.INSERT)
        self.entry_expr.insert(pos, token)
        self.entry_expr.focus_set()

    def _borrar_uno(self) -> None:
        self.lbl_error.config(text="")
        pos = self.entry_expr.index(tk.INSERT)
        if pos > 0:
            self.entry_expr.delete(pos - 1, pos)
        self.entry_expr.focus_set()

    def _limpiar_todo(self) -> None:
        pal = obtener_paleta()
        self.entry_expr.delete(0, tk.END)
        self.lbl_resultado.config(text="= 0", fg=pal["exito"])
        self.lbl_error.config(text="")
        self.ultimo_valor_str = ""
        self.entry_expr.focus_set()

    def limpiar(self) -> None:
        pal = obtener_paleta()
        self.entry_expr.delete(0, tk.END)
        self.ans = 0.0
        self.ultimo_valor_str = ""
        self.lbl_ans.config(text="ANS = 0")
        self.lbl_resultado.config(text="= 0", fg=pal["exito"])
        self.lbl_error.config(text="")

    def calcular(self):
        pal = obtener_paleta()
        expr = self.entry_expr.get()
        try:
            res = evaluar_expresion_segura(expr, ans=self.ans, modo_grados=self.modo_grados)
        except Exception as exc:
            self.lbl_resultado.config(text="= ERROR", fg=pal["peligro"])
            self.lbl_error.config(text=str(exc))
            return None

        self.ans = res
        txt = formatear_numero(res)
        self.ultimo_valor_str = txt
        self.lbl_ans.config(text=f"ANS = {txt}")
        self.lbl_resultado.config(text=f"= {txt}", fg=pal["exito"])
        self.lbl_error.config(text="")
        return res

    def _enviar_actual(self) -> None:
        if self.entry_expr.get().strip():
            res = self.calcular()
            if res is None:
                return
        elif not self.ultimo_valor_str:
            self.ultimo_valor_str = formatear_numero(self.ans)

        if self.al_enviar_resultado and self.ultimo_valor_str:
            self.al_enviar_resultado(self.ultimo_valor_str)
