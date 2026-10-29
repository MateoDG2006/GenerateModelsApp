# AppBackend

**Propósito:** explicar el servidor de la aplicación Reflex, su persistencia (PostgreSQL, bucket S3, Redis), el trabajador de generación y cómo reutilizan el núcleo de OrtesisLab sin depender de `bpy`.

| Documento | Responde a |
|---|---|
| [ARQUITECTURA.md](ARQUITECTURA.md) | Procesos, identidad, cola de generación, archivos, caché y decisiones |
| [MODULOS.md](MODULOS.md) | Para qué sirve cada archivo y cada grupo de métodos del backend |
| [CONTRATOS.md](CONTRATOS.md) | Eventos, arrays, NPZ, STL, lotes, fichas, claves del bucket y errores |
| [DATABASE.md](DATABASE.md) | Modelo de datos (SQLAlchemy y Alembic), roles, migraciones, lotes, historial y operación Docker/Makefile; implementado con las desviaciones que indica |
| [OPERACION_Y_PRUEBAS.md](OPERACION_Y_PRUEBAS.md) | Instalación, servicios, ejecución, diagnósticos y cobertura |

Consultar también [inventario global](../Agents/INVENTARIO.md), [núcleo geométrico](../BlenderPlugin/ALGORITMOS.md), [frontend](../AppFrontend/README.md) y [mantenimiento obligatorio](../Agents/MANTENIMIENTO.md).
