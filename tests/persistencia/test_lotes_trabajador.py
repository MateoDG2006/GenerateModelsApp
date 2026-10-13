"""Lotes idempotentes, trabajador con lease, aislamiento y conciliación."""

from __future__ import annotations

import unittest
import uuid
from datetime import timedelta

import redis
from sqlalchemy import func, insert, select, update

from GenerateModelsApp.util.Utilidades import Configuracion
from tests.persistencia.apoyo_persistencia import (
    URL_TRABAJADOR,
    Conectar,
    CrearUsuario,
    EntornoServicios,
    Rol,
    requiere_base,
)
from tests.persistencia.test_almacen_import import Placa
from web.GeneradorWeb import GeneradorWeb
from web.cache.CacheRedis import CacheRedis
from web.jobs.ConciliadorArchivos import ConciliadorArchivos
from web.jobs.TrabajadorGeneracion import TrabajadorGeneracion
from web.persistence.Contratos import (
    AccesoDenegado,
    CuotaExcedida,
    SolicitudIdempotenteEnConflicto,
    SolicitudLote,
)
from web.persistence.Modelos import ArchivoAlmacenado, IntentoGeneracion, ItemLoteGeneracion, VersionModelo
from web.services.ContextoUsuario import ContextoUsuario
from web.services.ServicioHistorial import ServicioHistorial
from web.services.ServicioImports import ServicioImports
from web.services.ServicioLotes import ServicioLotes
from web.storage.AlmacenamientoPrivado import Almacen


def Macizo(espesor: float = 2.4) -> dict:
    opciones = dict(Configuracion.ParametrosDefecto())
    opciones.update({"pattern": "SOLID", "solid_mm": espesor, "border_mm": 0.0})
    return opciones


@requiere_base
class LotesYTrabajador(unittest.TestCase):
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
        self.importacion, _ = ServicioImports.Importar(self.a, "placa.stl", Placa(100.0), autoescalar=True)
        self.trabajador = TrabajadorGeneracion("prueba")
        # La cola es global: cada prueba la deja vacía para la siguiente.
        self.addCleanup(self.Vaciar)

    def Solicitud(self, variantes, request_id=None) -> SolicitudLote:
        return SolicitudLote(
            import_id=self.importacion.id,
            request_id=request_id or uuid.uuid4(),
            mode="sweep" if len(variantes) > 1 else "single",
            definition={"prueba": True},
            variantes=variantes,
            auto_scale=True,
        )

    def Vaciar(self) -> int:
        procesados = 0
        with Rol(URL_TRABAJADOR):
            while self.trabajador.Ciclo():
                procesados += 1
        return procesados

    def test_doble_envio_no_duplica_y_otro_cuerpo_entra_en_conflicto(self):
        request_id = uuid.uuid4()
        primero = ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo()], request_id))
        segundo = ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo()], request_id))
        self.assertEqual(primero.id, segundo.id)
        with Conectar() as conexion:
            versiones = conexion.execute(
                select(func.count()).select_from(VersionModelo).where(VersionModelo.user_id == self.a.user_id)
            ).scalar_one()
        self.assertEqual(versiones, 1)
        with self.assertRaises(SolicitudIdempotenteEnConflicto):
            ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo(3.0)], request_id))

    def test_cuota_de_lotes_pendientes(self):
        for _ in range(3):
            ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo()]))
        with self.assertRaises(CuotaExcedida):
            ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo()]))
        self.Vaciar()

    def test_lote_parcial_publica_stl_en_el_bucket(self):
        lote = ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo(), Macizo(-1.0)]))
        self.assertEqual(self.Vaciar(), 2)
        progreso = ServicioLotes.Progreso(self.a, lote.id)
        self.assertEqual(progreso.lote.status, "partial")
        exito, fallo = progreso.items
        self.assertEqual((exito.status, fallo.status), ("succeeded", "failed"))
        self.assertTrue(fallo.error_message)
        resultado = exito.resultado
        self.assertEqual(resultado.stl_status, "ready")
        self.assertTrue(resultado.stl_url.endswith(".stl"))
        self.assertGreater(resultado.volume_mm3, 0)
        clave = resultado.stl_url.split("/ortesislab/", 1)[1]
        datos = Almacen.Actual().Leer(clave)
        self.assertEqual(int.from_bytes(datos[80:84], "little"), resultado.triangles)
        ficha = GeneradorWeb._FichaDeItem(exito)
        self.assertEqual(ficha["archivo"], resultado.stl_url)
        self.assertEqual(ficha["error"], "")
        with ContextoUsuario.Activar(self.a):
            self.assertEqual(GeneradorWeb.Leer(resultado.stl_url), datos)
            self.assertEqual(GeneradorWeb.Ruta(resultado.stl_url).as_posix(), clave)
        with ContextoUsuario.Activar(self.b):
            with self.assertRaises(ValueError):
                GeneradorWeb.Ruta(resultado.stl_url)
        with self.assertRaises(AccesoDenegado):
            ServicioLotes.Progreso(self.b, lote.id)
        pagina = ServicioHistorial.Listar(self.a, {}, None, 25)
        self.assertEqual({fila.status for fila in pagina.filas}, {"succeeded", "failed"})
        self.assertEqual(ServicioHistorial.Listar(self.b, {}, None, 25).filas, [])
        self.assertEqual(ServicioHistorial.RegistrarDescarga(self.a, resultado.stl_asset_id), resultado.stl_url)
        with self.assertRaises(AccesoDenegado):
            ServicioHistorial.RegistrarDescarga(self.b, resultado.stl_asset_id)

    def test_un_lease_vencido_no_pisa_al_ganador(self):
        lote = ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo()]))
        with Rol(URL_TRABAJADOR):
            caido = ServicioLotes.Reservar("caido", 120, "prueba", "x", {})
            self.assertIsNotNone(caido)
            with Conectar(URL_TRABAJADOR) as conexion:
                conexion.execute(
                    update(ItemLoteGeneracion)
                    .where(ItemLoteGeneracion.id == caido.item_id)
                    .values(lease_expires_at=func.now() - timedelta(seconds=1))
                )
            self.assertEqual(ServicioLotes.AbandonarVencidos(), 1)
            self.assertTrue(self.trabajador.Ciclo())
            self.assertFalse(ServicioLotes.Renovar(caido, 120))
        progreso = ServicioLotes.Progreso(self.a, lote.id)
        self.assertEqual(progreso.items[0].status, "succeeded")
        self.assertEqual(progreso.items[0].attempt_count, 2)
        with Conectar() as conexion:
            estados = list(
                conexion.execute(
                    select(IntentoGeneracion.status)
                    .where(IntentoGeneracion.batch_item_id == caido.item_id)
                    .order_by(IntentoGeneracion.attempt_number)
                ).scalars()
            )
        self.assertEqual(estados, ["abandoned", "succeeded"])

    def test_cancelar_antes_de_empezar(self):
        lote = ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo(), Macizo(3.0)]))
        with self.assertRaises(AccesoDenegado):
            ServicioLotes.Cancelar(self.b, lote.id)
        self.assertTrue(ServicioLotes.Cancelar(self.a, lote.id))
        progreso = ServicioLotes.Progreso(self.a, lote.id)
        self.assertEqual(progreso.lote.status, "cancelled")
        self.assertEqual({item.status for item in progreso.items}, {"cancelled"})
        self.assertEqual(self.Vaciar(), 0)

    def test_sin_redis_la_generacion_sigue(self):
        CacheRedis.Usar(redis.Redis(host="127.0.0.1", port=1, socket_timeout=0.2, socket_connect_timeout=0.2))
        self.addCleanup(CacheRedis.Usar, self.entorno.redis)
        lote = ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo(2.0)]))
        self.Vaciar()
        self.assertEqual(ServicioLotes.Progreso(self.a, lote.id).lote.status, "succeeded")

    def test_restaurar_crea_otra_version(self):
        lote = ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo(2.2)]))
        original = ServicioLotes.Progreso(self.a, lote.id).items[0]
        nuevo = ServicioHistorial.Restaurar(self.a, original.version_id)
        restaurada = ServicioLotes.Progreso(self.a, nuevo.id).items[0]
        self.assertNotEqual(restaurada.version_id, original.version_id)
        self.assertGreater(restaurada.version_number, original.version_number)
        detalle = ServicioHistorial.Detalle(self.a, restaurada.version_id)
        self.assertEqual(detalle.version.parent_version_id, original.version_id)
        self.assertEqual(detalle.parametros_padre, original.parameters)
        self.Vaciar()

    def test_conciliacion_de_staged_y_objetos_ausentes(self):
        lote = ServicioLotes.Solicitar(self.a, self.Solicitud([Macizo(2.6)]))
        self.Vaciar()
        resultado = ServicioLotes.Progreso(self.a, lote.id).items[0].resultado
        clave = resultado.stl_url.split("/ortesislab/", 1)[1]
        Almacen.Actual().Borrar(clave)
        staged = uuid.uuid4()
        with Conectar(URL_TRABAJADOR) as conexion:
            conexion.execute(
                insert(ArchivoAlmacenado).values(
                    id=staged,
                    user_id=self.a.user_id,
                    storage_key=Almacen.Clave(self.a.user_id, staged, True),
                    kind="result_stl",
                    media_type="model/stl",
                    size_bytes=1,
                    sha256="0" * 64,
                    status="staged",
                    created_at=func.now() - timedelta(days=2),
                )
            )
        with Rol(URL_TRABAJADOR):
            conciliador = ConciliadorArchivos()
            cuenta = {"ausentes": 0}
            for _ in range(50):
                parcial = conciliador.Ejecutar()
                cuenta["ausentes"] += parcial["ausentes"]
                if conciliador._cursor is None:
                    break
        self.assertGreaterEqual(cuenta["ausentes"], 1)
        with Conectar() as conexion:
            estados = dict(
                conexion.execute(
                    select(ArchivoAlmacenado.id, ArchivoAlmacenado.status).where(
                        ArchivoAlmacenado.id.in_([staged, resultado.stl_asset_id])
                    )
                ).all()
            )
        self.assertEqual(estados[staged], "deleted")
        self.assertEqual(estados[resultado.stl_asset_id], "missing")
        item = ServicioLotes.Progreso(self.a, lote.id).items[0]
        self.assertIn("ya no está", GeneradorWeb._FichaDeItem(item)["error"])


if __name__ == "__main__":
    unittest.main()
