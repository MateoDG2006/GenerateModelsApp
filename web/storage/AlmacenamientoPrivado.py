"""Contrato del almacén de bytes y claves de objeto.

La clave la genera el servidor: ``usuarios/<user_id>/assets/<asset_id>``. La URL
canónica es la base pública del bucket más esa clave; no lleva firma ni
credenciales. Solo hay una implementación: ``StorageS3``.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
from datetime import datetime
from typing import Protocol
from uuid import UUID

from web.persistence.Contratos import ErrorPersistencia

PATRON_CLAVE = re.compile(
    r"usuarios/(?P<user>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
    r"/assets/(?P<asset>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:\.stl)?"
)


class AlmacenamientoNoDisponible(ErrorPersistencia):
    def __init__(self, mensaje: str = "El almacén de archivos no responde."):
        super().__init__(mensaje)


class ObjetoAusente(ErrorPersistencia):
    def __init__(self, mensaje: str = "El archivo ya no está en el almacén."):
        super().__init__(mensaje)


class AlmacenamientoPrivado(Protocol):
    def Url(self, clave: str) -> str: ...

    def Publicar(self, clave: str, datos: bytes, media_type: str, sha256: str, nombre: str | None = None) -> str:
        """Sube el objeto completo, comprueba tamaño y hash, y devuelve su URL."""
        ...

    def Leer(self, clave: str) -> bytes: ...

    def Existe(self, clave: str) -> bool: ...

    def Borrar(self, clave: str) -> None: ...

    def Claves(self, prefijo: str) -> Iterator[tuple[str, datetime]]:
        """Clave y fecha de última modificación de cada objeto bajo el prefijo."""
        ...


class Almacen:
    """Instancia de proceso. Las pruebas la sustituyen con ``Usar``."""

    _actual: AlmacenamientoPrivado | None = None

    @staticmethod
    def Actual() -> AlmacenamientoPrivado:
        if Almacen._actual is None:
            from .StorageS3 import StorageS3

            Almacen._actual = StorageS3.DesdeAjustes()
        return Almacen._actual

    @staticmethod
    def Usar(almacen: AlmacenamientoPrivado | None) -> None:
        Almacen._actual = almacen

    @staticmethod
    def Clave(user_id: UUID, asset_id: UUID, stl_publico: bool = False) -> str:
        # La política del bucket solo concede lectura anónima a claves que terminan en .stl.
        return f"usuarios/{user_id}/assets/{asset_id}{'.stl' if stl_publico else ''}"

    @staticmethod
    def Sha256(datos: bytes) -> str:
        return hashlib.sha256(datos).hexdigest()

    @staticmethod
    def LeerVerificado(clave: str, sha256: str) -> bytes:
        datos = Almacen.Actual().Leer(clave)
        if Almacen.Sha256(datos) != sha256:
            raise ObjetoAusente("El archivo del almacén no coincide con su hash registrado.")
        return datos
