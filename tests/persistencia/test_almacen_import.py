"""Import al bucket, caché Redis y migración de subidas locales."""

from __future__ import annotations

import io
import tempfile
import unittest
import uuid
from pathlib import Path

import numpy as np
from sqlalchemy import select

from GenerateModelsApp.Excepciones import ArchivoSuperficieIlegible
from tests.persistencia.apoyo_persistencia import Conectar, CrearUsuario, EntornoServicios, requiere_base
from web.GeneradorWeb import GeneradorWeb
from web.cache.CacheRedis import CacheRedis
from web.persistence.Contratos import AccesoDenegado
from web.persistence.Modelos import Importacion
from web.persistence.repositorios import RepositorioAssets, RepositorioImports
from web.services.ServicioImports import ServicioImports
from web.storage.AlmacenamientoPrivado import Almacen


def Placa(lado: float = 1.0) -> bytes:
    vertices = [[0, 0, 0], [lado, 0, 0], [lado, lado, 0], [0, lado, 0]]
    return GeneradorWeb.Stl(vertices, [[0, 1, 2], [0, 2, 3]])


@requiere_base
class ImportAlBucket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entorno = EntornoServicios().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.entorno.__exit__(None, None, None)

    def setUp(self):
        with Conectar() as conexion:
            self.a = CrearUsuario(conexion, "A")
            self.b = CrearUsuario(conexion, "B")

    def test_importa_original_y_npz_con_url_y_hash(self):
        contenido = Placa()
        importacion, info = ServicioImports.Importar(self.a, "pieza.stl", contenido, autoescalar=True)
        self.assertEqual(importacion.status, "ready")
        self.assertEqual(importacion.format, "stl_binary")
        self.assertEqual(info["factor_escala"], 100)
        self.assertEqual((info["vertices"], info["caras"]), (4, 2))
        with Conectar() as conexion:
            original = RepositorioAssets.Obtener(conexion, self.a.user_id, importacion.original_asset_id)
            normal = RepositorioAssets.Obtener(conexion, self.a.user_id, importacion.normalized_asset_id)
        for asset in (original, normal):
            self.assertEqual(asset.status, "ready")
            self.assertTrue(asset.storage_key.startswith(f"usuarios/{self.a.user_id}/assets/"))
            self.assertEqual(asset.object_url, self.entorno.almacen.Url(asset.storage_key))
            Almacen.LeerVerificado(asset.storage_key, asset.sha256)
        self.assertEqual(Almacen.Sha256(contenido), original.sha256)
        if self.entorno.redis is not None:
            self.assertIsNotNone(CacheRedis.LeerTupla(CacheRedis.ClaveCruda(normal.sha256)))

    def test_repetir_la_subida_reutiliza_el_import(self):
        primero, _ = ServicioImports.Importar(self.a, "pieza.stl", Placa(2.0))
        segundo, _ = ServicioImports.Importar(self.a, "otra.stl", Placa(2.0))
        self.assertEqual(primero.id, segundo.id)

    def test_un_archivo_invalido_queda_rechazado(self):
        with self.assertRaises(ArchivoSuperficieIlegible):
            ServicioImports.Importar(self.a, "roto.stl", b"solid x\nvertex 1 2\nendsolid")
        with Conectar() as conexion:
            fila = conexion.execute(
                select(Importacion.status, Importacion.error_code)
                .where(Importacion.user_id == self.a.user_id)
                .order_by(Importacion.created_at.desc())
                .limit(1)
            ).mappings().one()
        self.assertEqual(fila["status"], "rejected")

    def test_otro_usuario_no_resuelve_la_superficie(self):
        importacion, _ = ServicioImports.Importar(self.a, "pieza.stl", Placa(3.0))
        nombre = ServicioImports.NombreSuperficie(importacion.normalized_asset_id)
        self.assertEqual(ServicioImports.Resolver(self.a, nombre).id, importacion.id)
        with self.assertRaises(AccesoDenegado):
            ServicioImports.Resolver(self.b, nombre)
        with self.assertRaises(ValueError):
            ServicioImports.Resolver(self.a, "../../etc/passwd")

    def test_la_plantilla_es_un_import_del_usuario(self):
        plantilla = ServicioImports.AsegurarPlantilla(self.a)
        self.assertEqual(plantilla.source_kind, "included_template")
        self.assertEqual(ServicioImports.Resolver(self.a, "").id, plantilla.id)
        self.assertNotEqual(ServicioImports.AsegurarPlantilla(self.b).id, plantilla.id)


@requiere_base
class MigracionDeSubidas(unittest.TestCase):
    def test_migra_borra_la_copia_local_y_no_duplica(self):
        from scripts import MigrarSubidas

        with EntornoServicios(), tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            salida = io.BytesIO()
            np.savez_compressed(
                salida,
                vertices=np.array([[0.0, 0, 0], [100, 0, 0], [0, 100, 0]]),
                faces=np.array([[0, 1, 2]], dtype=np.int32),
                normals=np.tile([0.0, 0, 1], (3, 1)),
                border=np.zeros(3),
            )
            npz = carpeta / f"superficie-{uuid.uuid4().hex}.npz"
            npz.write_bytes(salida.getvalue())
            stl = carpeta / "ortesis-0123abcd.stl"
            stl.write_bytes(Placa(50.0))
            copia = {npz.name: npz.read_bytes(), stl.name: stl.read_bytes()}

            usuario = MigrarSubidas.Propietario()
            urls = {ruta.name: MigrarSubidas.Migrar(ruta, usuario) for ruta in (npz, stl)}
            self.assertTrue(urls[stl.name].endswith(".stl"))
            with Conectar() as conexion:
                importacion = RepositorioImports.ListoPorOriginal(
                    conexion, usuario.user_id, usuario.project_id, Almacen.Sha256(copia[npz.name]), "upload"
                )
            self.assertIsNotNone(importacion)
            self.assertEqual(importacion.original_asset_id, importacion.normalized_asset_id)
            self.assertIn("ya migrado", MigrarSubidas.Migrar(stl, usuario))


if __name__ == "__main__":
    unittest.main()
