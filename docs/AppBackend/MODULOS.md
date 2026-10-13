# Carpetas y archivos de AppBackend

Las rutas se expresan desde la raíz del repositorio. [INVENTARIO.md](../Agents/INVENTARIO.md) cubre también herramientas, pruebas, configuraciones, archivos vacíos y artefactos. El [índice de símbolos](SIMBOLOS.md) enumera automáticamente cada clase, función y método del ámbito backend.

## Infraestructura y entradas

| Archivo/carpeta | Responsabilidad y relación |
|---|---|
| [`rxconfig.py`](../../rxconfig.py) | Selecciona el módulo web, sitemap, Tailwind V4 y tema Radix indigo/slate/medium |
| [`web/GenerateModelsApp.py`](../../web/GenerateModelsApp.py) | Instancia `rx.App` con el transformador OIDC, abre/cierra el motor SQLAlchemy de PostgreSQL en el ciclo de vida y registra `/` e `/historial` |
| [`web/Ajustes.py`](../../web/Ajustes.py) | Única declaración y lectura de las variables `ORTESISLAB_*`: cada atributo de `Ajustes` es una `Variable(clave, defecto)`; sin defecto es obligatoria y leerla ausente o vacía lanza `VariableFaltante`; las URL de base exigen el prefijo `postgresql+psycopg://` y, si no lo tienen, lanzan `VariableInvalida`. `Faltante(*atributos)` devuelve el mensaje de la primera variable sin definir, o una cadena vacía; las pruebas de persistencia lo usan para decidir si se omiten. `Cargar()` combina el `.env` raíz (UTF-8 con o sin BOM) con el entorno real, que tiene prioridad, sin modificar `os.environ` |
| [`web/__init__.py`](../../web/__init__.py) | Marcador del paquete web; no arranca servicios |
| [`web/ConfiguracionBackend.py`](../../web/ConfiguracionBackend.py) | `ConfiguracionBackend.Cargar(area)` lee `config/<area>.yaml` con `yaml.safe_load` y lo guarda en caché por proceso; distinta de `GenerateModelsApp.util.Utilidades.Configuracion`, que lee el JSON del complemento |
| [`config/`](../../config/web.yaml) | YAML de valores ajustables del backend: `persistencia`, `trabajador`, `cache`, `almacen`, `sesion` y `web`; catálogo en [OPERACION_Y_PRUEBAS.md](OPERACION_Y_PRUEBAS.md#valores-ajustables-configyaml) |
| [`.env.example`](../../.env.example) | Plantilla de variables: URLs de base app/trabajador/migrador, bucket S3, Redis, OIDC, URL de la app y bases de prueba |
| [`Makefile`](../../Makefile) | Envoltorio de Docker Compose y clientes PostgreSQL/MinIO: `db-up`, `db-seed`, backups, `db-test-reset` (base vacía), `auth-dev-up`; no ejecuta migraciones; `make db-help` los lista |
| [`infra/database/`](../../infra/database/compose.yaml) | Compose con PostgreSQL 17, MinIO, Redis, cliente `mc` y proveedor OIDC de pruebas (perfil `auth-dev`); roles y esquema vacío en `init/01_roles.sh`; políticas e inicialización del bucket en `minio/` |
| [`alembic.ini`](../../alembic.ini) / [`db/alembic/`](../../db/alembic/env.py) | Configuración de Alembic para el esquema `ortesislab` con el rol migrador; `versions/` sin revisiones en el repositorio (ver [DATABASE.md](DATABASE.md#12-migraciones-con-alembic)) |
| `db/seeds/development.sql`, `db/test/preparar_base.sql` | Datos de desarrollo y creación del esquema y permisos en una base vacía |
| [`pyproject.toml`](../../pyproject.toml) | Dependencias Python (incluye `sqlalchemy`, `alembic`, `psycopg[binary]`, `pyyaml`, `boto3`, `redis`, `authlib`, `itsdangerous`), versión y empaquetado |
| [`uv.lock`](../../uv.lock) / [`.python-version`](../../.python-version) | Resolución Python y selección de intérprete |
| `reflex.lock/` | `package.json` y `bun.lock` versionan dependencias del frontend generado |
| `.web/`, `.states/`, `.venv/` | Compilación frontend, artefactos de estado y entorno virtual generados; no modificar para implementar reglas |
| `uploaded_files/` | Directorio de la arquitectura anterior; solo lo lee `scripts/MigrarSubidas.py`, que lo vacía tras verificar cada objeto en el bucket |
| `GenerateModelsApp/logs/` | Registro compartido del dominio; aparece bajo demanda y está ignorado por Git |
| [`scripts/EjecutarTrabajador.py`](../../scripts/EjecutarTrabajador.py) | Proceso trabajador: motor del rol `ortesislab_worker`, bucle de cola y conciliación; `--una-vez` vacía la cola y termina |
| [`scripts/MigrarSubidas.py`](../../scripts/MigrarSubidas.py) | Traslado único de `uploaded_files/` al bucket bajo el usuario semilla `subidas-locales-previas`; `--simular` solo lista; repone objetos ausentes de filas ya migradas |
| [`src/generatemodelsapp/__init__.py`](../../src/generatemodelsapp/__init__.py) / [`scripts/IniciarConsola.py`](../../scripts/IniciarConsola.py) | Saludo de consola; no arranca Reflex |

## Estado de páginas

### `web/EstadoApp.py`

[`EstadoApp`](../../web/EstadoApp.py) hereda de `rx.State`. Los números de formulario se almacenan como cadenas para permitir edición y coma decimal.

| Grupo | Métodos/campos | Función |
|---|---|---|
| Parámetros | `pattern`, 13 campos numéricos (incluida `seed`), `liner`, `repair`, `flip_normals` | Adaptación del contrato compartido; ver [parámetros](../BlenderPlugin/PARAMETROS.md) |
| Edición | `set_*` explícitos con `@rx.event` | Asignan valores; `set_autoescalar_superficie` además guarda la preferencia con control de revisión |
| Sesión | `autenticado`, `usuario_nombre`, `_propietario`, `_Usuario`, `_OlvidarTrabajo` | Resuelven el usuario por cookie; al cambiar de usuario o cerrar sesión borran fichas, vistas y superficie de la pestaña |
| Entrada | `CargarSuperficie`, `UsarSuperficieIncluida`, `superficie_*` | Registran el import del usuario (`GuardarSuperficie`) o vuelven a la plantilla |
| Inicialización | `CargarPredeterminados` | Defaults JSON, preferencia de autoescala, último lote del usuario y reanudación con `SeguirLote` si está abierto |
| Trabajo | `Previsualizar`, `PedirLote` (fijan `_solicitud`), `Generar`, `SeguirLote`, `CancelarLote`, `_Seguir`, `_Publicar`, `lote_id` | Admisión idempotente del lote y lectura del progreso cada segundo |
| Selección | `Ver`, `Comparar`, `_Mostrar`, `archivo`, `ficha_*`, `vistas` | `archivo` es la `object_url` del STL |
| Descarga | `Descargar` | Registra `export_downloaded` y devuelve `rx.download(url=object_url)` |
| Derivados | `aviso_escala`, `espesor_total`, `porcentaje` | Aviso de escala, suma nominal de espesores y progreso entero |
| Adaptación | `_Numero`, `_Opciones`, `_Variantes` | Parsean texto, validan semilla y construyen opciones/combinaciones |

### `web/EstadoHistorial.py`

[`EstadoHistorial`](../../web/EstadoHistorial.py): filtros (`filtro_patron`, `filtro_estado`, `filtro_desde`, `filtro_hasta`), cursor (`_cursores`, `Siguiente`, `Anterior`), selección de hasta 3 versiones (`Seleccionar`, `comparacion`), `Restaurar`, `Reintentar` y `Descargar`. `_Fila` y `_Tarjeta` traducen DTO a textos; `_Tarjeta` lista los parámetros que difieren de la primera versión elegida. `ESTADOS_VISIBLES` (etiqueta de cada estado de ítem) se lee de `config/web.yaml`.

## `web/GeneradorWeb.py`

[`GeneradorWeb`](../../web/GeneradorWeb.py) conserva sus firmas públicas. `PATRONES`, `EJES` y `MAXIMO_VARIANTES` siguen exportándose desde aquí, pero sus valores salen de `config/web.yaml`.

| Métodos | Entrada → proceso → salida |
|---|---|
| `_Origen`, `Cruda`, `EjeMayor` | Nombre interno o vacío → SHA-256 del NPZ del usuario activo o de la plantilla → arrays originales (Redis o bucket) |
| `Superficie`, `_SuperficieConDiagnostico`, `SuperficieRefinada`, `_SuperficieRefinadaConDiagnostico` | Escala y refinamiento; la tupla refinada y su diagnóstico se guardan en Redis por contenido, paso y autoescala |
| `GuardarSuperficie` | Bytes → `ServicioImports.Importar` del usuario activo → `superficie-<asset hex>.npz` y metadatos |
| `Crear` | Encola un lote `single`, espera al trabajador (600 s) y devuelve la ficha |
| `_FichaDeItem`, `Ficha`, `FichaError`, `Detalle`, `Numero` | Ítem persistido o error → diccionario y texto español |
| `Combinaciones`, `Triangulos`, `Stl` | Producto acotado de variantes; triangulación y STL binario |
| `Ruta`, `Leer`, `Escribir`, `RutaSuperficie` | `object_url` o nombre → clave del bucket validada contra el usuario activo; lectura verificada por SHA-256; `Escribir` solo repone bytes con el mismo hash |

## `web/LectorSuperficie.py`

[`LectorSuperficie`](../../web/LectorSuperficie.py) restringe extensiones, tamaño, finitud y topología. `_StlBinario` acepta registros si el tamaño es exactamente `84 + 50*n`; de lo contrario `_StlAscii` extrae grupos de tres líneas `vertex`. `_Stl` fusiona coordenadas por cuantización y recalcula normales. `_Npz` revisa la expansión declarada ZIP y carga sin pickle. `Preparar` devuelve la superficie analizada y metadatos; no escribe por sí mismo.

## Persistencia: `web/persistence/`

| Archivo | Responsabilidad |
|---|---|
| [`ConexionPostgres.py`](../../web/persistence/ConexionPostgres.py) | Motor SQLAlchemy `postgresql+psycopg` por proceso (`pool_size`=máximo, sin overflow, espera de 5 s, `pool_pre_ping`) y `sessionmaker(expire_on_commit=False)`. `Abrir` prueba las conexiones mínimas; `Transaccion` entrega una `Session` con commit o rollback; `Ejecutar(fn)` reintenta hasta 3 veces ante deadlock o fallo de serialización (`DBAPIError.orig`). La espera agotada y los errores de conexión se convierten en `PersistenciaNoDisponible`. Recibe la URL tal como la entrega `Ajustes` |
| [`Modelos.py`](../../web/persistence/Modelos.py) | Modelos declarativos de las 13 tablas con FK compuestas, `CHECK` con nombre, `JSONB`, `timestamptz` e índices parciales; fuente de `alembic --autogenerate`. Los `CHECK ... IN (...)`, los `server_default` de estado y los índices parciales por estado se construyen desde `web/enums`: `_Valores(columna, tabla, Enum)` recorre los miembros en orden y `_Defecto(miembro)` genera el literal |
| [`Contratos.py`](../../web/persistence/Contratos.py) | DTO inmutables (`UsuarioAutenticado`, `Asset`, `ImportDTO`, `VersionDTO`, `SolicitudLote`, `LoteDTO`, `ItemLote`, `ProgresoLote`, `TrabajoReservado`, `ResultadoDTO`, `FilaHistorial`…), errores con mensaje visible y constantes de versión/cuota. `ProgresoLote` usa `ITEMS_TERMINALES` y `LOTES_ABIERTOS` |

## Valores cerrados: `web/enums/`

`StrEnum` por dominio; cada miembro es también su texto, así que se compara con las cadenas leídas de PostgreSQL y psycopg lo envía por su valor. Deben coincidir con los `CHECK` del esquema: cambiar o añadir un valor exige una migración. Repositorios, servicios, jobs, `MigrarSubidas.py` y `EstadoHistorial` usan los miembros en lugar de literales. En los archivos auditados solo `EstadoApp.TERMINALES` y `LectorSuperficie.EXTENSIONES` salen de aquí; `GeneradorWeb.py`, `PaginaComparacion.py` y el resto de `EstadoApp.py` conservan sus literales.

| Archivo | Enums |
|---|---|
| [`Usuarios.py`](../../web/enums/Usuarios.py) | `EstadoUsuario` |
| [`Archivos.py`](../../web/enums/Archivos.py) | `TipoAsset`, `EstadoAsset`, `ExtensionSuperficie` (`.stl`, `.npz`) |
| [`Imports.py`](../../web/enums/Imports.py) | `OrigenImport`, `EstadoImport`, `FormatoImport` |
| [`Lotes.py`](../../web/enums/Lotes.py) | `BackendGeneracion`, `ModoLote`, `EstadoLote` (incluye `partial`), `EstadoItem`, `EstadoIntento`; tuplas `ITEMS_TERMINALES` y `LOTES_ABIERTOS` |
| [`Resultados.py`](../../web/enums/Resultados.py) | `EstadoValidacion`, `AlcanceGeometria`, `FormatoExport`, `UnidadExport`, `EstadoExport` |
| [`Historial.py`](../../web/enums/Historial.py) | `TipoEvento` |
| [`repositorios/`](../../web/persistence/repositorios/__init__.py) | Paquete con un archivo por repositorio; `__init__` reexporta las nueve clases y `NOMBRE_PROYECTO_PREDETERMINADO`, por lo que se importan con `from web.persistence.repositorios import RepositorioX`. Todos reciben una `Session` abierta, nunca hacen commit y devuelven DTO o `dict` |
| [`repositorios/RepositorioBase.py`](../../web/persistence/repositorios/RepositorioBase.py) | Clase padre con `TABLA` y `DTO` por subclase y ayudas protegidas: `_Uno` (primera fila o `None`), `_Todos`, `_Construir`/`_Dto` (DTO desde los campos del dataclass), `_Opcional`, `_Lista` y `_DelUsuario`, que filtra por `user_id`, admite `FOR UPDATE` y lanza `AccesoDenegado` si no hay fila |
| [`repositorios/Consultas.py`](../../web/persistence/repositorios/Consultas.py) | Alias de las tablas de `Modelos`, `AHORA` y fragmentos compartidos: `Segundos`, `UltimoError`, `ConStlGanador` y `ColumnasResultado` |
| `repositorios/Repositorio*.py` | `RepositorioUsuarios` (usuarios y sesiones), `RepositorioPreferencias` (revisión optimista), `RepositorioProyectos`, `RepositorioAssets`, `RepositorioImports`, `RepositorioVersiones`, `RepositorioLotes` (admisión, reserva con `FOR UPDATE SKIP LOCKED`, lease y cierre), `RepositorioResultados` (resultados y exports) y `RepositorioHistorial` (cursor compuesto) |

## Servicios: `web/services/`

| Archivo | Responsabilidad |
|---|---|
| [`ContextoUsuario.py`](../../web/services/ContextoUsuario.py) | Cookie de sesión, `Requerir`, `IniciarSesion`, `CerrarSesion`, `Activar`/`Actual` |
| [`AutenticacionOidc.py`](../../web/services/AutenticacionOidc.py) | Aplicación Starlette de `/auth/*` con authlib; las variables OIDC son obligatorias y su ausencia impide arrancar la web |
| [`ServicioImports.py`](../../web/services/ServicioImports.py) | Import con deduplicación por SHA-256 del original; staged → original → normalización → NPZ → Redis → ready; plantilla por usuario; `Resolver` de `superficie_archivo` |
| [`ServicioVersiones.py`](../../web/services/ServicioVersiones.py) | Parámetros canónicos, hash, instantánea de material PETG y alta de versiones numeradas |
| [`ServicioLotes.py`](../../web/services/ServicioLotes.py) | Admisión, progreso, último lote, espera, cancelación; del lado trabajador: reserva, latido, salidas staged, confirmación, fallo con reintento y abandono de leases vencidos |
| [`GeneradorGeometrico.py`](../../web/services/GeneradorGeometrico.py) | Construcción pura: superficie, cascarón, métricas, STL y JSON; no toca base ni bucket |
| [`ServicioHistorial.py`](../../web/services/ServicioHistorial.py) | Listado paginado (25 por defecto, 100 máximo), detalle, comparación de hasta 3, restaurar, reintentar y registro de descarga |
| [`ServicioPreferencias.py`](../../web/services/ServicioPreferencias.py) | Lectura y guardado de la autoescala con revisión optimista |

## Almacenamiento, caché y trabajos

| Archivo | Responsabilidad |
|---|---|
| [`web/storage/AlmacenamientoPrivado.py`](../../web/storage/AlmacenamientoPrivado.py) | Protocolo de almacén, `PATRON_CLAVE`, `Almacen` (instancia actual, claves, SHA-256, lectura verificada) y errores `AlmacenamientoNoDisponible`/`ObjetoAusente` |
| [`web/storage/StorageS3.py`](../../web/storage/StorageS3.py) | Cliente boto3 path-style con timeouts; publica con tipo, metadato `sha256` y `Content-Disposition` y comprueba con `HEAD` |
| [`web/cache/CacheRedis.py`](../../web/cache/CacheRedis.py) | Claves por contenido, tuplas en NPZ, diagnósticos en JSON, TTL 7 días y apagado temporal de 30 s ante fallos |
| [`web/jobs/TrabajadorGeneracion.py`](../../web/jobs/TrabajadorGeneracion.py) | `Ciclo`, `Procesar` (latido, construcción, cancelación, publicación, confirmación) y `Ejecutar` con supervisión de leases y conciliación periódica |
| [`web/jobs/ConciliadorArchivos.py`](../../web/jobs/ConciliadorArchivos.py) | Limpieza de staged y rechazados, detección de objetos ausentes y borrado de huérfanos |

## Dominio reutilizado

`Modeling.py` orquesta patrones/cascarón; `Malla.py` valida la base; `EscalaMalla.py` decide factores decimales; `RefinadorMalla.py` subdivide; `SuavizadoBorde.py` filtra el contorno; `Cascaron.py` recorta y engrosa; `constants/Paterns.py` calcula campos; `constants/Materials.py` convierte volumen en coste; `util/Utilidades.py` lee configuración y registra errores; `Excepciones.py` tipa los fallos. Su explicación completa está en [BlenderPlugin/MODULOS.md](../BlenderPlugin/MODULOS.md) y [ALGORITMOS.md](../BlenderPlugin/ALGORITMOS.md).

`ApiBlender`, `Interfaz`, `Objeto`, `Superficie`, `ReparacionMalla`, `ValidacionMalla`, `Exportacion` y `OrtesisLab` no deben importarse para arrancar la web ni el trabajador: requieren el entorno Blender.
