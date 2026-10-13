# RES-2026-10-13-002 — Orden de pruebas y assets de prueba

Fecha: 2026-10-13 (America/Bogota)
Auditorías: AUD-2026-10-13-001
Estado: EN_CURSO
Responsable: agente de implementación, por instrucción del usuario (Mateo Del Giudice)

## Autorización para corregir

Instrucción explícita del usuario, 2026-10-13:

> «Necesito que dentro de la carpeta de test le demos un orden sobre que afecta
> cada test, para que sea mas explicativo y facil de revisar, los assets que
> estan fuera de los test tienen que ir igual encarpetados en una carpeta de
> assets»

Alcance autorizado: trasladar los archivos de `tests/` a subcarpetas según el
área que cubren, y dejar los fixtures y la evidencia histórica en
`tests/assets/`. En los archivos auditados solo se ajustan rutas e imports que
el traslado rompe. No se cambia la lógica de las pruebas, no se regeneran logs
ni `resultado_blender.json`, y no se cierran los hallazgos de
`AUD-2026-10-13-001`.

`assets/visor.html`, `assets/favicon.ico` y `assets/superficie_interior_mm.npz`
ya están en `assets/`. No se mueven: Reflex publica `/visor.html` y
`/favicon.ico` desde esa raíz, y el núcleo carga
`assets/superficie_interior_mm.npz`.

## Archivos y hallazgos

Huella anterior: SHA-256 del archivo en disco justo antes de este traslado.
La verificada se completa al terminar el trabajo.

| Archivo desde la raíz (antes) | Hallazgos | SHA-256 anterior | Destino |
|---|---|---|---|
| `tests/test_nucleo.py` | A-19, revisión pendiente | `8126b4d236823805d53ee414f4dbbd9052068ca00a8723aec5e4eecf5948b047` | `tests/nucleo/test_nucleo.py` |
| `tests/test_escala_malla.py` | A-14, A-19 | `3d5f0d06fd584cd8de69aa87be0cc97495ae9a8948c230dd8a332ba88f592d47` | `tests/geometria/test_escala_malla.py` |
| `tests/test_refinador_malla.py` | A-19 | `f419c427927ddf4307bccd635c22e25fe0720aefa4dbbc653c75118c90e82b81` | `tests/geometria/test_refinador_malla.py` |
| `tests/test_suavizado_borde.py` | A-19 | `fda99a8a497f97ca8eb25db3467bfec0ddfa5a8f8f2e6abe1a79c2a1f4ea6630` | `tests/geometria/test_suavizado_borde.py` |
| `tests/test_superficie_abierta.py` | A-19 | `f55834ed043b1a073ee1c9765c582da15704a393a1dedfa7be995d11ff6b77cc` | `tests/geometria/test_superficie_abierta.py` |
| `tests/test_generador_web.py` | A-19; también en RES-2026-10-13-001 | `4894eca18f684fd1f23cb61b6bfd979f71f22f4a375422d5f7833519a98a51b2` | `tests/aplicacion_web/test_generador_web.py` |
| `tests/blender_paquete_zip.py` | A-19 | `7c2b92c20b06e963018bb68e1684a569fe8b196205c913445a11b0f4f768cfcf` | `tests/blender/blender_paquete_zip.py` |
| `tests/blender_superficie_abierta.py` | A-19 | `0e3c0b60942bc65771ea4d3f941e51418238f08b474f09e8800e0fed2d622dd7` | `tests/blender/blender_superficie_abierta.py` |
| `tests/Test.stl` | Revisión sin hallazgos, pendiente | `38c9ac7dee2c4a2ccb5928a0bbd9d51f193a7cb01043ec6271fd3d1e339a2f8a` | `tests/assets/Test.stl` |
| `tests/resultado_blender.json` | Revisión sin hallazgos, pendiente | `36af17050270b52225ce1b91581f37ec75dafdf37df27f3ad0a66b07c202819f` | `tests/assets/resultado_blender.json` |
| `tests/blender_ejecucion.log` | Revisión sin hallazgos, pendiente | `45b1369c3c960572fc24231e14a149bb16017adb6dc9e3d71a60d86490482bbc` | `tests/assets/blender_ejecucion.log` |
| `tests/nucleo_ejecucion.log` | A-19 | `40c1a9351cb6fc5b1d947e5526337526450382d89308b0f406e4348d823ddef8` | `tests/assets/nucleo_ejecucion.log` |
| `tests/zip_ejecucion.log` | Revisión sin hallazgos, pendiente | `6ad04ad13d423234e9f5e4df18aeb229edcc9b8d0595b2772c821627c028608c` | `tests/assets/zip_ejecucion.log` |
| `README.md` | Revisión sin hallazgos, pendiente | `a90c80f6f58419f87b6d089fd9446400b64e2488ca17f6475c91d69c07f96dd4` | Misma ruta; solo el comando de Blender y el enlace al índice |

Fuera del inventario, y por tanto sin bloqueo: `tests/apoyo_persistencia.py`,
`tests/test_almacen_import.py`, `tests/test_lotes_trabajador.py` y
`tests/test_propiedad_datos.py` pasan a `tests/persistencia/`.

## Decisión y trabajo realizado

Traslado de ubicación, sin cambiar aserciones. Los hallazgos siguen abiertos.

| Destino | SHA-256 verificada | Cambio de contenido |
|---|---|---|
| `tests/nucleo/test_nucleo.py` | `76109edf3dd99f6be0b5beb2b55ff0e553a82c882be35e09d6cba37defe515db` | `parents[2]` para seguir apuntando a la raíz |
| `tests/geometria/test_escala_malla.py` | `3d5f0d06fd584cd8de69aa87be0cc97495ae9a8948c230dd8a332ba88f592d47` | Ninguno |
| `tests/geometria/test_refinador_malla.py` | `f419c427927ddf4307bccd635c22e25fe0720aefa4dbbc653c75118c90e82b81` | Ninguno |
| `tests/geometria/test_suavizado_borde.py` | `fda99a8a497f97ca8eb25db3467bfec0ddfa5a8f8f2e6abe1a79c2a1f4ea6630` | Ninguno |
| `tests/geometria/test_superficie_abierta.py` | `f55834ed043b1a073ee1c9765c582da15704a393a1dedfa7be995d11ff6b77cc` | Ninguno |
| `tests/aplicacion_web/test_generador_web.py` | `14060580f579369d6c642b8c8829f32ce85f9efd5f2aa7612be00d90c55fa311` | Import de `tests.persistencia` y lectura de `tests/assets/Test.stl` |
| `tests/blender/blender_paquete_zip.py` | `bc73ae7b40b03e935631b882d2325ebd321a50c47c7898757e37f4541676f1a0` | `parents[2]` |
| `tests/blender/blender_superficie_abierta.py` | `79964aad678b8a67d52c70786f030c2ab286fa36ef3b8085a2501c194c36e709` | `parents[2]` y escritura en `tests/assets/resultado_blender.json` |
| `tests/assets/Test.stl` | `38c9ac7dee2c4a2ccb5928a0bbd9d51f193a7cb01043ec6271fd3d1e339a2f8a` | Ninguno |
| `tests/assets/resultado_blender.json` | `36af17050270b52225ce1b91581f37ec75dafdf37df27f3ad0a66b07c202819f` | Ninguno |
| `tests/assets/blender_ejecucion.log` | `45b1369c3c960572fc24231e14a149bb16017adb6dc9e3d71a60d86490482bbc` | Ninguno |
| `tests/assets/nucleo_ejecucion.log` | `40c1a9351cb6fc5b1d947e5526337526450382d89308b0f406e4348d823ddef8` | Ninguno |
| `tests/assets/zip_ejecucion.log` | `6ad04ad13d423234e9f5e4df18aeb229edcc9b8d0595b2772c821627c028608c` | Ninguno |
| `README.md` | `33f259cfb1e826674df7b7739cdb6c4d219fe18a808bbaf828cd01d76cc5eb38` | Comando de Blender y enlace a `tests/README.md` |

La carpeta de la aplicación web se llama `aplicacion_web` y no `web`: con
`unittest discover -s tests`, el directorio de pruebas queda al frente de
`sys.path` y una carpeta `web` ocultaría el paquete de la aplicación.

`assets/visor.html`, `assets/favicon.ico` y `assets/superficie_interior_mm.npz`
no se movieron. `assets/README.md` explica por qué siguen en esa raíz.

## Verificación

Ejecutada el 2026-10-13 desde la raíz del repositorio:

- `.venv\Scripts\python.exe -B -m unittest discover -s tests`: 73 pruebas
  aprobadas, ninguna omitida, en 32,2 s, contra PostgreSQL 17 en Docker.
- Las huellas de `Test.stl`, `resultado_blender.json` y los tres logs coinciden
  con las de antes del traslado.
- No se ejecutaron `tests/blender/blender_superficie_abierta.py` ni
  `tests/blender/blender_paquete_zip.py`.

## Riesgo residual y cierre

Los hallazgos de `AUD-2026-10-13-001`, incluidos A-14 y A-19, quedan abiertos.
Este registro documenta un traslado autorizado; no es un cierre de auditoría.
Los archivos de la tabla siguen bloqueados para cualquier cambio que no esté
en este alcance.
