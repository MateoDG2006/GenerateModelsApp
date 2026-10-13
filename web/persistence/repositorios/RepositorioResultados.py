"""Resultados geométricos, intentos de una versión y exports STL."""

from __future__ import annotations

import uuid
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, insert, select

from web.enums import FormatoExport, UnidadExport

from ..Contratos import IntentoDTO, ResultadoDTO, ResultadoGeometrico, TrabajoReservado
from .Consultas import ASSETS, EXPORTS, INTENTOS, ITEMS, RESULTADOS, ColumnasResultado
from .RepositorioBase import RepositorioBase


class RepositorioResultados(RepositorioBase):
    TABLA = RESULTADOS

    @staticmethod
    def Insertar(conexion, trabajo: TrabajoReservado, resultado: ResultadoGeometrico, alcance: str) -> UUID:
        result_id = uuid.uuid4()
        conexion.execute(
            insert(RESULTADOS).values(
                id=result_id,
                user_id=trabajo.user_id,
                batch_item_id=trabajo.item_id,
                attempt_id=trabajo.attempt_id,
                volume_mm3=resultado.volume_mm3,
                weight_g=resultado.weight_g,
                estimated_price=resultado.estimated_price,
                price_per_gram=resultado.price_per_gram,
                density_g_cm3=resultado.density_g_cm3,
                currency=resultado.currency,
                vertices=resultado.vertices,
                triangles=resultado.triangles,
                dimensions_mm=resultado.dimensions_mm,
                warnings=resultado.warnings,
                geometry_scope=alcance,
            )
        )
        return result_id

    @staticmethod
    def InsertarExport(conexion, user_id: UUID, result_id: UUID, asset_id: UUID, formato: str, version: str) -> UUID:
        export_id = uuid.uuid4()
        conexion.execute(
            insert(EXPORTS).values(
                id=export_id,
                user_id=user_id,
                result_id=result_id,
                asset_id=asset_id,
                format=formato,
                units=UnidadExport.MM,
                exporter_version=version,
            )
        )
        return export_id

    @staticmethod
    def Dto(fila: dict) -> ResultadoDTO:
        # Las columnas vienen de ColumnasResultado: id renombrado y numéricos sin tipo fijo.
        return ResultadoDTO(
            id=fila["result_id"],
            attempt_id=fila["attempt_id"],
            volume_mm3=float(fila["volume_mm3"]),
            weight_g=float(fila["weight_g"]),
            estimated_price=Decimal(fila["estimated_price"]),
            currency=fila["currency"],
            vertices=int(fila["vertices"]),
            triangles=int(fila["triangles"]),
            dimensions_mm=[float(valor) for valor in fila["dimensions_mm"]],
            validation_status=fila["validation_status"],
            warnings=list(fila["warnings"]),
            effective_scale=fila["effective_scale"],
            stl_asset_id=fila["stl_asset_id"],
            stl_url=fila["stl_url"],
            stl_status=fila["stl_status"],
        )

    @classmethod
    def _Dto(cls, fila: dict) -> ResultadoDTO:
        return cls.Dto(fila)

    @classmethod
    def Intentos(cls, conexion, user_id: UUID, version_id: UUID) -> list[IntentoDTO]:
        filas = cls._Todos(
            conexion,
            select(INTENTOS)
            .select_from(
                INTENTOS.join(
                    ITEMS, and_(ITEMS.c.id == INTENTOS.c.batch_item_id, ITEMS.c.user_id == INTENTOS.c.user_id)
                )
            )
            .where(INTENTOS.c.user_id == user_id, ITEMS.c.version_id == version_id)
            .order_by(INTENTOS.c.started_at, INTENTOS.c.attempt_number),
        )
        return [cls._Construir(IntentoDTO, fila) for fila in filas]

    @classmethod
    def DeVersion(cls, conexion, user_id: UUID, version_id: UUID) -> list[ResultadoDTO]:
        origen = (
            RESULTADOS.join(
                INTENTOS, and_(INTENTOS.c.id == RESULTADOS.c.attempt_id, INTENTOS.c.user_id == RESULTADOS.c.user_id)
            )
            .join(ITEMS, and_(ITEMS.c.id == RESULTADOS.c.batch_item_id, ITEMS.c.user_id == RESULTADOS.c.user_id))
            .outerjoin(
                EXPORTS,
                and_(
                    EXPORTS.c.result_id == RESULTADOS.c.id,
                    EXPORTS.c.user_id == RESULTADOS.c.user_id,
                    EXPORTS.c.format == FormatoExport.STL_BINARY,
                ),
            )
            .outerjoin(ASSETS, and_(ASSETS.c.id == EXPORTS.c.asset_id, ASSETS.c.user_id == RESULTADOS.c.user_id))
        )
        return cls._Lista(
            conexion,
            select(*ColumnasResultado(INTENTOS))
            .select_from(origen)
            .where(RESULTADOS.c.user_id == user_id, ITEMS.c.version_id == version_id)
            .order_by(RESULTADOS.c.created_at.desc()),
        )

    @classmethod
    def ExportStl(cls, conexion, user_id: UUID, asset_id: UUID) -> dict | None:
        return cls._Uno(
            conexion,
            select(
                EXPORTS.c.id.label("export_id"),
                EXPORTS.c.status,
                RESULTADOS.c.batch_item_id,
                ITEMS.c.project_id,
                ITEMS.c.version_id,
                ITEMS.c.batch_id,
                ASSETS.c.storage_key,
                ASSETS.c.object_url,
            )
            .select_from(
                EXPORTS.join(ASSETS, and_(ASSETS.c.id == EXPORTS.c.asset_id, ASSETS.c.user_id == EXPORTS.c.user_id))
                .join(
                    RESULTADOS,
                    and_(RESULTADOS.c.id == EXPORTS.c.result_id, RESULTADOS.c.user_id == EXPORTS.c.user_id),
                )
                .join(ITEMS, and_(ITEMS.c.id == RESULTADOS.c.batch_item_id, ITEMS.c.user_id == EXPORTS.c.user_id))
            )
            .where(
                EXPORTS.c.user_id == user_id,
                EXPORTS.c.asset_id == asset_id,
                EXPORTS.c.format == FormatoExport.STL_BINARY,
            ),
        )
