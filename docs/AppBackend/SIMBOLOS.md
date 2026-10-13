# Índice de símbolos: AppBackend

> Generado por `python docs/Agents/Scripts/GenerarIndices.py`. No editar a mano.

Incluye funciones anidadas y métodos privados para localizar todas las piezas. Las líneas son una ayuda de navegación; el nombre del símbolo es la referencia estable.

## `rxconfig.py`

Configuración Reflex, módulo web, plugins y tema.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `scripts/EjecutarOrtesisLab.py`

Script para abrir el complemento dentro de Blender.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `scripts/EjecutarTrabajador.py`

Proceso trabajador de OrtesisLab: cola de generación y conciliación.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `main` | Función/método | [27](../../scripts/EjecutarTrabajador.py#L27) | Sin docstring; consultar el catálogo de módulos y el código. |

## `scripts/EmpaquetarBlender.py`

Genera el ZIP instalable de Blender, sin Reflex, logs ni la base v5.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `empaquetar` | Función/método | [9](../../scripts/EmpaquetarBlender.py#L9) | Sin docstring; consultar el catálogo de módulos y el código. |

## `scripts/IniciarConsola.py`

Script del comando de consola del proyecto.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `IniciarConsola` | Clase | [8](../../scripts/IniciarConsola.py#L8) | Punto de entrada del saludo. El paquete no depende de este archivo. |
| `IniciarConsola.Ejecutar` | Función/método | [12](../../scripts/IniciarConsola.py#L12) | Sin docstring; consultar el catálogo de módulos y el código. |

## `scripts/MigrarSubidas.py`

Traslada una sola vez ``uploaded_files/`` al bucket y registra cada objeto.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Propietario` | Función/método | [45](../../scripts/MigrarSubidas.py#L45) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Propietario.asegurar` | Función/método | [46](../../scripts/MigrarSubidas.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Migrar` | Función/método | [56](../../scripts/MigrarSubidas.py#L56) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Migrar.registrar` | Función/método | [85](../../scripts/MigrarSubidas.py#L85) | Sin docstring; consultar el catálogo de módulos y el código. |
| `main` | Función/método | [103](../../scripts/MigrarSubidas.py#L103) | Sin docstring; consultar el catálogo de módulos y el código. |

## `src/generatemodelsapp/__init__.py`

Marcador de paquete; ver índice de símbolos si contiene funciones.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `main` | Función/método | [1](../../src/generatemodelsapp/__init__.py#L1) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/__init__.py`

Aplicación Reflex.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `web/Ajustes.py`

Configuración de servidor de la persistencia, leída del entorno.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `VariableFaltante` | Clase | [18](../../web/Ajustes.py#L18) | Sin docstring; consultar el catálogo de módulos y el código. |
| `VariableFaltante.__init__` | Función/método | [19](../../web/Ajustes.py#L19) | Sin docstring; consultar el catálogo de módulos y el código. |
| `VariableInvalida` | Clase | [24](../../web/Ajustes.py#L24) | Sin docstring; consultar el catálogo de módulos y el código. |
| `VariableInvalida.__init__` | Función/método | [25](../../web/Ajustes.py#L25) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Variable` | Clase | [30](../../web/Ajustes.py#L30) | Una clave del entorno; sin ``defecto`` es obligatoria y no admite vacío. |
| `Variable.__init__` | Función/método | [33](../../web/Ajustes.py#L33) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Variable.__get__` | Función/método | [38](../../web/Ajustes.py#L38) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Ajustes` | Clase | [51](../../web/Ajustes.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Ajustes.__init__` | Función/método | [79](../../web/Ajustes.py#L79) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Ajustes.cookie_secure` | Función/método | [83](../../web/Ajustes.py#L83) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Ajustes.Faltante` | Función/método | [86](../../web/Ajustes.py#L86) | Mensaje de la primera variable sin definir entre ``atributos``; vacío si están todas. |
| `Ajustes.Cargar` | Función/método | [97](../../web/Ajustes.py#L97) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Ajustes._LeerArchivo` | Función/método | [101](../../web/Ajustes.py#L101) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/cache/__init__.py`

Marcador de paquete.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `web/cache/CacheRedis.py`

Caché compartida de superficies preparadas.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `CacheRedis` | Clase | [27](../../web/cache/CacheRedis.py#L27) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis.ClaveCruda` | Función/método | [32](../../web/cache/CacheRedis.py#L32) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis.ClaveRefinada` | Función/método | [36](../../web/cache/CacheRedis.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis.ClaveDiagnostico` | Función/método | [40](../../web/cache/CacheRedis.py#L40) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis.Usar` | Función/método | [46](../../web/cache/CacheRedis.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis._Cliente` | Función/método | [51](../../web/cache/CacheRedis.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis._Fallo` | Función/método | [63](../../web/cache/CacheRedis.py#L63) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis.LeerTupla` | Función/método | [69](../../web/cache/CacheRedis.py#L69) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis.GuardarTupla` | Función/método | [87](../../web/cache/CacheRedis.py#L87) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis.LeerDiagnostico` | Función/método | [99](../../web/cache/CacheRedis.py#L99) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CacheRedis.GuardarDiagnostico` | Función/método | [111](../../web/cache/CacheRedis.py#L111) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/ConfiguracionBackend.py`

Valores ajustables del backend, leídos de ``config/<area>.yaml`` en la raíz.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ConfiguracionBackend` | Clase | [17](../../web/ConfiguracionBackend.py#L17) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConfiguracionBackend.Cargar` | Función/método | [20](../../web/ConfiguracionBackend.py#L20) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/enums/__init__.py`

Valores cerrados del dominio. Deben coincidir con los ``CHECK`` del esquema.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `web/enums/Archivos.py`

Tipos y estados de los objetos del bucket registrados en ``file_assets``.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `TipoAsset` | Clase | [6](../../web/enums/Archivos.py#L6) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoAsset` | Clase | [13](../../web/enums/Archivos.py#L13) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ExtensionSuperficie` | Clase | [22](../../web/enums/Archivos.py#L22) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/enums/Historial.py`

Tipos de evento de ``history_events``.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `TipoEvento` | Clase | [6](../../web/enums/Historial.py#L6) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/enums/Imports.py`

Origen, estado y formato de una superficie importada (``imports``).

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `OrigenImport` | Clase | [6](../../web/enums/Imports.py#L6) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoImport` | Clase | [11](../../web/enums/Imports.py#L11) | Sin docstring; consultar el catálogo de módulos y el código. |
| `FormatoImport` | Clase | [18](../../web/enums/Imports.py#L18) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/enums/Lotes.py`

Backend de versión, modos de lote y estados de lotes, ítems e intentos.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `BackendGeneracion` | Clase | [6](../../web/enums/Lotes.py#L6) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ModoLote` | Clase | [10](../../web/enums/Lotes.py#L10) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoLote` | Clase | [16](../../web/enums/Lotes.py#L16) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoItem` | Clase | [25](../../web/enums/Lotes.py#L25) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoIntento` | Clase | [33](../../web/enums/Lotes.py#L33) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/enums/Resultados.py`

Validación y alcance de ``generation_results`` y formato, unidad y estado de ``exports``.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `EstadoValidacion` | Clase | [6](../../web/enums/Resultados.py#L6) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AlcanceGeometria` | Clase | [12](../../web/enums/Resultados.py#L12) | Sin docstring; consultar el catálogo de módulos y el código. |
| `FormatoExport` | Clase | [16](../../web/enums/Resultados.py#L16) | Sin docstring; consultar el catálogo de módulos y el código. |
| `UnidadExport` | Clase | [21](../../web/enums/Resultados.py#L21) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoExport` | Clase | [25](../../web/enums/Resultados.py#L25) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/enums/Usuarios.py`

Estados de una cuenta de ``app_users``.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `EstadoUsuario` | Clase | [6](../../web/enums/Usuarios.py#L6) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/EstadoApp.py`

Estado de la página de comparación.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `EstadoApp` | Clase | [44](../../web/EstadoApp.py#L44) | Parámetros del complemento, lote en curso y fichas ya generadas. |
| `EstadoApp.set_pattern` | Función/método | [105](../../web/EstadoApp.py#L105) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_cell_mm` | Función/método | [109](../../web/EstadoApp.py#L109) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_rib_width_mm` | Función/método | [113](../../web/EstadoApp.py#L113) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_rib_height_mm` | Función/método | [117](../../web/EstadoApp.py#L117) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_liner` | Función/método | [121](../../web/EstadoApp.py#L121) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_skin_mm` | Función/método | [125](../../web/EstadoApp.py#L125) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_solid_mm` | Función/método | [129](../../web/EstadoApp.py#L129) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_border_mm` | Función/método | [133](../../web/EstadoApp.py#L133) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_rounding_mm` | Función/método | [137](../../web/EstadoApp.py#L137) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_angle_deg` | Función/método | [141](../../web/EstadoApp.py#L141) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_seed` | Función/método | [145](../../web/EstadoApp.py#L145) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_reinforce_y_mm` | Función/método | [149](../../web/EstadoApp.py#L149) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_reinforce_width_mm` | Función/método | [153](../../web/EstadoApp.py#L153) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_flip_normals` | Función/método | [157](../../web/EstadoApp.py#L157) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_surface_step_mm` | Función/método | [161](../../web/EstadoApp.py#L161) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_autoescalar_superficie` | Función/método | [165](../../web/EstadoApp.py#L165) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_usar_voronoi` | Función/método | [185](../../web/EstadoApp.py#L185) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_usar_hex` | Función/método | [189](../../web/EstadoApp.py#L189) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_usar_diamond` | Función/método | [193](../../web/EstadoApp.py#L193) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_usar_square` | Función/método | [197](../../web/EstadoApp.py#L197) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_usar_solid` | Función/método | [201](../../web/EstadoApp.py#L201) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_eje` | Función/método | [205](../../web/EstadoApp.py#L205) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_desde` | Función/método | [209](../../web/EstadoApp.py#L209) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_hasta` | Función/método | [213](../../web/EstadoApp.py#L213) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_paso` | Función/método | [217](../../web/EstadoApp.py#L217) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.set_ambos_revestimientos` | Función/método | [221](../../web/EstadoApp.py#L221) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.CargarSuperficie` | Función/método | [225](../../web/EstadoApp.py#L225) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.UsarSuperficieIncluida` | Función/método | [275](../../web/EstadoApp.py#L275) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.CargarPredeterminados` | Función/método | [287](../../web/EstadoApp.py#L287) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.Previsualizar` | Función/método | [336](../../web/EstadoApp.py#L336) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.PedirLote` | Función/método | [342](../../web/EstadoApp.py#L342) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.Generar` | Función/método | [348](../../web/EstadoApp.py#L348) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.SeguirLote` | Función/método | [422](../../web/EstadoApp.py#L422) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.CancelarLote` | Función/método | [442](../../web/EstadoApp.py#L442) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.Ver` | Función/método | [454](../../web/EstadoApp.py#L454) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.Comparar` | Función/método | [461](../../web/EstadoApp.py#L461) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.Descargar` | Función/método | [476](../../web/EstadoApp.py#L476) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.aviso_escala` | Función/método | [496](../../web/EstadoApp.py#L496) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.espesor_total` | Función/método | [521](../../web/EstadoApp.py#L521) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp.porcentaje` | Función/método | [530](../../web/EstadoApp.py#L530) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp._Usuario` | Función/método | [535](../../web/EstadoApp.py#L535) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp._Seguir` | Función/método | [550](../../web/EstadoApp.py#L550) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp._Publicar` | Función/método | [568](../../web/EstadoApp.py#L568) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp._OlvidarTrabajo` | Función/método | [591](../../web/EstadoApp.py#L591) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp._Mostrar` | Función/método | [603](../../web/EstadoApp.py#L603) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp._Variantes` | Función/método | [611](../../web/EstadoApp.py#L611) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp._Opciones` | Función/método | [641](../../web/EstadoApp.py#L641) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoApp._Numero` | Función/método | [666](../../web/EstadoApp.py#L666) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/EstadoHistorial.py`

Estado de /historial: filtros, cursor y comparación de hasta tres versiones.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `EstadoHistorial` | Clase | [35](../../web/EstadoHistorial.py#L35) | Listado paginado del trabajo del usuario y comparación de versiones. |
| `EstadoHistorial.set_filtro_patron` | Función/método | [55](../../web/EstadoHistorial.py#L55) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.set_filtro_estado` | Función/método | [59](../../web/EstadoHistorial.py#L59) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.set_filtro_desde` | Función/método | [63](../../web/EstadoHistorial.py#L63) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.set_filtro_hasta` | Función/método | [67](../../web/EstadoHistorial.py#L67) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.Cargar` | Función/método | [71](../../web/EstadoHistorial.py#L71) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.Siguiente` | Función/método | [79](../../web/EstadoHistorial.py#L79) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.Anterior` | Función/método | [87](../../web/EstadoHistorial.py#L87) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.Seleccionar` | Función/método | [95](../../web/EstadoHistorial.py#L95) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.Restaurar` | Función/método | [107](../../web/EstadoHistorial.py#L107) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.Reintentar` | Función/método | [119](../../web/EstadoHistorial.py#L119) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial.Descargar` | Función/método | [131](../../web/EstadoHistorial.py#L131) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial._Usuario` | Función/método | [145](../../web/EstadoHistorial.py#L145) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial._Leer` | Función/método | [164](../../web/EstadoHistorial.py#L164) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial._Comparar` | Función/método | [192](../../web/EstadoHistorial.py#L192) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial._Filtros` | Función/método | [209](../../web/EstadoHistorial.py#L209) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial._Fecha` | Función/método | [218](../../web/EstadoHistorial.py#L218) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial._Fila` | Función/método | [227](../../web/EstadoHistorial.py#L227) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EstadoHistorial._Tarjeta` | Función/método | [251](../../web/EstadoHistorial.py#L251) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/GeneradorWeb.py`

Genera cascarones para la aplicación web.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `_HuellaPlantilla` | Función/método | [45](../../web/GeneradorWeb.py#L45) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb` | Clase | [51](../../web/GeneradorWeb.py#L51) | Prepara la superficie y traduce resultados persistidos a fichas de la página. |
| `GeneradorWeb._Origen` | Función/método | [55](../../web/GeneradorWeb.py#L55) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Cruda` | Función/método | [69](../../web/GeneradorWeb.py#L69) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.EjeMayor` | Función/método | [81](../../web/GeneradorWeb.py#L81) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Superficie` | Función/método | [88](../../web/GeneradorWeb.py#L88) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb._SuperficieConDiagnostico` | Función/método | [92](../../web/GeneradorWeb.py#L92) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.SuperficieRefinada` | Función/método | [108](../../web/GeneradorWeb.py#L108) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb._SuperficieRefinadaConDiagnostico` | Función/método | [112](../../web/GeneradorWeb.py#L112) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb._SuperficieRefinadaConDiagnostico.refinar` | Función/método | [128](../../web/GeneradorWeb.py#L128) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.GuardarSuperficie` | Función/método | [145](../../web/GeneradorWeb.py#L145) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Crear` | Función/método | [155](../../web/GeneradorWeb.py#L155) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb._FichaDeItem` | Función/método | [178](../../web/GeneradorWeb.py#L178) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.FichaError` | Función/método | [207](../../web/GeneradorWeb.py#L207) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Ficha` | Función/método | [215](../../web/GeneradorWeb.py#L215) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Detalle` | Función/método | [238](../../web/GeneradorWeb.py#L238) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Combinaciones` | Función/método | [270](../../web/GeneradorWeb.py#L270) | Entrada: patrones, rango y paso. Proceso: acota el barrido antes de |
| `GeneradorWeb.Numero` | Función/método | [345](../../web/GeneradorWeb.py#L345) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Stl` | Función/método | [351](../../web/GeneradorWeb.py#L351) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Triangulos` | Función/método | [370](../../web/GeneradorWeb.py#L370) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Escribir` | Función/método | [382](../../web/GeneradorWeb.py#L382) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Leer` | Función/método | [393](../../web/GeneradorWeb.py#L393) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.Ruta` | Función/método | [400](../../web/GeneradorWeb.py#L400) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorWeb.RutaSuperficie` | Función/método | [411](../../web/GeneradorWeb.py#L411) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/GenerateModelsApp.py`

Aplicación Reflex de comparación de ortesis.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `PoolPostgres` | Función/método | [25](../../web/GenerateModelsApp.py#L25) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/jobs/__init__.py`

Marcador de paquete.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `web/jobs/ConciliadorArchivos.py`

Conciliación entre filas de ``file_assets`` y objetos del bucket.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ConciliadorArchivos` | Clase | [30](../../web/jobs/ConciliadorArchivos.py#L30) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConciliadorArchivos.__init__` | Función/método | [31](../../web/jobs/ConciliadorArchivos.py#L31) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConciliadorArchivos.Ejecutar` | Función/método | [34](../../web/jobs/ConciliadorArchivos.py#L34) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConciliadorArchivos._BorrarHuerfanos` | Función/método | [77](../../web/jobs/ConciliadorArchivos.py#L77) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/jobs/TrabajadorGeneracion.py`

Trabajador de generación: un ítem a la vez, con lease y latido.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `_Revision` | Función/método | [40](../../web/jobs/TrabajadorGeneracion.py#L40) | Sin docstring; consultar el catálogo de módulos y el código. |
| `TrabajadorGeneracion` | Clase | [51](../../web/jobs/TrabajadorGeneracion.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `TrabajadorGeneracion.__init__` | Función/método | [52](../../web/jobs/TrabajadorGeneracion.py#L52) | Sin docstring; consultar el catálogo de módulos y el código. |
| `TrabajadorGeneracion.Ciclo` | Función/método | [58](../../web/jobs/TrabajadorGeneracion.py#L58) | Procesa un ítem si hay alguno disponible. Devuelve si procesó. |
| `TrabajadorGeneracion.Procesar` | Función/método | [66](../../web/jobs/TrabajadorGeneracion.py#L66) | Sin docstring; consultar el catálogo de módulos y el código. |
| `TrabajadorGeneracion.Procesar.latir` | Función/método | [71](../../web/jobs/TrabajadorGeneracion.py#L71) | Sin docstring; consultar el catálogo de módulos y el código. |
| `TrabajadorGeneracion._FallarSinPerder` | Función/método | [126](../../web/jobs/TrabajadorGeneracion.py#L126) | Sin docstring; consultar el catálogo de módulos y el código. |
| `TrabajadorGeneracion.Ejecutar` | Función/método | [133](../../web/jobs/TrabajadorGeneracion.py#L133) | Bucle principal: supervisa leases, concilia archivos y procesa la cola. |

## `web/LectorSuperficie.py`

Lectura de superficies subidas a la aplicación web.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `LectorSuperficie` | Clase | [21](../../web/LectorSuperficie.py#L21) | Convierte STL o NPZ en los arreglos que consume el núcleo geométrico. |
| `LectorSuperficie.Preparar` | Función/método | [29](../../web/LectorSuperficie.py#L29) | Sin docstring; consultar el catálogo de módulos y el código. |
| `LectorSuperficie._Npz` | Función/método | [93](../../web/LectorSuperficie.py#L93) | Sin docstring; consultar el catálogo de módulos y el código. |
| `LectorSuperficie._Stl` | Función/método | [110](../../web/LectorSuperficie.py#L110) | Sin docstring; consultar el catálogo de módulos y el código. |
| `LectorSuperficie._StlBinario` | Función/método | [132](../../web/LectorSuperficie.py#L132) | Sin docstring; consultar el catálogo de módulos y el código. |
| `LectorSuperficie._StlAscii` | Función/método | [149](../../web/LectorSuperficie.py#L149) | Sin docstring; consultar el catálogo de módulos y el código. |
| `LectorSuperficie._Normales` | Función/método | [163](../../web/LectorSuperficie.py#L163) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/PaginaComparacion.py`

Pantalla para previsualizar una ortesis o un lote de variantes.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `PaginaComparacion` | Clase | [19](../../web/PaginaComparacion.py#L19) | Formulario con los parámetros del panel y los visores del lote. |
| `PaginaComparacion.Index` | Función/método | [23](../../web/PaginaComparacion.py#L23) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Formulario` | Función/método | [55](../../web/PaginaComparacion.py#L55) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Superficie` | Función/método | [134](../../web/PaginaComparacion.py#L134) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Vista` | Función/método | [203](../../web/PaginaComparacion.py#L203) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Lote` | Función/método | [247](../../web/PaginaComparacion.py#L247) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Fila` | Función/método | [339](../../web/PaginaComparacion.py#L339) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Marco` | Función/método | [370](../../web/PaginaComparacion.py#L370) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Visor` | Función/método | [374](../../web/PaginaComparacion.py#L374) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Enlace` | Función/método | [386](../../web/PaginaComparacion.py#L386) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Campo` | Función/método | [393](../../web/PaginaComparacion.py#L393) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Interruptor` | Función/método | [402](../../web/PaginaComparacion.py#L402) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Selector` | Función/método | [411](../../web/PaginaComparacion.py#L411) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaComparacion.Medida` | Función/método | [428](../../web/PaginaComparacion.py#L428) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/PaginaHistorial.py`

Pantalla /historial: generaciones del usuario, comparación y restauración.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `PaginaHistorial` | Clase | [13](../../web/PaginaHistorial.py#L13) | Filtros, tabla paginada por cursor y visores de las versiones elegidas. |
| `PaginaHistorial.Index` | Función/método | [17](../../web/PaginaHistorial.py#L17) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaHistorial.Filtros` | Función/método | [42](../../web/PaginaHistorial.py#L42) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaHistorial.Fecha` | Función/método | [75](../../web/PaginaHistorial.py#L75) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaHistorial.Tabla` | Función/método | [83](../../web/PaginaHistorial.py#L83) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaHistorial.Fila` | Función/método | [133](../../web/PaginaHistorial.py#L133) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaHistorial.Comparacion` | Función/método | [177](../../web/PaginaHistorial.py#L177) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaHistorial.Tarjeta` | Función/método | [196](../../web/PaginaHistorial.py#L196) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/__init__.py`

Acceso a PostgreSQL con SQL parametrizado, sin ORM.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `web/persistence/ConexionPostgres.py`

Pool síncrono de Psycopg por proceso.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ConexionPostgres` | Clase | [29](../../web/persistence/ConexionPostgres.py#L29) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConexionPostgres.Abrir` | Función/método | [36](../../web/persistence/ConexionPostgres.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConexionPostgres.Cerrar` | Función/método | [60](../../web/persistence/ConexionPostgres.py#L60) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConexionPostgres.Abierta` | Función/método | [67](../../web/persistence/ConexionPostgres.py#L67) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConexionPostgres.Transaccion` | Función/método | [72](../../web/persistence/ConexionPostgres.py#L72) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConexionPostgres.Ejecutar` | Función/método | [88](../../web/persistence/ConexionPostgres.py#L88) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/Contratos.py`

DTO y errores de la persistencia. No son entidades ORM.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ErrorPersistencia` | Clase | [28](../../web/persistence/Contratos.py#L28) | Error previsto con un mensaje que se puede mostrar. |
| `PersistenciaNoDisponible` | Clase | [32](../../web/persistence/Contratos.py#L32) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SesionInvalida` | Clase | [36](../../web/persistence/Contratos.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SesionInvalida.__init__` | Función/método | [37](../../web/persistence/Contratos.py#L37) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AccesoDenegado` | Clase | [41](../../web/persistence/Contratos.py#L41) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AccesoDenegado.__init__` | Función/método | [42](../../web/persistence/Contratos.py#L42) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SolicitudIdempotenteEnConflicto` | Clase | [46](../../web/persistence/Contratos.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SolicitudIdempotenteEnConflicto.__init__` | Función/método | [47](../../web/persistence/Contratos.py#L47) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConflictoRevision` | Clase | [51](../../web/persistence/Contratos.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConflictoRevision.__init__` | Función/método | [52](../../web/persistence/Contratos.py#L52) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CuotaExcedida` | Clase | [56](../../web/persistence/Contratos.py#L56) | Sin docstring; consultar el catálogo de módulos y el código. |
| `UsuarioAutenticado` | Clase | [61](../../web/persistence/Contratos.py#L61) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Asset` | Clase | [69](../../web/persistence/Contratos.py#L69) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ImportDTO` | Clase | [83](../../web/persistence/Contratos.py#L83) | Sin docstring; consultar el catálogo de módulos y el código. |
| `VersionDTO` | Clase | [100](../../web/persistence/Contratos.py#L100) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SolicitudLote` | Clase | [116](../../web/persistence/Contratos.py#L116) | Variantes ya expandidas y validadas por ``GeneradorWeb.Combinaciones``. |
| `LoteDTO` | Clase | [131](../../web/persistence/Contratos.py#L131) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ResultadoDTO` | Clase | [144](../../web/persistence/Contratos.py#L144) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ItemLote` | Clase | [163](../../web/persistence/Contratos.py#L163) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ProgresoLote` | Clase | [177](../../web/persistence/Contratos.py#L177) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ProgresoLote.terminados` | Función/método | [182](../../web/persistence/Contratos.py#L182) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ProgresoLote.abierto` | Función/método | [186](../../web/persistence/Contratos.py#L186) | Sin docstring; consultar el catálogo de módulos y el código. |
| `TrabajoReservado` | Clase | [191](../../web/persistence/Contratos.py#L191) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ResultadoGeometrico` | Clase | [208](../../web/persistence/Contratos.py#L208) | Sin docstring; consultar el catálogo de módulos y el código. |
| `FilaHistorial` | Clase | [226](../../web/persistence/Contratos.py#L226) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PaginaHistorial` | Clase | [248](../../web/persistence/Contratos.py#L248) | Sin docstring; consultar el catálogo de módulos y el código. |
| `IntentoDTO` | Clase | [254](../../web/persistence/Contratos.py#L254) | Sin docstring; consultar el catálogo de módulos y el código. |
| `DetalleVersion` | Clase | [271](../../web/persistence/Contratos.py#L271) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Preferencias` | Clase | [281](../../web/persistence/Contratos.py#L281) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/Modelos.py`

Modelos declarativos de SQLAlchemy del esquema ``ortesislab``.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Base` | Clase | [63](../../web/persistence/Modelos.py#L63) | Sin docstring; consultar el catálogo de módulos y el código. |
| `_Sha` | Función/método | [83](../../web/persistence/Modelos.py#L83) | Sin docstring; consultar el catálogo de módulos y el código. |
| `_Valores` | Función/método | [87](../../web/persistence/Modelos.py#L87) | Sin docstring; consultar el catálogo de módulos y el código. |
| `_Defecto` | Función/método | [93](../../web/persistence/Modelos.py#L93) | Sin docstring; consultar el catálogo de módulos y el código. |
| `_Objeto` | Función/método | [97](../../web/persistence/Modelos.py#L97) | Sin docstring; consultar el catálogo de módulos y el código. |
| `_Check` | Función/método | [101](../../web/persistence/Modelos.py#L101) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Usuario` | Clase | [105](../../web/persistence/Modelos.py#L105) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SesionAutenticacion` | Clase | [123](../../web/persistence/Modelos.py#L123) | Sesión de servidor tras el login OIDC; la cookie solo lleva el token. |
| `PreferenciaUsuario` | Clase | [141](../../web/persistence/Modelos.py#L141) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ArchivoAlmacenado` | Clase | [159](../../web/persistence/Modelos.py#L159) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Proyecto` | Clase | [194](../../web/persistence/Modelos.py#L194) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Importacion` | Clase | [222](../../web/persistence/Modelos.py#L222) | Sin docstring; consultar el catálogo de módulos y el código. |
| `VersionModelo` | Clase | [287](../../web/persistence/Modelos.py#L287) | Versión inmutable; el trigger ``model_versions_comprobar`` valida import y padre. |
| `LoteGeneracion` | Clase | [348](../../web/persistence/Modelos.py#L348) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ItemLoteGeneracion` | Clase | [393](../../web/persistence/Modelos.py#L393) | Sin docstring; consultar el catálogo de módulos y el código. |
| `IntentoGeneracion` | Clase | [462](../../web/persistence/Modelos.py#L462) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ResultadoGeneracion` | Clase | [522](../../web/persistence/Modelos.py#L522) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Exportacion` | Clase | [570](../../web/persistence/Modelos.py#L570) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EventoHistorial` | Clase | [600](../../web/persistence/Modelos.py#L600) | Historial append-only: los roles de aplicación no tienen UPDATE ni DELETE. |

## `web/persistence/repositorios/__init__.py`

Repositorios SQLAlchemy, uno por archivo. Reciben una ``Session`` ya abierta y no hacen commit.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `web/persistence/repositorios/Consultas.py`

Tablas y fragmentos de consulta que comparten varios repositorios.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Segundos` | Función/método | [45](../../web/persistence/repositorios/Consultas.py#L45) | Sin docstring; consultar el catálogo de módulos y el código. |
| `UltimoError` | Función/método | [49](../../web/persistence/repositorios/Consultas.py#L49) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConStlGanador` | Función/método | [62](../../web/persistence/repositorios/Consultas.py#L62) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ColumnasResultado` | Función/método | [81](../../web/persistence/repositorios/Consultas.py#L81) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioAssets.py`

Filas de ``file_assets``: el contenido vive en el bucket.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioAssets` | Clase | [18](../../web/persistence/repositorios/RepositorioAssets.py#L18) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets._Seleccion` | Función/método | [27](../../web/persistence/repositorios/RepositorioAssets.py#L27) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.CrearStaged` | Función/método | [31](../../web/persistence/repositorios/RepositorioAssets.py#L31) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.MarcarListo` | Función/método | [57](../../web/persistence/repositorios/RepositorioAssets.py#L57) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.MarcarEstado` | Función/método | [67](../../web/persistence/repositorios/RepositorioAssets.py#L67) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.Obtener` | Función/método | [75](../../web/persistence/repositorios/RepositorioAssets.py#L75) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.ListoPorSha` | Función/método | [79](../../web/persistence/repositorios/RepositorioAssets.py#L79) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.StagedVencidos` | Función/método | [94](../../web/persistence/repositorios/RepositorioAssets.py#L94) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.RechazadosVencidos` | Función/método | [104](../../web/persistence/repositorios/RepositorioAssets.py#L104) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.ListosParaComprobar` | Función/método | [123](../../web/persistence/repositorios/RepositorioAssets.py#L123) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.PorClave` | Función/método | [130](../../web/persistence/repositorios/RepositorioAssets.py#L130) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.ClavesRegistradas` | Función/método | [134](../../web/persistence/repositorios/RepositorioAssets.py#L134) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioAssets.MarcarExportsFaltantes` | Función/método | [139](../../web/persistence/repositorios/RepositorioAssets.py#L139) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioBase.py`

Clase padre de los repositorios: lectura de filas y conversión a DTO.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioBase` | Clase | [19](../../web/persistence/repositorios/RepositorioBase.py#L19) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioBase._Uno` | Función/método | [24](../../web/persistence/repositorios/RepositorioBase.py#L24) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioBase._Todos` | Función/método | [29](../../web/persistence/repositorios/RepositorioBase.py#L29) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioBase._Construir` | Función/método | [33](../../web/persistence/repositorios/RepositorioBase.py#L33) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioBase._Dto` | Función/método | [38](../../web/persistence/repositorios/RepositorioBase.py#L38) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioBase._Seleccion` | Función/método | [42](../../web/persistence/repositorios/RepositorioBase.py#L42) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioBase._Opcional` | Función/método | [46](../../web/persistence/repositorios/RepositorioBase.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioBase._Lista` | Función/método | [51](../../web/persistence/repositorios/RepositorioBase.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioBase._DelUsuario` | Función/método | [55](../../web/persistence/repositorios/RepositorioBase.py#L55) | Fila del usuario que cumple ``condiciones``; un recurso ajeno o inexistente lanza ``AccesoDenegado``. |

## `web/persistence/repositorios/RepositorioHistorial.py`

Eventos de historial y listado de ejecuciones por versión.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioHistorial` | Clase | [25](../../web/persistence/repositorios/RepositorioHistorial.py#L25) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioHistorial.Evento` | Función/método | [29](../../web/persistence/repositorios/RepositorioHistorial.py#L29) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioHistorial.Listar` | Función/método | [55](../../web/persistence/repositorios/RepositorioHistorial.py#L55) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioHistorial.EventosDeVersion` | Función/método | [133](../../web/persistence/repositorios/RepositorioHistorial.py#L133) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioImports.py`

Importaciones de superficies: original recibido y NPZ normalizado.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioImports` | Clase | [16](../../web/persistence/repositorios/RepositorioImports.py#L16) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioImports.Crear` | Función/método | [21](../../web/persistence/repositorios/RepositorioImports.py#L21) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioImports.MarcarListo` | Función/método | [46](../../web/persistence/repositorios/RepositorioImports.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioImports.MarcarRechazado` | Función/método | [69](../../web/persistence/repositorios/RepositorioImports.py#L69) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioImports.Obtener` | Función/método | [77](../../web/persistence/repositorios/RepositorioImports.py#L77) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioImports.ListoPorNormalizado` | Función/método | [81](../../web/persistence/repositorios/RepositorioImports.py#L81) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioImports.ListoPorOriginal` | Función/método | [95](../../web/persistence/repositorios/RepositorioImports.py#L95) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioImports.NombreOriginal` | Función/método | [125](../../web/persistence/repositorios/RepositorioImports.py#L125) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioLotes.py`

Lotes, ítems y cola del trabajador: admisión, reserva, lease y cierre.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioLotes` | Clase | [32](../../web/persistence/repositorios/RepositorioLotes.py#L32) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes._ClaveBloqueo` | Función/método | [37](../../web/persistence/repositorios/RepositorioLotes.py#L37) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.BloquearUsuario` | Función/método | [41](../../web/persistence/repositorios/RepositorioLotes.py#L41) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.IntentarBloquearUsuario` | Función/método | [46](../../web/persistence/repositorios/RepositorioLotes.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.PorRequest` | Función/método | [52](../../web/persistence/repositorios/RepositorioLotes.py#L52) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.ContarPendientes` | Función/método | [56](../../web/persistence/repositorios/RepositorioLotes.py#L56) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.InsertarLote` | Función/método | [66](../../web/persistence/repositorios/RepositorioLotes.py#L66) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.InsertarItem` | Función/método | [91](../../web/persistence/repositorios/RepositorioLotes.py#L91) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.Obtener` | Función/método | [109](../../web/persistence/repositorios/RepositorioLotes.py#L109) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.Ultimo` | Función/método | [113](../../web/persistence/repositorios/RepositorioLotes.py#L113) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.Items` | Función/método | [123](../../web/persistence/repositorios/RepositorioLotes.py#L123) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.SolicitarCancelacion` | Función/método | [150](../../web/persistence/repositorios/RepositorioLotes.py#L150) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.Recalcular` | Función/método | [171](../../web/persistence/repositorios/RepositorioLotes.py#L171) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes._Candidato` | Función/método | [220](../../web/persistence/repositorios/RepositorioLotes.py#L220) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.ReservarPendiente` | Función/método | [246](../../web/persistence/repositorios/RepositorioLotes.py#L246) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes._ItemVigente` | Función/método | [345](../../web/persistence/repositorios/RepositorioLotes.py#L345) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.RenovarLease` | Función/método | [354](../../web/persistence/repositorios/RepositorioLotes.py#L354) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.BloquearVigente` | Función/método | [370](../../web/persistence/repositorios/RepositorioLotes.py#L370) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.CancelacionPedida` | Función/método | [377](../../web/persistence/repositorios/RepositorioLotes.py#L377) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.CerrarIntento` | Función/método | [384](../../web/persistence/repositorios/RepositorioLotes.py#L384) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.Exito` | Función/método | [412](../../web/persistence/repositorios/RepositorioLotes.py#L412) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.Liberar` | Función/método | [443](../../web/persistence/repositorios/RepositorioLotes.py#L443) | Saca el ítem de ``running``: a la cola, cancelado o fallido. |
| `RepositorioLotes.AbandonarIntento` | Función/método | [469](../../web/persistence/repositorios/RepositorioLotes.py#L469) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes.Vencidos` | Función/método | [488](../../web/persistence/repositorios/RepositorioLotes.py#L488) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioLotes._Item` | Función/método | [508](../../web/persistence/repositorios/RepositorioLotes.py#L508) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioPreferencias.py`

Preferencias por usuario con control optimista de revisión.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioPreferencias` | Clase | [15](../../web/persistence/repositorios/RepositorioPreferencias.py#L15) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioPreferencias.Obtener` | Función/método | [20](../../web/persistence/repositorios/RepositorioPreferencias.py#L20) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioPreferencias.Guardar` | Función/método | [27](../../web/persistence/repositorios/RepositorioPreferencias.py#L27) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioProyectos.py`

Proyectos del usuario; cada cuenta tiene uno predeterminado.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioProyectos` | Clase | [16](../../web/persistence/repositorios/RepositorioProyectos.py#L16) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioProyectos.Predeterminado` | Función/método | [20](../../web/persistence/repositorios/RepositorioProyectos.py#L20) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioProyectos.Crear` | Función/método | [36](../../web/persistence/repositorios/RepositorioProyectos.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioProyectos.PorNombre` | Función/método | [44](../../web/persistence/repositorios/RepositorioProyectos.py#L44) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioProyectos.Listar` | Función/método | [53](../../web/persistence/repositorios/RepositorioProyectos.py#L53) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioResultados.py`

Resultados geométricos, intentos de una versión y exports STL.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioResultados` | Clase | [18](../../web/persistence/repositorios/RepositorioResultados.py#L18) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioResultados.Insertar` | Función/método | [22](../../web/persistence/repositorios/RepositorioResultados.py#L22) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioResultados.InsertarExport` | Función/método | [46](../../web/persistence/repositorios/RepositorioResultados.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioResultados.Dto` | Función/método | [62](../../web/persistence/repositorios/RepositorioResultados.py#L62) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioResultados._Dto` | Función/método | [83](../../web/persistence/repositorios/RepositorioResultados.py#L83) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioResultados.Intentos` | Función/método | [87](../../web/persistence/repositorios/RepositorioResultados.py#L87) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioResultados.DeVersion` | Función/método | [102](../../web/persistence/repositorios/RepositorioResultados.py#L102) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioResultados.ExportStl` | Función/método | [127](../../web/persistence/repositorios/RepositorioResultados.py#L127) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioUsuarios.py`

Cuentas creadas desde OIDC y sus sesiones de servidor.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioUsuarios` | Clase | [18](../../web/persistence/repositorios/RepositorioUsuarios.py#L18) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioUsuarios.Upsert` | Función/método | [22](../../web/persistence/repositorios/RepositorioUsuarios.py#L22) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioUsuarios.Estado` | Función/método | [41](../../web/persistence/repositorios/RepositorioUsuarios.py#L41) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioUsuarios.CrearSesion` | Función/método | [45](../../web/persistence/repositorios/RepositorioUsuarios.py#L45) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioUsuarios.ResolverSesion` | Función/método | [51](../../web/persistence/repositorios/RepositorioUsuarios.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioUsuarios.RevocarSesion` | Función/método | [65](../../web/persistence/repositorios/RepositorioUsuarios.py#L65) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/persistence/repositorios/RepositorioVersiones.py`

Versiones inmutables numeradas por proyecto.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RepositorioVersiones` | Clase | [16](../../web/persistence/repositorios/RepositorioVersiones.py#L16) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioVersiones.ReservarNumeros` | Función/método | [21](../../web/persistence/repositorios/RepositorioVersiones.py#L21) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioVersiones.Insertar` | Función/método | [35](../../web/persistence/repositorios/RepositorioVersiones.py#L35) | Sin docstring; consultar el catálogo de módulos y el código. |
| `RepositorioVersiones.Obtener` | Función/método | [69](../../web/persistence/repositorios/RepositorioVersiones.py#L69) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/services/__init__.py`

Marcador de paquete.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `web/services/AutenticacionOidc.py`

Rutas OIDC del backend: /auth/login, /auth/callback y /auth/logout.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `AutenticacionOidc` | Clase | [27](../../web/services/AutenticacionOidc.py#L27) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AutenticacionOidc.Aplicacion` | Función/método | [29](../../web/services/AutenticacionOidc.py#L29) | Aplicación raíz que Reflex usa como transformador; monta /auth. |
| `AutenticacionOidc.Aplicacion.login` | Función/método | [41](../../web/services/AutenticacionOidc.py#L41) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AutenticacionOidc.Aplicacion.callback` | Función/método | [44](../../web/services/AutenticacionOidc.py#L44) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AutenticacionOidc.Aplicacion.logout` | Función/método | [72](../../web/services/AutenticacionOidc.py#L72) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/services/ContextoUsuario.py`

Principal autenticado de cada operación.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ContextoUsuario` | Clase | [30](../../web/services/ContextoUsuario.py#L30) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ContextoUsuario.Hash` | Función/método | [32](../../web/services/ContextoUsuario.py#L32) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ContextoUsuario.TokenDeCookie` | Función/método | [36](../../web/services/ContextoUsuario.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ContextoUsuario.Requerir` | Función/método | [48](../../web/services/ContextoUsuario.py#L48) | Entrada: cabecera Cookie. Proceso: resuelve la sesión vigente y el |
| `ContextoUsuario.Requerir.resolver` | Función/método | [57](../../web/services/ContextoUsuario.py#L57) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ContextoUsuario.IniciarSesion` | Función/método | [67](../../web/services/ContextoUsuario.py#L67) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ContextoUsuario.IniciarSesion.crear` | Función/método | [72](../../web/services/ContextoUsuario.py#L72) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ContextoUsuario.CerrarSesion` | Función/método | [84](../../web/services/ContextoUsuario.py#L84) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ContextoUsuario.Activar` | Función/método | [92](../../web/services/ContextoUsuario.py#L92) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ContextoUsuario.Actual` | Función/método | [101](../../web/services/ContextoUsuario.py#L101) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/services/GeneradorGeometrico.py`

Construcción numérica de una versión: métricas, STL y JSON de parámetros.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `GeneradorGeometrico` | Clase | [26](../../web/services/GeneradorGeometrico.py#L26) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorGeometrico.MaterialDe` | Función/método | [28](../../web/services/GeneradorGeometrico.py#L28) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorGeometrico.Construir` | Función/método | [39](../../web/services/GeneradorGeometrico.py#L39) | Salida: resultado numérico, STL binario y JSON canónico de parámetros. |

## `web/services/ServicioHistorial.py`

Historial por usuario: listado paginado, detalle, restauración y reintento.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ServicioHistorial` | Clase | [40](../../web/services/ServicioHistorial.py#L40) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioHistorial.CodificarCursor` | Función/método | [42](../../web/services/ServicioHistorial.py#L42) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioHistorial.DecodificarCursor` | Función/método | [47](../../web/services/ServicioHistorial.py#L47) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioHistorial.Listar` | Función/método | [55](../../web/services/ServicioHistorial.py#L55) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioHistorial.Detalle` | Función/método | [79](../../web/services/ServicioHistorial.py#L79) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioHistorial.Detalle.leer` | Función/método | [80](../../web/services/ServicioHistorial.py#L80) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioHistorial.Comparar` | Función/método | [98](../../web/services/ServicioHistorial.py#L98) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioHistorial.Restaurar` | Función/método | [104](../../web/services/ServicioHistorial.py#L104) | Crea una versión nueva con los parámetros de otra; no modifica la original. |
| `ServicioHistorial.Reintentar` | Función/método | [124](../../web/services/ServicioHistorial.py#L124) | Nuevo lote ``retry`` sobre versiones existentes: nuevos intentos, mismas versiones. |
| `ServicioHistorial.RegistrarDescarga` | Función/método | [146](../../web/services/ServicioHistorial.py#L146) | Devuelve la object_url del STL del usuario y registra la descarga. |
| `ServicioHistorial.RegistrarDescarga.registrar` | Función/método | [149](../../web/services/ServicioHistorial.py#L149) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/services/ServicioImports.py`

Importación de superficies: original y NPZ normalizado en el bucket.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ServicioImports` | Clase | [41](../../web/services/ServicioImports.py#L41) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports.NombreSuperficie` | Función/método | [43](../../web/services/ServicioImports.py#L43) | Identificador que la página guarda en ``superficie_archivo``. |
| `ServicioImports.AssetDeNombre` | Función/método | [48](../../web/services/ServicioImports.py#L48) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports.TuplaANpz` | Función/método | [60](../../web/services/ServicioImports.py#L60) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports.NpzATupla` | Función/método | [67](../../web/services/ServicioImports.py#L67) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports.PrepararPlantilla` | Función/método | [80](../../web/services/ServicioImports.py#L80) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports.Importar` | Función/método | [90](../../web/services/ServicioImports.py#L90) | Entrada: archivo subido. Proceso: lo guarda y normaliza. Salida: import |
| `ServicioImports.Importar.normalizar` | Función/método | [112](../../web/services/ServicioImports.py#L112) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports.AsegurarPlantilla` | Función/método | [120](../../web/services/ServicioImports.py#L120) | La plantilla incluida pasa a ser un import del proyecto del usuario. |
| `ServicioImports.Resolver` | Función/método | [129](../../web/services/ServicioImports.py#L129) | ``""`` es la plantilla; otro valor es el NPZ de un import del usuario. |
| `ServicioImports.Info` | Función/método | [142](../../web/services/ServicioImports.py#L142) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports._Registrar` | Función/método | [158](../../web/services/ServicioImports.py#L158) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports._Registrar.recibir` | Función/método | [178](../../web/services/ServicioImports.py#L178) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioImports._Registrar.publicar` | Función/método | [221](../../web/services/ServicioImports.py#L221) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/services/ServicioLotes.py`

Admisión de lotes, progreso y transiciones del trabajador.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ServicioLotes` | Clase | [46](../../web/services/ServicioLotes.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.HuellaSolicitud` | Función/método | [48](../../web/services/ServicioLotes.py#L48) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Solicitar` | Función/método | [62](../../web/services/ServicioLotes.py#L62) | Entrada: variantes ya validadas. Proceso: crea versiones, lote e ítems |
| `ServicioLotes.Solicitar.admitir` | Función/método | [73](../../web/services/ServicioLotes.py#L73) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Progreso` | Función/método | [114](../../web/services/ServicioLotes.py#L114) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Progreso.leer` | Función/método | [115](../../web/services/ServicioLotes.py#L115) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Ultimo` | Función/método | [122](../../web/services/ServicioLotes.py#L122) | Último lote del usuario: la página lo recupera al recargar o reiniciar. |
| `ServicioLotes.Ultimo.leer` | Función/método | [125](../../web/services/ServicioLotes.py#L125) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Esperar` | Función/método | [134](../../web/services/ServicioLotes.py#L134) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Cancelar` | Función/método | [143](../../web/services/ServicioLotes.py#L143) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Cancelar.cancelar` | Función/método | [144](../../web/services/ServicioLotes.py#L144) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Reservar` | Función/método | [157](../../web/services/ServicioLotes.py#L157) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Renovar` | Función/método | [163](../../web/services/ServicioLotes.py#L163) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.CancelacionPedida` | Función/método | [167](../../web/services/ServicioLotes.py#L167) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.RegistrarSalidas` | Función/método | [171](../../web/services/ServicioLotes.py#L171) | Filas ``staged`` de los objetos que el trabajador va a subir: |
| `ServicioLotes.RegistrarSalidas.registrar` | Función/método | [175](../../web/services/ServicioLotes.py#L175) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Confirmar` | Función/método | [182](../../web/services/ServicioLotes.py#L182) | Publica resultado y exports si el lease sigue vigente. Devuelve False |
| `ServicioLotes.Confirmar.confirmar` | Función/método | [192](../../web/services/ServicioLotes.py#L192) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Fallar` | Función/método | [216](../../web/services/ServicioLotes.py#L216) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.Fallar.fallar` | Función/método | [217](../../web/services/ServicioLotes.py#L217) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.CerrarCancelado` | Función/método | [234](../../web/services/ServicioLotes.py#L234) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.CerrarCancelado.cerrar` | Función/método | [235](../../web/services/ServicioLotes.py#L235) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioLotes.AbandonarVencidos` | Función/método | [245](../../web/services/ServicioLotes.py#L245) | Devuelve a la cola los ítems cuyo trabajador dejó de renovar el lease. |
| `ServicioLotes.AbandonarVencidos.abandonar` | Función/método | [248](../../web/services/ServicioLotes.py#L248) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/services/ServicioPreferencias.py`

Preferencias por usuario con control optimista de revisión.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ServicioPreferencias` | Clase | [10](../../web/services/ServicioPreferencias.py#L10) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioPreferencias.Obtener` | Función/método | [12](../../web/services/ServicioPreferencias.py#L12) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioPreferencias.GuardarAutoescala` | Función/método | [16](../../web/services/ServicioPreferencias.py#L16) | Errores: ConflictoRevision si otra pestaña guardó antes. |
| `ServicioPreferencias.GuardarAutoescala.guardar` | Función/método | [19](../../web/services/ServicioPreferencias.py#L19) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/services/ServicioVersiones.py`

Versiones inmutables: snapshot de parámetros, material y escala.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ServicioVersiones` | Clase | [22](../../web/services/ServicioVersiones.py#L22) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioVersiones.Canonico` | Función/método | [24](../../web/services/ServicioVersiones.py#L24) | JSON estable para hashes: claves ordenadas, sin espacios, sin NaN. |
| `ServicioVersiones.Sha` | Función/método | [29](../../web/services/ServicioVersiones.py#L29) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioVersiones.Material` | Función/método | [33](../../web/services/ServicioVersiones.py#L33) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioVersiones.Parametros` | Función/método | [46](../../web/services/ServicioVersiones.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ServicioVersiones.Insertar` | Función/método | [56](../../web/services/ServicioVersiones.py#L56) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/Sesion.py`

Barra de sesión común a la comparación y al historial.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Sesion` | Clase | [8](../../web/Sesion.py#L8) | Enlaces a las rutas OIDC del backend y navegación entre páginas. |
| `Sesion.Ruta` | Función/método | [12](../../web/Sesion.py#L12) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Sesion.Boton` | Función/método | [17](../../web/Sesion.py#L17) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Sesion.Barra` | Función/método | [23](../../web/Sesion.py#L23) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/storage/__init__.py`

Marcador de paquete.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `web/storage/AlmacenamientoPrivado.py`

Contrato del almacén de bytes y claves de objeto.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `AlmacenamientoNoDisponible` | Clase | [25](../../web/storage/AlmacenamientoPrivado.py#L25) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AlmacenamientoNoDisponible.__init__` | Función/método | [26](../../web/storage/AlmacenamientoPrivado.py#L26) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ObjetoAusente` | Clase | [30](../../web/storage/AlmacenamientoPrivado.py#L30) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ObjetoAusente.__init__` | Función/método | [31](../../web/storage/AlmacenamientoPrivado.py#L31) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AlmacenamientoPrivado` | Clase | [35](../../web/storage/AlmacenamientoPrivado.py#L35) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AlmacenamientoPrivado.Url` | Función/método | [36](../../web/storage/AlmacenamientoPrivado.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AlmacenamientoPrivado.Publicar` | Función/método | [38](../../web/storage/AlmacenamientoPrivado.py#L38) | Sube el objeto completo, comprueba tamaño y hash, y devuelve su URL. |
| `AlmacenamientoPrivado.Leer` | Función/método | [42](../../web/storage/AlmacenamientoPrivado.py#L42) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AlmacenamientoPrivado.Existe` | Función/método | [44](../../web/storage/AlmacenamientoPrivado.py#L44) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AlmacenamientoPrivado.Borrar` | Función/método | [46](../../web/storage/AlmacenamientoPrivado.py#L46) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AlmacenamientoPrivado.Claves` | Función/método | [48](../../web/storage/AlmacenamientoPrivado.py#L48) | Clave y fecha de última modificación de cada objeto bajo el prefijo. |
| `Almacen` | Clase | [53](../../web/storage/AlmacenamientoPrivado.py#L53) | Instancia de proceso. Las pruebas la sustituyen con ``Usar``. |
| `Almacen.Actual` | Función/método | [59](../../web/storage/AlmacenamientoPrivado.py#L59) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Almacen.Usar` | Función/método | [67](../../web/storage/AlmacenamientoPrivado.py#L67) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Almacen.Clave` | Función/método | [71](../../web/storage/AlmacenamientoPrivado.py#L71) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Almacen.Sha256` | Función/método | [76](../../web/storage/AlmacenamientoPrivado.py#L76) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Almacen.LeerVerificado` | Función/método | [80](../../web/storage/AlmacenamientoPrivado.py#L80) | Sin docstring; consultar el catálogo de módulos y el código. |

## `web/storage/StorageS3.py`

Almacén de bytes en un bucket S3 (MinIO en desarrollo).

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `StorageS3` | Clase | [25](../../web/storage/StorageS3.py#L25) | Sin docstring; consultar el catálogo de módulos y el código. |
| `StorageS3.__init__` | Función/método | [26](../../web/storage/StorageS3.py#L26) | Sin docstring; consultar el catálogo de módulos y el código. |
| `StorageS3.DesdeAjustes` | Función/método | [45](../../web/storage/StorageS3.py#L45) | Sin docstring; consultar el catálogo de módulos y el código. |
| `StorageS3.Url` | Función/método | [56](../../web/storage/StorageS3.py#L56) | Sin docstring; consultar el catálogo de módulos y el código. |
| `StorageS3.Publicar` | Función/método | [59](../../web/storage/StorageS3.py#L59) | Sin docstring; consultar el catálogo de módulos y el código. |
| `StorageS3.Leer` | Función/método | [72](../../web/storage/StorageS3.py#L72) | Sin docstring; consultar el catálogo de módulos y el código. |
| `StorageS3.Existe` | Función/método | [83](../../web/storage/StorageS3.py#L83) | Sin docstring; consultar el catálogo de módulos y el código. |
| `StorageS3.Borrar` | Función/método | [94](../../web/storage/StorageS3.py#L94) | Sin docstring; consultar el catálogo de módulos y el código. |
| `StorageS3.Claves` | Función/método | [100](../../web/storage/StorageS3.py#L100) | Sin docstring; consultar el catálogo de módulos y el código. |
