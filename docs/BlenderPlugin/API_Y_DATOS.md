# API Python, contratos y datos de Blender

## Uso desde Blender

Ejecutar dentro de Blender con el paquete instalado o la raíz del repositorio en `sys.path`:

```python
import bpy
from GenerateModelsApp.Objeto import GeneradorObjeto
from GenerateModelsApp.ValidacionMalla import ValidadorMalla
from GenerateModelsApp.Exportacion import ExportadorStl

base = bpy.context.active_object  # Object Mode, MESH abierto sin espesor
resultado = GeneradorObjeto.Crear(
    base,
    pattern="VORONOI",
    cell_mm=15.0,
    rib_width_mm=2.8,
    rib_height_mm=1.4,
    liner=True,
    skin_mm=1.0,
    repair=False,
    autoescalar=True,
)
informe = ValidadorMalla.Comprobar(resultado)
if informe["ok"]:
    ExportadorStl.Exportar(resultado, bpy.path.abspath("//ortesis.stl"))
```

No instala el paquete con un archivo suelto: son necesarias sus importaciones y configuraciones. No ejecutar esta API en el intérprete web.

| API | Precondiciones → resultado / efectos |
|---|---|
| `SuperficieInterior.Leer(source, paso_mm=None, autoescalar=True)` | MESH base, Object Mode, sin modificadores, escala aplicada → tupla de arrays; escala/refina copia y actualiza diagnóstico/caché |
| `SuperficieInterior.Cargar(path=None)` | NPZ explícito o rutas candidatas → objeto oculto `OL_SuperficieInterior`; fija unidades escena; no se llama desde panel |
| `Complemento.BuildGeometry(source, **options)` | Base válida → `(vertices, faces, cfg, n_interiores, m_interiores)`; no escribe resultado en escena ni aplica voxel |
| `GeneradorObjeto.Crear(source, **options)` | Base/opciones válidas → objeto `OL_Ortesis`; sustituye malla, oculta base y selecciona resultado; voxel opcional |
| `ReparadorMalla.Arreglar(objeto, autoescalar=True)` | Base activa válida para limpieza → resumen; modifica base si valida copia y pone escala a uno |
| `ValidadorMalla.Comprobar(ob, intersections=True)` | Objeto MESH generado → informe; copia BMesh para medir, guarda JSON en `ol_validation` |
| `ExportadorStl.Exportar(ob, path)` | Objeto con `ol_config` e informe final válido → escribe STL y `path + '.json'`; devuelve informe |

## API del núcleo sin Blender

```python
from GenerateModelsApp.Malla import AnalizadorMalla
from GenerateModelsApp.Modeling import Model3DForPrinting

# puntos: float (N,3), triangulos: enteros (M,3), normales: float (N,3)
p, f, n, borde = AnalizadorMalla.Preparar(
    puntos, triangulos, normales, suavizarNormales=False
)
modelo = Model3DForPrinting()
vertices, caras, cfg, n_base, m_base = modelo.Construir(
    p, f, n, borde, pattern="SOLID", solid_mm=2.4
)
volumen_mm3 = modelo.CalculateVolume()
peso_g = modelo.CalculateWeight()
precio = modelo.CalculatePrice()
```

Los nombres `puntos`, `triangulos` y `normales` representan datos del llamador; el ejemplo no incorpora una base anatómica. `Construir` no refina por sí mismo: los adaptadores deciden cómo preparar arrays. `ConstruirGeometria` es estático y no guarda geometría en una instancia; `Construir` sí. Cambiar patrón con `ChangePatern`/`ChangePattern` selecciona opciones, pero no reconstruye automáticamente vertices/faces: volver a llamar `Construir` antes de medir el nuevo diseño.

Contrato de salida: vertices float64 `(2N,3)` después de recorte si lo hay; caras como lista de tuplas, combinando triángulos y muros cuadriláteros; configuración completa validada; conteos interiores antes de duplicar. `CalculateVolume` necesita geometría y cachea el resultado. La tupla de entrada y NPZ están detallados en [AppBackend/CONTRATOS.md](../AppBackend/CONTRATOS.md).

## Propiedades del resultado

| Propiedad | Contenido |
|---|---|
| `ol_config` | JSON serializado de opciones completas |
| `ol_role` | `generated_geometry_mm` (base reparada: `contact_surface_mm`) |
| `ol_inner_vertices`, `ol_inner_faces` | Conteos antes de engrosar; se ponen a cero tras voxel |
| `ol_validation` | `Pendiente` al generar; JSON de informe al comprobar |
| `ol_scope` | Texto de alcance geométrico sin predicción de resistencia/fabricación |
| `ol_source_object` | Nombre del objeto base |
| `ol_surface_step_mm` | Paso efectivo solicitado a la preparación |
| `ol_removed_tiny_fragments` | Vértices de residuos retirados después de voxel |
| `ol_reconstruction_resolution_mm` | Voxel efectivo usado |

Nombres: resultado `OL_Ortesis`, datablock `OL_Geometria`, fuente histórica `OL_SuperficieInterior`, atributo antiguo `ol_offset_normal`. Estas propiedades son metadata, no un sistema de versiones ni historial de cambios. Al reutilizar un objeto, propiedades de un voxel anterior pueden permanecer si la nueva generación no las sobrescribe: no inferir el modo actual solo a partir de su presencia; consultar `ol_config`.

## Informe y sidecar

```json
{
  "parameters": {"pattern": "SOLID", "solid_mm": 2.4},
  "validation": {
    "open_edges": 0,
    "nonmanifold_edges": 0,
    "degenerate_faces": 0,
    "triangles": 12,
    "components": 1,
    "triangle_crossings": 0,
    "ok": true
  },
  "stl_units": "mm"
}
```

Ejemplo abreviado: en un sidecar real `parameters` contiene las 17 opciones. `ortesis.stl` produce `ortesis.stl.json`, no `ortesis.json`. El informe pertenece a esa comprobación y puede quedar obsoleto si se edita la malla; exportar lo vuelve a medir. Un STL no declara unidades internamente; el JSON documenta la convención. Autoescala aplicada y huella de la base no están incluidas en `parameters`: para reproducibilidad completa registrar también la superficie y la decisión de unidades.

## Familias de errores

| Área | Clases principales | Acción |
|---|---|---|
| Entorno/configuración | `EntornoBlenderRequerido`, `ConfiguracionInvalida` | Usar Blender o corregir JSON/entorno según el caso |
| Archivo | `ArchivoSuperficieNoEncontrado`, `ArchivoSuperficieIlegible` | Revisar ruta, claves y formato; el mensaje de archivo ausente conserva texto histórico de blend |
| Base | `SuperficieNoEsMalla`, `SuperficieSinCaras`, `SuperficieInvalida`, `SolidoCerrado`, `AristasNoManifold`, `VerticesSueltos`, `NormalesInvalidas`, `ModificadoresSinAplicar`, `EscalaSinAplicar` | Corregir entrada; Arreglar no convierte un sólido en capa abierta |
| Opciones | `ParametrosNoReconocidos`, `ParametroNoPositivo`, `ParametroNoFinito`, `PatronNoReconocido`, `PatronNoImplementado`, `CeldaDemasiadoPequena`, `NervaduraDemasiadoAncha`, `ResolucionNoPositiva`, `SemillaInvalida`, `BordeNegativo` | Ajustar parámetros y claves |
| Construcción | `GeometriaInconsistente`, `SuperficieEliminadaPorPatron`, `MallaNoConstruida` | Revisar datos, espesor y retícula |
| Reconstrucción | `ResolucionDemasiadoFina`, `GeometriaFragmentada`, `ReconstruccionFallida` | Revisar espesores/resolución o desactivar voxel y revisar geometría |
| Salida/métricas | `ModeloNoGenerado`, `MallaNoValida`, `ExportacionFallida`, `ModeloSinGeometria`, `MaterialInvalido` | Generar, validar y revisar destino/material |

Todas derivan de `OrtesisLabError`; el [índice de símbolos](SIMBOLOS.md) enumera su definición actual. Los operadores capturan `Exception`, notifican y cancelan; errores inesperados añaden traza al log.
