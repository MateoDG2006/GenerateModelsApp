# Mantenimiento automático y revisión de documentación

## Contrato de las siguientes iteraciones

Las instrucciones persistentes están en [AGENTS.md](../../AGENTS.md). Todo agente que cambie lógica fundamental debe actualizar documentación **en la misma iteración**, sin esperar una petición documental adicional. Esto es parte de terminar el cambio de software.

La automatización tiene dos niveles: el agente/desarrollador actualiza las explicaciones por significado, y `scripts/VerificarDocumentacion.py` regenera hechos extraíbles y detecta deriva. Un script de hashes no puede comprender ni certificar que un algoritmo está explicado correctamente. No hay una tarea programada ni CI instalada por esta entrega; el procedimiento es local y queda listo para incorporarlo a CI.

## Qué cuenta como cambio fundamental

Cambiar geometría, sentido de normales, topología/recorte, patrón, escala, refinamiento, suavizado, espesores, validación, exportación o formato; añadir/eliminar parámetros o modificar límites/defaults; cambiar eventos/estado/carga/descarga/almacenamiento; nuevas pantallas o componentes; cambiar dependencias con efecto en compilación/protocolo; modificar registro, empaquetado o separación Blender/web.

El verificador usa huellas completas de fuentes y es deliberadamente conservador: también detecta cambios pequeños/comentarios. El agente decide y registra si no cambia el contrato. No existe un detector infalible de «fundamental».

## Matriz de impacto obligatorio

| Cambio | Documentos a revisar |
|---|---|
| `Modeling`, `Malla`, `Cascaron`, patrones, refinador, escala o borde | BlenderPlugin/ALGORITMOS, MODULOS, API_Y_DATOS; arquitectura backend y diferencias web/Blender |
| Defaults, límites, propiedades del panel | BlenderPlugin/PARAMETROS y CONFIGURACION_GENERADA; formularios frontend y contratos backend |
| `EstadoApp`, `GeneradorWeb`, `LectorSuperficie` | AppBackend/ARQUITECTURA, MODULOS, CONTRATOS, pruebas; flujos frontend |
| Página, componentes, binding, rutas o visor | AppFrontend/ARQUITECTURA, COMPONENTES_Y_FLUJOS, VISOR_3D y aceptación; contratos si cambian datos |
| Objeto, reparación, validación, exportación y registro Blender | BlenderPlugin/ARQUITECTURA, API_Y_DATOS, OPERACION_Y_PRUEBAS y guía breve LEEME |
| Dependencias, procesos o empaquetado | Operación de sistemas afectados, inventario, README y versión de la línea base |
| Archivos nuevos, eliminados o renombrados | Catálogo de responsabilidad y enlaces; inventario e índices generados |

## Secuencia obligatoria del agente/desarrollador

1. Leer instrucciones de repo. Si hay `.codegraph/`, consultarlo antes de localizar/entender código; no indexar por cuenta propia.
2. Identificar fuentes cambiadas, contratos, consumidores y pruebas. Revisar las filas de la matriz que correspondan.
3. Actualizar la prosa canónica y diagramas UML/flujo, con nombres reales y diferencias entre adaptadores. No copiar comportamientos propuestos como existentes.
4. Añadir al [REGISTRO_CAMBIOS.md](REGISTRO_CAMBIOS.md) fecha, motivo, archivos/contratos afectados y evidencia ejecutada o no disponible.
5. Ejecutar comprobaciones funcionales apropiadas al cambio. Para geometría ejecutar núcleo; para adaptadores/ZIP ejecutar Blender si está disponible; para UI verificar flujos relevantes. No afirmar pruebas no ejecutadas.
6. Regenerar hechos y aceptar la nueva línea base **después de revisar la explicación**:

   ```powershell
   python scripts/VerificarDocumentacion.py --actualizar
   python scripts/VerificarDocumentacion.py
   ```

7. Revisar diff de documentación y código juntos. La entrega debe incluir prosa, diagramas y artefactos generados coherentes; no limitarse a aceptar hashes para silenciar el fallo.

## Qué hace el verificador

- Inventaría archivos versionados y nuevos no ignorados, con propósito y carpetas generadas explicadas.
- Extrae por AST las clases/funciones/métodos, incluidos privados y anidados, sin importar Reflex ni Blender.
- Regenera índices `SIMBOLOS.md`, valores `CONFIGURACION_GENERADA.md` e `INVENTARIO.md`.
- Guarda huellas SHA-256 normalizando CRLF en fuentes textuales; detecta adiciones/eliminaciones/modificaciones del ámbito vigilado.
- Valida enlaces locales de Markdown, cierres de bloques, tipos de diagramas admitidos y presencia de cada parámetro canónico en su tabla.
- Devuelve código 1 si encuentra deriva; código 0 si las comprobaciones mecánicas pasan.

No valida destinos externos, anclas de encabezados, exactitud de la prosa, sintaxis completa/render de Mermaid ni equivalencia geométrica. `--actualizar` reemplaza únicamente archivos generados y manifiesto, no modifica código de producto, no corrige narrativas y no ejecuta pruebas.

El alcance de enlaces y diagramas son las tres carpetas de producto, `docs/Agents/` y el README directamente en `docs/`. Los registros de `docs/Audit/` tienen revisión y ciclo de vida propios; se inventarían si existen, pero no se reescriben ni se validan como parte de estas áreas. Antes de editar fuentes, respetar también los bloqueos de auditoría que establezca `AGENTS.md`; regenerar documentación no autoriza cambios en código bloqueado.

El ZIP del complemento se excluye de huellas porque es derivado; logs y resultado Blender históricos también. Assets fuente y fixture STL sí se vigilan. Agregar un documento cambia el inventario pero no implica que las fuentes cambien. Salidas ignoradas (`.web`, `.venv`, `.states`, subidas, logs, dist) quedan fuera de las huellas.

## Integración futura con CI

El comando de verificación usa solo biblioteca estándar Python y Git; puede ejecutarse antes de pruebas/build sin Blender ni Reflex. Añadir `python scripts/VerificarDocumentacion.py` como paso que deba pasar en CI permite impedir merges con deriva detectada. **No ejecutar `--actualizar` automáticamente en CI**: aceptaría cambios sin revisar su significado. Un bot/agente autorizado puede preparar la prosa y ejecutar la regeneración, dejando todo en el mismo diff revisable.
