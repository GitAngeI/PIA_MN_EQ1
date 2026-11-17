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
from .guias_metodos import GUIAS_METODOS
from .tema import (
    FONDO_GALAXIA,
    FUENTE_MONO,
    F_CUERPO,
    F_CUERPO_BOLD,
    F_TITULO,
    alternar_tema_actual,
    crear_boton_3d,
    obtener_paleta,
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
        al_cambiar_tema: Optional[Callable[[], None]] = None,
    ):
        pal = obtener_paleta()
        super().__init__(master, bg=pal["fondo"])
        self.nombre_metodo = nombre_metodo
        self.estado = estado
        self.al_volver = al_volver
        self.al_cambiar_tema = al_cambiar_tema
        self._feedback_clave = "texto_sec"

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
        self._guia_overlay: Optional[tk.Frame] = None
        self._foto_formula = None
        self._foto_guia = None
        self._tooltip_lbl: Optional[tk.Label] = None
        self._tooltip_after_id: Optional[str] = None

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
        pal = obtener_paleta()
        self.top = tk.Frame(self, bg=pal["panel"], highlightbackground=pal["borde"], highlightthickness=2)
        self.top.pack(fill="x", padx=16, pady=(6, 4))

        self.btn_volver = tk.Button(
            self.top,
            text="VOLVER",
            command=self._salir,
            bg=pal["panel_elevado"],
            fg=pal["texto"],
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
            bg=pal["panel"],
            fg=pal["titulo"],
            font=("Segoe UI", 12, "bold"),
        )
        self.lbl_titulo.pack(side="left", padx=(4, 8))

        self.lbl_modo_badge = tk.Label(
            self.top,
            text="PRACTICA",
            bg=pal["exito"],
            fg=pal["texto_en_exito"],
            font=(FUENTE_MONO, 9, "bold"),
            padx=8,
            pady=2,
        )
        self.lbl_modo_badge.pack(side="left", padx=4)

        self.btn_tema = tk.Button(
            self.top,
            text=pal["btn_tema_txt"],
            command=self._alternar_tema,
            bg=pal["btn_tema_bg"],
            fg=pal["btn_tema_fg"],
            highlightbackground=pal["borde"],
            highlightthickness=1,
            font=(FUENTE_MONO, 8, "bold"),
            bd=0,
            padx=9,
            pady=3,
            cursor="hand2",
        )
        self.btn_tema.pack(side="right", padx=(4, 10), pady=4)

        self.lbl_record = tk.Label(self.top, text="", bg=pal["panel"], fg=pal["exito"], font=(FUENTE_MONO, 9, "bold"))
        self.lbl_record.pack(side="right", padx=(6, 6))

        self.est_box = tk.Frame(self.top, bg=pal["panel"])
        self.est_box.pack(side="right", padx=6)
        self.visor_estrellas = EstrellasCanvas(self.est_box, valor=3.0, maximo=3, radio=9, espaciado=22, bg=pal["panel"])
        self.visor_estrellas.pack(side="left")
        self.lbl_estrellas_intento = tk.Label(
            self.est_box, text="3.0/3.0", bg=pal["panel"], fg=pal["titulo"], font=(FUENTE_MONO, 9, "bold"), padx=4
        )
        self.lbl_estrellas_intento.pack(side="left")

        # Barra de oxigeno (+ interruptor Sin Tiempo exclusivo de Revision Docente / Practica)
        self.ox_frame = tk.Frame(self, bg=pal["panel"], highlightbackground=pal["borde"], highlightthickness=1)
        self.ox_frame.pack(fill="x", padx=16, pady=(0, 4))

        self.lbl_oxigeno = tk.Label(
            self.ox_frame, text="OXIGENO: 360 s", bg=pal["panel"], fg=pal["acento"], font=(FUENTE_MONO, 9, "bold"), width=26, anchor="w"
        )
        self.lbl_oxigeno.pack(side="left", padx=10, pady=3)

        self.btn_sin_tiempo = tk.Button(
            self.ox_frame,
            text="MODO SIN TIEMPO: OFF",
            command=self._alternar_sin_tiempo,
            bg=pal["panel_elevado"],
            fg=pal["titulo"],
            font=(FUENTE_MONO, 8, "bold"),
            bd=0,
            padx=9,
            pady=3,
            cursor="hand2",
        )
        if not self.estado.es_modo_examen:
            self.btn_sin_tiempo.pack(side="right", padx=(6, 10), pady=2)

        self.canvas_ox = tk.Canvas(self.ox_frame, height=14, bg=pal["superficie_barra"], highlightthickness=0)
        self.canvas_ox.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=3)

        # Cuerpo principal: 2 columnas proporcionales en cualquier resolucion
        self.cuerpo = tk.Frame(self, bg=pal["fondo"])
        self.cuerpo.pack(fill="both", expand=True, padx=14, pady=(0, 6))
        self.cuerpo.columnconfigure(0, weight=54, uniform="col_mision")
        self.cuerpo.columnconfigure(1, weight=46, uniform="col_mision")
        self.cuerpo.rowconfigure(0, weight=1)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

    def _construir_panel_izquierdo(self) -> None:
        pal = obtener_paleta()
        self.izq = tk.Frame(self.cuerpo, bg=pal["panel"], highlightbackground=pal["borde"], highlightthickness=2)
        self.izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.meta_row = tk.Frame(self.izq, bg=pal["panel"])
        self.meta_row.pack(fill="x", padx=12, pady=(8, 2))
        self.lbl_escenario = tk.Label(self.meta_row, text="", bg=pal["panel"], fg=pal["texto_sec"], font=("Segoe UI", 10, "bold"))
        self.lbl_escenario.pack(side="left")

        self.lbl_referencia = tk.Label(
            self.izq,
            text="",
            bg=pal["panel"],
            fg=pal["texto_sec"],
            font=(FUENTE_MONO, 10),
            anchor="w",
            wraplength=480,
            justify="left",
        )
        self.lbl_referencia.pack(fill="x", padx=12, pady=(0, 4))

        self.lbl_sec_formula = tk.Label(
            self.izq, text="FORMULA OFICIAL DEL METODO", bg=pal["panel"], fg=pal["acento"], font=(FUENTE_MONO, 10, "bold")
        )
        self.lbl_sec_formula.pack(anchor="w", padx=12, pady=(2, 2))

        self.frame_formula = tk.Frame(self.izq, bg=pal["superficie"], highlightbackground=pal["borde"], highlightthickness=1)
        self.frame_formula.pack(fill="x", padx=12, pady=(0, 8))
        self.lbl_formula_img = tk.Label(self.frame_formula, bg=pal["superficie"], padx=6, pady=4)
        self.lbl_formula = tk.Label(
            self.frame_formula,
            text="",
            bg=pal["superficie"],
            fg=pal["titulo"],
            font=(FUENTE_MONO, 13, "bold"),
            wraplength=480,
            justify="left",
            padx=8,
            pady=6,
        )

        # Tarjeta destacada del enunciado con letra grande y legible
        self.card_enunciado = tk.Frame(
            self.izq, bg=pal["superficie_alt"], highlightbackground=pal["acento"], highlightthickness=1
        )
        self.card_enunciado.pack(fill="x", padx=12, pady=(0, 8))

        self.lbl_sec_prob = tk.Label(
            self.card_enunciado,
            text="PROBLEMA ACADEMICO PARAMETRIZADO",
            bg=pal["superficie_alt"],
            fg=pal["acento"],
            font=(FUENTE_MONO, 10, "bold"),
        )
        self.lbl_sec_prob.pack(anchor="w", padx=10, pady=(6, 2))

        self.lbl_enunciado = tk.Label(
            self.card_enunciado,
            text="",
            bg=pal["superficie_alt"],
            fg=pal["texto"],
            font=("Segoe UI", self._tam_enun),
            wraplength=480,
            justify="left",
            anchor="w",
        )
        self.lbl_enunciado.pack(fill="x", padx=10, pady=(0, 8))

        # Switcher de 3 sub-vistas en panel izquierdo (mas espacio vertical para tablas grandes)
        self.tabs_izq = tk.Frame(self.izq, bg=pal["panel"])
        self.tabs_izq.pack(fill="x", padx=12, pady=(0, 4))
        self.btn_tab_datos = tk.Button(
            self.tabs_izq,
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
            self.tabs_izq,
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
            self.tabs_izq,
            text="GRAFICA REAL",
            font=(FUENTE_MONO, 9, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: self._cambiar_tab_izq("grafica"),
        )
        self.btn_tab_grafica.pack(side="left")

        self.cont_izq_sub = tk.Frame(self.izq, bg=pal["panel"])
        self.cont_izq_sub.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Vista 1: Tabla de entrada amplia y con fuente grande
        self.frame_datos = tk.Frame(self.cont_izq_sub, bg=pal["panel"])
        self.tabla_wrap = tk.Frame(self.frame_datos, bg=pal["superficie"], highlightbackground=pal["borde"], highlightthickness=1)
        self.tabla_wrap.pack(fill="both", expand=True)
        sc_t = tk.Scrollbar(self.tabla_wrap, orient="vertical")
        sc_tx = tk.Scrollbar(self.tabla_wrap, orient="horizontal")
        self.txt_tabla = tk.Text(
            self.tabla_wrap,
            bg=pal["superficie"],
            fg=pal["texto"],
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
        self.frame_progresiva = tk.Frame(self.cont_izq_sub, bg=pal["panel"])
        self.lbl_prog_titulo = tk.Label(
            self.frame_progresiva,
            text="BITACORA PROGRESIVA DE ITERACIONES",
            bg=pal["panel"],
            fg=pal["exito"],
            font=(FUENTE_MONO, 10, "bold"),
            anchor="w",
        )
        self.lbl_prog_titulo.pack(fill="x", pady=(0, 4))

        self.prog_wrap = tk.Frame(self.frame_progresiva, bg=pal["superficie_prog"], highlightbackground=pal["borde"], highlightthickness=1)
        self.prog_wrap.pack(fill="both", expand=True)
        sc_p = tk.Scrollbar(self.prog_wrap, orient="vertical")
        sc_px = tk.Scrollbar(self.prog_wrap, orient="horizontal")
        self.txt_tabla_prog = tk.Text(
            self.prog_wrap,
            bg=pal["superficie_prog"],
            fg=pal["titulo"],
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
        self.frame_grafica = tk.Frame(self.cont_izq_sub, bg=pal["panel"])
        self.visor_grafica = VisorGraficaHUD(self.frame_grafica, height=260)
        self.visor_grafica.pack(fill="both", expand=True)

        self.izq.bind("<Configure>", self._programar_ajuste_izq)
        self._cambiar_tab_izq("datos")

    def _construir_panel_derecho(self) -> None:
        pal = obtener_paleta()
        self.der = tk.Frame(self.cuerpo, bg=pal["panel"], highlightbackground=pal["borde"], highlightthickness=2)
        self.der.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.canvas_der = tk.Canvas(self.der, bg=pal["panel"], highlightthickness=0)
        self.sc_der = tk.Scrollbar(self.der, orient="vertical", command=self.canvas_der.yview)
        self.canvas_der.configure(yscrollcommand=self.sc_der.set)
        self.canvas_der.pack(side="left", fill="both", expand=True)

        self.der_contenido = tk.Frame(self.canvas_der, bg=pal["panel"])
        self._win_der_id = self.canvas_der.create_window((0, 0), window=self.der_contenido, anchor="nw")

        self.canvas_der.bind("<Configure>", self._programar_ajuste_der)
        self.der_contenido.bind("<Configure>", lambda _e: self._actualizar_region_scroll_der())
        self.canvas_der.bind("<Enter>", lambda _e: self._activar_rueda_der(True))
        self.canvas_der.bind("<Leave>", lambda _e: self._activar_rueda_der(False))

        self.canvas_pasos = tk.Canvas(self.der_contenido, height=34, bg=pal["panel"], highlightthickness=0)
        self.canvas_pasos.pack(fill="x", padx=14, pady=(8, 0))
        self.canvas_pasos.bind("<Configure>", lambda _e: self._al_redimensionar_pasos())

        self.lbl_progreso_paso = tk.Label(
            self.der_contenido, text="PASO 1 DE 3", bg=pal["panel"], fg=pal["exito"], font=(FUENTE_MONO, 10, "bold")
        )
        self.lbl_progreso_paso.pack(anchor="w", padx=14, pady=(2, 2))

        self.lbl_paso_titulo = tk.Label(
            self.der_contenido,
            text="",
            bg=pal["panel"],
            fg=pal["titulo"],
            font=("Segoe UI", self._tam_paso, "bold"),
            wraplength=440,
            justify="left",
        )
        self.lbl_paso_titulo.pack(anchor="w", padx=14, pady=(0, 4))

        self.lbl_pregunta = tk.Label(
            self.der_contenido,
            text="",
            bg=pal["panel"],
            fg=pal["texto"],
            font=("Segoe UI", self._tam_preg),
            wraplength=440,
            justify="left",
        )
        self.lbl_pregunta.pack(anchor="w", padx=14, pady=(0, 4))

        self.lbl_tooltip_input = tk.Label(
            self.der_contenido,
            text="",
            bg=pal["panel"],
            fg=pal["texto_sec"],
            font=("Segoe UI", 9, "italic"),
            wraplength=430,
            justify="left",
            anchor="w",
        )
        self.lbl_tooltip_input.pack(fill="x", padx=14, pady=(0, 4))

        self.zona_entrada = tk.Frame(self.der_contenido, bg=pal["panel"])
        self.zona_entrada.pack(fill="x", padx=14, pady=(0, 8))

        self.entry_resp = tk.Entry(
            self.zona_entrada,
            bg=pal["superficie"],
            fg=pal["titulo"],
            insertbackground=pal["titulo"],
            highlightbackground=pal["borde"],
            highlightthickness=1,
            font=("Consolas", 17, "bold"),
            relief="flat",
        )
        self.entry_resp.bind("<Return>", lambda _e: self._verificar_paso())

        self.frame_opciones = tk.Frame(self.zona_entrada, bg=pal["panel"])

        self.btn_row = tk.Frame(self.der_contenido, bg=pal["panel"])
        self.btn_row.pack(fill="x", padx=12, pady=(0, 6))

        self.btn_verificar = crear_boton_3d(
            self.btn_row,
            "VERIFICAR",
            self._verificar_paso,
            bg=pal["acento"],
            fg=pal["texto_en_acento"],
            sombra=pal["sombra_acento"],
            fuente=(FUENTE_MONO, 10, "bold"),
            padx=10,
            pady=5,
        )
        self.btn_verificar.pack(side="left", padx=(0, 5))

        self.btn_toggle_calc = tk.Button(
            self.btn_row,
            text="OCULTAR CALC",
            command=self._alternar_calculadora,
            bg=pal["panel_elevado"],
            fg=pal["titulo"],
            font=(FUENTE_MONO, 9, "bold"),
            bd=0,
            padx=7,
            pady=6,
            cursor="hand2",
        )
        self.btn_toggle_calc.pack(side="left", padx=(0, 5))

        self.btn_guia = tk.Button(
            self.btn_row,
            text="? GUIA",
            command=self._abrir_modal_guia,
            bg=pal["btn_guia_bg"],
            fg=pal["btn_guia_fg"],
            font=(FUENTE_MONO, 9, "bold"),
            highlightbackground=pal["titulo"],
            highlightthickness=1,
            bd=0,
            padx=8,
            pady=5,
            cursor="hand2",
        )
        self.btn_guia.pack(side="left", padx=(0, 5))

        self.btn_nuevos_datos = crear_boton_3d(
            self.btn_row,
            "NUEVOS DATOS",
            lambda: self.nueva_mision_aleatoria(permitir_en_examen=False),
            bg=pal["panel_elevado"],
            fg=pal["texto"],
            sombra=pal["sombra_panel"],
            fuente=(FUENTE_MONO, 9, "bold"),
            padx=7,
            pady=5,
        )
        self.btn_nuevos_datos.pack(side="left")

        self._vincular_tooltip(self.entry_resp, lambda: self._texto_tooltip_paso())
        self._vincular_tooltip(self.btn_guia, lambda: "Abre el formulario oficial completo y resumen de 3 pasos del metodo.")
        self._vincular_tooltip(self.btn_toggle_calc, lambda: "Muestra u oculta la calculadora cientifica integrada.")
        self._vincular_tooltip(self.btn_sin_tiempo, lambda: "Pausa/activa el temporizador libremente en revision docente (desactivado en Examen).")
        self._vincular_tooltip(self.btn_tema, lambda: "Alterna entre tema oscuro espacial y tema claro (blanco/gris suave).")

        self.lbl_feedback = tk.Label(
            self.der_contenido,
            text="",
            bg=pal["superficie"],
            fg=pal["texto_sec"],
            highlightbackground=pal["borde"],
            highlightthickness=1,
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
            bg=pal["calc_bg"],
            acento=pal["acento"],
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
            self.lbl_tooltip_input.config(wraplength=wrap)
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
        pal = obtener_paleta()
        self.frame_datos.pack_forget()
        self.frame_progresiva.pack_forget()
        self.frame_grafica.pack_forget()

        self.btn_tab_datos.config(bg=pal["panel_elevado"], fg=pal["texto"])
        self.btn_tab_prog.config(bg=pal["panel_elevado"], fg=pal["texto"])
        self.btn_tab_grafica.config(bg=pal["panel_elevado"], fg=pal["texto"])

        if tab == "datos":
            self.frame_datos.pack(fill="both", expand=True)
            self.btn_tab_datos.config(bg=pal["titulo"], fg=pal["texto_en_acento"])
        elif tab == "progresiva":
            self.frame_progresiva.pack(fill="both", expand=True)
            self.btn_tab_prog.config(bg=pal["titulo"], fg=pal["texto_en_acento"])
        else:
            self.frame_grafica.pack(fill="both", expand=True)
            self.btn_tab_grafica.config(bg=pal["titulo"], fg=pal["texto_en_acento"])
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

    def _set_feedback(self, texto: str, clave_color: str = "texto_sec") -> None:
        pal = obtener_paleta()
        self._feedback_clave = clave_color
        self.lbl_feedback.config(text=texto, bg=pal["superficie"], fg=pal.get(clave_color, pal["texto_sec"]))

    def _recibir_de_calculadora(self, texto_val: str) -> None:
        pasos = self.mision.get("pasos", [])
        if self.paso_idx >= len(pasos) or pasos[self.paso_idx].get("tipo") != "numero":
            return
        self.entry_resp.delete(0, tk.END)
        self.entry_resp.insert(0, texto_val)
        self.entry_resp.focus_set()
        self._set_feedback(f"Valor {texto_val} transferido desde calculadora.", "exito")

    def _alternar_tema(self) -> None:
        nuevo = alternar_tema_actual()
        self.estado.establecer_tema_visual(nuevo)
        self.aplicar_tema()
        if self.al_cambiar_tema is not None:
            try:
                self.al_cambiar_tema()
            except Exception:
                pass

    def aplicar_tema(self) -> None:
        pal = obtener_paleta()
        esc = obtener_escenario(self.mision.get("sala_id", 1)) if self.mision else obtener_escenario(1)

        self.top.configure(bg=pal["panel"], highlightbackground=pal["borde"])
        self.btn_volver.configure(bg=pal["panel_elevado"], fg=pal["texto"])
        self.lbl_titulo.configure(bg=pal["panel"], fg=pal["titulo"])
        self.btn_tema.configure(
            text=pal["btn_tema_txt"],
            bg=pal["btn_tema_bg"],
            fg=pal["btn_tema_fg"],
            highlightbackground=pal["borde"],
        )
        self.lbl_record.configure(bg=pal["panel"], fg=pal["exito"])
        self.est_box.configure(bg=pal["panel"])
        self.visor_estrellas.aplicar_tema(pal["panel"])
        self._actualizar_indicador_estrellas()

        self.ox_frame.configure(bg=pal["panel"], highlightbackground=pal["borde"])
        self.lbl_oxigeno.configure(bg=pal["panel"])
        self.canvas_ox.configure(bg=pal["superficie_barra"])
        self._actualizar_boton_sin_tiempo()
        self._refrescar_oxigeno_ui()

        self.meta_row.configure(bg=esc["panel"])
        self.frame_formula.configure(bg=pal["superficie"], highlightbackground=pal["borde"])
        self.lbl_formula_img.configure(bg=pal["superficie"])
        self.lbl_formula.configure(bg=pal["superficie"], fg=pal["titulo"])

        self.card_enunciado.configure(bg=pal["superficie_alt"], highlightbackground=esc["acento"])
        self.lbl_sec_prob.configure(bg=pal["superficie_alt"], fg=esc["acento"])
        self.lbl_enunciado.configure(bg=pal["superficie_alt"], fg=pal["texto"])

        self.tabs_izq.configure(bg=esc["panel"])
        self.tabla_wrap.configure(bg=pal["superficie"], highlightbackground=pal["borde"])
        self.txt_tabla.configure(bg=pal["superficie"], fg=pal["texto"])
        self.prog_wrap.configure(bg=pal["superficie_prog"], highlightbackground=pal["borde"])
        self.txt_tabla_prog.configure(bg=pal["superficie_prog"], fg=pal["titulo"])

        self.entry_resp.configure(
            bg=pal["superficie"],
            fg=pal["titulo"],
            insertbackground=pal["titulo"],
            highlightbackground=pal["borde"],
        )
        for hijo in self.frame_opciones.winfo_children():
            if isinstance(hijo, tk.Radiobutton):
                hijo.configure(
                    bg=esc["panel"],
                    fg=pal["texto"],
                    selectcolor=pal["borde"],
                    activebackground=esc["panel"],
                    activeforeground=pal["titulo"],
                )

        self.btn_row.configure(bg=esc["panel"])
        self.btn_verificar.actualizar_colores(pal["acento"], pal["texto_en_acento"], pal["sombra_acento"])
        self.btn_toggle_calc.configure(bg=pal["panel_elevado"], fg=pal["titulo"])
        self.btn_guia.configure(bg=pal["btn_guia_bg"], fg=pal["btn_guia_fg"], highlightbackground=pal["titulo"])
        self.btn_nuevos_datos.actualizar_colores(pal["panel_elevado"], pal["texto"], pal["sombra_panel"])

        self.lbl_feedback.configure(
            bg=pal["superficie"],
            fg=pal.get(self._feedback_clave, pal["texto_sec"]),
            highlightbackground=pal["borde"],
        )

        self.aplicar_tema_calculadora(pal, esc)
        self._aplicar_colores_escenario(esc)
        self._actualizar_badge_modo()
        self._cambiar_tab_izq(self._tab_izq_actual)
        self._refrescar_formula_imagen()
        self._al_redimensionar_pasos()
        if self.mision:
            self.visor_grafica.actualizar(
                self.mision,
                esc["acento"],
                paso_idx=self.paso_idx,
                completado=(not self.activo and self.paso_idx >= len(self.mision.get("pasos", []))),
            )

    def aplicar_tema_calculadora(self, pal: Dict[str, Any], esc: Dict[str, Any]) -> None:
        self.calculadora.aplicar_tema(bg=pal["calc_bg"], acento=esc["acento"])

    def _actualizar_badge_modo(self) -> None:
        pal = obtener_paleta()
        if self.estado.es_modo_examen:
            self.lbl_modo_badge.config(text="MODO EXAMEN", bg=pal["peligro"], fg=pal["texto_en_peligro"])
            self.btn_nuevos_datos.boton.config(state="disabled", text="BLOQUEADO EXAMEN")
        else:
            self.lbl_modo_badge.config(text="MODO PRACTICA", bg=pal["exito"], fg=pal["texto_en_exito"])
            self.btn_nuevos_datos.boton.config(state="normal", text="NUEVOS DATOS")

    # ------------------------------------------------------------------
    # MODO REVISION SIN TIEMPO, TOOLTIPS EMBEBIDOS Y MODAL ? GUIA
    # ------------------------------------------------------------------

    def _esta_sin_tiempo(self) -> bool:
        return (not self.estado.es_modo_examen) and bool(self.estado.sin_limite_tiempo)

    def _alternar_sin_tiempo(self) -> None:
        if self.estado.es_modo_examen or not self.activo:
            return
        nuevo = self.estado.establecer_sin_limite_tiempo(not self.estado.sin_limite_tiempo)
        if not nuevo:
            # Restaura tiempo_inicio coherente con el oxigeno restante sin perderlo
            consumido = max(0.0, self.oxigeno_total - self.oxigeno_restante - self._penalizacion_seg)
            self.tiempo_inicio = time.time() - consumido
            if self._after_id is None:
                self._tick_oxigeno()
        self._actualizar_boton_sin_tiempo()
        self._refrescar_oxigeno_ui()

    def _actualizar_boton_sin_tiempo(self) -> None:
        pal = obtener_paleta()
        if self.estado.es_modo_examen:
            if self.btn_sin_tiempo.winfo_ismapped():
                self.btn_sin_tiempo.pack_forget()
            return
        if not self.btn_sin_tiempo.winfo_ismapped():
            self.btn_sin_tiempo.pack(side="right", padx=(6, 10), pady=2)
        if self._esta_sin_tiempo():
            self.btn_sin_tiempo.config(text="SIN TIEMPO: ON", bg=pal["exito"], fg=pal["texto_en_exito"])
        else:
            self.btn_sin_tiempo.config(text="MODO SIN TIEMPO: OFF", bg=pal["panel_elevado"], fg=pal["titulo"])

    def _texto_tooltip_paso(self) -> str:
        pasos = self.mision.get("pasos", [])
        if self.paso_idx < len(pasos):
            return str(pasos[self.paso_idx].get("tooltip", "")).strip()
        return ""

    def _vincular_tooltip(self, widget: tk.Widget, texto_fn: Callable[[], str]) -> None:
        widget.bind("<Enter>", lambda _e, w=widget, fn=texto_fn: self._programar_tooltip(w, fn), add="+")
        widget.bind("<Leave>", lambda _e: self._ocultar_tooltip(), add="+")
        widget.bind("<ButtonPress-1>", lambda _e: self._ocultar_tooltip(), add="+")

    def _programar_tooltip(self, widget: tk.Widget, texto_fn: Callable[[], str]) -> None:
        self._ocultar_tooltip()
        if not self.winfo_exists():
            return
        self._tooltip_after_id = self.after(320, lambda: self._mostrar_tooltip(widget, texto_fn()))

    def _mostrar_tooltip(self, widget: tk.Widget, texto: str) -> None:
        self._tooltip_after_id = None
        if not texto or not self.winfo_exists() or not widget.winfo_exists():
            return
        try:
            rx = widget.winfo_rootx() - self.winfo_rootx()
            ry = widget.winfo_rooty() - self.winfo_rooty() - 36
            if ry < 8:
                ry = widget.winfo_rooty() - self.winfo_rooty() + widget.winfo_height() + 4
            rx = max(12, min(rx, max(40, self.winfo_width() - 360)))
        except tk.TclError:
            return
        self._ocultar_tooltip()
        pal = obtener_paleta()
        lbl = tk.Label(
            self,
            text=texto,
            bg=pal["tooltip_bg"],
            fg=pal["tooltip_fg"],
            highlightbackground=pal["acento"],
            highlightthickness=1,
            font=("Segoe UI", 9, "bold"),
            wraplength=340,
            justify="left",
            padx=8,
            pady=4,
        )
        lbl.place(x=rx, y=ry)
        lbl.lift()
        self._tooltip_lbl = lbl

    def _ocultar_tooltip(self) -> None:
        if self._tooltip_after_id is not None:
            try:
                self.after_cancel(self._tooltip_after_id)
            except tk.TclError:
                pass
            self._tooltip_after_id = None
        if self._tooltip_lbl is not None and self._tooltip_lbl.winfo_exists():
            self._tooltip_lbl.destroy()
        self._tooltip_lbl = None

    def _cerrar_modal_guia(self) -> None:
        if self._guia_overlay is not None and self._guia_overlay.winfo_exists():
            try:
                self._guia_overlay.unbind_all("<MouseWheel>")
            except Exception:
                pass
            self._guia_overlay.destroy()
        self._guia_overlay = None
        self._foto_guia = None

    def _abrir_modal_guia(self) -> None:
        """Abre modal embebido (sin Toplevel) con formulario completo y guía en 3 pasos."""
        self._ocultar_tooltip()
        self._cerrar_modal_guia()
        guia = GUIAS_METODOS.get(self.nombre_metodo)
        if not guia:
            return
        pal = obtener_paleta()
        esc = obtener_escenario(self.mision.get("sala_id", 1))
        acento = esc["acento"]

        ov = tk.Frame(self, bg=pal["overlay"])
        ov.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._guia_overlay = ov

        ancho_modal = min(760, max(540, self.winfo_width() - 80))
        alto_modal = min(600, max(440, self.winfo_height() - 60))
        card = tk.Frame(ov, bg=pal["panel"], highlightbackground=acento, highlightthickness=3)
        card.place(relx=0.5, rely=0.5, anchor="center", width=ancho_modal, height=alto_modal)

        hdr = tk.Frame(card, bg=pal["superficie_alt"])
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text=f"FORMULARIO Y GUIA OFICIAL // {self.nombre_metodo.upper()}",
            bg=pal["superficie_alt"],
            fg=pal["titulo"],
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        ).pack(side="left", padx=14, pady=10)
        tk.Button(
            hdr,
            text="CERRAR [X]",
            command=self._cerrar_modal_guia,
            bg=pal["acento"],
            fg=pal["texto_en_acento"],
            font=(FUENTE_MONO, 9, "bold"),
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
        ).pack(side="right", padx=12, pady=8)

        body_host = tk.Frame(card, bg=pal["panel"])
        body_host.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        sc_g = tk.Scrollbar(body_host, orient="vertical")
        can_g = tk.Canvas(body_host, bg=pal["panel"], highlightthickness=0, yscrollcommand=sc_g.set)
        sc_g.config(command=can_g.yview)
        sc_g.pack(side="right", fill="y")
        can_g.pack(side="left", fill="both", expand=True)

        inner_g = tk.Frame(can_g, bg=pal["panel"], padx=10, pady=8)
        win_g = can_g.create_window((0, 0), window=inner_g, anchor="nw")
        can_g.bind("<Configure>", lambda e: can_g.itemconfigure(win_g, width=max(320, e.width - 4)))
        inner_g.bind("<Configure>", lambda _e: can_g.configure(scrollregion=can_g.bbox("all")))
        can_g.bind("<Enter>", lambda _e: can_g.bind_all("<MouseWheel>", lambda ev: can_g.yview_scroll(int(-ev.delta / 120), "units") if can_g.winfo_exists() else None))
        can_g.bind("<Leave>", lambda _e: can_g.unbind_all("<MouseWheel>"))

        wrap_txt = ancho_modal - 70
        tk.Label(
            inner_g, text=f"Fuente de clase: {guia['fuente']}", bg=pal["panel"], fg=pal["texto_sec"],
            font=(FUENTE_MONO, 9, "bold"), anchor="w", wraplength=wrap_txt, justify="left",
        ).pack(fill="x", pady=(0, 6))

        latex = LATEX_METODOS.get(self.nombre_metodo)
        foto = renderizar_formula_tk(latex, color_texto=acento, tamano_pt=14, max_ancho=wrap_txt) if latex else None
        if foto is not None:
            self._foto_guia = foto
            fr_ltx = tk.Frame(inner_g, bg=pal["superficie"], highlightbackground=pal["borde"], highlightthickness=1)
            fr_ltx.pack(fill="x", pady=(0, 8))
            tk.Label(fr_ltx, image=foto, bg=pal["superficie"], padx=8, pady=6).pack(anchor="w")

        tk.Label(inner_g, text="ECUACIONES COMPLETAS DEL METODO", bg=pal["panel"], fg=pal["acento"], font=(FUENTE_MONO, 10, "bold"), anchor="w").pack(fill="x")
        tk.Label(
            inner_g, text=guia["ecuaciones"], bg=pal["superficie"], fg=pal["titulo"],
            font=(FUENTE_MONO, 10), justify="left", anchor="w", padx=10, pady=8, wraplength=wrap_txt,
        ).pack(fill="x", pady=(2, 8))

        tk.Label(inner_g, text="VARIABLES SOLICITADAS", bg=pal["panel"], fg=pal["exito"], font=(FUENTE_MONO, 10, "bold"), anchor="w").pack(fill="x")
        tk.Label(
            inner_g, text=guia["variables"], bg=pal["superficie_alt"], fg=pal["texto"],
            font=("Segoe UI", 10), justify="left", anchor="w", padx=10, pady=6, wraplength=wrap_txt,
        ).pack(fill="x", pady=(2, 8))

        tk.Label(inner_g, text="RESUMEN EN 3 PASOS PARA RESOLVERLO", bg=pal["panel"], fg=acento, font=(FUENTE_MONO, 10, "bold"), anchor="w").pack(fill="x")
        pasos_box = tk.Frame(inner_g, bg=pal["superficie"], highlightbackground=pal["borde"], highlightthickness=1, padx=10, pady=6)
        pasos_box.pack(fill="x", pady=(2, 8))
        for p_txt in guia["pasos_guia"]:
            tk.Label(
                pasos_box, text=p_txt, bg=pal["superficie"], fg=pal["texto"],
                font=("Segoe UI", 10), justify="left", anchor="w", wraplength=wrap_txt - 16,
            ).pack(fill="x", pady=2)

        if guia.get("tabla_extra"):
            tk.Label(inner_g, text="TABLA OFICIAL DE CONSTANTES", bg=pal["panel"], fg=pal["titulo"], font=(FUENTE_MONO, 10, "bold"), anchor="w").pack(fill="x")
            tk.Label(
                inner_g, text=guia["tabla_extra"], bg=pal["superficie_prog"], fg=pal["texto"],
                font=(FUENTE_MONO, 9), justify="left", anchor="w", padx=10, pady=6,
            ).pack(fill="x", pady=(2, 6))

    # ------------------------------------------------------------------
    # SEGURIDAD DE MODO EXAMEN INGE (FOCUS / CLIPBOARD / PRIVACY CURTAIN)
    # ------------------------------------------------------------------

    def _configurar_seguridad_modo(self) -> None:
        es_ex = self.estado.es_modo_examen
        if es_ex:
            self.estado.establecer_sin_limite_tiempo(False)
            self._actualizar_badge_modo()
            self.calculadora.establecer_clipboard_bloqueado(True)
            self._aplicar_bloqueo_portapapeles(True)
            self._activar_detector_foco()
        else:
            self._actualizar_badge_modo()
            self.calculadora.establecer_clipboard_bloqueado(False)
            self._aplicar_bloqueo_portapapeles(False)
            self._desactivar_detector_foco()
        self._actualizar_boton_sin_tiempo()

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
        pal = obtener_paleta()
        if self._cortina_overlay is None or not self._cortina_overlay.winfo_exists():
            ov = tk.Frame(self, bg=pal["overlay_foco"])
            ov.place(relx=0, rely=0, relwidth=1, relheight=1)
            card = tk.Frame(ov, bg=pal["panel"], highlightbackground=pal["peligro"], highlightthickness=3, padx=32, pady=24)
            card.place(relx=0.5, rely=0.5, anchor="center", width=560)
            self._lbl_cortina_titulo = tk.Label(card, text="", bg=pal["panel"], fg=pal["peligro"], font=F_TITULO)
            self._lbl_cortina_titulo.pack(pady=(0, 10))
            self._lbl_cortina_msg = tk.Label(
                card, text="", bg=pal["panel"], fg=pal["texto"], font=F_CUERPO, wraplength=490, justify="center"
            )
            self._lbl_cortina_msg.pack(pady=(0, 16))
            self._btn_cortina_accion = crear_boton_3d(
                card,
                "GENERAR NUEVO EJERCICIO Y REANUDAR",
                self._reiniciar_por_incidente_foco,
                bg=pal["peligro"],
                fg=pal["texto_en_peligro"],
                sombra=pal["sombra_peligro"],
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
            self._set_feedback(
                f"Aviso: Micro-pausa del sistema detectada ({self._micro_pausas_intento}/2). Mantente en el examen.",
                "titulo",
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
                "Se registro un incidente de abandono/minimizacion en Modo Examen.\n"
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
        self._ocultar_tooltip()
        self._cerrar_modal_guia()
        for attr in ("_resize_izq_id", "_resize_der_id", "_scroll_idle_id", "_tooltip_after_id"):
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
        pal = obtener_paleta()
        overlay = tk.Frame(self, bg=pal["overlay_hud"])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._modal_overlay = overlay

        card = tk.Frame(overlay, bg=pal["panel"], highlightbackground=acento, highlightthickness=3, padx=32, pady=24)
        card.place(relx=0.5, rely=0.5, anchor="center", width=560)

        tk.Label(card, text=titulo.upper(), bg=pal["panel"], fg=acento, font=F_TITULO).pack(pady=(0, 10))
        tk.Label(card, text=mensaje, bg=pal["panel"], fg=pal["texto"], font=F_CUERPO, wraplength=480, justify="center").pack(pady=(0, 18))

        def _accion():
            self._cerrar_modal_hud()
            if self.winfo_exists():
                comando()

        btn = crear_boton_3d(
            card, texto_boton, _accion, bg=acento, fg=pal["texto_en_acento"], sombra=pal["sombra_modal"], fuente=F_CUERPO_BOLD, padx=24, pady=9
        )
        btn.pack()
        btn.boton.focus_set()

    def _aplicar_colores_escenario(self, esc: Dict[str, Any]) -> None:
        pal = obtener_paleta()
        fondo = esc["fondo"]
        panel = esc.get("panel", pal["panel"])
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
        self.meta_row.configure(bg=panel)
        self.tabs_izq.configure(bg=panel)
        self.btn_row.configure(bg=panel)
        self.card_enunciado.configure(highlightbackground=acento)
        for lbl in (
            self.lbl_escenario,
            self.lbl_referencia,
            self.lbl_sec_formula,
            self.lbl_prog_titulo,
            self.lbl_progreso_paso,
            self.lbl_paso_titulo,
            self.lbl_pregunta,
            self.lbl_tooltip_input,
        ):
            lbl.configure(bg=panel)
        self.lbl_referencia.configure(fg=pal["texto_sec"])
        self.lbl_sec_formula.configure(fg=pal["acento"])
        self.lbl_prog_titulo.configure(fg=pal["exito"])
        self.lbl_progreso_paso.configure(fg=pal["exito"])
        self.lbl_paso_titulo.configure(fg=pal["titulo"])
        self.lbl_pregunta.configure(fg=pal["texto"])
        self.lbl_tooltip_input.configure(fg=pal["texto_sec"])
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
        self._cerrar_modal_guia()
        self._ocultar_tooltip()
        self._verificando = False
        self._micro_pausas_intento = 0
        self._foco_perdido = False
        self._breach_confirmado = False

        self.mision = generar_mision(self.nombre_metodo, excluir_plantilla_id=excluir_plantilla_id)
        self.paso_idx = 0
        self.oxigeno_total = int(self.mision["oxigeno_seg"]) * 5
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
        self._set_feedback("Calcula el paso actual y verificalo antes de agotar el oxigeno.", "texto_sec")
        self._refrescar_oxigeno_ui()
        self._configurar_seguridad_modo()
        self._tick_oxigeno()

    def _actualizar_indicador_estrellas(self) -> None:
        pal = obtener_paleta()
        est = calcular_estrellas(self.errores_intento)
        col = pal["exito"] if est >= 2.5 else (pal["titulo"] if est >= 1.5 else pal["alerta"])
        self.visor_estrellas.actualizar(est)
        self.lbl_estrellas_intento.config(text=f"{est:.1f}/3.0", bg=pal["panel"], fg=col)

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
        pal = obtener_paleta()
        self.canvas_pasos.delete("all")
        w = max(self.canvas_pasos.winfo_width(), 320)
        espacio = (w - 40) / max(1, total - 1) if total > 1 else 0
        for i in range(total):
            x = 20 + i * espacio if total > 1 else w / 2
            if i < total - 1:
                x_sig = 20 + (i + 1) * espacio
                col_l = pal["exito"] if i < self.paso_idx else pal["borde"]
                self.canvas_pasos.create_line(x, 17, x_sig, 17, fill=col_l, width=3)
            if i < self.paso_idx:
                col_c, txt_c = pal["exito"], pal["texto_en_exito"]
            elif i == self.paso_idx:
                col_c, txt_c = pal["titulo"], pal["texto_en_acento"]
            else:
                col_c, txt_c = pal["panel_elevado"], pal["texto_sec"]
            self.canvas_pasos.create_oval(x - 11, 6, x + 11, 28, fill=col_c, outline="")
            self.canvas_pasos.create_text(x, 17, text=str(i + 1), fill=txt_c, font=("Consolas", 9, "bold"))

    def _mostrar_paso_actual(self) -> None:
        pal = obtener_paleta()
        pasos = self.mision["pasos"]
        paso = pasos[self.paso_idx]
        self._dibujar_indicador_pasos(len(pasos))
        self.lbl_progreso_paso.config(text=f"PASO {self.paso_idx + 1} DE {len(pasos)}")
        self.lbl_paso_titulo.config(text=paso["titulo"])
        self.lbl_pregunta.config(text=paso["pregunta"])
        tip = str(paso.get("tooltip", "")).strip()
        self.lbl_tooltip_input.config(text=f"Guia del campo: {tip}" if tip else "")
        self._ocultar_tooltip()

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
                    fg=pal["texto"],
                    selectcolor=pal["borde"],
                    activebackground=panel,
                    activeforeground=pal["titulo"],
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
                    self._set_feedback("Ingresa un numero valido (ejemplo: 1.4142).", "alerta")
                    return
                if not math.isfinite(val):
                    self._set_feedback("Ingresa un numero real finito (no NaN o Infinito).", "alerta")
                    return
                correcto = self.es_respuesta_numerica_valida(val, paso["esperado"], paso["tolerancia"])
            else:
                sel = self.opcion_var.get()
                if sel == -1:
                    self._set_feedback("Selecciona una opcion antes de verificar.", "alerta")
                    return
                correcto = sel == paso["indice_correcto"]

            if not correcto:
                self.errores_intento += 1
                self.estado.registrar_error(self.nombre_metodo)
                self._actualizar_indicador_estrellas()
                if self._esta_sin_tiempo():
                    self._refrescar_oxigeno_ui()
                    msg_err = f"INCORRECTO (-0.5 estrella | Sin limite de tiempo). Pista: {paso['pista']}"
                else:
                    self._penalizacion_seg += 8.0
                    self.oxigeno_restante = max(0.0, self.oxigeno_total - self._penalizacion_seg - (time.time() - self.tiempo_inicio))
                    self._refrescar_oxigeno_ui()
                    if self.oxigeno_restante <= 0.0:
                        self._manejar_sin_oxigeno()
                        return
                    if self.estado.es_modo_examen:
                        msg_err = "INCORRECTO (-8 s de oxigeno | -0.5 estrella). Pistas deshabilitadas en Modo Examen."
                    else:
                        msg_err = f"INCORRECTO (-8 s de oxigeno | -0.5 estrella). Pista: {paso['pista']}"
                self._set_feedback(msg_err, "alerta")
                return

            self.paso_idx += 1
            if self.paso_idx < len(pasos):
                self._set_feedback("Paso correcto. Avanza al siguiente calculo.", "exito")
                self._mostrar_paso_actual()
            else:
                pal = obtener_paleta()
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
                    pal["exito"],
                    "VOLVER A LA SALA >",
                    self.al_volver,
                )
        finally:
            self._verificando = False

    def _refrescar_oxigeno_ui(self) -> None:
        pal = obtener_paleta()
        if self._esta_sin_tiempo():
            self.lbl_oxigeno.config(text="OXIGENO: LIBRE [DOCENTE]", fg=pal["exito"])
            self._dibujar_barra_oxigeno(1.0)
            return
        color = pal["peligro"] if self.oxigeno_restante <= 25 else pal["acento"]
        suf = " [EXAM]" if self.estado.es_modo_examen else ""
        self.lbl_oxigeno.config(text=f"OXIGENO: {int(math.ceil(self.oxigeno_restante))} s{suf}", fg=color)
        self._dibujar_barra_oxigeno(self.oxigeno_restante / max(self.oxigeno_total, 1))

    def _manejar_sin_oxigeno(self) -> None:
        pal = obtener_paleta()
        self.oxigeno_restante = 0.0
        self.activo = False
        self._cancelar_timer()
        self._desactivar_detector_foco()
        self._dibujar_barra_oxigeno(0.0)
        self.lbl_oxigeno.config(text="OXIGENO: 0 s", fg=pal["peligro"])
        plantilla_prev = self.mision.get("plantilla_id")
        self._mostrar_modal_hud(
            "Oxigeno Agotado",
            "Se agoto el suministro de oxigeno.\nSe generara un nuevo problema del banco academico para este metodo.",
            pal["alerta"],
            "REINTENTAR MODULO >",
            lambda: self.nueva_mision_aleatoria(permitir_en_examen=True, excluir_plantilla_id=plantilla_prev),
        )

    def _tick_oxigeno(self) -> None:
        self._after_id = None
        if not self.activo or not self.winfo_exists():
            return
        if self._esta_sin_tiempo():
            self._refrescar_oxigeno_ui()
            self._after_id = self.after(350, self._tick_oxigeno)
            return
        self.oxigeno_restante = self.oxigeno_total - self._penalizacion_seg - (time.time() - self.tiempo_inicio)
        if self.oxigeno_restante <= 0:
            self._manejar_sin_oxigeno()
            return
        self._refrescar_oxigeno_ui()
        self._after_id = self.after(200, self._tick_oxigeno)

    def _dibujar_barra_oxigeno(self, fraccion: float) -> None:
        pal = obtener_paleta()
        w = max(self.canvas_ox.winfo_width(), 200)
        self.canvas_ox.delete("all")
        color = pal["peligro"] if fraccion <= 0.2 else (pal["titulo"] if fraccion <= 0.5 else pal["exito"])
        self.canvas_ox.create_rectangle(0, 0, w * max(0.0, min(1.0, fraccion)), 16, fill=color, outline="")

    def _salir(self) -> None:
        self.activo = False
        self._cancelar_timer()
        self._desactivar_detector_foco()
        self._cerrar_modal_hud()
        self.al_volver()
