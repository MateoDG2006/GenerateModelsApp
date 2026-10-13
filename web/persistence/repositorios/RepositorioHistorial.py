"""Eventos de historial y listado de ejecuciones por versión."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, insert, select, tuple_

from ..Contratos import FilaHistorial
from .Consultas import (
    ASSETS,
    EVENTOS,
    EXPORTS,
    ITEMS,
    PROYECTOS,
    RESULTADOS,
    VERSIONES,
    ConStlGanador,
    UltimoError,
)
from .RepositorioBase import RepositorioBase


class RepositorioHistorial(RepositorioBase):
    TABLA = EVENTOS

    @staticmethod
    def Evento(
        conexion,
        user_id: UUID,
        project_id: UUID,
        tipo: str,
        *,
        version_id: UUID | None = None,
        batch_id: UUID | None = None,
        attempt_id: UUID | None = None,
        export_id: UUID | None = None,
        payload: dict | None = None,
    ) -> None:
        conexion.execute(
            insert(EVENTOS).values(
                user_id=user_id,
                project_id=project_id,
                version_id=version_id,
                batch_id=batch_id,
                attempt_id=attempt_id,
                export_id=export_id,
                event_type=tipo,
                payload=payload or {},
            )
        )

    @classmethod
    def Listar(
        cls,
        conexion,
        user_id: UUID,
        filtros: dict,
        cursor: tuple[datetime, UUID] | None,
        limite: int,
    ) -> tuple[list[FilaHistorial], bool]:
        # Una fila por ejecución de versión. Cursor compuesto (created_at, id) descendente.
        patron = VERSIONES.c.parameters["pattern"].astext
        origen = ITEMS.join(
            VERSIONES, and_(VERSIONES.c.id == ITEMS.c.version_id, VERSIONES.c.user_id == ITEMS.c.user_id)
        ).join(PROYECTOS, and_(PROYECTOS.c.id == ITEMS.c.project_id, PROYECTOS.c.user_id == ITEMS.c.user_id))
        consulta = (
            select(
                ITEMS.c.id.label("item_id"),
                ITEMS.c.batch_id,
                VERSIONES.c.id.label("version_id"),
                VERSIONES.c.project_id,
                PROYECTOS.c.name.label("project_name"),
                VERSIONES.c.version_number,
                patron.label("pattern"),
                VERSIONES.c.parameters,
                ITEMS.c.created_at,
                ITEMS.c.status,
                RESULTADOS.c.volume_mm3,
                RESULTADOS.c.weight_g,
                RESULTADOS.c.estimated_price,
                RESULTADOS.c.currency,
                RESULTADOS.c.validation_status,
                ASSETS.c.object_url.label("stl_url"),
                EXPORTS.c.status.label("stl_status"),
                UltimoError(),
            )
            .select_from(ConStlGanador(origen))
            .where(ITEMS.c.user_id == user_id)
        )
        if filtros.get("project_id") is not None:
            consulta = consulta.where(ITEMS.c.project_id == filtros["project_id"])
        if filtros.get("pattern") is not None:
            consulta = consulta.where(patron == filtros["pattern"])
        if filtros.get("status") is not None:
            consulta = consulta.where(ITEMS.c.status == filtros["status"])
        if filtros.get("desde") is not None:
            consulta = consulta.where(ITEMS.c.created_at >= filtros["desde"])
        if filtros.get("hasta") is not None:
            consulta = consulta.where(ITEMS.c.created_at < filtros["hasta"])
        if cursor is not None:
            consulta = consulta.where(tuple_(ITEMS.c.created_at, ITEMS.c.id) < tuple_(cursor[0], cursor[1]))
        filas = cls._Todos(
            conexion, consulta.order_by(ITEMS.c.created_at.desc(), ITEMS.c.id.desc()).limit(limite + 1)
        )
        hay_mas = len(filas) > limite
        return [
            FilaHistorial(
                item_id=fila["item_id"],
                batch_id=fila["batch_id"],
                version_id=fila["version_id"],
                project_id=fila["project_id"],
                project_name=fila["project_name"],
                version_number=fila["version_number"],
                pattern=fila["pattern"] or "",
                parameters=dict(fila["parameters"]),
                created_at=fila["created_at"],
                status=fila["status"],
                volume_mm3=fila["volume_mm3"],
                weight_g=fila["weight_g"],
                estimated_price=fila["estimated_price"],
                currency=fila["currency"],
                validation_status=fila["validation_status"],
                stl_url=fila["stl_url"],
                stl_status=fila["stl_status"],
                error_message=fila["error_message"],
            )
            for fila in filas[:limite]
        ], hay_mas

    @classmethod
    def EventosDeVersion(cls, conexion, user_id: UUID, version_id: UUID) -> list[dict]:
        return cls._Todos(
            conexion,
            select(EVENTOS.c.event_type, EVENTOS.c.payload, EVENTOS.c.created_at)
            .where(EVENTOS.c.user_id == user_id, EVENTOS.c.version_id == version_id)
            .order_by(EVENTOS.c.created_at, EVENTOS.c.id),
        )
