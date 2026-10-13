"""Origen, estado y formato de una superficie importada (``imports``)."""

from enum import StrEnum


class OrigenImport(StrEnum):
    UPLOAD = "upload"
    INCLUDED_TEMPLATE = "included_template"


class EstadoImport(StrEnum):
    RECEIVED = "received"
    VALIDATING = "validating"
    READY = "ready"
    REJECTED = "rejected"


class FormatoImport(StrEnum):
    STL_BINARY = "stl_binary"
    STL_ASCII = "stl_ascii"
    NPZ = "npz"
