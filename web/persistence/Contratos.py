"""DTO y errores de la persistencia. No son entidades ORM.

Importes en Decimal, geometría en float finito, UUID y fechas UTC.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from web.ConfiguracionBackend import ConfiguracionBackend
from web.enums import ITEMS_TERMINALES, LOTES_ABIERTOS

ESQUEMA_PARAMETROS = 1
ESQUEMA_NORMALIZACION = 1
VERSION_LECTOR = "LectorSuperficie-1"
VERSION_EXPORTADOR = "GeneradorWeb.Stl-1"

_LOTES = ConfiguracionBackend.Cargar("persistencia")["lotes"]
MAXIMO_ITEMS_LOTE = _LOTES["maximo_items"]
MAXIMO_LOTES_PENDIENTES = _LOTES["maximo_pendientes"]
MAXIMO_INTENTOS = _LOTES["maximo_intentos"]


class ErrorPersistencia(Exception):
    """Error previsto con un mensaje que se puede mostrar."""


class PersistenciaNoDisponible(ErrorPersistencia):
    pass


class SesionInvalida(ErrorPersistencia):
    def __init__(self, mensaje: str = "Inicie sesión para guardar y consultar su trabajo."):
        super().__init__(mensaje)


class AccesoDenegado(ErrorPersistencia):
    def __init__(self, mensaje: str = "El recurso no existe o no le pertenece."):
        super().__init__(mensaje)


class SolicitudIdempotenteEnConflicto(ErrorPersistencia):
    def __init__(self):
        super().__init__("Esa solicitud ya se registró con otros parámetros.")


class ConflictoRevision(ErrorPersistencia):
    def __init__(self):
        super().__init__("Las preferencias cambiaron en otra pestaña. Se recargaron los valores guardados.")


class CuotaExcedida(ErrorPersistencia):
    pass


@dataclass(frozen=True)
class UsuarioAutenticado:
    user_id: UUID
    display_name: str
    email: str | None
    project_id: UUID


@dataclass(frozen=True)
class Asset:
    id: UUID
    user_id: UUID
    storage_key: str
    object_url: str | None
    kind: str
    original_name: str | None
    media_type: str
    size_bytes: int
    sha256: str
    status: str


@dataclass(frozen=True)
class ImportDTO:
    id: UUID
    project_id: UUID
    original_asset_id: UUID
    normalized_asset_id: UUID | None
    source_kind: str
    status: str
    format: str
    vertex_count: int | None
    face_count: int | None
    raw_dimensions_mm: list[float] | None
    error_code: str | None
    error_message: str | None
    created_at: datetime


@dataclass(frozen=True)
class VersionDTO:
    id: UUID
    project_id: UUID
    import_id: UUID
    parent_version_id: UUID | None
    version_number: int
    label: str | None
    change_note: str | None
    parameters: dict[str, Any]
    auto_scale: bool
    material_snapshot: dict[str, Any]
    parameters_sha256: str
    created_at: datetime


@dataclass(frozen=True)
class SolicitudLote:
    """Variantes ya expandidas y validadas por ``GeneradorWeb.Combinaciones``."""

    import_id: UUID
    request_id: UUID
    mode: str
    definition: dict[str, Any]
    variantes: list[dict[str, Any]]
    auto_scale: bool
    parent_version_id: UUID | None = None
    change_note: str | None = None
    version_ids: list[UUID] | None = None


@dataclass(frozen=True)
class LoteDTO:
    id: UUID
    project_id: UUID
    request_id: UUID
    mode: str
    status: str
    total_items: int
    cancel_requested_at: datetime | None
    created_at: datetime
    finished_at: datetime | None


@dataclass(frozen=True)
class ResultadoDTO:
    id: UUID
    attempt_id: UUID
    volume_mm3: float
    weight_g: float
    estimated_price: Decimal
    currency: str | None
    vertices: int
    triangles: int
    dimensions_mm: list[float]
    validation_status: str
    warnings: list[str]
    effective_scale: float | None
    stl_asset_id: UUID | None
    stl_url: str | None
    stl_status: str | None


@dataclass(frozen=True)
class ItemLote:
    id: UUID
    batch_id: UUID
    position: int
    status: str
    version_id: UUID
    version_number: int
    parameters: dict[str, Any]
    attempt_count: int
    error_message: str | None
    resultado: ResultadoDTO | None


@dataclass(frozen=True)
class ProgresoLote:
    lote: LoteDTO
    items: list[ItemLote]

    @property
    def terminados(self) -> int:
        return sum(1 for item in self.items if item.status in ITEMS_TERMINALES)

    @property
    def abierto(self) -> bool:
        return self.lote.status in LOTES_ABIERTOS


@dataclass(frozen=True)
class TrabajoReservado:
    item_id: UUID
    attempt_id: UUID
    attempt_number: int
    lease_token: UUID
    user_id: UUID
    project_id: UUID
    batch_id: UUID
    version_id: UUID
    parameters: dict[str, Any]
    auto_scale: bool
    normalized_asset_id: UUID
    max_attempts: int
    material_snapshot: dict[str, Any]


@dataclass(frozen=True)
class ResultadoGeometrico:
    volume_mm3: float
    weight_g: float
    estimated_price: Decimal
    price_per_gram: Decimal
    density_g_cm3: Decimal
    currency: str | None
    vertices: int
    triangles: int
    dimensions_mm: list[float]
    effective_scale: float
    effective_step_mm: float | None
    warnings: list[str]
    configuracion: dict[str, Any]
    execution_parameters: dict[str, Any]


@dataclass(frozen=True)
class FilaHistorial:
    item_id: UUID
    batch_id: UUID
    version_id: UUID
    project_id: UUID
    project_name: str
    version_number: int
    pattern: str
    parameters: dict[str, Any]
    created_at: datetime
    status: str
    volume_mm3: float | None
    weight_g: float | None
    estimated_price: Decimal | None
    currency: str | None
    validation_status: str | None
    stl_url: str | None
    stl_status: str | None
    error_message: str | None


@dataclass(frozen=True)
class PaginaHistorial:
    filas: list[FilaHistorial]
    cursor_siguiente: str | None


@dataclass(frozen=True)
class IntentoDTO:
    id: UUID
    attempt_number: int
    status: str
    worker_id: str
    generator_version: str
    code_revision: str
    effective_scale: float | None
    effective_step_mm: float | None
    error_code: str | None
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None
    duration_ms: int | None


@dataclass(frozen=True)
class DetalleVersion:
    version: VersionDTO
    importacion: ImportDTO
    parametros_padre: dict[str, Any] | None
    intentos: list[IntentoDTO] = field(default_factory=list)
    resultados: list[ResultadoDTO] = field(default_factory=list)
    eventos: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class Preferencias:
    user_id: UUID
    auto_scale: bool
    locale: str
    display_currency: str | None
    default_parameters: dict[str, Any]
    revision: int
