"""Tipos de evento de ``history_events``."""

from enum import StrEnum


class TipoEvento(StrEnum):
    IMPORT_RECEIVED = "import_received"
    IMPORT_READY = "import_ready"
    IMPORT_REJECTED = "import_rejected"
    VERSION_CREATED = "version_created"
    BATCH_QUEUED = "batch_queued"
    BATCH_CANCEL_REQUESTED = "batch_cancel_requested"
    BATCH_FINISHED = "batch_finished"
    ATTEMPT_STARTED = "attempt_started"
    ATTEMPT_FAILED = "attempt_failed"
    ATTEMPT_ABANDONED = "attempt_abandoned"
    RESULT_READY = "result_ready"
    EXPORT_DOWNLOADED = "export_downloaded"
    PROJECT_ARCHIVED = "project_archived"
