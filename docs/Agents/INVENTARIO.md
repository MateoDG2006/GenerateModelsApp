# Inventario completo del repositorio

> Generado por `python docs/Agents/Scripts/GenerarIndices.py`. Incluye archivos versionados y nuevos no ignorados; excluye Git, dependencias y salidas locales ignoradas. Las descripciones de la tabla se editan a mano y el script las conserva.

Los catálogos de [backend](../AppBackend/MODULOS.md), [frontend](../AppFrontend/COMPONENTES_Y_FLUJOS.md) y [plugin](../BlenderPlugin/MODULOS.md) explican las colaboraciones. Aquí se asigna propósito a cada archivo propio; no se atribuye lógica de aplicación a librerías de terceros.

| Archivo | Propósito |
|---|---|
| [.agents/skills/reflex-docs/SKILL.md](../../.agents/skills/reflex-docs/SKILL.md) | Skill local Reflex: instrucciones y referencias para agentes. |
| [.agents/skills/reflex-process-management/SKILL.md](../../.agents/skills/reflex-process-management/SKILL.md) | Skill local Reflex: instrucciones y referencias para agentes. |
| [.agents/skills/setup-python-env/SKILL.md](../../.agents/skills/setup-python-env/SKILL.md) | Skill local Reflex: instrucciones y referencias para agentes. |
| [.codegraph/.gitignore](../../.codegraph/.gitignore) | Excluye el índice local de CodeGraph del versionado. |
| [.env.example](../../.env.example) | Plantilla de variables `ORTESISLAB_*` de la aplicación, el trabajador y las pruebas. |
| [.gitignore](../../.gitignore) | Excluye entornos, compilación, estados, subidas anteriores, logs y `.env`. |
| [.python-version](../../.python-version) | Selecciona el intérprete Python del proyecto para uv. |
| [.vscode/settings.json](../../.vscode/settings.json) | Configuración local de editor; actualmente objeto vacío. |
| [AGENTS.md](../../AGENTS.md) | Instrucciones Reflex y obligación de mantenimiento documental para agentes. |
| [CLAUDE.md](../../CLAUDE.md) | Entrada de instrucciones que remite a AGENTS.md. |
| [GenerateModelsApp.zip](../../GenerateModelsApp.zip) | Distribución Blender; puede no coincidir con fuentes hasta reempaquetar. |
| [GenerateModelsApp/ApiBlender.py](../../GenerateModelsApp/ApiBlender.py) | API de Blender, separada del núcleo geométrico. |
| [GenerateModelsApp/Cascaron.py](../../GenerateModelsApp/Cascaron.py) | Recorte de celdas y cascarón de espesor variable. |
| [GenerateModelsApp/EscalaMalla.py](../../GenerateModelsApp/EscalaMalla.py) | Diagnóstico de unidades para una superficie de ortesis. |
| [GenerateModelsApp/Excepciones.py](../../GenerateModelsApp/Excepciones.py) | Errores de OrtesisLab. |
| [GenerateModelsApp/Exportacion.py](../../GenerateModelsApp/Exportacion.py) | Exporta el STL en milímetros y un JSON con parámetros y comprobación. |
| [GenerateModelsApp/Interfaz.py](../../GenerateModelsApp/Interfaz.py) | Panel N y operadores de OrtesisLab en la vista 3D. |
| [GenerateModelsApp/Malla.py](../../GenerateModelsApp/Malla.py) | Análisis de la superficie abierta, sin Blender. |
| [GenerateModelsApp/Modeling.py](../../GenerateModelsApp/Modeling.py) | Modelo de impresión y construcción de la geometría. |
| [GenerateModelsApp/Objeto.py](../../GenerateModelsApp/Objeto.py) | Crea o actualiza el objeto OL_Ortesis en la escena de Blender. |
| [GenerateModelsApp/OrtesisLab.py](../../GenerateModelsApp/OrtesisLab.py) | Complemento OrtesisLab dentro del paquete. |
| [GenerateModelsApp/RefinadorMalla.py](../../GenerateModelsApp/RefinadorMalla.py) | Refinamiento triangular independiente de Blender para evaluar patrones. |
| [GenerateModelsApp/ReparacionMalla.py](../../GenerateModelsApp/ReparacionMalla.py) | Limpieza segura de la superficie base dentro de Blender. |
| [GenerateModelsApp/SuavizadoBorde.py](../../GenerateModelsApp/SuavizadoBorde.py) | Suavizado del contorno exterior antes de dar espesor. |
| [GenerateModelsApp/Superficie.py](../../GenerateModelsApp/Superficie.py) | Carga y lectura de la superficie interior dentro de Blender. |
| [GenerateModelsApp/ValidacionMalla.py](../../GenerateModelsApp/ValidacionMalla.py) | Comprobación geométrica de la malla ya generada. |
| [GenerateModelsApp/__init__.py](../../GenerateModelsApp/__init__.py) | Paquete del complemento de Blender y del núcleo de geometría. |
| [GenerateModelsApp/config/comprobacion_geometrica.json](../../GenerateModelsApp/config/comprobacion_geometrica.json) | Mediciones históricas de referencia, no umbrales de aceptación. |
| [GenerateModelsApp/config/limites.json](../../GenerateModelsApp/config/limites.json) | Umbrales, tolerancias y presupuestos de algoritmos. |
| [GenerateModelsApp/config/parametros_defecto.json](../../GenerateModelsApp/config/parametros_defecto.json) | Valores iniciales de las 17 opciones geométricas. |
| [GenerateModelsApp/config/registro.json](../../GenerateModelsApp/config/registro.json) | Niveles de logging y nombre de archivo. |
| [GenerateModelsApp/constants/Materials.py](../../GenerateModelsApp/constants/Materials.py) | Materiales de impresión. |
| [GenerateModelsApp/constants/Nombres.py](../../GenerateModelsApp/constants/Nombres.py) | Nombres estables de objetos, atributos y archivos. |
| [GenerateModelsApp/constants/Paterns.py](../../GenerateModelsApp/constants/Paterns.py) | Patrones de nervadura. |
| [GenerateModelsApp/constants/__init__.py](../../GenerateModelsApp/constants/__init__.py) | Constantes de OrtesisLab: nombres, patrones, materiales y límites. |
| [GenerateModelsApp/util/Utilidades.py](../../GenerateModelsApp/util/Utilidades.py) | Registro de mensajes y lectura de la carpeta config. |
| [GenerateModelsApp/util/__init__.py](../../GenerateModelsApp/util/__init__.py) | Utilidades compartidas: registro de ejecución y lectura de JSON. |
| [Makefile](../../Makefile) | Objetivos de Compose, dbmate, backups, base de pruebas y OIDC de pruebas (`make db-help`). |
| [README.md](../../README.md) | Presentación, instalación y entradas a documentación. |
| [alembic.ini](../../alembic.ini) | Configuración de Alembic: carpeta `db/alembic`, plantilla de revisiones y logging. La URL la aporta `env.py` desde `Ajustes`. |
| [assets/README.md](../../assets/README.md) | Assets de la aplicación |
| [assets/favicon.ico](../../assets/favicon.ico) | Icono del sitio. |
| [assets/superficie_interior_mm.npz](../../assets/superficie_interior_mm.npz) | Superficie de ejemplo incluida para web y carga explícita legacy. |
| [assets/visor.html](../../assets/visor.html) | Visor Three.js que carga el STL binario desde su `object_url`, cámara e interacción WebGL. |
| [config/almacen.yaml](../../config/almacen.yaml) | Timeouts de conexión y lectura e intentos del cliente S3. |
| [config/cache.yaml](../../config/cache.yaml) | TTL, pausa de reintento y timeout de Redis. |
| [config/persistencia.yaml](../../config/persistencia.yaml) | Conexión PostgreSQL (reintentos, esperas, timeout), cuotas de lotes y límites del historial. |
| [config/sesion.yaml](../../config/sesion.yaml) | Duración de la sesión y vigencia de la cookie del intercambio OIDC. |
| [config/trabajador.yaml](../../config/trabajador.yaml) | Lease, latido, supervisión y conciliación del trabajador. |
| [config/web.yaml](../../config/web.yaml) | Progreso, variantes y tamaños de subida de la app; etiquetas de patrones, ejes y estados. |
| [db/alembic/env.py](../../db/alembic/env.py) | Entorno de Alembic: migra el esquema ortesislab con el rol migrador. |
| [db/alembic/script.py.mako](../../db/alembic/script.py.mako) | Plantilla con la que Alembic crea cada archivo de revisión. |
| [db/alembic/versions/.gitkeep](../../db/alembic/versions/.gitkeep) | Conserva la carpeta de revisiones, vacía en el repositorio. |
| [db/seeds/development.sql](../../db/seeds/development.sql) | Datos idempotentes de desarrollo para `ortesislab_dev`. |
| [db/test/preparar_base.sql](../../db/test/preparar_base.sql) | Preparación de la base `ortesislab_test` antes de migrarla. |
| [docs/Agents/ESTANDAR_DOCUMENTACION.md](ESTANDAR_DOCUMENTACION.md) | Estándar documental |
| [docs/Agents/GUIA_REFLEX.md](GUIA_REFLEX.md) | Reflex Documentation |
| [docs/Agents/INVENTARIO.md](INVENTARIO.md) | Inventario de carpetas y archivos propios (instantánea). |
| [docs/Agents/MANTENIMIENTO.md](MANTENIMIENTO.md) | Mantenimiento automático y revisión de documentación |
| [docs/Agents/README.md](README.md) | Agents |
| [docs/Agents/REGISTRO_CAMBIOS.md](REGISTRO_CAMBIOS.md) | Registro de cambios documentales |
| [docs/Agents/Scripts/GenerarIndices.py](Scripts/GenerarIndices.py) | Regenera los catálogos de hechos de la documentación y comprueba enlaces. |
| [docs/AppBackend/ARQUITECTURA.md](../AppBackend/ARQUITECTURA.md) | Arquitectura interna de AppBackend |
| [docs/AppBackend/CONTRATOS.md](../AppBackend/CONTRATOS.md) | Contratos de AppBackend |
| [docs/AppBackend/DATABASE.md](../AppBackend/DATABASE.md) | DATABASE — PostgreSQL, versiones e historial |
| [docs/AppBackend/MODULOS.md](../AppBackend/MODULOS.md) | Carpetas y archivos de AppBackend |
| [docs/AppBackend/OPERACION_Y_PRUEBAS.md](../AppBackend/OPERACION_Y_PRUEBAS.md) | Operación y pruebas del backend |
| [docs/AppBackend/README.md](../AppBackend/README.md) | AppBackend |
| [docs/AppBackend/SIMBOLOS.md](../AppBackend/SIMBOLOS.md) | Índice de clases, funciones y métodos del backend (instantánea). |
| [docs/AppFrontend/ARQUITECTURA.md](../AppFrontend/ARQUITECTURA.md) | Arquitectura del frontend Reflex |
| [docs/AppFrontend/COMPONENTES_Y_FLUJOS.md](../AppFrontend/COMPONENTES_Y_FLUJOS.md) | Componentes, archivos y flujos de interfaz |
| [docs/AppFrontend/OPERACION_Y_PRUEBAS.md](../AppFrontend/OPERACION_Y_PRUEBAS.md) | Operación y verificación del frontend |
| [docs/AppFrontend/README.md](../AppFrontend/README.md) | AppFrontend |
| [docs/AppFrontend/SIMBOLOS.md](../AppFrontend/SIMBOLOS.md) | Índice de componentes y estado relacionados con el frontend (instantánea). |
| [docs/AppFrontend/VISOR_3D.md](../AppFrontend/VISOR_3D.md) | Visor 3D: código, datos e interacción |
| [docs/Audit/README.md](../Audit/README.md) | Auditorías y resoluciones |
| [docs/Audit/audits/2026-10-13-auditoria-base-codigo.md](../Audit/audits/2026-10-13-auditoria-base-codigo.md) | AUD-2026-10-13-001 — Auditoría de la base de código |
| [docs/Audit/audits/2026-10-13-evidencias.json](../Audit/audits/2026-10-13-evidencias.json) | Archivo auxiliar versionado; revisar su contrato al modificarlo. |
| [docs/Audit/audits/2026-10-13-export-evidence.json](../Audit/audits/2026-10-13-export-evidence.json) | Archivo auxiliar versionado; revisar su contrato al modificarlo. |
| [docs/Audit/audits/2026-10-13-inventario.json](../Audit/audits/2026-10-13-inventario.json) | Archivo auxiliar versionado; revisar su contrato al modificarlo. |
| [docs/Audit/audits/README.md](../Audit/audits/README.md) | Auditorías |
| [docs/Audit/resolves/2026-10-13-firmas-base.json](../Audit/resolves/2026-10-13-firmas-base.json) | Instantánea AST de las 69 firmas públicas de los archivos auditados. |
| [docs/Audit/resolves/2026-10-13-resolve-organizar-pruebas.md](../Audit/resolves/2026-10-13-resolve-organizar-pruebas.md) | RES-2026-10-13-002 — Orden de pruebas y assets de prueba |
| [docs/Audit/resolves/2026-10-13-resolve-persistencia-postgres.md](../Audit/resolves/2026-10-13-resolve-persistencia-postgres.md) | RES-2026-10-13-001 — Persistencia PostgreSQL, bucket S3 y caché Redis |
| [docs/Audit/resolves/README.md](../Audit/resolves/README.md) | Resoluciones |
| [docs/BlenderPlugin/ALGORITMOS.md](../BlenderPlugin/ALGORITMOS.md) | Algoritmos de generación y comprobación |
| [docs/BlenderPlugin/API_Y_DATOS.md](../BlenderPlugin/API_Y_DATOS.md) | API Python, contratos y datos de Blender |
| [docs/BlenderPlugin/ARQUITECTURA.md](../BlenderPlugin/ARQUITECTURA.md) | Arquitectura del complemento |
| [docs/BlenderPlugin/CONFIGURACION_GENERADA.md](../BlenderPlugin/CONFIGURACION_GENERADA.md) | Valores exactos de los cuatro JSON del núcleo, generados desde las fuentes. |
| [docs/BlenderPlugin/LEEME.md](../BlenderPlugin/LEEME.md) | OrtesisLab 1.3 — superficie sin espesor |
| [docs/BlenderPlugin/MODULOS.md](../BlenderPlugin/MODULOS.md) | Mapa completo del paquete Blender y del núcleo |
| [docs/BlenderPlugin/OPERACION_Y_PRUEBAS.md](../BlenderPlugin/OPERACION_Y_PRUEBAS.md) | Operación y pruebas del complemento |
| [docs/BlenderPlugin/PARAMETROS.md](../BlenderPlugin/PARAMETROS.md) | Parámetros: propósito, efecto y restricciones |
| [docs/BlenderPlugin/README.md](../BlenderPlugin/README.md) | BlenderPlugin |
| [docs/BlenderPlugin/SIMBOLOS.md](../BlenderPlugin/SIMBOLOS.md) | Índice de símbolos del paquete Blender y núcleo (instantánea). |
| [docs/README.md](../README.md) | Documentación de OrtesisLab |
| [infra/database/.env.example](../../infra/database/.env.example) | Plantilla de secretos, usuarios y puertos de Compose. |
| [infra/database/.gitattributes](../../infra/database/.gitattributes) | Fuerza LF en scripts, SQL y JSON que se ejecutan en contenedores. |
| [infra/database/.gitignore](../../infra/database/.gitignore) | Excluye `.env` y volcados de backups. |
| [infra/database/backups/.gitkeep](../../infra/database/backups/.gitkeep) | Conserva la carpeta de volcados; su contenido se ignora. |
| [infra/database/compose.yaml](../../infra/database/compose.yaml) | PostgreSQL 17, MinIO, Redis, dbmate, cliente `mc` y OIDC de pruebas. |
| [infra/database/init/01_roles.sh](../../infra/database/init/01_roles.sh) | Crea los roles separados al inicializar el volumen de PostgreSQL. |
| [infra/database/minio/inicializar.sh](../../infra/database/minio/inicializar.sh) | Crea bucket, políticas y cuenta de servicio en MinIO. |
| [infra/database/minio/politica-aplicacion.json](../../infra/database/minio/politica-aplicacion.json) | Permisos S3 de la cuenta de servicio del backend. |
| [infra/database/minio/politica-lectura-stl.json](../../infra/database/minio/politica-lectura-stl.json) | Lectura anónima solo de `usuarios/*/assets/*.stl`. |
| [pyproject.toml](../../pyproject.toml) | Metadata Python, dependencias, build y comando de consola. |
| [reflex.lock/bun.lock](../../reflex.lock/bun.lock) | Resolución reproducible de dependencias JavaScript. |
| [reflex.lock/package.json](../../reflex.lock/package.json) | Dependencias y scripts JavaScript del frontend generado. |
| [rxconfig.py](../../rxconfig.py) | Configuración Reflex, módulo web, plugins y tema. |
| [scripts/EjecutarOrtesisLab.py](../../scripts/EjecutarOrtesisLab.py) | Script para abrir el complemento dentro de Blender. |
| [scripts/EjecutarTrabajador.py](../../scripts/EjecutarTrabajador.py) | Proceso trabajador de OrtesisLab: cola de generación y conciliación. |
| [scripts/EmpaquetarBlender.py](../../scripts/EmpaquetarBlender.py) | Genera el ZIP instalable de Blender, sin Reflex, logs ni la base v5. |
| [scripts/IniciarConsola.py](../../scripts/IniciarConsola.py) | Script del comando de consola del proyecto. |
| [scripts/MigrarSubidas.py](../../scripts/MigrarSubidas.py) | Traslada una sola vez ``uploaded_files/`` al bucket y registra cada objeto. |
| [skills-lock.json](../../skills-lock.json) | Procedencia y huellas de las tres skills Reflex instaladas. |
| [src/generatemodelsapp/__init__.py](../../src/generatemodelsapp/__init__.py) | Marcador de paquete; ver índice de símbolos si contiene funciones. |
| [tests/README.md](../../tests/README.md) | Pruebas |
| [tests/aplicacion_web/__init__.py](../../tests/aplicacion_web/__init__.py) | Pruebas del generador web y del lector de superficies. |
| [tests/aplicacion_web/test_generador_web.py](../../tests/aplicacion_web/test_generador_web.py) | Comprueba el lote y el STL sin abrir Blender ni la superficie real. |
| [tests/assets/Test.stl](../../tests/assets/Test.stl) | Superficie STL de entrada para las pruebas. |
| [tests/assets/resultado_blender.json](../../tests/assets/resultado_blender.json) | Resultado histórico de una ejecución en Blender; no valida la versión actual. |
| [tests/blender/__init__.py](../../tests/blender/__init__.py) | Scripts de integración que ejecuta Blender; unittest no los recoge. |
| [tests/blender/blender_paquete_zip.py](../../tests/blender/blender_paquete_zip.py) | Comprueba el paquete distribuido en aislamiento, sin assets ni Reflex. |
| [tests/blender/blender_superficie_abierta.py](../../tests/blender/blender_superficie_abierta.py) | Ejecutar con Blender --background --factory-startup --python-exit-code 1 --python este_archivo. |
| [tests/geometria/__init__.py](../../tests/geometria/__init__.py) | Pruebas de escala, refinamiento, suavizado de borde y espesor. |
| [tests/geometria/test_escala_malla.py](../../tests/geometria/test_escala_malla.py) | Diagnóstico de unidades de una superficie antes de usar Blender. |
| [tests/geometria/test_refinador_malla.py](../../tests/geometria/test_refinador_malla.py) | Refinamiento de patrones web sin depender de Blender. |
| [tests/geometria/test_suavizado_borde.py](../../tests/geometria/test_suavizado_borde.py) | El contorno exterior pierde los dientes y conserva la forma general. |
| [tests/geometria/test_superficie_abierta.py](../../tests/geometria/test_superficie_abierta.py) | Regresiones del espesor: pared cerrada, canal superior abierto. |
| [tests/nucleo/__init__.py](../../tests/nucleo/__init__.py) | Pruebas del núcleo geométrico: validación, catálogo, volumen y material. |
| [tests/nucleo/test_nucleo.py](../../tests/nucleo/test_nucleo.py) | Comprueba que el núcleo repartido conserva la geometría del script original. |
| [tests/persistencia/__init__.py](../../tests/persistencia/__init__.py) | Pruebas de PostgreSQL, bucket, Redis, lotes, trabajador y permisos. |
| [tests/persistencia/apoyo_persistencia.py](../../tests/persistencia/apoyo_persistencia.py) | Apoyo de pruebas contra la base desechable ``ortesislab_test``. |
| [tests/persistencia/test_almacen_import.py](../../tests/persistencia/test_almacen_import.py) | Import al bucket, caché Redis y migración de subidas locales. |
| [tests/persistencia/test_lotes_trabajador.py](../../tests/persistencia/test_lotes_trabajador.py) | Lotes idempotentes, trabajador con lease, aislamiento y conciliación. |
| [tests/persistencia/test_propiedad_datos.py](../../tests/persistencia/test_propiedad_datos.py) | Propiedad de los datos y permisos de rol sobre PostgreSQL real. |
| [uv.lock](../../uv.lock) | Resoluciones reproducibles de dependencias Python. |
| [web/Ajustes.py](../../web/Ajustes.py) | Configuración de servidor de la persistencia, leída del entorno. |
| [web/ConfiguracionBackend.py](../../web/ConfiguracionBackend.py) | Valores ajustables del backend, leídos de ``config/<area>.yaml`` en la raíz. |
| [web/EstadoApp.py](../../web/EstadoApp.py) | Estado de la página de comparación. |
| [web/EstadoHistorial.py](../../web/EstadoHistorial.py) | Estado de /historial: filtros, cursor y comparación de hasta tres versiones. |
| [web/GeneradorWeb.py](../../web/GeneradorWeb.py) | Genera cascarones para la aplicación web. |
| [web/GenerateModelsApp.py](../../web/GenerateModelsApp.py) | Aplicación Reflex de comparación de ortesis. |
| [web/LectorSuperficie.py](../../web/LectorSuperficie.py) | Lectura de superficies subidas a la aplicación web. |
| [web/PaginaComparacion.py](../../web/PaginaComparacion.py) | Pantalla para previsualizar una ortesis o un lote de variantes. |
| [web/PaginaHistorial.py](../../web/PaginaHistorial.py) | Pantalla /historial: generaciones del usuario, comparación y restauración. |
| [web/Sesion.py](../../web/Sesion.py) | Barra de sesión común a la comparación y al historial. |
| [web/__init__.py](../../web/__init__.py) | Aplicación Reflex. |
| [web/cache/CacheRedis.py](../../web/cache/CacheRedis.py) | Caché compartida de superficies preparadas. |
| [web/cache/__init__.py](../../web/cache/__init__.py) | Marcador de paquete. |
| [web/enums/Archivos.py](../../web/enums/Archivos.py) | Tipos y estados de los objetos del bucket registrados en ``file_assets``. |
| [web/enums/Historial.py](../../web/enums/Historial.py) | Tipos de evento de ``history_events``. |
| [web/enums/Imports.py](../../web/enums/Imports.py) | Origen, estado y formato de una superficie importada (``imports``). |
| [web/enums/Lotes.py](../../web/enums/Lotes.py) | Backend de versión, modos de lote y estados de lotes, ítems e intentos. |
| [web/enums/Resultados.py](../../web/enums/Resultados.py) | Validación y alcance de ``generation_results`` y formato, unidad y estado de ``exports``. |
| [web/enums/Usuarios.py](../../web/enums/Usuarios.py) | Estados de una cuenta de ``app_users``. |
| [web/enums/__init__.py](../../web/enums/__init__.py) | Valores cerrados del dominio. Deben coincidir con los ``CHECK`` del esquema. |
| [web/jobs/ConciliadorArchivos.py](../../web/jobs/ConciliadorArchivos.py) | Conciliación entre filas de ``file_assets`` y objetos del bucket. |
| [web/jobs/TrabajadorGeneracion.py](../../web/jobs/TrabajadorGeneracion.py) | Trabajador de generación: un ítem a la vez, con lease y latido. |
| [web/jobs/__init__.py](../../web/jobs/__init__.py) | Marcador de paquete. |
| [web/persistence/ConexionPostgres.py](../../web/persistence/ConexionPostgres.py) | Pool síncrono de Psycopg por proceso. |
| [web/persistence/Contratos.py](../../web/persistence/Contratos.py) | DTO y errores de la persistencia. No son entidades ORM. |
| [web/persistence/Modelos.py](../../web/persistence/Modelos.py) | Modelos declarativos de SQLAlchemy del esquema ``ortesislab``. |
| [web/persistence/__init__.py](../../web/persistence/__init__.py) | Acceso a PostgreSQL con SQL parametrizado, sin ORM. |
| [web/persistence/repositorios/Consultas.py](../../web/persistence/repositorios/Consultas.py) | Tablas y fragmentos de consulta que comparten varios repositorios. |
| [web/persistence/repositorios/RepositorioAssets.py](../../web/persistence/repositorios/RepositorioAssets.py) | Filas de ``file_assets``: el contenido vive en el bucket. |
| [web/persistence/repositorios/RepositorioBase.py](../../web/persistence/repositorios/RepositorioBase.py) | Clase padre de los repositorios: lectura de filas y conversión a DTO. |
| [web/persistence/repositorios/RepositorioHistorial.py](../../web/persistence/repositorios/RepositorioHistorial.py) | Eventos de historial y listado de ejecuciones por versión. |
| [web/persistence/repositorios/RepositorioImports.py](../../web/persistence/repositorios/RepositorioImports.py) | Importaciones de superficies: original recibido y NPZ normalizado. |
| [web/persistence/repositorios/RepositorioLotes.py](../../web/persistence/repositorios/RepositorioLotes.py) | Lotes, ítems y cola del trabajador: admisión, reserva, lease y cierre. |
| [web/persistence/repositorios/RepositorioPreferencias.py](../../web/persistence/repositorios/RepositorioPreferencias.py) | Preferencias por usuario con control optimista de revisión. |
| [web/persistence/repositorios/RepositorioProyectos.py](../../web/persistence/repositorios/RepositorioProyectos.py) | Proyectos del usuario; cada cuenta tiene uno predeterminado. |
| [web/persistence/repositorios/RepositorioResultados.py](../../web/persistence/repositorios/RepositorioResultados.py) | Resultados geométricos, intentos de una versión y exports STL. |
| [web/persistence/repositorios/RepositorioUsuarios.py](../../web/persistence/repositorios/RepositorioUsuarios.py) | Cuentas creadas desde OIDC y sus sesiones de servidor. |
| [web/persistence/repositorios/RepositorioVersiones.py](../../web/persistence/repositorios/RepositorioVersiones.py) | Versiones inmutables numeradas por proyecto. |
| [web/persistence/repositorios/__init__.py](../../web/persistence/repositorios/__init__.py) | Repositorios SQLAlchemy, uno por archivo. Reciben una ``Session`` ya abierta y no hacen commit. |
| [web/services/AutenticacionOidc.py](../../web/services/AutenticacionOidc.py) | Rutas OIDC del backend: /auth/login, /auth/callback y /auth/logout. |
| [web/services/ContextoUsuario.py](../../web/services/ContextoUsuario.py) | Principal autenticado de cada operación. |
| [web/services/GeneradorGeometrico.py](../../web/services/GeneradorGeometrico.py) | Construcción numérica de una versión: métricas, STL y JSON de parámetros. |
| [web/services/ServicioHistorial.py](../../web/services/ServicioHistorial.py) | Historial por usuario: listado paginado, detalle, restauración y reintento. |
| [web/services/ServicioImports.py](../../web/services/ServicioImports.py) | Importación de superficies: original y NPZ normalizado en el bucket. |
| [web/services/ServicioLotes.py](../../web/services/ServicioLotes.py) | Admisión de lotes, progreso y transiciones del trabajador. |
| [web/services/ServicioPreferencias.py](../../web/services/ServicioPreferencias.py) | Preferencias por usuario con control optimista de revisión. |
| [web/services/ServicioVersiones.py](../../web/services/ServicioVersiones.py) | Versiones inmutables: snapshot de parámetros, material y escala. |
| [web/services/__init__.py](../../web/services/__init__.py) | Marcador de paquete. |
| [web/storage/AlmacenamientoPrivado.py](../../web/storage/AlmacenamientoPrivado.py) | Contrato del almacén de bytes y claves de objeto. |
| [web/storage/StorageS3.py](../../web/storage/StorageS3.py) | Almacén de bytes en un bucket S3 (MinIO en desarrollo). |
| [web/storage/__init__.py](../../web/storage/__init__.py) | Marcador de paquete. |

## Carpetas y artefactos locales

| Carpeta | Propósito y mantenimiento |
|---|---|
| `web/` | Aplicación Reflex: entrada, páginas, estado, lectores y generador web |
| `db/` | Migraciones dbmate, volcado del esquema, seed de desarrollo y preparación de pruebas |
| `infra/database/` | Compose, roles, políticas de MinIO y backups locales |
| `web/persistence/`, `web/services/`, `web/storage/`, `web/cache/`, `web/jobs/` | Persistencia, servicios, bucket, caché Redis y trabajador |
| `GenerateModelsApp/` | Núcleo común y adaptadores Blender; subcarpetas constants, config y util |
| `src/generatemodelsapp/` | Entrada del comando de saludo empaquetado por uv |
| `scripts/` | Lanzadores, empaquetado, trabajador y migración de subidas |
| `tests/` | Pruebas Python, integraciones Blender, fixture y evidencia histórica |
| `assets/` | Visor, favicon y superficie incluida; external/ ignorado contiene assets externos generados |
| `docs/` | README de carpetas, AppBackend, AppFrontend, BlenderPlugin, Agents y registros de audit |
| `docs/Agents/` | Mantenimiento con agentes, estándar, inventario, referencia Reflex y cambios |
| `.agents/skills/` | Instrucciones Reflex versionadas; no lógica de producto |
| `.codegraph/` | Índice local de navegación; no reindexar sin decisión del usuario |
| `.vscode/` | Preferencias de editor |
| `reflex.lock/` | Dependencias frontend reproducibles |
| `.venv/` | Intérprete/dependencias Python instaladas; regenerar con uv |
| `__pycache__/` | Bytecode Python regenerable; nunca fuente |
| `.states/` | Artefactos de estado Reflex; no historial de dominio |
| `uploaded_files/` | Subidas de la arquitectura anterior; `scripts/MigrarSubidas.py` las traslada al bucket y las borra |
| `GenerateModelsApp/logs/` | Logs de ejecución del dominio |
| `dist/` | Copias/ensayos de distribución; incluye ZIP anteriores y extracciones temporales de pruebas; no fuente vigente |

## `.web/`: árbol generado

No se inventarían los miles de archivos transitivos de node_modules ni builds: pertenecen al compilador/dependencias, no a código desarrollado en este repositorio. Los directorios cambian con la versión instalada.

| Elemento | Función |
|---|---|
| `app/`, `app_components/`, `components/` | Rutas React Router y componentes compilados |
| `backend/`, `utils/` | Integración generada de eventos/estado/utilidades cliente |
| `public/`, `styles/` | Assets publicados y estilos compilados |
| `build/`, `.react-router/` | Salidas de build y metadata de rutas |
| `node_modules/` | Dependencias transitivas instaladas |
| `package.json`, `bun.lock`, `bunfig.toml`, `.npmrc` | Resolución y configuración del gestor JS |
| `vite.config.js`, `react-router.config.js`, `jsconfig.json` | Configuración del frontend generado |
| `tailwind.config.js`, `postcss.config.js` | Compilación CSS |
| `env.json`, `reflex.json` | Parámetros generados de entorno/framework; no publicar secretos |
| `compress-static.js`, `vite-plugin-safari-cachebust.js` | Utilidades de build generadas |
| `.memo-manifest.json`, `reflex.install_frontend_packages.cached`, `.reflex_dev_backend_started` | Cachés y marcadores del compilador/proceso |
| `.gitignore` | Exclusiones de la compilación |
