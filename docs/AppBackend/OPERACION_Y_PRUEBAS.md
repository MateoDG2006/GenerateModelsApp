# Operación y pruebas del backend

## Entorno reproducible

Desde la raíz, con uv disponible:

```powershell
uv python install 3.14
uv sync --locked
uv run reflex run
```

Abrir `http://localhost:3000`; el backend de desarrollo normalmente escucha en 8000. Blender no es requisito web. La aplicación necesita `assets/superficie_interior_mm.npz`, `assets/visor.html`, los JSON del paquete y permiso de escritura en subidas/logs. El visor necesita descargar Three.js desde unpkg; el núcleo no necesita ese CDN.

`pyproject.toml` admite Python ≥3.14 y mínimos de paquetes; usar `uv.lock` para reproducir. El entorno inspeccionado tiene Reflex 0.9.12 y NumPy 2.5.3. No modificar `.web/` como fuente de la aplicación ni usar el comando `generatemodelsapp` para arrancarla: ese comando solo saluda.

Antes de crear/modificar código Reflex o iniciar/depurar procesos, aplicar las skills del repositorio `reflex-docs`, `setup-python-env` y `reflex-process-management` según [AGENTS.md](../../AGENTS.md). Esta revisión documental no requiere iniciar un servidor.

## Comprobación funcional

1. Cargar la página: formulario con valores predeterminados y superficie incluida, sin malla aún.
2. Previsualizar `SOLID`: ficha con volumen/peso/precio y STL en visor.
3. Cargar STL abierto, alternar autoescala y generar: comprobar que conserva el archivo original y cambia la interpretación en la siguiente ejecución.
4. Probar el lote de 12 variantes de [CONTRATOS.md](CONTRATOS.md): progreso por variante, primera válida visible y errores aislados.
5. Comparar tres resultados; el cuarto muestra límite. Repetir un botón Comparar quita esa vista.
6. Descargar STL y comprobar que tiene longitud `84 + 50*T`; esto valida formato, no toda su topología.
7. Reiniciar proceso: verificar disponibilidad de assets/subidas según el despliegue; no asumir recuperación del lote o de fichas.

Estas acciones son un procedimiento de aceptación; no se presentan como pruebas de navegador ejecutadas en esta revisión.

## Pruebas existentes y trazabilidad

```powershell
uv run python -m unittest discover -s tests
python scripts/VerificarDocumentacion.py
```

| Archivo de prueba | Evidencia que aporta |
|---|---|
| `test_generador_web.py` | 13 casos: combinaciones y límites, semilla, STL, lectura STL/NPZ, autoescala, archivo `Test.stl`, expansión e índices inválidos |
| `test_escala_malla.py` | 12 casos: factores decimales, desactivación, selección por paso y conservación de tamaño ante presupuesto |
| `test_nucleo.py` | 14 casos: equivalencia algorítmica con referencia, catálogo, validación, importación sin Blender, volumen/material |
| `test_refinador_malla.py` | 3 casos: subdivisión, rejilla recortada y escala/paso |
| `test_suavizado_borde.py` | 4 casos: dientes, tramo recto, borde corto e integración del marco |
| `test_superficie_abierta.py` | 5 casos: cierre local del espesor, inversión, rechazo de capas/duplicados/sueltos/orientación |

Línea base: **51 pruebas aprobadas el 2026-10-13** usando `.venv/Scripts/python.exe -m unittest discover -s tests`. No se ejecutaron integraciones Blender ni navegador; no confundir logs versionados con evidencia nueva. Ver [registro](../Agents/REGISTRO_CAMBIOS.md).

## Diagnóstico

| Síntoma | Revisar |
|---|---|
| `EntornoBlenderRequerido` al importar web | Importación accidental de adaptadores Blender; entrada debe ser `web.GenerateModelsApp` |
| No aparece base incluida | Existencia y claves del NPZ en assets |
| Superficie rechazada | Debe ser abierta, orientada y conectada; un STL de una ortesis con espesor no sirve como base |
| Demora o mucha memoria | Paso, ancho de nervadura, número de caras, tamaño de celda y número de variantes |
| Visor vacío con métricas correctas | Consola de iframe, CDN Three.js, URL del STL, HTTP backend y WebGL |
| JSON de configuración inválido | Claves exactas en defaults/límites/registro; no continuar con valores parciales |
| Caché después de cambiar configuración | Reiniciar proceso; `Configuracion.Recargar` no invalida por sí sola refinados web |
| Disco crece tras muchas sesiones | No existe limpieza automática de subidas; definir retención antes de borrar trabajo |

Logs: `ortesislab.<subsistema>`, consola INFO y archivo DEBUG `GenerateModelsApp/logs/ortesislab.log`, según `config/registro.json`. Los errores previstos se registran al construirse. La configuración de logging se inicia una vez; cambiar el JSON requiere tener en cuenta esa inicialización, no solo vaciar la caché de configuración.

## Despliegue y recuperación

El repositorio no contiene una receta Docker, infraestructura cloud, CI ni servicio gestionado configurado. Un despliegue debe mantener accesibles ambos lados de Reflex, sus eventos y archivos; asegurar almacenamiento coherente si hay varias instancias; y definir TLS, autenticación, cuotas y retención. Son decisiones de despliegue pendientes. No hay SLA ni garantía de «20 segundos»: ese texto existe en el estado inicial pero no es una medición por modelo.
