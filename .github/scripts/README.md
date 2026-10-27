# Automatización: tareas de Notion → issues de GitHub

El workflow `notion-to-issues.yml` crea una issue de GitHub por cada tarea de la
base **Tasksk** (Notion) del proyecto **OrtesisLab** que aún no tenga issue, y
escribe la URL de la issue de vuelta en la tarea (propiedad **GitHub Issue**).
Es idempotente: no duplica.

## Puesta en marcha (una sola vez)

1. **Crear una integración interna de Notion**
   - Ve a https://www.notion.so/my-integrations → *New integration* (tipo *Internal*).
   - Copia el *Internal Integration Secret* (empieza con `ntn_` o `secret_`).
2. **Compartir la base Tasksk con la integración**
   - Abre la base **Tasksk** en Notion → menú `•••` → *Connections* → agrega la integración.
3. **Agregar el secreto al repo**
   - GitHub → *Settings* → *Secrets and variables* → *Actions* → *New repository secret*.
   - Nombre: `NOTION_TOKEN`. Valor: el secreto de la integración.
4. **Permitir que Actions cree issues** (si hiciera falta)
   - *Settings* → *Actions* → *General* → *Workflow permissions* → *Read and write*.

## Ejecutar

- Manual: pestaña **Actions** → *Notion → GitHub Issues* → *Run workflow*.
- Automático: diario (cron `17 13 * * *`, UTC). Ajusta el cron en el `.yml`.

## Notas

- El token de GitHub lo provee Actions (`GITHUB_TOKEN`); no hace falta un PAT.
- Las etiquetas `P1`/`P2` se crean solas con la primera issue.
- Para probar sin crear nada: corre el script con `DRY_RUN=1`.
- IDs usados (no son secretos): base Tasksk y página del proyecto OrtesisLab, en el `.yml`.
