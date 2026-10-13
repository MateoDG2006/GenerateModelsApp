# Índice de símbolos: BlenderPlugin

> Generado por `python docs/Agents/Scripts/GenerarIndices.py`. No editar a mano.

Incluye funciones anidadas y métodos privados para localizar todas las piezas. Las líneas son una ayuda de navegación; el nombre del símbolo es la referencia estable.

## `GenerateModelsApp/__init__.py`

Paquete del complemento de Blender y del núcleo de geometría.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `register` | Función/método | [19](../../GenerateModelsApp/__init__.py#L19) | Sin docstring; consultar el catálogo de módulos y el código. |
| `unregister` | Función/método | [25](../../GenerateModelsApp/__init__.py#L25) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/ApiBlender.py`

API de Blender, separada del núcleo geométrico.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `GenerateModelsApp/Cascaron.py`

Recorte de celdas y cascarón de espesor variable.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Cascaron` | Clase | [14](../../GenerateModelsApp/Cascaron.py#L14) | Pasa de una superficie abierta a un sólido de espesor conocido. |
| `Cascaron.Smooth01` | Función/método | [18](../../GenerateModelsApp/Cascaron.py#L18) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Cascaron.Recortar` | Función/método | [24](../../GenerateModelsApp/Cascaron.py#L24) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Cascaron.Recortar.verticeOriginal` | Función/método | [48](../../GenerateModelsApp/Cascaron.py#L48) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Cascaron.Recortar.cruce` | Función/método | [56](../../GenerateModelsApp/Cascaron.py#L56) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Cascaron.Engrosar` | Función/método | [102](../../GenerateModelsApp/Cascaron.py#L102) | Añade espesor a las caras existentes; nunca rellena una abertura. |
| `Cascaron.Cerrar` | Función/método | [150](../../GenerateModelsApp/Cascaron.py#L150) | Alias compatible: cerrar el espesor no significa tapar el canal. |
| `Cascaron.VolumenMm3` | Función/método | [155](../../GenerateModelsApp/Cascaron.py#L155) | Entrada: vértices y caras del cascarón en mm. Proceso: triangula |

## `GenerateModelsApp/constants/__init__.py`

Constantes de OrtesisLab: nombres, patrones, materiales y límites.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `GenerateModelsApp/constants/Materials.py`

Materiales de impresión.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Material` | Clase | [16](../../GenerateModelsApp/constants/Materials.py#L16) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Material.__init__` | Función/método | [19](../../GenerateModelsApp/constants/Materials.py#L19) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Material.Gramos` | Función/método | [47](../../GenerateModelsApp/constants/Materials.py#L47) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Material.Costo` | Función/método | [57](../../GenerateModelsApp/constants/Materials.py#L57) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PETG` | Clase | [62](../../GenerateModelsApp/constants/Materials.py#L62) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PETG.__init__` | Función/método | [63](../../GenerateModelsApp/constants/Materials.py#L63) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/constants/Nombres.py`

Nombres estables de objetos, atributos y archivos.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `GenerateModelsApp/constants/Paterns.py`

Patrones de nervadura.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Patron` | Clase | [21](../../GenerateModelsApp/constants/Paterns.py#L21) | Catálogo y, cuando existe, distancia al eje de la nervadura. |
| `Patron.__init__` | Función/método | [26](../../GenerateModelsApp/constants/Paterns.py#L26) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Patron.Distancia` | Función/método | [31](../../GenerateModelsApp/constants/Paterns.py#L31) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Patron.RotarXy` | Función/método | [36](../../GenerateModelsApp/constants/Paterns.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Patron.DistanciaCuadricula` | Función/método | [43](../../GenerateModelsApp/constants/Paterns.py#L43) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Patron.DistanciaSemillas` | Función/método | [48](../../GenerateModelsApp/constants/Paterns.py#L48) | Entrada: puntos XY y celda en mm. Proceso: evalúa semillas próximas |
| `Patron._DistanciaPlanos` | Función/método | [96](../../GenerateModelsApp/constants/Paterns.py#L96) | Entrada: puntos y semillas XY. Proceso: calcula la bisectriz más |
| `Patron.Geometricos` | Función/método | [111](../../GenerateModelsApp/constants/Paterns.py#L111) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Patron.Obtener` | Función/método | [122](../../GenerateModelsApp/constants/Paterns.py#L122) | Sin docstring; consultar el catálogo de módulos y el código. |
| `HoneyComb` | Clase | [136](../../GenerateModelsApp/constants/Paterns.py#L136) | Sin docstring; consultar el catálogo de módulos y el código. |
| `HoneyComb.__init__` | Función/método | [140](../../GenerateModelsApp/constants/Paterns.py#L140) | Sin docstring; consultar el catálogo de módulos y el código. |
| `HoneyComb.Distancia` | Función/método | [146](../../GenerateModelsApp/constants/Paterns.py#L146) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Square` | Clase | [150](../../GenerateModelsApp/constants/Paterns.py#L150) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Square.__init__` | Función/método | [153](../../GenerateModelsApp/constants/Paterns.py#L153) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Square.Distancia` | Función/método | [159](../../GenerateModelsApp/constants/Paterns.py#L159) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Triangle` | Clase | [163](../../GenerateModelsApp/constants/Paterns.py#L163) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Triangle.__init__` | Función/método | [165](../../GenerateModelsApp/constants/Paterns.py#L165) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Minimalistic` | Clase | [172](../../GenerateModelsApp/constants/Paterns.py#L172) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Minimalistic.__init__` | Función/método | [174](../../GenerateModelsApp/constants/Paterns.py#L174) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Diamond` | Clase | [181](../../GenerateModelsApp/constants/Paterns.py#L181) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Diamond.__init__` | Función/método | [184](../../GenerateModelsApp/constants/Paterns.py#L184) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Diamond.Distancia` | Función/método | [190](../../GenerateModelsApp/constants/Paterns.py#L190) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Voronoi` | Clase | [198](../../GenerateModelsApp/constants/Paterns.py#L198) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Voronoi.__init__` | Función/método | [201](../../GenerateModelsApp/constants/Paterns.py#L201) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Voronoi.Distancia` | Función/método | [207](../../GenerateModelsApp/constants/Paterns.py#L207) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Solid` | Clase | [211](../../GenerateModelsApp/constants/Paterns.py#L211) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Solid.__init__` | Función/método | [214](../../GenerateModelsApp/constants/Paterns.py#L214) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Solid.Distancia` | Función/método | [220](../../GenerateModelsApp/constants/Paterns.py#L220) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/EscalaMalla.py`

Diagnóstico de unidades para una superficie de ortesis.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `EscalaMalla` | Clase | [19](../../GenerateModelsApp/EscalaMalla.py#L19) | Decide si el eje mayor parece expresado en una unidad distinta de mm. |
| `EscalaMalla.Candidatos` | Función/método | [26](../../GenerateModelsApp/EscalaMalla.py#L26) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EscalaMalla.Diagnosticar` | Función/método | [42](../../GenerateModelsApp/EscalaMalla.py#L42) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EscalaMalla.AlcanzaPaso` | Función/método | [70](../../GenerateModelsApp/EscalaMalla.py#L70) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EscalaMalla.Presupuesto` | Función/método | [80](../../GenerateModelsApp/EscalaMalla.py#L80) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EscalaMalla.EsFalloDePaso` | Función/método | [99](../../GenerateModelsApp/EscalaMalla.py#L99) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EscalaMalla.Aplicar` | Función/método | [104](../../GenerateModelsApp/EscalaMalla.py#L104) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EscalaMalla.Resolver` | Función/método | [194](../../GenerateModelsApp/EscalaMalla.py#L194) | Devuelve el factor aplicado y conserva el factor sugerido para informar. |

## `GenerateModelsApp/Excepciones.py`

Errores de OrtesisLab.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `OrtesisLabError` | Clase | [10](../../GenerateModelsApp/Excepciones.py#L10) | Base de los errores previstos del generador. |
| `OrtesisLabError.__init__` | Función/método | [13](../../GenerateModelsApp/Excepciones.py#L13) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ConfiguracionInvalida` | Clase | [27](../../GenerateModelsApp/Excepciones.py#L27) | Un archivo de ``config`` falta, no es JSON o no tiene las claves exigidas. |
| `EntornoBlenderRequerido` | Clase | [31](../../GenerateModelsApp/Excepciones.py#L31) | El módulo usa la API de Blender y se importó fuera de Blender. |
| `ArchivoSuperficieNoEncontrado` | Clase | [35](../../GenerateModelsApp/Excepciones.py#L35) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ArchivoSuperficieNoEncontrado.__init__` | Función/método | [36](../../GenerateModelsApp/Excepciones.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ArchivoSuperficieIlegible` | Clase | [43](../../GenerateModelsApp/Excepciones.py#L43) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ArchivoSuperficieIlegible.__init__` | Función/método | [44](../../GenerateModelsApp/Excepciones.py#L44) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieNoEsMalla` | Clase | [51](../../GenerateModelsApp/Excepciones.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieNoEsMalla.__init__` | Función/método | [52](../../GenerateModelsApp/Excepciones.py#L52) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieInvalida` | Clase | [56](../../GenerateModelsApp/Excepciones.py#L56) | La base no es una superficie conectada y orientada de una sola capa. |
| `ModificadoresSinAplicar` | Clase | [60](../../GenerateModelsApp/Excepciones.py#L60) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ModificadoresSinAplicar.__init__` | Función/método | [61](../../GenerateModelsApp/Excepciones.py#L61) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EscalaSinAplicar` | Clase | [68](../../GenerateModelsApp/Excepciones.py#L68) | Sin docstring; consultar el catálogo de módulos y el código. |
| `EscalaSinAplicar.__init__` | Función/método | [69](../../GenerateModelsApp/Excepciones.py#L69) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieSinCaras` | Clase | [76](../../GenerateModelsApp/Excepciones.py#L76) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieSinCaras.__init__` | Función/método | [77](../../GenerateModelsApp/Excepciones.py#L77) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SolidoCerrado` | Clase | [81](../../GenerateModelsApp/Excepciones.py#L81) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SolidoCerrado.__init__` | Función/método | [82](../../GenerateModelsApp/Excepciones.py#L82) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AristasNoManifold` | Clase | [89](../../GenerateModelsApp/Excepciones.py#L89) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AristasNoManifold.__init__` | Función/método | [90](../../GenerateModelsApp/Excepciones.py#L90) | Sin docstring; consultar el catálogo de módulos y el código. |
| `VerticesSueltos` | Clase | [94](../../GenerateModelsApp/Excepciones.py#L94) | Sin docstring; consultar el catálogo de módulos y el código. |
| `VerticesSueltos.__init__` | Función/método | [95](../../GenerateModelsApp/Excepciones.py#L95) | Sin docstring; consultar el catálogo de módulos y el código. |
| `NormalesInvalidas` | Clase | [99](../../GenerateModelsApp/Excepciones.py#L99) | Sin docstring; consultar el catálogo de módulos y el código. |
| `NormalesInvalidas.__init__` | Función/método | [100](../../GenerateModelsApp/Excepciones.py#L100) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ParametrosNoReconocidos` | Clase | [104](../../GenerateModelsApp/Excepciones.py#L104) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ParametrosNoReconocidos.__init__` | Función/método | [105](../../GenerateModelsApp/Excepciones.py#L105) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ParametroNoPositivo` | Clase | [110](../../GenerateModelsApp/Excepciones.py#L110) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ParametroNoPositivo.__init__` | Función/método | [111](../../GenerateModelsApp/Excepciones.py#L111) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PatronNoReconocido` | Clase | [115](../../GenerateModelsApp/Excepciones.py#L115) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PatronNoReconocido.__init__` | Función/método | [116](../../GenerateModelsApp/Excepciones.py#L116) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PatronNoImplementado` | Clase | [120](../../GenerateModelsApp/Excepciones.py#L120) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PatronNoImplementado.__init__` | Función/método | [121](../../GenerateModelsApp/Excepciones.py#L121) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CeldaDemasiadoPequena` | Clase | [128](../../GenerateModelsApp/Excepciones.py#L128) | Sin docstring; consultar el catálogo de módulos y el código. |
| `CeldaDemasiadoPequena.__init__` | Función/método | [129](../../GenerateModelsApp/Excepciones.py#L129) | Sin docstring; consultar el catálogo de módulos y el código. |
| `NervaduraDemasiadoAncha` | Clase | [135](../../GenerateModelsApp/Excepciones.py#L135) | Sin docstring; consultar el catálogo de módulos y el código. |
| `NervaduraDemasiadoAncha.__init__` | Función/método | [136](../../GenerateModelsApp/Excepciones.py#L136) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ParametroNoFinito` | Clase | [142](../../GenerateModelsApp/Excepciones.py#L142) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ParametroNoFinito.__init__` | Función/método | [143](../../GenerateModelsApp/Excepciones.py#L143) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ResolucionNoPositiva` | Clase | [147](../../GenerateModelsApp/Excepciones.py#L147) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ResolucionNoPositiva.__init__` | Función/método | [148](../../GenerateModelsApp/Excepciones.py#L148) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SemillaInvalida` | Clase | [152](../../GenerateModelsApp/Excepciones.py#L152) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SemillaInvalida.__init__` | Función/método | [153](../../GenerateModelsApp/Excepciones.py#L153) | Sin docstring; consultar el catálogo de módulos y el código. |
| `BordeNegativo` | Clase | [157](../../GenerateModelsApp/Excepciones.py#L157) | Sin docstring; consultar el catálogo de módulos y el código. |
| `BordeNegativo.__init__` | Función/método | [158](../../GenerateModelsApp/Excepciones.py#L158) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieEliminadaPorPatron` | Clase | [165](../../GenerateModelsApp/Excepciones.py#L165) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieEliminadaPorPatron.__init__` | Función/método | [166](../../GenerateModelsApp/Excepciones.py#L166) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ResolucionDemasiadoFina` | Clase | [170](../../GenerateModelsApp/Excepciones.py#L170) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ResolucionDemasiadoFina.__init__` | Función/método | [171](../../GenerateModelsApp/Excepciones.py#L171) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeometriaFragmentada` | Clase | [178](../../GenerateModelsApp/Excepciones.py#L178) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeometriaFragmentada.__init__` | Función/método | [179](../../GenerateModelsApp/Excepciones.py#L179) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeometriaInconsistente` | Clase | [187](../../GenerateModelsApp/Excepciones.py#L187) | Los arreglos internos no coinciden entre sí. Indica un fallo del generador. |
| `MallaNoConstruida` | Clase | [191](../../GenerateModelsApp/Excepciones.py#L191) | Sin docstring; consultar el catálogo de módulos y el código. |
| `MallaNoConstruida.__init__` | Función/método | [192](../../GenerateModelsApp/Excepciones.py#L192) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ReconstruccionFallida` | Clase | [196](../../GenerateModelsApp/Excepciones.py#L196) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ReconstruccionFallida.__init__` | Función/método | [197](../../GenerateModelsApp/Excepciones.py#L197) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ModeloNoGenerado` | Clase | [204](../../GenerateModelsApp/Excepciones.py#L204) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ModeloNoGenerado.__init__` | Función/método | [205](../../GenerateModelsApp/Excepciones.py#L205) | Sin docstring; consultar el catálogo de módulos y el código. |
| `MallaNoValida` | Clase | [209](../../GenerateModelsApp/Excepciones.py#L209) | Sin docstring; consultar el catálogo de módulos y el código. |
| `MallaNoValida.__init__` | Función/método | [210](../../GenerateModelsApp/Excepciones.py#L210) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ExportacionFallida` | Clase | [216](../../GenerateModelsApp/Excepciones.py#L216) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ExportacionFallida.__init__` | Función/método | [217](../../GenerateModelsApp/Excepciones.py#L217) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ModeloSinGeometria` | Clase | [224](../../GenerateModelsApp/Excepciones.py#L224) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ModeloSinGeometria.__init__` | Función/método | [225](../../GenerateModelsApp/Excepciones.py#L225) | Sin docstring; consultar el catálogo de módulos y el código. |
| `MaterialInvalido` | Clase | [229](../../GenerateModelsApp/Excepciones.py#L229) | Densidad, precio o volumen incompatibles con el cálculo de material. |

## `GenerateModelsApp/Exportacion.py`

Exporta el STL en milímetros y un JSON con parámetros y comprobación.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ExportadorStl` | Clase | [15](../../GenerateModelsApp/Exportacion.py#L15) | Escribe el STL solo si la malla pasó la comprobación. |
| `ExportadorStl.Exportar` | Función/método | [19](../../GenerateModelsApp/Exportacion.py#L19) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/Interfaz.py`

Panel N y operadores de OrtesisLab en la vista 3D.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `PanelAyuda` | Clase | [30](../../GenerateModelsApp/Interfaz.py#L30) | Lee los controles del panel y muestra los errores en la interfaz. |
| `PanelAyuda.OrigenAutoescala` | Función/método | [34](../../GenerateModelsApp/Interfaz.py#L34) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PanelAyuda.AvisarEscala` | Función/método | [43](../../GenerateModelsApp/Interfaz.py#L43) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PanelAyuda.OpcionesDesdeAjustes` | Función/método | [63](../../GenerateModelsApp/Interfaz.py#L63) | Sin docstring; consultar el catálogo de módulos y el código. |
| `PanelAyuda.Cancelar` | Función/método | [73](../../GenerateModelsApp/Interfaz.py#L73) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_Preferences` | Clase | [83](../../GenerateModelsApp/Interfaz.py#L83) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_Preferences.draw` | Función/método | [95](../../GenerateModelsApp/Interfaz.py#L95) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_Settings` | Clase | [99](../../GenerateModelsApp/Interfaz.py#L99) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_generate` | Clase | [153](../../GenerateModelsApp/Interfaz.py#L153) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_generate.execute` | Función/método | [159](../../GenerateModelsApp/Interfaz.py#L159) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_use_surface` | Clase | [177](../../GenerateModelsApp/Interfaz.py#L177) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_use_surface.execute` | Función/método | [182](../../GenerateModelsApp/Interfaz.py#L182) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_repair_surface` | Clase | [198](../../GenerateModelsApp/Interfaz.py#L198) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_repair_surface.poll` | Función/método | [209](../../GenerateModelsApp/Interfaz.py#L209) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_repair_surface.execute` | Función/método | [213](../../GenerateModelsApp/Interfaz.py#L213) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_validate` | Clase | [245](../../GenerateModelsApp/Interfaz.py#L245) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_validate.execute` | Función/método | [250](../../GenerateModelsApp/Interfaz.py#L250) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_export` | Clase | [264](../../GenerateModelsApp/Interfaz.py#L264) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_export.invoke` | Función/método | [271](../../GenerateModelsApp/Interfaz.py#L271) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_OT_export.execute` | Función/método | [276](../../GenerateModelsApp/Interfaz.py#L276) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_PT_panel` | Clase | [289](../../GenerateModelsApp/Interfaz.py#L289) | Sin docstring; consultar el catálogo de módulos y el código. |
| `OL_PT_panel.draw` | Función/método | [297](../../GenerateModelsApp/Interfaz.py#L297) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/Malla.py`

Análisis de la superficie abierta, sin Blender.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `AnalizadorMalla` | Clase | [24](../../GenerateModelsApp/Malla.py#L24) | Comprueba que la base sea una superficie abierta y mide el borde. |
| `AnalizadorMalla.NormalesDeCaras` | Función/método | [28](../../GenerateModelsApp/Malla.py#L28) | Entrada: vértices y triángulos orientados. Proceso: promedia normales |
| `AnalizadorMalla.Preparar` | Función/método | [47](../../GenerateModelsApp/Malla.py#L47) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AnalizadorMalla.DistanciaAlContorno` | Función/método | [136](../../GenerateModelsApp/Malla.py#L136) | Entrada: malla triangular abierta. Proceso: Dijkstra por aristas. |
| `AnalizadorMalla._Adyacencia` | Función/método | [148](../../GenerateModelsApp/Malla.py#L148) | Sin docstring; consultar el catálogo de módulos y el código. |
| `AnalizadorMalla._Geodesica` | Función/método | [157](../../GenerateModelsApp/Malla.py#L157) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/Modeling.py`

Modelo de impresión y construcción de la geometría.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Model3DForPrinting` | Clase | [48](../../GenerateModelsApp/Modeling.py#L48) | Pieza paramétrica: geometría, volumen, peso y precio de material. |
| `Model3DForPrinting.__init__` | Función/método | [51](../../GenerateModelsApp/Modeling.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Model3DForPrinting.ValidarOpciones` | Función/método | [63](../../GenerateModelsApp/Modeling.py#L63) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Model3DForPrinting.ConstruirGeometria` | Función/método | [113](../../GenerateModelsApp/Modeling.py#L113) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Model3DForPrinting.ChangePatern` | Función/método | [162](../../GenerateModelsApp/Modeling.py#L162) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Model3DForPrinting.ChangePattern` | Función/método | [179](../../GenerateModelsApp/Modeling.py#L179) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Model3DForPrinting.Construir` | Función/método | [183](../../GenerateModelsApp/Modeling.py#L183) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Model3DForPrinting.CalculateVolume` | Función/método | [200](../../GenerateModelsApp/Modeling.py#L200) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Model3DForPrinting.CalculateWeight` | Función/método | [217](../../GenerateModelsApp/Modeling.py#L217) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Model3DForPrinting.CalculatePrice` | Función/método | [225](../../GenerateModelsApp/Modeling.py#L225) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/Objeto.py`

Crea o actualiza el objeto OL_Ortesis en la escena de Blender.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `GeneradorObjeto` | Clase | [37](../../GenerateModelsApp/Objeto.py#L37) | Escribe el cascarón en la escena y, si se pide, lo reconstruye con voxel. |
| `GeneradorObjeto._EspesorMinimo` | Función/método | [41](../../GenerateModelsApp/Objeto.py#L41) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorObjeto._Componentes` | Función/método | [50](../../GenerateModelsApp/Objeto.py#L50) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorObjeto._AplicarModificador` | Función/método | [73](../../GenerateModelsApp/Objeto.py#L73) | Sin docstring; consultar el catálogo de módulos y el código. |
| `GeneradorObjeto.Crear` | Función/método | [80](../../GenerateModelsApp/Objeto.py#L80) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/OrtesisLab.py`

Complemento OrtesisLab dentro del paquete.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Complemento` | Clase | [15](../../GenerateModelsApp/OrtesisLab.py#L15) | Registra el panel y construye geometría sin escribirla todavía en escena. |
| `Complemento.BuildGeometry` | Función/método | [19](../../GenerateModelsApp/OrtesisLab.py#L19) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Complemento.Retirar` | Función/método | [36](../../GenerateModelsApp/OrtesisLab.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Complemento.Registrar` | Función/método | [51](../../GenerateModelsApp/OrtesisLab.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `register` | Función/método | [74](../../GenerateModelsApp/OrtesisLab.py#L74) | Sin docstring; consultar el catálogo de módulos y el código. |
| `unregister` | Función/método | [79](../../GenerateModelsApp/OrtesisLab.py#L79) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/RefinadorMalla.py`

Refinamiento triangular independiente de Blender para evaluar patrones.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `RefinadorMalla` | Clase | [12](../../GenerateModelsApp/RefinadorMalla.py#L12) | Divide únicamente las aristas largas y conserva una superficie conectada. |
| `RefinadorMalla.PasoPatron` | Función/método | [16](../../GenerateModelsApp/RefinadorMalla.py#L16) | Entrada: parámetros validados. Proceso: limita el paso según el patrón. |
| `RefinadorMalla.AristaMayor` | Función/método | [26](../../GenerateModelsApp/RefinadorMalla.py#L26) | Entrada: malla triangular. Proceso: mide sus aristas. Salida: longitud |
| `RefinadorMalla.Refinar` | Función/método | [36](../../GenerateModelsApp/RefinadorMalla.py#L36) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/ReparacionMalla.py`

Limpieza segura de la superficie base dentro de Blender.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ReparadorMalla` | Clase | [24](../../GenerateModelsApp/ReparacionMalla.py#L24) | Limpia una superficie abierta sin convertirla en un volumen. |
| `ReparadorMalla._ComponentesCaras` | Función/método | [30](../../GenerateModelsApp/ReparacionMalla.py#L30) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ReparadorMalla._EliminarCarasDuplicadas` | Función/método | [51](../../GenerateModelsApp/ReparacionMalla.py#L51) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ReparadorMalla._EliminarSinCaras` | Función/método | [67](../../GenerateModelsApp/ReparacionMalla.py#L67) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ReparadorMalla._ArreglarBmesh` | Función/método | [76](../../GenerateModelsApp/ReparacionMalla.py#L76) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ReparadorMalla._ValidarBmesh` | Función/método | [157](../../GenerateModelsApp/ReparacionMalla.py#L157) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ReparadorMalla.Arreglar` | Función/método | [173](../../GenerateModelsApp/ReparacionMalla.py#L173) | Repara la malla activa y devuelve un resumen de lo retirado. |

## `GenerateModelsApp/SuavizadoBorde.py`

Suavizado del contorno exterior antes de dar espesor.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `SuavizadoBorde` | Clase | [15](../../GenerateModelsApp/SuavizadoBorde.py#L15) | Aplana los dientes del contorno sin mover el interior de la superficie. |
| `SuavizadoBorde.Aplicar` | Función/método | [19](../../GenerateModelsApp/SuavizadoBorde.py#L19) | Entrada: superficie abierta ya validada. Proceso: filtra cada bucle |
| `SuavizadoBorde._Bucles` | Función/método | [104](../../GenerateModelsApp/SuavizadoBorde.py#L104) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuavizadoBorde._Pasabajos` | Función/método | [140](../../GenerateModelsApp/SuavizadoBorde.py#L140) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuavizadoBorde._MascaraRota` | Función/método | [175](../../GenerateModelsApp/SuavizadoBorde.py#L175) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuavizadoBorde._CarasRotas` | Función/método | [185](../../GenerateModelsApp/SuavizadoBorde.py#L185) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/Superficie.py`

Carga y lectura de la superficie interior dentro de Blender.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `SuperficieInterior` | Clase | [39](../../GenerateModelsApp/Superficie.py#L39) | Prepara una copia de la superficie elegida, sin cerrar sus aberturas. |
| `SuperficieInterior._Candidatos` | Función/método | [52](../../GenerateModelsApp/Superficie.py#L52) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieInterior.Cargar` | Función/método | [65](../../GenerateModelsApp/Superficie.py#L65) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieInterior._CorregirUnidades` | Función/método | [109](../../GenerateModelsApp/Superficie.py#L109) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieInterior.Leer` | Función/método | [129](../../GenerateModelsApp/Superficie.py#L129) | Sin docstring; consultar el catálogo de módulos y el código. |
| `SuperficieInterior.Leer.refinar` | Función/método | [170](../../GenerateModelsApp/Superficie.py#L170) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/util/__init__.py`

Utilidades compartidas: registro de ejecución y lectura de JSON.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |

## `GenerateModelsApp/util/Utilidades.py`

Registro de mensajes y lectura de la carpeta config.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `Registro` | Clase | [17](../../GenerateModelsApp/util/Utilidades.py#L17) | Escribe en consola y en logs/ortesislab.log. |
| `Registro._Preferencias` | Función/método | [31](../../GenerateModelsApp/util/Utilidades.py#L31) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Registro._Nivel` | Función/método | [50](../../GenerateModelsApp/util/Utilidades.py#L50) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Registro.Configurar` | Función/método | [58](../../GenerateModelsApp/util/Utilidades.py#L58) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Registro.Obtener` | Función/método | [92](../../GenerateModelsApp/util/Utilidades.py#L92) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Configuracion` | Clase | [98](../../GenerateModelsApp/util/Utilidades.py#L98) | Carga los JSON de config y comprueba que traigan las claves esperadas. |
| `Configuracion._Error` | Función/método | [159](../../GenerateModelsApp/util/Utilidades.py#L159) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Configuracion.Recargar` | Función/método | [166](../../GenerateModelsApp/util/Utilidades.py#L166) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Configuracion.CargarJson` | Función/método | [172](../../GenerateModelsApp/util/Utilidades.py#L172) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Configuracion._ExigirClaves` | Función/método | [197](../../GenerateModelsApp/util/Utilidades.py#L197) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Configuracion.ParametrosDefecto` | Función/método | [207](../../GenerateModelsApp/util/Utilidades.py#L207) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Configuracion.Limites` | Función/método | [214](../../GenerateModelsApp/util/Utilidades.py#L214) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Configuracion.ValorLimite` | Función/método | [221](../../GenerateModelsApp/util/Utilidades.py#L221) | Sin docstring; consultar el catálogo de módulos y el código. |
| `Configuracion.ComprobacionDeReferencia` | Función/método | [231](../../GenerateModelsApp/util/Utilidades.py#L231) | Sin docstring; consultar el catálogo de módulos y el código. |

## `GenerateModelsApp/ValidacionMalla.py`

Comprobación geométrica de la malla ya generada.

| Símbolo | Tipo | Línea | Descripción declarada |
|---|---|---:|---|
| `ValidadorMalla` | Clase | [18](../../GenerateModelsApp/ValidacionMalla.py#L18) | Informa si OL_Ortesis es una sola pieza cerrada. |
| `ValidadorMalla._Componentes` | Función/método | [22](../../GenerateModelsApp/ValidacionMalla.py#L22) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ValidadorMalla._Cruces` | Función/método | [42](../../GenerateModelsApp/ValidacionMalla.py#L42) | Sin docstring; consultar el catálogo de módulos y el código. |
| `ValidadorMalla.Comprobar` | Función/método | [70](../../GenerateModelsApp/ValidacionMalla.py#L70) | Sin docstring; consultar el catálogo de módulos y el código. |
