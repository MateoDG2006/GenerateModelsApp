"""Apoyo de pruebas contra la base desechable ``ortesislab_test``.

Se omiten si no hay URL o si PostgreSQL no responde o no tiene el esquema.
Preparar la base según ``docs/AppBackend/OPERACION_Y_PRUEBAS.md``.
"""

from __future__ import annotations

import hashlib
import unittest
import uuid
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import Engine, create_engine, exc, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from web.Ajustes import Ajustes
from web.persistence.ConexionPostgres import ConexionPostgres
from web.persistence.Contratos import UsuarioAutenticado
from web.persistence.repositorios import (
    RepositorioAssets,
    RepositorioImports,
    RepositorioPreferencias,
    RepositorioProyectos,
    RepositorioUsuarios,
)

AJUSTES = Ajustes.Cargar()
FALTANTE = AJUSTES.Faltante("test_database_url", "test_worker_database_url")
URL_APP = "" if FALTANTE else AJUSTES.test_database_url
URL_TRABAJADOR = "" if FALTANTE else AJUSTES.test_worker_database_url


class SesionPrueba(Session):
    """Sesión directa de un rol: confirma al salir del ``with`` sin error."""

    def __exit__(self, tipo, valor, traza) -> None:
        if tipo is None:
            self.commit()
        else:
            self.rollback()
        self.close()


@lru_cache(maxsize=None)
def _Motor(url: str) -> Engine:
    return create_engine(url, poolclass=NullPool, connect_args={"connect_timeout": 3})


def Conectar(url: str = URL_APP) -> SesionPrueba:
    return SesionPrueba(_Motor(url))


@contextmanager
def ErrorDeBase(caso: unittest.TestCase, clase: type[Exception]):
    """Espera un error de PostgreSQL concreto envuelto por SQLAlchemy."""
    with caso.assertRaises(exc.DBAPIError) as contexto:
        yield
    caso.assertIsInstance(contexto.exception.orig, clase)


def _Disponible() -> str:
    if FALTANTE:
        return FALTANTE
    try:
        with Conectar() as conexion:
            conexion.execute(text("SELECT 1 FROM history_events LIMIT 1"))
    except exc.DBAPIError as error:
        return f"Base de pruebas no disponible o sin esquema: {error.orig}"
    return ""


MOTIVO_OMISION = _Disponible()
requiere_base = unittest.skipIf(bool(MOTIVO_OMISION), MOTIVO_OMISION)


class EntornoServicios:
    """Pool de la base de pruebas, S3 de moto por HTTP y Redis en la base 15.

    moto sustituye a MinIO solo en pruebas: habla la misma API S3 por HTTP.
    """

    def __init__(self, url: str = URL_APP):
        self.url = url

    def __enter__(self):
        import socket

        import redis
        from moto.server import ThreadedMotoServer

        from web.cache.CacheRedis import CacheRedis
        from web.storage.AlmacenamientoPrivado import Almacen
        from web.storage.StorageS3 import StorageS3

        with socket.socket() as libre:
            libre.bind(("127.0.0.1", 0))
            self.puerto = libre.getsockname()[1]
        self.servidor = ThreadedMotoServer(ip_address="127.0.0.1", port=self.puerto, verbose=False)
        self.servidor.start()
        endpoint = f"http://127.0.0.1:{self.puerto}"
        self.almacen = StorageS3(endpoint, endpoint, "prueba", "prueba", "ortesislab", "us-east-1")
        self.almacen.cliente.create_bucket(Bucket="ortesislab")
        Almacen.Usar(self.almacen)
        self.redis = redis.Redis(host="127.0.0.1", port=6379, db=15, socket_timeout=0.5)
        try:
            self.redis.flushdb()
            CacheRedis.Usar(self.redis)
        except redis.RedisError:
            self.redis = None
            CacheRedis.Usar(None)
        ConexionPostgres.Cerrar()
        ConexionPostgres.Abrir(self.url, 1, 3, "pruebas")
        return self

    def __exit__(self, *_):
        from web.cache.CacheRedis import CacheRedis
        from web.storage.AlmacenamientoPrivado import Almacen

        ConexionPostgres.Cerrar()
        Almacen.Usar(None)
        CacheRedis.Usar(None)
        self.servidor.stop()


class Rol:
    """Reabre el motor del proceso con otro rol: la web o el trabajador."""

    def __init__(self, url: str):
        self.url = url

    def __enter__(self):
        ConexionPostgres.Cerrar()
        ConexionPostgres.Abrir(self.url, 1, 3, "pruebas")
        return self

    def __exit__(self, *_):
        ConexionPostgres.Cerrar()
        ConexionPostgres.Abrir(URL_APP, 1, 3, "pruebas")


def CrearUsuario(conexion, nombre: str = "Prueba") -> UsuarioAutenticado:
    user_id = RepositorioUsuarios.Upsert(conexion, "urn:ortesislab:test", uuid.uuid4().hex, None, nombre)
    RepositorioPreferencias.Obtener(conexion, user_id)
    proyecto = RepositorioProyectos.Predeterminado(conexion, user_id)
    return UsuarioAutenticado(user_id, nombre, None, proyecto)


def CrearAssetListo(conexion, usuario: UsuarioAutenticado, kind: str = "surface_npz", contenido: bytes | None = None):
    asset_id = uuid.uuid4()
    datos = contenido if contenido is not None else uuid.uuid4().bytes
    clave = f"usuarios/{usuario.user_id}/assets/{asset_id}"
    RepositorioAssets.CrearStaged(
        conexion, usuario.user_id, asset_id, clave, kind, "prueba.npz", "application/octet-stream",
        len(datos), hashlib.sha256(datos).hexdigest(),
    )
    RepositorioAssets.MarcarListo(conexion, usuario.user_id, asset_id, f"http://s3.test/ortesislab/{clave}")
    return asset_id


def CrearImportListo(conexion, usuario: UsuarioAutenticado) -> uuid.UUID:
    original = CrearAssetListo(conexion, usuario, "import_original")
    normalizado = CrearAssetListo(conexion, usuario, "surface_npz")
    import_id = uuid.uuid4()
    RepositorioImports.Crear(conexion, usuario, import_id, original, "upload", "stl_binary", "prueba", 1)
    RepositorioImports.MarcarListo(conexion, usuario.user_id, import_id, normalizado, 4, 2, [100.0, 100.0, 0.0])
    return import_id
