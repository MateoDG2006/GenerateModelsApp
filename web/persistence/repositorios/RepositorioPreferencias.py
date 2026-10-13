"""Preferencias por usuario con control optimista de revisión."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as insertar_pg

from ..Contratos import ConflictoRevision, Preferencias
from .Consultas import AHORA, PREFERENCIAS
from .RepositorioBase import RepositorioBase


class RepositorioPreferencias(RepositorioBase):
    TABLA = PREFERENCIAS
    DTO = Preferencias

    @classmethod
    def Obtener(cls, conexion, user_id: UUID) -> Preferencias:
        conexion.execute(
            insertar_pg(PREFERENCIAS).values(user_id=user_id).on_conflict_do_nothing(index_elements=["user_id"])
        )
        return cls._Dto(cls._Uno(conexion, select(PREFERENCIAS).where(PREFERENCIAS.c.user_id == user_id)))

    @classmethod
    def Guardar(
        cls,
        conexion,
        user_id: UUID,
        auto_scale: bool,
        parametros: dict,
        revision_esperada: int,
    ) -> Preferencias:
        preferencias = cls._Opcional(
            conexion,
            update(PREFERENCIAS)
            .where(PREFERENCIAS.c.user_id == user_id, PREFERENCIAS.c.revision == revision_esperada)
            .values(
                auto_scale=auto_scale,
                default_parameters=parametros,
                revision=PREFERENCIAS.c.revision + 1,
                updated_at=AHORA,
            )
            .returning(*PREFERENCIAS.c),
        )
        if preferencias is None:
            raise ConflictoRevision()
        return preferencias
