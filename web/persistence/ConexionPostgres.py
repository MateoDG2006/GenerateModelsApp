"""Motor SQLAlchemy y sesiones por proceso.

Los handlers de Reflex llaman a los servicios con ``asyncio.to_thread``. Las
transacciones son cortas: nunca abarcan geometría ni transferencias de archivos.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import TypeVar

from psycopg import errors
from sqlalchemy import Engine, create_engine, exc
from sqlalchemy.orm import Session, sessionmaker

from GenerateModelsApp.util.Utilidades import Registro
from web.ConfiguracionBackend import ConfiguracionBackend

from .Contratos import PersistenciaNoDisponible

T = TypeVar("T")

REINTENTABLES = (errors.SerializationFailure, errors.DeadlockDetected)
_CONFIG = ConfiguracionBackend.Cargar("persistencia")["conexion"]


class ConexionPostgres:
    _motor: Engine | None = None
    _sesiones: sessionmaker[Session] | None = None
    REINTENTOS = _CONFIG["reintentos"]
    ESPERA_ADQUISICION_S = _CONFIG["espera_adquisicion_s"]

    @staticmethod
    def Abrir(dsn: str, minimo: int = 1, maximo: int = 4, nombre: str = "backend") -> None:
        if ConexionPostgres._motor is not None:
            return
        motor = create_engine(
            dsn,
            pool_size=maximo,
            max_overflow=0,
            pool_timeout=ConexionPostgres.ESPERA_ADQUISICION_S,
            pool_pre_ping=True,
            connect_args={"connect_timeout": _CONFIG["timeout_conexion_s"], "application_name": f"ortesislab-{nombre}"},
        )
        try:
            # Abre las conexiones mínimas para fallar al arrancar y no en la primera petición.
            conexiones = [motor.connect() for _ in range(max(1, minimo))]
            for conexion in conexiones:
                conexion.close()
        except exc.DBAPIError as error:
            motor.dispose()
            raise PersistenciaNoDisponible("No se pudo conectar con PostgreSQL.") from error
        ConexionPostgres._motor = motor
        ConexionPostgres._sesiones = sessionmaker(bind=motor, expire_on_commit=False)
        Registro.Obtener("persistencia").info("Motor PostgreSQL %s abierto (%s-%s).", nombre, minimo, maximo)

    @staticmethod
    def Cerrar() -> None:
        motor, ConexionPostgres._motor = ConexionPostgres._motor, None
        ConexionPostgres._sesiones = None
        if motor is not None:
            motor.dispose()

    @staticmethod
    def Abierta() -> bool:
        return ConexionPostgres._motor is not None

    @staticmethod
    @contextmanager
    def Transaccion() -> Iterator[Session]:
        # Commit al salir sin error; rollback ante cualquier excepción.
        sesiones = ConexionPostgres._sesiones
        if sesiones is None:
            raise PersistenciaNoDisponible("La base de datos no está abierta en este proceso.")
        try:
            with sesiones.begin() as sesion:
                yield sesion
        except exc.TimeoutError as error:
            raise PersistenciaNoDisponible("La base de datos no respondió a tiempo.") from error
        except exc.OperationalError as error:
            if isinstance(error.orig, REINTENTABLES):
                raise
            raise PersistenciaNoDisponible("La base de datos no está disponible.") from error

    @staticmethod
    def Ejecutar(funcion: Callable[[Session], T]) -> T:
        # Repite transacciones cortas ante deadlock o fallo de serialización.
        for intento in range(1, ConexionPostgres.REINTENTOS + 1):
            try:
                with ConexionPostgres.Transaccion() as sesion:
                    return funcion(sesion)
            except exc.DBAPIError as error:
                if not isinstance(error.orig, REINTENTABLES) or intento == ConexionPostgres.REINTENTOS:
                    raise
                time.sleep(_CONFIG["pausa_reintento_s"] * intento)
        raise AssertionError("inalcanzable")
