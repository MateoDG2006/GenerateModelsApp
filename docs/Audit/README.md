# Auditorías y resoluciones

**Fecha de creación:** 2026-10-13, America/Bogota.

Esta carpeta conserva revisiones trazables del repositorio y sus resoluciones.
La regla obligatoria para agentes está en [AGENTS.md](../../AGENTS.md).

| Carpeta | Propósito | Entrada |
|---|---|---|
| `audits` | Alcance, motivos, hallazgos, evidencias y huellas de cada revisión | [Índice de auditorías](audits/README.md) |
| `resolves` | Decisiones concretas y verificables sobre los archivos auditados | [Protocolo de resolución](resolves/README.md) |

## Regla de edición

**Un archivo auditado sin una resolución válida en `resolves` no se puede editar.**
Se aplica al archivo completo, aunque el cambio propuesto esté fuera de las
líneas señaladas. Incluye movimientos, renombres, borrado, formato, regeneración
y cambios en binarios distribuidos. Si varias auditorías incluyen un archivo,
resolver solo una no lo desbloquea.

La revisión inicial es `AUD-2026-10-13-001`. Su
[inventario](audits/2026-10-13-inventario.json) enumera los archivos bloqueados y
sus SHA-256. Todos tienen estado `PENDIENTE`, incluidos los revisados sin un
hallazgo individual. La pertenencia al inventario, y no una coincidencia de
palabras en el informe, determina su alcance. Cambiar la huella no elimina la
pertenencia: un cambio sin resolución es un incumplimiento.

## Qué constituye una resolución

Debe identificar la auditoría y los archivos, tratar todos los hallazgos que
afectan a cada archivo, explicar la decisión, aportar pruebas y precisar la
revisión/huella verificada. Los estados de cierre son `RESUELTO`,
`DESCARTADO_CON_EVIDENCIA` y `RIESGO_ACEPTADO`; este último exige autorización
explícita del usuario y riesgo residual documentado. Un cierre parcial solo
cierra el alcance expresamente verificado. Una plantilla, un enlace a una tarea,
un plan o un registro `EN_CURSO` no cuentan como cierre.

Para corregir código bloqueado se necesita una instrucción explícita del usuario
que habilite esa corrección. Registrar primero esa autorización, archivos,
hallazgos y límites en un resolve `EN_CURSO`. Esa instrucción habilita únicamente
la corrección autorizada; no equivale a cerrar la auditoría ni permite cambios
ajenos. Tras corregir y verificar, completar la evidencia y el estado de cierre.
Sin esa instrucción, mantener el bloqueo. No declarar un problema resuelto antes
de comprobarlo para poder empezar a editarlo.

Se permiten lectura, revisión y comprobaciones aisladas, además de crear nuevos
registros en estas carpetas. Los informes son históricos: las rectificaciones se
registran como adendas enlazadas, conservando evidencia anterior. No reescribir
inventarios ni reglas para retirar un bloqueo sin trazabilidad.

## Alcance del mecanismo

Es una regla de trabajo y revisión registrada en `AGENTS.md`. Esta entrega no
instala hooks de Git, no cambia permisos del sistema de archivos y no incorpora
un control de CI. Por tanto, no impide técnicamente que una herramienta externa
escriba archivos: agentes y revisores deben comprobar la regla antes de actuar.
Un control automático futuro requiere una implementación específica.

Los documentos que se estaban creando concurrentemente durante esta revisión se
identifican como contexto en el informe y no forman parte del inventario
congelado. Los registros nuevos de `docs/Audit/` tampoco se incluyen en su propio
inventario; así puede mantenerse la trazabilidad sin un bloqueo recursivo.
