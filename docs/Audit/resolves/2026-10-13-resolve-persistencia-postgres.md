# RES-2026-10-13-001 — Persistencia PostgreSQL, bucket S3 y caché Redis

Fecha: 2026-10-13 (America/Bogota)
Auditorías: AUD-2026-10-13-001
Estado: EN_CURSO
Responsable: agente de implementación, por instrucción del usuario (Mateo Del Giudice)

## Autorización para corregir

Instrucción explícita del usuario, 2026-10-13, durante la planificación de la
persistencia descrita en [DATABASE.md](../../AppBackend/DATABASE.md):

> «Lo unico que nos preocupa de los archivos afectados por el audit son las
> firmas, hay que mantener las mismas firmas en esos archivos y listo, podemos
> pasar por encima del audit»

Alcance autorizado: editar por dentro los archivos auditados que intervienen en
la persistencia (lista siguiente) **sin cambiar sus firmas públicas**: mismo
nombre, mismos parámetros y mismo tipo de retorno. La autorización no cierra los
hallazgos de `AUD-2026-10-13-001`; esos hallazgos siguen abiertos salvo que un
resolve posterior aporte evidencia de su cierre.

## Archivos y hallazgos

| Archivo desde la raíz | Hallazgos | SHA-256 anterior (revisión `64bb48e`) | SHA-256 verificada |
|---|---|---|---|
| `web/EstadoApp.py` | Hallazgos abiertos de la auditoría; no se cierran aquí | `51fc192cc0639494ff491cff4fbae1019a59f50d36d1197c212b8b9e3af665af` | `136a0ea871bb117ef3d675addcc655a9cbb0d7ed532e6aeec0ddc832b1512255` |
| `web/GeneradorWeb.py` | Ídem | `71c693ac23eaba5bb589bdb67b205b2324a17c13bfd3671c9ce965979cf18892` | `31c906689852d364b7f93d31ea2c88aef6465c836a999551afa810420409eab7` |
| `web/GenerateModelsApp.py` | Ídem | `26bf2674e95d3c74c1c2e0bb2f3d7467a2d40bd1bc5b3eaf9af4560e6aac96ee` | `ab03e671ba514acdde18da54bedd2af27c3e5905d40065690215b5897a9c789f` |
| `web/PaginaComparacion.py` | Ídem | `a7389e9a38dff6e58ff0a4ef15121217805f07cff9b05f5743b4ca50a43fd83a` | `2836c94f731cded8e934d806bb36819c744ac01a734933bf9c6c41772ff67edb` |
| `assets/visor.html` | Ídem | `814cd36e4e09e7f10bfc7abb330b5a59eda46e96144d223e1ac4f8508ef63e42` | `be9f30401d1c1a1e3962ee3ec58178105505a7004ab00dd35831d79655930cad` |
| `pyproject.toml` | Ídem | `b2f51b98bc2279be58720e4549bc4880f0a3e0ce9439a3415dee6fe738f1a152` | `b9decc460b2239ce1d800a5e70517bc7d89eeb48b572617dc3e18c9521810d35` |
| `uv.lock` | Ídem | `496b88d51f5b90de93ca2d8e3870678ddabf041596fb84ba9b213b8c0446e2c2` | `6c28297a646bd1a74b440e3563b1dd716143ec659ad1cd402b5182a5e54ef78a` |
| `.gitignore` | Ídem | `a3e1b5bdd24653cc04e6ea600afdd0e58452224ab09379e1b3c1e81ea03dafba` | `4d92fe40659d5effeae3e725ac6c15ad393b9c14f9b56f742c73eb7a2475c8f8` |
| `rxconfig.py` | Ídem | `ec17cd818298c195ff428b3a27b1615cba943ae81a0dce925b86bcd81c6a14bf` | Sin cambios (misma huella) |
| `tests/test_generador_web.py` | Ídem | `09db51153fc06e546f1ae2b59191a0ae1dbf846c39495e4aa15b39da810675de` | `4894eca18f684fd1f23cb61b6bfd979f71f22f4a375422d5f7833519a98a51b2` |

`web/LectorSuperficie.py` (`a8751d67…a98`) se reutiliza sin edición.

### Ampliación: documentación de entrada (2026-10-13)

Instrucción adicional del usuario tras comprobar que
`scripts/VerificarDocumentacion.py` ya no existe en disco ni en `64bb48e`:

> «Eliminalo de la documentacion»

Bajo esa instrucción y la autorización anterior se editan dos archivos
auditados sin firmas Python. En `README.md` se describe la nueva arquitectura,
el arranque con Docker/Makefile y trabajador, y se sustituye la sección del
verificador por la de mantenimiento. En `AGENTS.md` solo se cambian los
pasos 3–4 de «Antes de terminar». La regla de bloqueo por auditorías no se toca.

Instrucción posterior del usuario, el mismo día:

> «Haz un script para generalo automaticamente pero guardalo en la parte de
> docs/Agents/Scripts»

Se crea `docs/Agents/Scripts/GenerarIndices.py` y los pasos 3–4 de `AGENTS.md`
y la sección de mantenimiento de `README.md` pasan a indicar su ejecución. Las
huellas siguientes son las del estado final.

| Archivo desde la raíz | Hallazgos | SHA-256 del blob en `64bb48e` | SHA-256 del archivo editado |
|---|---|---|---|
| `README.md` | Hallazgos abiertos de la auditoría; no se cierran aquí | `264f035ef4579f430aa5637cbabc6a2bc6d703421c779a8234cf26165f098f72` | `a90c80f6f58419f87b6d089fd9446400b64e2488ca17f6475c91d69c07f96dd4` |
| `AGENTS.md` | Ídem | `f8bffe9f0d25ab4e5c14e20e5e24dc8a3d405ac889949ade9ff5f5d183677124` | `d3e4ae205d9f5f03bceb204f3c313bd93f24f4a0347828a06dff50e0295e549b` |

### Ampliación: patrones y ejes en YAML (2026-10-13)

Instrucción del usuario sobre `web/GeneradorWeb.py`, líneas 40-60: «Esto
debería de estar en el yaml también», confirmada después con «Terminala».
Alcance autorizado: los diccionarios `PATRONES` y `EJES` pasan a
`config/web.yaml` (claves `patrones` y `ejes`) y se leen con
`ConfiguracionBackend`. Se conservan los nombres de ambas constantes, su orden y
sus valores; ninguna otra línea del archivo entra en la autorización. Los
hallazgos de la auditoría siguen abiertos.

Huella SHA-256 tras el cambio: `web/GeneradorWeb.py`
`50d7498e776d155037322562fbf3df97b673fcf8fd1194cfa2247a914d5649b1`.

Verificación ejecutada: los pares clave-etiqueta de `PATRONES` y `EJES`, en
orden, coinciden con una copia tomada antes del cambio; unittest con 73
pruebas, OK, 23 omitidas; firmas sin cambios en las 69 públicas;
`import web.GenerateModelsApp` correcto.

### Ampliación: estados y tipos como enums (2026-10-13)

Instrucción del usuario: «ESTADOS = {...} Todos estos así, pueden estar
guardados en una carpeta de enums o en el archivo yaml». En la consulta
posterior eligió una carpeta de enums, reemplazar también los literales sueltos
y autorizó cambiar en los archivos auditados solo estas constantes, sin tocar
firmas:

- `web/EstadoApp.py`: `TERMINALES` se construye desde el enum de estados de
  ítem, con la importación que eso requiere.
- `web/LectorSuperficie.py`: `LectorSuperficie.EXTENSIONES` se construye desde
  el enum de extensiones, con la importación que eso requiere.

Los demás literales de `EstadoApp.py`, `GeneradorWeb.py` y
`PaginaComparacion.py` no entran en la autorización y se conservan. Los
hallazgos de la auditoría siguen abiertos.

| Archivo | SHA-256 tras el cambio |
|---|---|
| `web/EstadoApp.py` | `eb17e965e019a95c1a0a778335ac3191a8e8e58ae2fbe41f854da250f258e977` |
| `web/LectorSuperficie.py` | `0b13a5e9c340090bb1c2df161674eee5bc37226b57ca52f59510012bd2af6db5` |

Verificación ejecutada: `TERMINALES` conserva los mismos tres valores y en el
mismo orden; `LectorSuperficie.EXTENSIONES` es igual a `{".stl", ".npz"}`;
unittest con 73 pruebas, OK, 23 omitidas; firmas sin cambios en las 69
públicas; `import web.GenerateModelsApp` correcto.

## Firmas que no cambian

La instantánea [2026-10-13-firmas-base.json](2026-10-13-firmas-base.json)
contiene las 69 firmas públicas de `web/EstadoApp.py`, `web/GeneradorWeb.py`,
`web/GenerateModelsApp.py`, `web/PaginaComparacion.py` y
`web/LectorSuperficie.py`, extraídas por AST antes del primer cambio. Al cerrar
el trabajo se compara la versión final contra esa instantánea.

## Decisión y trabajo realizado

Decisión: edición interna autorizada, firmas conservadas. Estado de este
registro: trabajo autorizado completado; hallazgos de la auditoría abiertos.

- `EstadoApp.py`: handlers resuelven el usuario por cookie, crean lotes
  persistidos y leen su progreso; nuevos `SeguirLote`, `CancelarLote`,
  `autenticado`, `usuario_nombre` y borrado de la pestaña al cambiar de usuario.
  `set_autoescalar_superficie`, `UsarSuperficieIncluida`,
  `CargarPredeterminados` y `Descargar` pasan a corrutinas con los mismos
  parámetros.
- `GeneradorWeb.py`: cachés de clase sustituidas por Redis; superficies y STL
  leídos y escritos en el bucket a través de `file_assets`; `Crear` encola un
  lote y espera al trabajador.
- `GenerateModelsApp.py`: transformador OIDC, pool PostgreSQL en el ciclo de
  vida y ruta `/historial`.
- `PaginaComparacion.py`: barra de sesión; `Enlace` usa la `object_url`.
- `visor.html`: mensajes para fallo de red y 404/403 del bucket.
- `pyproject.toml`/`uv.lock`: dependencias de PostgreSQL, S3, Redis y OIDC.
- `.gitignore`: ignora `.env` y redefine el comentario de `uploaded_files/`.
- `test_generador_web.py`: la prueba de preferencia de autoescala usa un import
  persistido.

## Verificación

Ejecutada el 2026-10-13 sobre el árbol de trabajo:

- Comparación AST de firmas públicas contra
  [2026-10-13-firmas-base.json](2026-10-13-firmas-base.json) con un script
  temporal fuera del repositorio: «Sin cambios en 69 firmas públicas». La
  comparación cubre nombre y parámetros; no registra si un método es corrutina.
- `.venv\Scripts\python.exe -B -m unittest discover -s tests`: 73 pruebas
  aprobadas, ninguna omitida, contra PostgreSQL 17 en Docker.
- Recorrido en navegador descrito en
  [OPERACION_Y_PRUEBAS.md](../../AppBackend/OPERACION_Y_PRUEBAS.md), con
  `moto_server` en lugar de MinIO.

## Riesgo residual y cierre

Los hallazgos de `AUD-2026-10-13-001` quedan abiertos. Este registro documenta
una autorización de edición limitada por firmas; no es un cierre de auditoría.
