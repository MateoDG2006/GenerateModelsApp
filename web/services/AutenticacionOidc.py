"""Rutas OIDC del backend: /auth/login, /auth/callback y /auth/logout.

Se montan con ``api_transformer``. Las variables OIDC son obligatorias: si falta
una, la aplicación no arranca (no existe un modo anónimo que persista trabajo).
"""

from __future__ import annotations

import asyncio

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse, Response
from starlette.routing import Mount, Route

from GenerateModelsApp.util.Utilidades import Registro
from web.Ajustes import Ajustes
from web.ConfiguracionBackend import ConfiguracionBackend
from web.persistence.Contratos import ErrorPersistencia

from .ContextoUsuario import DURACION_SESION, NOMBRE_COOKIE, ContextoUsuario


class AutenticacionOidc:
    @staticmethod
    def Aplicacion() -> Starlette:
        """Aplicación raíz que Reflex usa como transformador; monta /auth."""
        ajustes = Ajustes.Cargar()
        oauth = OAuth()
        oauth.register(
            name="oidc",
            client_id=ajustes.oidc_client_id,
            client_secret=ajustes.oidc_client_secret,
            server_metadata_url=f"{ajustes.oidc_issuer.rstrip('/')}/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

        async def login(request: Request) -> Response:
            return await oauth.oidc.authorize_redirect(request, ajustes.oidc_redirect_uri)

        async def callback(request: Request) -> Response:
            try:
                token = await oauth.oidc.authorize_access_token(request)
            except OAuthError as exc:
                Registro.Obtener("auth").warning("Callback OIDC rechazado: %s", exc.error)
                return PlainTextResponse("No se pudo completar el inicio de sesión.", status_code=400)
            datos = token.get("userinfo") or {}
            if not datos.get("sub") or not datos.get("iss"):
                return PlainTextResponse("El proveedor no devolvió una identidad válida.", status_code=400)
            nombre = str(datos.get("name") or datos.get("preferred_username") or datos.get("email") or datos["sub"])
            try:
                valor, _expira = await asyncio.to_thread(
                    ContextoUsuario.IniciarSesion, str(datos["iss"]), str(datos["sub"]), datos.get("email"), nombre
                )
            except ErrorPersistencia as exc:
                return PlainTextResponse(str(exc), status_code=503)
            respuesta = RedirectResponse(ajustes.app_url, status_code=303)
            respuesta.set_cookie(
                NOMBRE_COOKIE,
                valor,
                max_age=int(DURACION_SESION.total_seconds()),
                httponly=True,
                secure=ajustes.cookie_secure,
                samesite="lax",
                path="/",
            )
            return respuesta

        async def logout(request: Request) -> Response:
            try:
                await asyncio.to_thread(ContextoUsuario.CerrarSesion, request.headers.get("cookie", ""))
            except ErrorPersistencia:
                pass
            respuesta = RedirectResponse(ajustes.app_url, status_code=303)
            respuesta.delete_cookie(NOMBRE_COOKIE, path="/", httponly=True, secure=ajustes.cookie_secure, samesite="lax")
            return respuesta

        # La sesión de Starlette solo guarda state y nonce durante el intercambio OIDC.
        rutas = Starlette(
            routes=[
                Route("/login", login),
                Route("/callback", callback),
                Route("/logout", logout),
            ],
            middleware=[
                Middleware(
                    SessionMiddleware,
                    secret_key=ajustes.session_secret,
                    session_cookie="ortesislab_oidc",
                    max_age=ConfiguracionBackend.Cargar("sesion")["intercambio_oidc_s"],
                    same_site="lax",
                    https_only=ajustes.cookie_secure,
                )
            ],
        )
        return Starlette(routes=[Mount("/auth", app=rutas)])
