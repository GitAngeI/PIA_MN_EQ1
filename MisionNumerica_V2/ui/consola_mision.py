"""Consola interactiva paso a paso con Modo Examen, calculadora embebida, tablas progresivas y visor real."""

import math
import time
import tkinter as tk
from typing import Any, Callable, Dict, Optional

from ..juego.estado import EstadoJuego, calcular_estrellas
from ..metodos.generadores import generar_mision
from .calculadora import CalculadoraCientifica
from .escenarios import obtener_escenario
from .estrellas import EstrellasCanvas
from .formulas_latex import LATEX_METODOS, renderizar_formula_tk
from .tema import (
    AMBAR,
    BORDE_CALIDO,
    CORAL,
    CREMA,
    DORADO,
    ESMERALDA,
    FONDO_GALAXIA,
    FUENTE_MONO,
    F_CUERPO,
    F_CUERPO_BOLD,
    F_FORMULA,
    F_SUBTITULO,
    F_TABLA,
    F_TITULO,
    GRIS_CALIDO,
    PANEL_ELEVADO,
    PANEL_OSCURO,
    ROJO_OXIGENO,
    crear_boton_3d,
)
from .visor_grafica import VisorGraficaHUD


class ConsolaMision(tk.Frame):
    """Pantalla donde el alumno resuelve paso a paso un problema de libro parametrizado."""

    def __init__(
        self,
        master,
        nombre_metodo: str,
        estado: EstadoJuego,
        al_volver: Callable[[], None],
    ):
        super().__init__(master, bg=FONDO_GALAXIA)
        self.nombre_metodo = nombre_metodo
        self.estado = estado
        self.al_volver = al_volver

        self.mision: Dict[str, Any] = {}
        self.paso_idx = 0
        self.oxigeno_total = 180
        self.oxigeno_restante = 180.0
        self._penalizacion_seg = 0.0
        self.errores_intento = 0
        self.tiempo_inicio = 0.0
        self._after_id: Optional[str] = None
        self.activo = False
        self._verificando = False
        self._modal_overlay: Optional[tk.Frame] = None
        self._foto_formula = None

        # Pestañas y estado de UI / escalado responsivo
        self._tab_izq_actual = "datos"
        self._calc_visible = True
        self.opcion_var = tk.IntVar(value=-1)
        self._tam_enun = 13
        self._tam_tabla = 12
        self._tam_paso = 13
        self._tam_preg = 12
        self._tam_opc = 11
        self._tam_latex = 15
        self._ancho_izq_prev = 0
        self._ancho_der_prev = 0
        self._estado_scroll_der = (0, 0, 0)
        self._resize_izq_id: Optional[str] = None
        self._resize_der_id: Optional[str] = None
        self._scroll_idle_id: Optional[str] = None

        # Estado anti-fuga Modo Examen
        self._seguridad_activa = False
        self._micro_pausas_intento = 0
        self._foco_perdido = False
        self._breach_confirmado = False
        self._instante_salida = 0.0
        self._foco_after_id: Optional[str] = None
        self._gracia_after_id: Optional[str] = None
        self._focus_in_after_id: Optional[str] = None
        self._cortina_overlay: Optional[tk.Frame] = None
        self._lbl_cortina_titulo: Optional[tk.Label] = None
        self._lbl_cortina_msg: Optional[tk.Label] = None
        self._btn_cortina_accion: Optional[tk.Frame] = None
        self._top_binds: list[tuple[Any, str, str]] = []
        self._widgets_bloqueados_clip: list[tk.Widget] = []

        self.bind("<Destroy>", lambda _e: self._al_destruir(), add="+")
        self._construir_ui()
        self.nueva_mision_aleatoria(permitir_en_examen=True)

    # ------------------------------------------------------------------
    # CONSTRUCCION DE INTERFAZ (1100x720)
    # ------------------------------------------------------------------

    def _construir_ui(self) -> None:
        self.top = tk.Frame(self, bg=PANEL_OSCURO, highlightbackground=BORDE_CALIDO, highlightthickness=2)
        self.top.pack(fill="x", padx=16, pady=(6, 4))

        self.btn_volver = tk.Button(
            self.top,
            text="VOLVER",
            command=self._salir,
            bg=PANEL_ELEVADO,
            fg=CREMA,
            font=(FUENTE_MONO, 9, "bold"),
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
        )
        self.btn_volver.pack(side="left", padx=(8, 6), pady=4)

        self.lbl_titulo = tk.Label(
            self.top,
            text=self.nombre_metodo.upper(),
            bg=PANEL_OSCURO,
            fg=DORADO,
            font=("Segoe UI", 12, "bold"),
        )
        self.lbl_titulo.pack(side="left", padx=(4, 8))

        self.lbl_modo_badge = tk.Label(
            self.top,
            text="PRACTICA",
            bg=ESMERALDA,
            fg=FONDO_GALAXIA,
            font=(FUENTE_MONO, 9, "bold"),
            padx=8,
            pady=2,
        )
        self.lbl_modo_badge.pack(side="left", padx=4)

        self.lbl_record = tk.Label(self.top, text="", bg=PANEL_OSCURO, fg=ESMERALDA, font=(FUENTE_MONO, 9, "bold"))
        self.lbl_record.pack(side="right", padx=(6, 12))

        est_box = tk.Frame(self.top, bg=PANEL_OSCURO)
        est_box.pack(side="right", padx=6)
        self.visor_estrellas = EstrellasCanvas(est_box, valor=3.0, maximo=3, radio=9, espaciado=22, bg=PANEL_OSCURO)
        self.visor_estrellas.pack(side="left")
        self.lbl_estrellas_intento = tk.Label(
            est_box, text="3.0/3.0", bg=PANEL_OSCURO, fg=DORADO, font=(FUENTE_MONO, 9, "bold"), padx=4
        )
        self.lbl_estrellas_intento.pack(side="left")

        # Barra de oxigeno
        self.ox_frame = tk.Frame(self, bg=PANEL_OSCURO, highlightbackground=BORDE_CALIDO, highlightthickness=1)
        self.ox_frame.pack(fill="x", padx=16, pady=(0, 4))

        self.lbl_oxigeno = tk.Label(
            self.ox_frame, text="OXIGENO: 180 s", bg=PANEL_OSCURO, fg=AMBAR, font=(FUENTE_MONO, 9, "bold"), width=18, anchor="w"
        )
        self.lbl_oxigeno.pack(side="left", padx=10, pady=3)

        self.canvas_ox = tk.Canvas(self.ox_frame, height=14, bg="#100C1C", highlightthickness=0)
        self.canvas_ox.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=3)

        # Cuerpo principal: 2 columnas proporcionales en cualquier resolucion
        self.cuerpo = tk.Frame(self, bg=FONDO_GALAXIA)
        self.cuerpo.pack(fill="both", expand=True, padx=14, pady=(0, 6))
        self.cuerpo.columnconfigure(0, weight=54, uniform="col_mision")
        self.cuerpo.columnconfigure(1, weight=46, uniform="col_mision")
        self.cuerpo.rowconfigure(0, weight=1)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

    def _construir_panel_izquierdo(self) -> None:
        self.izq = tk.Frame(self.cuerpo, bg=PANEL_OSCURO, highlightbackground=BORDE_CALIDO, highlightthickness=2)
        self.izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        meta_row = tk.Frame(self.izq, bg=PANEL_OSCURO)
        meta_row.pack(fill="x", padx=12, pady=(8, 2))
        self.lbl_escenario = tk.Label(meta_row, text="", bg=PANEL_OSCURO, fg=GRIS_CALIDO, font=("Segoe UI", 10, "bold"))
        self.lbl_escenario.pack(side="left")

        self.lbl_referencia = tk.Label(
            self.izq,
            text="",
            bg=PANEL_OSCURO,
            fg=GRIS_CALIDO,
            font=(FUENTE_MONO, 10),
            anchor="w",
            wraplength=480,
            justify="left",
        )
        self.lbl_referencia.pack(fill="x", padx=12, pady=(0, 4))

        self.lbl_sec_formula = tk.Label(
            self.izq, text="FORMULA OFICIAL DEL METODO", bg=PANEL_OSCURO, fg=AMBAR, font=(FUENTE_MONO, 10, "bold")
        )
        self.lbl_sec_formula.pack(anchor="w", padx=12, pady=(2, 2))

        self.frame_formula = tk.Frame(self.izq, bg="#120E20", highlightbackground=BORDE_CALIDO, highlightthickness=1)
        self.frame_formula.pack(fill="x", padx=12, pady=(0, 8))
        self.lbl_formula_img = tk.Label(self.frame_formula, bg="#120E20", padx=6, pady=4)
        self.lbl_formula = tk.Label(
            self.frame_formula,
            text="",
            bg="#120E20",
            fg=DORADO,
            font=(FUENTE_MONO, 13, "bold"),
            wraplength=480,
            justify="left",
            padx=8,
            pady=6,
        )

        # Tarjeta destacada del enunciado con letra grande y legible
        self.card_enunciado = tk.Frame(
            self.izq, bg="#16112B", highlightbackground=AMBAR, highlightthickness=1
        )
        self.card_enunciado.pack(fill="x", padx=12, pady=(0, 8))

        self.lbl_sec_prob = tk.Label(
            self.card_enunciado,
            text="PROBLEMA ACADEMICO PARAMETRIZADO",
            bg="#16112B",
            fg=AMBAR,
            font=(FUENTE_MONO, 10, "bold"),
        )
        self.lbl_sec_prob.pack(anchor="w", padx=10, pady=(6, 2))

        self.lbl_enunciado = tk.Label(
            self.card_enunciado,
            text="",
            bg="#16112B",
            fg=CREMA,
            font=("Segoe UI", self._tam_enun),
            wraplength=480,
            justify="left",
            anchor="w",
        )
        self.lbl_enunciado.pack(fill="x", padx=10, pady=(0, 8))

        # Switcher de 3 sub-vistas en panel izquierdo (mas espacio vertical para tablas grandes)
        tabs_izq = tk.Frame(self.izq, bg=PANEL_OSCURO)
        tabs_izq.pack(fill="x", padx=12, pady=(0, 4))
        self.btn_tab_datos = tk.Button(
            tabs_izq,
            text="DATOS DEL PROBLEMA",
            font=(FUENTE_MONO, 9, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: self._cambiar_tab_izq("datos"),
        )
        self.btn_tab_datos.pack(side="left", padx=(0, 5))
        self.btn_tab_tablas = self.btn_tab_datos

        self.btn_tab_prog = tk.Button(
            tabs_izq,
            text="TABLA PROGRESIVA",
            font=(FUENTE_MONO, 9, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: self._cambiar_tab_izq("progresiva"),
        )
        self.btn_tab_prog.pack(side="left", padx=(0, 5))

        self.btn_tab_grafica = tk.Button(
            tabs_izq,
            text="GRAFICA REAL",
            font=(FUENTE_MONO, 9, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: self._cambiar_tab_izq("grafica"),
        )
        self.btn_tab_grafica.pack(side="left")

        self.cont_izq_sub = tk.Frame(self.izq, bg=PANEL_OSCURO)
        self.cont_izq_sub.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Vista 1: Tabla de entrada amplia y con fuente grande
        self.frame_datos = tk.Frame(self.cont_izq_sub, bg=PANEL_OSCURO)
        tabla_wrap = tk.Frame(self.frame_datos, bg="#120E20", highlightbackground=BORDE_CALIDO, highlightthickness=1)
        tabla_wrap.pack(fill="both", expand=True)
        sc_t = tk.Scrollbar(tabla_wrap, orient="vertical")
        sc_tx = tk.Scrollbar(tabla_wrap, orient="horizontal")
        self.txt_tabla = tk.Text(
            tabla_wrap,
            bg="#120E20",
            fg=CREMA,
            font=(FUENTE_MONO, self._tam_tabla),
            bd=0,
            padx=10,
            pady=8,
            spacing1=3,
            spacing3=3,
            wrap="none",
            state="disabled",
            yscrollcommand=sc_t.set,
            xscrollcommand=sc_tx.set,
        )
        sc_t.config(command=self.txt_tabla.yview)
        sc_tx.config(command=self.txt_tabla.xview)
        sc_t.pack(side="right", fill="y")
        sc_tx.pack(side="bottom", fill="x")
        self.txt_tabla.pack(side="left", fill="both", expand=True)

        # Vista 2: Tabla progresiva dedicada (iteraciones sin spoiler)
        self.frame_progresiva = tk.Frame(self.cont_izq_sub, bg=PANEL_OSCURO)
        self.lbl_prog_titulo = tk.Label(
            self.frame_progresiva,
            text="BITACORA PROGRESIVA DE ITERACIONES",
            bg=PANEL_OSCURO,
            fg=ESMERALDA,
            font=(FUENTE_MONO, 10, "bold"),
            anchor="w",
        )
        self.lbl_prog_titulo.pack(fill="x", pady=(0, 4))

        prog_wrap = tk.Frame(self.frame_progresiva, bg="#100D1E", highlightbackground=BORDE_CALIDO, highlightthickness=1)
        prog_wrap.pack(fill="both", expand=True)
        sc_p = tk.Scrollbar(prog_wrap, orient="vertical")
        sc_px = tk.Scrollbar(prog_wrap, orient="horizontal")
        self.txt_tabla_prog = tk.Text(
            prog_wrap,
            bg="#100D1E",
            fg=DORADO,
            font=(FUENTE_MONO, self._tam_tabla),
            bd=0,
            padx=10,
            pady=8,
            spacing1=3,
            spacing3=3,
            wrap="none",
            state="disabled",
            yscrollcommand=sc_p.set,
            xscrollcommand=sc_px.set,
        )
        sc_p.config(command=self.txt_tabla_prog.yview)
        sc_px.config(command=self.txt_tabla_prog.xview)
        sc_p.pack(side="right", fill="y")
        sc_px.pack(side="bottom", fill="x")
        self.txt_tabla_prog.pack(side="left", fill="both", expand=True)

        # Vista 3: Grafica Analitica Real ampliada
        self.frame_grafica = tk.Frame(self.cont_izq_sub, bg=PANEL_OSCURO)
        self.visor_grafica = VisorGraficaHUD(self.frame_grafica, height=260)
        self.visor_grafica.pack(fill="both", expand=True)

        self.izq.bind("<Configure>", self._programar_ajuste_izq)
        self._cambiar_tab_izq("datos")

    def _construir_panel_derecho(self) -> None:
        self.der = tk.Frame(self.cuerpo, bg=PANEL_OSCURO, highlightbackground=BORDE_CALIDO, highlightthickness=2)
        self.der.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.canvas_der = tk.Canvas(self.der, bg=PANEL_OSCURO, highlightthickness=0)
        self.sc_der = tk.Scrollbar(self.der, orient="vertical", command=self.canvas_der.yview)
        self.canvas_der.configure(yscrollcommand=self.sc_der.set)
        self.canvas_der.pack(side="left", fill="both", expand=True)

        self.der_contenido = tk.Frame(self.canvas_der, bg=PANEL_OSCURO)
        self._win_der_id = self.canvas_der.create_window((0, 0), window=self.der_contenido, anchor="nw")

        self.canvas_der.bind("<Configure>", self._programar_ajuste_der)
        self.der_contenido.bind("<Configure>", lambda _e: self._actualizar_region_scroll_der())
        self.canvas_der.bind("<Enter>", lambda _e: self._activar_rueda_der(True))
        self.canvas_der.bind("<Leave>", lambda _e: self._activar_rueda_der(False))

        self.canvas_pasos = tk.Canvas(self.der_contenido, height=34, bg=PANEL_OSCURO, highlightthickness=0)
        self.canvas_pasos.pack(fill="x", padx=14, pady=(8, 0))
        self.canvas_pasos.bind("<Configure>", lambda _e: self._al_redimensionar_pasos())

        self.lbl_progreso_paso = tk.Label(
            self.der_contenido, text="PASO 1 DE 3", bg=PANEL_OSCURO, fg=ESMERALDA, font=(FUENTE_MONO, 10, "bold")
        )
        self.lbl_progreso_paso.pack(anchor="w", padx=14, pady=(2, 2))

        self.lbl_paso_titulo = tk.Label(
            self.der_contenido,
            text="",
            bg=PANEL_OSCURO,
            fg=DORADO,
            font=("Segoe UI", self._tam_paso, "bold"),
            wraplength=440,
            justify="left",
        )
        self.lbl_paso_titulo.pack(anchor="w", padx=14, pady=(0, 4))

        self.lbl_pregunta = tk.Label(
            self.der_contenido,
            text="",
            bg=PANEL_OSCURO,
            fg=CREMA,
            font=("Segoe UI", self._tam_preg),
            wraplength=440,
            justify="left",
        )
        self.lbl_pregunta.pack(anchor="w", padx=14, pady=(0, 8))

        self.zona_entrada = tk.Frame(self.der_contenido, bg=PANEL_OSCURO)
        self.zona_entrada.pack(fill="x", padx=14, pady=(0, 8))

        self.entry_resp = tk.Entry(
            self.zona_entrada,
            bg="#120E20",
            fg=DORADO,
            insertbackground=DORADO,
            font=("Consolas", 17, "bold"),
            relief="flat",
        )
        self.entry_resp.bind("<Return>", lambda _e: self._verificar_paso())

        self.frame_opciones = tk.Frame(self.zona_entrada, bg=PANEL_OSCURO)

        btn_row = tk.Frame(self.der_contenido, bg=PANEL_OSCURO)
        btn_row.pack(fill="x", padx=12, pady=(0, 6))

        self.btn_verificar = crear_boton_3d(
            btn_row,
            "VERIFICAR",
            self._verificar_paso,
            bg=AMBAR,
            fg="#160F24",
            sombra="#8C4E22",
            fuente=(FUENTE_MONO, 10, "bold"),
            padx=12,
            pady=5,
        )
        self.btn_verificar.pack(side="left", padx=(0, 6))

        self.btn_toggle_calc = tk.Button(
            btn_row,
            text="OCULTAR CALC",
            command=self._alternar_calculadora,
            bg=PANEL_ELEVADO,
            fg=DORADO,
            font=(FUENTE_MONO, 9, "bold"),
            bd=0,
            padx=9,
            pady=6,
            cursor="hand2",
        )
        self.btn_toggle_calc.pack(side="left", padx=(0, 6))

        self.btn_nuevos_datos = crear_boton_3d(
            btn_row,
            "NUEVOS DATOS",
            lambda: self.nueva_mision_aleatoria(permitir_en_examen=False),
            bg=PANEL_ELEVADO,
            fg=CREMA,
            sombra="#120E20",
            fuente=(FUENTE_MONO, 9, "bold"),
            padx=9,
            pady=5,
        )
        self.btn_nuevos_datos.pack(side="left")

        self.lbl_feedback = tk.Label(
            self.der_contenido,
            text="",
            bg="#120E20",
            fg=GRIS_CALIDO,
            font=("Segoe UI", 10, "bold"),
            wraplength=420,
            justify="left",
            padx=10,
            pady=6,
            anchor="w",
        )
        self.lbl_feedback.pack(fill="x", padx=12, pady=(0, 6))

        # Calculadora cientifica embebida (NUNCA Toplevel para no disparar FocusOut)
        self.calculadora = CalculadoraCientifica(
            self.der_contenido,
            al_enviar_resultado=self._recibir_de_calculadora,
            bg="#161129",
            acento=AMBAR,
            permitir_clipboard=not self.estado.es_modo_examen,
        )
        self.calculadora.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    # ------------------------------------------------------------------
    # ESCALADO RESPONSIVO Y SCROLL AUTOMATICO
    # ------------------------------------------------------------------

    def _activar_rueda_der(self, activo: bool) -> None:
        if not self.winfo_exists():
            return
        if activo:
            self.canvas_der.bind_all("<MouseWheel>", self._scroll_rueda_der)
        else:
            try:
                self.canvas_der.unbind_all("<MouseWheel>")
            except Exception:
                pass

    def _scroll_rueda_der(self, event) -> None:
        if not self.canvas_der.winfo_exists():
            return
        req_h = self.der_contenido.winfo_reqheight()
        vis_h = self.canvas_der.winfo_height()
        if req_h > vis_h:
            paso = int(-1 * (event.delta / 120))
            if paso != 0:
                self.canvas_der.yview_scroll(paso, "units")

    def _programar_ajuste_izq(self, event=None) -> None:
        w = event.width if event else self.izq.winfo_width()
        if w < 120:
            return
        if abs(w - self._ancho_izq_prev) < 14:
            return
        if self._resize_izq_id is not None:
            try:
                self.after_cancel(self._resize_izq_id)
            except Exception:
                pass
        self._resize_izq_id = self.after(45, self._aplicar_ajuste_izq)

    def _aplicar_ajuste_izq(self) -> None:
        self._resize_izq_id = None
        if not self.winfo_exists() or not self.izq.winfo_exists():
            return
        w = max(self.izq.winfo_width(), 360)
        h = max(self.izq.winfo_height(), 400)
        self._ancho_izq_prev = w

        if w >= 640 and h >= 620:
            enun, tabla, latex_pt, ref_pt = 14, 13, 15, 11
        elif w >= 520 and h >= 540:
            enun, tabla, latex_pt, ref_pt = 13, 12, 14, 10
        else:
            enun, tabla, latex_pt, ref_pt = 12, 11, 13, 10

        wrap = max(300, w - 44)
        self.lbl_referencia.config(wraplength=wrap, font=(FUENTE_MONO, ref_pt))
        self.lbl_formula.config(wraplength=wrap)
        self.lbl_enunciado.config(wraplength=wrap, font=("Segoe UI", enun))
        self.txt_tabla.config(font=(FUENTE_MONO, tabla))
        self.txt_tabla_prog.config(font=(FUENTE_MONO, tabla))

        cambio_latex = (latex_pt != self._tam_latex or abs(enun - self._tam_enun) >= 1)
        self._tam_enun = enun
        self._tam_tabla = tabla
        self._tam_latex = latex_pt

        if cambio_latex and self.mision:
            self._refrescar_formula_imagen(max_ancho=wrap)

    def _refrescar_formula_imagen(self, max_ancho: Optional[int] = None) -> None:
        if not self.mision:
            return
        esc = obtener_escenario(self.mision.get("sala_id", 1))
        latex = LATEX_METODOS.get(self.nombre_metodo)
        ancho_lim = max(320, max_ancho or (self.izq.winfo_width() - 44))
        foto = (
            renderizar_formula_tk(latex, color_texto=esc["acento"], tamano_pt=self._tam_latex, max_ancho=ancho_lim)
            if latex
            else None
        )
        self.lbl_formula_img.pack_forget()
        self.lbl_formula.pack_forget()
        if foto is not None:
            self._foto_formula = foto
            self.lbl_formula_img.config(image=foto, text="")
            self.lbl_formula_img.pack(fill="x")
        else:
            self.lbl_formula.config(text=self.mision["formula"])
            self.lbl_formula.pack(fill="x")

    def _programar_ajuste_der(self, event=None) -> None:
        if self._resize_der_id is not None:
            try:
                self.after_cancel(self._resize_der_id)
            except Exception:
                pass
        self._resize_der_id = self.after(30, self._aplicar_ajuste_der)

    def _aplicar_ajuste_der(self) -> None:
        self._resize_der_id = None
        if not self.winfo_exists() or not self.canvas_der.winfo_exists():
            return
        w = max(self.canvas_der.winfo_width(), 320)
        h = max(self.canvas_der.winfo_height(), 360)
        if abs(w - self._ancho_der_prev) >= 14:
            self._ancho_der_prev = w
            if w >= 560 and h >= 640:
                self._tam_paso, self._tam_preg, self._tam_opc = 14, 13, 12
            elif w >= 450 and h >= 550:
                self._tam_paso, self._tam_preg, self._tam_opc = 13, 12, 11
            else:
                self._tam_paso, self._tam_preg, self._tam_opc = 12, 11, 10
            wrap = max(260, w - 42)
            self.lbl_paso_titulo.config(wraplength=wrap, font=("Segoe UI", self._tam_paso, "bold"))
            self.lbl_pregunta.config(wraplength=wrap, font=("Segoe UI", self._tam_preg))
            self.lbl_feedback.config(wraplength=wrap)
            for hijo in self.frame_opciones.winfo_children():
                if isinstance(hijo, tk.Radiobutton):
                    hijo.config(wraplength=wrap, font=("Segoe UI", self._tam_opc))
        self._actualizar_region_scroll_der()

    def _programar_scroll_der(self) -> None:
        if not self.winfo_exists():
            return
        if self._scroll_idle_id is not None:
            try:
                self.after_cancel(self._scroll_idle_id)
            except tk.TclError:
                pass
        self._scroll_idle_id = self.after_idle(self._actualizar_region_scroll_der)

    def _actualizar_region_scroll_der(self) -> None:
        self._scroll_idle_id = None
        if not self.winfo_exists() or not self.canvas_der.winfo_exists():
            return
        w = max(self.canvas_der.winfo_width(), 320)
        h = max(self.canvas_der.winfo_height(), 200)
        req_h = max(self.der_contenido.winfo_reqheight(), 1)
        estado = (w, h, req_h)
        if estado == self._estado_scroll_der:
            return
        self._estado_scroll_der = estado

        if req_h > h + 4:
            if not self.sc_der.winfo_ismapped():
                self.sc_der.pack(side="right", fill="y")
            w_eff = max(280, self.der.winfo_width() - self.sc_der.winfo_reqwidth() - 4)
            self.canvas_der.itemconfigure(self._win_der_id, width=w_eff, height=req_h)
            self.canvas_der.configure(scrollregion=(0, 0, w_eff, req_h))
        else:
            if self.sc_der.winfo_ismapped():
                self.sc_der.pack_forget()
            self.canvas_der.itemconfigure(self._win_der_id, width=w, height=h)
            self.canvas_der.configure(scrollregion=(0, 0, w, h))
            self.canvas_der.yview_moveto(0.0)

    # ------------------------------------------------------------------
    # NAVEGACION INTERNA Y CALCULADORA
    # ------------------------------------------------------------------

    def _cambiar_tab_izq(self, tab: str) -> None:
        if tab == "tablas":
            tab = "datos"
        self._tab_izq_actual = tab
        self.frame_datos.pack_forget()
        self.frame_progresiva.pack_forget()
        self.frame_grafica.pack_forget()

        self.btn_tab_datos.config(bg=PANEL_ELEVADO, fg=CREMA)
        self.btn_tab_prog.config(bg=PANEL_ELEVADO, fg=CREMA)
        self.btn_tab_grafica.config(bg=PANEL_ELEVADO, fg=CREMA)

        if tab == "datos":
            self.frame_datos.pack(fill="both", expand=True)
            self.btn_tab_datos.config(bg=DORADO, fg=FONDO_GALAXIA)
        elif tab == "progresiva":
            self.frame_progresiva.pack(fill="both", expand=True)
            self.btn_tab_prog.config(bg=DORADO, fg=FONDO_GALAXIA)
        else:
            self.frame_grafica.pack(fill="both", expand=True)
            self.btn_tab_grafica.config(bg=DORADO, fg=FONDO_GALAXIA)
            if self.mision:
                esc = obtener_escenario(self.mision.get("sala_id", 1))
                self.visor_grafica.actualizar(
                    self.mision,
                    esc["acento"],
                    paso_idx=self.paso_idx,
                    completado=(not self.activo and self.paso_idx >= len(self.mision.get("pasos", []))),
                )

    def _alternar_calculadora(self) -> None:
        self._calc_visible = not self._calc_visible
        if self._calc_visible:
            self.calculadora.pack(fill="both", expand=True, padx=12, pady=(0, 8))
            self.btn_toggle_calc.config(text="OCULTAR CALC")
        else:
            self.calculadora.pack_forget()
            self.btn_toggle_calc.config(text="MOSTRAR CALC")
        self._programar_scroll_der()

    def _recibir_de_calculadora(self, texto_val: str) -> None:
        pasos = self.mision.get("pasos", [])
        if self.paso_idx >= len(pasos) or pasos[self.paso_idx].get("tipo") != "numero":
            return
        self.entry_resp.delete(0, tk.END)
        self.entry_resp.insert(0, texto_val)
        self.entry_resp.focus_set()
        self.lbl_feedback.config(text=f"Valor {texto_val} transferido desde calculadora.", fg=ESMERALDA)

    # ------------------------------------------------------------------
    # SEGURIDAD DE MODO EXAMEN INGE (FOCUS / CLIPBOARD / PRIVACY CURTAIN)
    # ------------------------------------------------------------------

    def _configurar_seguridad_modo(self) -> None:
        es_ex = self.estado.es_modo_examen
        if es_ex:
            self.lbl_modo_badge.config(text="MODO EXAMEN INGE", bg=ROJO_OXIGENO, fg=CREMA)
            self.btn_nuevos_datos.boton.config(state="disabled", text="BLOQUEADO EXAMEN")
            self.calculadora.establecer_clipboard_bloqueado(True)
            self._aplicar_bloqueo_portapapeles(True)
            self._activar_detector_foco()
        else:
            self.lbl_modo_badge.config(text="MODO PRACTICA", bg=ESMERALDA, fg=FONDO_GALAXIA)
            self.btn_nuevos_datos.boton.config(state="normal", text="NUEVOS DATOS")
            self.calculadora.establecer_clipboard_bloqueado(False)
            self._aplicar_bloqueo_portapapeles(False)
            self._desactivar_detector_foco()

    def _aplicar_bloqueo_portapapeles(self, bloquear: bool) -> None:
        eventos_clip = (
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
        )
        eventos_sel = ("<B1-Motion>", "<Double-Button-1>", "<Triple-Button-1>", "<Shift-Left>", "<Shift-Right>")
        for w in (self.txt_tabla, self.txt_tabla_prog, self.entry_resp):
            for ev in eventos_clip:
                if bloquear:
                    w.bind(ev, lambda _e: "break")
                else:
                    w.unbind(ev)
        for w_ro in (self.txt_tabla, self.txt_tabla_prog):
            for ev in eventos_sel:
                if bloquear:
                    w_ro.bind(ev, lambda _e: "break")
                else:
                    w_ro.unbind(ev)

    def _activar_detector_foco(self) -> None:
        self._desactivar_detector_foco()
        top = self.winfo_toplevel()
        self._seguridad_activa = True
        self._foco_perdido = False
        self._breach_confirmado = False
        try:
            b1 = top.bind("<FocusOut>", self._al_perder_foco, add="+")
            b2 = top.bind("<FocusIn>", self._al_recuperar_foco, add="+")
            b3 = top.bind("<Unmap>", self._al_minimizar, add="+")
            self._top_binds = [(top, "<FocusOut>", b1), (top, "<FocusIn>", b2), (top, "<Unmap>", b3)]
        except tk.TclError:
            self._top_binds = []

    def _desactivar_detector_foco(self) -> None:
        self._seguridad_activa = False
        for attr in ("_foco_after_id", "_gracia_after_id", "_focus_in_after_id"):
            cid = getattr(self, attr, None)
            if cid is not None:
                try:
                    self.after_cancel(cid)
                except tk.TclError:
                    pass
                setattr(self, attr, None)
        for w, ev, funcid in self._top_binds:
            try:
                if w.winfo_exists() and funcid:
                    w.unbind(ev, funcid)
            except tk.TclError:
                pass
        self._top_binds = []
        self._ocultar_cortina_privacidad()

    def _mostrar_cortina_privacidad(self, titulo: str, mensaje: str, bloqueada_con_reset: bool) -> None:
        if not self.winfo_exists():
            return
        if self._cortina_overlay is None or not self._cortina_overlay.winfo_exists():
            ov = tk.Frame(self, bg="#090611")
            ov.place(relx=0, rely=0, relwidth=1, relheight=1)
            card = tk.Frame(ov, bg=PANEL_OSCURO, highlightbackground=ROJO_OXIGENO, highlightthickness=3, padx=32, pady=24)
            card.place(relx=0.5, rely=0.5, anchor="center", width=560)
            self._lbl_cortina_titulo = tk.Label(card, text="", bg=PANEL_OSCURO, fg=ROJO_OXIGENO, font=F_TITULO)
            self._lbl_cortina_titulo.pack(pady=(0, 10))
            self._lbl_cortina_msg = tk.Label(
                card, text="", bg=PANEL_OSCURO, fg=CREMA, font=F_CUERPO, wraplength=490, justify="center"
            )
            self._lbl_cortina_msg.pack(pady=(0, 16))
            self._btn_cortina_accion = crear_boton_3d(
                card,
                "GENERAR NUEVO EJERCICIO Y REANUDAR",
                self._reiniciar_por_incidente_foco,
                bg=ROJO_OXIGENO,
                fg=CREMA,
                sombra="#5A1525",
                fuente=F_CUERPO_BOLD,
                padx=18,
                pady=10,
            )
            self._cortina_overlay = ov
        self._cortina_overlay.lift()
        if self._lbl_cortina_titulo is not None:
            self._lbl_cortina_titulo.config(text=titulo)
        if self._lbl_cortina_msg is not None:
            self._lbl_cortina_msg.config(text=mensaje)
        if self._btn_cortina_accion is not None:
            if bloqueada_con_reset:
                self._btn_cortina_accion.pack(pady=(4, 0))
            else:
                self._btn_cortina_accion.pack_forget()

    def _ocultar_cortina_privacidad(self) -> None:
        if self._cortina_overlay is not None and self._cortina_overlay.winfo_exists():
            self._cortina_overlay.destroy()
        self._cortina_overlay = None
        self._lbl_cortina_titulo = None
        self._lbl_cortina_msg = None
        self._btn_cortina_accion = None

    def _al_minimizar(self, evento) -> None:
        if not self._seguridad_activa or not self.activo or not self.estado.es_modo_examen:
            return
        top = self.winfo_toplevel()
        if evento.widget is not top:
            return
        try:
            estado_win = top.state()
        except tk.TclError:
            estado_win = "iconic"
        if estado_win == "iconic":
            self._confirmar_incidente_foco("minimizado", "VENTANA MINIMIZADA DETECTADA")

    def _al_perder_foco(self, evento) -> None:
        if not self._seguridad_activa or not self.activo or not self.estado.es_modo_examen:
            return
        top = self.winfo_toplevel()
        if evento.widget is not top:
            return
        # 0 ms: cortina de privacidad inmediata (reloj sigue corriendo)
        self._mostrar_cortina_privacidad(
            "VERIFICANDO INTEGRIDAD DE VENTANA...",
            "Contenido del examen oculto temporalmente por perdida de foco.",
            bloqueada_con_reset=False,
        )
        if self._foco_after_id is not None:
            try:
                self.after_cancel(self._foco_after_id)
            except tk.TclError:
                pass
        self._foco_after_id = self.after(45, self._evaluar_foco_tras_rebote)

    def _evaluar_foco_tras_rebote(self) -> None:
        self._foco_after_id = None
        if not self._seguridad_activa or not self.activo or not self.winfo_exists():
            return
        top = self.winfo_toplevel()
        if top.focus_displayof() is not None:
            # Rebote interno dentro de la propia aplicacion: sin penalizacion
            if not self._breach_confirmado:
                self._ocultar_cortina_privacidad()
            return

        # Foco salio realmente de la aplicacion
        self._foco_perdido = True
        self._instante_salida = time.time()
        try:
            if top.state() == "iconic":
                self._confirmar_incidente_foco("minimizado", "VENTANA MINIMIZADA DETECTADA")
                return
        except tk.TclError:
            pass

        if self._micro_pausas_intento >= 2:
            self._confirmar_incidente_foco("micro_pausas_excedidas", "LIMITE DE SALIDAS DE VENTANA EXCEDIDO")
            return

        if self._gracia_after_id is not None:
            try:
                self.after_cancel(self._gracia_after_id)
            except tk.TclError:
                pass
        self._gracia_after_id = self.after(2500, self._expirar_ventana_gracia)

    def _expirar_ventana_gracia(self) -> None:
        self._gracia_after_id = None
        if not self._seguridad_activa or not self.activo or self._breach_confirmado:
            return
        self._confirmar_incidente_foco("salida_prolongada", "SALIDA PROLONGADA DE LA APLICACION (> 2.5 s)")

    def _al_recuperar_foco(self, evento) -> None:
        if not self._seguridad_activa or not self.activo or not self.estado.es_modo_examen:
            return
        if not self._foco_perdido or self._breach_confirmado:
            return
        top = self.winfo_toplevel()
        if evento.widget is not top:
            return
        if self._focus_in_after_id is not None:
            try:
                self.after_cancel(self._focus_in_after_id)
            except tk.TclError:
                pass
        self._focus_in_after_id = self.after(45, self._validar_retorno_foco)

    def _validar_retorno_foco(self) -> None:
        self._focus_in_after_id = None
        if not self._seguridad_activa or not self.activo or self._breach_confirmado or not self.winfo_exists():
            return
        top = self.winfo_toplevel()
        try:
            if top.state() == "iconic" or top.focus_displayof() is None:
                return
        except tk.TclError:
            return

        if self._gracia_after_id is not None:
            try:
                self.after_cancel(self._gracia_after_id)
            except tk.TclError:
                pass
            self._gracia_after_id = None

        duracion = max(0.0, time.time() - self._instante_salida)
        self._foco_perdido = False
        if duracion <= 2.5 and self._micro_pausas_intento < 2:
            self._micro_pausas_intento += 1
            self.estado.registrar_micro_pausa(
                self.nombre_metodo,
                seed_id=self.mision.get("seed_id", ""),
                duracion_s=duracion,
                paso=self.paso_idx,
            )
            self._ocultar_cortina_privacidad()
            self.lbl_feedback.config(
                text=f"Aviso: Micro-pausa del sistema detectada ({self._micro_pausas_intento}/2). Mantente en el examen.",
                fg=DORADO,
            )
        else:
            self._confirmar_incidente_foco("salida_prolongada", "SALIDA PROLONGADA DE LA APLICACION")

    def _confirmar_incidente_foco(self, tipo: str, titulo_motivo: str) -> None:
        if self._breach_confirmado:
            return
        self._breach_confirmado = True
        self._foco_perdido = False
        for attr in ("_foco_after_id", "_gracia_after_id", "_focus_in_after_id"):
            cid = getattr(self, attr, None)
            if cid is not None:
                try:
                    self.after_cancel(cid)
                except tk.TclError:
                    pass
                setattr(self, attr, None)

        duracion = max(0.0, time.time() - self._instante_salida) if self._instante_salida else 0.0
        self.estado.registrar_incidente_foco(
            self.nombre_metodo,
            seed_id=self.mision.get("seed_id", ""),
            tipo=tipo,
            duracion_s=duracion,
            paso=self.paso_idx,
        )
        self._mostrar_cortina_privacidad(
            titulo_motivo,
            (
                "Se registro un incidente de abandono/minimizacion en Modo Examen Inge.\n"
                "Por politica anti-copia el problema actual fue invalidado y debes resolver otra variante."
            ),
            bloqueada_con_reset=True,
        )

    def _reiniciar_por_incidente_foco(self) -> None:
        plantilla_previa = self.mision.get("plantilla_id")
        self._ocultar_cortina_privacidad()
        self.nueva_mision_aleatoria(permitir_en_examen=True, excluir_plantilla_id=plantilla_previa)

    # ------------------------------------------------------------------
    # CICLO DE VIDA, MISION Y VALIDACION DE PASOS
    # ------------------------------------------------------------------

    def _cancelar_timer(self) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def _al_destruir(self) -> None:
        self.activo = False
        self._cancelar_timer()
        for attr in ("_resize_izq_id", "_resize_der_id", "_scroll_idle_id"):
            cid = getattr(self, attr, None)
            if cid is not None:
                try:
                    self.after_cancel(cid)
                except tk.TclError:
                    pass
                setattr(self, attr, None)
        try:
            self.canvas_der.unbind_all("<MouseWheel>")
        except Exception:
            pass
        self._desactivar_detector_foco()

    def _cerrar_modal_hud(self) -> None:
        if self._modal_overlay is not None and self._modal_overlay.winfo_exists():
            self._modal_overlay.destroy()
        self._modal_overlay = None

    def _mostrar_modal_hud(self, titulo: str, mensaje: str, acento: str, texto_boton: str, comando: Callable[[], None]) -> None:
        self._cerrar_modal_hud()
        overlay = tk.Frame(self, bg="#0D0A18")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._modal_overlay = overlay

        card = tk.Frame(overlay, bg=PANEL_OSCURO, highlightbackground=acento, highlightthickness=3, padx=32, pady=24)
        card.place(relx=0.5, rely=0.5, anchor="center", width=560)

        tk.Label(card, text=titulo.upper(), bg=PANEL_OSCURO, fg=acento, font=F_TITULO).pack(pady=(0, 10))
        tk.Label(card, text=mensaje, bg=PANEL_OSCURO, fg=CREMA, font=F_CUERPO, wraplength=480, justify="center").pack(pady=(0, 18))

        def _accion():
            self._cerrar_modal_hud()
            if self.winfo_exists():
                comando()

        btn = crear_boton_3d(
            card, texto_boton, _accion, bg=acento, fg="#160F24", sombra="#2D1E42", fuente=F_CUERPO_BOLD, padx=24, pady=9
        )
        btn.pack()
        btn.boton.focus_set()

    def _aplicar_colores_escenario(self, esc: Dict[str, Any]) -> None:
        fondo = esc["fondo"]
        panel = esc.get("panel", PANEL_OSCURO)
        acento = esc["acento"]
        self.configure(bg=fondo)
        self.cuerpo.configure(bg=fondo)
        self.izq.configure(bg=panel, highlightbackground=acento)
        self.der.configure(bg=panel, highlightbackground=acento)
        self.canvas_der.configure(bg=panel)
        self.der_contenido.configure(bg=panel)
        self.canvas_pasos.configure(bg=panel)
        self.zona_entrada.configure(bg=panel)
        self.frame_opciones.configure(bg=panel)
        self.frame_datos.configure(bg=panel)
        self.frame_progresiva.configure(bg=panel)
        self.frame_grafica.configure(bg=panel)
        self.cont_izq_sub.configure(bg=panel)
        self.card_enunciado.configure(highlightbackground=acento)
        for lbl in (
            self.lbl_escenario,
            self.lbl_referencia,
            self.lbl_sec_formula,
            self.lbl_prog_titulo,
            self.lbl_progreso_paso,
            self.lbl_paso_titulo,
            self.lbl_pregunta,
        ):
            lbl.configure(bg=panel)
        self.lbl_sec_prob.configure(fg=acento)
        self.lbl_escenario.config(text=f"ESCENARIO: {esc['nombre'].upper()}", fg=acento)

    def nueva_mision_aleatoria(
        self,
        permitir_en_examen: bool = False,
        excluir_plantilla_id: Optional[str] = None,
    ) -> None:
        if self.estado.es_modo_examen and not permitir_en_examen and self.mision:
            return
        self._cancelar_timer()
        self._cerrar_modal_hud()
        self._verificando = False
        self._micro_pausas_intento = 0
        self._foco_perdido = False
        self._breach_confirmado = False

        self.mision = generar_mision(self.nombre_metodo, excluir_plantilla_id=excluir_plantilla_id)
        self.paso_idx = 0
        self.oxigeno_total = int(self.mision["oxigeno_seg"])
        self.oxigeno_restante = float(self.oxigeno_total)
        self._penalizacion_seg = 0.0
        self.errores_intento = 0
        self.tiempo_inicio = time.time()
        self.activo = True

        self.calculadora.limpiar()

        rec = self.estado.obtener_record(self.nombre_metodo)
        self.lbl_record.config(text=f"REC: {rec:.1f} s" if rec is not None else "SIN RECORD")
        self._actualizar_indicador_estrellas()

        esc = obtener_escenario(self.mision.get("sala_id", 1))
        self._aplicar_colores_escenario(esc)

        ref = self.mision.get("referencia", "Bibliografia Oficial")
        seed = self.mision.get("seed_id", "-")
        self.lbl_referencia.config(text=f"Ref: {ref}   |   Seed ID: {seed}")

        self._refrescar_formula_imagen()

        self.lbl_enunciado.config(text=self.mision["enunciado"])
        self._mostrar_tabla()
        self._mostrar_tabla_progresiva()
        self.visor_grafica.actualizar(self.mision, esc["acento"], paso_idx=0, completado=False)
        self._mostrar_paso_actual()
        self.lbl_feedback.config(text="Calcula el paso actual y verificalo antes de agotar el oxigeno.", fg=GRIS_CALIDO)
        self._refrescar_oxigeno_ui()
        self._configurar_seguridad_modo()
        self._tick_oxigeno()

    def _actualizar_indicador_estrellas(self) -> None:
        est = calcular_estrellas(self.errores_intento)
        col = ESMERALDA if est >= 2.5 else (DORADO if est >= 1.5 else CORAL)
        self.visor_estrellas.actualizar(est)
        self.lbl_estrellas_intento.config(text=f"{est:.1f}/3.0", fg=col)

    def _mostrar_tabla(self) -> None:
        encabezados, filas = self.mision["datos_tabla"]
        lineas = ["  |  ".join(str(h).ljust(12) for h in encabezados)]
        lineas.append("-" * len(lineas[0]))
        for fila in filas:
            lineas.append("  |  ".join(str(c).ljust(12) for c in fila))
        self.txt_tabla.config(state="normal")
        self.txt_tabla.delete("1.0", "end")
        self.txt_tabla.insert("1.0", "\n".join(lineas))
        self.txt_tabla.config(state="disabled")

    def _mostrar_tabla_progresiva(self) -> None:
        tp = self.mision.get("tabla_progresiva") or {}
        titulo = tp.get("titulo", "BITACORA PROGRESIVA")
        cols = tp.get("columnas") or []
        filas = tp.get("filas") or []
        self.lbl_prog_titulo.config(text=titulo.upper())

        lineas = []
        if cols:
            lineas.append(" | ".join(str(c).ljust(11) for c in cols))
            lineas.append("-" * len(lineas[0]))
        paso_ef = 999 if (not self.activo and self.paso_idx >= len(self.mision.get("pasos", []))) else self.paso_idx
        desbloqueadas = 0
        ocultas = 0
        for fila in filas:
            if paso_ef >= int(fila.get("paso_min", 0)):
                vals = fila.get("valores") or []
                lineas.append(" | ".join(str(v).ljust(11) for v in vals))
                desbloqueadas += 1
            else:
                ocultas += 1
        if ocultas > 0:
            lineas.append(f"[{ocultas} fila(s) bloqueada(s) hasta completar pasos]")

        if filas:
            self.btn_tab_prog.config(text=f"TABLA PROGRESIVA ({desbloqueadas}/{len(filas)})")
        else:
            self.btn_tab_prog.config(text="TABLA PROGRESIVA")

        self.txt_tabla_prog.config(state="normal")
        self.txt_tabla_prog.delete("1.0", "end")
        self.txt_tabla_prog.insert("1.0", "\n".join(lineas))
        self.txt_tabla_prog.config(state="disabled")

    def _al_redimensionar_pasos(self) -> None:
        total = len(self.mision.get("pasos", []))
        if total > 0:
            self._dibujar_indicador_pasos(total)

    def _dibujar_indicador_pasos(self, total: int) -> None:
        self.canvas_pasos.delete("all")
        w = max(self.canvas_pasos.winfo_width(), 320)
        espacio = (w - 40) / max(1, total - 1) if total > 1 else 0
        for i in range(total):
            x = 20 + i * espacio if total > 1 else w / 2
            if i < total - 1:
                x_sig = 20 + (i + 1) * espacio
                col_l = ESMERALDA if i < self.paso_idx else BORDE_CALIDO
                self.canvas_pasos.create_line(x, 17, x_sig, 17, fill=col_l, width=3)
            if i < self.paso_idx:
                col_c, txt_c = ESMERALDA, FONDO_GALAXIA
            elif i == self.paso_idx:
                col_c, txt_c = DORADO, FONDO_GALAXIA
            else:
                col_c, txt_c = PANEL_ELEVADO, GRIS_CALIDO
            self.canvas_pasos.create_oval(x - 11, 6, x + 11, 28, fill=col_c, outline="")
            self.canvas_pasos.create_text(x, 17, text=str(i + 1), fill=txt_c, font=("Consolas", 9, "bold"))

    def _mostrar_paso_actual(self) -> None:
        pasos = self.mision["pasos"]
        paso = pasos[self.paso_idx]
        self._dibujar_indicador_pasos(len(pasos))
        self.lbl_progreso_paso.config(text=f"PASO {self.paso_idx + 1} DE {len(pasos)}")
        self.lbl_paso_titulo.config(text=paso["titulo"])
        self.lbl_pregunta.config(text=paso["pregunta"])

        self.entry_resp.pack_forget()
        self.frame_opciones.pack_forget()
        for w in self.frame_opciones.winfo_children():
            w.destroy()

        if paso["tipo"] == "numero":
            self.entry_resp.delete(0, "end")
            self.entry_resp.pack(fill="x", ipady=5)
            self.entry_resp.focus_set()
        else:
            self.opcion_var.set(-1)
            panel = self.der_contenido["bg"]
            wrap_op = max(260, self._ancho_der_prev - 46) if self._ancho_der_prev > 0 else 410
            for idx, op in enumerate(paso["opciones"]):
                rb = tk.Radiobutton(
                    self.frame_opciones,
                    text=op,
                    variable=self.opcion_var,
                    value=idx,
                    bg=panel,
                    fg=CREMA,
                    selectcolor=BORDE_CALIDO,
                    activebackground=panel,
                    activeforeground=DORADO,
                    font=("Segoe UI", self._tam_opc),
                    wraplength=wrap_op,
                    justify="left",
                    anchor="w",
                    pady=4,
                    cursor="hand2",
                )
                rb.pack(fill="x", anchor="w")
            self.frame_opciones.pack(fill="x")

        self._mostrar_tabla_progresiva()
        esc = obtener_escenario(self.mision.get("sala_id", 1))
        self.visor_grafica.actualizar(self.mision, esc["acento"], paso_idx=self.paso_idx, completado=False)
        self._programar_scroll_der()

    @staticmethod
    def es_respuesta_numerica_valida(val: float, esperado: float, tol_paso: float) -> bool:
        if not math.isfinite(val):
            return False
        tol = max(float(tol_paso), abs(float(esperado)) * 0.012)
        return abs(val - esperado) <= tol

    def _verificar_paso(self) -> None:
        if not self.activo or self._verificando or self._breach_confirmado or self._foco_perdido:
            return
        self._verificando = True
        try:
            pasos = self.mision["pasos"]
            paso = pasos[self.paso_idx]
            if paso["tipo"] == "numero":
                raw = self.entry_resp.get().strip().replace(",", ".")
                try:
                    val = float(raw)
                except ValueError:
                    self.lbl_feedback.config(text="Ingresa un numero valido (ejemplo: 1.4142).", fg=CORAL)
                    return
                if not math.isfinite(val):
                    self.lbl_feedback.config(text="Ingresa un numero real finito (no NaN o Infinito).", fg=CORAL)
                    return
                correcto = self.es_respuesta_numerica_valida(val, paso["esperado"], paso["tolerancia"])
            else:
                sel = self.opcion_var.get()
                if sel == -1:
                    self.lbl_feedback.config(text="Selecciona una opcion antes de verificar.", fg=CORAL)
                    return
                correcto = sel == paso["indice_correcto"]

            if not correcto:
                self.errores_intento += 1
                self.estado.registrar_error(self.nombre_metodo)
                self._penalizacion_seg += 8.0
                self._actualizar_indicador_estrellas()
                self.oxigeno_restante = max(0.0, self.oxigeno_total - self._penalizacion_seg - (time.time() - self.tiempo_inicio))
                self._refrescar_oxigeno_ui()
                if self.oxigeno_restante <= 0.0:
                    self._manejar_sin_oxigeno()
                    return
                if self.estado.es_modo_examen:
                    msg_err = "INCORRECTO (-8 s de oxigeno | -0.5 estrella). Pistas deshabilitadas en Modo Examen."
                else:
                    msg_err = f"INCORRECTO (-8 s de oxigeno | -0.5 estrella). Pista: {paso['pista']}"
                self.lbl_feedback.config(text=msg_err, fg=CORAL)
                return

            self.paso_idx += 1
            if self.paso_idx < len(pasos):
                self.lbl_feedback.config(text="Paso correcto. Avanza al siguiente calculo.", fg=ESMERALDA)
                self._mostrar_paso_actual()
            else:
                self.activo = False
                self._cancelar_timer()
                self._desactivar_detector_foco()
                self._mostrar_tabla_progresiva()
                esc = obtener_escenario(self.mision.get("sala_id", 1))
                self.visor_grafica.actualizar(self.mision, esc["acento"], paso_idx=len(pasos), completado=True)

                tiempo_total = time.time() - self.tiempo_inicio
                est_ganadas = calcular_estrellas(self.errores_intento)
                es_record = self.estado.registrar_victoria(
                    self.nombre_metodo,
                    tiempo_total,
                    errores_intento=self.errores_intento,
                    seed_id=self.mision.get("seed_id", ""),
                    plantilla_id=self.mision.get("plantilla_id", ""),
                )
                msg_rec = "NUEVO RECORD DE TIEMPO." if es_record else "Modulo estabilizado."
                self._mostrar_modal_hud(
                    "Modulo Completado",
                    (
                        f"Completaste {self.nombre_metodo} en {tiempo_total:.1f} s.\n"
                        f"Calificacion: {est_ganadas:.1f} / 3.0 estrellas.\n"
                        f"Seed auditado: {self.mision.get('seed_id', '-')}\n{msg_rec}"
                    ),
                    ESMERALDA,
                    "VOLVER A LA SALA >",
                    self.al_volver,
                )
        finally:
            self._verificando = False

    def _refrescar_oxigeno_ui(self) -> None:
        color = ROJO_OXIGENO if self.oxigeno_restante <= 25 else AMBAR
        suf = " [EXAM]" if self.estado.es_modo_examen else ""
        self.lbl_oxigeno.config(text=f"OXIGENO: {int(math.ceil(self.oxigeno_restante))} s{suf}", fg=color)
        self._dibujar_barra_oxigeno(self.oxigeno_restante / max(self.oxigeno_total, 1))

    def _manejar_sin_oxigeno(self) -> None:
        self.oxigeno_restante = 0.0
        self.activo = False
        self._cancelar_timer()
        self._desactivar_detector_foco()
        self._dibujar_barra_oxigeno(0.0)
        self.lbl_oxigeno.config(text="OXIGENO: 0 s", fg=ROJO_OXIGENO)
        plantilla_prev = self.mision.get("plantilla_id")
        self._mostrar_modal_hud(
            "Oxigeno Agotado",
            "Se agoto el suministro de oxigeno.\nSe generara un nuevo problema del banco academico para este metodo.",
            CORAL,
            "REINTENTAR MODULO >",
            lambda: self.nueva_mision_aleatoria(permitir_en_examen=True, excluir_plantilla_id=plantilla_prev),
        )

    def _tick_oxigeno(self) -> None:
        self._after_id = None
        if not self.activo or not self.winfo_exists():
            return
        self.oxigeno_restante = self.oxigeno_total - self._penalizacion_seg - (time.time() - self.tiempo_inicio)
        if self.oxigeno_restante <= 0:
            self._manejar_sin_oxigeno()
            return
        self._refrescar_oxigeno_ui()
        self._after_id = self.after(200, self._tick_oxigeno)

    def _dibujar_barra_oxigeno(self, fraccion: float) -> None:
        w = max(self.canvas_ox.winfo_width(), 200)
        self.canvas_ox.delete("all")
        color = ROJO_OXIGENO if fraccion <= 0.2 else (DORADO if fraccion <= 0.5 else ESMERALDA)
        self.canvas_ox.create_rectangle(0, 0, w * max(0.0, min(1.0, fraccion)), 16, fill=color, outline="")

    def _salir(self) -> None:
        self.activo = False
        self._cancelar_timer()
        self._desactivar_detector_foco()
        self._cerrar_modal_hud()
        self.al_volver()
