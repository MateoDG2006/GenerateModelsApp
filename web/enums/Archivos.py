"""Tipos y estados de los objetos del bucket registrados en ``file_assets``."""

from enum import StrEnum


class TipoAsset(StrEnum):
    IMPORT_ORIGINAL = "import_original"
    SURFACE_NPZ = "surface_npz"
    RESULT_STL = "result_stl"
    EXPORT_JSON = "export_json"


class EstadoAsset(StrEnum):
    STAGED = "staged"
    READY = "ready"
    QUARANTINED = "quarantined"
    MISSING = "missing"
    DELETING = "deleting"
    DELETED = "deleted"


class ExtensionSuperficie(StrEnum):
    STL = ".stl"
    NPZ = ".npz"
