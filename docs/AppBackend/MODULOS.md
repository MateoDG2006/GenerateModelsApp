# Carpetas y archivos de AppBackend

Las rutas se expresan desde la raíz del repositorio. [INVENTARIO.md](../Agents/INVENTARIO.md) cubre también herramientas, pruebas, configuraciones, archivos vacíos y artefactos. El [índice de símbolos](SIMBOLOS.md) enumera automáticamente cada clase, función y método del ámbito backend.

## Infraestructura y entradas

| Archivo/carpeta | Responsabilidad y relación |
|---|---|
| [`rxconfig.py`](../../rxconfig.py) | Selecciona el módulo web, sitemap, Tailwind V4 y tema Radix indigo/slate/medium |
| [`web/GenerateModelsApp.py`](../../web/GenerateModelsApp.py) | Instancia `rx.App`; registra página y evento inicial |
| [`web/__init__.py`](../../web/__init__.py) | Marcador del paquete web; no arranca servicios |
| [`pyproject.toml`](../../pyproject.toml) | Dependencias Python, versión del proyecto, empaquetado `uv_build` y comando de saludo |
| [`uv.lock`](../../uv.lock) / [`.python-version`](../../.python-version) | Resolución Python y selección de intérprete |
| `reflex.lock/` | `package.json` y `bun.lock` versionan dependencias del frontend generado |
| `.web/`, `.states/`, `.venv/` | Compilación frontend, artefactos de estado y entorno virtual generados; no modificar para implementar reglas |
| `uploaded_files/` | Salidas STL y superficies normalizadas NPZ; regenerables pero pueden contener trabajo del usuario |
| `GenerateModelsApp/logs/` | Registro compartido del dominio; aparece bajo demanda y está ignorado por Git |
| [`src/generatemodelsapp/__init__.py`](../../src/generatemodelsapp/__init__.py) | `main` localiza e invoca el saludo de consola; no arranca Reflex |
| [`scripts/IniciarConsola.py`](../../scripts/IniciarConsola.py) | Implementa ese saludo; no genera modelos |

## `web/EstadoApp.py`

[`EstadoApp`](../../web/EstadoApp.py) hereda de `rx.State`. Los números de formulario se almacenan como cadenas para permitir edición y coma decimal. Los booleanos permanecen booleanos.

| Grupo | Métodos/campos | Función |
|---|---|---|
| Parámetros | `pattern`, 13 campos numéricos (incluida `seed`), `liner`, `repair`, `flip_normals` | Adaptación del contrato compartido; ver [parámetros](../BlenderPlugin/PARAMETROS.md) |
| Edición | `set_*` explícitos decorados con `@rx.event` | Asignan valores; no generan geometría ni validan cada tecla |
| Entrada | `CargarSuperficie`, `UsarSuperficieIncluida`, `superficie_*`, `autoescalar_superficie` | Seleccionan entrada y limpian resultados al aceptar una nueva base |
| Inicialización | `CargarPredeterminados` | Copia el JSON al formulario al cargar la página; no consulta una base de datos |
| Trabajo | `Previsualizar`, `PedirLote`, `Generar`, `_trabajando`, `ocupado`, `hechos`, `total` | Encadenan y ejecutan la generación explícita con progreso |
| Selección | `Ver`, `Comparar`, `_Mostrar`, `archivo`, `ficha_*`, `vistas` | Abren una ficha o alternan su presencia entre hasta tres visores |
| Descarga | `Descargar` | Lee el STL por identificador de ficha y devuelve `rx.download(data=..., filename=...)` |
| Derivados | `aviso_escala`, `espesor_total`, `porcentaje` con `@rx.var` | Aviso de escala, suma nominal de espesores y progreso entero |
| Adaptación | `_Numero`, `_Opciones`, `_Variantes` | Parsean texto, validan semilla y construyen opciones/combinaciones |

`ID_SUBIDA_SUPERFICIE="superficie-entrada"` vincula selector, upload y limpieza de selección. `LIMITE_LOTE` exporta a la página el máximo de `GeneradorWeb`.

## `web/GeneradorWeb.py`

[`GeneradorWeb`](../../web/GeneradorWeb.py) es un servicio de métodos estáticos. `PATRONES` traduce códigos a etiquetas; `EJES` define los once campos que se pueden barrer; `MAXIMO_VARIANTES=12` limita el lote.

| Métodos | Entrada → proceso → salida / efectos |
|---|---|
| `Cruda`, `_GuardarCruda`, `EjeMayor` | Nombre interno o vacío → NPZ guardado o asset incluido → arrays originales y dimensión; caché de dos entradas |
| `Superficie`, `_SuperficieConDiagnostico` | Copias originales → `EscalaMalla.Resolver` → arrays escalados y diagnóstico; no cambian el archivo |
| `SuperficieRefinada`, `_SuperficieRefinadaConDiagnostico` | Nombre, paso, autoescala → escala/refinamiento → arrays y diagnóstico; caché de dos entradas |
| `GuardarSuperficie` | Bytes STL/NPZ → lector y validación sin hornear autoescala → NPZ normalizado con UUID; conserva coordenadas originales |
| `Crear` | Opciones/base/preferencia → superficie, `Construir`, métricas, STL → ficha; escribe archivo en subidas |
| `Ficha`, `FichaError`, `Detalle`, `Numero` | Datos de dominio → diccionario y texto español; errores abreviados a 180 caracteres |
| `Combinaciones` | Base, patrones, rango, capas → producto acotado de variantes; `Decimal` evita acumulación binaria en el barrido |
| `Triangulos`, `Stl` | Polígonos → abanico triangular y normales → bytes STL binarios |
| `Ruta`, `RutaSuperficie` | Nombre interno → validación sintáctica → ruta bajo `rx.get_upload_dir()` |
| `Escribir`, `Leer` | Nombre interno y bytes → E/S en disco; `Escribir` también activa el soporte de subidas de Reflex |

## `web/LectorSuperficie.py`

[`LectorSuperficie`](../../web/LectorSuperficie.py) restringe extensiones, tamaño, finitud y topología. `_StlBinario` acepta registros si el tamaño es exactamente `84 + 50*n`; de lo contrario `_StlAscii` extrae grupos de tres líneas `vertex`. `_Stl` fusiona coordenadas por cuantización y recalcula normales de caras. `_Npz` revisa la expansión declarada ZIP y carga sin pickle. `Preparar` devuelve la superficie analizada y metadatos; no escribe por sí mismo.

## Dominio reutilizado

`Modeling.py` orquesta patrones/cascarón; `Malla.py` valida la base; `EscalaMalla.py` decide factores decimales; `RefinadorMalla.py` subdivide; `SuavizadoBorde.py` filtra el contorno; `Cascaron.py` recorta y engrosa; `constants/Paterns.py` calcula campos; `constants/Materials.py` convierte volumen en coste; `util/Utilidades.py` lee configuración y registra errores; `Excepciones.py` tipa los fallos. Su explicación completa está en [BlenderPlugin/MODULOS.md](../BlenderPlugin/MODULOS.md) y [ALGORITMOS.md](../BlenderPlugin/ALGORITMOS.md).

`ApiBlender`, `Interfaz`, `Objeto`, `Superficie`, `ReparacionMalla`, `ValidacionMalla`, `Exportacion` y `OrtesisLab` no deben importarse para arrancar la web: requieren el entorno Blender.
