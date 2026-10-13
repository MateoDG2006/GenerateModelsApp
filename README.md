# GenerateModelsApp

Geometría paramétrica de una ortesis. El complemento de Blender y la aplicación Reflex son sistemas independientes: comparten el cálculo del paquete `GenerateModelsApp` y no se llaman entre sí. Blender genera y exporta. La web previsualiza el cascarón, muestra volumen, peso y precio, y puede generar varias variantes para compararlas.

- [Documentación completa](docs/README.md): arquitectura, inventario y estándar documental.
- [AppBackend](docs/AppBackend/README.md): infraestructura Reflex, eventos, contratos y operación.
- [AppFrontend](docs/AppFrontend/README.md): componentes, flujos y visor 3D.
- [BlenderPlugin](docs/BlenderPlugin/README.md): algoritmos, parámetros, API, validación y exportación.
- [Uso breve en Blender](docs/BlenderPlugin/LEEME.md): guía distribuida en el ZIP.
- [Mantenimiento documental](docs/Agents/MANTENIMIENTO.md): actualización automática por agentes y verificación.

## Setup

Hace falta **Python 3.14** y [uv](https://docs.astral.sh/uv/). Blender 5.x solo hace falta para el complemento; la web no lo abre.

Desde la raíz del repositorio:

```powershell
uv python install 3.14
uv sync
```

`uv sync` crea `.venv` e instala Reflex y NumPy según `uv.lock`.

Aplicación web:

```powershell
uv run reflex run
```

Queda en `http://localhost:3000`. El backend escucha en el puerto 8000.

Pruebas del núcleo, sin Blender:

```powershell
uv run python -m unittest discover -s tests
```

Complemento de Blender:

```powershell
uv run python scripts/EmpaquetarBlender.py
```

Eso regenera `GenerateModelsApp.zip`. En Blender: **Edit > Preferences > Add-ons > Install from Disk**, activa **OrtesisLab** y reinicia si había una versión anterior. El uso está en [docs/BlenderPlugin/LEEME.md](docs/BlenderPlugin/LEEME.md).

La integración dentro de Blender:

```powershell
blender --factory-startup --background --python-exit-code 1 --python tests/blender_superficie_abierta.py
```

El complemento 1.3.0 parte de la **malla seleccionada sin espesor**, una sola capa de caras abierta por arriba también en el dedo. Añade espesor a las paredes sin tapar los canales y conserva la superficie base. Instala `GenerateModelsApp.zip`, selecciona la base y usa **N > Ortesis > Usar malla seleccionada**. No carga automáticamente la plantilla v5.
## Verificar documentación

```powershell
python scripts/VerificarDocumentacion.py
```

Si cambia lógica fundamental, actualizar las explicaciones y diagramas en la misma iteración y luego regenerar índices con `python scripts/VerificarDocumentacion.py --actualizar`, según [MANTENIMIENTO.md](docs/Agents/MANTENIMIENTO.md).
