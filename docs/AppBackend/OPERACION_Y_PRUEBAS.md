# Operación y pruebas del backend

## Entorno reproducible

Desde la raíz, con uv, Docker Compose y `make` disponibles:

```powershell
uv python install 3.14
uv sync --locked
copy infra\database\.env.example infra\database\.env   # completar secretos
copy .env.example .env                                  # completar URLs y credenciales
make db-up            # PostgreSQL 127.0.0.1:5433, MinIO :9000/:9001, Redis :6379
make db-init-s3       # bucket, políticas (lectura anónima solo de STL) y cuenta de servicio
# inicializar la base y aplicar migraciones: ver «Base de datos: inicializar y migrar»
make auth-dev-up      # proveedor OIDC de pruebas (opcional; ORTESISLAB_OIDC_PORT cambia el puerto local)
uv run python scripts/EjecutarTrabajador.py
uv run reflex run
```

Variables de la aplicación: [`.env.example`](../../.env.example). Todas se declaran en un solo lugar, la clase `Ajustes` de [`web/Ajustes.py`](../../web/Ajustes.py), y ningún otro archivo lee el entorno. El entorno real tiene prioridad sobre el `.env` de la raíz. Una variable sin valor por defecto es obligatoria: leerla sin definirla, o con valor vacío, lanza `VariableFaltante` («Falta la variable de entorno …»). Ese es el único error de la configuración; la comprobación ocurre al leer la variable, de modo que cada proceso solo exige las que usa.

| Variable | Defecto | La usa |
|---|---|---|
| `ORTESISLAB_DATABASE_URL` | Obligatoria | Web (rol `ortesislab_app`) y `MigrarSubidas.py` |
| `ORTESISLAB_WORKER_DATABASE_URL` | Obligatoria | Trabajador (rol `ortesislab_worker`) |
| `ORTESISLAB_MIGRATOR_DATABASE_URL` | Obligatoria | Alembic |
| `ORTESISLAB_TEST_DATABASE_URL`, `ORTESISLAB_TEST_WORKER_DATABASE_URL` | Obligatorias | Pruebas de persistencia (si faltan, se omiten) |
| `ORTESISLAB_TEST_MIGRATOR_DATABASE_URL` | Obligatoria | Alembic con `-x base=test` |
| `ORTESISLAB_S3_ENDPOINT`, `ORTESISLAB_S3_ACCESS_KEY`, `ORTESISLAB_S3_SECRET_KEY` | Obligatorias | Web y trabajador |
| `ORTESISLAB_S3_PUBLIC_URL` | Vacía: se usa el endpoint | Base de `object_url` |
| `ORTESISLAB_S3_BUCKET` / `ORTESISLAB_S3_REGION` | `ortesislab` / `us-east-1` | Web y trabajador |
| `ORTESISLAB_REDIS_URL` | Vacía: sin caché | Web y trabajador |
| `ORTESISLAB_OIDC_ISSUER`, `ORTESISLAB_OIDC_CLIENT_ID`, `ORTESISLAB_OIDC_CLIENT_SECRET`, `ORTESISLAB_OIDC_REDIRECT_URI`, `ORTESISLAB_SESSION_SECRET` | Obligatorias | Web; sin ellas no arranca |
| `ORTESISLAB_APP_URL` | `http://localhost:3000` | Redirección tras login y logout |
| `ORTESISLAB_COOKIE_SECURE` | `false` | `true` añade `Secure` a las cookies |

La web exige al arrancar la base y OIDC; las variables S3 se exigen en la primera operación con el bucket. El trabajador exige las S3 y la suya de base al arrancar. Para añadir una variable se declara un atributo `Variable("ORTESISLAB_…", defecto)` en `Ajustes`, se añade a `.env.example` y se lee con `Ajustes.Cargar().<atributo>`. Las seis URL de base de datos deben escribirse con el driver de SQLAlchemy, `postgresql+psycopg://usuario:clave@host:puerto/base`. Si una no empieza así, leerla lanza `VariableInvalida`; el código no las convierte.

### Valores ajustables (`config/*.yaml`)

Los límites, tiempos y tamaños del backend no van en el entorno ni en el código. Están en archivos YAML versionados en [`config/`](../../config/web.yaml), uno por área, que lee `ConfiguracionBackend.Cargar("<area>")` ([`web/ConfiguracionBackend.py`](../../web/ConfiguracionBackend.py)). Cada archivo se lee una vez por proceso, al importar el módulo que lo usa, así que un cambio exige reiniciar la web y el trabajador. Si falta un archivo o una clave, el proceso falla al importar ese módulo. Las constantes de contrato no están aquí: versiones de lector y exportador, prefijos de claves, nombre de la cookie y esquema SQL. Los estados, tipos y formatos son `StrEnum` en [`web/enums/`](../../web/enums/__init__.py), porque deben coincidir con los `CHECK` del esquema; un YAML solo guarda sus etiquetas visibles.

| Archivo | Claves | Lo usa |
|---|---|---|
| [`persistencia.yaml`](../../config/persistencia.yaml) | `conexion`: `reintentos` 3, `pausa_reintento_s` 0.05, `espera_adquisicion_s` 5, `timeout_conexion_s` 10. `lotes`: `maximo_items` 12, `maximo_pendientes` 3, `maximo_intentos` 3, `espera_reintento_s` 5. `historial`: `limite_defecto` 25, `limite_maximo` 100, `maximo_comparacion` 3 | `ConexionPostgres`, `Contratos`, `ServicioLotes`, `ServicioHistorial` |
| [`trabajador.yaml`](../../config/trabajador.yaml) | `lease_s` 120, `latido_s` 30, `supervision_s` 30, `conciliacion_s` 600. `conciliador`: `horas_staged` 24, `dias_rechazo` 30, `lote_comprobacion` 200 | `TrabajadorGeneracion`, `ConciliadorArchivos` |
| [`cache.yaml`](../../config/cache.yaml) | `ttl_s` 604800 (7 días), `reintento_s` 30, `timeout_s` 0.5 | `CacheRedis` |
| [`almacen.yaml`](../../config/almacen.yaml) | `timeout_conexion_s` 3, `timeout_lectura_s` 30, `intentos` 3 | `StorageS3` |
| [`sesion.yaml`](../../config/sesion.yaml) | `duracion_horas` 12, `intercambio_oidc_s` 600 | `ContextoUsuario`, `AutenticacionOidc` |
| [`web.yaml`](../../config/web.yaml) | `intervalo_progreso_s` 1, `maximo_variantes` 12, `espera_crear_s` 600, `maximo_bytes` 50 MiB, `maximo_descomprimido_bytes` 128 MiB; `patrones` (5) y `ejes` (11): clave y etiqueta visible, en el orden de los selectores; `estados_visibles` (5): etiqueta de cada estado de ítem en `/historial` | `EstadoApp`, `GeneradorWeb`, `LectorSuperficie`, `EstadoHistorial` |

Al editarlos hay que respetar dos relaciones que el código no comprueba:
- `web.yaml` `maximo_variantes` no debe superar `persistencia.yaml` `lotes.maximo_items`; si lo supera, la admisión rechaza los lotes más grandes.
- `latido_s` debe ser bastante menor que `lease_s`, o el trabajador pierde la reserva mientras construye.

El complemento de Blender conserva su configuración JSON en `GenerateModelsApp/config/`, porque el Python de Blender no incluye PyYAML.

`ORTESISLAB_OIDC_REDIRECT_URI` debe apuntar al puerto donde responde `/auth/callback`: en desarrollo, el backend Reflex (8000); con `reflex run --env prod`, la aplicación sirve frontend y backend en un único puerto (3000). Blender no es requisito web ni del trabajador. El visor descarga Three.js desde unpkg.

Para trasladar subidas de la arquitectura anterior: `uv run python scripts/MigrarSubidas.py --simular` y después sin `--simular`. Cada archivo se borra de `uploaded_files/` solo después de verificar su objeto en el bucket.

Antes de crear/modificar código Reflex o iniciar/depurar procesos, aplicar las skills del repositorio `reflex-docs`, `setup-python-env` y `reflex-process-management` según [AGENTS.md](../../AGENTS.md).

## Base de datos: inicializar y migrar

El repositorio no trae migraciones: `db/alembic/versions/` está vacío y las migraciones las genera y aplica el responsable del esquema. Los comandos de esta sección son manuales; `make` no ejecuta migraciones. Los ejemplos usan PowerShell desde la raíz, con `$c` como abreviatura de Compose:

```powershell
$c = "docker compose -f infra/database/compose.yaml --env-file infra/database/.env"
```

### 1. Inicializar una base vacía

En el primer `make db-up` (volumen nuevo) [`infra/database/init/01_roles.sh`](../../infra/database/init/01_roles.sh) crea `ortesislab_dev`, los roles `ortesislab_migrator`, `ortesislab_app`, `ortesislab_worker` y `ortesislab_backup`, sus `search_path` y `statement_timeout`, y el esquema `ortesislab` cuyo dueño es el migrador. No crea tablas.

Si el volumen ya existe pero la base no (por ejemplo, tras `make db-drop`), los roles siguen en el clúster y basta con crear la base y su esquema con [`db/test/preparar_base.sql`](../../db/test/preparar_base.sql), que recibe el nombre en la variable `base`:

```powershell
Invoke-Expression "$c exec -T postgres createdb -U ortesislab_admin -O ortesislab_migrator ortesislab_dev"
Get-Content -Raw db\test\preparar_base.sql | Invoke-Expression "$c exec -T postgres psql -v ON_ERROR_STOP=1 -q -v base=ortesislab_dev -U ortesislab_admin -d ortesislab_dev"
```

Para la base de pruebas, `make db-test-reset` borra `ortesislab_test`, la vuelve a crear y aplica el mismo archivo con `base=ortesislab_test`. Queda vacía hasta migrarla.

### 2. Configurar Alembic

[`alembic.ini`](../../alembic.ini) apunta a [`db/alembic/`](../../db/alembic/env.py). `env.py` toma la URL del rol migrador de `Ajustes` (`ORTESISLAB_MIGRATOR_DATABASE_URL`; con `-x base=test`, `ORTESISLAB_TEST_MIGRATOR_DATABASE_URL`; cualquier otro valor de `base` usa la primera), usa `Base.metadata` de [`web/persistence/Modelos.py`](../../web/persistence/Modelos.py) como esquema objetivo, guarda `alembic_version` en `ortesislab`, ignora esa tabla en la comparación y compara tipos y defaults. Tiene un único flujo de ejecución, siempre conectado a la base: no admite el modo `--sql` de Alembic, que genera SQL sin conexión.

### 3. Crear una migración

Cambiar primero `Modelos.py` y después generar la revisión contra una base que esté en `head` (o vacía, para la primera):

```powershell
uv run alembic -x base=test revision --autogenerate -m "descripcion"
```

El autogenerado debe revisarse a mano antes de aplicarlo. Alembic no genera estos elementos del esquema, que la migración inicial debe incluir con `op.execute` u operaciones explícitas (su contenido está en [DATABASE.md](DATABASE.md#12-migraciones-con-alembic)):

- la función y el trigger `model_versions_comprobar` de `model_versions`;
- los `GRANT` de `ortesislab_app` y `ortesislab_worker`;
- la FK circular `batch_items_winning_attempt_fk`: el modelo la marca `use_alter`, pero el autogenerado la deja dentro de `create_table('batch_items')`. Hay que quitarla de ahí y crearla con `op.create_foreign_key` después de `generation_attempts`; en `downgrade`, borrarla antes de las tablas.

Los cambios posteriores de `CHECK`, `GRANT`, funciones o triggers también se escriben a mano.

### 4. Aplicar, consultar y revertir

| Acción | Desarrollo | Base de pruebas |
|---|---|---|
| Aplicar pendientes | `uv run alembic upgrade head` | `uv run alembic -x base=test upgrade head` |
| Revisión actual | `uv run alembic current` | `uv run alembic -x base=test current` |
| Historial | `uv run alembic history` | igual |
| Modelos y base coinciden | `uv run alembic check` | `uv run alembic -x base=test check` |
| Revertir la última | `uv run alembic downgrade -1` | `uv run alembic -x base=test downgrade -1` |
`alembic check` termina con error si los modelos y la base difieren en lo que Alembic compara, es decir, tablas, columnas, tipos, defaults, índices y restricciones con nombre. No compara `GRANT` ni triggers. Alembic no bloquea migraciones concurrentes: ejecutarlas desde un único operador. Después de migrar `ortesislab_dev`, `make db-seed` carga el fixture opcional.

## Comprobación funcional

1. Sin sesión, pulsar Previsualizar: mensaje `Inicie sesión para continuar.` y ninguna fila nueva.
2. Iniciar sesión: la cookie `ortesislab_sesion` es HttpOnly; la barra muestra el nombre.
3. Previsualizar: progreso `En cola…`, ficha con métricas y STL en el visor cargado desde su `object_url`.
4. Recargar la página: el último lote reaparece desde la base.
5. Lote de varias variantes: progreso `x de y` y comparación de hasta tres vistas.
6. Descargar: `Content-Disposition: attachment` y evento `export_downloaded`.
7. `/historial`: filtrar, comparar versiones (diferencias de parámetros) y restaurar (versión nueva con `parent_version_id`).
8. Cerrar sesión y entrar con otro usuario: no ve fichas, historial ni archivos del anterior.
9. `make db-backup FILE=x.dump` y restauración en una base desechable.

## Pruebas existentes y trazabilidad

Las pruebas de persistencia necesitan `ortesislab_test` creada con `make db-test-reset` y migrada con `uv run alembic -x base=test upgrade head`, y las variables `ORTESISLAB_TEST_DATABASE_URL` y `ORTESISLAB_TEST_WORKER_DATABASE_URL`. Sin base, sin esquema o sin variables se omiten con un motivo explícito. Cada rol abre su propia `Session` de SQLAlchemy, que confirma al salir del `with`. Los errores de PostgreSQL se comprueban en `DBAPIError.orig`. Levantan un `ThreadedMotoServer` (API S3 por HTTP en lugar de MinIO) y usan Redis local en la base 15 si responde; si no, prueban sin caché.

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests
```

El detalle de cada carpeta está en [tests/README.md](../../tests/README.md).

| Archivo de prueba | Evidencia que aporta |
|---|---|
| `tests/aplicacion_web/test_generador_web.py` | 13 casos: combinaciones y límites, semilla, STL, lectura STL/NPZ, preferencia de autoescala con import persistido, archivo `tests/assets/Test.stl`, expansión e índices inválidos |
| `tests/persistencia/test_almacen_import.py` | 6 casos: import con `object_url` y hash, deduplicación, rechazo, aislamiento entre usuarios, plantilla por usuario y migración de `uploaded_files` |
| `tests/persistencia/test_lotes_trabajador.py` | 8 casos: idempotencia, cuota, lote parcial con STL en el bucket, lease vencido, cancelación, generación sin Redis, restauración y conciliación |
| `tests/persistencia/test_propiedad_datos.py` | 8 casos: acceso entre usuarios, FK compuestas, URL obligatoria en `ready`, revisión de preferencias, permisos de roles app/trabajador y validez de sesiones |
| `tests/geometria/test_escala_malla.py` | 12 casos: factores decimales, desactivación, selección por paso y conservación de tamaño ante presupuesto |
| `tests/nucleo/test_nucleo.py` | 14 casos: equivalencia algorítmica con referencia, catálogo, validación, importación sin Blender, volumen/material |
| `tests/geometria/test_refinador_malla.py` | 3 casos: subdivisión, rejilla recortada y escala/paso |
| `tests/geometria/test_suavizado_borde.py` | 4 casos: dientes, tramo recto, borde corto e integración del marco |
| `tests/geometria/test_superficie_abierta.py` | 5 casos: cierre local del espesor, inversión, rechazo de capas/duplicados/sueltos/orientación |

Línea base con SQLAlchemy: **73 pruebas, 50 aprobadas y 23 omitidas, el 2026-10-13** con `.venv\Scripts\python.exe -B -m unittest discover -s tests`. Se omitieron todas las de `tests/persistencia/` porque no existían `ortesislab_dev` ni `ortesislab_test` ni migraciones. La persistencia SQLAlchemy no se ha probado contra PostgreSQL. Sí se compilaron con el dialecto PostgreSQL las sentencias de los 59 métodos de repositorio. La comprobación funcional 1–9 y las 73 pruebas sin omisiones se ejecutaron antes, con la implementación Psycopg/dbmate: no validan la versión actual. Ver [registro](../Agents/REGISTRO_CAMBIOS.md).

## Diagnóstico

| Síntoma | Revisar |
|---|---|
| `Inicie sesión para continuar.` con sesión iniciada | Cookie ausente o vencida (12 h), sesión revocada, `ORTESISLAB_SESSION_SECRET` cambiado |
| `/auth/login` muestra la página 404 de la app | El enlace debe navegar con recarga completa; revisar `ORTESISLAB_OIDC_REDIRECT_URI` y el puerto del backend |
| `VariableFaltante: Falta la variable de entorno …` al arrancar o en la primera subida | Definir esa variable en el entorno o en `.env` |
| `VariableInvalida: … debe empezar por postgresql+psycopg://` | Cambiar el esquema de esa URL de `postgresql://` a `postgresql+psycopg://` |
| Lote queda `En cola…` | El trabajador no está corriendo o no alcanza la base; revisar su log |
| Base no disponible | Motor SQLAlchemy no abierto al arrancar (log `web`); `make db-health` |
| `relation "..." does not exist` | Base sin migrar: `uv run alembic current` y `upgrade head` |
| Visor: `El STL ya no está en el almacén` | Objeto borrado o fila `missing`; volver a generar |
| Visor: `No se pudo contactar con el almacén` | MinIO caído, `ORTESISLAB_S3_PUBLIC_URL` incorrecta o política de lectura de STL no aplicada |
| Superficie rechazada | Debe ser abierta, orientada y conectada; un STL de una ortesis con espesor no sirve como base |
| Generación lenta tras reinicio de Redis | Caché vacía; se reconstruye por contenido |
| Demora o mucha memoria | Paso, ancho de nervadura, número de caras, tamaño de celda y número de variantes |
| `EntornoBlenderRequerido` al importar web | Importación accidental de adaptadores Blender |

Logs: `ortesislab.<subsistema>`, consola INFO y archivo DEBUG `GenerateModelsApp/logs/ortesislab.log`, según `config/registro.json`.

## Despliegue y recuperación

El repositorio incluye Compose para desarrollo local con puertos ligados a 127.0.0.1. No hay infraestructura cloud, CI ni TLS configurados. Para varias instancias Reflex se necesita el mismo PostgreSQL, bucket y Redis; los lotes se recuperan desde la base tras reiniciar cualquier proceso y los leases vencidos vuelven a la cola. Respaldo: `make db-backup` (metadatos) y `make s3-backup` (objetos) deben tomarse juntos; `db-restore` no restaura objetos. Alembic no bloquea migraciones concurrentes: ejecutarlas desde un único operador.
