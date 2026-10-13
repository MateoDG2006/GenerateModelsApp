"""Filas de ``file_assets``: el contenido vive en el bucket."""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, insert, select, update

from web.enums import EstadoAsset, EstadoExport, EstadoImport

from ..Contratos import AccesoDenegado, Asset
from .Consultas import AHORA, ASSETS, EXPORTS, IMPORTS
from .RepositorioBase import RepositorioBase


class RepositorioAssets(RepositorioBase):
    TABLA = ASSETS
    DTO = Asset
    COLUMNAS = (
        "id", "user_id", "storage_key", "object_url", "kind", "original_name", "media_type", "size_bytes",
        "sha256", "status",
    )

    @classmethod
    def _Seleccion(cls) -> Any:
        return select(*(ASSETS.c[nombre] for nombre in cls.COLUMNAS))

    @staticmethod
    def CrearStaged(
        conexion,
        user_id: UUID,
        asset_id: UUID,
        storage_key: str,
        kind: str,
        nombre: str | None,
        media_type: str,
        size_bytes: int,
        sha256: str,
    ) -> None:
        conexion.execute(
            insert(ASSETS).values(
                id=asset_id,
                user_id=user_id,
                storage_key=storage_key,
                kind=kind,
                original_name=nombre,
                media_type=media_type,
                size_bytes=size_bytes,
                sha256=sha256,
                status=EstadoAsset.STAGED,
            )
        )

    @staticmethod
    def MarcarListo(conexion, user_id: UUID, asset_id: UUID, object_url: str) -> None:
        resultado = conexion.execute(
            update(ASSETS)
            .where(ASSETS.c.user_id == user_id, ASSETS.c.id == asset_id, ASSETS.c.status == EstadoAsset.STAGED)
            .values(status=EstadoAsset.READY, object_url=object_url, ready_at=AHORA)
        )
        if resultado.rowcount != 1:
            raise AccesoDenegado("El archivo no está pendiente de publicación.")

    @staticmethod
    def MarcarEstado(conexion, asset_id: UUID, estado: str) -> None:
        # Solo la usa la conciliación del trabajador, con IDs que leyó de la base.
        valores: dict[str, Any] = {"status": estado}
        if estado == EstadoAsset.DELETED:
            valores["deleted_at"] = AHORA
        conexion.execute(update(ASSETS).where(ASSETS.c.id == asset_id).values(**valores))

    @classmethod
    def Obtener(cls, conexion, user_id: UUID, asset_id: UUID) -> Asset:
        return cls._DelUsuario(conexion, user_id, ASSETS.c.id == asset_id)

    @classmethod
    def ListoPorSha(cls, conexion, user_id: UUID, sha256: str, kind: str) -> Asset | None:
        return cls._Opcional(
            conexion,
            cls._Seleccion()
            .where(
                ASSETS.c.user_id == user_id,
                ASSETS.c.sha256 == sha256,
                ASSETS.c.kind == kind,
                ASSETS.c.status == EstadoAsset.READY,
            )
            .order_by(ASSETS.c.created_at)
            .limit(1),
        )

    @classmethod
    def StagedVencidos(cls, conexion, horas: int) -> list[Asset]:
        return cls._Lista(
            conexion,
            cls._Seleccion()
            .where(ASSETS.c.status == EstadoAsset.STAGED, ASSETS.c.created_at < AHORA - timedelta(hours=horas))
            .order_by(ASSETS.c.created_at)
            .limit(200),
        )

    @classmethod
    def RechazadosVencidos(cls, conexion, dias: int) -> list[Asset]:
        union = and_(
            ASSETS.c.user_id == IMPORTS.c.user_id,
            ASSETS.c.id.in_([IMPORTS.c.original_asset_id, IMPORTS.c.normalized_asset_id]),
        )
        return cls._Lista(
            conexion,
            cls._Seleccion()
            .distinct()
            .select_from(IMPORTS.join(ASSETS, union))
            .where(
                IMPORTS.c.status == EstadoImport.REJECTED,
                IMPORTS.c.finished_at < AHORA - timedelta(days=dias),
                ASSETS.c.status.in_((EstadoAsset.READY, EstadoAsset.QUARANTINED, EstadoAsset.STAGED)),
            )
            .limit(200),
        )

    @classmethod
    def ListosParaComprobar(cls, conexion, desde_id: UUID | None, limite: int) -> list[Asset]:
        consulta = cls._Seleccion().where(ASSETS.c.status == EstadoAsset.READY)
        if desde_id is not None:
            consulta = consulta.where(ASSETS.c.id > desde_id)
        return cls._Lista(conexion, consulta.order_by(ASSETS.c.id).limit(limite))

    @classmethod
    def PorClave(cls, conexion, user_id: UUID, storage_key: str) -> Asset:
        return cls._DelUsuario(conexion, user_id, ASSETS.c.storage_key == storage_key)

    @staticmethod
    def ClavesRegistradas(conexion, claves: list[str]) -> set[str]:
        filas = conexion.execute(select(ASSETS.c.storage_key).where(ASSETS.c.storage_key.in_(claves))).scalars()
        return set(filas)

    @staticmethod
    def MarcarExportsFaltantes(conexion, asset_id: UUID) -> None:
        conexion.execute(
            update(EXPORTS)
            .where(EXPORTS.c.asset_id == asset_id, EXPORTS.c.status == EstadoExport.READY)
            .values(status=EstadoExport.MISSING)
        )
