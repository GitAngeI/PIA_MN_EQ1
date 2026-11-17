"""Estado de progreso v4.0: perfiles Práctica/Examen, estrellas .5, auditoría HMAC y exportación."""

import csv
import datetime
import hashlib
import hmac
import json
import os
import shutil
import tempfile
import time
from typing import Dict, Any, Optional, List

from ..rutas import obtener_ruta_progreso
from ..ui.tema import TODOS_LOS_METODOS, SALAS

METODOS_VALIDOS = set(TODOS_LOS_METODOS)
_CLAVE_AUDITORIA = b"NaveAurora-FIME-OraliaZamora-v4-Auditoria"


def calcular_estrellas(errores_intento: int) -> float:
    """Escala académica: 3.0 sin fallos, -0.5 por error al verificar, piso 0.5 al aprobar."""
    return max(0.5, 3.0 - 0.5 * max(0, int(errores_intento)))


def _nuevo_perfil_vacio() -> Dict[str, Any]:
    return {
        "completados": {},
        "mejores_tiempos": {},
        "estrellas": {},
        "errores_totales": 0,
        "errores_por_metodo": {},
        "incidentes_foco": 0,
        "micro_pausas_so": 0,
        "incidentes_por_metodo": {},
        "seeds_completados": {},
        "bitacora_auditoria": [],
    }


def _firmar_dict(payload: Dict[str, Any]) -> str:
    crudo = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hmac.new(_CLAVE_AUDITORIA, crudo, hashlib.sha256).hexdigest()[:16].upper()


class EstadoJuego:
    def __init__(self, ruta: Optional[str] = None):
        self.ruta = os.path.abspath(ruta) if ruta else obtener_ruta_progreso()
        self.modo_actual: str = "practica"  # "practica" | "examen"
        self.alumno: str = ""
        self.matricula: str = ""
        self.integridad_verificada: bool = True
        self.ultimo_error_carga: Optional[str] = None
        self._sin_limite_tiempo: bool = False
        self.tema_visual: str = "oscuro"  # "oscuro" | "claro"
        self.perfiles: Dict[str, Dict[str, Any]] = {
            "practica": _nuevo_perfil_vacio(),
            "examen": _nuevo_perfil_vacio(),
        }
        self.cargar()

    def _perfil_activo(self) -> Dict[str, Any]:
        return self.perfiles["examen" if self.modo_actual == "examen" else "practica"]

    @property
    def completados(self) -> Dict[str, bool]:
        return self._perfil_activo()["completados"]

    @completados.setter
    def completados(self, val: Dict[str, bool]) -> None:
        self._perfil_activo()["completados"] = val

    @property
    def mejores_tiempos(self) -> Dict[str, float]:
        return self._perfil_activo()["mejores_tiempos"]

    @mejores_tiempos.setter
    def mejores_tiempos(self, val: Dict[str, float]) -> None:
        self._perfil_activo()["mejores_tiempos"] = val

    @property
    def estrellas(self) -> Dict[str, float]:
        return self._perfil_activo()["estrellas"]

    @estrellas.setter
    def estrellas(self, val: Dict[str, float]) -> None:
        self._perfil_activo()["estrellas"] = val

    @property
    def errores_totales(self) -> int:
        return int(self._perfil_activo()["errores_totales"])

    @errores_totales.setter
    def errores_totales(self, val: int) -> None:
        self._perfil_activo()["errores_totales"] = max(0, int(val))

    @property
    def incidentes_foco(self) -> int:
        return int(self._perfil_activo()["incidentes_foco"])

    @property
    def micro_pausas_so(self) -> int:
        return int(self._perfil_activo()["micro_pausas_so"])

    @property
    def es_modo_examen(self) -> bool:
        return self.modo_actual == "examen"

    @property
    def sin_limite_tiempo(self) -> bool:
        return (not self.es_modo_examen) and self._sin_limite_tiempo

    def establecer_sin_limite_tiempo(self, activo: bool) -> bool:
        """Permite modo sin límite de tiempo para revisión docente SOLO fuera de Modo Examen."""
        if self.es_modo_examen:
            self._sin_limite_tiempo = False
            return False
        self._sin_limite_tiempo = bool(activo)
        return self._sin_limite_tiempo

    def establecer_tema_visual(self, tema: str) -> str:
        """Guarda preferencia visual ('oscuro' | 'claro') sin alterar el payload HMAC."""
        self.tema_visual = "claro" if str(tema).strip().lower() == "claro" else "oscuro"
        self.guardar()
        return self.tema_visual

    @staticmethod
    def _normalizar_perfil(raw: Any) -> Dict[str, Any]:
        p = _nuevo_perfil_vacio()
        if not isinstance(raw, dict):
            return p

        comp_raw = raw.get("completados")
        if isinstance(comp_raw, dict):
            p["completados"] = {
                str(k): bool(v)
                for k, v in comp_raw.items()
                if str(k) in METODOS_VALIDOS and bool(v)
            }

        tiempos_raw = raw.get("mejores_tiempos")
        if isinstance(tiempos_raw, dict):
            for k, v in tiempos_raw.items():
                if str(k) in METODOS_VALIDOS and isinstance(v, (int, float)) and v >= 0:
                    p["mejores_tiempos"][str(k)] = round(float(v), 1)

        est_raw = raw.get("estrellas")
        if isinstance(est_raw, dict):
            for k, v in est_raw.items():
                if str(k) in METODOS_VALIDOS and isinstance(v, (int, float)):
                    val = round(float(v) * 2.0) / 2.0
                    p["estrellas"][str(k)] = max(0.0, min(3.0, val))

        for m, ok in p["completados"].items():
            if ok and m not in p["estrellas"]:
                p["estrellas"][m] = 3.0

        for campo_int in ("errores_totales", "incidentes_foco", "micro_pausas_so"):
            try:
                p[campo_int] = max(0, int(raw.get(campo_int, 0)))
            except (TypeError, ValueError):
                p[campo_int] = 0

        for campo_map in ("errores_por_metodo", "incidentes_por_metodo"):
            mp_raw = raw.get(campo_map)
            if isinstance(mp_raw, dict):
                for k, v in mp_raw.items():
                    if str(k) in METODOS_VALIDOS and isinstance(v, (int, float)):
                        p[campo_map][str(k)] = max(0, int(v))

        seeds_raw = raw.get("seeds_completados")
        if isinstance(seeds_raw, dict):
            p["seeds_completados"] = {
                str(k): str(v) for k, v in seeds_raw.items() if str(k) in METODOS_VALIDOS
            }

        bit_raw = raw.get("bitacora_auditoria")
        if isinstance(bit_raw, list):
            p["bitacora_auditoria"] = [ev for ev in bit_raw[-400:] if isinstance(ev, dict)]
        return p

    def cargar(self) -> None:
        self.perfiles = {
            "practica": _nuevo_perfil_vacio(),
            "examen": _nuevo_perfil_vacio(),
        }
        self.modo_actual = "practica"
        self.alumno = ""
        self.matricula = ""
        self.integridad_verificada = True
        self.ultimo_error_carga = None
        self.tema_visual = "oscuro"

        if not os.path.exists(self.ruta):
            return

        try:
            with open(self.ruta, "r", encoding="utf-8") as f:
                data: Any = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("El archivo de progreso no contiene un objeto JSON válido.")
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            self.ultimo_error_carga = str(exc)
            try:
                ts = int(time.time())
                shutil.copy2(self.ruta, f"{self.ruta}.{ts}.corrupt.bak")
            except OSError:
                pass
            return

        if "practica" in data or "examen" in data:
            modo = str(data.get("modo_actual", "practica"))
            self.modo_actual = "examen" if modo == "examen" else "practica"
            tema_raw = str(data.get("tema_visual", "oscuro")).strip().lower()
            self.tema_visual = "claro" if tema_raw == "claro" else "oscuro"
            self.alumno = str(data.get("alumno", "")).strip()
            self.matricula = str(data.get("matricula", "")).strip()
            self.perfiles["practica"] = self._normalizar_perfil(data.get("practica"))
            self.perfiles["examen"] = self._normalizar_perfil(data.get("examen"))

            firma_guardada = str(data.get("firma_hmac", ""))
            if firma_guardada:
                cuerpo = {
                    "version": 4,
                    "modo_actual": self.modo_actual,
                    "alumno": self.alumno,
                    "matricula": self.matricula,
                    "practica": self.perfiles["practica"],
                    "examen": self.perfiles["examen"],
                }
                self.integridad_verificada = hmac.compare_digest(firma_guardada, _firmar_dict(cuerpo))
        else:
            # Migración automática de esquema v3 plano hacia perfil 'practica'
            self.perfiles["practica"] = self._normalizar_perfil(data)

    def guardar(self) -> bool:
        """Guarda atómicamente con archivo temporal + os.replace y firma HMAC."""
        cuerpo = {
            "version": 4,
            "modo_actual": self.modo_actual,
            "alumno": self.alumno,
            "matricula": self.matricula,
            "practica": self.perfiles["practica"],
            "examen": self.perfiles["examen"],
        }
        data = dict(cuerpo)
        data["firma_hmac"] = _firmar_dict(cuerpo)
        data["tema_visual"] = self.tema_visual

        directorio = os.path.dirname(self.ruta) or "."
        tmp_path: Optional[str] = None
        try:
            os.makedirs(directorio, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(prefix=".prog_", suffix=".tmp", dir=directorio)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.ruta)
            return True
        except OSError:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            return False

    def establecer_modo(self, modo: str, alumno: Optional[str] = None, matricula: Optional[str] = None) -> None:
        self.modo_actual = "examen" if modo == "examen" else "practica"
        if self.es_modo_examen:
            self._sin_limite_tiempo = False
        if alumno is not None:
            self.alumno = alumno.strip()
        if matricula is not None:
            self.matricula = matricula.strip().upper()
        self.guardar()

    def iniciar_nuevo_examen(self, alumno: str, matricula: str) -> None:
        self.modo_actual = "examen"
        self._sin_limite_tiempo = False
        self.alumno = alumno.strip()
        self.matricula = matricula.strip().upper()
        self.perfiles["examen"] = _nuevo_perfil_vacio()
        self.guardar()

    def registrar_victoria(
        self,
        nombre_metodo: str,
        tiempo_seg: float,
        errores_intento: int = 0,
        seed_id: str = "",
        plantilla_id: str = "",
    ) -> bool:
        """Registra módulo completado, mejor calificación en estrellas y si hubo nuevo récord."""
        perfil = self._perfil_activo()
        perfil["completados"][nombre_metodo] = True

        est_ganadas = calcular_estrellas(errores_intento)
        prev_est = perfil["estrellas"].get(nombre_metodo, 0.0)
        if est_ganadas > prev_est:
            perfil["estrellas"][nombre_metodo] = est_ganadas

        if seed_id:
            perfil["seeds_completados"][nombre_metodo] = seed_id

        tiempo_red = round(max(0.0, float(tiempo_seg)), 1)
        prev = perfil["mejores_tiempos"].get(nombre_metodo)
        es_record = prev is None or tiempo_red < prev
        if es_record:
            perfil["mejores_tiempos"][nombre_metodo] = tiempo_red

        perfil["bitacora_auditoria"].append({
            "evento": "victoria",
            "metodo": nombre_metodo,
            "estrellas": est_ganadas,
            "errores": int(errores_intento),
            "tiempo_seg": tiempo_red,
            "seed_id": seed_id,
            "plantilla_id": plantilla_id,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        })
        perfil["bitacora_auditoria"] = perfil["bitacora_auditoria"][-400:]
        self.guardar()
        return es_record

    def registrar_error(self, nombre_metodo: Optional[str] = None) -> None:
        perfil = self._perfil_activo()
        perfil["errores_totales"] += 1
        if nombre_metodo and nombre_metodo in METODOS_VALIDOS:
            perfil["errores_por_metodo"][nombre_metodo] = perfil["errores_por_metodo"].get(nombre_metodo, 0) + 1
        self.guardar()

    def registrar_micro_pausa(
        self,
        nombre_metodo: str,
        seed_id: str = "",
        duracion_s: float = 0.0,
        paso: int = 0,
    ) -> None:
        perfil = self._perfil_activo()
        perfil["micro_pausas_so"] += 1
        perfil["bitacora_auditoria"].append({
            "evento": "micro_pausa_so",
            "metodo": nombre_metodo,
            "duracion_s": round(float(duracion_s), 2),
            "paso": int(paso),
            "seed_id": seed_id,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        })
        perfil["bitacora_auditoria"] = perfil["bitacora_auditoria"][-400:]
        self.guardar()

    def registrar_incidente_foco(
        self,
        nombre_metodo: str,
        seed_id: str = "",
        tipo: str = "salida_prolongada",
        duracion_s: float = 0.0,
        paso: int = 0,
    ) -> None:
        perfil = self._perfil_activo()
        perfil["incidentes_foco"] += 1
        perfil["incidentes_por_metodo"][nombre_metodo] = perfil["incidentes_por_metodo"].get(nombre_metodo, 0) + 1
        perfil["bitacora_auditoria"].append({
            "evento": "incidente_foco",
            "tipo": tipo,
            "metodo": nombre_metodo,
            "duracion_s": round(float(duracion_s), 2),
            "paso": int(paso),
            "seed_id": seed_id,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        })
        perfil["bitacora_auditoria"] = perfil["bitacora_auditoria"][-400:]
        self.guardar()

    def reiniciar(self, alcance: str = "activo") -> None:
        """Reinicia el avance en 0 ('activo', 'practica' o 'todo') conservando auditoría si aplica."""
        if alcance == "todo":
            self.perfiles["practica"] = _nuevo_perfil_vacio()
            self.perfiles["examen"] = _nuevo_perfil_vacio()
        elif alcance == "practica":
            self.perfiles["practica"] = _nuevo_perfil_vacio()
        else:
            self.perfiles[self.modo_actual] = _nuevo_perfil_vacio()
        self.guardar()

    def obtener_record(self, nombre_metodo: str) -> Optional[float]:
        return self.mejores_tiempos.get(nombre_metodo)

    def obtener_estrellas(self, nombre_metodo: str) -> float:
        """Retorna 0.0 si no está completado, o 0.5..3.0 según desempeño."""
        if not self.completados.get(nombre_metodo, False):
            return 0.0
        return self.estrellas.get(nombre_metodo, 0.0)

    def promedio_estrellas_sala(self, metodos: List[str]) -> float:
        """Promedio de estrellas (0.0..3.0) de una sala cuantizado a pasos de 0.5."""
        if not metodos:
            return 0.0
        total = sum(self.obtener_estrellas(m) for m in metodos)
        return round((total / len(metodos)) * 2.0) / 2.0

    def total_completados(self) -> int:
        return sum(1 for m in TODOS_LOS_METODOS if self.completados.get(m))

    def total_estrellas(self) -> float:
        return round(sum(self.obtener_estrellas(m) for m in TODOS_LOS_METODOS), 1)

    def generar_resumen_reporte(self, modo: Optional[str] = None) -> Dict[str, Any]:
        clave_modo = "examen" if (modo or self.modo_actual) == "examen" else "practica"
        perfil = self.perfiles[clave_modo]
        filas = []
        for sid, nombre_sala, _, metodos in SALAS:
            for m in metodos:
                comp = bool(perfil["completados"].get(m, False))
                est = perfil["estrellas"].get(m, 0.0) if comp else 0.0
                filas.append({
                    "sala": f"0{sid}. {nombre_sala}",
                    "metodo": m,
                    "estado": "APROBADO" if comp else "PENDIENTE",
                    "estrellas": est,
                    "mejor_tiempo_seg": perfil["mejores_tiempos"].get(m),
                    "errores": perfil["errores_por_metodo"].get(m, 0),
                    "incidentes_foco": perfil["incidentes_por_metodo"].get(m, 0),
                    "seed_id": perfil["seeds_completados"].get(m, ""),
                })
        comp_tot = sum(1 for f in filas if f["estado"] == "APROBADO")
        est_tot = round(sum(f["estrellas"] for f in filas), 1)
        resumen = {
            "fecha_generacion": datetime.datetime.now().isoformat(timespec="seconds"),
            "modo": clave_modo.upper(),
            "alumno": self.alumno or "SIN REGISTRO",
            "matricula": self.matricula or "N/A",
            "modulos_completados": f"{comp_tot}/32",
            "estrellas_totales": f"{est_tot:.1f}/96.0",
            "errores_totales": int(perfil["errores_totales"]),
            "incidentes_foco": int(perfil["incidentes_foco"]),
            "micro_pausas_so": int(perfil["micro_pausas_so"]),
            "integridad_json_valida": self.integridad_verificada,
            "modulos": filas,
        }
        resumen["codigo_verificacion"] = _firmar_dict(resumen)
        return resumen

    def exportar_reporte(self, ruta_destino: str, formato: str = "txt", modo: Optional[str] = None) -> str:
        """Exporta el Reporte Oficial de Auditoría para la Inge en TXT, CSV o JSON."""
        rep = self.generar_resumen_reporte(modo=modo)
        fmt = formato.lower().strip(".")
        if fmt == "json":
            with open(ruta_destino, "w", encoding="utf-8") as f:
                json.dump(rep, f, ensure_ascii=False, indent=2)
            return ruta_destino

        if fmt == "csv":
            with open(ruta_destino, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ALUMNO", rep["alumno"], "MATRICULA", rep["matricula"], "MODO", rep["modo"], "CODIGO", rep["codigo_verificacion"]])
                writer.writerow(["COMPLETADOS", rep["modulos_completados"], "ESTRELLAS", rep["estrellas_totales"], "ERRORES", rep["errores_totales"], "INCIDENTES_FOCO", rep["incidentes_foco"]])
                writer.writerow([])
                writer.writerow(["Sala", "Metodo", "Estado", "Estrellas", "MejorTiempo(s)", "Errores", "IncidentesFoco", "SeedID"])
                for m in rep["modulos"]:
                    writer.writerow([
                        m["sala"], m["metodo"], m["estado"], f"{m['estrellas']:.1f}",
                        f"{m['mejor_tiempo_seg']:.1f}" if m["mejor_tiempo_seg"] is not None else "",
                        m["errores"], m["incidentes_foco"], m["seed_id"],
                    ])
            return ruta_destino

        # TXT estructurado legible para entregar a la profesora
        lineas = [
            "=" * 78,
            "MISION NUMERICA v4.0 // NAVE AURORA - REPORTE OFICIAL DE AUDITORIA ACADEMICA",
            "Análisis Numérico - FIME UANL | Formulario Oficial Ing. Oralia Zamora Pequeño",
            "=" * 78,
            f"Fecha             : {rep['fecha_generacion']}",
            f"Modo de Sesion    : {rep['modo']}",
            f"Estudiante        : {rep['alumno']}",
            f"Matricula         : {rep['matricula']}",
            f"Modulos Aprobados : {rep['modulos_completados']}",
            f"Estrellas Totales : {rep['estrellas_totales']}",
            f"Errores Totales   : {rep['errores_totales']}",
            f"Incidentes Foco   : {rep['incidentes_foco']} (Micro-pausas SO <=2.5s: {rep['micro_pausas_so']})",
            f"Integridad Guard  : {'VERIFICADA' if rep['integridad_json_valida'] else 'ALTERACION DETECTADA'}",
            f"Codigo Verif. HMAC: {rep['codigo_verificacion']}",
            "-" * 78,
            f"{'METODO':<42} {'EST':>5} {'SEG':>7} {'ERR':>4} {'FOC':>4} {'SEED':>10}",
            "-" * 78,
        ]
        for m in rep["modulos"]:
            t_str = f"{m['mejor_tiempo_seg']:.1f}" if m["mejor_tiempo_seg"] is not None else "---"
            lineas.append(
                f"{m['metodo'][:41]:<42} {m['estrellas']:>5.1f} {t_str:>7} {m['errores']:>4} {m['incidentes_foco']:>4} {m['seed_id'][:10]:>10}"
            )
        lineas.append("=" * 78)
        with open(ruta_destino, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))
        return ruta_destino
