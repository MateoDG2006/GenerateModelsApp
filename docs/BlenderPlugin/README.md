# BlenderPlugin

**Propósito:** explicar el complemento OrtesisLab 1.3.0 para Blender ≥5.0, su núcleo compartido y la transformación de una superficie abierta en una pared con patrón.

| Documento | Contenido |
|---|---|
| [LEEME.md](LEEME.md) | Guía breve de uso distribuida en el ZIP |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Registro, objetos, operadores y secuencias UML |
| [MODULOS.md](MODULOS.md) | Todas las carpetas y archivos del paquete, dependencias y funciones |
| [ALGORITMOS.md](ALGORITMOS.md) | Matemática, estructuras de datos, recorte, engrosado, voxel y validación |
| [PARAMETROS.md](PARAMETROS.md) | Cada control, predeterminado, rango, efecto e interacciones |
| [API_Y_DATOS.md](API_Y_DATOS.md) | API Python, propiedades de objeto, configuración y exportación |
| [OPERACION_Y_PRUEBAS.md](OPERACION_Y_PRUEBAS.md) | Instalación, uso, diagnóstico e integración Blender |
| [SIMBOLOS.md](SIMBOLOS.md) | Índice generado de todas las clases, funciones y métodos |
| [CONFIGURACION_GENERADA.md](CONFIGURACION_GENERADA.md) | Valores exactos de los cuatro JSON, generados automáticamente |

La [guía breve](LEEME.md) se distribuye dentro del ZIP. La documentación extensa permanece en el repositorio. El núcleo también es usado por [AppBackend](../AppBackend/README.md); Blender y Reflex son consumidores independientes, no procesos conectados por RPC.
