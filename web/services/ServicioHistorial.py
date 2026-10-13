"""Historial por usuario: listado paginado, detalle, restauración y reintento.

El cursor es ``(created_at, id)`` codificado; no lleva autorización: cada
consulta vuelve a filtrar por el usuario activo.
"""

from __future__ import annotations

import base64
import uuid
from datetime import datetime
from uuid import UUID

from web.ConfiguracionBackend import ConfiguracionBackend
from web.enums import EstadoExport, EstadoItem, ModoLote, TipoEvento
from web.persistence.ConexionPostgres import ConexionPostgres
from web.persistence.Contratos import (
    AccesoDenegado,
    DetalleVersion,
    LoteDTO,
    PaginaHistorial,
    SolicitudLote,
    UsuarioAutenticado,
)
from web.persistence.repositorios import (
    RepositorioHistorial,
    RepositorioImports,
    RepositorioResultados,
    RepositorioVersiones,
)

from .ServicioLotes import ServicioLotes

_CONFIG = ConfiguracionBackend.Cargar("persistencia")["historial"]
LIMITE_DEFECTO = _CONFIG["limite_defecto"]
LIMITE_MAXIMO = _CONFIG["limite_maximo"]
MAXIMO_COMPARACION = _CONFIG["maximo_comparacion"]


class ServicioHistorial:
    @staticmethod
    def CodificarCursor(fecha: datetime, identificador: UUID) -> str:
        texto = f"{fecha.isoformat()}|{identificador}"
        return base64.urlsafe_b64encode(texto.encode("utf-8")).decode("ascii")

    @staticmethod
    def DecodificarCursor(cursor: str) -> tuple[datetime, UUID]:
        try:
            fecha, identificador = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8").split("|")
            return datetime.fromisoformat(fecha), UUID(identificador)
        except (ValueError, UnicodeError) as exc:
            raise ValueError("El cursor de la página no es válido.") from exc

    @staticmethod
    def Listar(
        usuario: UsuarioAutenticado, filtros: dict, cursor: str | None = None, limite: int = LIMITE_DEFECTO
    ) -> PaginaHistorial:
        limite = max(1, min(int(limite), LIMITE_MAXIMO))
        estado = filtros.get("status") or None
        if estado is not None and estado not in EstadoItem:
            raise ValueError("Estado de filtro desconocido.")
        limpios = {
            "project_id": UUID(str(filtros["project_id"])) if filtros.get("project_id") else None,
            "pattern": filtros.get("pattern") or None,
            "status": estado,
            "desde": filtros.get("desde"),
            "hasta": filtros.get("hasta"),
        }
        posicion = ServicioHistorial.DecodificarCursor(cursor) if cursor else None
        filas, hay_mas = ConexionPostgres.Ejecutar(
            lambda conexion: RepositorioHistorial.Listar(conexion, usuario.user_id, limpios, posicion, limite)
        )
        siguiente = (
            ServicioHistorial.CodificarCursor(filas[-1].created_at, filas[-1].item_id) if hay_mas and filas else None
        )
        return PaginaHistorial(filas, siguiente)

    @staticmethod
    def Detalle(usuario: UsuarioAutenticado, version_id: UUID) -> DetalleVersion:
        def leer(conexion) -> DetalleVersion:
            version = RepositorioVersiones.Obtener(conexion, usuario.user_id, version_id)
            importacion = RepositorioImports.Obtener(conexion, usuario.user_id, version.import_id)
            padre = None
            if version.parent_version_id is not None:
                padre = RepositorioVersiones.Obtener(conexion, usuario.user_id, version.parent_version_id).parameters
            return DetalleVersion(
                version=version,
                importacion=importacion,
                parametros_padre=padre,
                intentos=RepositorioResultados.Intentos(conexion, usuario.user_id, version_id),
                resultados=RepositorioResultados.DeVersion(conexion, usuario.user_id, version_id),
                eventos=RepositorioHistorial.EventosDeVersion(conexion, usuario.user_id, version_id),
            )

        return ConexionPostgres.Ejecutar(leer)

    @staticmethod
    def Comparar(usuario: UsuarioAutenticado, version_ids: list[UUID]) -> list[DetalleVersion]:
        if not 1 <= len(version_ids) <= MAXIMO_COMPARACION:
            raise ValueError(f"Compare de 1 a {MAXIMO_COMPARACION} versiones.")
        return [ServicioHistorial.Detalle(usuario, version_id) for version_id in version_ids]

    @staticmethod
    def Restaurar(usuario: UsuarioAutenticado, version_id: UUID, request_id: UUID | None = None) -> LoteDTO:
        """Crea una versión nueva con los parámetros de otra; no modifica la original."""
        version = ConexionPostgres.Ejecutar(
            lambda conexion: RepositorioVersiones.Obtener(conexion, usuario.user_id, version_id)
        )
        return ServicioLotes.Solicitar(
            usuario,
            SolicitudLote(
                import_id=version.import_id,
                request_id=request_id or uuid.uuid4(),
                mode=ModoLote.SINGLE,
                definition={"origen": "restaurar", "version_id": str(version.id)},
                variantes=[version.parameters],
                auto_scale=version.auto_scale,
                parent_version_id=version.id,
                change_note=f"Restaurada desde la versión {version.version_number}.",
            ),
        )

    @staticmethod
    def Reintentar(usuario: UsuarioAutenticado, version_ids: list[UUID], request_id: UUID | None = None) -> LoteDTO:
        """Nuevo lote ``retry`` sobre versiones existentes: nuevos intentos, mismas versiones."""
        versiones = [
            ConexionPostgres.Ejecutar(lambda conexion, v=v: RepositorioVersiones.Obtener(conexion, usuario.user_id, v))
            for v in version_ids
        ]
        if not versiones or len({version.import_id for version in versiones}) != 1:
            raise AccesoDenegado("Reintente versiones de una misma superficie.")
        return ServicioLotes.Solicitar(
            usuario,
            SolicitudLote(
                import_id=versiones[0].import_id,
                request_id=request_id or uuid.uuid4(),
                mode=ModoLote.RETRY,
                definition={"origen": "reintentar"},
                variantes=[],
                auto_scale=versiones[0].auto_scale,
                version_ids=[version.id for version in versiones],
            ),
        )

    @staticmethod
    def RegistrarDescarga(usuario: UsuarioAutenticado, asset_id: UUID) -> str:
        """Devuelve la object_url del STL del usuario y registra la descarga."""

        def registrar(conexion) -> str:
            export = RepositorioResultados.ExportStl(conexion, usuario.user_id, asset_id)
            if export is None:
                raise AccesoDenegado()
            if export["status"] != EstadoExport.READY or not export["object_url"]:
                raise AccesoDenegado("El STL ya no está en el almacén.")
            RepositorioHistorial.Evento(
                conexion, usuario.user_id, export["project_id"], TipoEvento.EXPORT_DOWNLOADED,
                version_id=export["version_id"], batch_id=export["batch_id"], export_id=export["export_id"],
            )
            return export["object_url"]

        return ConexionPostgres.Ejecutar(registrar)
