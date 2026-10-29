# Contratos de AppBackend

## Eventos públicos de la página principal (`/`)

Todos los eventos que leen o escriben datos resuelven primero el usuario desde la cookie `ortesislab_sesion`. Sin sesión válida muestran `Inicie sesión para continuar.` y no crean filas ni objetos.

| Evento | Entrada | Resultado observable / error |
|---|---|---|
| `CargarPredeterminados` | Carga de página | Valores JSON en formulario, mensaje `Listo para generar…`, preferencia de autoescala guardada, último lote del usuario y reanudación de su seguimiento si sigue abierto; si cambió el usuario de la pestaña, borra el trabajo anterior |
| `set_*` | Cadena o booleano según campo | Actualiza formulario; `set_autoescalar_superficie` además guarda la preferencia y ante conflicto de revisión recarga la guardada |
| `CargarSuperficie` | Lista de exactamente un `rx.UploadFile` | Import del usuario: original y NPZ en el bucket, nombre `superficie-<32 hex>.npz` y metadatos; si falla conserva la base anterior |
| `UsarSuperficieIncluida` | Ninguna | Nombre interno vacío (plantilla), borra fichas/vistas/archivo actual |
| `Previsualizar` / `PedirLote` | Parámetros actuales | Nuevo `request_id` y evento `Generar` en modo individual/lote |
| `Generar` | Instantánea de opciones y base | Lote persistido; progreso cada segundo, fichas de los ítems terminados y estado final |
| `SeguirLote` | `lote_id` actual | Reanuda la lectura del progreso de un lote abierto |
| `CancelarLote` | `lote_id` actual | Pide la cancelación; los ítems en cola pasan a `cancelled` y el trabajador detiene el que corre entre etapas |
| `Ver(id)` / `Comparar(id)` | ID de ficha del lote | Selecciona o alterna vista; cuarta comparación se rechaza con mensaje |
| `Descargar(id)` | ID de ficha del lote | Registra `export_downloaded` y descarga desde la `object_url`; ID ausente o ficha sin archivo no hace nada |

## Eventos de `/historial`

| Evento | Entrada | Resultado |
|---|---|---|
| `Cargar` | Carga de página o botón Filtrar | Primera página (25 filas) de versiones del usuario con los filtros actuales, más recientes primero; borra la selección |
| `set_filtro_*` | Patrón, estado, desde, hasta | Guarda el filtro; se aplica con Filtrar. Fechas `AAAA-MM-DD` en UTC: `desde` a las 00:00 y `hasta` hasta el final del día |
| `Siguiente` / `Anterior` | Ninguna | Cursor `(created_at, id)`; no usa OFFSET |
| `Seleccionar(version_id)` | ID de versión | Alterna selección; con 2 o 3 versiones muestra tarjetas con diferencias de parámetros; la cuarta se rechaza |
| `Restaurar(version_id)` | ID de versión | Lote `single` con una versión nueva de mismos parámetros, autoescala y `parent_version_id`; la original no cambia; redirige a `/` |
| `Reintentar(version_id)` | ID de versión | Lote `retry` que crea intentos nuevos para la misma versión; redirige a `/` |
| `Descargar(fila_id)` | ID de fila | Igual que la descarga principal |

No son endpoints REST documentados ni una API estable para terceros. Los nombres y el transporte corresponden al sistema de eventos Reflex. Las rutas HTTP propias son `/auth/login`, `/auth/callback` y `/auth/logout`.

## Entrada de geometría

La tupla compartida es `(vertices, faces, normals, border)`. Coordenadas y distancias en mm; `vertices` y `normals`: arrays float64 `(N,3)`; `faces`: enteros `(M,3)`; `border`: float64 `(N,)`. `border` mide caminos por aristas hasta el contorno, no distancia euclidiana al borde ni al plano XY.

Para un **NPZ externo** son obligatorias `vertices`, `faces`, `normals`. Para el **NPZ normalizado interno** se guarda además `border`. La plantilla incluida se prepara mediante `AnalizadorMalla` y se registra como import propio de cada usuario la primera vez que la usa. El lector no usa pickle. Se exigen índices enteros válidos, normales finitas y no nulas, triángulos no degenerados/duplicados, orientación consistente, contornos regulares y una sola componente abierta.

Límites: 50 × 1024 × 1024 bytes de subida (50 MiB); 128 MiB de expansión declarada para NPZ. El texto de la UI dice MB. La selección cliente limita a un archivo y el servidor lo vuelve a comprobar. STL ASCII y binario se aceptan; las normales de STL se reconstruyen con áreas de triángulos. La cuantización de coincidencias usa `clip_snap_mm=0.0001` en las coordenadas que llegan, antes de la autoescala. Un mismo original (mismo SHA-256) del mismo usuario reutiliza el import existente.

## Opciones y escala

Las 17 claves canónicas están en [PARAMETROS.md](../BlenderPlugin/PARAMETROS.md) y `config/parametros_defecto.json`. `_Numero` admite coma decimal y rechaza NaN/infinito. `_Opciones` convierte semilla a entero no negativo. El núcleo vuelve a validar opciones; incluso los campos ocultos deben conservar valores válidos.

`superficie_archivo=""` significa plantilla incluida. Un nombre guardado usa `superficie-<32 hex>.npz`, donde el hex es el `asset_id` del NPZ normalizado del usuario. La autoescala es preferencia del usuario (`user_preferences.auto_scale_surface`) y se copia a cada versión; no es clave del JSON geométrico. En no macizo se usa `EscalaMalla.Aplicar` junto al refinamiento; en macizo web, `Resolver` sin refinamiento.

## Variantes, lotes y fichas

Rango: `desde + i*paso <= hasta`, inclusive si se alcanza exactamente. Paso > 0, números finitos y desde ≤ hasta. El barrido de `seed` exige enteros no negativos. El número de variantes se acota **antes** de materializar el rango. Cada patrón no macizo se duplica si se prueban ambas capas; `SOLID` no se duplica por capa. No hay deduplicación geométrica.

Ejemplo: patrones `HEX` y `SQUARE`, celdas 10/15/20, con y sin capa → `2 × 3 × 2 = 12`. Ejes disponibles: `cell_mm`, `rib_width_mm`, `rib_height_mm`, `skin_mm`, `solid_mm`, `border_mm`, `rounding_mm`, `angle_deg`, `seed`, `reinforce_width_mm`, `reinforce_y_mm`.

`SolicitudLote` contiene `import_id`, `request_id` (UUID por clic), `mode` (`single`, `batch`, `retry`), `definition`, `variantes` (máximo 12) y `auto_scale`. Repetir el mismo `request_id` con el mismo cuerpo devuelve el lote existente; con otro cuerpo falla con `SolicitudIdempotenteEnConflicto`. Un usuario puede tener 3 lotes pendientes; el cuarto falla con `CuotaExcedida`.

| Estado | Valores |
|---|---|
| Lote | `queued`, `running`, `succeeded`, `partial`, `failed`, `cancelled` |
| Ítem / versión visible | `queued`, `running`, `succeeded`, `failed`, `cancelled` |
| Asset | `staged`, `ready`, `quarantined`, `missing`, `deleting`, `deleted` |

```json
{
  "id": "1234abcd",
  "archivo": "http://127.0.0.1:9000/ortesislab/usuarios/<user_id>/assets/<asset_id>.stl",
  "patron": "Hexagonal",
  "detalle": "Celda 15,0 mm · nervadura 2,80 × 1,40 mm · capa continua",
  "volumen": "1.000,0 mm³",
  "peso": "1,27 g",
  "precio": "0,19",
  "error": ""
}
```

Ejemplo ilustrativo de formato, no resultado medido. Todas las propiedades son cadenas. `archivo` es la `object_url` del STL. Una ficha fallida tiene ID, detalle y error, pero archivo/métricas vacíos. `Numero` usa punto de miles y coma decimal. No parsear estos textos para recalcular costes: los valores numéricos están en `generation_results`.

## Bucket S3

| Objeto | Clave | Lectura |
|---|---|---|
| Original subido | `usuarios/<user_id>/assets/<asset_id>` | Solo backend |
| NPZ normalizado | `usuarios/<user_id>/assets/<asset_id>` | Solo backend |
| JSON de parámetros del resultado | `usuarios/<user_id>/assets/<asset_id>` | Solo backend |
| STL de resultado | `usuarios/<user_id>/assets/<asset_id>.stl` | Anónima por URL (`infra/database/minio/politica-lectura-stl.json`) |

`object_url = ORTESISLAB_S3_PUBLIC_URL/<bucket>/<clave>`. Cada objeto lleva el metadato `sha256`; el backend verifica tamaño y hash antes de marcar la fila `ready` y al leerla. `GeneradorWeb.Ruta` acepta solo una `object_url` de un STL del usuario activo.

## Salida STL y material

STL binario: cabecera de 80 bytes, contador uint32 little endian y registros de 50 bytes (normal float32×3, tres vértices float32×3, atributo uint16). Los polígonos se triangulan en abanico. Longitud esperada: `84 + 50*T`. Nombre de descarga: `ortesis-<8 hex del asset>.stl`.

La web no escribe el sidecar de Blender ni llama `ValidadorMalla`. Volumen: suma orientada de tetraedros del cascarón, en valor absoluto. PETG: densidad 1.27 g/cm³, precio 0.15 por gramo; peso = volumen_mm³ × 1.27 / 1000, precio = peso × 0.15. La versión guarda una instantánea de esos valores. No hay moneda declarada, soportes, relleno, merma, tiempo de máquina ni mano de obra.

## Errores y efectos laterales

| Error | Mensaje/uso |
|---|---|
| `SesionInvalida` | `Inicie sesión para continuar.` |
| `PersistenciaNoDisponible` | Base no disponible; no se crea trabajo |
| `AlmacenamientoNoDisponible` / `ObjetoAusente` | Bucket no disponible / objeto borrado o alterado |
| `AccesoDenegado` | Recurso inexistente o de otro usuario (misma respuesta) |
| `SolicitudIdempotenteEnConflicto`, `CuotaExcedida`, `ConflictoRevision` | Admisión y preferencias |
| `ValueError`, `OrtesisLabError` | Parseo, barrido, dominio y configuración: fallo previsto del ítem |

En un lote cada ítem falla de manera aislada y se reintenta hasta 3 veces. Los objetos subidos de un intento que no confirma quedan `staged` y los borra el conciliador. Toda acción relevante deja una fila en `history_events` (`import_received`, `import_ready`, `import_rejected`, `version_created`, `batch_queued`, `batch_cancel_requested`, `batch_finished`, `attempt_started`, `attempt_failed`, `attempt_abandoned`, `result_ready`, `export_downloaded`, `project_archived`). Referencia del soporte de descargas: [Reflex upload/download](https://reflex.dev/docs/assets/upload-and-download-files/).
