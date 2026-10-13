# Parámetros: propósito, efecto y restricciones

## Fuentes y reglas generales

Fuentes: [`OL_Settings` y panel](../../GenerateModelsApp/Interfaz.py), [`parametros_defecto.json`](../../GenerateModelsApp/config/parametros_defecto.json), [`ValidarOpciones`](../../GenerateModelsApp/Modeling.py) y [`limites.json`](../../GenerateModelsApp/config/limites.json). Los predeterminados de las propiedades Blender están declarados en código, además del JSON: no se enlazan automáticamente. La tabla refleja su coincidencia actual.

Todas las longitudes son mm en coordenadas de malla; ángulos en grados. Los **rangos UI** limitan el panel Blender; la **API** impone sus propias reglas y puede aceptar valores fuera de esos rangos. Campos ocultos siguen formando parte de las opciones y pueden ser validados. Ningún control genera mientras se arrastra: pulsar Generar / actualizar.

## Selección, preferencias y estado (fuera de las 17 opciones geométricas)

| Control / clave | Predeterminado | Propósito y cambio |
|---|---|---|
| Superficie sin espesor / `source` | Sin objeto | Selecciona base MESH; filtra el resultado. Si está vacío, Generar toma el activo. Elegir otra base cambia la forma de partida; no carga plantilla NPZ automáticamente |
| Autoescalar / `auto_scale` | `True` | Permite factor decimal para llevar eje mayor al rango 20–1000 mm. Generar escala una copia; Arreglar hornea esa corrección. Desactivado mantiene tamaño y muestra sugerencia |
| `status` | `Listo para generar` | Texto de estado; panel muestra primeros 48 caracteres. No es un parámetro de geometría |
| `filepath` del operador exportar | `//Ortesis_configurada.stl` | Ruta de salida; `//` es relativa al blend según Blender. Se añade extensión `.stl` si hace falta |

La preferencia instalada `OL_Preferences.auto_scale` prevalece sobre `OL_Settings.auto_scale`; al ejecutar desde scripts se usa la de escena. La API recibe esta decisión como `autoescalar`, no `auto_scale`, y la retira antes de validar opciones.

## Las 17 opciones del núcleo

| Clave / control | Default | Rango UI Blender | Efecto al cambiar / cuándo aplica |
|---|---:|---|---|
| `pattern` / Patrón | `VORONOI` | VORONOI, HEX, DIAMOND, SQUARE, SOLID | Selecciona algoritmo. SOLID usa espesor uniforme y oculta retícula. Triangle/Minimalistic no generan |
| `cell_mm` / Tamaño de celda | 15.0 | 5–40 | Aumentar separa los ejes y reduce densidad de celdas; puede reducir trabajo de semillas. Para HEX es separación horizontal de semillas, no diámetro de hueco garantizado |
| `rib_width_mm` / Ancho de nervadura | 2.8 | 1.2–10 | Aumentar amplía región `width/2-d>=0`, reduce huecos y normalmente aumenta material. También aumenta el paso permitido por `width/3`. El ancho es proyectado XY |
| `rib_height_mm` / Altura de nervadura | 1.4 | 0.3–6 | Con capa añade relieve máximo sobre `skin_mm`; sin capa es el espesor completo de las tiras. Aumentar desplaza más la piel y puede generar cruces en curvas |
| `liner` / Capa interior continua | true | Booleano | Activado mantiene caras y fondo de celdas; desactivado recorta huecos pasantes. No cierra la abertura anatómica |
| `skin_mm` / Espesor de capa | 1.0 | 0.3–5 | Con liner aumenta espesor mínimo y desplaza toda la piel; interviene en voxel mínimo. Oculto sin capa y en SOLID |
| `solid_mm` / Espesor macizo | 2.4 | 0.5–8 | Espesor uniforme de SOLID; no depende de ancho, altura ni liner |
| `border_mm` / Marco perimetral | 4.0 | 0–15 | Amplía material donde la distancia geodésica al contorno es menor al ancho. Cero elimina marco adicional. No cruza la abertura ni crea nueva superficie |
| `rounding_mm` / Transición de nervadura | 0.8 | 0–3 | Amplía zona de transición Hermite entre capa y nervadura. Mayor valor hace el relieve más gradual; no es bisel/radio real. Solo con liner no macizo; mínimo efectivo 0.02 |
| `angle_deg` / Giro del patrón | 0.0 | −180–180 | Rota coordenadas evaluadas del patrón XY. No rota la base ni la banda Y. DIAMOND añade su rotación propia de 45° |
| `seed` / Semilla orgánica | 7 | 0–99999, entero | Cambia jitter reproducible de VORONOI; no altera HEX, SQUARE, DIAMOND ni SOLID. No garantiza igual dibujo al cambiar extensión de la base |
| `reinforce_y_mm` / Posición banda Y | 0.0 | −250–250 | Traslada centro de franja maciza a lo largo de Y local. Solo tiene efecto si su ancho >0; puede quedar fuera de la pieza |
| `reinforce_width_mm` / Ancho banda | 0.0 | 0–60 | Cero la desactiva; aumentar amplía franja maciza sobre caras existentes y reduce huecos. No crea un puente por zonas sin caras |
| `repair` / Reconstrucción voxel | false | Booleano | Blender reconstruye y suaviza el resultado. Puede cerrar huecos, redondear y alterar dimensiones. La web acepta configuración pero no ejecuta voxel |
| `flip_normals` / Generar hacia dentro | false | Booleano | Invierte normales y orientación. False: desplazamiento `p+n*t`; true: `p-n*t` respecto a normales de entrada. Depende de que esas normales estén orientadas como se espera |
| `surface_step_mm` / Paso superficie | 1.0 | 0.15–5 | Menor paso añade detalle/tiempo/memoria; se limita también por celda/nervadura. Blender refina todos los modos, web solo no macizo; no aumenta precisión ilimitadamente por presupuesto |
| `resolution_mm` / Resolución geométrica | 0.3 | 0.15–0.8 | Tamaño voxel solicitado. Menor valor busca más detalle a mayor coste. Solo cambia geometría Blender con repair; voxel efectivo puede ser menor por espesor/3 |

## Validación real de la API

- `liner`, `repair`, `flip_normals` deben ser booleanos reales.
- `cell_mm`, `rib_width_mm`, `rib_height_mm`, `skin_mm`, `solid_mm`, `surface_step_mm` deben ser números finitos positivos, excluyendo bool.
- Celda ≥5 mm, incluso si el modo macizo no la usa geométricamente.
- En no macizo: `rib_width_mm < 0.75*cell_mm` (igualdad rechazada).
- `border_mm`, `rounding_mm`, `reinforce_width_mm` son finitos y ≥0.
- `angle_deg`, `reinforce_y_mm` son finitos sin los topes del panel; `resolution_mm` es finito y >0.
- `seed` debe ser entero no negativo, excluyendo bool; la API no fija 99999 como máximo.
- Solo se aceptan claves conocidas y códigos geométricos. Los aliases de nombres son aceptados por `Patron.Obtener`/`ChangePatern`, pero `ValidarOpciones` espera códigos canónicos.
- En Blender con repair: `min(resolution_mm,m/3) >= 0.15`, donde `m` depende del modo. Se comprueba adicionalmente en `GeneradorObjeto`, no en el núcleo puro.

## Interacciones y ejemplos

**Defaults con capa:** el espesor nominal máximo es `1.0+1.4=2.4 mm`; las celdas conservan fondo de 1.0 mm. No implica espesor medido exacto en todas las curvas.

**Misma configuración sin capa:** quedan tiras de 1.4 mm de espesor; `skin_mm` y `rounding_mm` no cambian la construcción, aunque deben ser válidos. Marco/banda pueden conectar tiras.

**Detalle:** con paso 1.0, ancho 2.8 y celda 15, el paso efectivo no macizo es `min(1,2.8/3,15/6)=0.933333… mm`. Bajar el ancho puede forzar más subdivisión aunque se conserve el paso solicitado.

**Voxel:** con capa de 0.3 mm, `m/3=0.1`; activar repair se rechaza aunque la resolución del panel sea 0.3. Con defaults `m=1`, voxel `min(0.3,1/3)=0.3` es admisible.

**Banda:** centro Y=25 y ancho 10 conserva material entre Y=20 y 30 en la superficie existente. Girar el patrón 60° no gira esa franja.

## Límites internos configurables (no controles del panel)

Valores exactos actualizados en [CONFIGURACION_GENERADA.md](CONFIGURACION_GENERADA.md). Cambiar estos límites exige revisar algoritmos, pruebas y documentación, y normalmente reiniciar procesos.

| Clave de `limites.json` | Valor actual | Propósito / efecto de aumentar |
|---|---:|---|
| `min_cell_mm` | 5 | Celda mínima aceptada; aumentar restringe más diseños |
| `max_rib_width_ratio` | 0.75 | Máxima relación ancho/celda, exclusiva; aumentar admite tiras más anchas |
| `min_voxel_repair_mm` | 0.15 | Piso permitido de voxel; aumentar evita reconstrucciones finas |
| `fragment_vertex_floor` | 50 | Piso de descarte de fragmentos tras voxel; aumentar permite retirar más residuos |
| `fragment_vertex_ratio` | 0.005 | Fracción de vértices tolerada fuera de pieza mayor; aumentar relaja control |
| `normal_smooth_iterations` | 20 | Iteraciones de promedio de normales; aumentar suaviza más la dirección, no la posición |
| `min_normal_length` | 0.5 | Longitud mínima de normal antes de normalizar; aumentar endurece rechazo |
| `scale_tolerance` | 1e-6 | Tolerancia respecto a escala de objeto 1; aumentar permite mayor desviación |
| `degenerate_area` | 1e-8 | Área mínima de cara; aumentar rechaza/elimina triángulos mayores |
| `pattern_batch` | 384 | Puntos por bloque en semillas; aumentar consume más RAM temporal |
| `voronoi_jitter` | 0.28 | Perturbación uniforme por eje como fracción de celda; aumentar cambia irregularidad |
| `seed_separation_epsilon` | 1e-10 | Tolerancia del denominador entre semillas; cambiar afecta estabilidad numérica |
| `smooth_factor` | 0.3 | Intensidad del modificador smooth después del voxel |
| `smooth_iterations` | 2 | Pasadas smooth después del voxel; más pasadas alteran más el resultado |
| `min_rounding_width_mm` | 0.02 | Piso de transición incluso cuando rounding=0 |
| `normal_epsilon` | 1e-12 | Protección numérica en normalización; aumentar puede rechazar interpolaciones pequeñas |
| `max_surface_vertices` | 500000 | Presupuesto para seguir subdividiendo; aumentar permite más detalle y memoria |
| `max_refined_cache_entries` | 2 | Entradas de caché LRU Blender; no cambia los máximos fijos de caché web |
| `surface_subdivision_iterations` | 16 | Máximo de rondas y cota de alcance de paso; aumentar admite más mitades |
| `clip_snap_mm` | 0.0001 | Cuantización de coincidencias STL web antes de escala; aumentar fusiona más coordenadas cercanas |
| `clip_connect_mm` | 0.005 | Margen positivo alrededor del cero del campo; aumentar ensancha uniones casi puntuales |
| `border_smooth_wavelength_mm` | 8.0 | Ondas cortas a filtrar; aumentar suaviza variaciones más largas; ≤0 desactiva filtrado |
| `border_smooth_max_mm` | 3.0 | Desplazamiento máximo del borde; aumentar permite más cambio; ≤0 no actúa como tope |
| `min_plausible_surface_extent_mm` | 20 | Eje mayor mínimo considerado plausible en heurística de escala |
| `max_plausible_surface_extent_mm` | 1000 | Eje mayor máximo considerado plausible en heurística de escala |

Los límites son configuración técnica, no resultados clínicos ni tolerancias de impresora. No modificar `comprobacion_geometrica.json` para intentar aprobar una malla: contiene referencias históricas.
