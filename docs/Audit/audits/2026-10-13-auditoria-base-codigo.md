# AUD-2026-10-13-001 — Auditoría de la base de código

**Fecha:** 2026-10-13, America/Bogota. **Estado:** ABIERTA, sin resoluciones.
**Modo:** auditoría y definición de la regla de bloqueo; sin correcciones de producción.
**Revisión de partida:** `2b74669eb0cd3fc4b060168034b1a73db27ee9bf`, rama `master`.

## Resultado

Se identificaron **22 hallazgos**: **10 P1** y **12 P2**. No se confirmó un P0.
La ausencia de P0 no acredita ausencia de vulnerabilidades. Las 51 pruebas Python
existentes y la integración `blender_superficie_abierta.py` pasan, pero las
comprobaciones adicionales reproducen fallos que esas pruebas no detectan.

Los problemas de mayor impacto son la reserva de memoria inducida por cabeceras
NPZ, la aceptación de normales que producen volumen cero, vértices no manifold
aceptados por el validador, pérdida del resultado previo ante fallos de
reconstrucción y discrepancias entre la geometría comprobada y el STL exportado.
La web permite descargar geometría sin la validación final del complemento.

Todos los archivos del [inventario](2026-10-13-inventario.json) están
`PENDIENTE` y sujetos al bloqueo de [AGENTS.md](../../../AGENTS.md). No se ha
creado ningún resolve de cierre. La incorporación de esta regla es parte de la
solicitud inicial; no constituye una resolución de los hallazgos.

## Alcance, propósito y método

Se revisaron los **41 archivos Python versionados**: 33 de aplicación,
adaptadores, configuración y scripts; 8 de pruebas. También se revisaron el
visor HTML/JavaScript, los cuatro JSON de configuración, manifiestos, locks,
instrucciones, documentación de partida y artefactos versionados. El inventario
registra nombre, tamaño, SHA-256, categoría, motivo y hallazgos de cada archivo.

Se audita seguridad porque la web procesa STL/NPZ de usuarios y publica archivos;
corrección porque el núcleo genera geometría y calcula métricas; algoritmos
porque refinamiento, recorte, desplazamiento normal y búsqueda de semillas pueden
alterar topología o consumir recursos; duplicación y código muerto porque
divergencias entre Blender y web dificultan mantener un mismo contrato;
protocolos y estándares porque el resultado se intercambia entre NumPy, Reflex,
Blender, STL y JSON.

Se usó CodeGraph antes de localizar código, seguido de lectura de los módulos y
secciones que sus respuestas no incluyeron. Se contrastaron llamadas, pruebas,
configuración, estado Git y bytes del ZIP distribuido. Las búsquedas de `eval`,
`exec`, procesos externos, pickle y credenciales no mostraron una ruta propia de
ejecución remota de código ni secretos de aplicación evidentes; esto no sustituye
un escáner exhaustivo de secretos o dependencias.

### Criterios y límites

- **Reglas del proyecto:** `AGENTS.md`, separación Blender/web, unidades en mm,
  conservación de la base, superficie abierta/conectada/orientada, comprobación
  antes de exportar en Blender y distribución ZIP coherente con las fuentes.
- **Baseline adicional:** configuración validada, dependencias y estado con
  dueño, contratos tipados, documentación EPS —Entrada, Proceso, Salida—,
  pruebas y operaciones recuperables, de la skill `enforce-code-standards`.
  Las brechas EPS/tipado se señalan respecto de este baseline; no se afirma que
  el repositorio exigiera previamente EPS en todos sus símbolos.
- **CONFIRMADO:** demostrado por lectura inequívoca o reproducción controlada.
  **RIESGO:** consecuencia condicionada o hipótesis no reproducida completamente.
  **RECOMENDACIÓN:** mejora sugerida, sin afirmar que exista un fallo demostrado.
- P1: corrección, integridad o disponibilidad significativa; P2: confiabilidad,
  mantenibilidad, contratos o calidad. La prioridad no es una puntuación CVSS.
- No se instalaron dependencias, iniciaron servidores web ni modificaron fuentes
  de producción. Los ensayos se realizaron en procesos aislados y mallas sintéticas.
  Los resultados históricos versionados no se sustituyeron.
- `.venv`, `.web`, `dist`, `.states`, caches, logs operativos y subidas existentes
  no son fuentes canónicas y no se auditaron exhaustivamente. Se inspeccionó
  puntualmente código local de NumPy/Reflex para verificar dos mecanismos.
- El sketch `output/TestMicrofonoINMP441/TestMicrofonoINMP441.ino`, fuera de este
  repositorio, es un proyecto de audio independiente: no integra OrtesisLab y
  queda fuera de esta auditoría. No se afirma haber auditado el firmware.
- Durante la revisión aparecieron documentos no versionados en `docs/AppBackend`,
  `docs/BlenderPlugin`, `docs/README.md` y `docs/ESTANDAR_DOCUMENTACION.md`.
  Se preservaron; el estándar documental se leyó como contexto. No se congelan
  esos documentos concurrentes ni se atribuye su creación a esta auditoría.
  Cualquier documento o código que aparezca después del inventario requiere otra
  revisión; la auditoría no garantiza un estado futuro del árbol de trabajo.
  Más tarde aparecieron `docs/AppFrontend`, `docs/Agents`, índices, el nuevo
  `scripts/VerificarDocumentacion.py` e instrucciones de mantenimiento, mientras
  se trasladaban documentos antiguos y se ajustaba la ruta de la guía en el
  empaquetador. Ese trabajo concurrente tiene su propio registro en
  [resolves](../resolves/2026-10-13-reorganizacion-documental.md), sin cerrar
  hallazgos de código. El inventario conserva las huellas del commit de partida
  y la presencia/huella observada al registrar; no restaura documentos retirados.
  El nuevo verificador se leyó para seguir sus instrucciones y se ejecutó, pero
  no forma parte de los 41 Python de partida ni de la auditoría de su lógica.
  El nombre solicitado para esta carpeta es **`docs/Audit`**.

## Hallazgos priorizados

### A-01 · P1 · Cabeceras NPY permiten reservas ajenas al límite ZIP

**Estado:** CONFIRMADO, reproducción segura.
**Archivos y evidencia:** `web/LectorSuperficie.py:90–103`, especialmente 93–99;
NumPy local `numpy/lib/_format_impl.py:822–827, 859–862`.

`_Npz` limita la suma de `ZipInfo.file_size` y luego materializa los arrays con
`np.load`. Ese tamaño no valida que `shape × itemsize` de cada cabecera NPY
coincida con los bytes reales. Un ZIP de **197 bytes**, con un miembro NPY de
128 bytes que declara `(1_000_000_000, 3)` float64, llegó a solicitar
**24 000 000 000 bytes**. Se interceptó `numpy.ndarray` antes de reservarlos.
`allow_pickle=False` protege frente a pickle, pero no corrige este problema.

**Por qué/impacto:** una subida no confiable puede agotar memoria del proceso.
**Regla:** validar formato, dimensiones y presupuesto antes de materializar.
**Tratamiento y cierre:** inspeccionar cabeceras con límites, dtype/shape
permitidos, producto seguro, bytes esperados y consistencia del miembro ZIP;
procesar entradas hostiles en un proceso con recursos acotados. Regresión que
rechace el archivo pequeño **antes** de cualquier reserva grande. La guía de
[seguridad de NumPy](https://numpy.org/doc/stable/reference/security.html)
también identifica memoria y broadcasting como riesgos al procesar datos ajenos.

### A-02 · P1 · Las superficies descritas como privadas se guardan en el directorio servido

**Estado:** ubicación y ausencia de ACL CONFIRMADAS; acceso por terceros condicionado
al despliegue y conocimiento del nombre, sin ataque contra un servidor real.
**Archivos y evidencia:** `web/GeneradorWeb.py:185–219, 460–474`,
`web/EstadoApp.py:356–362`, `web/PaginaComparacion.py:383–387`, `rxconfig.py:3–15`.

`GuardarSuperficie` dice guardar una copia privada, pero `RutaSuperficie` devuelve
`rx.get_upload_dir()`. Reflex 0.9.12 monta ese directorio como `StaticFiles`
en `reflex/app.py:891–895`. El mismo almacenamiento contiene STL y NPZ originales
normalizados. La aplicación no implementa propiedad de archivo ni ACL por sesión;
la comprobación de la ficha en `Descargar` no protege la ruta estática.

**Por qué/impacto:** en un servicio compartido, quien obtenga una URL podría leer
una superficie ajena. Un UUID impredecible reduce descubrimiento; no establece
autorización. No se afirma que el despliegue actual sea público.
**Regla:** separar almacenamiento privado y descargas autorizadas.
**Tratamiento y cierre:** NPZ fuera del directorio público; asociar archivos a
sesiones/identidades y servir descargas con control de acceso. Verificar dos
sesiones y acceso directo sin autorización. El mecanismo de subidas se contrastó
con la [documentación oficial de Reflex](https://reflex.dev/docs/assets/upload-and-download-files/).

### A-03 · P1 · Faltan presupuestos de entrada, semillas, concurrencia y almacenamiento

**Estado:** ausencia de límites CONFIRMADA; agotamiento total no provocado.
**Archivos y evidencia:** `web/LectorSuperficie.py:21–23, 46–70, 114–125`,
`GenerateModelsApp/constants/Paterns.py:54–91, 101–108`,
`GenerateModelsApp/RefinadorMalla.py:43–63`, `web/EstadoApp.py:269–332`,
`web/GeneradorWeb.py:208–219, 245–247, 438–444`.

50 MiB de archivo y 128 MiB de expansión declarada no acotan intermediarios,
cantidad inicial de vértices/caras ni área de semillas. `max_surface_vertices`
solo impide añadir vértices en una ronda; no rechaza una entrada ya mayor ni
limita el cascarón final. Voronoi/HEX materializan semillas para toda la caja XY;
la selección local reduce cálculos posteriores, pero no esa lista. Sin
autoescala se admiten extensiones arbitrarias. Un cuadrado de 1 000 000 unidades
con celda 15 implica aproximadamente **5,13 mil millones de semillas**, por
estimación de área/paso, sin ejecutar esa carga.

El límite de 12 variantes es por lote; `_trabajando` es por estado de sesión.
`asyncio.to_thread` no introduce una cola global acotada, cancelación del cálculo
ni timeout. Nuevas superficies y STL permanecen en disco al cambiar de base o
crear lotes; no hay cuota, TTL ni limpieza.

**Por qué/impacto:** CPU, RAM, pool de trabajo y disco pueden agotarse.
**Regla:** operaciones largas acotadas, cancelables y con ciclo de vida.
**Tratamiento y cierre:** presupuestos antes de cargas/refinamiento/semillas,
límites de salida, cola de trabajos y recursos por sesión/proceso, cancelación
cooperativa o aislamiento, y retención que preserve archivos todavía en uso.
Ensayar entradas límite y varias sesiones con datos sintéticos acotados.

### A-04 · P1 · Normales NPZ finitas y unitarias pueden ser incompatibles con las caras

**Estado:** CONFIRMADO.
**Archivos y evidencia:** `web/LectorSuperficie.py:98–101`,
`GenerateModelsApp/Malla.py:61–64, 92–112`, `GenerateModelsApp/Cascaron.py:121–124`.

El NPZ aporta normales y el analizador comprueba longitud/finitud, sin contrastar
dirección con las normales geométricas. Una placa XY de 40 × 40 con normales
`(1,0,0)` pasa la entrada. `SOLID`, espesor 2, produce ocho vértices todavía
coplanares y volumen **0 mm³**; se acepta como construcción.

**Por qué/impacto:** una entrada aparentemente válida genera paredes colapsadas
y métricas erróneas. STL y Blender reconstruyen normales de caras, por lo que
el contrato diverge de NPZ.
**Regla:** misma validación geométrica en todos los formatos.
**Tratamiento y cierre:** recalcular normales de caras para NPZ, o validar
orientación y coherencia según un contrato explícito para normales de offset;
rechazar espesor colapsado. Añadir regresiones tangencial, opuesta y nula.

### A-05 · P1 · El control de aristas no detecta vértices no manifold

**Estado:** CONFIRMADO en Python y Blender 5.2.2.
**Archivos y evidencia:** `GenerateModelsApp/Malla.py:75–90, 114–124`,
`GenerateModelsApp/ValidacionMalla.py:22–39, 84–106`.

La preparación exige aristas con multiplicidad ≤2 y grado de contorno regular,
pero no un único abanico de caras por vértice. Aceptó un tetraedro y un triángulo
abierto unidos solo por el vértice 0. En salida, dos tetraedros unidos únicamente
por un vértice tienen una componente por aristas y cero aristas no manifold:
`Comprobar` devolvió **`ok=true`**, aunque BMesh contó **un vértice no manifold**.

**Por qué/impacto:** uniones puntuales y paredes no volumétricas pueden superar
la comprobación y alcanzar la exportación.
**Regla:** la topología válida incluye vecindades de vértices, no solo aristas.
**Tratamiento y cierre:** validar enlaces/abanicos en entrada y vértices manifold
en el sólido final. Conservar fixtures de ambas reproducciones y exigir rechazo.

### A-06 · P1 · El refinamiento devuelve éxito sin alcanzar el paso

**Estado:** CONFIRMADO con presupuesto reducido solo en memoria.
**Archivos y evidencia:** `GenerateModelsApp/RefinadorMalla.py:57–63, 119–148`,
`GenerateModelsApp/RefinadorMalla.py:16–23`, `web/GeneradorWeb.py:230–241`.

Cuando una ronda excedería el presupuesto, `detenida=True` omite el rechazo por
aristas demasiado largas. Con una placa 40 × 40, presupuesto de 4 vértices y
paso 5 mm, devuelve la placa original: arista máxima **56,5685 mm**, sin error.
El mensaje posterior sigue informando el paso solicitado, no el alcanzado.

**Por qué/impacto:** los campos de patrón y el recorte quedan submuestreados;
pueden faltar nervaduras o huecos. No se garantiza que reducir el paso aumente
el detalle cuando se alcanza el límite.
**Regla:** declarar las postcondiciones realmente obtenidas.
**Tratamiento y cierre:** devolver un resultado explícito de calidad insuficiente
o rechazar; no continuar silenciosamente. Verificar arista efectiva y métricas
de patrón cuando se detiene por presupuesto y cuando se agotan las rondas.

### A-07 · P1 · La descarga web omite validación final de la geometría

**Estado:** flujo CONFIRMADO; brecha funcional documentada por el proyecto.
**Archivos y evidencia:** `web/GeneradorWeb.py:223–260, 407–435`,
`web/EstadoApp.py:356–362`, `web/PaginaComparacion.py:355–360`.

`Crear` construye, calcula volumen y escribe STL; no verifica conectividad,
autointersecciones, degeneraciones o manifoldness del resultado. `Descargar`
entrega los bytes de cualquier ficha construida. La validación de la superficie
de entrada no acredita el sólido después del recorte y desplazamiento.

**Por qué/impacto:** se pueden descargar resultados defectuosos; las métricas y
la visualización no son una comprobación geométrica. La documentación distingue
esta capacidad de Blender, pero esa limitación no aporta una barrera de salida.
**Regla:** hacer explícito y verificable el contrato de salida de cada interfaz.
**Tratamiento y cierre:** validador independiente de Blender antes de publicar,
o una política explícita de resultado sin validar que bloquee su uso como
exportación validada. Probar piezas separadas, paredes colapsadas y cruces.

### A-08 · P1 · Blender comprueba la malla original y exporta la evaluada

**Estado:** CONFIRMADO con exportación real a un archivo sintético temporal.
**Archivos y evidencia:** `GenerateModelsApp/ValidacionMalla.py:78–81`,
`GenerateModelsApp/Exportacion.py:29–46`.

`Comprobar` usa `ob.data`; la exportación activa `apply_modifiers=True`.
Sobre un cubo con Array de dos copias separadas, el informe acepta una pieza y
12 triángulos. La malla evaluada contiene dos piezas, 24 triángulos y falla la
regla de componente única. Aun así se exportó el STL de **24 triángulos** con
un informe de **12**, `ok=true`. La prueba asignó `ol_config` sintético para
ejercitar la frontera pública; el mismo desajuste ocurre al añadir un
modificador a un resultado generado.

**Por qué/impacto:** el informe y el sidecar no corresponden a lo exportado.
La transformación del objeto también queda fuera del análisis local.
**Regla:** validar exactamente los bytes/geometría que se entregan.
**Tratamiento y cierre:** evaluar una sola instantánea con modificadores y
transformaciones, validar y exportar esa instantánea; o prohibir modificaciones
pendientes. Comprobar conteo y conectividad del STL reimportado. Véase
[evidencia detallada](2026-10-13-export-evidence.json).

### A-09 · P1 · Un fallo de reconstrucción ya ha sustituido el resultado anterior

**Estado:** CONFIRMADO con inyección controlada de fallo en Blender.
**Archivos y evidencia:** `GenerateModelsApp/Objeto.py:108–137, 150–194`,
`GenerateModelsApp/Interfaz.py:159–174`.

Se asigna `objeto.data=malla` y se elimina la malla anterior sin usuarios antes
de remesh, fragmentos y suavizado. Al inyectar `ReconstruccionFallida` en
`_AplicarModificador`, la operación falla pero la malla anterior ya fue eliminada
y los parámetros guardados son los del intento nuevo. El operador captura el
error; no implementa rollback del objeto. La base se conserva, el resultado
anterior no.

**Por qué/impacto:** pérdida del resultado previo y escena en estado parcial.
**Regla:** conservar originales hasta completar la operación.
**Tratamiento y cierre:** generar/reconstruir/validar en un objeto temporal y
sustituir al finalizar; liberar temporales al fallar. Regresiones de remesh,
fragmentación, suavizado y objeto homónimo ajeno, verificando identidad de la
malla previa y selección/visibilidad tras el fallo.

### A-10 · P2 · STL y JSON no se publican como un resultado consistente

**Estado:** CONFIRMADO por orden de operaciones; fallo de disco no provocado.
**Archivos y evidencia:** `GenerateModelsApp/Exportacion.py:38–59`,
`web/GeneradorWeb.py:438–444`.

Blender escribe el STL antes de interpretar `ol_config` y crear el JSON.
`json.loads` ocurre fuera del `try` que supuestamente captura su error. Un JSON
inválido o un fallo al escribir el sidecar deja un STL nuevo con metadatos
ausentes o antiguos. No se comprueba el estado retornado por el operador de
exportación. La escritura web también reemplaza el destino directamente.

**Por qué/impacto:** archivos parciales y asociación incorrecta de parámetros.
**Regla:** escrituras atómicas, errores estables y recuperación.
**Tratamiento y cierre:** validar metadatos antes de exportar, escribir temporales,
comprobar el operador y publicar con recuperación documentada para el par de
archivos. No afirmar que dos renombres son una transacción atómica. Ensayar fallo
del segundo archivo, cancelación y destino preexistente, preservando ambos originales.

### A-11 · P2 · Los límites aceptan cero, NaN, fracciones y relaciones inválidas

**Estado:** CONFIRMADO.
**Archivos y evidencia:** `GenerateModelsApp/util/Utilidades.py:214–228`,
`GenerateModelsApp/config/limites.json`, `GenerateModelsApp/constants/Paterns.py:60,72`.

`ValorLimite` comprueba que el valor sea numérico y no booleano, pero no finitud,
rango, integralidad ni relaciones. Con `pattern_batch=0` en una copia en memoria,
devuelve `0.0`; HEX termina en `ValueError: range() arg 3 must not be zero`.
Otros consumidores convierten fracciones a int silenciosamente.

**Por qué/impacto:** configuración aceptada que rompe algoritmos o anula controles.
**Regla:** configuración tipada y validada antes de usarla.
**Tratamiento y cierre:** schema por límite, conteos enteros positivos, tolerancias
positivas, ratios acotados y mínimo de escala ≤ máximo. Rechazar configuración
incorrecta al cargar; probar cada clase de límite con cero, NaN y fracciones.

### A-12 · P2 · Cachés globales no tienen invalidación coherente ni sincronización

**Estado:** estado global e invalidación ausente CONFIRMADOS; carrera entre sesiones
es un RIESGO no reproducido con tráfico simultáneo.
**Archivos y evidencia:** `web/GeneradorWeb.py:61–77, 81–97, 152–182`,
`GenerateModelsApp/Superficie.py:41–49, 168–179`,
`GenerateModelsApp/util/Utilidades.py:102, 166–168`.

La clave de refinamiento web contiene archivo, autoescala y paso, sin huella del
contenido ni configuración. `Configuracion.Recargar()` no invalida esos refinados;
Blender sí incluye límites y geometría en su clave. Las cachés se comparten entre
trabajos `to_thread` y las secuencias comprobar/insertar/evictar/devolver no tienen
protección. Se devuelven arrays reutilizables sin una política de inmutabilidad.

**Por qué/impacto:** geometría obsoleta, mutación accidental y posibles fallos de
evicción concurrente. Limitar entradas no limita su peso en memoria.
**Regla:** dueño, ciclo de vida e invalidación de estado compartido.
**Tratamiento y cierre:** servicio de caché acotado por bytes, resultados inmutables
o copias, clave por contenido/configuración y acceso sincronizado. Verificar
recarga de límites y tres trabajos concurrentes con evicción determinista.

### A-13 · P2 · El volumen cacheado no sigue cambios de la geometría pública

**Estado:** CONFIRMADO.
**Archivos y evidencia:** `GenerateModelsApp/Modeling.py:55–60, 200–215`.

`vertices` y `faces` son públicos y mutables. Tras cubicar un tetraedro
(1/6 mm³), multiplicar `vertices` por 2 y volver a calcular devuelve **1/6**,
en vez de **8/6 mm³**. La caché se invalida en algunas operaciones del modelo,
pero no ante una mutación directa; peso y precio heredan el error.

**Por qué/impacto:** métricas que no representan la geometría actual.
**Regla:** encapsular invariantes y derivados.
**Tratamiento y cierre:** geometría inmutable/revisionada, setters que invaliden
derivados o eliminar la caché si no es necesaria. Regresión de vértices y caras.

### A-14 · P1 · La dificultad de refinamiento puede cambiar el tamaño físico

**Estado:** comportamiento CONFIRMADO por código y tests; valoración de diseño
como RIESGO dimensional que requiere decisión del responsable.
**Archivos y evidencia:** `GenerateModelsApp/EscalaMalla.py:118–144, 174–190`,
`tests/test_escala_malla.py:42–81`, `web/GeneradorWeb.py:225–236`.

`Aplicar` puede probar una potencia menor cuando falla el paso, siempre que quede
en el rango plausible. El test de dimensión 800 espera reintentar de ×1 a ×0,1:
el resultado pasa de 800 a **80 mm** por dificultad computacional. El presupuesto
de vértices por sí solo no reduce la escala; el riesgo corresponde al fallo de
paso/rondas y a la elección de candidatos alcanzables. El modo macizo web usa
`Resolver`, mientras Blender siempre pasa por `Aplicar` con refinamiento.

**Por qué/impacto:** el detalle solicitado puede influir en la interpretación de
unidades y producir dimensiones distintas entre interfaces o patrones.
**Regla:** unidades determinadas por contrato, separadas del presupuesto de cálculo.
**Tratamiento y cierre:** decidir escala antes del refinamiento y mantenerla;
si no cabe, fallar o declarar calidad insuficiente. Si se conserva la heurística,
exigir una decisión explícita sobre sus dimensiones y documentar divergencias.
Probar que variar el paso no cambia dimensiones de una base ya en mm.

### A-15 · P2 · La conversión a float32 puede escribir infinitos en STL

**Estado:** CONFIRMADO con tres vértices sintéticos.
**Archivos y evidencia:** `web/GeneradorWeb.py:407–423`,
`GenerateModelsApp/Modeling.py:78–83, 96–102`.

Ser finito en float64 no garantiza ser representable en float32. `Stl` aceptó
un vértice con Z=`1e40` y escribió un infinito; solo emitió
`overflow encountered in cast`. Los parámetros de espesor no tienen un máximo
físico compartido y el serializador no comprueba el resultado de la conversión.

**Por qué/impacto:** un STL binario de longitud correcta puede ser ilegible o inválido.
**Regla:** validar en el tipo y formato de salida.
**Tratamiento y cierre:** límites físicos, validación de índices/finitud y
representabilidad antes y después del cast; rechazar sin publicar. Regresiones
de overflow, salida vacía, degeneraciones y round trip STL.

### A-16 · P2 · La fusión STL usa tolerancia en mm antes de corregir unidades

**Estado:** CONFIRMADO.
**Archivos y evidencia:** `web/LectorSuperficie.py:46–64, 114–125`,
`GenerateModelsApp/config/limites.json:21`.

La cuantización usa `clip_snap_mm=0.0001` sobre coordenadas crudas. Un triángulo
de lado `0.00004` tiene una corrección admitida ×1 000 000, hasta 40 mm, pero
sus vértices se fusionan antes de autoescalar y se rechaza como degenerado.
La tolerancia declarada en mm está actuando en unidades desconocidas.

**Por qué/impacto:** pierde topología y rechaza una base que la propia heurística
de escala podría interpretar; diferencias frente al NPZ con igual geometría.
**Regla:** tolerancias expresadas y aplicadas en la misma unidad.
**Tratamiento y cierre:** resolver unidades antes de soldar o convertir la
tolerancia a las unidades de entrada. Comparar STL/NPZ equivalentes en distintas
escalas sin modificar la conectividad antes de fijar las unidades.

### A-17 · P2 · Hay lógica duplicada y ramas inalcanzables

**Estado:** CONFIRMADO para duplicación y ramas; usos externos desconocidos.
**Archivos y evidencia:**

- `GenerateModelsApp/Malla.py:85–87, 94–96`: se recalculan grado y rechazo de
  vértices sueltos sin cambios intermedios en aristas/puntos; el segundo rechazo
  es inalcanzable tras pasar el primero.
- `GenerateModelsApp/Cascaron.py:38–39, 58–61`: con `clip_connect_mm=0.005`, todos
  los ceros se convierten en margen positivo; los casos `valores[a/b] == 0` ya
  no se alcanzan. Cambiar configuración podría alterar esa conclusión.
- `GenerateModelsApp/Cascaron.py:162–168` y `web/GeneradorWeb.py:426–435`:
  triangulación en abanico repetida en volumen y exportación.
- `GenerateModelsApp/Objeto.py:50–70` y
  `GenerateModelsApp/ValidacionMalla.py:22–39`: mismo recorrido de componentes
  por aristas con salida distinta, susceptible de compartir el mecanismo.
- `GenerateModelsApp/Interfaz.py:111–147`, `web/EstadoApp.py:26–42` y
  `GenerateModelsApp/config/parametros_defecto.json`: valores iniciales duplicados;
  la web los reemplaza al cargar, Blender conserva los literales.
- `GenerateModelsApp/Objeto.py:83–94` y `GenerateModelsApp/OrtesisLab.py:25–33`:
  coordinación de validar, determinar paso, leer y construir repetida.

`CATALOGO`, `Material.Costo` y algunos datos de catálogo no tienen consumidores
internos observados; son **candidatos a API residual**, no código muerto probado.
`ChangePattern`, `ChangePatern`, `Cascaron.Cerrar` y utilidades NPZ tienen usos
de compatibilidad o pruebas: no deben eliminarse solo por poco uso. La copia
`ReferenciaOriginal` es un oráculo de regresión intencional.

**Por qué/impacto:** reparaciones y cambios de contrato pueden divergir.
**Regla:** un criterio canónico por mecanismo, sin abstraer solo por simetría.
**Tratamiento y cierre:** extraer mecanismos con consumidores reales, retirar
ramas tras demostrar invariantes, derivar defaults y aclarar APIs públicas.
Verificar equivalencia y compatibilidad; no borrar candidatos sin evaluar usos externos.

### A-18 · P2 · Contratos y documentación EPS son incompletos

**Estado:** CONFIRMADO respecto del baseline adicional.
**Archivos y evidencia:** `GenerateModelsApp/Modeling.py:63,113,183`,
`GenerateModelsApp/Cascaron.py:24,102`, `web/GeneradorWeb.py:223,271–291`,
`GenerateModelsApp/Exportacion.py:50–55`, `src/generatemodelsapp/__init__.py:1–11`.

Los contratos centrales usan tuplas posicionales y diccionarios sin schema.
Opciones, fichas, NPZ normalizados, configuración en objeto y sidecar no incluyen
una versión de schema propia. La revisión AST de 33 Python de producción contó
226 funciones/métodos, **217 sin docstring con Entrada/Proceso/Salida**, y solo
63 con retorno y argumentos posicionales simples anotados. Las 73 clases y los
33 módulos no contienen EPS completo. Es un indicador de presencia de texto y
anotaciones, no una certificación semántica ni un análisis de todos los tipos.

**Por qué/impacto:** es difícil distinguir invariantes, errores y efectos;
cambios incompatibles pueden reutilizar estructuras antiguas silenciosamente.
El comando de consola depende de `scripts/` fuera del paquete `src`; su
funcionamiento en una wheel instalada queda sin verificar.
**Regla:** contratos tipados/versionados y documentación de frontera.
**Tratamiento y cierre:** DTO/schema para superficies, opciones, fichas y
validación; EPS primero en APIs públicas; versionado y errores de contrato.
Pruebas de compatibilidad NPZ/JSON y smoke test de wheel fuera del checkout.
No añadir clases que solo envuelvan diccionarios sin validar invariantes.

### A-19 · P2 · Las pruebas y los controles no cubren los fallos críticos de frontera

**Estado:** cobertura observada CONFIRMADA; porcentaje de cobertura no medido.
**Archivos y evidencia:** los ocho Python bajo `tests/`,
`pyproject.toml:1–23`, `AGENTS.md`, `tests/nucleo_ejecucion.log`.

Hay 51 casos Python y una integración Blender útil de nueve combinaciones,
preservación de canales/base, panel y reconstrucción. Sin embargo no hay E2E
de navegador ni controles versionados de CI, lint o tipos. Las pruebas no
detectan A-01, A-04, A-05, A-08 o A-09. El test de equivalencia de Voronoi
compara con una copia del algoritmo original: preserva comportamiento, pero no
valida de forma independiente su corrección geométrica.

Los tests comparten clases/cachés globales; algunos cambian configuración en
memoria y escriben subidas. `blender_paquete_zip.py:16–24` extrae sobre una
carpeta fija sin limpiarla: un archivo residual puede enmascarar una omisión del
ZIP. Los logs antiguos, incluido uno de 17 pruebas, son evidencia histórica.

**Por qué/impacto:** una suite verde no garantiza contratos de seguridad/salida.
**Regla:** verificaciones representativas, aisladas y reproducibles.
**Tratamiento y cierre:** regresiones de los P1, fixtures adversariales pequeñas,
E2E de carga/generación/descarga y dos sesiones; ZIP en carpeta temporal vacía;
pruebas metamórficas de geometría, CI y configuración explícita de lint/tipos.
No imponer una reorganización de carpetas sin beneficio demostrado.

### A-20 · P2 · Etiquetas visuales sin asociación programática explícita

**Estado:** omisión en fuente CONFIRMADA; árbol de accesibilidad no inspeccionado.
**Archivos y evidencia:** `web/PaginaComparacion.py:390–420`,
`assets/visor.html:98–112`.

`Campo` crea un label y un input hermanos sin `html_for/id`; `Interruptor` usa
texto hermano del switch y `Selector` texto separado del trigger sin asociación
explícita. El visor solo registra controles de puntero/rueda. No se observan
alternativas de teclado para rotación y zoom.

**Por qué/impacto:** riesgo de controles sin nombre accesible y operación limitada
para lectores de pantalla o teclado.
**Regla:** nombres accesibles y operación por teclado del baseline frontend.
**Tratamiento y cierre:** asociaciones estables o ARIA y controles de teclado;
verificar el DOM compilado, foco, nombre/rol/valor y navegación real. No se
afirma una auditoría completa de WCAG ni se midieron contraste o tamaños.

### A-21 · P2 · El visor confía en el contador STL y en una URL sin validar

**Estado:** falta de validación CONFIRMADA; bloqueo del navegador no provocado.
**Archivos y evidencia:** `assets/visor.html:15, 19–24, 55–86`.

`geometria` lee el contador en offset 80 y reserva `caras*9` float32 antes de
verificar longitud `84+50*caras`, límites o coordenadas. El parámetro `src`
acepta cualquier URL que `fetch` permita; un enlace al visor puede apuntar a
un archivo ajeno al generador. Un buffer corto produce excepción sin manejo
global que actualice el aviso. No es SSRF del servidor: el fetch es del navegador.

Además se importa Three.js desde un CDN externo fijando versión, pero fuera de
los locks del proyecto y sin copia local; el visor depende de ese suministro.
No se afirma una vulnerabilidad conocida de esa versión.

**Por qué/impacto:** reserva excesiva, visor inutilizable ante datos malformados y
fallo de disponibilidad sin CDN.
**Regla:** validar antes de reservar y hacer explícita la frontera de carga.
**Tratamiento y cierre:** validar origen/ruta admitida, tamaño/cantidad y finitud;
límite de descarga, AbortController y estado de error; empaquetar la dependencia
o controlar su integridad. Ensayar contadores falsos, buffer corto y fallo de red.

### A-22 · P2 · El filtro de normales interpreta distancias entre vectores como milímetros

**Estado:** uso dimensional CONFIRMADO por código; defecto visual concreto sin
cuantificar, pendiente de comparación contra una referencia geométrica.
**Archivos y evidencia:** `GenerateModelsApp/SuavizadoBorde.py:76–92, 140–170`.

`Aplicar` filtra posiciones con `_Pasabajos(coords, longitud_mm)`, pero reutiliza
la misma función para `normales_salida[bucle]`. `_Pasabajos` calcula perímetro
con distancias entre las filas recibidas: para normales unitarias ese perímetro
es adimensional y no representa la longitud física del contorno. La ganancia
también preserva siempre los dos primeros modos, cualquiera sea la longitud.

**Por qué/impacto:** el alisado de normales no corresponde al corte espacial de
8 mm que controla las posiciones; puede alterar offsets en curvas sin relación
con el tamaño de la pieza.
**Regla:** unidades explícitas y parametrización geométrica consistente.
**Tratamiento y cierre:** parametrizar ambos filtros por las longitudes del
contorno físico y renormalizar el campo vectorial. Ensayar el mismo campo normal
sobre contornos físicamente escalados y comparar con un filtro de referencia.

## Matriz de cumplimiento

| Área | Estado | Evidencia y alcance |
|---|---|---|
| Configuración y constantes | FAIL | A-11, A-17; JSON centrales presentes, sin schema de rango y con defaults repetidos |
| Separación de mecanismos | PARTIAL | Núcleo importable sin Blender; adaptadores separados; coordinación y utilidades aún mezclan responsabilidades |
| Compartidos/herramientas | PARTIAL | `util/Utilidades.py` concentra configuración y logging; A-17 recomienda extracción solo con consumidores reales |
| EPS | FAIL respecto del baseline adicional | A-18; conteo AST, sin atribuir una regla previa inexistente |
| Contratos, tipos y protocolos | FAIL | A-01, A-04, A-15, A-16, A-18 |
| Geometría/topología/algoritmos | FAIL | A-04 a A-08, A-14, A-22 |
| Estado, idempotencia y recuperación | FAIL | A-09, A-10, A-12, A-13 |
| Pruebas existentes | PASS en comandos ejecutados | 51 Python e integración Blender; no equivale a cobertura completa |
| E2E, lint, tipos y CI | NOT_VERIFIED / ausentes | A-19; herramientas y configuración no presentes, navegador no ensayado |
| Seguridad de entradas y recursos | FAIL | A-01, A-03, A-21 |
| Autorización de archivos | PARTIAL | A-02: ubicación/ACL observadas, despliegue real sin comprobar |
| Dependencias/CVE/licencias | NOT_VERIFIED | Locks presentes; no se ejecutó un escáner CVE/licencias ni revisión de todos los paquetes transitivos |
| Observabilidad | PARTIAL | Logger por subsistema y errores con traza; sin correlación por job, cuotas, cancelación ni progreso intravariante |
| Accesibilidad | PARTIAL | A-20, revisión de fuente; sin navegador o auditoría completa WCAG |
| ZIP instalable frente a fuentes | PASS | 27 miembros, CRC correcto, 26 Python/JSON coinciden byte por byte y LEEME coincide |
| Wheel/consola instalada | NOT_VERIFIED | Sin backend de build local, no se instaló software; riesgo descrito en A-18 |

## Inventario funcional: qué se auditó y por qué

Cada fila corresponde a código revisado. La ausencia de un hallazgo exclusivo
en una fila no cierra su revisión ni elimina el bloqueo. Las líneas exactas y
los símbolos de los hallazgos se complementan con las huellas del inventario JSON.

| Archivo desde la raíz | Qué se audita | Por qué se audita |
|---|---|---|
| [GenerateModelsApp/ApiBlender.py](../../../GenerateModelsApp/ApiBlender.py) | Importación y superficie pública de bpy/bmesh | Mantener el núcleo utilizable sin Blender y errores de entorno claros |
| [GenerateModelsApp/Cascaron.py](../../../GenerateModelsApp/Cascaron.py) | Recorte, cruces, cierre de bordes, volumen y validación | Evitar paredes colapsadas, topología inválida y volúmenes incorrectos |
| [GenerateModelsApp/EscalaMalla.py](../../../GenerateModelsApp/EscalaMalla.py) | Candidatos, presupuesto, reintentos y unidades | Evitar que un límite de cálculo cambie dimensiones físicas |
| [GenerateModelsApp/Excepciones.py](../../../GenerateModelsApp/Excepciones.py) | Jerarquía, mensajes, logging y detalles | Contratos de error, diagnóstico y efectos secundarios al construir errores |
| [GenerateModelsApp/Exportacion.py](../../../GenerateModelsApp/Exportacion.py) | Validación, operador STL y sidecar | Integridad entre malla, bytes y parámetros; recuperación de escrituras |
| [GenerateModelsApp/Interfaz.py](../../../GenerateModelsApp/Interfaz.py) | Ajustes, operadores, panel, excepciones y preferencias | Consistencia de defaults/rangos y transiciones de escena |
| [GenerateModelsApp/Malla.py](../../../GenerateModelsApp/Malla.py) | Índices, normales, manifoldness, conectividad y Dijkstra | Validar entradas y asegurar significado de distancia al contorno |
| [GenerateModelsApp/Modeling.py](../../../GenerateModelsApp/Modeling.py) | Parámetros, generación, patrones y métricas | Invariantes del modelo y coherencia de caché, geometría y material |
| [GenerateModelsApp/Objeto.py](../../../GenerateModelsApp/Objeto.py) | Sustitución, remesh, componentes y suavizado | Preservar resultados válidos y evitar estados parciales |
| [GenerateModelsApp/OrtesisLab.py](../../../GenerateModelsApp/OrtesisLab.py) | Registro/retiro y BuildGeometry | Ciclo de vida Blender y paridad con GeneradorObjeto |
| [GenerateModelsApp/RefinadorMalla.py](../../../GenerateModelsApp/RefinadorMalla.py) | Subdivisión, ocho máscaras, límites y paso final | Conservar orientación/conectividad y cumplir resolución solicitada |
| [GenerateModelsApp/ReparacionMalla.py](../../../GenerateModelsApp/ReparacionMalla.py) | Fusión, limpieza, componentes, validación y escritura | Evitar destrucción de la base ante fallos y operaciones compartidas |
| [GenerateModelsApp/SuavizadoBorde.py](../../../GenerateModelsApp/SuavizadoBorde.py) | Bucles, FFT, unidades, límites y caras volteadas | Conservar contornos y coherencia entre posiciones/normales |
| [GenerateModelsApp/Superficie.py](../../../GenerateModelsApp/Superficie.py) | NPZ local, lectura de escena, escala, huella y caché | Copias de trabajo correctas y fuentes actuales sin reutilización obsoleta |
| [GenerateModelsApp/ValidacionMalla.py](../../../GenerateModelsApp/ValidacionMalla.py) | Componentes, degeneraciones, aristas y cruces BVH | Que una comprobación válida represente el sólido exportado |
| [GenerateModelsApp/__init__.py](../../../GenerateModelsApp/__init__.py) | Metadata e importaciones tardías | Compatibilidad de versiones y carga sin dependencias de Blender |
| [GenerateModelsApp/constants/Materials.py](../../../GenerateModelsApp/constants/Materials.py) | Validaciones, densidad, coste y unidades | Coherencia de métricas y ausencia de valores no finitos |
| [GenerateModelsApp/constants/Nombres.py](../../../GenerateModelsApp/constants/Nombres.py) | Identificadores, roles, atributos y unidades | Contratos estables entre escena, configuración y exportación |
| [GenerateModelsApp/constants/Paterns.py](../../../GenerateModelsApp/constants/Paterns.py) | Catálogo, alias, campos XY y semillas | Corrección, complejidad, equivalencia y APIs residuales |
| [GenerateModelsApp/constants/__init__.py](../../../GenerateModelsApp/constants/__init__.py) | Declaración del paquete | Coherencia de módulos públicos y ausencia de efectos de importación |
| [GenerateModelsApp/util/Utilidades.py](../../../GenerateModelsApp/util/Utilidades.py) | Logging, lectura JSON, límites y recarga | Configuración válida, estado global y manejo de fallos |
| [GenerateModelsApp/util/__init__.py](../../../GenerateModelsApp/util/__init__.py) | Reexportación pública | Dependencias e interfaz compartida |
| [rxconfig.py](../../../rxconfig.py) | Entry point, plugins y configuración Reflex | Frontera de ejecución web y configuración de servicios |
| [scripts/EjecutarOrtesisLab.py](../../../scripts/EjecutarOrtesisLab.py) | Resolución de raíz e importación del complemento | Arranque reproducible sin fragmentos de paquete aislados |
| [scripts/EmpaquetarBlender.py](../../../scripts/EmpaquetarBlender.py) | Selección de archivos, CRC, respaldo y reemplazo | ZIP coherente sin bytecode, logs ni bases privadas |
| [scripts/IniciarConsola.py](../../../scripts/IniciarConsola.py) | Comando heredado y efectos observables | Distinguir saludo de arranque real del producto |
| [src/generatemodelsapp/__init__.py](../../../src/generatemodelsapp/__init__.py) | Main, sys.path e importación de scripts | Detectar dependencia del checkout al instalar una distribución |
| [web/EstadoApp.py](../../../web/EstadoApp.py) | Estado, uploads, eventos, jobs, fichas y descarga | Aislamiento, recuperación, validación y operaciones concurrentes |
| [web/GeneradorWeb.py](../../../web/GeneradorWeb.py) | Cachés, superficies, variantes, volumen, STL y rutas | Seguridad de archivos, presupuestos y consistencia de salida |
| [web/GenerateModelsApp.py](../../../web/GenerateModelsApp.py) | App, ruta y on_load | Enlace real de interfaz con estado y valores iniciales |
| [web/LectorSuperficie.py](../../../web/LectorSuperficie.py) | STL/NPZ, bytes, cabeceras, índices y normales | Frontera de entrada no confiable y preservación de topología |
| [web/PaginaComparacion.py](../../../web/PaginaComparacion.py) | Componentes, eventos, opciones, iframe y etiquetas | Contratos con estado, errores y accesibilidad desde fuente |
| [web/__init__.py](../../../web/__init__.py) | Límite de paquete web | Separación respecto del ZIP Blender |
| [assets/visor.html](../../../assets/visor.html) | Parser STL, fetch, dependencia CDN y controles | Reservas antes de validar, errores y operación por teclado |
| [tests/blender_paquete_zip.py](../../../tests/blender_paquete_zip.py) | Aislamiento ZIP y exportación | Evitar falsos positivos por archivos residuales; no ejecutado en esta revisión |
| [tests/blender_superficie_abierta.py](../../../tests/blender_superficie_abierta.py) | Nueve variantes, canales, base, edición y remesh | Integración geométrica Blender ejecutada en un proceso aislado |
| [tests/test_escala_malla.py](../../../tests/test_escala_malla.py) | Doce casos de unidades y reintentos | Contrastar comportamiento esperado con conservación dimensional |
| [tests/test_generador_web.py](../../../tests/test_generador_web.py) | Trece casos de lote, STL y carga | Cobertura de límites/formatos y huecos de seguridad |
| [tests/test_nucleo.py](../../../tests/test_nucleo.py) | Catorce casos de núcleo y oráculo original | Compatibilidad, validaciones y límites del oráculo compartido |
| [tests/test_refinador_malla.py](../../../tests/test_refinador_malla.py) | Tres casos de refinamiento y patrón abierto | Resolución alcanzada, recorte y unidades |
| [tests/test_suavizado_borde.py](../../../tests/test_suavizado_borde.py) | Cuatro casos de filtros y conservación del interior | Alcance de la verificación del borde y de las normales |
| [tests/test_superficie_abierta.py](../../../tests/test_superficie_abierta.py) | Cinco casos de espesor y rechazo de superficies | Invariantes topológicos y orientación de generación |

### Configuración, documentación y artefactos

| Archivos | Qué se audita y por qué |
|---|---|
| `GenerateModelsApp/config/parametros_defecto.json` | Las 17 claves, unidades, tipos y correspondencia con interfaces |
| `GenerateModelsApp/config/limites.json` | Umbrales, presupuestos y relaciones; detectar controles inválidos o inefectivos |
| `GenerateModelsApp/config/registro.json` | Niveles y destino de logs; frontera de configuración local confiable |
| `GenerateModelsApp/config/comprobacion_geometrica.json` | Referencia histórica, nunca certificación del resultado actual |
| `pyproject.toml`, `uv.lock`, `.python-version` | Dependencias, Python, entry point y política de resolución |
| `reflex.lock/package.json`, `reflex.lock/bun.lock` | Dependencias frontend resueltas; reproducibilidad, sin auditoría CVE/licencias completa |
| `AGENTS.md`, `CLAUDE.md`, `.agents/skills/*/SKILL.md`, `skills-lock.json` | Reglas aplicables, skills instaladas y trazabilidad de instrucciones |
| `README.md`, `docs/BACKEND.md`, `docs/FRONTEND.md`, `docs/LEEME.md` | Arquitectura, flujos, comandos y promesas contrastadas con implementación |
| `docs/GUIA_REFLEX.md` | Índice externo de contexto; no se verificaron todos sus enlaces ni se trató como contrato del producto |
| `.gitignore`, `.codegraph/.gitignore`, `.vscode/settings.json` | Fuentes canónicas, archivos ignorados y configuración de herramientas |
| `GenerateModelsApp.zip` | CRC, miembros, fuente distribuida y README, comparados byte por byte |
| `assets/superficie_interior_mm.npz` | Claves, dtype, dimensiones: 52 125 vértices, 102 878 caras; SHA-256. No se generaron todas las variantes de esta base real |
| `tests/Test.stl` | Fixture de 92 684 bytes que el test de carga procesa; identidad y contrato de entrada |
| `tests/*_ejecucion.log`, `tests/resultado_blender.json` | Procedencia y límites de resultados anteriores; no reemplazarlos por evidencia nueva |
| `assets/favicon.ico` | Inventario e identidad del recurso binario; sin lógica ejecutable propia, sin análisis forense del formato |

## Verificación ejecutada y evidencia

Entorno comprobado: **Python 3.14.3**, **NumPy 2.5.3**, **Reflex 0.9.12** y
**Blender 5.2.2 LTS**, build `d13f752e3b9c`. El intérprete del venv emitió un aviso
de ubicación de Python, pero los comandos terminaron correctamente. Blender
mostró avisos de caché de extensiones/permisos de usuario; no impidieron los tests.

| Comando/comprobación | Resultado |
|---|---|
| `git status --short`, `git rev-parse HEAD`, `git branch --show-current` | Árbol versionado limpio al iniciar; después aparecen documentos concurrentes y los archivos de esta entrega |
| Consultas CodeGraph y lectura dirigida | Revisados núcleo, adaptadores, web, scripts, pruebas y estándares; se completaron respuestas parciales del grafo |
| `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` | **PASS: 51 tests, 1,485 s, exit 0** |
| Blender `--factory-startup --background --python-exit-code 1`, wrapper que ejecuta `runpy.run_path('tests/blender_superficie_abierta.py')` | **PASS, exit 0**. Se redirigió la única escritura del JSON de prueba a un temporal, preservando el resultado versionado |
| Blender: vértice no manifold y fallo inyectado de modificador | **CONFIRMADOS** A-05 y A-09; JSON de resultados transcrito en evidencia |
| Blender: cubo con Array, comprobación original/evaluada y exportación STL | **CONFIRMADO** A-08; 12 frente a 24 triángulos y 1 frente a 2 componentes |
| Ensayos Python aislados, con patches restaurados al salir | **CONFIRMADOS** A-01, A-04, A-05, A-06, A-11, A-13, A-15, A-16 |
| Parser ASCII con tres líneas `vertex` y sin `solid/facet` | Aceptado; el lector es permisivo en gramática. Recomendación de contrato, sin inferir ejecución de código |
| AST de los 41 Python versionados | Todos parsean; conteos EPS/anotaciones de A-18; 292 funciones/métodos en total |
| ZIP: `ZipFile.testzip()`, nombres y comparación de bytes | **PASS**: 27 miembros, 26 fuentes/JSON iguales, `LEEME.md` igual |
| Lectura NPZ incluido con `allow_pickle=False` | Claves `vertices/normals/faces`, formas `(52125,3)/(52125,3)/(102878,3)`, dtypes float64/float64/int64 |
| `python scripts/VerificarDocumentacion.py --actualizar` y verificación posterior, con el nuevo script concurrente | **PASS**: 64 fuentes, 29 documentos, 13 diagramas; comprobación mecánica, sin auditar la lógica del nuevo verificador |
| Comprobación propia de `docs/Audit` | **PASS**: JSON válidos, enlaces locales, bloques Markdown, 22 IDs únicos, prioridades y 73 archivos pendientes; nombre físico `Audit` verificado |
| `tests/blender_paquete_zip.py` | Revisado, **NO EJECUTADO**. Se verificó el ZIP estáticamente y la exportación con otra reproducción; no atribuirle un PASS nuevo |
| Ruff, mypy, pytest, pip-audit, build, uv_build | No instalados en el venv. No se instalaron; no se ejecutaron lint, análisis de tipos, CVE, licencias o build de wheel |
| Navegador, HTTP desplegado, pruebas de carga masiva, hardware o impresora | **NO EJECUTADOS**; ninguna certificación clínica o de fabricación |

Los [resultados adicionales](2026-10-13-evidencias.json) son evidencia de fallos
observados, no pruebas de que estén corregidos. Las pruebas sintéticas no
almacenan datos personales ni modelos de pacientes.

### Reproducción segura de A-01

Desde la raíz, con el Python del venv. El patch intercepta la reserva: **no
eliminarlo para probar agotamiento de memoria**. La alteración dura solo el proceso.

```python
import io
import zipfile
from unittest.mock import patch
import numpy as np
from web.LectorSuperficie import LectorSuperficie

header = io.BytesIO()
np.lib.format.write_array_header_1_0(header, {
    "descr": "<f8", "fortran_order": False,
    "shape": (1_000_000_000, 3),
})
payload = io.BytesIO()
with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("vertices.npy", header.getvalue())

class ReservaInterceptada(Exception):
    pass

class NumpyProxy:
    def __getattr__(self, name):
        return getattr(np, name)

    def ndarray(self, count, dtype):
        print("bytes solicitados:", int(count) * np.dtype(dtype).itemsize)
        raise ReservaInterceptada()

with patch("numpy.lib._format_impl.numpy", NumpyProxy()):
    try:
        LectorSuperficie._Npz(payload.getvalue(), "header-only.npz")
    except ReservaInterceptada:
        print("Reserva bloqueada; vulnerabilidad reproducida sin asignación")
```

Es un detalle de NumPy 2.5.3: si cambia la implementación de `read_array`,
revisar el punto de interceptación antes de ejecutar el ensayo en otra versión.

### Reproducciones de geometría y estado

- **A-04:** crear NPZ con placa `(0,0,0), (40,0,0), (40,40,0), (0,40,0)`,
  caras `(0,1,2), (0,2,3)` y cuatro normales `(1,0,0)`; llamar
  `LectorSuperficie.Preparar(..., False)` y construir `SOLID`, espesor 2.
  `Cascaron.VolumenMm3` devuelve 0.
- **A-05, Blender:** dos tetraedros con vértice 0 compartido; vértices
  `(0,0,0), (10,0,0), (0,10,0), (0,0,10), (-10,0,0), (0,-10,0), (0,0,-10)`;
  caras `(0,1,2), (0,3,1), (0,2,3), (1,3,2), (0,4,5), (0,6,4), (0,5,6), (4,6,5)`.
  Comparar `sum(not v.is_manifold for v in bm.verts)` con `Comprobar(obj)['ok']`.
- **A-06:** misma placa 40 × 40, normales Z; patch de `ValorLimite` que devuelve
  4 solo para `max_surface_vertices`, delegando los demás límites al original;
  `Refinar(..., 5)` devuelve arista 56,5685. Restaurar el patch al salir.
- **A-08:** en Blender vacío, cubo de lado 10, propiedad `ol_config` con JSON
  sintético y modificador `ARRAY`, count 2, relative offset `(2,0,0)`;
  comparar `Comprobar(obj)` con una copia de la malla del depsgraph y exportar a
  un destino de prueba. El contador STL uint32 en byte 80 es 24, informe 12.
- **A-09:** construir una placa con `GeneradorObjeto.Crear`, conservar su mesh;
  en un segundo intento con `repair=True`, patch de `_AplicarModificador` que
  lanza `ReconstruccionFallida`; comprobar que ya cambió `obj.data` y se eliminó
  la malla antigua. Ejecutar solo en escena sintética de un proceso aislado.
- **A-11:** copiar caché/límites en un proceso aislado, asignar `pattern_batch=0`,
  comprobar `ValorLimite`, llamar a HEX y restaurar la caché. Se devuelve 0 y
  después falla `range`, sin `ConfiguracionInvalida`.
- **A-13:** tetraedro unitario, cubicar; multiplicar `modelo.vertices *= 2` y
  volver a cubicar; se reutiliza 1/6 en vez de 8/6.
- **A-15:** `GeneradorWeb.Stl([[0,0,0],[1,0,0],[0,1,1e40]], [[0,1,2]])`;
  comprobar los float32 del registro sin publicar el archivo.
- **A-16:** triangular STL de lado `0.00004` y normales Z, generado en memoria;
  `Resolver(0.00004)` propone ×1 000 000, pero `Preparar(..., True)` rechaza
  degeneración tras fusionar sus vértices antes de autoescalar.

## Orden de tratamiento propuesto

Este plan **no autoriza editar archivos bloqueados**. Cada corrección necesita
el procedimiento de `resolves`, autorización explícita cuando corresponda y
evidencia de cierre.

| Orden | Trabajo | Hallazgos | Comprobación de cierre | Dependencias |
|---|---|---|---|---|
| 1 | Blindar carga y presupuestos | A-01, A-03, A-11 | Cabeceras falsas, límites, cancelación y cuotas acotadas | Contratos de entrada |
| 2 | Separar almacenamiento privado y acceso | A-02 | Dos sesiones, ruta directa y retención | Identidad/propiedad definida |
| 3 | Asegurar normales, unidades y topología | A-04, A-05, A-06, A-14, A-16, A-22 | Fixtures adversariales y métricas de resolución/dimensiones | Entrada y configuración |
| 4 | Validar y publicar la geometría real | A-07, A-08, A-15 | Reimportar STL, comparar topología/conteos y tipo de salida | Validador compartido |
| 5 | Preservar originales y escrituras | A-09, A-10 | Fallos inyectados; resultado y archivos previos intactos | Instantánea de resultado |
| 6 | Encapsular derivados y cachés | A-12, A-13 | Recarga, mutación y concurrencia determinista | Revisión de contrato y ciclo de vida |
| 7 | Consolidar mecanismos/contratos | A-17, A-18 | Equivalencia, compatibilidad y wheel aislada | APIs explícitas |
| 8 | Ampliar controles y acceso al frontend | A-19, A-20, A-21 | CI, E2E, accesibilidad y parser/errores de visor | Fixtures y contratos estabilizados |

## Riesgos residuales y cuestiones no resueltas

La distancia de borde es Dijkstra sobre aristas, no la geodésica continua de
la superficie; depende de la triangulación. El patrón se proyecta a XY y su
anchura sobre paredes inclinadas varía, como reconoce el manual. El offset
normal sin control de curvatura/colisión puede autointersectar; la comprobación
BVH excluye pares que comparten vértices y no cubre todos los solapes coplanares.
Estos límites deben formar parte de los fixtures y criterios de salida; no se
presentan como capacidades certificadas del generador.

No se verificó exhaustivamente precisión de volumen para grandes traslaciones,
todos los ángulos/semillas, todas las máscaras de subdivisión con una referencia
independiente, ni variantes de máxima complejidad de la superficie incluida.
La retícula de semillas se ancla a los extremos del conjunto XY; la estabilidad
del patrón ante cambios de extensión requiere definir el comportamiento deseado.
No se eliminaron aliases, catálogo residual ni duplicaciones deliberadas de tests.

No se realizó pentest de red, escaneo CVE/licencias de todas las dependencias,
análisis forense de binarios o certificación de seguridad. No se asume que los
servicios estén expuestos a Internet. Las fuentes oficiales consultadas apoyan
el funcionamiento de las fronteras descritas; los hallazgos concretos se basan
en este código y sus reproducciones, no en una vulnerabilidad atribuida a NumPy,
Reflex, Blender o Three.js de forma general.

**Cambios de esta entrega:** `AGENTS.md` y nuevos registros bajo `docs/Audit/`.
El código de aplicación, pruebas, configuración y ZIP distribuido no fueron
corregidos por esta auditoría. La reorganización concurrente cambia la ruta
documental del empaquetador y tiene su propio registro, conservado sin ampliar
su autorización. Se ajustó la referencia a `Audit` en mantenimiento y se
registraron estas pruebas en el historial documental concurrente. Todos los
hallazgos y la revisión de cada archivo inventariado
permanecen pendientes de un resolve válido.
