# GenerateModelsApp

Geometría paramétrica de una ortesis. El complemento de Blender y la aplicación Reflex son sistemas independientes: comparten el cálculo del paquete `GenerateModelsApp` y no se llaman entre sí. Blender genera y exporta. La web previsualiza el cascarón, muestra volumen, peso y precio, y puede generar varias variantes para compararlas.

- [Backend](docs/BACKEND.md): módulos, configuración, registro y errores.
- [Frontend](docs/FRONTEND.md): panel de Blender y estado actual de la web.
- [Uso en Blender](docs/LEEME.md): generar, comprobar y exportar.

El complemento 1.1 parte de la **malla seleccionada sin espesor**, una sola capa de caras abierta por arriba también en el dedo. Añade espesor a las paredes sin tapar los canales y conserva la superficie base. Instala `GenerateModelsApp.zip`, selecciona la base y usa **N > Ortesis > Usar malla seleccionada**. No carga automáticamente la plantilla v5.

Para regenerar el ZIP de Blender: `python scripts/EmpaquetarBlender.py`. Para comprobar el núcleo: `python -m unittest discover -s tests`. La integración real de Blender se ejecuta con `blender --factory-startup --background --python-exit-code 1 --python tests/blender_superficie_abierta.py`.
