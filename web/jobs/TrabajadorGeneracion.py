"""Trabajador de generación: un ítem a la vez, con lease y latido.

Reserva con ``FOR UPDATE SKIP LOCKED``, construye fuera de toda transacción,
sube STL y JSON al bucket y confirma solo si conserva el lease. Un hilo renueva
el lease cada ``latido_s`` de ``config/trabajador.yaml``; si lo pierde, el
resultado no se confirma.
"""

from __future__ import annotations

import os
import platform
import socket
import subprocess
import threading
import time
import uuid
from pathlib import Path

from GenerateModelsApp.Excepciones import OrtesisLabError
from GenerateModelsApp.util.Utilidades import Registro
from web.ConfiguracionBackend import ConfiguracionBackend
from web.enums import TipoAsset
from web.persistence.Contratos import ErrorPersistencia, TrabajoReservado, UsuarioAutenticado
from web.services.ContextoUsuario import ContextoUsuario
from web.services.GeneradorGeometrico import VERSION, GeneradorGeometrico
from web.services.ServicioImports import ServicioImports
from web.services.ServicioLotes import ServicioLotes
from web.storage.AlmacenamientoPrivado import Almacen

from .ConciliadorArchivos import ConciliadorArchivos

_CONFIG = ConfiguracionBackend.Cargar("trabajador")
LEASE_S = _CONFIG["lease_s"]
LATIDO_S = _CONFIG["latido_s"]
SUPERVISION_S = _CONFIG["supervision_s"]
CONCILIACION_S = _CONFIG["conciliacion_s"]


def _Revision() -> str:
    try:
        salida = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5,
            cwd=Path(__file__).resolve().parents[2],
        )
        return salida.stdout.strip() or "desconocida"
    except (OSError, subprocess.SubprocessError):
        return "desconocida"


class TrabajadorGeneracion:
    def __init__(self, identificador: str | None = None):
        self.identificador = identificador or f"{socket.gethostname()}:{os.getpid()}:{uuid.uuid4().hex[:6]}"
        self.revision = _Revision()
        self.runtime = {"python": platform.python_version(), "plataforma": platform.platform()}
        self.registro = Registro.Obtener("trabajador")

    def Ciclo(self) -> bool:
        """Procesa un ítem si hay alguno disponible. Devuelve si procesó."""
        trabajo = ServicioLotes.Reservar(self.identificador, LEASE_S, VERSION, self.revision, self.runtime)
        if trabajo is None:
            return False
        self.Procesar(trabajo)
        return True

    def Procesar(self, trabajo: TrabajoReservado) -> None:
        inicio = time.monotonic()
        perdido = threading.Event()
        parar = threading.Event()

        def latir() -> None:
            while not parar.wait(LATIDO_S):
                try:
                    if not ServicioLotes.Renovar(trabajo, LEASE_S):
                        perdido.set()
                        return
                except ErrorPersistencia:
                    self.registro.warning("No se pudo renovar el lease de %s.", trabajo.item_id)

        latido = threading.Thread(target=latir, name=f"latido-{trabajo.item_id}", daemon=True)
        latido.start()
        duracion = lambda: int((time.monotonic() - inicio) * 1000)  # noqa: E731
        try:
            usuario = UsuarioAutenticado(trabajo.user_id, "", None, trabajo.project_id)
            with ContextoUsuario.Activar(usuario):
                resultado, stl, parametros = GeneradorGeometrico.Construir(
                    trabajo.parameters,
                    ServicioImports.NombreSuperficie(trabajo.normalized_asset_id),
                    trabajo.auto_scale,
                    trabajo.material_snapshot,
                )
            if perdido.is_set():
                self.registro.warning("Lease perdido para %s; no se publica.", trabajo.item_id)
                return
            if ServicioLotes.CancelacionPedida(trabajo):
                ServicioLotes.CerrarCancelado(trabajo, duracion())
                return
            stl_id, json_id = uuid.uuid4(), uuid.uuid4()
            clave_stl = Almacen.Clave(trabajo.user_id, stl_id, stl_publico=True)
            clave_json = Almacen.Clave(trabajo.user_id, json_id)
            sha_stl, sha_json = Almacen.Sha256(stl), Almacen.Sha256(parametros)
            ServicioLotes.RegistrarSalidas(
                trabajo,
                [
                    (stl_id, clave_stl, TipoAsset.RESULT_STL, "model/stl", len(stl), sha_stl),
                    (json_id, clave_json, TipoAsset.EXPORT_JSON, "application/json", len(parametros), sha_json),
                ],
            )
            almacen = Almacen.Actual()
            url_stl = almacen.Publicar(clave_stl, stl, "model/stl", sha_stl, f"ortesis-{stl_id.hex[:8]}.stl")
            url_json = almacen.Publicar(clave_json, parametros, "application/json", sha_json)
            if not ServicioLotes.Confirmar(trabajo, resultado, (stl_id, url_stl), (json_id, url_json), duracion()):
                self.registro.warning("Otro intento ganó %s; los objetos quedan para la conciliación.", trabajo.item_id)
        except OrtesisLabError as exc:
            ServicioLotes.Fallar(trabajo, type(exc).__name__, str(exc), False, duracion())
        except ErrorPersistencia as exc:
            self.registro.warning("Fallo de infraestructura en %s: %s", trabajo.item_id, exc)
            self._FallarSinPerder(trabajo, type(exc).__name__, str(exc), True, duracion())
        except Exception as exc:  # noqa: BLE001 - un ítem roto no detiene el trabajador
            self.registro.exception("Fallo no previsto en %s", trabajo.item_id)
            self._FallarSinPerder(trabajo, "error_interno", str(exc) or type(exc).__name__, False, duracion())
        finally:
            parar.set()
            latido.join(timeout=5)

    def _FallarSinPerder(self, trabajo, codigo, mensaje, reintentable, duracion_ms) -> None:
        # Si la base tampoco responde, el lease vence y el supervisor reencola el ítem.
        try:
            ServicioLotes.Fallar(trabajo, codigo, mensaje, reintentable, duracion_ms)
        except ErrorPersistencia:
            self.registro.warning("No se pudo registrar el fallo de %s; vencerá su lease.", trabajo.item_id)

    def Ejecutar(self, detener: threading.Event, espera_s: float = 2.0) -> None:
        """Bucle principal: supervisa leases, concilia archivos y procesa la cola."""
        self.registro.info("Trabajador %s en marcha (revisión %s).", self.identificador, self.revision)
        ultima_supervision = ultima_conciliacion = 0.0
        conciliador = ConciliadorArchivos()
        while not detener.is_set():
            ahora = time.monotonic()
            try:
                if ahora - ultima_supervision >= SUPERVISION_S:
                    ultima_supervision = ahora
                    vencidos = ServicioLotes.AbandonarVencidos()
                    if vencidos:
                        self.registro.info("%s ítem(s) con lease vencido vuelven a la cola.", vencidos)
                if ahora - ultima_conciliacion >= CONCILIACION_S:
                    ultima_conciliacion = ahora
                    self.registro.info("Conciliación: %s", conciliador.Ejecutar())
                if self.Ciclo():
                    continue
            except ErrorPersistencia as exc:
                self.registro.warning("Infraestructura no disponible: %s", exc)
            detener.wait(espera_s)
        self.registro.info("Trabajador %s detenido.", self.identificador)
