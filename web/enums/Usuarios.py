"""Estados de una cuenta de ``app_users``."""

from enum import StrEnum


class EstadoUsuario(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETION_PENDING = "deletion_pending"
