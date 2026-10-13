"""Importaciones de superficies: original recibido y NPZ normalizado."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, insert, select, update

from web.enums import EstadoAsset, EstadoImport

from ..Contratos import ImportDTO, UsuarioAutenticado
from .Consultas import AHORA, ASSETS, IMPORTS
from .RepositorioBase import RepositorioBase


class RepositorioImports(RepositorioBase):
    TABLA = IMPORTS
    DTO = ImportDTO

    @staticmethod
    def Crear(
        conexion,
        user: UsuarioAutenticado,
        import_id: UUID,
        original_asset_id: UUID,
        source_kind: str,
        formato: str,
        reader_version: str,
        esquema: int,
    ) -> None:
        conexion.execute(
            insert(IMPORTS).values(
                id=import_id,
                user_id=user.user_id,
                project_id=user.project_id,
                original_asset_id=original_asset_id,
                source_kind=source_kind,
                status=EstadoImport.RECEIVED,
                format=formato,
                reader_version=reader_version,
                normalization_schema_version=esquema,
            )
        )

    @staticmethod
    def MarcarListo(
        conexion,
        user_id: UUID,
        import_id: UUID,
        normalized_asset_id: UUID,
        vertices: int,
        caras: int,
        dimensiones: list[float],
    ) -> None:
        conexion.execute(
            update(IMPORTS)
            .where(IMPORTS.c.user_id == user_id, IMPORTS.c.id == import_id)
            .values(
                status=EstadoImport.READY,
                normalized_asset_id=normalized_asset_id,
                vertex_count=vertices,
                face_count=caras,
                raw_dimensions_mm=dimensiones,
                finished_at=AHORA,
            )
        )

    @staticmethod
    def MarcarRechazado(conexion, user_id: UUID, import_id: UUID, codigo: str, mensaje: str) -> None:
        conexion.execute(
            update(IMPORTS)
            .where(IMPORTS.c.user_id == user_id, IMPORTS.c.id == import_id)
            .values(status=EstadoImport.REJECTED, error_code=codigo[:80], error_message=mensaje[:500], finished_at=AHORA)
        )

    @classmethod
    def Obtener(cls, conexion, user_id: UUID, import_id: UUID) -> ImportDTO:
        return cls._DelUsuario(conexion, user_id, IMPORTS.c.id == import_id)

    @classmethod
    def ListoPorNormalizado(cls, conexion, user_id: UUID, asset_id: UUID) -> ImportDTO | None:
        return cls._Opcional(
            conexion,
            select(IMPORTS)
            .where(
                IMPORTS.c.user_id == user_id,
                IMPORTS.c.normalized_asset_id == asset_id,
                IMPORTS.c.status == EstadoImport.READY,
            )
            .order_by(IMPORTS.c.created_at.desc())
            .limit(1),
        )

    @classmethod
    def ListoPorOriginal(
        cls, conexion, user_id: UUID, project_id: UUID, sha256: str, source_kind: str
    ) -> ImportDTO | None:
        original = ASSETS.alias("a")
        normalizado = ASSETS.alias("n")
        return cls._Opcional(
            conexion,
            select(IMPORTS, original.c.original_name)
            .select_from(
                IMPORTS.join(
                    original,
                    and_(original.c.id == IMPORTS.c.original_asset_id, original.c.user_id == IMPORTS.c.user_id),
                ).join(
                    normalizado,
                    and_(normalizado.c.id == IMPORTS.c.normalized_asset_id, normalizado.c.user_id == IMPORTS.c.user_id),
                )
            )
            .where(
                IMPORTS.c.user_id == user_id,
                IMPORTS.c.project_id == project_id,
                IMPORTS.c.source_kind == source_kind,
                IMPORTS.c.status == EstadoImport.READY,
                original.c.sha256 == sha256,
                normalizado.c.status == EstadoAsset.READY,
            )
            .order_by(IMPORTS.c.created_at)
            .limit(1),
        )

    @staticmethod
    def NombreOriginal(conexion, user_id: UUID, import_id: UUID) -> str:
        nombre = conexion.execute(
            select(ASSETS.c.original_name)
            .select_from(
                IMPORTS.join(
                    ASSETS, and_(ASSETS.c.id == IMPORTS.c.original_asset_id, ASSETS.c.user_id == IMPORTS.c.user_id)
                )
            )
            .where(IMPORTS.c.user_id == user_id, IMPORTS.c.id == import_id)
        ).scalar_one_or_none()
        return nombre or ""
