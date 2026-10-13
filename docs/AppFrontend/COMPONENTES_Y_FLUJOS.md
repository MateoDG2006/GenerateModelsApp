# Componentes, archivos y flujos de interfaz

## Catálogo de archivos

| Archivo/carpeta | Función |
|---|---|
| [`web/PaginaComparacion.py`](../../web/PaginaComparacion.py) | Todos los componentes visuales; `ETIQUETAS_EJE` agrega opción sin barrido a `EJES` |
| [`web/GenerateModelsApp.py`](../../web/GenerateModelsApp.py) | Página única, título y `on_load` |
| [`web/EstadoApp.py`](../../web/EstadoApp.py) | Estado/handlers que alimentan UI; se ejecutan en backend |
| [`web/GeneradorWeb.py`](../../web/GeneradorWeb.py) | Catálogos compartidos y fichas para mostrar; no renderiza |
| [`web/LectorSuperficie.py`](../../web/LectorSuperficie.py) | Límite de subida usado por cliente y lector real servidor |
| [`web/__init__.py`](../../web/__init__.py) | Marcador de paquete |
| [`rxconfig.py`](../../rxconfig.py) | Plugins de compilación y apariencia |
| [`assets/visor.html`](../../assets/visor.html) | Documento independiente Three.js dentro de iframe |
| [`assets/favicon.ico`](../../assets/favicon.ico) | Icono del sitio |
| [`assets/superficie_interior_mm.npz`](../../assets/superficie_interior_mm.npz) | Datos de ejemplo usados por backend; no componente visual |
| `reflex.lock/package.json`, `reflex.lock/bun.lock` | Dependencias JavaScript reproducibles |
| `.web/` | Compilación, dependencias instaladas y archivos públicos generados |

El [inventario global](../Agents/INVENTARIO.md) explica cada archivo auxiliar y los artefactos de `.web/`. [SIMBOLOS.md](SIMBOLOS.md) permite localizar todos los métodos.

## Componentes y bindings

| Método | Composición / conexiones |
|---|---|
| `Index` | Título, explicación, cambio de tema, Formulario/Vista y Lote |
| `Formulario` | Parámetros → `EstadoApp.<campo>`; `on_change=EstadoApp.set_<campo>`; Previsualizar → `EstadoApp.Previsualizar` |
| `Superficie` | `rx.upload` con ID `superficie-entrada`; selección local visible con badges; botón carga con `rx.upload_files`; botón incluida; avisos y metadatos |
| `Vista` | Si `archivo` no vacío: iframe 560px, detalle, volumen/peso/precio, texto de alcance; si vacío: placeholder |
| `Lote` | Switches de patrones, selector de eje, rango y ambas capas; `PedirLote`, progreso `porcentaje`, tabla `resultados` y comparación `vistas` |
| `Fila` | Columnas de una ficha; Ver, Comparar y STL por ID; botones desactivados si `archivo==''` |
| `Marco` | Wrapper flexible del visor de comparación, alto 320px |
| `Visor` | iframe con title y URL generada por Enlace |
| `Enlace` | `rx.get_upload_url(archivo)` → expresión JS `/visor.html?src=${encodeURIComponent(url)}` |
| `Campo` | Etiqueta y `rx.input(type='number')` controlado por cadena |
| `Interruptor` | Switch booleano con callback y texto |
| `Selector` | Opciones `(codigo, etiqueta)` → `rx.select` controlado |
| `Medida` | Etiqueta pequeña y valor destacado |

## Reglas de visibilidad

| Condición | Resultado |
|---|---|
| `pattern=='SOLID'` | Muestra espesor macizo; oculta celda, nervadura, capa, giro, marco, banda y paso |
| Patrón distinto de SOLID | Muestra parámetros de retícula y paso |
| `liner=True` en retícula | Muestra espesor capa, transición y espesor nominal total |
| `liner=False` | Texto de rejilla abierta; altura es espesor total |
| `pattern=='VORONOI'` | Muestra semilla |
| `eje!='ninguno'` | Muestra Desde/Hasta/Cada |
| `total>0` | Muestra progreso |
| `vistas.length()>0` | Muestra comparación |
| `ocupado=True` | Previsualizar y Generar lote cargando/desactivados; carga/incluida también desactivadas |
| `subiendo_superficie=True` | Carga/incluida desactivadas; no constituye por sí solo un bloqueo de los botones de generación |

La web muestra posición de banda aunque su ancho sea cero; Blender la oculta en ese caso. La web informa `repair`/`resolution_mm` como texto, sin control editable; no aplica voxel. Todos los campos numéricos deben seguir siendo válidos aunque estén ocultos.

## Flujo de carga y generación

```mermaid
sequenceDiagram
  actor U as Usuario
  participant P as PaginaComparacion
  participant E as EstadoApp
  participant L as LectorSuperficie
  participant G as GeneradorWeb
  U->>P: Elegir STL / NPZ
  P-->>U: Nombre seleccionado, aún no cargado
  U->>P: Cargar archivo
  P->>E: CargarSuperficie(upload_files)
  E->>G: GuardarSuperficie en thread
  G->>L: Preparar y validar
  alt Entrada válida
    L-->>G: Arrays y metadatos
    G-->>E: Nombre NPZ interno
    E-->>P: Base nueva, vaciar resultados/vistas
  else Entrada inválida
    E-->>P: Error, conservar base previa
  end
  U->>P: Previsualizar
  P->>E: Previsualizar → Generar
  E->>G: Crear con instantánea
  G-->>E: Ficha y nombre STL
  E-->>P: Métricas y archivo
  P-->>U: iframe carga malla
```

## Estado de trabajo

```mermaid
stateDiagram-v2
  [*] --> Listo
  Listo --> Preparando: Previsualizar o PedirLote
  Preparando --> Listo: Error de opciones
  Preparando --> Generando: Variantes válidas
  Generando --> Generando: Publicar siguiente ficha
  Generando --> Terminado: Todas procesadas
  Generando --> Interrumpido: Excepción fuera de variante
  Terminado --> Listo: Nueva petición o selección de base
  Interrumpido --> Listo: Reintentar
```

Estos son estados conceptuales, no un enum del código. La implementación usa `ocupado`, `_trabajando`, `hechos`, `total`, `mensaje`. Errores individuales se incorporan como filas y pueden coexistir con resultados válidos. Comparar alterna una URL entre hasta tres vistas; Ver reemplaza la principal; descargar lee bytes sin modificar opciones ni regenerar.

## UX y accesibilidad observadas

Interfaz en español, inputs numéricos y componentes Radix; no hay evidencia de una auditoría WCAG completa. `Campo` crea un elemento label visual pero no explicita IDs/`htmlFor` por campo; verificar asociación accesible. El iframe tiene título pero el canvas no ofrece descripción geométrica textual ni controles de cámara por teclado implementados. La tabla permite scroll horizontal y los bloques hacen wrap, pero tamaños mínimos pueden causar desbordes en pantallas estrechas.

La ausencia de mensajes de error por campo, cancelación, descarga de ficha JSON y cámaras sincronizadas describe el estado actual; son oportunidades futuras, no funciones ya desarrolladas.
