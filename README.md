# GenerateModelsApp

Geometría paramétrica de una ortesis. El complemento de Blender y la aplicación Reflex son sistemas independientes: comparten el cálculo del paquete `GenerateModelsApp` y no se llaman entre sí. Blender genera y exporta. La web previsualiza el cascarón, muestra volumen, peso y precio, y puede generar varias variantes para compararlas.

- [Backend](docs/BACKEND.md): módulos, configuración, registro y errores.
- [Frontend](docs/FRONTEND.md): panel de Blender y estado actual de la web.
- [Uso en Blender](docs/LEEME.md): generar, comprobar y exportar.

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

Eso regenera `GenerateModelsApp.zip`. En Blender: **Edit > Preferences > Add-ons > Install from Disk**, activa **OrtesisLab** y reinicia si había una versión anterior. El uso está en [docs/LEEME.md](docs/LEEME.md).

La integración dentro de Blender:

```powershell
blender --factory-startup --background --python-exit-code 1 --python tests/blender_superficie_abierta.py
```

El complemento 1.1 parte de la **malla seleccionada sin espesor**, una sola capa de caras abierta por arriba también en el dedo. Añade espesor a las paredes sin tapar los canales y conserva la superficie base. Instala `GenerateModelsApp.zip`, selecciona la base y usa **N > Ortesis > Usar malla seleccionada**. No carga automáticamente la plantilla v5.