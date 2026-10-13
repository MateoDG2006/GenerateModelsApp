"""Proyectos del usuario; cada cuenta tiene uno predeterminado."""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import insert, select

from .Consultas import PROYECTOS
from .RepositorioBase import RepositorioBase

NOMBRE_PROYECTO_PREDETERMINADO = "Proyecto principal"


class RepositorioProyectos(RepositorioBase):
    TABLA = PROYECTOS

    @staticmethod
    def Predeterminado(conexion, user_id: UUID) -> UUID:
        existente = conexion.execute(
            select(PROYECTOS.c.id)
            .where(
                PROYECTOS.c.user_id == user_id,
                PROYECTOS.c.archived_at.is_(None),
                PROYECTOS.c.name == NOMBRE_PROYECTO_PREDETERMINADO,
            )
            .order_by(PROYECTOS.c.created_at)
            .limit(1)
        ).scalar_one_or_none()
        if existente is not None:
            return existente
        return RepositorioProyectos.Crear(conexion, user_id, NOMBRE_PROYECTO_PREDETERMINADO)

    @staticmethod
    def Crear(conexion, user_id: UUID, nombre: str, descripcion: str | None = None) -> UUID:
        identificador = uuid.uuid4()
        conexion.execute(
            insert(PROYECTOS).values(id=identificador, user_id=user_id, name=nombre, description=descripcion)
        )
        return identificador

    @staticmethod
    def PorNombre(conexion, user_id: UUID, nombre: str) -> UUID | None:
        return conexion.execute(
            select(PROYECTOS.c.id)
            .where(PROYECTOS.c.user_id == user_id, PROYECTOS.c.name == nombre)
            .order_by(PROYECTOS.c.created_at)
            .limit(1)
        ).scalar_one_or_none()

    @classmethod
    def Listar(cls, conexion, user_id: UUID) -> list[dict]:
        return cls._Todos(
            conexion,
            select(PROYECTOS.c.id, PROYECTOS.c.name)
            .where(PROYECTOS.c.user_id == user_id, PROYECTOS.c.archived_at.is_(None))
            .order_by(PROYECTOS.c.updated_at.desc(), PROYECTOS.c.id.desc()),
        )
