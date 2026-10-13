<!-- reflex managed begin (do not edit inside this block; add custom content outside the markers) -->
# Agents

This project uses the **Reflex agent skills** � up-to-date knowledge for building full-stack Python web apps with [Reflex](https://reflex.dev). Install them first, then use them as described below.

## Installing the Skills

Before working on this project, make sure the Reflex skills are available to you.

### Claude Code

If the skills are not already available, install them yourself by running these shell commands:

```bash
claude plugin marketplace add reflex-dev/agent-skills
claude plugin install reflex@reflex-agent-skills
```

Newly installed plugins load on the next session. After installing, tell the user to restart the session so the skills auto-load; until then, read the skill files directly from `~/.claude/plugins/` when you need them.

### Other agents (Cursor, OpenCode, Codex, Pi)

```
npx skills add reflex-dev/agent-skills
```

Or clone https://github.com/reflex-dev/agent-skills and copy the `skills/` folders into your agent's skill directory (see the repo README for paths).

### Verifying

Before writing or editing any Reflex code, confirm these three skills are available: `reflex-docs`, `setup-python-env`, and `reflex-process-management`. If they are not, STOP and run the install step above � do not proceed without them.

## Using the Skills

### Reflex documentation

For anything about Reflex APIs � components, state management, events, styling, database, routing, authentication � use the **reflex-docs** skill rather than relying on memory. It carries current, version-accurate docs.

### Initializing a new Reflex project

When starting a new Reflex project or setting up a development environment, you **must** follow the **setup-python-env** skill before doing anything else.

Do not skip any steps. Do not assume a virtual environment or Reflex is already available � always verify first by following the skill's instructions in order.

After the environment is ready and Reflex is installed, run:

```bash
reflex init
```

Then proceed with the user's request.

Additional in the folder docs there is a complete guide for the location of all resources from Relfex as a knowledge base

### Managing a Reflex process

When you need to compile, run, reload, or debug a Reflex application, follow the **reflex-process-management** skill for the correct sequence and error investigation steps.
<!-- reflex managed end -->

## Documentación obligatoria en cada cambio fundamental

La documentación canónica está en `docs/AppBackend`, `docs/AppFrontend` y
`docs/BlenderPlugin`. Leer `docs/Agents/MANTENIMIENTO.md` y aplicar su matriz de impacto.
Cuando se cambie lógica fundamental, arquitectura, parámetros/defaults/límites,
contratos de datos, eventos, UI, validación, exportación o empaquetado, actualizar
automáticamente la documentación afectada en la misma iteración, sin esperar
otra solicitud del usuario. Esto incluye explicaciones, diagramas UML/flujo,
catálogos y evidencia de pruebas. Describir solo el comportamiento implementado.

Antes de terminar:
1. Revisar documentación y diagramas a partir del código vigente; usar CodeGraph
   primero si existe `.codegraph/`, según instrucciones de la sesión.
2. Actualizar `docs/Agents/REGISTRO_CAMBIOS.md` con pruebas realmente ejecutadas.
3. Ejecutar `python scripts/VerificarDocumentacion.py --actualizar` para regenerar
   inventario, símbolos, configuración y línea base después de la revisión.
4. Ejecutar `python scripts/VerificarDocumentacion.py` y resolver la deriva.

No aceptar una nueva línea base como sustituto de explicar el cambio. El script
no comprende semántica ni reescribe la prosa. No editar a mano archivos generados.
Mantener `docs/BlenderPlugin/LEEME.md` autocontenido porque se distribuye dentro del ZIP Blender.
No presentar logs o resultados históricos como validación de la versión actual.

## Bloqueo por auditorías pendientes (2026-10-13)

Antes de modificar cualquier archivo, consultar `docs/Audit/audits/`, sus
inventarios de alcance y `docs/Audit/resolves/`. La política completa está en
`docs/Audit/README.md`.

- Un archivo incluido en una auditoría queda **bloqueado para edición** mientras
  esa auditoría no tenga una resolución válida para ese archivo en
  `docs/Audit/resolves/`. El bloqueo incluye refactorizaciones, formato,
  renombres, movimientos, eliminaciones, regeneración y sustitución por copias.
- La resolución debe identificar auditoría, archivo, todos sus hallazgos,
  decisión, responsable, fecha, revisión/huella y evidencias de verificación.
  Solo `RESUELTO`, `DESCARTADO_CON_EVIDENCIA` o `RIESGO_ACEPTADO` cierran el
  alcance indicado; aceptar riesgo requiere autorización explícita del usuario.
  Un archivo vacío, plantilla, plan, trabajo en curso o resolución parcial no
  desbloquea los puntos pendientes. Si hay varias auditorías, todas deben tener
  resolución válida para ese archivo.
- El bloqueo también cubre archivos auditados sin hallazgos individuales: debe
  existir una resolución de su revisión. No inferir que ausencia de hallazgos
  significa cierre. La auditoría inicial y su inventario están abiertos.
- Leer archivos y ejecutar comprobaciones aisladas está permitido. Se pueden
  crear registros de auditoría y resolución; conservar los informes históricos
  y añadir adendas para rectificaciones. No borrar ni alterar evidencias para
  eludir el bloqueo, ni cambiar esta regla para habilitar una edición prohibida.
- Si corregir un hallazgo exige editar un archivo bloqueado, informar del bloqueo
  y obtener una instrucción explícita del usuario que habilite esa corrección.
  Registrar esa instrucción y su alcance en `resolves` antes de editar; mantener
  los hallazgos abiertos hasta completar y verificar el trabajo. Una petición
  genérica de cambios no es autorización para ignorar esta regla.

La incorporación inicial de esta regla y de `docs/Audit/` está autorizada por la
solicitud de auditoría del 2026-10-13. Esta excepción de creación termina con
esta entrega; no habilita correcciones del código auditado.
