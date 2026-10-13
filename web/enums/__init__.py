"""Valores cerrados del dominio. Deben coincidir con los ``CHECK`` del esquema.

Son ``StrEnum``: cada miembro es también su texto, así que se compara con las
cadenas leídas de PostgreSQL y psycopg lo envía por su valor. Cambiar o añadir
un valor exige una migración que actualice el ``CHECK`` correspondiente.
"""

from .Archivos import EstadoAsset, ExtensionSuperficie, TipoAsset
from .Historial import TipoEvento
from .Imports import EstadoImport, FormatoImport, OrigenImport
from .Lotes import (
    ITEMS_TERMINALES,
    LOTES_ABIERTOS,
    BackendGeneracion,
    EstadoIntento,
    EstadoItem,
    EstadoLote,
    ModoLote,
)
from .Resultados import AlcanceGeometria, EstadoExport, EstadoValidacion, FormatoExport, UnidadExport
from .Usuarios import EstadoUsuario

__all__ = [
    "ITEMS_TERMINALES",
    "LOTES_ABIERTOS",
    "AlcanceGeometria",
    "BackendGeneracion",
    "EstadoAsset",
    "EstadoExport",
    "EstadoImport",
    "EstadoIntento",
    "EstadoItem",
    "EstadoLote",
    "EstadoUsuario",
    "EstadoValidacion",
    "ExtensionSuperficie",
    "FormatoExport",
    "FormatoImport",
    "ModoLote",
    "OrigenImport",
    "TipoAsset",
    "TipoEvento",
    "UnidadExport",
]
