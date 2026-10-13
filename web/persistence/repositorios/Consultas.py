"""Tablas y fragmentos de consulta que comparten varios repositorios."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from sqlalchemy import and_, func, select

from web.enums import FormatoExport

from ..Modelos import (
    ArchivoAlmacenado,
    EventoHistorial,
    Exportacion,
    Importacion,
    IntentoGeneracion,
    ItemLoteGeneracion,
    LoteGeneracion,
    PreferenciaUsuario,
    Proyecto,
    ResultadoGeneracion,
    SesionAutenticacion,
    Usuario,
    VersionModelo,
)

USUARIOS = Usuario.__table__
SESIONES = SesionAutenticacion.__table__
PREFERENCIAS = PreferenciaUsuario.__table__
ASSETS = ArchivoAlmacenado.__table__
PROYECTOS = Proyecto.__table__
IMPORTS = Importacion.__table__
VERSIONES = VersionModelo.__table__
LOTES = LoteGeneracion.__table__
ITEMS = ItemLoteGeneracion.__table__
INTENTOS = IntentoGeneracion.__table__
RESULTADOS = ResultadoGeneracion.__table__
EXPORTS = Exportacion.__table__
EVENTOS = EventoHistorial.__table__

AHORA = func.now()


def Segundos(valor: float) -> timedelta:
    return timedelta(seconds=valor)


def UltimoError() -> Any:
    # Mensaje del intento más reciente del ítem de la consulta externa.
    ga = INTENTOS.alias("ga")
    return (
        select(ga.c.error_message)
        .where(ga.c.batch_item_id == ITEMS.c.id, ga.c.user_id == ITEMS.c.user_id)
        .order_by(ga.c.attempt_number.desc())
        .limit(1)
        .scalar_subquery()
        .label("error_message")
    )


def ConStlGanador(origen: Any) -> Any:
    # Resultado del intento ganador del ítem, su export STL y el archivo publicado.
    return (
        origen.outerjoin(
            RESULTADOS,
            and_(RESULTADOS.c.attempt_id == ITEMS.c.winning_attempt_id, RESULTADOS.c.user_id == ITEMS.c.user_id),
        )
        .outerjoin(
            EXPORTS,
            and_(
                EXPORTS.c.result_id == RESULTADOS.c.id,
                EXPORTS.c.user_id == ITEMS.c.user_id,
                EXPORTS.c.format == FormatoExport.STL_BINARY,
            ),
        )
        .outerjoin(ASSETS, and_(ASSETS.c.id == EXPORTS.c.asset_id, ASSETS.c.user_id == ITEMS.c.user_id))
    )


def ColumnasResultado(intento: Any) -> tuple:
    return (
        RESULTADOS.c.id.label("result_id"),
        RESULTADOS.c.attempt_id,
        RESULTADOS.c.volume_mm3,
        RESULTADOS.c.weight_g,
        RESULTADOS.c.estimated_price,
        RESULTADOS.c.currency,
        RESULTADOS.c.vertices,
        RESULTADOS.c.triangles,
        RESULTADOS.c.dimensions_mm,
        RESULTADOS.c.validation_status,
        RESULTADOS.c.warnings,
        intento.c.effective_scale,
        ASSETS.c.id.label("stl_asset_id"),
        ASSETS.c.object_url.label("stl_url"),
        EXPORTS.c.status.label("stl_status"),
    )
