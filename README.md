# GenerateModelsApp

Geometría paramétrica de una ortesis. El complemento de Blender y la aplicación Reflex son sistemas independientes: comparten el cálculo del paquete `GenerateModelsApp` y no se llaman entre sí. Blender genera y exporta. La web previsualiza el cascarón, muestra volumen, peso y precio, y puede generar varias variantes para compararlas. Cada usuario inicia sesión; sus superficies, versiones y lotes se guardan en PostgreSQL, los STL y archivos grandes en un bucket S3 (MinIO) y `/historial` permite comparar y restaurar versiones.

- [Documentación completa](docs/README.md): arquitectura, inventario y estándar documental.
- [AppBackend](docs/AppBackend/README.md): infraestructura Reflex, eventos, contratos y operación.
- [AppFrontend](docs/AppFrontend/README.md): componentes, flujos y visor 3D.
- [BlenderPlugin](docs/BlenderPlugin/README.md): algoritmos, parámetros, API, validación y exportación.
- [Uso breve en Blender](docs/BlenderPlugin/LEEME.md): guía distribuida en el ZIP.
- [Mantenimiento documental](docs/Agents/MANTENIMIENTO.md): qué actualizar en cada cambio y cómo revisarlo.

## Setup

Hace falta **Python 3.14** y [uv](https://docs.astral.sh/uv/). Blender 5.x solo hace falta para el complemento; la web no lo abre.

Desde la raíz del repositorio:

```powershell
uv python install 3.14
uv sync
```

`uv sync` crea `.venv` e instala Reflex, NumPy y los clientes de PostgreSQL, S3 y Redis según `uv.lock`.

Aplicación web (necesita Docker y `make`; copiar antes `infra/database/.env.example` y `.env.example` a `.env` y completarlos):

```powershell
make db-up
make db-init-s3
uv run alembic upgrade head   # requiere una revisión en db/alembic/versions; ver operación del backend
make auth-dev-up
uv run python scripts/EjecutarTrabajador.py
uv run reflex run
```

Queda en `http://localhost:3000`. El backend escucha en el puerto 8000; con `--env prod` todo usa el 3000. El trabajador genera los modelos encolados. Detalle en [operación del backend](docs/AppBackend/OPERACION_Y_PRUEBAS.md).

Pruebas, sin Blender (las de persistencia requieren `make db-test-reset`, `uv run alembic -x base=test upgrade head` y las variables `ORTESISLAB_TEST_*`; si no, se omiten):

```powershell
uv run python -m unittest discover -s tests
```

Qué cubre cada carpeta está en [tests/README.md](tests/README.md).

Complemento de Blender:

```powershell
uv run python scripts/EmpaquetarBlender.py
```

Eso regenera `GenerateModelsApp.zip`. En Blender: **Edit > Preferences > Add-ons > Install from Disk**, activa **OrtesisLab** y reinicia si había una versión anterior. El uso está en [docs/BlenderPlugin/LEEME.md](docs/BlenderPlugin/LEEME.md).

La integración dentro de Blender:

```powershell
blender --factory-startup --background --python-exit-code 1 --python tests/blender/blender_superficie_abierta.py
```

El complemento 1.3.0 parte de la **malla seleccionada sin espesor**, una sola capa de caras abierta por arriba también en el dedo. Añade espesor a las paredes sin tapar los canales y conserva la superficie base. Instala `GenerateModelsApp.zip`, selecciona la base y usa **N > Ortesis > Usar malla seleccionada**. No carga automáticamente la plantilla v5.

## Mantener la documentación

Si cambia lógica fundamental, actualizar las explicaciones y diagramas en la misma iteración y luego regenerar inventario e índices, según [MANTENIMIENTO.md](docs/Agents/MANTENIMIENTO.md):

```powershell
python docs/Agents/Scripts/GenerarIndices.py
python docs/Agents/Scripts/GenerarIndices.py --comprobar
```
