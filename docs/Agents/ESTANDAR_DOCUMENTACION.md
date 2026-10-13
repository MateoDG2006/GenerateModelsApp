# Estándar documental

**Estado:** vigente desde 2026-10-13. **Ámbito:** todo el repositorio.

## Organización y referencias

La estructura adopta vistas de contexto, componentes, ejecución y despliegue de **arc42/C4**, diagramas de clases y secuencia de **UML**, contratos de entrada/proceso/salida y procedimientos operativos. Es una convención de documentación de software; no se afirma certificación de cumplimiento de una norma ISO/IEEE.

Cada carpeta tiene un `README.md` como índice. Los documentos de arquitectura identifican límites, dependencias y decisiones; los catálogos explican archivos y símbolos; los contratos definen formatos, unidades, errores y efectos; los manuales incluyen precondiciones, pasos y resultados observables. La fecha y línea base común están en [Agents/README.md](README.md), evitando fechas distintas copiadas en cada página.

Referencias metodológicas: [arc42](https://arc42.org/overview), [C4](https://c4model.com/), [UML 2.5.1 de OMG](https://www.omg.org/spec/UML/2.5.1). Se usan como estructura de comunicación, no como funcionalidades del producto.

## Reglas de contenido

- Describir el código actual; marcar expresamente una propuesta o una limitación.
- Preferir nombres reales y enlaces relativos al archivo fuente; los símbolos sirven como anclas estables de búsqueda. No depender solo de números de línea.
- Especificar unidades, tipos, valores predeterminados, validación, efectos secundarios y diferencias entre interfaces.
- Un parámetro compartido tiene su definición canónica en [BlenderPlugin/PARAMETROS.md](../BlenderPlugin/PARAMETROS.md); los otros sistemas explican su adaptación.
- Diferenciar validación de entrada, generación y validación de salida. Un fichero escrito no demuestra que la malla sea imprimible.
- No publicar rutas personales, archivos de pacientes, secretos ni resultados históricos como garantías actuales.
- Cada cambio fundamental actualiza explicaciones, diagramas, contratos, pruebas referenciadas y registro de cambios en la misma entrega.

## Convenciones de diagramas

Los bloques `mermaid` están embebidos junto a su explicación y se versionan como texto. `classDiagram` representa estructura UML; `sequenceDiagram`, colaboración temporal; `stateDiagram-v2`, estados; `flowchart`, flujo de código o despliegue conceptual; `erDiagram`, entidades y cardinalidades relacionales. Una flecha `A --> B` significa uso/dependencia o paso de datos según el título. Los diagramas no implican herencia salvo que la indiquen con `<|--`.

Se pueden leer en un visor Markdown con Mermaid. Si el visor no lo soporta, el bloque conserva la especificación editable y la explicación contigua permite seguir el flujo. La validación documental comprueba delimitadores y enlaces; no sustituye un renderizador de Mermaid.

## Glosario

| Término | Significado en este proyecto |
|---|---|
| Superficie base | Capa de triángulos conectada y abierta, sin espesor; no un sólido de doble piel |
| Cascarón | Volumen obtenido al duplicar la superficie con desplazamiento normal y unir bordes homólogos |
| Canal abierto | Espacio para introducir mano/dedo; puede coexistir con una pared material cerrada |
| Marco | Región maciza definida por distancia geodésica al contorno existente |
| Patrón | Campo de distancias en XY a los ejes de nervadura |
| Liner/capa | Fondo continuo de las celdas; no una tapa sobre el canal |
| Reparar base | Limpieza BMesh de la superficie de entrada, antes del espesor |
| Repair/voxel | Reconstrucción opcional del resultado; diferente de reparar la base |
| Estado Reflex | Datos de sesión y manejadores Python en servidor |
| Var Reflex | Expresión reactiva usada para compilar la interfaz; no un array de geometría |
| Ficha | Diccionario de cadenas para mostrar y descargar una variante |
| Sidecar | JSON hermano del STL Blender, llamado `modelo.stl.json` |
| Línea base | Huellas de los archivos revisados; no prueba automática de exactitud semántica |
