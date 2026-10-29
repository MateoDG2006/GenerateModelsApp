# Mantenimiento y revisión de documentación

## Contrato de las siguientes iteraciones

Las instrucciones persistentes están en [AGENTS.md](../../AGENTS.md). Todo agente que cambie lógica fundamental debe actualizar documentación **en la misma iteración**, sin esperar una petición documental adicional. Esto es parte de terminar el cambio de software.

El agente/desarrollador actualiza las explicaciones por significado; [`Scripts/GenerarIndices.py`](Scripts/GenerarIndices.py) regenera los catálogos de hechos (inventario, índices de símbolos y configuración) y comprueba enlaces. El script no comprende ni certifica que un algoritmo esté bien explicado. No hay tarea programada ni CI instalada.

## Qué cuenta como cambio fundamental

Cambiar geometría, sentido de normales, topología/recorte, patrón, escala, refinamiento, suavizado, espesores, validación, exportación o formato; añadir/eliminar parámetros o modificar límites/defaults; cambiar eventos/estado/carga/descarga/almacenamiento; nuevas pantallas o componentes; cambiar dependencias con efecto en compilación/protocolo; modificar registro, empaquetado o separación Blender/web.

El agente decide y registra si un cambio no altera el contrato. No existe un detector de «fundamental».

## Matriz de impacto obligatorio

| Cambio | Documentos a revisar |
|---|---|
| `Modeling`, `Malla`, `Cascaron`, patrones, refinador, escala o borde | BlenderPlugin/ALGORITMOS, MODULOS, API_Y_DATOS; arquitectura backend y diferencias web/Blender |
| Defaults, límites, propiedades del panel | BlenderPlugin/PARAMETROS y CONFIGURACION_GENERADA; formularios frontend y contratos backend |
| `EstadoApp`, `GeneradorWeb`, `LectorSuperficie` | AppBackend/ARQUITECTURA, MODULOS, CONTRATOS, pruebas; flujos frontend |
| Página, componentes, binding, rutas o visor | AppFrontend/ARQUITECTURA, COMPONENTES_Y_FLUJOS, VISOR_3D y aceptación; contratos si cambian datos |
| Objeto, reparación, validación, exportación y registro Blender | BlenderPlugin/ARQUITECTURA, API_Y_DATOS, OPERACION_Y_PRUEBAS y guía breve LEEME |
| Dependencias, procesos o empaquetado | Operación de sistemas afectados, inventario y README |
| Archivos nuevos, eliminados o renombrados | Catálogo de responsabilidad y enlaces; INVENTARIO y SIMBOLOS |
| Clases, funciones o métodos nuevos, movidos o renombrados | SIMBOLOS del área |
| JSON de `GenerateModelsApp/config/` | CONFIGURACION_GENERADA y PARAMETROS |

## Secuencia obligatoria del agente/desarrollador

1. Leer instrucciones de repo. Si hay `.codegraph/`, consultarlo antes de localizar/entender código; no indexar por cuenta propia.
2. Identificar fuentes cambiadas, contratos, consumidores y pruebas. Revisar las filas de la matriz que correspondan.
3. Actualizar la prosa canónica y diagramas UML/flujo, con nombres reales y diferencias entre adaptadores. No copiar comportamientos propuestos como existentes.
4. Añadir al [REGISTRO_CAMBIOS.md](REGISTRO_CAMBIOS.md) fecha, motivo, archivos/contratos afectados y evidencia ejecutada o no disponible.
5. Ejecutar comprobaciones funcionales apropiadas al cambio. Para geometría ejecutar núcleo; para adaptadores/ZIP ejecutar Blender si está disponible; para UI verificar flujos relevantes. No afirmar pruebas no ejecutadas.
6. Regenerar los catálogos **después de revisar la explicación** y comprobar que no queda deriva:

   ```powershell
   python docs/Agents/Scripts/GenerarIndices.py
   python docs/Agents/Scripts/GenerarIndices.py --comprobar
   ```

7. Completar la descripción de cada archivo que el script informe como `Sin descripción en el inventario` editando su fila de `INVENTARIO.md`; el script conserva esas descripciones. Comprobar que cada parámetro canónico sigue en su tabla de [PARAMETROS.md](../BlenderPlugin/PARAMETROS.md).
8. Revisar diff de documentación y código juntos. La entrega debe incluir prosa, diagramas y catálogos coherentes.

## Qué hace el generador

- Inventaría archivos versionados y nuevos no ignorados (excluye `__pycache__`, el índice de CodeGraph y logs no versionados). Conserva las descripciones existentes; un archivo nuevo toma el primer renglón de su docstring o su título Markdown. Copia sin cambios la tabla de carpetas y la sección `.web/`.
- Extrae por AST, sin importar Reflex ni Blender, clases y funciones, incluidas privadas, anidadas y corrutinas, y escribe los tres `SIMBOLOS.md`: backend (`rxconfig.py`, `scripts/`, `src/`, `web/`), frontend (`rxconfig.py` y `web/Estado*`, `web/Pagina*`, `web/Sesion*`, `web/GenerateModelsApp.py`) y Blender (`GenerateModelsApp/`).
- Escribe `CONFIGURACION_GENERADA.md` con cada JSON de `GenerateModelsApp/config/`.
- Comprueba los enlaces relativos de `README.md` y `docs/`, salvo `docs/Audit/`, cuyos registros tienen ciclo propio.
- `--comprobar` no escribe y termina con 1 si algún catálogo cambiaría o hay enlaces rotos; sin esa opción termina con 1 solo por enlaces rotos.

No valida destinos externos, anclas, exactitud de la prosa, Mermaid ni equivalencia geométrica. Para CI, ejecutar solo `--comprobar`: regenerar automáticamente aceptaría cambios sin revisar su significado.

Los registros de `docs/Audit/` tienen revisión y ciclo de vida propios; se inventarían, pero no se reescriben como parte de estas áreas. Antes de editar fuentes, respetar los bloqueos de auditoría que establezca `AGENTS.md`; actualizar documentación no autoriza cambios en código bloqueado.
