# Registro de cambios documentales

## 2026-10-13 — Atributos en el diagrama entidad-relación

Se completa el ER de `AppBackend/DATABASE.md` con todos los atributos de las doce entidades, tipos, PK/FK/UK y nulabilidad. Las claves únicas compuestas se identifican con comentarios de agrupación; la sección de integridad conserva el detalle de FK compuestas e índices parciales. Se contrasta la cobertura de atributos con el diccionario de tablas y se ejecuta la verificación documental. El cambio es únicamente documental; no implementa PostgreSQL ni modifica el esquema propuesto.

## 2026-10-13 — Propuesta de PostgreSQL sin ORM

Se incorpora `AppBackend/DATABASE.md` como propuesta expresamente no implementada: doce tablas de dominio, ER/UML/secuencia, contratos de repositorios SQL/Psycopg, archivos privados, versiones inmutables, lotes durables, intentos y leases, historial y futura vista Reflex. Se especifican Docker, migraciones SQL/dbmate, seed y targets Makefile únicamente como trabajo posterior.

Decisiones confirmadas por el usuario: no usar ORM y conservar binarios en almacenamiento privado con referencias, hashes, parámetros y resultados en PostgreSQL. Al aclararse que el alcance era solo documental, se retiraron todos los archivos nuevos de infraestructura que se habían empezado a crear; no quedan Makefile, Compose, migraciones ni seed de esa propuesta. No se cambia código de aplicación ni se ejecutan SQL o contenedores.

Se añade `erDiagram` a los tipos aceptados por el verificador documental. La verificación de enlaces, índices, parámetros y huellas se ejecuta tras regenerar hechos. No se presentan pruebas PostgreSQL/Docker como ejecutadas ni se cierran hallazgos de la auditoría independiente.

## 2026-10-13 — Reorganización inicial

Base de código revisada: `2b74669`. Árbol inicialmente sin cambios locales. Proyecto Python 0.1.0; Blender `bl_info` 1.3.0, mínimo 5.0; entorno local Reflex 0.9.12 / NumPy 2.5.3.

Se crean AppBackend, AppFrontend y BlenderPlugin con arquitectura, módulos, contratos, algoritmos, parámetros, operación e índices de símbolos. Se separan núcleo común, UI web y adaptadores Blender. La documentación previa aporta contexto, pero las afirmaciones técnicas se contrastan con la fuente actual y las skills/referencias oficiales Reflex.

Se aclaran diferencias observadas: macizo web sin refinamiento, voxel/validación final solo Blender, cachés web de proceso, NPZ internos en directorio de subidas, límites de UI frente a API, sidecar `*.stl.json`, parámetros ocultos aún validados y base conservada con borde de trabajo suavizado. El encabezado histórico de Cascaron tiene sentido de normal contrario a la expresión actual; se documenta `p+n*t` sin modificar el algoritmo.

Se añaden instrucciones persistentes y verificador local para regenerar índices/configuración/inventario y detectar deriva. No se modifica lógica de generación, interfaz de producto, dependencias, ZIP ni infraestructura de despliegue.

**Evidencia ejecutada:** suite Python existente, 51 pruebas aprobadas; verificación documental e índices; validación sintáctica Python del verificador; comprobaciones de que el verificador detecta deriva y enlaces rotos mediante fixtures temporales. Los resultados específicos finales se informan al entregar.

**Fuera de la ejecución de esta revisión:** integración Blender, recompilación Reflex, pruebas end-to-end de navegador y renderizado completo Mermaid. Los diagramas son fuente Mermaid editable; se comprueban bloques y tipos. Los logs/JSON históricos no se presentan como nuevas pruebas.

## Plantilla para futuras entradas

```text
AAAA-MM-DD — Cambio y motivo
Base de código / versión:
Fuentes y contratos afectados:
Documentos y diagramas actualizados:
Pruebas y validaciones ejecutadas (comando y resultado):
Comprobaciones no ejecutadas y limitación:
```

## 2026-10-13 — Organización final solicitada

Se concentra la mantenibilidad con agentes en `docs/Agents/`, junto con estándar, inventario, referencias Reflex, historial y manifiesto. La guía breve se traslada a `docs/BlenderPlugin/LEEME.md`. En la raíz de `docs/` queda solo el README que explica las carpetas.

Se actualizan enlaces, rutas de instrucciones y destinos del verificador. El empaquetador cambia exclusivamente la ruta fuente de la guía; conserva su ubicación `GenerateModelsApp/LEEME.md` dentro del ZIP. Se registra el alcance de esta reorganización en Audit/resolves sin cerrar hallazgos de la auditoría independiente.

## 2026-10-13 — Auditoría de código y bloqueo de archivos

Se incorpora [AUD-2026-10-13-001](../Audit/audits/2026-10-13-auditoria-base-codigo.md)
con alcance de partida en `2b74669`, inventario SHA-256, 22 hallazgos y evidencias.
Se crean `Audit/audits` y `Audit/resolves` y se añade la regla de bloqueo en
`AGENTS.md`. No se corrige lógica de producto ni se cierran hallazgos. El
protocolo y las plantillas de `resolves` no constituyen un cierre.

Evidencia de esta auditoría: 51 pruebas Python aprobadas; integración
`tests/blender_superficie_abierta.py` aprobada en Blender 5.2.2 con escritura del
JSON histórico redirigida a un temporal; reproducciones adicionales de entrada
NPZ, normales, topología, refinamiento, caché y exportación. Se contrastó el ZIP
con las fuentes antes de los traslados documentales concurrentes. No se ejecutó
`blender_paquete_zip.py`, navegador, escaneo CVE/licencias o build de wheel.
El informe conserva los detalles, criterios de cierre y límites del alcance.

Comprobación final: verificador documental aprobado (64 fuentes, 29 documentos,
13 diagramas), y validación propia de JSON, enlaces y bloques de `docs/Audit`.
Se verificó el nombre físico `Audit`, con A mayúscula, y se preservó el registro
de reorganización concurrente sin cerrar los hallazgos de código.
