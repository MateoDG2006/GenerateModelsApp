"""Validación y alcance de ``generation_results`` y formato, unidad y estado de ``exports``."""

from enum import StrEnum


class EstadoValidacion(StrEnum):
    NOT_CHECKED = "not_checked"
    PASSED = "passed"
    FAILED = "failed"


class AlcanceGeometria(StrEnum):
    PRE_VOXEL_SHELL = "pre_voxel_shell"


class FormatoExport(StrEnum):
    STL_BINARY = "stl_binary"
    PARAMETERS_JSON = "parameters_json"


class UnidadExport(StrEnum):
    MM = "mm"


class EstadoExport(StrEnum):
    READY = "ready"
    MISSING = "missing"
    DELETED = "deleted"
