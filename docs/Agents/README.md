# Agents

Documentación para que agentes y desarrolladores mantengan el repositorio y sus explicaciones sincronizados. Las instrucciones de entrada permanecen en [AGENTS.md](../../AGENTS.md).

| Archivo | Propósito |
|---|---|
| [MANTENIMIENTO.md](MANTENIMIENTO.md) | Cambios que requieren actualizar documentación, matriz de impacto, proceso automático y verificación |
| [ESTANDAR_DOCUMENTACION.md](ESTANDAR_DOCUMENTACION.md) | Estructura común, convenciones UML/Mermaid, trazabilidad y glosario |
| [INVENTARIO.md](INVENTARIO.md) | Propósito de cada archivo y carpeta; generado desde el repositorio |
| [GUIA_REFLEX.md](GUIA_REFLEX.md) | Índice de documentación oficial del framework para consultar APIs |
| [REGISTRO_CAMBIOS.md](REGISTRO_CAMBIOS.md) | Historial documental y pruebas realmente ejecutadas |
| [linea_base_documental.json](linea_base_documental.json) | Huellas de fuentes revisadas para detectar deriva |

Después de actualizar la prosa y los diagramas del cambio, ejecutar desde la raíz:

```powershell
python scripts/VerificarDocumentacion.py --actualizar
python scripts/VerificarDocumentacion.py
```

El script regenera hechos extraíbles; el agente debe explicar el significado del cambio. Respetar también los bloqueos y resoluciones de [audit](../audit/README.md).

Línea base inicial: `2b74669`, revisada el 2026-10-13; proyecto Python 0.1.0, complemento Blender 1.3.0, entorno Reflex 0.9.12 y NumPy 2.5.3. Las huellas actuales están en el manifiesto y los cambios posteriores en el registro.
