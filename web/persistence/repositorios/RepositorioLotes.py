"""Lotes, ítems y cola del trabajador: admisión, reserva, lease y cierre."""

from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from sqlalchemy import BigInteger, Text, and_, cast, extract, func, insert, select, update

from web.enums import LOTES_ABIERTOS, EstadoIntento, EstadoItem, EstadoLote, EstadoUsuario, TipoEvento

from ..Contratos import ItemLote, LoteDTO, ResultadoGeometrico, TrabajoReservado
from .Consultas import (
    AHORA,
    IMPORTS,
    INTENTOS,
    ITEMS,
    LOTES,
    USUARIOS,
    VERSIONES,
    ColumnasResultado,
    ConStlGanador,
    Segundos,
    UltimoError,
)
from .RepositorioBase import RepositorioBase
from .RepositorioHistorial import RepositorioHistorial
from .RepositorioResultados import RepositorioResultados


class RepositorioLotes(RepositorioBase):
    TABLA = LOTES
    DTO = LoteDTO

    @staticmethod
    def _ClaveBloqueo(user_id: UUID) -> Any:
        return func.hashtextextended(cast(str(user_id), Text), 0)

    @staticmethod
    def BloquearUsuario(conexion, user_id: UUID) -> None:
        # Serializa admisión y reserva por usuario sin bloquear filas de dominio.
        conexion.execute(select(func.pg_advisory_xact_lock(RepositorioLotes._ClaveBloqueo(user_id))))

    @staticmethod
    def IntentarBloquearUsuario(conexion, user_id: UUID) -> bool:
        return bool(
            conexion.execute(select(func.pg_try_advisory_xact_lock(RepositorioLotes._ClaveBloqueo(user_id)))).scalar_one()
        )

    @classmethod
    def PorRequest(cls, conexion, user_id: UUID, request_id: UUID) -> dict | None:
        return cls._Uno(conexion, select(LOTES).where(LOTES.c.user_id == user_id, LOTES.c.request_id == request_id))

    @staticmethod
    def ContarPendientes(conexion, user_id: UUID) -> int:
        return int(
            conexion.execute(
                select(func.count())
                .select_from(LOTES)
                .where(LOTES.c.user_id == user_id, LOTES.c.status.in_(LOTES_ABIERTOS))
            ).scalar_one()
        )

    @staticmethod
    def InsertarLote(
        conexion,
        user_id: UUID,
        project_id: UUID,
        batch_id: UUID,
        request_id: UUID,
        request_sha256: str,
        modo: str,
        definicion: dict,
        total: int,
    ) -> None:
        conexion.execute(
            insert(LOTES).values(
                id=batch_id,
                user_id=user_id,
                project_id=project_id,
                request_id=request_id,
                request_sha256=request_sha256,
                mode=modo,
                definition=definicion,
                total_items=total,
            )
        )

    @staticmethod
    def InsertarItem(
        conexion, user_id: UUID, project_id: UUID, batch_id: UUID, version_id: UUID, posicion: int, maximo: int
    ) -> UUID:
        item_id = uuid.uuid4()
        conexion.execute(
            insert(ITEMS).values(
                id=item_id,
                user_id=user_id,
                project_id=project_id,
                batch_id=batch_id,
                version_id=version_id,
                position=posicion,
                max_attempts=maximo,
            )
        )
        return item_id

    @classmethod
    def Obtener(cls, conexion, user_id: UUID, batch_id: UUID, bloquear: bool = False) -> LoteDTO:
        return cls._DelUsuario(conexion, user_id, LOTES.c.id == batch_id, bloquear=bloquear)

    @classmethod
    def Ultimo(cls, conexion, user_id: UUID) -> LoteDTO | None:
        return cls._Opcional(
            conexion,
            select(LOTES)
            .where(LOTES.c.user_id == user_id)
            .order_by(LOTES.c.created_at.desc(), LOTES.c.id.desc())
            .limit(1),
        )

    @classmethod
    def Items(cls, conexion, user_id: UUID, batch_id: UUID) -> list[ItemLote]:
        # Ítems del lote con su versión, resultado ganador y STL.
        ganador = INTENTOS.alias("wa")
        origen = ITEMS.join(
            VERSIONES, and_(VERSIONES.c.id == ITEMS.c.version_id, VERSIONES.c.user_id == ITEMS.c.user_id)
        ).outerjoin(ganador, and_(ganador.c.id == ITEMS.c.winning_attempt_id, ganador.c.user_id == ITEMS.c.user_id))
        filas = cls._Todos(
            conexion,
            select(
                ITEMS.c.id,
                ITEMS.c.batch_id,
                ITEMS.c.position,
                ITEMS.c.status,
                ITEMS.c.attempt_count,
                VERSIONES.c.id.label("version_id"),
                VERSIONES.c.version_number,
                VERSIONES.c.parameters,
                UltimoError(),
                *ColumnasResultado(ganador),
            )
            .select_from(ConStlGanador(origen))
            .where(ITEMS.c.user_id == user_id, ITEMS.c.batch_id == batch_id)
            .order_by(ITEMS.c.position),
        )
        return [cls._Item(fila) for fila in filas]

    @staticmethod
    def SolicitarCancelacion(conexion, user_id: UUID, batch_id: UUID) -> bool:
        resultado = conexion.execute(
            update(LOTES)
            .where(
                LOTES.c.user_id == user_id,
                LOTES.c.id == batch_id,
                LOTES.c.cancel_requested_at.is_(None),
                LOTES.c.status.in_(LOTES_ABIERTOS),
            )
            .values(cancel_requested_at=AHORA)
        )
        if resultado.rowcount == 0:
            return False
        conexion.execute(
            update(ITEMS)
            .where(ITEMS.c.user_id == user_id, ITEMS.c.batch_id == batch_id, ITEMS.c.status == EstadoItem.QUEUED)
            .values(status=EstadoItem.CANCELLED, updated_at=AHORA)
        )
        return True

    @classmethod
    def Recalcular(cls, conexion, user_id: UUID, batch_id: UUID) -> str:
        # Cierra el lote solo cuando no quedan ítems pendientes ni en ejecución.
        lote = cls._Uno(
            conexion,
            select(LOTES.c.status, LOTES.c.cancel_requested_at, LOTES.c.project_id)
            .where(LOTES.c.user_id == user_id, LOTES.c.id == batch_id)
            .with_for_update(),
        )
        conteo = {
            estado: cantidad
            for estado, cantidad in conexion.execute(
                select(ITEMS.c.status, func.count())
                .where(ITEMS.c.user_id == user_id, ITEMS.c.batch_id == batch_id)
                .group_by(ITEMS.c.status)
            )
        }
        if conteo.get(EstadoItem.QUEUED, 0) or conteo.get(EstadoItem.RUNNING, 0):
            iniciado = conteo.get(EstadoItem.RUNNING, 0) or conteo.get(EstadoItem.SUCCEEDED, 0) or conteo.get(EstadoItem.FAILED, 0)
            estado = EstadoLote.RUNNING if iniciado else EstadoLote.QUEUED
            if estado != lote["status"] and lote["status"] in LOTES_ABIERTOS:
                conexion.execute(
                    update(LOTES)
                    .where(LOTES.c.id == batch_id)
                    .values(status=estado, started_at=func.coalesce(LOTES.c.started_at, AHORA))
                )
            return estado
        exitos = conteo.get(EstadoItem.SUCCEEDED, 0)
        total = sum(conteo.values())
        if lote["cancel_requested_at"] is not None:
            estado = EstadoLote.CANCELLED
        elif exitos == total:
            estado = EstadoLote.SUCCEEDED
        elif exitos:
            estado = EstadoLote.PARTIAL
        else:
            estado = EstadoLote.FAILED
        if lote["status"] != estado:
            conexion.execute(update(LOTES).where(LOTES.c.id == batch_id).values(status=estado, finished_at=AHORA))
            RepositorioHistorial.Evento(
                conexion,
                user_id,
                lote["project_id"],
                TipoEvento.BATCH_FINISHED,
                batch_id=batch_id,
                payload={"status": estado, "succeeded": exitos, "total": total},
            )
        return estado

    @staticmethod
    def _Candidato() -> Any:
        # Primer ítem disponible de un usuario activo sin otro ítem en ejecución.
        # SKIP LOCKED permite que varios trabajadores consuman la cola sin esperar.
        en_ejecucion = ITEMS.alias("r")
        return (
            select(ITEMS.c.id, ITEMS.c.user_id)
            .select_from(
                ITEMS.join(LOTES, and_(LOTES.c.id == ITEMS.c.batch_id, LOTES.c.user_id == ITEMS.c.user_id)).join(
                    USUARIOS, USUARIOS.c.id == ITEMS.c.user_id
                )
            )
            .where(
                ITEMS.c.status == EstadoItem.QUEUED,
                ITEMS.c.available_at <= AHORA,
                LOTES.c.cancel_requested_at.is_(None),
                USUARIOS.c.status == EstadoUsuario.ACTIVE,
                ~select(en_ejecucion.c.id)
                .where(en_ejecucion.c.user_id == ITEMS.c.user_id, en_ejecucion.c.status == EstadoItem.RUNNING)
                .exists(),
            )
            .order_by(ITEMS.c.available_at, ITEMS.c.created_at, ITEMS.c.id)
            .limit(1)
            .with_for_update(of=ITEMS, skip_locked=True)
        )

    @classmethod
    def ReservarPendiente(
        cls, conexion, trabajador_id: str, lease_s: int, generador: str, revision: str, runtime: dict
    ) -> TrabajoReservado | None:
        candidato = cls._Uno(conexion, cls._Candidato())
        if candidato is None:
            return None
        if not cls.IntentarBloquearUsuario(conexion, candidato["user_id"]):
            return None
        ocupado = conexion.execute(
            select(ITEMS.c.id)
            .where(ITEMS.c.user_id == candidato["user_id"], ITEMS.c.status == EstadoItem.RUNNING)
            .limit(1)
        ).first()
        if ocupado is not None:
            return None
        token = uuid.uuid4()
        item = cls._Uno(
            conexion,
            update(ITEMS)
            .where(ITEMS.c.id == candidato["id"])
            .values(
                status=EstadoItem.RUNNING,
                attempt_count=ITEMS.c.attempt_count + 1,
                lease_token=token,
                lease_expires_at=AHORA + Segundos(lease_s),
                updated_at=AHORA,
            )
            .returning(
                ITEMS.c.id,
                ITEMS.c.user_id,
                ITEMS.c.project_id,
                ITEMS.c.batch_id,
                ITEMS.c.version_id,
                ITEMS.c.attempt_count,
                ITEMS.c.max_attempts,
            ),
        )
        attempt_id = uuid.uuid4()
        conexion.execute(
            insert(INTENTOS).values(
                id=attempt_id,
                user_id=item["user_id"],
                batch_item_id=item["id"],
                attempt_number=item["attempt_count"],
                worker_id=trabajador_id,
                lease_token=token,
                generator_version=generador,
                code_revision=revision,
                runtime_snapshot=runtime,
                execution_parameters={},
            )
        )
        conexion.execute(
            update(LOTES)
            .where(LOTES.c.id == item["batch_id"], LOTES.c.status == EstadoLote.QUEUED)
            .values(status=EstadoLote.RUNNING, started_at=func.coalesce(LOTES.c.started_at, AHORA))
        )
        version = cls._Uno(
            conexion,
            select(
                VERSIONES.c.parameters,
                VERSIONES.c.auto_scale,
                VERSIONES.c.material_snapshot,
                IMPORTS.c.normalized_asset_id,
            )
            .select_from(
                VERSIONES.join(
                    IMPORTS, and_(IMPORTS.c.id == VERSIONES.c.import_id, IMPORTS.c.user_id == VERSIONES.c.user_id)
                )
            )
            .where(VERSIONES.c.user_id == item["user_id"], VERSIONES.c.id == item["version_id"]),
        )
        RepositorioHistorial.Evento(
            conexion,
            item["user_id"],
            item["project_id"],
            TipoEvento.ATTEMPT_STARTED,
            version_id=item["version_id"],
            batch_id=item["batch_id"],
            attempt_id=attempt_id,
            payload={"attempt_number": item["attempt_count"], "worker_id": trabajador_id},
        )
        return TrabajoReservado(
            item_id=item["id"],
            attempt_id=attempt_id,
            attempt_number=item["attempt_count"],
            lease_token=token,
            user_id=item["user_id"],
            project_id=item["project_id"],
            batch_id=item["batch_id"],
            version_id=item["version_id"],
            parameters=dict(version["parameters"]),
            auto_scale=version["auto_scale"],
            normalized_asset_id=version["normalized_asset_id"],
            max_attempts=item["max_attempts"],
            material_snapshot=dict(version["material_snapshot"]),
        )

    @staticmethod
    def _ItemVigente(trabajo: TrabajoReservado) -> tuple:
        return (
            ITEMS.c.id == trabajo.item_id,
            ITEMS.c.user_id == trabajo.user_id,
            ITEMS.c.status == EstadoItem.RUNNING,
            ITEMS.c.lease_token == trabajo.lease_token,
        )

    @staticmethod
    def RenovarLease(conexion, trabajo: TrabajoReservado, lease_s: int) -> bool:
        resultado = conexion.execute(
            update(ITEMS)
            .where(*RepositorioLotes._ItemVigente(trabajo))
            .values(lease_expires_at=AHORA + Segundos(lease_s), updated_at=AHORA)
        )
        if resultado.rowcount != 1:
            return False
        conexion.execute(
            update(INTENTOS)
            .where(INTENTOS.c.id == trabajo.attempt_id, INTENTOS.c.status == EstadoIntento.RUNNING)
            .values(heartbeat_at=AHORA)
        )
        return True

    @staticmethod
    def BloquearVigente(conexion, trabajo: TrabajoReservado) -> bool:
        fila = conexion.execute(
            select(ITEMS.c.id).where(*RepositorioLotes._ItemVigente(trabajo)).with_for_update()
        ).first()
        return fila is not None

    @staticmethod
    def CancelacionPedida(conexion, trabajo: TrabajoReservado) -> bool:
        fila = conexion.execute(
            select(LOTES.c.cancel_requested_at).where(LOTES.c.user_id == trabajo.user_id, LOTES.c.id == trabajo.batch_id)
        ).first()
        return fila is not None and fila.cancel_requested_at is not None

    @staticmethod
    def CerrarIntento(
        conexion,
        trabajo: TrabajoReservado,
        estado: str,
        duracion_ms: int,
        codigo: str | None = None,
        mensaje: str | None = None,
        reintentable: bool = False,
    ) -> None:
        conexion.execute(
            update(INTENTOS)
            .where(
                INTENTOS.c.user_id == trabajo.user_id,
                INTENTOS.c.id == trabajo.attempt_id,
                INTENTOS.c.status == EstadoIntento.RUNNING,
            )
            .values(
                status=estado,
                error_code=codigo and codigo[:80],
                error_message=mensaje and mensaje[:500],
                retryable=reintentable,
                finished_at=AHORA,
                heartbeat_at=AHORA,
                duration_ms=max(0, duracion_ms),
            )
        )

    @staticmethod
    def Exito(conexion, trabajo: TrabajoReservado, resultado: ResultadoGeometrico, duracion_ms: int) -> None:
        conexion.execute(
            update(INTENTOS)
            .where(
                INTENTOS.c.user_id == trabajo.user_id,
                INTENTOS.c.id == trabajo.attempt_id,
                INTENTOS.c.status == EstadoIntento.RUNNING,
            )
            .values(
                status=EstadoIntento.SUCCEEDED,
                finished_at=AHORA,
                heartbeat_at=AHORA,
                duration_ms=max(0, duracion_ms),
                effective_scale=resultado.effective_scale,
                effective_step_mm=resultado.effective_step_mm,
                execution_parameters=resultado.execution_parameters,
            )
        )
        conexion.execute(
            update(ITEMS)
            .where(ITEMS.c.user_id == trabajo.user_id, ITEMS.c.id == trabajo.item_id)
            .values(
                status=EstadoItem.SUCCEEDED,
                winning_attempt_id=trabajo.attempt_id,
                lease_token=None,
                lease_expires_at=None,
                updated_at=AHORA,
            )
        )

    @classmethod
    def Liberar(cls, conexion, user_id: UUID, item_id: UUID, reintentar: bool, espera_s: float) -> str:
        """Saca el ítem de ``running``: a la cola, cancelado o fallido."""
        fila = cls._Uno(
            conexion,
            select(ITEMS.c.attempt_count, ITEMS.c.max_attempts, LOTES.c.cancel_requested_at)
            .select_from(ITEMS.join(LOTES, and_(LOTES.c.id == ITEMS.c.batch_id, LOTES.c.user_id == ITEMS.c.user_id)))
            .where(ITEMS.c.user_id == user_id, ITEMS.c.id == item_id),
        )
        if fila["cancel_requested_at"] is not None:
            estado = EstadoItem.CANCELLED
        elif reintentar and fila["attempt_count"] < fila["max_attempts"]:
            estado = EstadoItem.QUEUED
        else:
            estado = EstadoItem.FAILED
        valores: dict[str, Any] = {
            "status": estado,
            "lease_token": None,
            "lease_expires_at": None,
            "updated_at": AHORA,
        }
        if estado == EstadoItem.QUEUED:
            valores["available_at"] = AHORA + Segundos(espera_s)
        conexion.execute(update(ITEMS).where(ITEMS.c.user_id == user_id, ITEMS.c.id == item_id).values(**valores))
        return estado

    @staticmethod
    def AbandonarIntento(conexion, user_id: UUID, item_id: UUID) -> UUID | None:
        return conexion.execute(
            update(INTENTOS)
            .where(
                INTENTOS.c.user_id == user_id,
                INTENTOS.c.batch_item_id == item_id,
                INTENTOS.c.status == EstadoIntento.RUNNING,
            )
            .values(
                status=EstadoIntento.ABANDONED,
                error_code="lease_expired",
                retryable=True,
                finished_at=AHORA,
                duration_ms=cast(extract("epoch", AHORA - INTENTOS.c.started_at) * 1000, BigInteger),
            )
            .returning(INTENTOS.c.id)
        ).scalar_one_or_none()

    @classmethod
    def Vencidos(cls, conexion) -> list[dict]:
        return cls._Todos(
            conexion,
            select(
                ITEMS.c.id,
                ITEMS.c.user_id,
                ITEMS.c.project_id,
                ITEMS.c.batch_id,
                ITEMS.c.version_id,
                ITEMS.c.attempt_count,
                ITEMS.c.max_attempts,
                ITEMS.c.lease_token,
            )
            .where(ITEMS.c.status == EstadoItem.RUNNING, ITEMS.c.lease_expires_at < AHORA)
            .order_by(ITEMS.c.lease_expires_at)
            .limit(50)
            .with_for_update(skip_locked=True),
        )

    @staticmethod
    def _Item(fila: dict) -> ItemLote:
        return ItemLote(
            id=fila["id"],
            batch_id=fila["batch_id"],
            position=fila["position"],
            status=fila["status"],
            version_id=fila["version_id"],
            version_number=fila["version_number"],
            parameters=dict(fila["parameters"]),
            attempt_count=fila["attempt_count"],
            error_message=fila["error_message"],
            resultado=RepositorioResultados.Dto(fila) if fila["result_id"] is not None else None,
        )
