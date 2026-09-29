# Backend de OrtesisLab

El núcleo construye la geometría de una ortesis a partir de una superficie interior abierta, en milímetros. Cambia el patrón, los espesores y el contorno. No predice resistencia ni ajuste sobre una persona.

Ese núcleo lo usan dos interfaces:

- El complemento de Blender carga la malla, reconstruye, comprueba y exporta. No calcula coste.
- La aplicación Reflex permite cargar una superficie, generar diseños, valorar el material y comparar variantes.

La parte de Blender solo funciona dentro de Blender 5.x. El patrón, el cascarón, los parámetros, el volumen y el material se importan sin Blender. El peso usa la densidad del material; no es el filamento medido por una impresora.

## Mapa de módulos

| Módulo | Responsabilidad |
|---|---|
| `scripts/EjecutarOrtesisLab.py` | Script: arranca el complemento dentro de Blender. |
| `scripts/IniciarConsola.py` | Script: saludo del comando de consola. |
| `OrtesisLab.py` | `register` y `unregister`, que Blender llama por ese nombre, y `Complemento`. |
| `Interfaz.py` | Ajustes, operadores y panel N. |
| `Superficie.py` | Lee una copia de la superficie seleccionada y usa `RefinadorMalla` para subdividirla sin cerrar contornos. Conserva la carga de NPZ como utilidad explícita. |
| `RefinadorMalla.py` | Refinamiento compartido por Blender y la web, incluido el paso adaptado al patrón. |
| `ReparacionMalla.py` | Clase `ReparadorMalla`: limpia una superficie seleccionada sin añadir espesor ni cerrar aberturas. |
| `EscalaMalla.py` | Clase `EscalaMalla`: detecta dimensiones fuera de rango y propone una corrección decimal de unidades. |
| `Objeto.py` | Clase `GeneradorObjeto`: crea `OL_Ortesis` y reconstruye. |
| `ValidacionMalla.py` | Clase `ValidadorMalla`. |
| `Exportacion.py` | Clase `ExportadorStl`. |
| `Modeling.py` | Clase `Model3DForPrinting`. |
| `Malla.py` | Clase `AnalizadorMalla`. Sin Blender. |
| `Cascaron.py` | Clase `Cascaron`: recorte, cierre y volumen. |
| `constants/Paterns.py` | Clase `Patron` y el catálogo. |
| `constants/Materials.py` | Clase `Material` y `PETG`. |
| `constants/Nombres.py` | Nombres de objetos y propiedades. |
| `util/Utilidades.py` | Clases `Registro` y `Configuracion`. |
| `Excepciones.py` | Un error por casuística. |
| `ApiBlender.py` | Única puerta de `bpy`. |

`web/GenerateModelsApp.py` arranca Reflex fuera del paquete de Blender. La página llama al núcleo para construir el cascarón y valorar el material; no abre Blender ni aplica el voxel.

El esqueleto `3DModelForPrinting` no era un identificador válido en Python. La clase es `Model3DForPrinting`. El método conserva el nombre `change_patern`; `change_pattern` hace lo mismo.

## Flujo al pulsar Generar

1. Se usa la superficie elegida en el panel o la malla activa. No se busca automáticamente la superficie v5 ni su NPZ.
2. Se rechaza una malla que no sea de tipo MESH, con modificadores sin aplicar, con escala distinta de 1 o sin caras.
3. Se exige una superficie abierta y conectada, sin caras duplicadas/degeneradas, con orientación consistente y normales finitas. Los vértices sueltos siempre se rechazan. Se leen las caras y normales actuales, sin caché de sumas ni atributos antiguos de offset.
4. Se validan parámetros contra los JSON. Una copia se subdivide según `surface_step_mm`, limitada además por ancho y tamaño de celda; la malla original no cambia.
5. El patrón calcula la distancia al eje en la proyección XY. El marco y la banda maciza ensanchan esa zona.
6. Con capa interior se varía el espesor. Sin ella se recorta la superficie. En macizo el espesor es uniforme.
7. `Cascaron.Engrosar` duplica las caras y une cada borde únicamente con su copia. No rellena contornos ni conecta labios opuestos. `flip_normals` invierte normales y orientación de caras; `Cerrar` sigue siendo un alias compatible.
8. Si la reconstrucción está activa y el voxel queda por debajo de 0,15 mm, se aborta antes de crear la malla.
9. Solo si se activa `repair` se aplica voxel (desactivado por defecto). Puede alterar aberturas estrechas. Si las piezas separadas superan el umbral (50 vértices o el 0,5 %, el que sea mayor), se aborta. Los restos pequeños se eliminan y se suaviza.
10. La comprobación y la exportación son pasos aparte. Exportar un STL con la malla en mal estado está bloqueado.

## Configuración

| Archivo | Uso |
|---|---|
| `config/parametros_defecto.json` | Valores iniciales de patrón, celda, nervadura, capa, marco, semilla y resolución. |
| `config/limites.json` | Mínimo de celda, relación de ancho, voxel, fragmentos, tolerancia del recorte y límite de caché de refinamiento de Blender. |
| `config/registro.json` | Nivel de la consola, nivel del archivo y nombre del log. |
| `config/comprobacion_geometrica.json` | Resultado ya medido de los dos ejemplos. No son umbrales: si faltan sus claves, la lectura de referencia falla. |

Los JSON se leen una vez y se reutilizan. `Configuracion.Recargar()` vuelve a disco. Un archivo ausente, mal formado o con claves de más o de menos lanza `ConfiguracionInvalida` y no sigue con valores a medias.

Blender y la web aplican el mismo refinamiento y calculan las normales de caras con el mismo criterio. Blender conserva hasta dos superficies refinadas; la clave incluye la geometría original, su escala y la configuración. La web conserva hasta dos superficies originales y dos refinadas. Cambiar parámetros del patrón sobre una base ya refinada evita repetir esa etapa. La generación sigue siendo una operación explícita: todavía no hay vista previa continua mientras se arrastra un control.

El ZIP instalable se genera con `scripts/EmpaquetarBlender.py`. El paquete solo incluye código fuente Python, JSON y `LEEME.md`; no debe incluir `__pycache__` ni bytecode de otra versión de Python. Tras cambiar el código fuente hay que volver a generar e instalar el ZIP para que Blender use la versión actual.

## Patrones y material

| Código | Clase | Geometría |
|---|---|---|
| `VORONOI` | `Voronoi` | Semillas hexagonales desplazadas con la semilla. |
| `HEX` | `HoneyComb` | La misma retícula, sin desplazamiento. |
| `DIAMOND` | `Diamond` | Rombos sobre la cuadrícula girada 45°. |
| `SQUARE` | `Square` | Distancia a la cuadrícula. |
| `SOLID` | `Solid` | Espesor uniforme, sin nervaduras. |
| — | `Triangle` | Solo catálogo. Pedirla para generar es un error. |
| — | `Minimalistic` | Solo catálogo. Pedirla para generar es un error. |

`ChangePatern` acepta el código (`HEX`) o el nombre (`HoneyComb`, `macizo`, `rombos`).

PETG conserva densidad 1,27 g/cm³, precio 0,15, color negro, tipo filamento y marca Prusament. El precio se trata como **precio por gramo**. El volumen en mm³ pasa a gramos como `volumen / 1000 * densidad`. Ese peso es el del cascarón anterior a la reconstrucción voxel, no el filamento que gastará la impresora.

## Registro

`Registro.Obtener("superficie")` escribe en el registrador `ortesislab.superficie`. La consola sale en INFO. El archivo `GenerateModelsApp/logs/ortesislab.log` guarda también DEBUG. La carpeta `logs/` no se versiona.

Cada error previsto se escribe al construirse, con el nombre de la clase y, cuando hace falta, un detalle que no se muestra en el panel (rutas probadas, escala leída, vértices de un fragmento). Los fallos no previstos de los operadores quedan con traza completa.

## Errores por casuística

| Situación | Error |
|---|---|
| Falta el npz y no está la superficie en la escena | `ArchivoSuperficieNoEncontrado` |
| El npz no se puede leer | `ArchivoSuperficieIlegible` |
| El objeto no es una malla | `SuperficieNoEsMalla` |
| Hay modificadores sin aplicar | `ModificadoresSinAplicar` |
| La escala no es 1 | `EscalaSinAplicar` |
| No hay caras | `SuperficieSinCaras` |
| La base es un sólido cerrado | `SolidoCerrado` |
| Hay aristas no manifold | `AristasNoManifold` |
| Hay vértices sueltos al suavizar normales | `VerticesSueltos` |
| La normal es nula o demasiado corta | `NormalesInvalidas` |
| Llega un parámetro que no existe | `ParametrosNoReconocidos` |
| Un espesor o una celda no es positivo | `ParametroNoPositivo` |
| El código de patrón no existe | `PatronNoReconocido` |
| Triangle o Minimalistic | `PatronNoImplementado` |
| Celda menor que el mínimo | `CeldaDemasiadoPequena` |
| La nervadura ocupa el 75 % o más de la celda | `NervaduraDemasiadoAncha` |
| Un ángulo o un borde no es finito | `ParametroNoFinito` |
| Resolución ≤ 0 | `ResolucionNoPositiva` |
| La semilla no es un entero ≥ 0 | `SemillaInvalida` |
| Marco, transición o banda negativos | `BordeNegativo` |
| El recorte elimina toda la superficie | `SuperficieEliminadaPorPatron` |
| El voxel de reconstrucción queda bajo 0,15 mm | `ResolucionDemasiadoFina` |
| La reconstrucción separa la pieza | `GeometriaFragmentada` |
| Blender rechaza la malla o el modificador | `MallaNoConstruida`, `ReconstruccionFallida` |
| Se comprueba o exporta sin modelo | `ModeloNoGenerado` |
| La comprobación no pasa y se intenta exportar | `MallaNoValida` |
| El STL o el JSON no se pueden escribir | `ExportacionFallida` |
| Volumen, peso o precio sin geometría o con un material inválido | `ModeloSinGeometria`, `MaterialInvalido` |
| JSON de configuración incorrecto | `ConfiguracionInvalida` |
| Se importa la API de Blender fuera de Blender | `EntornoBlenderRequerido` |
| Arreglos internos de distinta longitud | `GeometriaInconsistente` |

Si un vértice no alcanza el contorno, la distancia geodésica queda infinita y se escribe una advertencia. No se cambia el resultado respecto al script anterior.

La comprobación de cruces no cubre solapes coplanares ni caras que comparten vértices.

## API desde la consola de Blender

Con la raíz del repositorio en `sys.path`:

```python
import sys
sys.path.append(r"C:\ruta\al\repositorio")
from GenerateModelsApp.Objeto import GeneradorObjeto
from GenerateModelsApp.Exportacion import ExportadorStl
import bpy

base = bpy.data.objects["OL_SuperficieInterior"]
modelo = GeneradorObjeto.Crear(base, pattern="VORONOI", cell_mm=15.0, rib_width_mm=2.8, seed=7)
ExportadorStl.Exportar(modelo, r"C:\ruta\ortesis.stl")
```

`GeneradorObjeto.Crear` devuelve el objeto `OL_Ortesis`. `Complemento.BuildGeometry` devuelve vértices, caras, configuración y los conteos interiores, sin escribir la escena. `ValidadorMalla.Comprobar` devuelve el informe y lo guarda en `ol_validation`.

## Qué no hace el complemento

No abre un servidor ni expone rutas HTTP. No muestra volumen, peso ni precio: eso pertenece a la aplicación independiente y ya se puede calcular con `CalculateVolume`, `CalculateWeight` y `CalculatePrice`. El precio de PETG es 0,15 por gramo.
