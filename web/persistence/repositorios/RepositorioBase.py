"""Clase padre de los repositorios: lectura de filas y conversión a DTO.

Cada hijo fija ``TABLA`` (su tabla principal) y, si devuelve un DTO cuyos campos
se llaman como las columnas, ``DTO``. Los hijos con renombres o conversiones
redefinen ``_Dto``. Ningún método abre transacciones ni hace commit.
"""

from __future__ import annotations

from dataclasses import fields
from typing import Any, ClassVar

from sqlalchemy import Table, select
from sqlalchemy.orm import Session

from ..Contratos import AccesoDenegado


class RepositorioBase:
    TABLA: ClassVar[Table]
    DTO: ClassVar[type | None] = None

    @staticmethod
    def _Uno(conexion: Session, consulta: Any) -> dict | None:
        fila = conexion.execute(consulta).mappings().first()
        return None if fila is None else dict(fila)

    @staticmethod
    def _Todos(conexion: Session, consulta: Any) -> list[dict]:
        return [dict(fila) for fila in conexion.execute(consulta).mappings()]

    @staticmethod
    def _Construir(dto: type, fila: dict) -> Any:
        # Las columnas que el DTO no declara se ignoran.
        return dto(**{campo.name: fila[campo.name] for campo in fields(dto)})

    @classmethod
    def _Dto(cls, fila: dict) -> Any:
        return cls._Construir(cls.DTO, fila)

    @classmethod
    def _Seleccion(cls) -> Any:
        return select(cls.TABLA)

    @classmethod
    def _Opcional(cls, conexion: Session, consulta: Any) -> Any:
        fila = cls._Uno(conexion, consulta)
        return None if fila is None else cls._Dto(fila)

    @classmethod
    def _Lista(cls, conexion: Session, consulta: Any) -> list:
        return [cls._Dto(fila) for fila in cls._Todos(conexion, consulta)]

    @classmethod
    def _DelUsuario(cls, conexion: Session, user_id: Any, *condiciones: Any, bloquear: bool = False) -> Any:
        """Fila del usuario que cumple ``condiciones``; un recurso ajeno o inexistente lanza ``AccesoDenegado``."""
        consulta = cls._Seleccion().where(cls.TABLA.c.user_id == user_id, *condiciones)
        fila = cls._Uno(conexion, consulta.with_for_update() if bloquear else consulta)
        if fila is None:
            raise AccesoDenegado()
        return cls._Dto(fila)
