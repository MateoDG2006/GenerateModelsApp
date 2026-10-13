# Contratos de AppBackend

## Eventos públicos de la página

| Evento | Entrada | Resultado observable / error |
|---|---|---|
| `CargarPredeterminados` | Carga de página | Valores JSON en formulario y dimensión de la base incluida |
| `set_*` | Cadena o booleano según campo | Actualiza formulario; generación posterior explícita |
| `CargarSuperficie` | Lista de exactamente un `rx.UploadFile` | NPZ normalizado, nombre y metadatos; limpia selección del uploader; si falla conserva la base anterior |
| `UsarSuperficieIncluida` | Ninguna | Nombre interno vacío, borra fichas/vistas/archivo actual; no elimina archivos de disco |
| `Previsualizar` / `PedirLote` | Parámetros actuales | Evento `Generar` en modo individual/lote |
| `Generar` | Instantánea de opciones y base | Fichas incrementales, primera válida visible, progreso y estado final |
| `Ver(id)` / `Comparar(id)` | ID de ficha del lote | Selecciona o alterna vista; cuarta comparación se rechaza con mensaje |
| `Descargar(id)` | ID de ficha del lote | Descarga de bytes STL; ID ausente o ficha sin archivo no hace nada |

No son endpoints REST documentados ni una API estable para terceros. Los nombres y el transporte corresponden al sistema de eventos Reflex.

## Entrada de geometría

La tupla compartida es `(vertices, faces, normals, border)`. Coordenadas y distancias en mm; `vertices` y `normals`: arrays float64 `(N,3)`; `faces`: enteros `(M,3)`; `border`: float64 `(N,)`. `border` mide caminos por aristas hasta el contorno, no distancia euclidiana al borde ni al plano XY.

Para un **NPZ externo** son obligatorias `vertices`, `faces`, `normals`. Para el **NPZ normalizado interno** se guarda además `border`. La base incluida también se prepara mediante `AnalizadorMalla`; no se confía en una distancia de borde antigua. El lector no usa pickle. Se exigen índices enteros válidos, normales finitas y no nulas, triángulos no degenerados/duplicados, orientación consistente, contornos regulares y una sola componente abierta.

Límites: 50 × 1024 × 1024 bytes de subida (50 MiB); 128 MiB de expansión declarada para NPZ. El texto de la UI dice MB. La selección cliente limita a un archivo y el servidor lo vuelve a comprobar. La lectura solicita como máximo límite + 1 byte. STL ASCII y binario se aceptan; las normales de STL se reconstruyen con áreas de triángulos. La cuantización de coincidencias usa `clip_snap_mm=0.0001` en las coordenadas que llegan, antes de la autoescala.

## Opciones y escala

Las 17 claves canónicas están en [PARAMETROS.md](../BlenderPlugin/PARAMETROS.md) y `config/parametros_defecto.json`. `_Numero` admite coma decimal y rechaza NaN/infinito. `_Opciones` convierte semilla a entero no negativo. El núcleo vuelve a validar opciones; incluso los campos ocultos deben conservar valores válidos.

`superficie_archivo=""` significa asset incluido. Un nombre guardado usa `superficie-<32 hex>.npz`. La autoescala es preferencia de ejecución, no clave del JSON geométrico. Guardar la base no hornea ese factor: cambiar la casilla afecta la próxima generación. En no macizo se usa `EscalaMalla.Aplicar` junto al refinamiento; en macizo web, `Resolver` sin refinamiento. Por esa diferencia, el aviso previo y la decisión definitiva pueden diferir en un caso donde intervenga el límite de rondas.

## Variantes y fichas

Rango: `desde + i*paso <= hasta`, inclusive si se alcanza exactamente. Paso > 0, números finitos y desde ≤ hasta. El barrido de `seed` exige enteros no negativos. El número de variantes se acota **antes** de materializar el rango. Cada patrón no macizo se duplica si se prueban ambas capas; `SOLID` no se duplica por capa. Campos no relevantes a un patrón todavía pueden producir variantes redundantes: no hay deduplicación geométrica.

Ejemplo: patrones `HEX` y `SQUARE`, celdas 10/15/20, con y sin capa → `2 × 3 × 2 = 12`. Añadir `SOLID` excedería el máximo con ese barrido. Ejes disponibles: `cell_mm`, `rib_width_mm`, `rib_height_mm`, `skin_mm`, `solid_mm`, `border_mm`, `rounding_mm`, `angle_deg`, `seed`, `reinforce_width_mm`, `reinforce_y_mm`.

```json
{
  "id": "1234abcd",
  "archivo": "ortesis-1234abcd.stl",
  "patron": "Hexagonal",
  "detalle": "Celda 15,0 mm · nervadura 2,80 × 1,40 mm · capa continua",
  "volumen": "1.000,0 mm³",
  "peso": "1,27 g",
  "precio": "0,19",
  "error": ""
}
```

Ejemplo ilustrativo de formato, no resultado medido. Todas las propiedades son cadenas. Una ficha fallida tiene ID, detalle y error, pero archivo/métricas vacíos. `Numero` usa punto de miles y coma decimal. No tratar estos textos formateados como datos científicos ni parsearlos para recalcular costes.

## Salida STL y material

STL binario: cabecera de 80 bytes, contador uint32 little endian y registros de 50 bytes (normal float32×3, tres vértices float32×3, atributo uint16). Los polígonos se triangulan en abanico. Longitud esperada: `84 + 50*T`. Se guarda con ocho caracteres de UUID: `ortesis-<id>.stl`. `Ruta` verifica longitud, prefijo y sufijo, pero no valida explícitamente que el ID sea hexadecimal; no documentar una garantía más fuerte.

La web no escribe el sidecar de Blender ni llama `ValidadorMalla`. Volumen: suma orientada de tetraedros del cascarón, en valor absoluto. PETG: densidad 1.27 g/cm³, precio 0.15 por gramo; peso = volumen_mm³ × 1.27 / 1000, precio = peso × 0.15. No hay moneda declarada, soportes, relleno, merma, tiempo de máquina ni mano de obra.

## Errores y efectos laterales

`ValueError` cubre parseo y barrido; `OrtesisLabError` cubre dominio y configuración. Ambos se muestran como errores previstos. Excepciones inesperadas se registran con traza. En un lote cada variante falla de manera aislada; los STL ya escritos quedan en disco aunque otra variante falle. No hay rollback ni limpieza automática.

Las rutas se restringen a nombres internos, pero no hay ACL de archivos por sesión. El diccionario de fichas solo limita las acciones de UI de la sesión. Para exponer el servicio fuera de un entorno controlado se requiere diseñar control de acceso y cuotas; esa infraestructura aún no está implementada. Referencia del soporte de archivos: [Reflex upload/download](https://reflex.dev/docs/assets/upload-and-download-files/).
