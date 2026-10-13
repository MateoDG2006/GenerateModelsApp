"""Principal autenticado de cada operación.

La identidad sale de una sesión de servidor creada tras el login OIDC. El
navegador solo guarda un token aleatorio en una cookie HttpOnly; la base guarda
su SHA-256. El token de sesión de Reflex no es identidad.
"""

from __future__ import annotations

import hashlib
import secrets
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
from http.cookies import CookieError, SimpleCookie

from web.ConfiguracionBackend import ConfiguracionBackend
from web.enums import EstadoUsuario
from web.persistence.ConexionPostgres import ConexionPostgres
from web.persistence.Contratos import SesionInvalida, UsuarioAutenticado
from web.persistence.repositorios import RepositorioPreferencias, RepositorioProyectos, RepositorioUsuarios

NOMBRE_COOKIE = "ortesislab_sesion"
DURACION_SESION = timedelta(hours=ConfiguracionBackend.Cargar("sesion")["duracion_horas"])

_actual: ContextVar[UsuarioAutenticado | None] = ContextVar("ortesislab_usuario", default=None)


class ContextoUsuario:
    @staticmethod
    def Hash(token: str) -> str:
        return hashlib.sha256(token.encode("ascii")).hexdigest()

    @staticmethod
    def TokenDeCookie(cabecera: str) -> str:
        if not cabecera:
            return ""
        try:
            galleta = SimpleCookie()
            galleta.load(cabecera)
        except CookieError:
            return ""
        morsel = galleta.get(NOMBRE_COOKIE)
        return morsel.value if morsel is not None else ""

    @staticmethod
    def Requerir(cabecera_cookie: str) -> UsuarioAutenticado:
        """Entrada: cabecera Cookie. Proceso: resuelve la sesión vigente y el
        proyecto predeterminado. Salida: principal. Errores: SesionInvalida si
        falta, expiró, se revocó o la cuenta no está activa."""
        token = ContextoUsuario.TokenDeCookie(cabecera_cookie)
        if not token:
            raise SesionInvalida()
        huella = ContextoUsuario.Hash(token)

        def resolver(conexion) -> UsuarioAutenticado:
            fila = RepositorioUsuarios.ResolverSesion(conexion, huella)
            if fila is None:
                raise SesionInvalida("La sesión expiró. Vuelva a iniciar sesión.")
            proyecto = RepositorioProyectos.Predeterminado(conexion, fila["id"])
            return UsuarioAutenticado(fila["id"], fila["display_name"], fila["email"], proyecto)

        return ConexionPostgres.Ejecutar(resolver)

    @staticmethod
    def IniciarSesion(issuer: str, subject: str, email: str | None, nombre: str) -> tuple[str, datetime]:
        # Alta o actualización de la cuenta, preferencias y proyecto en una transacción.
        token = secrets.token_urlsafe(32)
        expira = datetime.now(timezone.utc) + DURACION_SESION

        def crear(conexion) -> None:
            user_id = RepositorioUsuarios.Upsert(conexion, issuer, subject, email, nombre)
            if RepositorioUsuarios.Estado(conexion, user_id) != EstadoUsuario.ACTIVE:
                raise SesionInvalida("La cuenta no está activa.")
            RepositorioPreferencias.Obtener(conexion, user_id)
            RepositorioProyectos.Predeterminado(conexion, user_id)
            RepositorioUsuarios.CrearSesion(conexion, user_id, ContextoUsuario.Hash(token), expira)

        ConexionPostgres.Ejecutar(crear)
        return token, expira

    @staticmethod
    def CerrarSesion(cabecera_cookie: str) -> None:
        token = ContextoUsuario.TokenDeCookie(cabecera_cookie)
        if token:
            huella = ContextoUsuario.Hash(token)
            ConexionPostgres.Ejecutar(lambda conexion: RepositorioUsuarios.RevocarSesion(conexion, huella))

    @staticmethod
    @contextmanager
    def Activar(usuario: UsuarioAutenticado) -> Iterator[UsuarioAutenticado]:
        # Fija el principal para el código síncrono que corre en este contexto.
        marca = _actual.set(usuario)
        try:
            yield usuario
        finally:
            _actual.reset(marca)

    @staticmethod
    def Actual() -> UsuarioAutenticado:
        usuario = _actual.get()
        if usuario is None:
            raise SesionInvalida()
        return usuario
