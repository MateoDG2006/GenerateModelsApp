"""Aplicación Reflex de comparación de ortesis.

El paquete GenerateModelsApp sigue siendo el complemento de Blender.
Esta página solo llama a sus funciones; el trabajo se guarda en PostgreSQL y
los archivos en el bucket S3. Las rutas /auth las sirve el transformador OIDC.
"""

import contextlib

import reflex as rx

from GenerateModelsApp.util.Utilidades import Registro

from .Ajustes import Ajustes
from .EstadoApp import EstadoApp
from .EstadoHistorial import EstadoHistorial
from .PaginaComparacion import PaginaComparacion
from .PaginaHistorial import PaginaHistorial
from .persistence.ConexionPostgres import ConexionPostgres
from .persistence.Contratos import ErrorPersistencia
from .services.AutenticacionOidc import AutenticacionOidc


@contextlib.asynccontextmanager
async def PoolPostgres():
    # Rol de aplicación, sin DDL; los handlers fallan con un mensaje si la base no está.
    try:
        ConexionPostgres.Abrir(Ajustes.Cargar().database_url, 1, 4, "backend")
    except ErrorPersistencia as exc:
        Registro.Obtener("web").error("PostgreSQL no disponible al arrancar: %s", exc)
    try:
        yield
    finally:
        ConexionPostgres.Cerrar()


app = rx.App(api_transformer=AutenticacionOidc.Aplicacion())
app.register_lifespan_task(PoolPostgres)
app.add_page(PaginaComparacion.Index, title="OrtesisLab", on_load=EstadoApp.CargarPredeterminados)
app.add_page(PaginaHistorial.Index, route="/historial", title="Historial · OrtesisLab", on_load=EstadoHistorial.Cargar)
