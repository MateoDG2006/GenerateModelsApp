# Frontend de OrtesisLab

Hay dos sistemas independientes. Comparten el núcleo de geometría (`Modeling`, `malla`, `cascaron`, patrones y materiales) y no se llaman entre sí.

El complemento de Blender genera y exporta una pieza. No calcula coste. La aplicación Reflex usa ese mismo cálculo para producir el diseño, mostrarlo y añadir el coste de impresión de cada variante. Desde ahí se pueden lanzar muchas generaciones, cambiando parámetros en cada iteración, y comparar los resultados.

## Panel de Blender

Aparece en la vista 3D, tecla **N**, pestaña **Ortesis**, después de registrar el complemento. Los controles no regeneran la malla al moverse: hay que pulsar **Generar / actualizar**.

| Control | Cuándo se muestra | Efecto |
|---|---|---|
| Superficie sin espesor | Siempre | Una capa de caras abierta en mano y dedo. Si está vacío, Generar usa la malla activa; no carga la plantilla v5. |
| Usar malla seleccionada | Siempre | Comprueba la superficie activa y la asigna como base. |
| Autoescalar a milímetros | Siempre, también en Preferences > Add-ons | Actívalo para que Generar y Arreglar corrijan factores decimales fuera de 20–1000 mm. Desactívalo para conservar el archivo; se muestra el factor sugerido. |
| Generar hacia dentro / Paso de superficie | Siempre | Por defecto el espesor crece hacia fuera siguiendo las normales. La inversión es opcional; el paso controla el detalle de la copia de trabajo. |
| Patrón | Siempre | Voronoi, hexagonal, rombos, cuadrícula o macizo. |
| Espesor macizo | Solo en macizo | Espesor uniforme. El resto de controles de nervadura se ocultan. |
| Celda, ancho, altura y capa continua | Cualquier patrón que no sea macizo | Retícula y si las celdas tienen fondo. |
| Espesor de capa y transición | Capa continua activada | El panel muestra el espesor total: capa + altura de nervadura. |
| Aviso de rejilla abierta | Capa continua desactivada | La altura pasa a ser el espesor total. |
| Giro | No macizo | Orientación en XY. |
| Semilla | Solo Voronoi | Celdas orgánicas reproducibles. |
| Marco y banda maciza | No macizo | La posición Y de la banda solo aparece si el ancho de banda es mayor que cero. |
| Reconstruir y resolución | La resolución solo si la reconstrucción está activa | Voxel opcional, desactivado por defecto para conservar los contornos. Puede alterar aberturas estrechas. |

Debajo están **Generar / actualizar**, **Comprobar malla** y **Exportar STL en mm**. Exportar abre el selector de archivo; el nombre inicial es `Ortesis_configurada.stl`, junto al `.blend` si hay uno abierto.

El estado cabe en 48 caracteres en la etiqueta del panel. El texto completo queda en el aviso de Blender y en `GenerateModelsApp/logs/ortesislab.log`. La última línea del panel recuerda que la herramienta modifica geometría y no evalúa resistencia.

### Qué ve la persona cuando algo falla

Los operadores capturan el error, lo marcan en rojo y copian el mensaje al estado. Los casos previstos usan el texto de cada clase de `excepciones.py` (superficie cerrada, celda demasiado pequeña, malla separada en piezas, exportar sin haber generado). Un fallo que no estaba previsto se registra con la traza y también se muestra.

Comprobar una malla válida informa «Pared sólida y conectada; geometría válida». Se cierra el volumen del material, no la abertura de la mano ni del dedo. Si la comprobación encuentra bordes, piezas o cruces, muestra el informe como aviso. Exportar esa malla se cancela.

Generar con éxito deja el estado «Modelo actualizado; valide antes de exportar.» Exportar con éxito confirma que el STL y los parámetros quedaron en milímetros. El JSON hermano del STL no se abre en el panel.

### Cómo se abre

En **Preferences > Add-ons > Install from Disk** se instala la carpeta del paquete `GenerateModelsApp` (la que tiene `__init__.py`). Para lanzarlo desde disco se ejecuta `scripts/EjecutarOrtesisLab.py`. Un bloque de texto copiado al editor de Blender no puede importar el resto de los módulos.

El detalle de uso, unidades y límites geométricos está en [LEEME.md](LEEME.md).

## Aplicación web Reflex

`rxconfig.py` nombra la aplicación `GenerateModelsApp` y activa el mapa del sitio, Tailwind 4 y Radix Themes. La página está en `web/PaginaComparacion.py`, fuera del paquete que se instala en Blender.

Esa página llama a `Model3DForPrinting`, `AnalizadorMalla`, `RefinadorMalla` y `PETG`. No importa `bpy`. Permite subir una superficie abierta STL o NPZ de hasta 50 MB, o usar la incluida (`assets/superficie_interior_mm.npz`). La casilla **Autoescalar a milímetros** decide, en cada previsualización o lote, si se corrigen factores decimales. El archivo guardado conserva las coordenadas originales. Antes de aplicar Voronoi, hexágonos, rombos o cuadrícula, la web refina la superficie según el paso indicado para que las celdas no dependan de una malla de entrada demasiado gruesa. Después construye el cascarón y lo muestra en un visor. Calcula volumen, peso y precio de ese cascarón. Un lote cruza los patrones del panel con el barrido de un parámetro numérico, hasta 12 variantes.

La reconstrucción voxel y la comprobación de malla final siguen solo en Blender. El precio usa 0,15 por gramo de PETG y no declara moneda.

`src/generatemodelsapp/__init__.py` es el punto del comando de consola del proyecto e imprime un saludo. No es la interfaz web.

La referencia de componentes de Reflex está en [GUIA_REFLEX.md](GUIA_REFLEX.md).

## Aplicación de comparación

La página web ya hace esa comparación, aparte del complemento:

- Reutiliza la geometría paramétrica de cada diseño. No abre Blender ni le envía archivos.
- Muestra volumen, peso y precio. El panel de Blender no los muestra.
- El precio de PETG es 0,15 por gramo. La moneda no está declarada en `Materials.py`.
- Recorre combinaciones de parámetros, genera cada variante y permite comparar hasta tres mallas.
- La interfaz está en español. Los nombres de catálogo HoneyComb, Square, Triangle y Minimalistic siguen en inglés dentro del paquete.
