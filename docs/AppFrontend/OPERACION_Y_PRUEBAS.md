# Operación y verificación del frontend

## Inicio y fuentes editables

La interfaz necesita el backend completo: PostgreSQL, bucket S3, trabajador y proveedor OIDC, según [operación del backend](../AppBackend/OPERACION_Y_PRUEBAS.md). Luego `uv run reflex run`, siguiendo las skills de proceso del repositorio, y abrir `http://localhost:3000`. Con `--env prod` frontend, backend y `/auth/*` comparten el puerto 3000. Cambios duraderos se hacen en `web/PaginaComparacion.py`, `web/PaginaHistorial.py`, `web/Sesion.py`, `web/EstadoApp.py`, `web/EstadoHistorial.py`, `rxconfig.py` o `assets/visor.html`, según responsabilidad; no en React generado.

Antes de migrar Reflex comparar locks y documentación oficial con el código compilado actual. Esta base utiliza React Router/Vite; no describirla como una aplicación Next.js por referencias antiguas del framework. El archivo `GUIA_REFLEX.md` contiene enlaces generales, no evidencia de tecnologías utilizadas por cada versión.

## Matriz de aceptación

| Caso | Resultado esperado |
|---|---|
| Primera carga sin sesión | Defaults, base incluida, botón Iniciar sesión; generar muestra `Inicie sesión para continuar.` |
| Iniciar / cerrar sesión | Vuelve a `/` con nombre visible / sin datos del usuario anterior |
| Selección de archivo | Nombre visible; no sustituye base hasta pulsar Cargar |
| Archivo inválido o múltiple | Error visible; anterior base disponible; uploader se limpia |
| SOLID / retícula / liner / Voronoi | Visibilidad coincide con tabla de [componentes](COMPONENTES_Y_FLUJOS.md) |
| Decimal con coma / no finito | Adaptación servidor admite coma; dato inválido se informa al generar |
| Una previsualización | `En cola…`, una ficha, métricas y visor cargado desde la `object_url` |
| Recargar durante o después de generar | El último lote reaparece y su seguimiento continúa |
| Lote mixto con fallos | Filas válidas y erróneas; acciones de errores desactivadas; mensaje con conteo |
| Comparación | Máximo tres, clic repetido quita, cuarta rechazada; cámaras independientes |
| Descarga | `Content-Disposition: attachment`, STL binario coherente con la ficha |
| `/historial` | Filtrar, paginar, comparar 2–3 versiones con diferencias, restaurar y reintentar redirigen a `/` |
| STL borrado del bucket | El visor muestra `El STL ya no está en el almacén…` |
| Cámara | Arrastre rota; rueda acerca/aleja; resize mantiene encuadre |
| Cambio de tema | Componentes Reflex cambian; visor mantiene fondo claro propio |
| Pantalla estrecha | Revisar wrap, mínimos y scroll tabla; no asumir ausencia de overflow |

## Evidencia y alcance de pruebas

Las 73 pruebas de Python pasaron el 2026-10-13. Cubren núcleo, lectores, variantes, persistencia, propiedad de datos y trabajador, pero **no** son pruebas end-to-end del navegador, accesibilidad ni renderizado WebGL. No hay suite Playwright/Cypress en el repositorio.

El mismo día se recorrieron en navegador (Reflex en modo prod, PostgreSQL, Redis y OIDC de pruebas en Docker, `moto_server` en lugar de MinIO): rechazo sin sesión, inicio de sesión con cookie HttpOnly, previsualización con visor, recarga con recuperación del lote, descarga con evento registrado, lote de 2 patrones con progreso y comparación, `/historial` con filtro, comparación de 2 versiones y restauración, cierre de sesión que borra la pestaña y un segundo usuario con historial vacío. No se verificó la vista móvil; los iframes del visor muestran barras de desplazamiento.

El [registro de cambios](../Agents/REGISTRO_CAMBIOS.md) separa evidencia ejecutada de procedimientos pendientes.

## Qué actualizar al cambiar UI

Cada pantalla nueva o cambio de binding requiere actualizar árbol de componentes, tabla evento/estado, reglas condicionales, recorrido de usuario y aceptación. Si cambia el visor, revisar contrato STL, controles, CDN y carga por URL. Si cambian parámetros o resultados, actualizar además AppBackend y BlenderPlugin según [MANTENIMIENTO.md](../Agents/MANTENIMIENTO.md).
