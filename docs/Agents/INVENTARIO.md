# Inventario completo del repositorio

> Generado por `scripts/VerificarDocumentacion.py --actualizar`. Incluye archivos versionados y nuevos no ignorados; excluye Git, dependencias y salidas locales ignoradas.

Los catálogos de [backend](../AppBackend/MODULOS.md), [frontend](../AppFrontend/COMPONENTES_Y_FLUJOS.md) y [plugin](../BlenderPlugin/MODULOS.md) explican las colaboraciones. Aquí se asigna propósito a cada archivo propio; no se atribuye lógica de aplicación a librerías de terceros.

| Archivo | Propósito |
|---|---|
| [.agents/skills/reflex-docs/SKILL.md](../../.agents/skills/reflex-docs/SKILL.md) | Skill local Reflex: instrucciones y referencias para agentes. |
| [.agents/skills/reflex-process-management/SKILL.md](../../.agents/skills/reflex-process-management/SKILL.md) | Skill local Reflex: instrucciones y referencias para agentes. |
| [.agents/skills/setup-python-env/SKILL.md](../../.agents/skills/setup-python-env/SKILL.md) | Skill local Reflex: instrucciones y referencias para agentes. |
| [.codegraph/.gitignore](../../.codegraph/.gitignore) | Excluye el índice local de CodeGraph del versionado. |
| [.gitignore](../../.gitignore) | Excluye entornos, compilación, estados, subidas y logs generados. |
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
| [README.md](../../README.md) | Presentación, instalación y entradas a documentación. |
| [assets/favicon.ico](../../assets/favicon.ico) | Icono del sitio. |
| [assets/superficie_interior_mm.npz](../../assets/superficie_interior_mm.npz) | Superficie de ejemplo incluida para web y carga explícita legacy. |
| [assets/visor.html](../../assets/visor.html) | Visor Three.js de STL binario, cámara e interacción WebGL. |
| [docs/Agents/ESTANDAR_DOCUMENTACION.md](ESTANDAR_DOCUMENTACION.md) | Estándar documental |
| [docs/Agents/GUIA_REFLEX.md](GUIA_REFLEX.md) | Reflex Documentation |
| [docs/Agents/INVENTARIO.md](INVENTARIO.md) | Inventario generado de carpetas y archivos propios. |
| [docs/Agents/MANTENIMIENTO.md](MANTENIMIENTO.md) | Mantenimiento automático y revisión de documentación |
| [docs/Agents/README.md](README.md) | Agents |
| [docs/Agents/REGISTRO_CAMBIOS.md](REGISTRO_CAMBIOS.md) | Registro de cambios documentales |
| [docs/Agents/linea_base_documental.json](linea_base_documental.json) | Huellas SHA-256 de fuentes revisadas para detectar deriva documental. |
| [docs/AppBackend/ARQUITECTURA.md](../AppBackend/ARQUITECTURA.md) | Arquitectura interna de AppBackend |
| [docs/AppBackend/CONTRATOS.md](../AppBackend/CONTRATOS.md) | Contratos de AppBackend |
| [docs/AppBackend/DATABASE.md](../AppBackend/DATABASE.md) | DATABASE — Propuesta de PostgreSQL, versiones e historial |
| [docs/AppBackend/MODULOS.md](../AppBackend/MODULOS.md) | Carpetas y archivos de AppBackend |
| [docs/AppBackend/OPERACION_Y_PRUEBAS.md](../AppBackend/OPERACION_Y_PRUEBAS.md) | Operación y pruebas del backend |
| [docs/AppBackend/README.md](../AppBackend/README.md) | AppBackend |
| [docs/AppBackend/SIMBOLOS.md](../AppBackend/SIMBOLOS.md) | Índice generado de todas las clases, funciones y métodos del backend. |
| [docs/AppFrontend/ARQUITECTURA.md](../AppFrontend/ARQUITECTURA.md) | Arquitectura del frontend Reflex |
| [docs/AppFrontend/COMPONENTES_Y_FLUJOS.md](../AppFrontend/COMPONENTES_Y_FLUJOS.md) | Componentes, archivos y flujos de interfaz |
| [docs/AppFrontend/OPERACION_Y_PRUEBAS.md](../AppFrontend/OPERACION_Y_PRUEBAS.md) | Operación y verificación del frontend |
| [docs/AppFrontend/README.md](../AppFrontend/README.md) | AppFrontend |
| [docs/AppFrontend/SIMBOLOS.md](../AppFrontend/SIMBOLOS.md) | Índice generado de componentes y estado relacionados con el frontend. |
| [docs/AppFrontend/VISOR_3D.md](../AppFrontend/VISOR_3D.md) | Visor 3D: código, datos e interacción |
| [docs/Audit/README.md](../Audit/README.md) | Auditorías y resoluciones |
| [docs/Audit/audits/2026-10-13-auditoria-base-codigo.md](../Audit/audits/2026-10-13-auditoria-base-codigo.md) | AUD-2026-10-13-001 — Auditoría de la base de código |
| [docs/Audit/audits/2026-10-13-evidencias.json](../Audit/audits/2026-10-13-evidencias.json) | Archivo auxiliar versionado; revisar su contrato al modificarlo. |
| [docs/Audit/audits/2026-10-13-export-evidence.json](../Audit/audits/2026-10-13-export-evidence.json) | Archivo auxiliar versionado; revisar su contrato al modificarlo. |
| [docs/Audit/audits/2026-10-13-inventario.json](../Audit/audits/2026-10-13-inventario.json) | Archivo auxiliar versionado; revisar su contrato al modificarlo. |
| [docs/Audit/audits/README.md](../Audit/audits/README.md) | Auditorías |
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
| [docs/BlenderPlugin/SIMBOLOS.md](../BlenderPlugin/SIMBOLOS.md) | Índice generado de todos los símbolos del paquete Blender y núcleo. |
| [docs/README.md](../README.md) | Documentación de OrtesisLab |
| [pyproject.toml](../../pyproject.toml) | Metadata Python, dependencias, build y comando de consola. |
| [reflex.lock/bun.lock](../../reflex.lock/bun.lock) | Resolución reproducible de dependencias JavaScript. |
| [reflex.lock/package.json](../../reflex.lock/package.json) | Dependencias y scripts JavaScript del frontend generado. |
| [rxconfig.py](../../rxconfig.py) | Configuración Reflex, módulo web, plugins y tema. |
| [scripts/EjecutarOrtesisLab.py](../../scripts/EjecutarOrtesisLab.py) | Script para abrir el complemento dentro de Blender. |
| [scripts/EmpaquetarBlender.py](../../scripts/EmpaquetarBlender.py) | Genera el ZIP instalable de Blender, sin Reflex, logs ni la base v5. |
| [scripts/IniciarConsola.py](../../scripts/IniciarConsola.py) | Script del comando de consola del proyecto. |
| [scripts/VerificarDocumentacion.py](../../scripts/VerificarDocumentacion.py) | Genera índices documentales y detecta deriva de fuentes sin importar Reflex/Blender. |
| [skills-lock.json](../../skills-lock.json) | Procedencia y huellas de las tres skills Reflex instaladas. |
| [src/generatemodelsapp/__init__.py](../../src/generatemodelsapp/__init__.py) | Marcador de paquete; ver índice de símbolos si contiene funciones. |
| [tests/Test.stl](../../tests/Test.stl) | Fixture de superficie STL para pruebas de lectura y escala. |
| [tests/blender_ejecucion.log](../../tests/blender_ejecucion.log) | Log histórico versionado; no es evidencia de pruebas ejecutadas hoy. |
| [tests/blender_paquete_zip.py](../../tests/blender_paquete_zip.py) | Integración de paquete ZIP aislado, registro, generación y exportación. |
| [tests/blender_superficie_abierta.py](../../tests/blender_superficie_abierta.py) | Integración Blender de cinco patrones, canales abiertos y conservación de base. |
| [tests/nucleo_ejecucion.log](../../tests/nucleo_ejecucion.log) | Log histórico versionado; no es evidencia de pruebas ejecutadas hoy. |
| [tests/resultado_blender.json](../../tests/resultado_blender.json) | Resultado histórico Blender; no valida una ejecución nueva. |
| [tests/test_escala_malla.py](../../tests/test_escala_malla.py) | Pruebas de heurística decimal, alcance de paso y presupuesto. |
| [tests/test_generador_web.py](../../tests/test_generador_web.py) | Pruebas de combinaciones, STL, lectores y autoescala web. |
| [tests/test_nucleo.py](../../tests/test_nucleo.py) | Equivalencia geométrica, validación, catálogo, volumen y material. |
| [tests/test_refinador_malla.py](../../tests/test_refinador_malla.py) | Pruebas de subdivisión y recorte sobre superficie refinada. |
| [tests/test_suavizado_borde.py](../../tests/test_suavizado_borde.py) | Pruebas de filtrado del contorno y conservación del interior. |
| [tests/test_superficie_abierta.py](../../tests/test_superficie_abierta.py) | Pruebas de pared sin tapas e integridad de superficie base. |
| [tests/zip_ejecucion.log](../../tests/zip_ejecucion.log) | Log histórico versionado; no es evidencia de pruebas ejecutadas hoy. |
| [uv.lock](../../uv.lock) | Resoluciones reproducibles de dependencias Python. |
| [web/EstadoApp.py](../../web/EstadoApp.py) | Estado de la página de comparación. |
| [web/GeneradorWeb.py](../../web/GeneradorWeb.py) | Genera cascarones para la aplicación web. |
| [web/GenerateModelsApp.py](../../web/GenerateModelsApp.py) | Aplicación Reflex de comparación de ortesis. |
| [web/LectorSuperficie.py](../../web/LectorSuperficie.py) | Lectura de superficies subidas a la aplicación web. |
| [web/PaginaComparacion.py](../../web/PaginaComparacion.py) | Pantalla para previsualizar una ortesis o un lote de variantes. |
| [web/__init__.py](../../web/__init__.py) | Aplicación Reflex. |

## Carpetas y artefactos locales

| Carpeta | Propósito y mantenimiento |
|---|---|
| `web/` | Aplicación Reflex: entrada, componentes, estado, servicio y lectores |
| `GenerateModelsApp/` | Núcleo común y adaptadores Blender; subcarpetas constants, config y util |
| `src/generatemodelsapp/` | Entrada del comando de saludo empaquetado por uv |
| `scripts/` | Lanzadores, empaquetado y verificación documental |
| `tests/` | Pruebas Python, integraciones Blender, fixture y evidencia histórica |
| `assets/` | Visor, favicon y superficie incluida; external/ ignorado contiene assets externos generados |
| `docs/` | README de carpetas, AppBackend, AppFrontend, BlenderPlugin, Agents y registros de audit |
| `docs/Agents/` | Mantenimiento con agentes, estándar, inventario, referencia Reflex, cambios y línea base |
| `.agents/skills/` | Instrucciones Reflex versionadas; no lógica de producto |
| `.codegraph/` | Índice local de navegación; no reindexar sin decisión del usuario |
| `.vscode/` | Preferencias de editor |
| `reflex.lock/` | Dependencias frontend reproducibles |
| `.venv/` | Intérprete/dependencias Python instaladas; regenerar con uv |
| `__pycache__/` | Bytecode Python regenerable; nunca fuente |
| `.states/` | Artefactos de estado Reflex; no historial de dominio |
| `uploaded_files/` | NPZ/STL de usuario y generación; sin retención automática implementada |
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
