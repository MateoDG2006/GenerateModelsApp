"""Modelos declarativos de SQLAlchemy del esquema ``ortesislab``.

Son la fuente de verdad de Alembic ``--autogenerate``. Los nombres de las
restricciones reproducen los que PostgreSQL asignaba al esquema original para
que el volcado ``pg_dump`` sea comparable. El esquema se resuelve por el
``search_path`` de cada rol, por eso las tablas no declaran ``schema``.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Double,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    MetaData,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.elements import TextClause

from web.enums import (
    AlcanceGeometria,
    BackendGeneracion,
    EstadoAsset,
    EstadoExport,
    EstadoImport,
    EstadoIntento,
    EstadoItem,
    EstadoLote,
    EstadoUsuario,
    EstadoValidacion,
    FormatoExport,
    FormatoImport,
    ModoLote,
    OrigenImport,
    TipoAsset,
    TipoEvento,
    UnidadExport,
)

AHORA = text("now()")
OBJETO_VACIO = text("'{}'::jsonb")


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "pk": "%(table_name)s_pkey",
            "uq": "%(table_name)s_%(column_0_name)s_key",
            "fk": "%(table_name)s_%(column_0_name)s_fkey",
        }
    )
    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
        datetime: DateTime(timezone=True),
        dict[str, Any]: JSONB,
        list[Any]: JSONB,
        str: Text,
        int: BigInteger,
        float: Double,
        Decimal: Numeric,
    }


def _Sha(columna: str, tabla: str) -> CheckConstraint:
    return CheckConstraint(f"{columna} ~ '^[0-9a-f]{{64}}$'", name=f"{tabla}_{columna}_check")


def _Valores(columna: str, tabla: str, valores: type[StrEnum]) -> CheckConstraint:
    # El orden de los miembros es el del CHECK existente; cambiarlo genera una migración.
    lista = ", ".join(f"'{valor}'" for valor in valores)
    return CheckConstraint(f"{columna} IN ({lista})", name=f"{tabla}_{columna}_check")


def _Defecto(valor: StrEnum) -> TextClause:
    return text(f"'{valor}'")


def _Objeto(columna: str, tabla: str) -> CheckConstraint:
    return CheckConstraint(f"jsonb_typeof({columna}) = 'object'", name=f"{tabla}_{columna}_check")


def _Check(tabla: str, columna: str, expresion: str) -> CheckConstraint:
    return CheckConstraint(expresion, name=f"{tabla}_{columna}_check")


class Usuario(Base):
    __tablename__ = "app_users"
    __table_args__ = (
        UniqueConstraint("auth_issuer", "auth_subject", name="app_users_issuer_subject_uk"),
        _Check("app_users", "display_name", "char_length(display_name) BETWEEN 1 AND 120"),
        _Valores("status", "app_users", EstadoUsuario),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    auth_issuer: Mapped[str]
    auth_subject: Mapped[str]
    email: Mapped[str | None]
    display_name: Mapped[str]
    status: Mapped[str] = mapped_column(server_default=_Defecto(EstadoUsuario.ACTIVE))
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    updated_at: Mapped[datetime] = mapped_column(server_default=AHORA)


class SesionAutenticacion(Base):
    """Sesión de servidor tras el login OIDC; la cookie solo lleva el token."""

    __tablename__ = "auth_sessions"
    __table_args__ = (
        _Sha("token_sha256", "auth_sessions"),
        CheckConstraint("expires_at > created_at", name="auth_sessions_check"),
        Index("auth_sessions_user_idx", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("app_users.id"))
    token_sha256: Mapped[str] = mapped_column(CHAR(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    expires_at: Mapped[datetime]
    revoked_at: Mapped[datetime | None]


class PreferenciaUsuario(Base):
    __tablename__ = "user_preferences"
    __table_args__ = (
        _Check("user_preferences", "display_currency", "display_currency ~ '^[A-Z]{3}$'"),
        _Objeto("default_parameters", "user_preferences"),
        _Check("user_preferences", "revision", "revision > 0"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("app_users.id"), primary_key=True)
    auto_scale: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    locale: Mapped[str] = mapped_column(server_default=text("'es-CO'"))
    display_currency: Mapped[str | None]
    default_parameters: Mapped[dict[str, Any]] = mapped_column(server_default=OBJETO_VACIO)
    revision: Mapped[int] = mapped_column(server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    updated_at: Mapped[datetime] = mapped_column(server_default=AHORA)


class ArchivoAlmacenado(Base):
    __tablename__ = "file_assets"
    __table_args__ = (
        UniqueConstraint("user_id", "id", name="file_assets_user_id_uk"),
        _Valores("kind", "file_assets", TipoAsset),
        _Check("file_assets", "original_name", "char_length(original_name) <= 255"),
        _Check("file_assets", "size_bytes", "size_bytes >= 0"),
        _Sha("sha256", "file_assets"),
        _Valores("status", "file_assets", EstadoAsset),
        CheckConstraint(
            f"status <> '{EstadoAsset.READY}' OR (object_url IS NOT NULL AND ready_at IS NOT NULL)",
            name="file_assets_ready_url_ck",
        ),
        CheckConstraint(
            f"status <> '{EstadoAsset.STAGED}' OR object_url IS NULL", name="file_assets_staged_sin_url_ck"
        ),
        Index("file_assets_user_sha_idx", "user_id", "sha256"),
        Index("file_assets_status_created_idx", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("app_users.id"))
    storage_key: Mapped[str] = mapped_column(unique=True)
    object_url: Mapped[str | None]
    kind: Mapped[str]
    original_name: Mapped[str | None]
    media_type: Mapped[str]
    size_bytes: Mapped[int]
    sha256: Mapped[str] = mapped_column(CHAR(64))
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    ready_at: Mapped[datetime | None]
    deleted_at: Mapped[datetime | None]


class Proyecto(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("user_id", "id", name="projects_user_id_uk"),
        _Check("projects", "name", "char_length(name) BETWEEN 1 AND 120"),
        _Check("projects", "description", "char_length(description) <= 2000"),
        _Check("projects", "next_version_number", "next_version_number > 0"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("app_users.id"))
    name: Mapped[str]
    description: Mapped[str | None]
    next_version_number: Mapped[int] = mapped_column(server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    updated_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    archived_at: Mapped[datetime | None]


Index(
    "projects_user_updated_idx",
    Proyecto.user_id,
    Proyecto.updated_at.desc(),
    Proyecto.id.desc(),
    postgresql_where=Proyecto.archived_at.is_(None),
)


class Importacion(Base):
    __tablename__ = "imports"
    __table_args__ = (
        UniqueConstraint("user_id", "id", name="imports_user_id_uk"),
        UniqueConstraint("user_id", "project_id", "id", name="imports_user_project_id_uk"),
        ForeignKeyConstraint(
            ["user_id", "project_id"], ["projects.user_id", "projects.id"], name="imports_project_fk"
        ),
        ForeignKeyConstraint(
            ["user_id", "original_asset_id"],
            ["file_assets.user_id", "file_assets.id"],
            name="imports_original_fk",
        ),
        ForeignKeyConstraint(
            ["user_id", "normalized_asset_id"],
            ["file_assets.user_id", "file_assets.id"],
            name="imports_normalized_fk",
        ),
        _Valores("source_kind", "imports", OrigenImport),
        _Valores("status", "imports", EstadoImport),
        _Valores("format", "imports", FormatoImport),
        _Check("imports", "vertex_count", "vertex_count >= 0"),
        _Check("imports", "face_count", "face_count >= 0"),
        _Check(
            "imports",
            "raw_dimensions_mm",
            "raw_dimensions_mm IS NULL OR (jsonb_typeof(raw_dimensions_mm) = 'array'"
            " AND jsonb_array_length(raw_dimensions_mm) = 3)",
        ),
        _Check("imports", "normalization_schema_version", "normalization_schema_version > 0"),
        _Check("imports", "error_message", "char_length(error_message) <= 500"),
        CheckConstraint(
            f"status <> '{EstadoImport.READY}' OR normalized_asset_id IS NOT NULL", name="imports_ready_normalizado_ck"
        ),
        Index("imports_normalized_idx", "user_id", "normalized_asset_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID]
    project_id: Mapped[uuid.UUID]
    original_asset_id: Mapped[uuid.UUID]
    normalized_asset_id: Mapped[uuid.UUID | None]
    source_kind: Mapped[str]
    status: Mapped[str]
    format: Mapped[str]
    vertex_count: Mapped[int | None]
    face_count: Mapped[int | None]
    raw_dimensions_mm: Mapped[list[Any] | None]
    reader_version: Mapped[str]
    normalization_schema_version: Mapped[int] = mapped_column(Integer)
    error_code: Mapped[str | None]
    error_message: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    finished_at: Mapped[datetime | None]


Index(
    "imports_user_project_created_idx",
    Importacion.user_id,
    Importacion.project_id,
    Importacion.created_at.desc(),
    Importacion.id.desc(),
)


class VersionModelo(Base):
    """Versión inmutable; el trigger ``model_versions_comprobar`` valida import y padre."""

    __tablename__ = "model_versions"
    __table_args__ = (
        UniqueConstraint("project_id", "version_number", name="model_versions_project_number_uk"),
        UniqueConstraint("user_id", "id", name="model_versions_user_id_uk"),
        UniqueConstraint("user_id", "project_id", "id", name="model_versions_user_project_id_uk"),
        ForeignKeyConstraint(
            ["user_id", "project_id"], ["projects.user_id", "projects.id"], name="model_versions_project_fk"
        ),
        ForeignKeyConstraint(
            ["user_id", "project_id", "import_id"],
            ["imports.user_id", "imports.project_id", "imports.id"],
            name="model_versions_import_fk",
        ),
        ForeignKeyConstraint(
            ["user_id", "project_id", "parent_version_id"],
            ["model_versions.user_id", "model_versions.project_id", "model_versions.id"],
            name="model_versions_parent_fk",
        ),
        _Check("model_versions", "version_number", "version_number > 0"),
        _Check("model_versions", "label", "char_length(label) <= 120"),
        _Check("model_versions", "change_note", "char_length(change_note) <= 2000"),
        _Objeto("parameters", "model_versions"),
        _Check("model_versions", "parameter_schema_version", "parameter_schema_version > 0"),
        _Objeto("material_snapshot", "model_versions"),
        _Valores("requested_backend", "model_versions", BackendGeneracion),
        _Sha("parameters_sha256", "model_versions"),
        CheckConstraint(
            "parent_version_id IS NULL OR parent_version_id <> id", name="model_versions_parent_distinto_ck"
        ),
        Index("model_versions_import_idx", "user_id", "project_id", "import_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID]
    project_id: Mapped[uuid.UUID]
    import_id: Mapped[uuid.UUID]
    parent_version_id: Mapped[uuid.UUID | None]
    version_number: Mapped[int]
    label: Mapped[str | None]
    change_note: Mapped[str | None]
    parameters: Mapped[dict[str, Any]]
    parameter_schema_version: Mapped[int] = mapped_column(Integer)
    auto_scale: Mapped[bool]
    material_snapshot: Mapped[dict[str, Any]]
    requested_backend: Mapped[str]
    parameters_sha256: Mapped[str] = mapped_column(CHAR(64))
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)


Index(
    "model_versions_user_project_created_idx",
    VersionModelo.user_id,
    VersionModelo.project_id,
    VersionModelo.created_at.desc(),
    VersionModelo.id.desc(),
)


class LoteGeneracion(Base):
    __tablename__ = "generation_batches"
    __table_args__ = (
        UniqueConstraint("user_id", "request_id", name="generation_batches_request_uk"),
        UniqueConstraint("user_id", "id", name="generation_batches_user_id_uk"),
        UniqueConstraint("user_id", "project_id", "id", name="generation_batches_user_project_id_uk"),
        ForeignKeyConstraint(
            ["user_id", "project_id"], ["projects.user_id", "projects.id"], name="generation_batches_project_fk"
        ),
        _Sha("request_sha256", "generation_batches"),
        _Valores("mode", "generation_batches", ModoLote),
        _Objeto("definition", "generation_batches"),
        _Valores("status", "generation_batches", EstadoLote),
        _Check("generation_batches", "total_items", "total_items BETWEEN 1 AND 12"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID]
    project_id: Mapped[uuid.UUID]
    request_id: Mapped[uuid.UUID]
    request_sha256: Mapped[str] = mapped_column(CHAR(64))
    mode: Mapped[str]
    definition: Mapped[dict[str, Any]]
    status: Mapped[str] = mapped_column(server_default=_Defecto(EstadoLote.QUEUED))
    total_items: Mapped[int] = mapped_column(Integer)
    cancel_requested_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    started_at: Mapped[datetime | None]
    finished_at: Mapped[datetime | None]


Index(
    "generation_batches_user_created_idx",
    LoteGeneracion.user_id,
    LoteGeneracion.created_at.desc(),
    LoteGeneracion.id.desc(),
)
Index(
    "generation_batches_user_status_idx",
    LoteGeneracion.user_id,
    LoteGeneracion.status,
    LoteGeneracion.created_at.desc(),
)


class ItemLoteGeneracion(Base):
    __tablename__ = "batch_items"
    __table_args__ = (
        UniqueConstraint("batch_id", "position", name="batch_items_batch_position_uk"),
        UniqueConstraint("user_id", "id", name="batch_items_user_id_uk"),
        ForeignKeyConstraint(
            ["user_id", "project_id", "batch_id"],
            ["generation_batches.user_id", "generation_batches.project_id", "generation_batches.id"],
            name="batch_items_batch_fk",
        ),
        ForeignKeyConstraint(
            ["user_id", "project_id", "version_id"],
            ["model_versions.user_id", "model_versions.project_id", "model_versions.id"],
            name="batch_items_version_fk",
        ),
        # Referencia circular: se crea después de generation_attempts.
        ForeignKeyConstraint(
            ["user_id", "id", "winning_attempt_id"],
            ["generation_attempts.user_id", "generation_attempts.batch_item_id", "generation_attempts.id"],
            name="batch_items_winning_attempt_fk",
            use_alter=True,
        ),
        _Check("batch_items", "position", "position >= 0"),
        _Valores("status", "batch_items", EstadoItem),
        _Check("batch_items", "attempt_count", "attempt_count >= 0"),
        _Check("batch_items", "max_attempts", "max_attempts > 0"),
        CheckConstraint("attempt_count <= max_attempts", name="batch_items_intentos_ck"),
        CheckConstraint(
            f"status <> '{EstadoItem.RUNNING}' OR (lease_token IS NOT NULL AND lease_expires_at IS NOT NULL)",
            name="batch_items_running_lease_ck",
        ),
        CheckConstraint(
            f"status <> '{EstadoItem.SUCCEEDED}' OR winning_attempt_id IS NOT NULL", name="batch_items_ganador_ck"
        ),
        Index("batch_items_user_status_idx", "user_id", "status"),
        Index("batch_items_version_idx", "user_id", "project_id", "version_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID]
    project_id: Mapped[uuid.UUID]
    batch_id: Mapped[uuid.UUID]
    version_id: Mapped[uuid.UUID]
    position: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(server_default=_Defecto(EstadoItem.QUEUED))
    attempt_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    max_attempts: Mapped[int] = mapped_column(Integer, server_default=text("3"))
    available_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    lease_token: Mapped[uuid.UUID | None]
    lease_expires_at: Mapped[datetime | None]
    winning_attempt_id: Mapped[uuid.UUID | None]
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    updated_at: Mapped[datetime] = mapped_column(server_default=AHORA)


Index(
    "batch_items_queued_idx",
    ItemLoteGeneracion.available_at,
    ItemLoteGeneracion.created_at,
    ItemLoteGeneracion.id,
    postgresql_where=ItemLoteGeneracion.status == EstadoItem.QUEUED,
)
Index(
    "batch_items_running_lease_idx",
    ItemLoteGeneracion.lease_expires_at,
    postgresql_where=ItemLoteGeneracion.status == EstadoItem.RUNNING,
)


class IntentoGeneracion(Base):
    __tablename__ = "generation_attempts"
    __table_args__ = (
        UniqueConstraint("batch_item_id", "attempt_number", name="generation_attempts_item_number_uk"),
        UniqueConstraint("user_id", "id", name="generation_attempts_user_id_uk"),
        UniqueConstraint("user_id", "batch_item_id", "id", name="generation_attempts_user_item_id_uk"),
        ForeignKeyConstraint(
            ["user_id", "batch_item_id"],
            ["batch_items.user_id", "batch_items.id"],
            name="generation_attempts_item_fk",
        ),
        _Check("generation_attempts", "attempt_number", "attempt_number > 0"),
        _Valores("status", "generation_attempts", EstadoIntento),
        _Objeto("runtime_snapshot", "generation_attempts"),
        _Check(
            "generation_attempts",
            "effective_scale",
            "effective_scale > 0 AND effective_scale < 'Infinity'",
        ),
        _Check(
            "generation_attempts",
            "effective_step_mm",
            "effective_step_mm > 0 AND effective_step_mm < 'Infinity'",
        ),
        _Objeto("execution_parameters", "generation_attempts"),
        _Check("generation_attempts", "error_message", "char_length(error_message) <= 500"),
        _Check("generation_attempts", "duration_ms", "duration_ms >= 0"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID]
    batch_item_id: Mapped[uuid.UUID]
    attempt_number: Mapped[int] = mapped_column(Integer)
    worker_id: Mapped[str]
    lease_token: Mapped[uuid.UUID]
    status: Mapped[str] = mapped_column(server_default=_Defecto(EstadoIntento.RUNNING))
    generator_version: Mapped[str]
    code_revision: Mapped[str]
    runtime_snapshot: Mapped[dict[str, Any]]
    effective_scale: Mapped[float | None]
    effective_step_mm: Mapped[float | None]
    execution_parameters: Mapped[dict[str, Any]]
    error_code: Mapped[str | None]
    error_message: Mapped[str | None]
    retryable: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    started_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    heartbeat_at: Mapped[datetime] = mapped_column(server_default=AHORA)
    finished_at: Mapped[datetime | None]
    duration_ms: Mapped[int | None]


Index(
    "generation_attempts_running_uk",
    IntentoGeneracion.batch_item_id,
    unique=True,
    postgresql_where=IntentoGeneracion.status == EstadoIntento.RUNNING,
)


class ResultadoGeneracion(Base):
    __tablename__ = "generation_results"
    __table_args__ = (
        UniqueConstraint("user_id", "attempt_id", name="generation_results_attempt_uk"),
        UniqueConstraint("user_id", "id", name="generation_results_user_id_uk"),
        ForeignKeyConstraint(
            ["user_id", "batch_item_id", "attempt_id"],
            ["generation_attempts.user_id", "generation_attempts.batch_item_id", "generation_attempts.id"],
            name="generation_results_attempt_fk",
        ),
        _Check("generation_results", "volume_mm3", "volume_mm3 >= 0 AND volume_mm3 < 'Infinity'"),
        _Check("generation_results", "weight_g", "weight_g >= 0 AND weight_g < 'Infinity'"),
        _Check("generation_results", "estimated_price", "estimated_price >= 0"),
        _Check("generation_results", "price_per_gram", "price_per_gram >= 0"),
        _Check("generation_results", "density_g_cm3", "density_g_cm3 > 0"),
        _Check("generation_results", "currency", "currency ~ '^[A-Z]{3}$'"),
        _Check("generation_results", "vertices", "vertices >= 0"),
        _Check("generation_results", "triangles", "triangles >= 0"),
        _Check(
            "generation_results",
            "dimensions_mm",
            "jsonb_typeof(dimensions_mm) = 'array' AND jsonb_array_length(dimensions_mm) = 3",
        ),
        _Valores("validation_status", "generation_results", EstadoValidacion),
        _Check("generation_results", "warnings", "jsonb_typeof(warnings) = 'array'"),
        _Valores("geometry_scope", "generation_results", AlcanceGeometria),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID]
    batch_item_id: Mapped[uuid.UUID]
    attempt_id: Mapped[uuid.UUID]
    volume_mm3: Mapped[float]
    weight_g: Mapped[float]
    estimated_price: Mapped[Decimal]
    price_per_gram: Mapped[Decimal]
    density_g_cm3: Mapped[Decimal]
    currency: Mapped[str | None]
    vertices: Mapped[int]
    triangles: Mapped[int]
    dimensions_mm: Mapped[list[Any]]
    validation_status: Mapped[str] = mapped_column(server_default=_Defecto(EstadoValidacion.NOT_CHECKED))
    validation_report: Mapped[dict[str, Any]] = mapped_column(server_default=OBJETO_VACIO)
    warnings: Mapped[list[Any]] = mapped_column(server_default=text("'[]'::jsonb"))
    geometry_scope: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)


class Exportacion(Base):
    __tablename__ = "exports"
    __table_args__ = (
        UniqueConstraint("user_id", "result_id", "format", name="exports_result_format_uk"),
        UniqueConstraint("user_id", "id", name="exports_user_id_uk"),
        ForeignKeyConstraint(
            ["user_id", "result_id"],
            ["generation_results.user_id", "generation_results.id"],
            name="exports_result_fk",
        ),
        ForeignKeyConstraint(
            ["user_id", "asset_id"], ["file_assets.user_id", "file_assets.id"], name="exports_asset_fk"
        ),
        _Valores("format", "exports", FormatoExport),
        _Valores("units", "exports", UnidadExport),
        _Valores("status", "exports", EstadoExport),
        Index("exports_asset_idx", "user_id", "asset_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID]
    result_id: Mapped[uuid.UUID]
    asset_id: Mapped[uuid.UUID]
    format: Mapped[str]
    units: Mapped[str]
    exporter_version: Mapped[str]
    status: Mapped[str] = mapped_column(server_default=_Defecto(EstadoExport.READY))
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)


class EventoHistorial(Base):
    """Historial append-only: los roles de aplicación no tienen UPDATE ni DELETE."""

    __tablename__ = "history_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "project_id"], ["projects.user_id", "projects.id"], name="history_events_project_fk"
        ),
        ForeignKeyConstraint(
            ["user_id", "version_id"],
            ["model_versions.user_id", "model_versions.id"],
            name="history_events_version_fk",
        ),
        ForeignKeyConstraint(
            ["user_id", "batch_id"],
            ["generation_batches.user_id", "generation_batches.id"],
            name="history_events_batch_fk",
        ),
        ForeignKeyConstraint(
            ["user_id", "attempt_id"],
            ["generation_attempts.user_id", "generation_attempts.id"],
            name="history_events_attempt_fk",
        ),
        ForeignKeyConstraint(
            ["user_id", "export_id"], ["exports.user_id", "exports.id"], name="history_events_export_fk"
        ),
        _Valores("event_type", "history_events", TipoEvento),
        _Check(
            "history_events",
            "payload",
            "jsonb_typeof(payload) = 'object' AND pg_column_size(payload) <= 16384",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("app_users.id"))
    project_id: Mapped[uuid.UUID]
    version_id: Mapped[uuid.UUID | None]
    batch_id: Mapped[uuid.UUID | None]
    attempt_id: Mapped[uuid.UUID | None]
    export_id: Mapped[uuid.UUID | None]
    event_type: Mapped[str]
    payload: Mapped[dict[str, Any]] = mapped_column(server_default=OBJETO_VACIO)
    created_at: Mapped[datetime] = mapped_column(server_default=AHORA)


Index(
    "history_events_user_created_idx",
    EventoHistorial.user_id,
    EventoHistorial.created_at.desc(),
    EventoHistorial.id.desc(),
)
Index(
    "history_events_user_project_created_idx",
    EventoHistorial.user_id,
    EventoHistorial.project_id,
    EventoHistorial.created_at.desc(),
    EventoHistorial.id.desc(),
)
