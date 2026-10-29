# Pruebas

Cada carpeta agrupa las pruebas por el código que cubren. Desde la raíz del
repositorio:

```powershell
uv run python -m unittest discover -s tests
```

Ese comando encuentra los módulos `test_*.py` de las subcarpetas. Los scripts de
`blender/` no entran en unittest: los ejecuta Blender. Las pruebas de
`persistencia/` necesitan `ortesislab_test` creada con `make db-test-reset`,
migrada con `uv run alembic -x base=test upgrade head`, y las variables
`ORTESISLAB_TEST_*`; sin ellas se omiten.

| Carpeta | Qué cubre | Archivos |
|---|---|---|
| [nucleo](nucleo/test_nucleo.py) | Núcleo común: geometría de `Modeling` y `Cascaron`, malla, catálogo de patrones, validación, volumen, peso, precio e importación sin Blender | `test_nucleo.py` |
| [geometria](geometria/test_escala_malla.py) | Unidades y presupuesto (`EscalaMalla`), subdivisión (`RefinadorMalla`), contorno (`SuavizadoBorde`) y espesor sin tapar canales (`Cascaron`) | `test_escala_malla.py`, `test_refinador_malla.py`, `test_suavizado_borde.py`, `test_superficie_abierta.py` |
| [aplicacion_web](aplicacion_web/test_generador_web.py) | Lote, STL y lectura de superficies en `GeneradorWeb` y `LectorSuperficie`, incluida la autoescala con un import persistido | `test_generador_web.py` |
| [persistencia](persistencia/apoyo_persistencia.py) | PostgreSQL, bucket, Redis, imports, lotes, trabajador, historial, propiedad de los datos y permisos de rol | `apoyo_persistencia.py`, `test_almacen_import.py`, `test_lotes_trabajador.py`, `test_propiedad_datos.py` |
| [blender](blender/blender_superficie_abierta.py) | Complemento dentro de Blender: superficie abierta, y el ZIP distribuido en aislamiento | `blender_superficie_abierta.py`, `blender_paquete_zip.py` |
| [assets](assets/Test.stl) | Fixture de entrada y evidencia histórica. No son pruebas y no validan una ejecución nueva | `Test.stl`, `resultado_blender.json`, logs `*_ejecucion.log` |

## nucleo

`test_nucleo.py` compara el núcleo repartido con el cálculo de referencia,
rechaza parámetros inválidos y comprueba catálogo, volumen del tetraedro y que
el paquete no exija Blender para importarse.

## geometria

- `test_escala_malla.py`: heurística decimal, alcance de paso y presupuesto.
- `test_refinador_malla.py`: subdivisión y recorte sobre la superficie refinada.
- `test_suavizado_borde.py`: el contorno pierde dientes y el interior se conserva.
- `test_superficie_abierta.py`: pared sin tapas e integridad de la superficie base.

## aplicacion_web

`test_generador_web.py` arma combinaciones y STL sin abrir Blender. La carga de
`Test.stl` lee el fixture de [assets](assets/Test.stl). La carpeta no se llama
`web`: durante `unittest discover` esa carpeta quedaría delante del paquete
`web/` de la aplicación y ocultaría sus módulos.

## persistencia

`apoyo_persistencia.py` no es una prueba: abre una `Session` de SQLAlchemy por
rol contra la base desechable `ortesislab_test` (confirma al salir del `with`),
prepara el bucket de prueba y los usuarios, y ofrece `ErrorDeBase` para esperar
un error concreto de PostgreSQL. Las otras tres lo usan.

- `test_almacen_import.py`: import al bucket, caché Redis y migración de subidas locales.
- `test_lotes_trabajador.py`: lotes idempotentes, lease, aislamiento y conciliación.
- `test_propiedad_datos.py`: un usuario no lee datos de otro, y los roles solo hacen lo que su permiso permite.

## blender

Desde la raíz, con Blender en PATH:

```powershell
blender --factory-startup --background --python-exit-code 1 --python tests/blender/blender_superficie_abierta.py
blender --factory-startup --background --python-exit-code 1 --python tests/blender/blender_paquete_zip.py
```

`blender_superficie_abierta.py` escribe el JSON de la corrida en
`tests/assets/resultado_blender.json`. El archivo versionado es el resultado de
una ejecución anterior; una corrida nueva lo sustituye y no debe presentarse
como evidencia de otra revisión. Los logs de `tests/assets/` tienen el mismo
límite.

## assets

`Test.stl` es la superficie de entrada del caso de carga web. `resultado_blender.json`
y los tres logs quedan guardados para saber de dónde salieron resultados viejos.
No sustituyen una prueba ejecutada sobre el código actual.
