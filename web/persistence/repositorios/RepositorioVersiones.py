"""Versiones inmutables numeradas por proyecto."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import insert, update

from web.enums import BackendGeneracion

from ..Contratos import AccesoDenegado, VersionDTO
from .Consultas import AHORA, PROYECTOS, VERSIONES
from .RepositorioBase import RepositorioBase


class RepositorioVersiones(RepositorioBase):
    TABLA = VERSIONES
    DTO = VersionDTO

    @staticmethod
    def ReservarNumeros(conexion, user_id: UUID, project_id: UUID, cantidad: int) -> range:
        # El UPDATE bloquea la fila del proyecto hasta el commit: dos lotes
        # simultáneos reciben rangos distintos.
        primero = conexion.execute(
            update(PROYECTOS)
            .where(PROYECTOS.c.user_id == user_id, PROYECTOS.c.id == project_id, PROYECTOS.c.archived_at.is_(None))
            .values(next_version_number=PROYECTOS.c.next_version_number + cantidad, updated_at=AHORA)
            .returning(PROYECTOS.c.next_version_number - cantidad)
        ).scalar_one_or_none()
        if primero is None:
            raise AccesoDenegado("El proyecto no existe o está archivado.")
        return range(primero, primero + cantidad)

    @staticmethod
    def Insertar(
        conexion,
        user_id: UUID,
        project_id: UUID,
        version_id: UUID,
        import_id: UUID,
        numero: int,
        parametros: dict,
        esquema: int,
        auto_scale: bool,
        material: dict,
        parametros_sha256: str,
        padre: UUID | None,
        nota: str | None,
    ) -> None:
        conexion.execute(
            insert(VERSIONES).values(
                id=version_id,
                user_id=user_id,
                project_id=project_id,
                import_id=import_id,
                parent_version_id=padre,
                version_number=numero,
                change_note=nota,
                parameters=parametros,
                parameter_schema_version=esquema,
                auto_scale=auto_scale,
                material_snapshot=material,
                requested_backend=BackendGeneracion.PYTHON_CORE,
                parameters_sha256=parametros_sha256,
            )
        )

    @classmethod
    def Obtener(cls, conexion, user_id: UUID, version_id: UUID) -> VersionDTO:
        return cls._DelUsuario(conexion, user_id, VERSIONES.c.id == version_id)
