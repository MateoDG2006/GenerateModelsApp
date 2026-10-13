"""Preferencias por usuario con control optimista de revisión."""

from __future__ import annotations

from web.persistence.ConexionPostgres import ConexionPostgres
from web.persistence.Contratos import Preferencias, UsuarioAutenticado
from web.persistence.repositorios import RepositorioPreferencias


class ServicioPreferencias:
    @staticmethod
    def Obtener(usuario: UsuarioAutenticado) -> Preferencias:
        return ConexionPostgres.Ejecutar(lambda conexion: RepositorioPreferencias.Obtener(conexion, usuario.user_id))

    @staticmethod
    def GuardarAutoescala(usuario: UsuarioAutenticado, auto_scale: bool, revision: int) -> Preferencias:
        """Errores: ConflictoRevision si otra pestaña guardó antes."""

        def guardar(conexion) -> Preferencias:
            actual = RepositorioPreferencias.Obtener(conexion, usuario.user_id)
            return RepositorioPreferencias.Guardar(
                conexion, usuario.user_id, auto_scale, actual.default_parameters, revision
            )

        return ConexionPostgres.Ejecutar(guardar)
