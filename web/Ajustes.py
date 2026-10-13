"""Variables de entorno de OrtesisLab: el único lugar que las declara y las lee.

El entorno real tiene prioridad sobre el ``.env`` de la raíz. Una variable sin
valor por defecto es obligatoria: leerla sin definirla lanza ``VariableFaltante``.
Una variable con prefijo exigido lanza ``VariableInvalida`` si no empieza por él.
Ningún valor se envía al navegador.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


class VariableFaltante(RuntimeError):
    def __init__(self, clave: str):
        super().__init__(f"Falta la variable de entorno {clave}.")
        self.clave = clave


class VariableInvalida(RuntimeError):
    def __init__(self, clave: str, prefijo: str):
        super().__init__(f"La variable de entorno {clave} debe empezar por {prefijo}")
        self.clave = clave


class Variable:
    """Una clave del entorno; sin ``defecto`` es obligatoria y no admite vacío."""

    def __init__(self, clave: str, defecto: str | None = None, prefijo: str = ""):
        self.clave = clave
        self.defecto = defecto
        self.prefijo = prefijo

    def __get__(self, ajustes: Ajustes, _tipo: type) -> str:
        valor = ajustes.valores.get(self.clave) or self.defecto
        if valor is None:
            raise VariableFaltante(self.clave)
        if not valor.startswith(self.prefijo):
            raise VariableInvalida(self.clave, self.prefijo)
        return valor


# SQLAlchemy necesita el driver en la URL.
POSTGRES = "postgresql+psycopg://"


class Ajustes:
    # PostgreSQL: la web, el trabajador y Alembic usan roles distintos.
    database_url = Variable("ORTESISLAB_DATABASE_URL", prefijo=POSTGRES)
    worker_database_url = Variable("ORTESISLAB_WORKER_DATABASE_URL", prefijo=POSTGRES)
    migrator_database_url = Variable("ORTESISLAB_MIGRATOR_DATABASE_URL", prefijo=POSTGRES)
    test_database_url = Variable("ORTESISLAB_TEST_DATABASE_URL", prefijo=POSTGRES)
    test_worker_database_url = Variable("ORTESISLAB_TEST_WORKER_DATABASE_URL", prefijo=POSTGRES)
    test_migrator_database_url = Variable("ORTESISLAB_TEST_MIGRATOR_DATABASE_URL", prefijo=POSTGRES)

    # Bucket S3; sin URL pública, el navegador usa el endpoint.
    s3_endpoint = Variable("ORTESISLAB_S3_ENDPOINT")
    s3_public_url = Variable("ORTESISLAB_S3_PUBLIC_URL", "")
    s3_access_key = Variable("ORTESISLAB_S3_ACCESS_KEY")
    s3_secret_key = Variable("ORTESISLAB_S3_SECRET_KEY")
    s3_bucket = Variable("ORTESISLAB_S3_BUCKET", "ortesislab")
    s3_region = Variable("ORTESISLAB_S3_REGION", "us-east-1")

    # Vacía: la generación funciona sin caché.
    redis_url = Variable("ORTESISLAB_REDIS_URL", "")

    oidc_issuer = Variable("ORTESISLAB_OIDC_ISSUER")
    oidc_client_id = Variable("ORTESISLAB_OIDC_CLIENT_ID")
    oidc_client_secret = Variable("ORTESISLAB_OIDC_CLIENT_SECRET")
    oidc_redirect_uri = Variable("ORTESISLAB_OIDC_REDIRECT_URI")
    session_secret = Variable("ORTESISLAB_SESSION_SECRET")
    app_url = Variable("ORTESISLAB_APP_URL", "http://localhost:3000")
    _cookie_secure = Variable("ORTESISLAB_COOKIE_SECURE", "false")

    def __init__(self, valores: dict[str, str]):
        self.valores = valores

    @property
    def cookie_secure(self) -> bool:
        return self._cookie_secure.lower() == "true"

    def Faltante(self, *atributos: str) -> str:
        """Mensaje de la primera variable sin definir entre ``atributos``; vacío si están todas."""
        for atributo in atributos:
            try:
                getattr(self, atributo)
            except VariableFaltante as error:
                return str(error)
        return ""

    @staticmethod
    @lru_cache(maxsize=1)
    def Cargar() -> Ajustes:
        return Ajustes({**Ajustes._LeerArchivo(RAIZ / ".env"), **os.environ})

    @staticmethod
    def _LeerArchivo(ruta: Path) -> dict[str, str]:
        # KEY=valor por línea; comentarios con #.
        if not ruta.is_file():
            return {}
        valores = {}
        for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                valores[clave.strip()] = valor.strip().strip('"').strip("'")
        return valores
