"""Admisión de lotes, progreso y transiciones del trabajador.

La admisión es idempotente por ``request_id`` + ``request_sha256`` y aplica
las cuotas bajo un advisory lock del usuario. El trabajador solo confirma un
resultado si conserva el ``lease_token`` del ítem.
"""

from __future__ import annotations

import time
import uuid
from uuid import UUID

from web.ConfiguracionBackend import ConfiguracionBackend
from web.enums import AlcanceGeometria, EstadoImport, EstadoIntento, FormatoExport, ModoLote, TipoEvento
from web.persistence.ConexionPostgres import ConexionPostgres
from web.persistence.Contratos import (
    MAXIMO_INTENTOS,
    MAXIMO_ITEMS_LOTE,
    MAXIMO_LOTES_PENDIENTES,
    VERSION_EXPORTADOR,
    AccesoDenegado,
    CuotaExcedida,
    LoteDTO,
    ProgresoLote,
    ResultadoGeometrico,
    SolicitudIdempotenteEnConflicto,
    SolicitudLote,
    TrabajoReservado,
    UsuarioAutenticado,
)
from web.persistence.repositorios import (
    RepositorioAssets,
    RepositorioHistorial,
    RepositorioImports,
    RepositorioLotes,
    RepositorioResultados,
    RepositorioVersiones,
)

from .ServicioVersiones import ServicioVersiones

ESPERA_REINTENTO_S = ConfiguracionBackend.Cargar("persistencia")["lotes"]["espera_reintento_s"]


class ServicioLotes:
    @staticmethod
    def HuellaSolicitud(solicitud: SolicitudLote) -> str:
        return ServicioVersiones.Sha(
            {
                "import_id": str(solicitud.import_id),
                "mode": solicitud.mode,
                "definition": solicitud.definition,
                "variantes": solicitud.variantes,
                "auto_scale": bool(solicitud.auto_scale),
                "parent_version_id": str(solicitud.parent_version_id or ""),
                "version_ids": [str(valor) for valor in solicitud.version_ids or []],
            }
        )

    @staticmethod
    def Solicitar(usuario: UsuarioAutenticado, solicitud: SolicitudLote) -> LoteDTO:
        """Entrada: variantes ya validadas. Proceso: crea versiones, lote e ítems
        en una transacción. Salida: lote nuevo o el ya registrado con el mismo
        request_id. Errores: conflicto idempotente, cuota, import ajeno."""
        reintento = solicitud.mode == ModoLote.RETRY
        total = len(solicitud.version_ids or []) if reintento else len(solicitud.variantes)
        if not 1 <= total <= MAXIMO_ITEMS_LOTE:
            raise CuotaExcedida(f"Un lote admite de 1 a {MAXIMO_ITEMS_LOTE} variantes.")
        huella = ServicioLotes.HuellaSolicitud(solicitud)
        user_id = usuario.user_id

        def admitir(conexion) -> LoteDTO:
            RepositorioLotes.BloquearUsuario(conexion, user_id)
            previo = RepositorioLotes.PorRequest(conexion, user_id, solicitud.request_id)
            if previo is not None:
                if previo["request_sha256"] != huella:
                    raise SolicitudIdempotenteEnConflicto()
                return RepositorioLotes._Dto(previo)
            if RepositorioLotes.ContarPendientes(conexion, user_id) >= MAXIMO_LOTES_PENDIENTES:
                raise CuotaExcedida(
                    f"Ya hay {MAXIMO_LOTES_PENDIENTES} lotes en espera. Espere a que termine uno o cancélelo."
                )
            importacion = RepositorioImports.Obtener(conexion, user_id, solicitud.import_id)
            if importacion.status != EstadoImport.READY:
                raise AccesoDenegado("La superficie todavía no está lista.")
            project_id = importacion.project_id
            if reintento:
                versiones = [RepositorioVersiones.Obtener(conexion, user_id, v) for v in solicitud.version_ids or []]
                if any(version.project_id != project_id for version in versiones):
                    raise AccesoDenegado("Las versiones no pertenecen a ese proyecto.")
                version_ids = [version.id for version in versiones]
            else:
                version_ids = ServicioVersiones.Insertar(
                    conexion, usuario, project_id, solicitud.import_id, solicitud.variantes, solicitud.auto_scale,
                    solicitud.parent_version_id, solicitud.change_note,
                )
            batch_id = uuid.uuid4()
            RepositorioLotes.InsertarLote(
                conexion, user_id, project_id, batch_id, solicitud.request_id, huella, solicitud.mode,
                solicitud.definition, total,
            )
            for posicion, version_id in enumerate(version_ids):
                RepositorioLotes.InsertarItem(conexion, user_id, project_id, batch_id, version_id, posicion, MAXIMO_INTENTOS)
            RepositorioHistorial.Evento(
                conexion, user_id, project_id, TipoEvento.BATCH_QUEUED, batch_id=batch_id,
                payload={"mode": solicitud.mode, "total_items": total},
            )
            return RepositorioLotes.Obtener(conexion, user_id, batch_id)

        return ConexionPostgres.Ejecutar(admitir)

    @staticmethod
    def Progreso(usuario: UsuarioAutenticado, batch_id: UUID) -> ProgresoLote:
        def leer(conexion) -> ProgresoLote:
            lote = RepositorioLotes.Obtener(conexion, usuario.user_id, batch_id)
            return ProgresoLote(lote, RepositorioLotes.Items(conexion, usuario.user_id, batch_id))

        return ConexionPostgres.Ejecutar(leer)

    @staticmethod
    def Ultimo(usuario: UsuarioAutenticado) -> ProgresoLote | None:
        """Último lote del usuario: la página lo recupera al recargar o reiniciar."""

        def leer(conexion) -> ProgresoLote | None:
            lote = RepositorioLotes.Ultimo(conexion, usuario.user_id)
            if lote is None:
                return None
            return ProgresoLote(lote, RepositorioLotes.Items(conexion, usuario.user_id, lote.id))

        return ConexionPostgres.Ejecutar(leer)

    @staticmethod
    def Esperar(usuario: UsuarioAutenticado, batch_id: UUID, limite_s: float, intervalo_s: float = 1.0) -> ProgresoLote:
        final = time.monotonic() + limite_s
        while True:
            progreso = ServicioLotes.Progreso(usuario, batch_id)
            if not progreso.abierto or time.monotonic() >= final:
                return progreso
            time.sleep(intervalo_s)

    @staticmethod
    def Cancelar(usuario: UsuarioAutenticado, batch_id: UUID) -> bool:
        def cancelar(conexion) -> bool:
            lote = RepositorioLotes.Obtener(conexion, usuario.user_id, batch_id, bloquear=True)
            if not RepositorioLotes.SolicitarCancelacion(conexion, usuario.user_id, batch_id):
                return False
            RepositorioHistorial.Evento(conexion, usuario.user_id, lote.project_id, TipoEvento.BATCH_CANCEL_REQUESTED, batch_id=batch_id)
            RepositorioLotes.Recalcular(conexion, usuario.user_id, batch_id)
            return True

        return ConexionPostgres.Ejecutar(cancelar)

    # Lado del trabajador.

    @staticmethod
    def Reservar(trabajador_id: str, lease_s: int, generador: str, revision: str, runtime: dict) -> TrabajoReservado | None:
        return ConexionPostgres.Ejecutar(
            lambda conexion: RepositorioLotes.ReservarPendiente(conexion, trabajador_id, lease_s, generador, revision, runtime)
        )

    @staticmethod
    def Renovar(trabajo: TrabajoReservado, lease_s: int) -> bool:
        return ConexionPostgres.Ejecutar(lambda conexion: RepositorioLotes.RenovarLease(conexion, trabajo, lease_s))

    @staticmethod
    def CancelacionPedida(trabajo: TrabajoReservado) -> bool:
        return ConexionPostgres.Ejecutar(lambda conexion: RepositorioLotes.CancelacionPedida(conexion, trabajo))

    @staticmethod
    def RegistrarSalidas(trabajo: TrabajoReservado, salidas: list[tuple[UUID, str, str, str, int, str]]) -> None:
        """Filas ``staged`` de los objetos que el trabajador va a subir:
        (asset_id, clave, kind, media_type, tamaño, sha256)."""

        def registrar(conexion) -> None:
            for asset_id, clave, kind, media, tamano, sha in salidas:
                RepositorioAssets.CrearStaged(conexion, trabajo.user_id, asset_id, clave, kind, None, media, tamano, sha)

        ConexionPostgres.Ejecutar(registrar)

    @staticmethod
    def Confirmar(
        trabajo: TrabajoReservado,
        resultado: ResultadoGeometrico,
        stl: tuple[UUID, str],
        parametros: tuple[UUID, str],
        duracion_ms: int,
    ) -> bool:
        """Publica resultado y exports si el lease sigue vigente. Devuelve False
        si otro intento ya tomó el ítem; sus objetos quedan para el conciliador."""

        def confirmar(conexion) -> bool:
            if not RepositorioLotes.BloquearVigente(conexion, trabajo):
                return False
            for asset_id, url in (stl, parametros):
                RepositorioAssets.MarcarListo(conexion, trabajo.user_id, asset_id, url)
            result_id = RepositorioResultados.Insertar(conexion, trabajo, resultado, AlcanceGeometria.PRE_VOXEL_SHELL)
            export_id = RepositorioResultados.InsertarExport(
                conexion, trabajo.user_id, result_id, stl[0], FormatoExport.STL_BINARY, VERSION_EXPORTADOR
            )
            RepositorioResultados.InsertarExport(
                conexion, trabajo.user_id, result_id, parametros[0], FormatoExport.PARAMETERS_JSON, VERSION_EXPORTADOR
            )
            RepositorioLotes.Exito(conexion, trabajo, resultado, duracion_ms)
            RepositorioHistorial.Evento(
                conexion, trabajo.user_id, trabajo.project_id, TipoEvento.RESULT_READY, version_id=trabajo.version_id,
                batch_id=trabajo.batch_id, attempt_id=trabajo.attempt_id, export_id=export_id,
                payload={"volume_mm3": resultado.volume_mm3, "weight_g": resultado.weight_g},
            )
            RepositorioLotes.Recalcular(conexion, trabajo.user_id, trabajo.batch_id)
            return True

        return ConexionPostgres.Ejecutar(confirmar)

    @staticmethod
    def Fallar(trabajo: TrabajoReservado, codigo: str, mensaje: str, reintentable: bool, duracion_ms: int) -> str | None:
        def fallar(conexion) -> str | None:
            if not RepositorioLotes.BloquearVigente(conexion, trabajo):
                return None
            RepositorioLotes.CerrarIntento(conexion, trabajo, EstadoIntento.FAILED, duracion_ms, codigo, mensaje, reintentable)
            espera = ESPERA_REINTENTO_S * (2 ** (trabajo.attempt_number - 1))
            estado = RepositorioLotes.Liberar(conexion, trabajo.user_id, trabajo.item_id, reintentable, espera)
            RepositorioHistorial.Evento(
                conexion, trabajo.user_id, trabajo.project_id, TipoEvento.ATTEMPT_FAILED, version_id=trabajo.version_id,
                batch_id=trabajo.batch_id, attempt_id=trabajo.attempt_id,
                payload={"attempt_number": trabajo.attempt_number, "error_code": codigo[:80], "retryable": reintentable},
            )
            RepositorioLotes.Recalcular(conexion, trabajo.user_id, trabajo.batch_id)
            return estado

        return ConexionPostgres.Ejecutar(fallar)

    @staticmethod
    def CerrarCancelado(trabajo: TrabajoReservado, duracion_ms: int) -> None:
        def cerrar(conexion) -> None:
            if not RepositorioLotes.BloquearVigente(conexion, trabajo):
                return
            RepositorioLotes.CerrarIntento(conexion, trabajo, EstadoIntento.CANCELLED, duracion_ms)
            RepositorioLotes.Liberar(conexion, trabajo.user_id, trabajo.item_id, False, 0)
            RepositorioLotes.Recalcular(conexion, trabajo.user_id, trabajo.batch_id)

        ConexionPostgres.Ejecutar(cerrar)

    @staticmethod
    def AbandonarVencidos() -> int:
        """Devuelve a la cola los ítems cuyo trabajador dejó de renovar el lease."""

        def abandonar(conexion) -> int:
            filas = RepositorioLotes.Vencidos(conexion)
            for fila in filas:
                attempt_id = RepositorioLotes.AbandonarIntento(conexion, fila["user_id"], fila["id"])
                RepositorioLotes.Liberar(conexion, fila["user_id"], fila["id"], True, 0)
                RepositorioHistorial.Evento(
                    conexion, fila["user_id"], fila["project_id"], TipoEvento.ATTEMPT_ABANDONED, version_id=fila["version_id"],
                    batch_id=fila["batch_id"], attempt_id=attempt_id, payload={"attempt_count": fila["attempt_count"]},
                )
                RepositorioLotes.Recalcular(conexion, fila["user_id"], fila["batch_id"])
            return len(filas)

        return ConexionPostgres.Ejecutar(abandonar)
