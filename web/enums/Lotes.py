"""Backend de versión, modos de lote y estados de lotes, ítems e intentos."""

from enum import StrEnum


class BackendGeneracion(StrEnum):
    PYTHON_CORE = "python_core"


class ModoLote(StrEnum):
    SINGLE = "single"
    SWEEP = "sweep"
    RETRY = "retry"


class EstadoLote(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EstadoItem(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EstadoIntento(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ABANDONED = "abandoned"
    CANCELLED = "cancelled"


# Un ítem en estos estados ya no vuelve a la cola.
ITEMS_TERMINALES = (EstadoItem.SUCCEEDED, EstadoItem.FAILED, EstadoItem.CANCELLED)
# Un lote en estos estados cuenta para la cuota de pendientes.
LOTES_ABIERTOS = (EstadoLote.QUEUED, EstadoLote.RUNNING)
