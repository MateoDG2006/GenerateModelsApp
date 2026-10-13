# Operación y verificación del frontend

## Inicio y fuentes editables

Desde la raíz: `uv sync --locked`, luego `uv run reflex run`, siguiendo las skills de proceso del repositorio. Abrir `http://localhost:3000`. Cambios duraderos se hacen en `web/PaginaComparacion.py`, `web/EstadoApp.py`, `rxconfig.py` o `assets/visor.html`, según responsabilidad; no en React generado.

Antes de migrar Reflex comparar locks y documentación oficial con el código compilado actual. Esta base utiliza React Router/Vite; no describirla como una aplicación Next.js por referencias antiguas del framework. El archivo `GUIA_REFLEX.md` contiene enlaces generales, no evidencia de tecnologías utilizadas por cada versión.

## Matriz de aceptación

| Caso | Resultado esperado |
|---|---|
| Primera carga | Defaults, base incluida, placeholder sin modelo |
| Selección de archivo | Nombre visible; no sustituye base hasta pulsar Cargar |
| Archivo inválido o múltiple | Error visible; anterior base disponible; uploader se limpia |
| SOLID / retícula / liner / Voronoi | Visibilidad coincide con tabla de [componentes](COMPONENTES_Y_FLUJOS.md) |
| Decimal con coma / no finito | Adaptación servidor admite coma; dato inválido se informa al generar; soporte de edición depende del input del navegador |
| Una previsualización | Mensaje/progreso, una ficha, métricas y visor |
| Lote mixto con fallos | Filas válidas y erróneas; acciones de errores desactivadas; mensaje con conteo |
| Comparación | Máximo tres, clic repetido quita, cuarta rechazada; cámaras independientes |
| Descarga | Nombre y STL binario coherentes con ficha |
| Cámara | Arrastre rota; rueda acerca/aleja; resize mantiene encuadre |
| Cambio de tema | Componentes Reflex cambian; visor mantiene fondo claro propio |
| Pantalla estrecha | Revisar wrap, mínimos y scroll tabla; no asumir ausencia de overflow |
| Backend/CDN inaccesible | Distinguir evento sin respuesta de fallo de carga dentro del iframe |

## Evidencia y alcance de pruebas

Las 51 pruebas existentes de Python pasaron el 2026-10-13. Cubren núcleo, lectores, variantes y formato de salida, pero **no** son pruebas end-to-end del navegador, accesibilidad ni renderizado WebGL. No hay suite Playwright/Cypress implementada en el repositorio. Esta entrega de documentación no recompila ni modifica la aplicación Reflex.

`python scripts/VerificarDocumentacion.py` comprueba enlaces, referencias de archivos, índices generados, parámetros y huellas. No afirma que el diseño sea accesible ni que una captura corresponda al modelo. El [registro de cambios](../Agents/REGISTRO_CAMBIOS.md) separa evidencia ejecutada de procedimientos pendientes.

## Qué actualizar al cambiar UI

Cada pantalla nueva o cambio de binding requiere actualizar árbol de componentes, tabla evento/estado, reglas condicionales, recorrido de usuario y aceptación. Si cambia el visor, revisar contrato STL, controles, CDN y carga por URL. Si cambian parámetros o resultados, actualizar además AppBackend y BlenderPlugin según [MANTENIMIENTO.md](../Agents/MANTENIMIENTO.md).
