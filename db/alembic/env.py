"""Entorno de Alembic: migra el esquema ortesislab con el rol migrador."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from web.Ajustes import Ajustes
from web.persistence.Modelos import Base

ESQUEMA = "ortesislab"

configuracion = context.config
if configuracion.config_file_name is not None:
    fileConfig(configuracion.config_file_name)

target_metadata = Base.metadata


def _Url() -> str:
    ajustes = Ajustes.Cargar()
    prueba = context.get_x_argument(as_dictionary=True).get("base") == "test"
    return ajustes.test_migrator_database_url if prueba else ajustes.migrator_database_url


def _Incluir(nombre: str | None, tipo: str, _padres: dict) -> bool:
    # El esquema por defecto es ortesislab, así que la tabla de versiones aparece
    # en la reflexión y Alembic la propondría borrar.
    return not (tipo == "table" and nombre == "alembic_version")


def Ejecutar() -> None:
    # Siempre con conexión: no se admite el modo --sql de Alembic.
    motor = create_engine(_Url())
    with motor.connect() as conexion:
        # search_path del rol migrador = ortesislab; se fija igualmente por si el
        # rol se usa sin su configuración de base.
        conexion.exec_driver_sql(f"SET search_path TO {ESQUEMA}")
        conexion.commit()
        context.configure(
            connection=conexion,
            target_metadata=target_metadata,
            include_name=_Incluir,
            version_table_schema=ESQUEMA,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    motor.dispose()


Ejecutar()
