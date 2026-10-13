# Resoluciones

**Fecha:** 2026-10-13. **Resoluciones de cierre de esta auditoría:** ninguna.

Este índice y la plantilla siguiente **no resuelven ni desbloquean archivos**.
Los hallazgos de `AUD-2026-10-13-001` permanecen abiertos.

El [registro de reorganización documental](2026-10-13-reorganizacion-documental.md)
procede de trabajo concurrente autorizado por el usuario. Su alcance se limita
a traslados y referencias; no cierra los hallazgos de código de esta auditoría.

[RES-2026-10-13-002](2026-10-13-resolve-organizar-pruebas.md) autoriza el
traslado de las pruebas a subcarpetas y de sus fixtures a `tests/assets/`.
Sigue en curso y no cierra hallazgos.

## Protocolo

1. Identificar todas las auditorías que incluyan cada archivo y todos los
   hallazgos aplicables. Usar los inventarios e informes, no solo sus títulos.
2. Documentar la decisión y el alcance en un archivo
   `AAAA-MM-DD-resolve-<identificador>.md`.
3. Si se requiere editar un archivo bloqueado, obtener una instrucción explícita
   del usuario y registrarla antes de editar. Un resolve `EN_CURSO` sin esa
   instrucción no habilita cambios. No autoaprobar una excepción.
4. Ejecutar la corrección autorizada y las verificaciones indicadas, preservando
   datos originales y cambios ajenos. Registrar resultados reales, incluidos
   fallos y pruebas no ejecutadas.
5. Cerrar únicamente los archivos y hallazgos respaldados por la evidencia. Si
   queda un punto pendiente de cualquier auditoría, ese archivo sigue bloqueado
   para cambios generales.

## Plantilla orientativa

```markdown
# RES-AAAA-MM-DD-NNN — título

Fecha: AAAA-MM-DD (America/Bogota)
Auditorías: AUD-...
Estado: EN_CURSO | RESUELTO | DESCARTADO_CON_EVIDENCIA | RIESGO_ACEPTADO
Responsable: nombre o rol explícito

## Archivos y hallazgos

| Archivo desde la raíz | Hallazgos | SHA-256/revisión anterior | SHA-256/revisión verificada |
|---|---|---|---|
| ruta exacta | A-... o revisión sin hallazgos | ... | ... |

## Autorización para corregir (si había bloqueo)

Instrucción explícita del usuario, fecha, referencia y alcance autorizado.
No inventar autorización ni interpretar el silencio como aprobación.

## Decisión y trabajo realizado

Causa, tratamiento concreto y relación con cada hallazgo.
Un archivo sin hallazgos requiere una decisión explícita sobre su revisión.

## Verificación

Comandos, entorno, entradas, resultados observados y evidencias enlazadas.
Comparar el comportamiento antes/después y consignar pruebas no ejecutadas.

## Riesgo residual y cierre

Qué queda pendiente y qué archivos siguen bloqueados.
Para RIESGO_ACEPTADO: autorización explícita del usuario, motivo, controles,
responsable y fecha de revisión del riesgo.
```

No crear un resolve ficticio para cerrar esta auditoría documentalmente. El
informe inicial registra problemas existentes; no implementa sus correcciones.
