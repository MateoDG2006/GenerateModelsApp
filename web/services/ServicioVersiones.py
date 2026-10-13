"""Versiones inmutables: snapshot de parámetros, material y escala.

Los números de versión se reservan con un UPDATE sobre ``projects`` dentro de
la transacción del lote, así que dos lotes simultáneos no comparten número.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from uuid import UUID

from GenerateModelsApp.Excepciones import ParametrosNoReconocidos
from GenerateModelsApp.constants.Materials import PETG
from GenerateModelsApp.util.Utilidades import Configuracion
from web.enums import BackendGeneracion, TipoEvento
from web.persistence.Contratos import ESQUEMA_PARAMETROS, UsuarioAutenticado
from web.persistence.repositorios import RepositorioHistorial, RepositorioVersiones


class ServicioVersiones:
    @staticmethod
    def Canonico(valor) -> str:
        """JSON estable para hashes: claves ordenadas, sin espacios, sin NaN."""
        return json.dumps(valor, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

    @staticmethod
    def Sha(valor) -> str:
        return hashlib.sha256(ServicioVersiones.Canonico(valor).encode("utf-8")).hexdigest()

    @staticmethod
    def Material() -> dict:
        material = PETG()
        return {
            "name": material.name,
            "density_g_cm3": material.density,
            "price_per_gram": material.price,
            "currency": None,
            "color": material.color,
            "kind": material.type,
            "brand": material.brand,
        }

    @staticmethod
    def Parametros(opciones: dict) -> dict:
        # Snapshot completo de las opciones del complemento. La validación
        # geométrica ocurre en el trabajador: una variante inválida falla sola.
        plantilla = Configuracion.ParametrosDefecto()
        desconocidos = set(opciones) - set(plantilla)
        if desconocidos:
            raise ParametrosNoReconocidos(desconocidos)
        return dict(plantilla) | dict(opciones)

    @staticmethod
    def Insertar(
        conexion,
        usuario: UsuarioAutenticado,
        project_id: UUID,
        import_id: UUID,
        variantes: list[dict],
        auto_scale: bool,
        padre: UUID | None = None,
        nota: str | None = None,
    ) -> list[UUID]:
        numeros = RepositorioVersiones.ReservarNumeros(conexion, usuario.user_id, project_id, len(variantes))
        material = ServicioVersiones.Material()
        identificadores = []
        for numero, opciones in zip(numeros, variantes):
            parametros = ServicioVersiones.Parametros(opciones)
            version_id = uuid.uuid4()
            huella = ServicioVersiones.Sha(
                {"parameters": parametros, "auto_scale": bool(auto_scale), "backend": BackendGeneracion.PYTHON_CORE}
            )
            RepositorioVersiones.Insertar(
                conexion, usuario.user_id, project_id, version_id, import_id, numero, parametros,
                ESQUEMA_PARAMETROS, bool(auto_scale), material, huella, padre, nota,
            )
            RepositorioHistorial.Evento(
                conexion, usuario.user_id, project_id, TipoEvento.VERSION_CREATED, version_id=version_id,
                payload={"version_number": numero, "pattern": parametros.get("pattern")},
            )
            identificadores.append(version_id)
        return identificadores
