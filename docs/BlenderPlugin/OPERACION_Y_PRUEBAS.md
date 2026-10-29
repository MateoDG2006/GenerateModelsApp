# Operación y pruebas del complemento

## Construcción e instalación

Desde la raíz del repositorio:

```powershell
uv run python scripts/EmpaquetarBlender.py
```

Instalar `GenerateModelsApp.zip` con **Edit > Preferences > Add-ons > Install from Disk** y activar OrtesisLab. Reiniciar Blender después de sustituir una versión previa evita módulos antiguos cargados. `bl_info` vigente declara 1.3.0 y Blender mínimo 5.0. La versión 0.1.0 de `pyproject.toml` corresponde al proyecto Python, no a la del complemento.

Alternativa desde el repositorio, dentro de Blender: ejecutar `scripts/EjecutarOrtesisLab.py` desde disco. El complemento requiere NumPy en el entorno Blender pero no Reflex. No instalar solo `OrtesisLab.py` ni copiar un bloque suelto al editor de texto.

## Preparar y generar

1. Crear/importar una única capa de caras conectadas, sin espesor y con aberturas modeladas en mano/dedo. El complemento no identifica anatomía ni retira tapas.
2. Trabajar con coordenadas interpretadas en mm. Metric, Unit Scale 0.001 facilita presentación; por sí sola no garantiza que un STL entrante tenga tamaño correcto. Eje longitudinal Y y abertura hacia Z favorecen el patrón XY.
3. En Object Mode aplicar modificadores y escala. Si hay duplicados, sueltos o fragmentos, seleccionar base y usar Arreglar: esta acción conserva componente mayor y modifica la entrada.
4. En **N > Ortesis**, Usar malla seleccionada o elegir `source`. Revisar el aviso de autoescala y dimensiones. La generación escala/refina una copia; la base queda oculta pero conserva su geometría.
5. Ajustar controles con [PARAMETROS.md](PARAMETROS.md). Empezar con `repair=False` permite evaluar el cascarón antes de aproximarlo con voxel.
6. Pulsar Generar / actualizar. El resultado único se llama `OL_Ortesis`; un resultado previo se reemplaza.
7. Comprobar malla. Confirmar contornos y ausencia de techos de mano/dedo visualmente, además de `ok` geométrico.
8. Exportar STL en mm. Verificar que existen STL y `*.stl.json`. La exportación vuelve a validar y bloquea defectos detectados.

Para cambiar la forma, mostrar la base en Outliner, editar caras, volver a Object Mode y generar. No usar el resultado engrosado como base. No hay generación automática continua.

## Integraciones reproducibles

Con Blender en PATH:

```powershell
blender --factory-startup --background --python-exit-code 1 --python tests/blender/blender_superficie_abierta.py
blender --factory-startup --background --python-exit-code 1 --python tests/blender/blender_paquete_zip.py
```

`blender_superficie_abierta.py` usa una probeta de bandeja con canal lateral de dedo, cinco patrones, con/sin capa, registro y conservación de base. Examina que no se añadan techos sobre canales y la validez de las paredes. No es un modelo anatómico nuevo ni acredita todos los escenarios posibles.

`blender_paquete_zip.py` extrae el ZIP en una carpeta temporal de pruebas, confirma importación aislada, ausencia de NPZ/bytecode, versión, registro, generación desde plano y exportación. Puede usar `ORTESISLAB_ZIP` para apuntar a otro paquete. Generar el ZIP antes de ejecutarla si ha cambiado el código; probar un ZIP histórico no valida las fuentes actuales.

Las pruebas de núcleo, geometría, web y persistencia se ejecutan con `uv run python -m unittest discover -s tests`. El mapa de carpetas está en [tests/README.md](../../tests/README.md). El 2026-10-13, antes de agruparlas, pasaron 51 en la revisión documental de esta guía. Las integraciones Blender anteriores quedan como procedimientos **no ejecutados en esta revisión documental**. `tests/assets/resultado_blender.json` y los logs versionados de esa carpeta son evidencia histórica. [Registro de revisión](../Agents/REGISTRO_CAMBIOS.md).

## Diagnóstico de fallos

| Mensaje/síntoma | Interpretación y siguiente paso |
|---|---|
| Base sólida cerrada | Eliminar segunda piel/tapas manualmente para obtener superficie abierta |
| Modificadores o escala pendientes | Aplicarlos antes de Generar; Arreglar hornea escala pero rechaza modificadores |
| Normales inconsistentes | Recalcular normales o reparar base y revisar orientación esperada |
| Dibujo deficiente en pocas caras | Reducir paso efectivo dentro del presupuesto; mirar densidad lograda |
| Voxel demasiado fino | Espesor mínimo/3 <0.15 o resolución solicitada demasiado baja; cambiar configuración |
| Fragmentación tras voxel | Residuos superan umbral; revisar celdas, espesor y continuidad; puede quedar resultado parcial |
| Pared cerrada pero canal tapado | Puede existir tapa en la base o voxel unir lados próximos; la comprobación no reconoce anatomía |
| Error de exportación JSON | El STL puede haberse escrito; corregir ruta/permisos y exportar otra vez |
| Cambios de código no aparecen | Reinstalar ZIP y reiniciar módulos/Blender |

El estado visible se trunca a 48 caracteres; consultar notificación completa y `GenerateModelsApp/logs/ortesislab.log`. La generación puede tardar según geometría; no hay tiempo garantizado ni mecanismo de cancelación propio.

## Criterios para una nueva entrega

Actualizar código, defaults/panel si cambian, algoritmos/contratos/diagramas y pruebas afectadas; regenerar índices y comprobar documentación según [MANTENIMIENTO.md](../Agents/MANTENIMIENTO.md). Si cambia código del complemento, empaquetar y ejecutar integraciones Blender en un entorno disponible. Si no se pueden ejecutar, dejar explícita la falta de evidencia; no copiar el resultado histórico como aprobación nueva.
