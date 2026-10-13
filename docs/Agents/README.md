# Agents

Documentación para que agentes y desarrolladores mantengan el repositorio y sus explicaciones sincronizados. Las instrucciones de entrada permanecen en [AGENTS.md](../../AGENTS.md).

| Archivo | Propósito |
|---|---|
| [MANTENIMIENTO.md](MANTENIMIENTO.md) | Cambios que requieren actualizar documentación, matriz de impacto y secuencia de actualización |
| [ESTANDAR_DOCUMENTACION.md](ESTANDAR_DOCUMENTACION.md) | Estructura común, convenciones UML/Mermaid, trazabilidad y glosario |
| [INVENTARIO.md](INVENTARIO.md) | Propósito de cada archivo y carpeta; tabla regenerada, descripciones escritas a mano |
| [Scripts/GenerarIndices.py](Scripts/GenerarIndices.py) | Regenera inventario, índices de símbolos y configuración; comprueba enlaces |
| [GUIA_REFLEX.md](GUIA_REFLEX.md) | Índice de documentación oficial del framework para consultar APIs |
| [REGISTRO_CAMBIOS.md](REGISTRO_CAMBIOS.md) | Historial documental y pruebas realmente ejecutadas |

Después de actualizar la prosa y los diagramas del cambio, ejecutar desde la raíz:

```powershell
python docs/Agents/Scripts/GenerarIndices.py
python docs/Agents/Scripts/GenerarIndices.py --comprobar
```

Detalle en [MANTENIMIENTO.md](MANTENIMIENTO.md). Respetar también los bloqueos y resoluciones de [audit](../audit/README.md).

Revisión inicial: `2b74669`, 2026-10-13; proyecto Python 0.1.0, complemento Blender 1.3.0, entorno Reflex 0.9.12 y NumPy 2.5.3. Los cambios posteriores están en el registro.
