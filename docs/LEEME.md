# OrtesisLab 1.3 — superficie sin espesor

El complemento convierte una sola capa de caras en una pared con espesor, patrón de rejilla y capa interior continua opcional. No necesita el modelo v5 ni su NPZ.

## Instalar y generar

1. Instala **GenerateModelsApp.zip** desde **Edit > Preferences > Add-ons > Install from Disk** y activa **OrtesisLab**. Si tienes una versión anterior, actualízala y reinicia Blender para descargar los módulos antiguos.
2. Modela o importa la **superficie de contacto sin espesor**: una sola capa de caras conectadas. Debe tener la parte superior abierta tanto en la mano como en el dedo, sin una tapa sobre esas zonas ni una segunda piel exterior.
3. Usa coordenadas en **mm**. En este flujo, 100 unidades de malla representan 100 mm; puedes configurar Metric con Unit Scale 0.001. Trabaja con el eje longitudinal en Y y la abertura hacia Z para el patrón XY.
4. En **Object Mode**, selecciona esa superficie. Abre **N > Ortesis** y pulsa **Usar malla seleccionada**. También puedes elegirla en **Superficie sin espesor**. Si el campo está vacío, Generar usa el objeto activo; nunca carga la plantilla antigua automáticamente.
5. Si la base tiene vértices repetidos, elementos sueltos, fragmentos separados, caras duplicadas o normales desordenadas, pulsa **Arreglar**. La casilla **Autoescalar a milímetros** está en el panel y en las preferencias del complemento. Activada, Generar corrige en una copia los factores decimales cuando el eje mayor queda fuera de 20–1000 mm, y Arreglar además hornea esa corrección y la escala del objeto en la base. Desactívala para conservar las dimensiones; en ese caso se muestra el factor sugerido. Arreglar conserva la pieza de caras más grande, triangula y vuelve a comprobarla. No añade espesor ni convierte un sólido cerrado en una superficie: en ese caso hay que eliminar manualmente la segunda piel y las tapas.
6. Ajusta patrón, espesores y celdas, y pulsa **Generar / actualizar**. La base se conserva y se oculta; el resultado aparece como `OL_Ortesis`.
7. Usa **Comprobar malla** y **Exportar STL en mm**. Se guarda también un JSON con los parámetros empleados y la comprobación geométrica.

Desde el repositorio puedes ejecutar `scripts/EjecutarOrtesisLab.py` en Blender. No instales solo OrtesisLab.py: requiere los otros módulos. Reflex no es necesario para el complemento.

## Qué significa abierta

La abertura para introducir la mano y el dedo procede del contorno que dibujas en la base. El generador **no rellena contornos ni une labios opuestos**: duplica las caras hacia el exterior y une cada arista libre únicamente con su copia, cerrando el espesor de la pared.

Por eso una ortesis abierta por arriba puede tener una malla sólida sin aristas abiertas: el material tiene volumen, pero el canal permanece abierto. **Capa interior continua** añade fondo a las celdas de la pared; no crea un techo sobre el canal. Desactivarla produce huecos pasantes.

El programa no identifica anatómicamente el dedo ni elimina techos que ya existan en la base. Si una superficie trae una tapa, elimínala en Edit Mode antes de seleccionarla. No se corta automáticamente por altura, porque podría eliminar partes útiles de otra forma de ortesis.

## Controles

| Control | Efecto |
|---|---|
| Generar hacia dentro (invertir) | Desactivado, el material crece hacia fuera siguiendo las normales de la base. Actívalo únicamente para invertir ese sentido. |
| Paso de superficie | Tamaño máximo de arista en una copia de trabajo. Subdivide bases de pocas caras, sin cambiar sus contornos. Para patrones se limita además a un tercio del ancho de nervadura y un sexto de la celda. |
| Patrón | Orgánico/Voronoi, hexagonal, rombos, cuadrícula o macizo. |
| Tamaño de celda | Separación del patrón en la proyección XY. |
| Ancho de nervadura | Ancho de las tiras en esa proyección; en paredes inclinadas la medida sobre la superficie varía. |
| Altura de nervadura | Relieve exterior adicional a la capa lisa. Sin capa, es el espesor total de la rejilla. |
| Capa interior continua / espesor | Activa el fondo de las celdas y define su espesor nominal. |
| Espesor macizo | Espesor nominal uniforme para el patrón macizo. |
| Marco perimetral | Banda siguiendo los bordes existentes, sin atravesar la abertura superior. |
| Transición, giro y semilla | Suavizado del relieve, orientación y variación reproducible del patrón. |
| Banda maciza | Banda de ancho y posición Y configurables sobre las caras existentes. |
| Reconstrucción voxel | Opcional y **desactivada por defecto**. Aproxima el resultado y puede modificar o unir huecos estrechos; revisa las aberturas si la activas. |

Con capa: espesor nominal de la nervadura = espesor de capa + altura de nervadura. El desplazamiento sigue normales; las medidas locales pueden variar en curvas fuertes y tras reconstrucción.

Para editar la forma, muestra la base desde el Outliner, modifica sus caras, vuelve a Object Mode y genera. Se leen las caras y normales actuales, sin reutilizar normales antiguas de v5. Se rechazan sólidos cerrados, caras duplicadas, orientaciones inconsistentes, vértices sueltos y superficies desconectadas. La subdivisión tiene un límite de 500 000 vértices.

## Uso desde Python de Blender

```python
import bpy
from GenerateModelsApp.Objeto import GeneradorObjeto

base = bpy.context.active_object  # superficie sin espesor, ya abierta
modelo = GeneradorObjeto.Crear(
    base,
    pattern='VORONOI',
    cell_mm=15.0,
    rib_width_mm=2.8,
    rib_height_mm=1.4,
    liner=True,
    skin_mm=1.0,
    flip_normals=False,
    surface_step_mm=1.0,
    repair=False,
)
```

`SuperficieInterior.Cargar(path)` se conserva como utilidad explícita para NPZ antiguos. No se invoca desde el panel y el ZIP de Blender no incorpora aquella base.

## Comprobación

Las pruebas en Blender usan una bandeja con un canal lateral de dedo, ambos abiertos, en cinco patrones, con y sin capa. Comprueban la ausencia de techo en los dos canales, la conservación de la base, el registro del panel y la validez de las paredes. Es una probeta geométrica, no un nuevo modelo anatómico.

La exportación comprueba conectividad, caras degeneradas, aristas del sólido y cruces detectables. No comprueba ajuste anatómico ni todos los posibles solapes coplanares. El resultado anterior en `config/comprobacion_geometrica.json` es una referencia histórica, no una validación de la malla que generes hoy.

