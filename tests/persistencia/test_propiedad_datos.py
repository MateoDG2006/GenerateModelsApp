"""Propiedad de los datos y permisos de rol sobre PostgreSQL real."""

from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timedelta, timezone

from psycopg import errors
from sqlalchemy import insert, text, update

from tests.persistencia.apoyo_persistencia import (
    URL_APP,
    URL_TRABAJADOR,
    Conectar,
    CrearAssetListo,
    CrearImportListo,
    CrearUsuario,
    ErrorDeBase,
    requiere_base,
)
from web.persistence.ConexionPostgres import ConexionPostgres
from web.persistence.Contratos import AccesoDenegado, ConflictoRevision, SesionInvalida
from web.persistence.Modelos import ArchivoAlmacenado, SesionAutenticacion, Usuario
from web.persistence.repositorios import (
    RepositorioAssets,
    RepositorioHistorial,
    RepositorioImports,
    RepositorioPreferencias,
    RepositorioUsuarios,
)
from web.services.ContextoUsuario import NOMBRE_COOKIE, ContextoUsuario


@requiere_base
class PropiedadDeRecursos(unittest.TestCase):
    def setUp(self):
        self.conexion = Conectar()
        self.addCleanup(self.conexion.close)
        self.a = CrearUsuario(self.conexion, "Usuario A")
        self.b = CrearUsuario(self.conexion, "Usuario B")
        self.conexion.commit()

    def test_otro_usuario_no_abre_asset_ni_import(self):
        import_id = CrearImportListo(self.conexion, self.a)
        importacion = RepositorioImports.Obtener(self.conexion, self.a.user_id, import_id)
        self.conexion.commit()
        with self.assertRaises(AccesoDenegado):
            RepositorioAssets.Obtener(self.conexion, self.b.user_id, importacion.normalized_asset_id)
        with self.assertRaises(AccesoDenegado):
            RepositorioImports.Obtener(self.conexion, self.b.user_id, import_id)
        filas, hay_mas = RepositorioHistorial.Listar(self.conexion, self.b.user_id, {}, None, 25)
        self.assertEqual((filas, hay_mas), ([], False))

    def test_la_fk_compuesta_impide_mezclar_propietarios(self):
        asset_a = CrearAssetListo(self.conexion, self.a, "import_original")
        self.conexion.commit()
        with ErrorDeBase(self, errors.ForeignKeyViolation):
            RepositorioImports.Crear(self.conexion, self.b, uuid.uuid4(), asset_a, "upload", "stl_binary", "x", 1)
        self.conexion.rollback()

    def test_un_asset_ready_exige_url_y_staged_no_la_admite(self):
        with ErrorDeBase(self, errors.CheckViolation):
            self.conexion.execute(
                insert(ArchivoAlmacenado).values(
                    id=uuid.uuid4(),
                    user_id=self.a.user_id,
                    storage_key=f"k/{uuid.uuid4()}",
                    kind="result_stl",
                    media_type="model/stl",
                    size_bytes=1,
                    sha256="0" * 64,
                    status="ready",
                )
            )
        self.conexion.rollback()

    def test_preferencias_con_revision(self):
        actual = RepositorioPreferencias.Obtener(self.conexion, self.a.user_id)
        nueva = RepositorioPreferencias.Guardar(self.conexion, self.a.user_id, False, {}, actual.revision)
        self.assertEqual(nueva.revision, actual.revision + 1)
        with self.assertRaises(ConflictoRevision):
            RepositorioPreferencias.Guardar(self.conexion, self.a.user_id, True, {}, actual.revision)
        self.conexion.rollback()


@requiere_base
class PermisosDeRol(unittest.TestCase):
    def test_la_app_no_reescribe_historial_ni_resultados(self):
        with Conectar(URL_APP) as conexion:
            usuario = CrearUsuario(conexion)
            RepositorioHistorial.Evento(conexion, usuario.user_id, usuario.project_id, "project_archived")
            conexion.commit()
            for sentencia in (
                "UPDATE history_events SET payload = '{}'::jsonb",
                "DELETE FROM history_events",
                "DELETE FROM file_assets",
                "INSERT INTO generation_results (id) VALUES (gen_random_uuid())",
                "UPDATE model_versions SET change_note = 'x'",
                "CREATE TABLE intrusa (id int)",
            ):
                with self.subTest(sentencia=sentencia):
                    with ErrorDeBase(self, errors.InsufficientPrivilege):
                        conexion.execute(text(sentencia))
                    conexion.rollback()

    def test_el_trabajador_no_crea_usuarios_ni_versiones(self):
        with Conectar(URL_TRABAJADOR) as conexion:
            for sentencia in (
                "INSERT INTO app_users (id, auth_issuer, auth_subject, display_name) VALUES (gen_random_uuid(), 'i', 's', 'n')",
                "UPDATE model_versions SET change_note = 'x'",
                "DELETE FROM batch_items",
            ):
                with self.subTest(sentencia=sentencia):
                    with ErrorDeBase(self, errors.InsufficientPrivilege):
                        conexion.execute(text(sentencia))
                    conexion.rollback()


@requiere_base
class SesionesDeServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ConexionPostgres.Cerrar()
        ConexionPostgres.Abrir(URL_APP, 1, 2, "pruebas")

    @classmethod
    def tearDownClass(cls):
        ConexionPostgres.Cerrar()

    def test_cookie_valida_revocada_y_ausente(self):
        token, _expira = ContextoUsuario.IniciarSesion("urn:ortesislab:test", uuid.uuid4().hex, "a@x.test", "Ana")
        cabecera = f"otra=1; {NOMBRE_COOKIE}={token}"
        usuario = ContextoUsuario.Requerir(cabecera)
        self.assertEqual(usuario.display_name, "Ana")
        self.assertIsNotNone(usuario.project_id)
        with ContextoUsuario.Activar(usuario):
            self.assertEqual(ContextoUsuario.Actual(), usuario)
        with self.assertRaises(SesionInvalida):
            ContextoUsuario.Actual()
        ContextoUsuario.CerrarSesion(cabecera)
        with self.assertRaises(SesionInvalida):
            ContextoUsuario.Requerir(cabecera)
        with self.assertRaises(SesionInvalida):
            ContextoUsuario.Requerir("")
        with self.assertRaises(SesionInvalida):
            ContextoUsuario.Requerir(f"{NOMBRE_COOKIE}=inventado")

    def test_sesion_expirada_o_cuenta_deshabilitada(self):
        with Conectar() as conexion:
            usuario = CrearUsuario(conexion)
            token = uuid.uuid4().hex
            pasado = datetime.now(timezone.utc) - timedelta(seconds=1)
            conexion.execute(
                insert(SesionAutenticacion).values(
                    id=uuid.uuid4(),
                    user_id=usuario.user_id,
                    token_sha256=ContextoUsuario.Hash(token),
                    created_at=pasado - timedelta(hours=1),
                    expires_at=pasado,
                )
            )
            vigente = uuid.uuid4().hex
            RepositorioUsuarios.CrearSesion(
                conexion, usuario.user_id, ContextoUsuario.Hash(vigente), datetime.now(timezone.utc) + timedelta(hours=1)
            )
            conexion.commit()
            with self.assertRaises(SesionInvalida):
                ContextoUsuario.Requerir(f"{NOMBRE_COOKIE}={token}")
            self.assertEqual(ContextoUsuario.Requerir(f"{NOMBRE_COOKIE}={vigente}").user_id, usuario.user_id)
            conexion.execute(update(Usuario).where(Usuario.id == usuario.user_id).values(status="disabled"))
            conexion.commit()
            with self.assertRaises(SesionInvalida):
                ContextoUsuario.Requerir(f"{NOMBRE_COOKIE}={vigente}")


if __name__ == "__main__":
    unittest.main()
