"""Aplicación Reflex de comparación de ortesis.

El paquete GenerateModelsApp sigue siendo el complemento de Blender.
Esta página solo llama a sus funciones.
"""

import reflex as rx

from .PaginaComparacion import PaginaComparacion
from .EstadoApp import EstadoApp

app = rx.App()
app.add_page(PaginaComparacion.Index, title="OrtesisLab", on_load=EstadoApp.CargarPredeterminados)
