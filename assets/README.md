# Assets de la aplicación

Reflex publica esta carpeta en la raíz del sitio. Estos tres archivos permanecen
en la raíz de `assets/`, no en una subcarpeta: el visor se abre en `/visor.html`,
el icono en `/favicon.ico` y el núcleo busca `assets/superficie_interior_mm.npz`.

| Archivo | Qué es |
|---|---|
| [visor.html](visor.html) | Visor Three.js. Cada vista de comparación lo carga en un iframe con la `object_url` del STL. |
| [favicon.ico](favicon.ico) | Icono del sitio. |
| [superficie_interior_mm.npz](superficie_interior_mm.npz) | Superficie de ejemplo incluida. La usa la carga explícita de la plantilla, no el visor. |

Los fixtures y la evidencia de las pruebas no viven aquí. Están en
[tests/assets](../tests/assets/Test.stl), para no publicarlos con el sitio.
`assets/external/` es salida generada y está ignorada por Git.
