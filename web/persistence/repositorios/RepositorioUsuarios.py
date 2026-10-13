"""Cuentas creadas desde OIDC y sus sesiones de servidor."""

from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.dialects.postgresql import insert as insertar_pg

from web.enums import EstadoUsuario

from .Consultas import AHORA, SESIONES, USUARIOS
from .RepositorioBase import RepositorioBase


class RepositorioUsuarios(RepositorioBase):
    TABLA = USUARIOS

    @staticmethod
    def Upsert(conexion, issuer: str, subject: str, email: str | None, nombre: str) -> UUID:
        sentencia = insertar_pg(USUARIOS).values(
            id=uuid.uuid4(),
            auth_issuer=issuer,
            auth_subject=subject,
            email=email,
            display_name=nombre[:120] or subject[:120],
        )
        sentencia = sentencia.on_conflict_do_update(
            index_elements=[USUARIOS.c.auth_issuer, USUARIOS.c.auth_subject],
            set_={
                "email": sentencia.excluded.email,
                "display_name": sentencia.excluded.display_name,
                "updated_at": AHORA,
            },
        )
        return conexion.execute(sentencia.returning(USUARIOS.c.id)).scalar_one()

    @staticmethod
    def Estado(conexion, user_id: UUID) -> str | None:
        return conexion.execute(select(USUARIOS.c.status).where(USUARIOS.c.id == user_id)).scalar_one_or_none()

    @staticmethod
    def CrearSesion(conexion, user_id: UUID, token_sha256: str, expira: datetime) -> None:
        conexion.execute(
            insert(SESIONES).values(id=uuid.uuid4(), user_id=user_id, token_sha256=token_sha256, expires_at=expira)
        )

    @classmethod
    def ResolverSesion(cls, conexion, token_sha256: str) -> dict | None:
        return cls._Uno(
            conexion,
            select(USUARIOS.c.id, USUARIOS.c.display_name, USUARIOS.c.email)
            .select_from(SESIONES.join(USUARIOS, USUARIOS.c.id == SESIONES.c.user_id))
            .where(
                SESIONES.c.token_sha256 == token_sha256,
                SESIONES.c.revoked_at.is_(None),
                SESIONES.c.expires_at > AHORA,
                USUARIOS.c.status == EstadoUsuario.ACTIVE,
            ),
        )

    @staticmethod
    def RevocarSesion(conexion, token_sha256: str) -> None:
        conexion.execute(
            update(SESIONES)
            .where(SESIONES.c.token_sha256 == token_sha256, SESIONES.c.revoked_at.is_(None))
            .values(revoked_at=AHORA)
        )
