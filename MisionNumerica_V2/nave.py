"""Misión Numérica - Nave Aurora (Python / Tkinter) - Temario Oficial Ing. Oralia Zamora."""

import os
import sys
import tkinter as tk
from tkinter import filedialog

# Asegura importaciones relativas cuando se ejecuta directamente como script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PADRE_DIR = os.path.dirname(BASE_DIR)
if PADRE_DIR not in sys.path:
    sys.path.insert(0, PADRE_DIR)

from MisionNumerica_V2.juego.estado import EstadoJuego
from MisionNumerica_V2.ui.consola_mision import ConsolaMision
from MisionNumerica_V2.ui.escenarios import obtener_escenario
from MisionNumerica_V2.ui.estrellas import EstrellasCanvas
from MisionNumerica_V2.ui.formulas_latex import LATEX_METODOS, renderizar_formula_tk
from MisionNumerica_V2.ui.mapa_nave import MapaNaveAurora
from MisionNumerica_V2.ui.mapa_progreso import MapaProgresoUI
from MisionNumerica_V2.ui.tema import (
    AMBAR,
    BORDE_CALIDO,
    CORAL,
    CREMA,
    DORADO,
    ESMERALDA,
    FONDO_GALAXIA,
    FUENTE_MONO,
    FUNDAMENTOS_METODOS,
    F_CUERPO,
    F_CUERPO_BOLD,
    F_TITULO,
    GRIS_CALIDO,
    PANEL_ELEVADO,
    PANEL_OSCURO,
    ROJO_OXIGENO,
    SALAS,
    TEMAS_SALAS,
    TODOS_LOS_METODOS,
    crear_boton_3d,
)

TECLAS_MAPA = (
    "<w>", "<W>", "<s>", "<S>", "<a>", "<A>", "<d>", "<D>",
    "<Up>", "<Down>", "<Left>", "<Right>", "<Return>",
)


class NaveAuroraApp(tk.Tk):
    def __init__(self, estado: EstadoJuego = None):
        super().__init__()
        self.title("Nave Aurora // Mision Numerica v4.0")
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        ancho_ini = max(920, min(int(sw * 0.90), 1360))
        alto_ini = max(600, min(int(sh * 0.88), 860))
        ancho_ini = min(ancho_ini, max(740, sw - 24))
        alto_ini = min(alto_ini, max(500, sh - 48))
        pos_x = max(0, (sw - ancho_ini) // 2)
        pos_y = max(0, (sh - alto_ini) // 2 - 14)
        self._ancho_inicial = ancho_ini
        self._alto_inicial = alto_ini
        self.geometry(f"{ancho_ini}x{alto_ini}+{pos_x}+{pos_y}")
        self.minsize(min(920, max(720, sw - 40)), min(580, max(480, sh - 60)))
        self.configure(bg=FONDO_GALAXIA)

        self.estado = estado or EstadoJuego()
        self._en_transicion = False
        self._foto_briefing = None
        self._modal_inicio = None

        self.var_modo = tk.StringVar(value=self.estado.modo_actual)
        self.var_alumno = tk.StringVar(value=self.estado.alumno)
        self.var_matricula = tk.StringVar(value=self.estado.matricula)
        self.var_sin_tiempo = tk.BooleanVar(value=self.estado.sin_limite_tiempo)

        self.contenedor = tk.Frame(self, bg=FONDO_GALAXIA)
        self.contenedor.pack(fill="both", expand=True)

        self.mostrar_inicio()

    def _crear_contenedor_scroll(self, padre, bg: str = FONDO_GALAXIA):
        """Área adaptable con scroll vertical automático solo cuando la vista supera el alto."""
        canvas = tk.Canvas(padre, bg=bg, highlightthickness=0)
        sb = tk.Scrollbar(padre, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=bg)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        estado_prev = [0, 0, 0]
        idle_id = [None]

        def _ajustar(_e=None):
            idle_id[0] = None
            if not canvas.winfo_exists() or not inner.winfo_exists():
                return
            w = max(canvas.winfo_width(), 200)
            h = max(canvas.winfo_height(), 200)
            req_h = max(inner.winfo_reqheight(), 1)
            est = (w, h, req_h)
            if est == tuple(estado_prev):
                return
            estado_prev[0], estado_prev[1], estado_prev[2] = w, h, req_h
            if req_h > h + 4:
                if not sb.winfo_ismapped():
                    sb.pack(side="right", fill="y")
                w_eff = max(200, padre.winfo_width() - sb.winfo_reqwidth() - 2)
                canvas.itemconfigure(win_id, width=w_eff, height=req_h)
                canvas.configure(scrollregion=(0, 0, w_eff, req_h))
            else:
                if sb.winfo_ismapped():
                    sb.pack_forget()
                canvas.itemconfigure(win_id, width=w, height=h)
                canvas.configure(scrollregion=(0, 0, w, h))
                canvas.yview_moveto(0.0)

        def _programar_ajuste(_e=None):
            if not canvas.winfo_exists():
                return
            if idle_id[0] is not None:
                try:
                    canvas.after_cancel(idle_id[0])
                except tk.TclError:
                    pass
            idle_id[0] = canvas.after_idle(_ajustar)

        def _cancelar_idle(_e=None):
            if idle_id[0] is not None:
                try:
                    canvas.after_cancel(idle_id[0])
                except tk.TclError:
                    pass
                idle_id[0] = None

        def _wheel(ev):
            if canvas.winfo_exists() and inner.winfo_reqheight() > canvas.winfo_height():
                delta = int(-1 * (ev.delta / 120))
                if delta != 0:
                    canvas.yview_scroll(delta, "units")

        canvas.bind("<Configure>", _ajustar)
        inner.bind("<Configure>", _programar_ajuste)
        canvas.bind("<Destroy>", _cancelar_idle, add="+")
        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", _wheel))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))
        return canvas, inner

    def _desbindear_mapa(self):
        """Elimina cualquier binding global de WASD/flechas/Return del mapa antes de cambiar de vista."""
        for k in TECLAS_MAPA:
            try:
                self.unbind(k)
            except Exception:
                pass

    def _limpiar(self):
        self._desbindear_mapa()
        try:
            self.unbind_all("<MouseWheel>")
        except Exception:
            pass
        self._modal_inicio = None
        for w in self.contenedor.winfo_children():
            w.destroy()

    def _transicion(self, _texto: str, destino_fn):
        """Cortinilla deslizable animada estilo HUD con bloqueo de reentrancia."""
        if self._en_transicion:
            return
        self._en_transicion = True
        overlay = tk.Canvas(self, bg=FONDO_GALAXIA, highlightthickness=0)
        overlay.place(relwidth=1, relheight=1)
        ancho = max(self.winfo_width(), 720)
        alto = max(self.winfo_height(), 480)
        cortina = overlay.create_rectangle(0, 0, 0, alto, fill=AMBAR, outline="")
        paso = max(90, ancho // 10)

        def cerrar(w: int):
            if not overlay.winfo_exists():
                self._en_transicion = False
                return
            if w < ancho:
                overlay.coords(cortina, 0, 0, w + paso, alto)
                self.after(12, cerrar, w + paso)
            else:
                overlay.itemconfig(cortina, fill=FONDO_GALAXIA)
                try:
                    self._limpiar()
                    destino_fn()
                finally:
                    abrir(0)

        def abrir(x: int):
            if not overlay.winfo_exists():
                self._en_transicion = False
                return
            if x < ancho:
                overlay.coords(cortina, x + paso, 0, ancho, alto)
                self.after(12, abrir, x + paso)
            else:
                overlay.destroy()
                self._en_transicion = False

        cerrar(0)

    # ------------------------------------------------------------------
    # PANTALLA DE INICIO (MODOS, ALUMNO, REINICIO Y EXPORTACION)
    # ------------------------------------------------------------------

    def mostrar_inicio(self):
        self._limpiar()
        self.var_modo.set(self.estado.modo_actual)
        self.var_alumno.set(self.estado.alumno)
        self.var_matricula.set(self.estado.matricula)

        _, inner = self._crear_contenedor_scroll(self.contenedor, bg=FONDO_GALAXIA)
        inner.columnconfigure(0, weight=1)
        inner.rowconfigure(0, weight=1)

        # Contenedor principal ajustado para caber completo en pantalla sin scroll
        tarjeta = tk.Frame(
            inner,
            bg=PANEL_OSCURO,
            highlightbackground=DORADO,
            highlightthickness=2,
            padx=34,
            pady=16,
        )
        tarjeta.grid(row=0, column=0, sticky="nsew", padx=28, pady=12)
        tarjeta.columnconfigure(0, weight=1)

        # 1. Encabezado institucional compacto
        header = tk.Frame(tarjeta, bg=PANEL_OSCURO)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        lbl_uni = tk.Label(
            header,
            text="FIME — UANL  |  METODOS NUMERICOS",
            bg=PANEL_OSCURO,
            fg=GRIS_CALIDO,
            font=("Segoe UI", 13, "bold"),
        )
        lbl_uni.pack()

        lbl_tit = tk.Label(
            header,
            text="PROYECTO AURORA // MISION NUMERICA",
            bg=PANEL_OSCURO,
            fg=DORADO,
            font=("Segoe UI", 24, "bold"),
        )
        lbl_tit.pack(pady=(2, 2))

        lbl_sub = tk.Label(
            header,
            text="Simulador Academico de Analisis Numerico   •   32 Metodos en 7 Sectores   •   Evaluacion Auditada",
            bg=PANEL_OSCURO,
            fg=CREMA,
            font=("Segoe UI", 13),
            justify="center",
            wraplength=960,
        )
        lbl_sub.pack(pady=(0, 2))

        # 2. Panel de Configuracion de Sesion y Credenciales
        panel_perfil = tk.Frame(
            tarjeta,
            bg="#141024",
            highlightbackground=BORDE_CALIDO,
            highlightthickness=1,
            padx=22,
            pady=12,
        )
        panel_perfil.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        panel_perfil.columnconfigure(0, weight=1)

        fila_modo = tk.Frame(panel_perfil, bg="#141024")
        fila_modo.pack(fill="x", pady=(0, 8))

        tk.Label(
            fila_modo,
            text="MODALIDAD DE OPERACION:",
            bg="#141024",
            fg=DORADO,
            font=(FUENTE_MONO, 12, "bold"),
        ).pack(side="left", padx=(0, 14))

        btn_prac = tk.Button(
            fila_modo,
            text="MODO PRACTICA (Con Pistas y Apoyo)",
            font=("Segoe UI", 12, "bold"),
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=lambda: self._cambiar_modo_inicio("practica"),
        )
        btn_prac.pack(side="left", padx=(0, 10))

        btn_exam = tk.Button(
            fila_modo,
            text="MODO EXAMEN (Evaluacion Estricta)",
            font=("Segoe UI", 12, "bold"),
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=lambda: self._cambiar_modo_inicio("examen"),
        )
        btn_exam.pack(side="left")

        def _pintar_botones_modo():
            es_ex = self.var_modo.get() == "examen"
            btn_prac.config(
                bg=PANEL_ELEVADO if es_ex else DORADO,
                fg=GRIS_CALIDO if es_ex else FONDO_GALAXIA,
            )
            btn_exam.config(
                bg=DORADO if es_ex else PANEL_ELEVADO,
                fg=FONDO_GALAXIA if es_ex else GRIS_CALIDO,
            )

        self._pintar_botones_modo_cb = _pintar_botones_modo
        _pintar_botones_modo()

        # Casilla de Modo Evaluacion / Sin Limite de Tiempo
        self.var_sin_tiempo.set(bool(getattr(self.estado, "sin_limite_tiempo", False)))
        chk = tk.Checkbutton(
            panel_perfil,
            text="  Modo Evaluacion / Sin Limite de Tiempo (solo en Practica para revisar sin prisa)",
            variable=self.var_sin_tiempo,
            command=self._aplicar_sin_limite,
            bg="#141024",
            fg=CREMA,
            selectcolor=PANEL_ELEVADO,
            activebackground="#141024",
            activeforeground=DORADO,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            cursor="hand2",
        )
        
        chk.pack(fill="x", pady=(0, 8))
        # Campos de Alumno y Matricula
        fila_datos = tk.Frame(panel_perfil, bg="#141024")
        fila_datos.pack(fill="x", pady=(2, 0))

        tk.Label(
            fila_datos,
            text="NOMBRE DEL ALUMNO:",
            bg="#141024",
            fg=CREMA,
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left", padx=(0, 10))

        entry_alum_wrap = tk.Frame(fila_datos, bg="#0E0B1A", highlightbackground=BORDE_CALIDO, highlightthickness=1)
        entry_alum_wrap.pack(side="left", fill="x", expand=True, padx=(0, 20))
        entry_alum = tk.Entry(
            entry_alum_wrap,
            textvariable=self.var_alumno,
            bg="#0E0B1A",
            fg=DORADO,
            insertbackground=DORADO,
            font=("Consolas", 14, "bold"),
            relief="flat",
        )
        entry_alum.pack(fill="x", padx=8, ipady=4)

        tk.Label(
            fila_datos,
            text="MATRICULA:",
            bg="#141024",
            fg=CREMA,
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left", padx=(0, 10))

        entry_mat_wrap = tk.Frame(fila_datos, bg="#0E0B1A", highlightbackground=BORDE_CALIDO, highlightthickness=1)
        entry_mat_wrap.pack(side="left")
        entry_mat = tk.Entry(
            entry_mat_wrap,
            textvariable=self.var_matricula,
            width=14,
            bg="#0E0B1A",
            fg=DORADO,
            insertbackground=DORADO,
            font=("Consolas", 14, "bold"),
            relief="flat",
        )
        entry_mat.pack(padx=8, ipady=4)

        self.lbl_aviso_inicio = tk.Label(
            panel_perfil,
            text="",
            bg="#141024",
            fg=CORAL,
            font=("Segoe UI", 11, "bold"),
            wraplength=920,
        )
        self.lbl_aviso_inicio.pack(fill="x", pady=(4, 0))

        # 3. Tarjetas de Estado del Sistema
        comp = self.estado.total_completados()
        est_tot = self.estado.total_estrellas()
        integridad = int((comp / 32.0) * 100)
        stats = tk.Frame(tarjeta, bg=PANEL_OSCURO)
        stats.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        tarjetas_data = (
            ("MODALIDAD ACTIVA", self.estado.modo_actual.upper(), DORADO),
            ("MODULOS RESUELTOS", f"{comp} / 32", DORADO if comp < 32 else ESMERALDA),
            ("ESTRELLAS OBTENIDAS", f"{est_tot:.1f} / 96.0", DORADO),
            ("AVANCE DEL SISTEMA", f"{integridad}%", CREMA),
            ("ALERTAS DE VENTANA", str(self.estado.incidentes_foco), CORAL if self.estado.incidentes_foco else CREMA),
        )
        for idx_s, (titulo_s, val_s, col_s) in enumerate(tarjetas_data):
            stats.columnconfigure(idx_s, weight=1, uniform="stat_box")
            box = tk.Frame(
                stats,
                bg="#141024",
                highlightbackground=BORDE_CALIDO,
                highlightthickness=1,
                padx=10,
                pady=10,
            )
            box.grid(row=0, column=idx_s, sticky="nsew", padx=4)
            tk.Label(
                box,
                text=titulo_s,
                bg="#141024",
                fg=GRIS_CALIDO,
                font=(FUENTE_MONO, 10, "bold"),
            ).pack(pady=(0, 2))
            tk.Label(
                box,
                text=val_s,
                bg="#141024",
                fg=col_s,
                font=("Segoe UI", 18, "bold"),
            ).pack()

        # 4. Botonera Principal de Navegacion
        btns = tk.Frame(tarjeta, bg=PANEL_OSCURO)
        btns.grid(row=3, column=0, pady=(0, 10))

        crear_boton_3d(
            btns,
            "INICIAR SISTEMA  >",
            self._iniciar_desde_inicio,
            bg=DORADO,
            fg="#130F21",
            sombra="#8C6D1F",
            fuente=("Segoe UI", 14, "bold"),
            padx=24,
            pady=9,
        ).pack(side="left", padx=6)

        crear_boton_3d(
            btns,
            "BITACORA DE MISION",
            lambda: self._transicion("CARGANDO BITACORA...", self.mostrar_historia),
            bg=PANEL_ELEVADO,
            fg=CREMA,
            sombra="#120E20",
            fuente=("Segoe UI", 13, "bold"),
            padx=18,
            pady=9,
        ).pack(side="left", padx=6)

        crear_boton_3d(
            btns,
            "AUDITORIA Y CERTIFICADO",
            lambda: self._transicion("GENERANDO AUDITORIA...", self.mostrar_certificado_final),
            bg=PANEL_ELEVADO,
            fg=DORADO if comp == 32 else CREMA,
            sombra="#120E20",
            fuente=("Segoe UI", 13, "bold"),
            padx=18,
            pady=9,
        ).pack(side="left", padx=6)

        # 5. Barra inferior de utilidades administrativas
        bar_sec = tk.Frame(tarjeta, bg=PANEL_OSCURO)
        bar_sec.grid(row=4, column=0, pady=(2, 0))

        tk.Button(
            bar_sec,
            text="EXPORTAR REPORTE OFICIAL (.TXT / .CSV / .JSON)",
            command=lambda: self._exportar_reporte_dialogo(self.contenedor),
            bg=PANEL_ELEVADO,
            fg=CREMA,
            activebackground=BORDE_CALIDO,
            activeforeground=DORADO,
            font=(FUENTE_MONO, 10, "bold"),
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=6)

        tk.Button(
            bar_sec,
            text="REINICIAR PROGRESO A CERO",
            command=lambda: self._mostrar_modal_reinicio(self.contenedor),
            bg=PANEL_ELEVADO,
            fg=CORAL,
            activebackground=BORDE_CALIDO,
            activeforeground=CREMA,
            font=(FUENTE_MONO, 10, "bold"),
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=6)

        def _ajustar_inicio(ev):
            lim = max(560, ev.width - 120)
            lbl_sub.config(wraplength=lim)
            self.lbl_aviso_inicio.config(wraplength=lim)

        inner.bind("<Configure>", _ajustar_inicio, add="+")

    def _aplicar_sin_limite(self):
        val = bool(self.var_sin_tiempo.get())
        if hasattr(self.estado, "establecer_sin_limite_tiempo"):
            self.estado.establecer_sin_limite_tiempo(val)
        elif hasattr(self.estado, "cambiar_sin_limite_tiempo"):
            self.estado.cambiar_sin_limite_tiempo(val)
        else:
            try:
                self.estado.establecer_modo(
                    self.var_modo.get(),
                    alumno=self.var_alumno.get().strip(),
                    matricula=self.var_matricula.get().strip(),
                    sin_limite_tiempo=val,
                )
                return
            except TypeError:
                pass
            for attr in ("_sin_limite_tiempo", "modo_sin_limite"):
                if hasattr(self.estado, attr):
                    setattr(self.estado, attr, val)
            if hasattr(self.estado, "_perfil_activo"):
                self.estado._perfil_activo()["sin_limite_tiempo"] = val

    def _cambiar_modo_inicio(self, modo: str):
        self.var_modo.set(modo)
        self.estado.establecer_modo(
            modo,
            alumno=self.var_alumno.get().strip(),
            matricula=self.var_matricula.get().strip(),
        )
        self.mostrar_inicio()

    def _iniciar_desde_inicio(self):
        modo = self.var_modo.get()
        alum = self.var_alumno.get().strip()
        mat = self.var_matricula.get().strip()
        if modo == "examen" and (len(alum) < 2 or len(mat) < 3):
            self.lbl_aviso_inicio.config(
                text="En MODO EXAMEN ingresa Nombre del Alumno y Matricula antes de iniciar.",
                fg=ROJO_OXIGENO,
            )
            return
        self._aplicar_sin_limite()
        self.estado.establecer_modo(modo, alumno=alum, matricula=mat)
        self._transicion("INICIANDO MAPA TACTICO...", self.mostrar_mapa_nave)

    def _mostrar_modal_reinicio(self, padre):
        if self._modal_inicio is not None and self._modal_inicio.winfo_exists():
            self._modal_inicio.destroy()
        ov = tk.Frame(padre, bg="#0B0816")
        ov.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._modal_inicio = ov

        card = tk.Frame(ov, bg=PANEL_OSCURO, highlightbackground=ROJO_OXIGENO, highlightthickness=3, padx=26, pady=22)
        card.place(relx=0.5, rely=0.5, anchor="center", width=590)

        tk.Label(card, text="REINICIAR PROGRESO A 0", bg=PANEL_OSCURO, fg=ROJO_OXIGENO, font=("Segoe UI", 19, "bold")).pack(pady=(0, 8))
        tk.Label(
            card,
            text=f"El perfil activo actual es '{self.estado.modo_actual.upper()}'.\nElige si deseas reiniciar solo este perfil o borrar ambos perfiles a 0.",
            bg=PANEL_OSCURO, fg=CREMA, font=("Segoe UI", 13), justify="center", wraplength=520,
        ).pack(pady=(0, 16))

        def _ejecutar(alcance: str):
            self.estado.reiniciar(alcance=alcance)
            if ov.winfo_exists():
                ov.destroy()
            self.mostrar_inicio()

        btns = tk.Frame(card, bg=PANEL_OSCURO)
        btns.pack()
        tk.Button(
            btns, text=f"REINICIAR {self.estado.modo_actual.upper()}",
            command=lambda: _ejecutar("activo"),
            bg=AMBAR, fg=FONDO_GALAXIA, font=("Segoe UI", 12, "bold"), bd=0, padx=14, pady=8, cursor="hand2",
        ).pack(side="left", padx=6)
        tk.Button(
            btns, text="BORRAR TODO (PRACTICA + EXAMEN)",
            command=lambda: _ejecutar("todo"),
            bg=ROJO_OXIGENO, fg=CREMA, font=("Segoe UI", 12, "bold"), bd=0, padx=14, pady=8, cursor="hand2",
        ).pack(side="left", padx=6)
        tk.Button(
            card, text="CANCELAR", command=ov.destroy,
            bg=PANEL_ELEVADO, fg=CREMA, font=F_CUERPO_BOLD, bd=0, padx=16, pady=7, cursor="hand2",
        ).pack(pady=(12, 0))

    def _exportar_reporte_dialogo(self, padre=None):
        alum = (self.var_alumno.get().strip() or self.estado.alumno or "alumno").replace(" ", "_")
        ruta = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar Reporte Oficial Nave Aurora",
            initialfile=f"reporte_aurora_{self.estado.modo_actual}_{alum}.txt",
            defaultextension=".txt",
            filetypes=[
                ("Reporte de Texto Auditoria (*.txt)", "*.txt"),
                ("Tabla CSV (*.csv)", "*.csv"),
                ("Registro JSON (*.json)", "*.json"),
            ],
        )
        if not ruta:
            return
        ext = os.path.splitext(ruta)[1].lower().lstrip(".")
        fmt = ext if ext in ("txt", "csv", "json") else "txt"
        self.estado.exportar_reporte(ruta, formato=fmt, modo=self.estado.modo_actual)
        if hasattr(self, "lbl_aviso_inicio") and self.lbl_aviso_inicio.winfo_exists():
            self.lbl_aviso_inicio.config(text=f"Reporte exportado correctamente en: {os.path.basename(ruta)}", fg=ESMERALDA)

    # ------------------------------------------------------------------
    # HISTORIA / MAPA PRINCIPAL / SALAS / BRIEFING / CONSOLA / CERTIFICADO
    # ------------------------------------------------------------------

    def mostrar_historia(self):
        self._limpiar()
        _, inner = self._crear_contenedor_scroll(self.contenedor, bg=FONDO_GALAXIA)

        card = tk.Frame(inner, bg=PANEL_OSCURO, highlightbackground=BORDE_CALIDO, highlightthickness=2, padx=32, pady=24)
        card.pack(expand=True, fill="x", padx=44, pady=24)

        grafico = tk.Canvas(card, bg="#120E20", highlightthickness=1, highlightbackground=BORDE_CALIDO, height=150)
        grafico.pack(fill="x", pady=(0, 14))
        alerta_txt_id = [None]

        def _dibujar_alerta(_e=None):
            gw = max(grafico.winfo_width(), 480)
            gh = max(grafico.winfo_height(), 150)
            cx = gw / 2.0
            grafico.delete("all")
            grafico.create_polygon(cx, 20, cx - 95, gh - 28, cx + 95, gh - 28, outline=DORADO, fill="", width=2)
            grafico.create_polygon(cx - 65, gh - 28, cx - 85, gh - 6, cx - 45, gh - 6, outline=DORADO, fill="", width=2)
            grafico.create_polygon(cx + 65, gh - 28, cx + 85, gh - 6, cx + 45, gh - 6, outline=DORADO, fill="", width=2)
            grafico.create_text(cx, gh * 0.56, text="!", fill=ROJO_OXIGENO, font=("Consolas", 32, "bold"))
            grafico.create_line(cx - 125, gh * 0.56, max(160, cx - 220), gh * 0.56, fill=ROJO_OXIGENO, width=2, dash=(4, 4))
            alerta_txt_id[0] = grafico.create_text(
                max(80, cx - 295), gh * 0.56, text="FALLO CRITICO", fill=ROJO_OXIGENO, font=("Segoe UI", 14, "bold")
            )

        grafico.bind("<Configure>", _dibujar_alerta)

        def parpadear():
            if not grafico.winfo_exists():
                return
            tid = alerta_txt_id[0]
            if tid is not None:
                try:
                    actual = grafico.itemcget(tid, "fill")
                    grafico.itemconfig(tid, fill="#120E20" if actual == ROJO_OXIGENO else ROJO_OXIGENO)
                except tk.TclError:
                    pass
            self.after(500, parpadear)

        _dibujar_alerta()
        parpadear()

        tk.Label(card, text="BITACORA DE MISION // ANO 2041", bg=PANEL_OSCURO, fg=DORADO, font=F_TITULO).pack(pady=(0, 10))
        texto = (
            "La nave de exploracion Aurora se aproxima a la orbita de Marte cuando una anomalia "
            "electromagnetica paraliza su computadora central. Los sistemas de pilotaje, "
            "soporte vital y propulsion estan fuera de linea.\n\n"
            "Como ingeniero en jefe, debes acceder a las 7 secciones de la nave y resolver los "
            "32 modulos con problemas parametrizados de libros de Analisis Numerico y las "
            "formulas oficiales de la Ing. Oralia Zamora."
        )
        lbl_hist = tk.Label(card, text=texto, bg=PANEL_OSCURO, fg=CREMA, font=("Segoe UI", 14), justify="left", wraplength=760)
        lbl_hist.pack(fill="x", pady=(0, 18))
        card.bind("<Configure>", lambda e: lbl_hist.config(wraplength=max(420, e.width - 80)), add="+")

        tk.Button(
            card, text="ACCEDER AL PLANO DE LA NAVE >",
            command=lambda: self._transicion("DESPLEGANDO NAVE...", self.mostrar_mapa_nave),
            bg=AMBAR, fg="#160F24", font=F_CUERPO_BOLD, bd=0, padx=24, pady=10, cursor="hand2",
        ).pack()

    def mostrar_mapa_nave(self):
        self._limpiar()
        top = tk.Frame(self.contenedor, bg=PANEL_OSCURO, highlightbackground=DORADO, highlightthickness=2)
        top.pack(fill="x", padx=16, pady=(10, 6))

        tk.Button(
            top,
            text="< MENU INICIAL",
            command=lambda: self._transicion("VOLVIENDO AL INICIO...", self.mostrar_inicio),
            bg=PANEL_ELEVADO,
            fg=CREMA,
            activebackground=BORDE_CALIDO,
            activeforeground=DORADO,
            font=("Segoe UI", 12, "bold"),
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=10, pady=7)

        tk.Label(
            top,
            text="NAVE AURORA  //  PLANO TACTICO DE SISTEMAS",
            bg=PANEL_OSCURO,
            fg=DORADO,
            font=("Segoe UI", 15, "bold"),
        ).pack(side="left", padx=8)

        modo_txt = f"MODO EXAMEN ({self.estado.alumno or 'Alumno'})" if self.estado.es_modo_examen else "MODO PRACTICA"
        tk.Label(
            top,
            text=modo_txt,
            bg="#141024",
            fg=CORAL if self.estado.es_modo_examen else DORADO,
            highlightbackground=CORAL if self.estado.es_modo_examen else BORDE_CALIDO,
            highlightthickness=1,
            font=(FUENTE_MONO, 10, "bold"),
            padx=10,
            pady=4,
        ).pack(side="left", padx=8)

        tk.Button(
            top,
            text="RUTA DE PROGRESO",
            command=lambda: MapaProgresoUI(
                self,
                self.estado,
                al_seleccionar_sala=lambda sid: self._transicion(f"ABRIENDO SALA {sid}...", lambda: self.mostrar_sala(sid)),
            ),
            bg=PANEL_ELEVADO,
            fg=DORADO,
            activebackground=BORDE_CALIDO,
            activeforeground=CREMA,
            font=("Segoe UI", 11, "bold"),
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
        ).pack(side="right", padx=10, pady=7)

        comp = self.estado.total_completados()
        if comp == 32:
            tk.Button(
                top,
                text="CERTIFICADO",
                command=lambda: self._transicion("CARGANDO CERTIFICADO...", self.mostrar_certificado_final),
                bg=ESMERALDA,
                fg=FONDO_GALAXIA,
                font=("Segoe UI", 11, "bold"),
                bd=0,
                padx=12,
                pady=7,
                cursor="hand2",
            ).pack(side="right", padx=4, pady=7)

        tk.Label(
            top,
            text=f"MODULOS: {comp}/32   |   ESTRELLAS: {self.estado.total_estrellas():.1f}/96.0",
            bg=PANEL_OSCURO,
            fg=CREMA,
            font=(FUENTE_MONO, 11, "bold"),
        ).pack(side="right", padx=12)

        cuerpo_mapa = tk.Frame(self.contenedor, bg=FONDO_GALAXIA)
        cuerpo_mapa.pack(fill="both", expand=True, padx=16, pady=(2, 12))

        # Panel lateral derecho mas amplio, formal y con tipografia grande
        hud_der = tk.Frame(
            cuerpo_mapa,
            bg=PANEL_OSCURO,
            highlightbackground=BORDE_CALIDO,
            highlightthickness=2,
            width=360,
        )
        hud_der.pack(side="right", fill="y", padx=(12, 0))
        hud_der.pack_propagate(False)

        header_hud = tk.Frame(hud_der, bg="#141024", highlightbackground=BORDE_CALIDO, highlightthickness=1, padx=14, pady=12)
        header_hud.pack(fill="x", padx=12, pady=(12, 10))

        tk.Label(
            header_hud,
            text="SECTOR SELECCIONADO",
            bg="#141024",
            fg=GRIS_CALIDO,
            font=(FUENTE_MONO, 9, "bold"),
            anchor="w",
        ).pack(fill="x")

        lbl_hud_sid = tk.Label(
            header_hud,
            text="07. COMPUTADORA CENTRAL",
            bg="#141024",
            fg=DORADO,
            font=("Segoe UI", 15, "bold"),
            anchor="w",
            wraplength=310,
            justify="left",
        )
        lbl_hud_sid.pack(fill="x", pady=(2, 4))

        lbl_hud_tema = tk.Label(
            header_hud,
            text="",
            bg="#141024",
            fg=CREMA,
            font=("Segoe UI", 12),
            anchor="w",
            wraplength=310,
            justify="left",
        )
        lbl_hud_tema.pack(fill="x", pady=(0, 8))

        lbl_hud_prog = tk.Label(
            header_hud,
            text="AVANCE DEL SECTOR: 0 / 5 MODULOS",
            bg="#141024",
            fg=GRIS_CALIDO,
            font=(FUENTE_MONO, 10, "bold"),
            anchor="w",
        )
        lbl_hud_prog.pack(fill="x", pady=(0, 4))

        barra_sala = tk.Canvas(header_hud, height=10, bg="#0D0A18", highlightthickness=1, highlightbackground=BORDE_CALIDO)
        barra_sala.pack(fill="x")

        tk.Label(
            hud_der,
            text="METODOS DEL SECTOR (CLIC PARA ABRIR):",
            bg=PANEL_OSCURO,
            fg=GRIS_CALIDO,
            font=(FUENTE_MONO, 10, "bold"),
            anchor="w",
        ).pack(fill="x", padx=14, pady=(2, 4))

        btn_entrar_hud = tk.Button(
            hud_der,
            text="INGRESAR A SALA  >",
            bg=DORADO,
            fg="#130F21",
            activebackground=AMBAR,
            activeforeground="#130F21",
            font=("Segoe UI", 14, "bold"),
            bd=0,
            padx=14,
            pady=11,
            cursor="hand2",
        )
        btn_entrar_hud.pack(side="bottom", fill="x", padx=12, pady=(8, 12))

        lista_host = tk.Frame(hud_der, bg=PANEL_OSCURO)
        lista_host.pack(fill="both", expand=True, padx=12, pady=(0, 4))
        _, lista_hud = self._crear_contenedor_scroll(lista_host, bg=PANEL_OSCURO)

        def actualizar_hud(sid: int):
            s_id, s_nom, _s_col, s_mets = next(s for s in SALAS if s[0] == sid)
            lbl_hud_sid.config(text=f"0{s_id}. {s_nom}", fg=DORADO)
            lbl_hud_tema.config(text=f"Unidad: {TEMAS_SALAS.get(s_id, '')}")
            comp_s = sum(1 for m in s_mets if self.estado.completados.get(m))
            tot_s = max(len(s_mets), 1)
            frac = comp_s / tot_s
            lbl_hud_prog.config(
                text=f"AVANCE DEL SECTOR: {comp_s} / {len(s_mets)} MODULOS",
                fg=ESMERALDA if comp_s == len(s_mets) else GRIS_CALIDO,
            )
            barra_sala.delete("all")
            bw = max(barra_sala.winfo_width(), 280)
            barra_sala.create_rectangle(
                0, 0, bw * frac, 10,
                fill=ESMERALDA if frac == 1 else DORADO,
                outline="",
            )
            for w in lista_hud.winfo_children():
                w.destroy()
            for idx_m, m in enumerate(s_mets, start=1):
                ok = self.estado.completados.get(m, False)
                est_m = self.estado.obtener_estrellas(m) if ok else 0.0
                borde_item = ESMERALDA if ok else BORDE_CALIDO
                row = tk.Frame(
                    lista_hud,
                    bg="#141024",
                    highlightbackground=borde_item,
                    highlightthickness=1,
                    padx=8,
                    pady=7,
                    cursor="hand2",
                )
                row.pack(fill="x", pady=4)

                badge_txt = f"{est_m:.1f} ★" if ok else f"M{idx_m:02d}"
                lbl_ok = tk.Label(
                    row,
                    text=badge_txt,
                    bg="#1F1835" if not ok else "#132A26",
                    fg=ESMERALDA if ok else DORADO,
                    font=(FUENTE_MONO, 10, "bold"),
                    width=6,
                    pady=3,
                )
                lbl_ok.pack(side="left", padx=(2, 8))

                lbl_m = tk.Label(
                    row,
                    text=m,
                    bg="#141024",
                    fg=CREMA,
                    font=("Segoe UI", 11, "bold"),
                    anchor="w",
                    justify="left",
                    wraplength=max(200, hud_w_cache[0] - 115),
                )
                lbl_m.pack(side="left", fill="x", expand=True)

                abrir_m = lambda _e, met=m, s=s_id: self._transicion(
                    "CARGANDO REPORTE...",
                    lambda: self.mostrar_entorno_metodo(met, s),
                )
                row.bind("<Button-1>", abrir_m)
                lbl_ok.bind("<Button-1>", abrir_m)
                lbl_m.bind("<Button-1>", abrir_m)

            btn_entrar_hud.config(
                command=lambda s=s_id: self._transicion(f"ABRIENDO SALA {s}...", lambda: self.mostrar_sala(s)),
            )

        mapa = MapaNaveAurora(
            cuerpo_mapa,
            self.estado,
            al_entrar_sala=lambda sid: self._transicion(f"ABRIENDO SALA {sid}...", lambda: self.mostrar_sala(sid)),
            al_cambiar_sala=actualizar_hud,
        )
        mapa.pack(side="left", fill="both", expand=True)

        hud_w_cache = [360]

        def _ajustar_cuerpo_mapa(ev):
            if ev.width < 400:
                return
            w_hud = max(320, min(420, int(ev.width * 0.30)))
            if abs(w_hud - hud_w_cache[0]) >= 12:
                hud_w_cache[0] = w_hud
                hud_der.config(width=w_hud)
                lbl_hud_sid.config(wraplength=max(240, w_hud - 48))
                lbl_hud_tema.config(wraplength=max(240, w_hud - 48))
                actualizar_hud(mapa.sala_actual)

        cuerpo_mapa.bind("<Configure>", _ajustar_cuerpo_mapa)
        actualizar_hud(mapa.sala_actual)

        for k, dx, dy in (
            ("<w>", 0, -1), ("<W>", 0, -1),
            ("<s>", 0, 1), ("<S>", 0, 1),
            ("<a>", -1, 0), ("<A>", -1, 0),
            ("<d>", 1, 0), ("<D>", 1, 0),
            ("<Up>", 0, -1), ("<Down>", 0, 1), ("<Left>", -1, 0), ("<Right>", 1, 0),
        ):
            self.bind(k, lambda _e, x=dx, y=dy: mapa.mover_tecla(x, y) if mapa.winfo_exists() else None)
        self.bind(
            "<Return>",
            lambda _e: self._transicion(
                f"ABRIENDO SALA {mapa.sala_actual}...",
                lambda: self.mostrar_sala(mapa.sala_actual),
            )
            if mapa.winfo_exists()
            else None,
        )

    def mostrar_sala(self, sala_id: int):
        self._limpiar()
        sid, nombre, color, metodos = next(s for s in SALAS if s[0] == sala_id)
        tema_sala = TEMAS_SALAS.get(sid, "")
        prom_sala = self.estado.promedio_estrellas_sala(metodos)

        top = tk.Frame(self.contenedor, bg=PANEL_OSCURO, highlightbackground=color, highlightthickness=2)
        top.pack(fill="x", padx=16, pady=(12, 6))

        tk.Button(
            top, text="< VOLVER AL PLANO",
            command=lambda: self._transicion("REGRESANDO AL MAPA...", self.mostrar_mapa_nave),
            bg=PANEL_ELEVADO, fg=CREMA, font=("Segoe UI", 12, "bold"), bd=0, padx=12, pady=6, cursor="hand2",
        ).pack(side="left", padx=10, pady=8)

        tk.Label(
            top, text=f"SALA 0{sid} // {nombre} ({tema_sala})",
            bg=PANEL_OSCURO, fg=color, font=("Segoe UI", 16, "bold"),
        ).pack(side="left", padx=10)

        EstrellasCanvas(top, valor=prom_sala, maximo=3, radio=10, espaciado=24, bg=PANEL_OSCURO).pack(side="right", padx=12)
        tk.Label(
            top, text=f"PROMEDIO: {prom_sala:.1f}/3.0",
            bg=PANEL_OSCURO, fg=DORADO, font=(FUENTE_MONO, 10, "bold"),
        ).pack(side="right", padx=6)

        host_lista = tk.Frame(self.contenedor, bg=FONDO_GALAXIA)
        host_lista.pack(fill="both", expand=True, padx=16, pady=(4, 10))
        _, lista = self._crear_contenedor_scroll(host_lista, bg=FONDO_GALAXIA)

        for metodo in metodos:
            num_mod = TODOS_LOS_METODOS.index(metodo) + 1
            comp = self.estado.completados.get(metodo, False)
            rec = self.estado.obtener_record(metodo)
            est = self.estado.obtener_estrellas(metodo)
            rec_txt = f"Rec: {rec:.1f}s" if rec is not None else "Sin record"
            estado_txt = "REPARADO" if comp else "PENDIENTE"
            estado_col = ESMERALDA if comp else CORAL

            fila = tk.Frame(lista, bg=PANEL_OSCURO, highlightbackground=BORDE_CALIDO, highlightthickness=2)
            fila.pack(fill="x", padx=4, pady=5)

            tk.Label(
                fila, text=f"MOD {num_mod:02d}  |  {metodo}",
                bg=PANEL_OSCURO, fg=CREMA, font=("Segoe UI", 13, "bold"), anchor="w",
            ).pack(side="left", padx=14, pady=12)

            tk.Button(
                fila, text="CONFIGURAR >",
                command=lambda m=metodo, s=sala_id: self._transicion(
                    "CARGANDO REPORTE...",
                    lambda: self.mostrar_entorno_metodo(m, s),
                ),
                bg=AMBAR, fg="#160F24", font=("Segoe UI", 12, "bold"), bd=0, padx=14, pady=7, cursor="hand2",
            ).pack(side="right", padx=12, pady=8)

            EstrellasCanvas(
                fila, valor=est if comp else 0.0, maximo=3, radio=10, espaciado=24, bg=PANEL_OSCURO,
            ).pack(side="right", padx=6)

            tk.Label(
                fila, text=f"{estado_txt} | {est if comp else 0.0:.1f}/3.0 | {rec_txt}",
                bg=PANEL_OSCURO, fg=estado_col, font=(FUENTE_MONO, 10, "bold"),
            ).pack(side="right", padx=10)

    def mostrar_entorno_metodo(self, nombre_metodo: str, sala_id: int):
        """Pantalla de briefing (Reporte de daños + Ecuaciones oficiales) previa al cronómetro."""
        self._limpiar()
        sid, nombre_sala, color_sala, _ = next(s for s in SALAS if s[0] == sala_id)
        tema_sala = TEMAS_SALAS.get(sid, "")
        num_mod = TODOS_LOS_METODOS.index(nombre_metodo) + 1
        fundamento = FUNDAMENTOS_METODOS.get(nombre_metodo, "")

        main = tk.Frame(self.contenedor, bg=FONDO_GALAXIA)
        main.pack(fill="both", expand=True, padx=18, pady=12)

        top = tk.Frame(main, bg=FONDO_GALAXIA)
        top.pack(fill="x", pady=(0, 8))

        tk.Button(
            top, text="< VOLVER A LA SALA",
            command=lambda: self._transicion("VOLVIENDO A LA SALA...", lambda: self.mostrar_sala(sala_id)),
            bg=PANEL_ELEVADO, fg=CREMA, font=("Segoe UI", 12, "bold"), bd=0, padx=12, pady=6, cursor="hand2",
        ).pack(side="left")

        tk.Label(
            top, text=f"MODULO {num_mod:02d} // {nombre_metodo.upper()}",
            bg=FONDO_GALAXIA, fg=color_sala, font=("Segoe UI", 15, "bold"),
        ).pack(side="right")

        marco_borde = tk.Frame(main, bg=PANEL_OSCURO, highlightbackground=color_sala, highlightthickness=2)
        marco_borde.pack(fill="both", expand=True)
        _, info = self._crear_contenedor_scroll(marco_borde, bg=PANEL_OSCURO)

        contenido = tk.Frame(info, bg=PANEL_OSCURO, padx=22, pady=16)
        contenido.pack(fill="both", expand=True)

        tk.Label(contenido, text=f"FALLO DETECTADO: MODULO {num_mod:02d} AVERIADO", bg=PANEL_OSCURO, fg=DORADO, font=("Segoe UI", 19, "bold"), anchor="w").pack(fill="x")
        tk.Label(contenido, text=f"SALA: {nombre_sala}  |  TEMA: {tema_sala}", bg=PANEL_OSCURO, fg=GRIS_CALIDO, font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", pady=(4, 10))

        rep_frame = tk.Frame(contenido, bg="#120E20", highlightbackground=BORDE_CALIDO, highlightthickness=1, padx=14, pady=10)
        rep_frame.pack(fill="x", pady=5)
        tk.Label(rep_frame, text="DIAGNOSTICO DEL SISTEMA", bg="#120E20", fg=color_sala, font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x")

        fallos_por_sala = {
            1: (
                f"Los sensores opticos de {nombre_sala} registraron lecturas discretas incompletas durante la maniobra orbital. "
                f"Emplea {nombre_metodo} para construir el modelo interpolante y estimar la coordenada intermedia faltante."
            ),
            2: (
                f"El balance termodinamico en {nombre_sala} depende de una ecuacion no lineal que perdio su punto de equilibrio. "
                f"Aplica {nombre_metodo} para aproximar la raiz real que estabiliza el regimen de empuje."
            ),
            3: (
                f"Las mallas de distribucion en {nombre_sala} presentan un desbalance de cargas acopladas 3x3. "
                f"Resuelve el sistema de ecuaciones lineales mediante {nombre_metodo} para restablecer los voltajes nominales."
            ),
            4: (
                f"Las mediciones experimentales de {nombre_sala} presentan dispersion por ruido electromagnetico. "
                f"Determina la curva de regresion por minimos cuadrados usando {nombre_metodo} para predecir el comportamiento del escudo."
            ),
            5: (
                f"El control criogenico de {nombre_sala} requiere cuantificar el flujo acumulado a partir de muestras discretas y funciones de caudal. "
                f"Calcula el valor de la integral definida aplicando {nombre_metodo}."
            ),
            6: (
                f"El barrido de telemetria en {nombre_sala} obedece una ecuacion diferencial ordinaria de primer orden con condicion inicial conocida. "
                f"Aproxima el estado futuro de la señal resolviendo el paso de integracion con {nombre_metodo}."
            ),
            7: (
                f"El procesador de {nombre_sala} necesita simular trayectorias dinamicas de alta precision gobernadas por ecuaciones diferenciales. "
                f"Calcula las pendientes acopladas y el siguiente estado del sistema utilizando {nombre_metodo}."
            ),
        }

        lbl_rep = tk.Label(
            rep_frame,
            text=fallos_por_sala.get(sala_id, f"Recalibra los parametros de {nombre_sala} usando {nombre_metodo}."),
            bg="#120E20", fg=CREMA, font=("Segoe UI", 13), justify="left", wraplength=780, anchor="w",
        )
        lbl_rep.pack(fill="x", pady=(4, 0))

        obj_frame = tk.Frame(contenido, bg="#120E20", highlightbackground=ESMERALDA, highlightthickness=1, padx=14, pady=10)
        obj_frame.pack(fill="x", pady=5)
        tk.Label(obj_frame, text="OBJETIVO Y REGLAS", bg="#120E20", fg=ESMERALDA, font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x")
        regla_ex = (
            "MODO EXAMEN ACTIVO: Pistas ocultas, portapapeles bloqueado y deteccion de abandono de ventana."
            if self.estado.es_modo_examen
            else "MODO PRACTICA: Pistas habilitadas. 3.0 estrellas sin errores; -0.5 estrella por cada error."
        )
        lbl_obj = tk.Label(
            obj_frame,
            text=f"Resolver paso a paso un problema de libro mediante {nombre_metodo}. {regla_ex}",
            bg="#120E20", fg=CREMA, font=("Segoe UI", 13), justify="left", wraplength=780, anchor="w",
        )
        lbl_obj.pack(fill="x", pady=(4, 0))

        esc = obtener_escenario(sala_id)
        fund_frame = tk.Frame(contenido, bg="#120E20", highlightbackground=esc["acento"], highlightthickness=1, padx=14, pady=10)
        fund_frame.pack(fill="x", pady=5)
        tk.Label(
            fund_frame,
            text=f"ECUACIONES Y FUNDAMENTO MATEMATICO  |  ESCENARIO: {esc['nombre'].upper()}",
            bg="#120E20", fg=esc["acento"], font=("Segoe UI", 13, "bold"), anchor="w",
        ).pack(fill="x")
        latex = LATEX_METODOS.get(nombre_metodo)
        foto = renderizar_formula_tk(latex, color_texto=esc["acento"], tamano_pt=15, max_ancho=820) if latex else None
        lbl_fund_txt = None
        if foto is not None:
            self._foto_briefing = foto
            tk.Label(fund_frame, image=foto, bg="#120E20").pack(anchor="w", pady=(6, 3))
        else:
            lbl_fund_txt = tk.Label(
                fund_frame,
                text=fundamento,
                bg="#120E20", fg=DORADO, font=(FUENTE_MONO, 14, "bold"), justify="left", wraplength=780, anchor="w",
            )
            lbl_fund_txt.pack(fill="x", pady=(4, 0))

        def _ajustar_briefing(e):
            lim = max(420, e.width - 96)
            lbl_rep.config(wraplength=lim)
            lbl_obj.config(wraplength=lim)
            if lbl_fund_txt is not None:
                lbl_fund_txt.config(wraplength=lim)

        contenido.bind("<Configure>", _ajustar_briefing, add="+")

        tk.Button(
            contenido, text="ABRIR ENTORNO DE CALCULO >",
            command=lambda: self._transicion(
                "GENERANDO PROBLEMA DE LIBRO...",
                lambda: self.mostrar_mision(nombre_metodo, sala_id),
            ),
            bg=AMBAR, fg="#160F24", font=("Segoe UI", 15, "bold"), bd=0, padx=24, pady=11, cursor="hand2",
        ).pack(pady=(14, 4))

    def mostrar_mision(self, nombre_metodo: str, sala_id: int):
        self._limpiar()
        consola = ConsolaMision(
            self.contenedor,
            nombre_metodo=nombre_metodo,
            estado=self.estado,
            al_volver=lambda: self._transicion(f"VOLVIENDO A SALA {sala_id}...", lambda: self.mostrar_sala(sala_id)),
        )
        consola.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # PANTALLA DE AUDITORIA / CERTIFICACION 32/32
    # ------------------------------------------------------------------

    def mostrar_certificado_final(self):
        self._limpiar()
        resumen = self.estado.generar_resumen_reporte(modo=self.estado.modo_actual)

        top = tk.Frame(self.contenedor, bg=PANEL_OSCURO, highlightbackground=DORADO, highlightthickness=2)
        top.pack(fill="x", padx=16, pady=(12, 6))

        tk.Button(
            top, text="< VOLVER AL MAPA",
            command=lambda: self._transicion("CARGANDO MAPA...", self.mostrar_mapa_nave),
            bg=PANEL_ELEVADO, fg=CREMA, font=("Segoe UI", 12, "bold"), bd=0, padx=12, pady=6, cursor="hand2",
        ).pack(side="left", padx=10, pady=8)

        tk.Label(
            top,
            text="CERTIFICACION ACADEMICA // NAVE AURORA",
            bg=PANEL_OSCURO, fg=DORADO, font=("Segoe UI", 16, "bold"),
        ).pack(side="left", padx=10)

        tk.Button(
            top, text="EXPORTAR REPORTE OFICIAL",
            command=self._exportar_reporte_dialogo,
            bg=ESMERALDA, fg=FONDO_GALAXIA, font=("Segoe UI", 12, "bold"), bd=0, padx=12, pady=6, cursor="hand2",
        ).pack(side="right", padx=10, pady=8)

        cuerpo = tk.Frame(self.contenedor, bg=FONDO_GALAXIA)
        cuerpo.pack(fill="both", expand=True, padx=16, pady=(4, 12))

        # Encabezado de alumno y resumen
        ficha = tk.Frame(cuerpo, bg=PANEL_OSCURO, highlightbackground=BORDE_CALIDO, highlightthickness=2, padx=16, pady=12)
        ficha.pack(fill="x", pady=(0, 8))

        comp_cert = self.estado.total_completados()
        estado_cert = "NAVE ESTABILIZADA (32/32 COMPLETOS)" if comp_cert == 32 else f"AVANCE PARCIAL ({resumen['modulos_completados']})"
        col_cert = ESMERALDA if comp_cert == 32 else AMBAR
        tk.Label(ficha, text=estado_cert, bg=PANEL_OSCURO, fg=col_cert, font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x")

        alum = resumen["alumno"] or "Sin especificar"
        mat = resumen["matricula"] or "Sin especificar"
        int_txt = f"HMAC VALIDA ({resumen['codigo_verificacion']})" if resumen["integridad_json_valida"] else "ADVERTENCIA INTEGRIDAD"
        lbl_ficha_det = tk.Label(
            ficha,
            text=(
                f"Alumno: {alum}  |  Matricula: {mat}  |  Perfil: {resumen['modo']}  |  "
                f"Estrellas: {resumen['estrellas_totales']}  |  Fallos: {resumen['errores_totales']}  |  "
                f"Incidentes Foco: {resumen['incidentes_foco']}  |  {int_txt}"
            ),
            bg=PANEL_OSCURO, fg=CREMA, font=(FUENTE_MONO, 10), anchor="w", wraplength=820, justify="left",
        )
        lbl_ficha_det.pack(fill="x", pady=(4, 0))
        ficha.bind("<Configure>", lambda e: lbl_ficha_det.config(wraplength=max(460, e.width - 48)), add="+")

        # Tabla resumida por las 7 Salas con estrellas reales (adaptable con scroll automatico)
        marco_borde = tk.Frame(cuerpo, bg=PANEL_OSCURO, highlightbackground=BORDE_CALIDO, highlightthickness=1)
        marco_borde.pack(fill="both", expand=True)
        _, marco_salas = self._crear_contenedor_scroll(marco_borde, bg=PANEL_OSCURO)

        for sid, nom, col, metodos in SALAS:
            comp_s = sum(1 for m in metodos if self.estado.completados.get(m))
            prom_s = self.estado.promedio_estrellas_sala(metodos)
            fila = tk.Frame(marco_salas, bg="#120E20", highlightbackground=ESMERALDA if comp_s == len(metodos) else BORDE_CALIDO, highlightthickness=1)
            fila.pack(fill="x", padx=12, pady=4)
            tk.Label(
                fila, text=f"0{sid}. {nom} ({TEMAS_SALAS.get(sid, '')})",
                bg="#120E20", fg=col, font=("Segoe UI", 12, "bold"), anchor="w",
            ).pack(side="left", padx=12, pady=8)

            EstrellasCanvas(fila, valor=prom_s, maximo=3, radio=9, espaciado=22, bg="#120E20").pack(side="right", padx=12)
            tk.Label(
                fila, text=f"{comp_s}/{len(metodos)}  |  Prom: {prom_s:.1f}/3.0",
                bg="#120E20", fg=CREMA, font=(FUENTE_MONO, 10, "bold"),
            ).pack(side="right", padx=10)


if __name__ == "__main__":
    app = NaveAuroraApp()
    app.mainloop()
