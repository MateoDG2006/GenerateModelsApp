"""Regenera los catálogos de hechos de la documentación y comprueba enlaces.

Genera ``docs/Agents/INVENTARIO.md``, los tres ``SIMBOLOS.md`` y
``docs/BlenderPlugin/CONFIGURACION_GENERADA.md``. Usa solo la biblioteca
estándar y Git: no importa Reflex, Blender ni el código del proyecto.

Las descripciones del inventario escritas a mano se conservan; un archivo
nuevo toma el primer renglón de su docstring o su título Markdown. La tabla de
carpetas y la sección de ``.web/`` se copian tal cual.

Uso, desde cualquier carpeta del repositorio::

    python docs/Agents/Scripts/GenerarIndices.py              # escribe
    python docs/Agents/Scripts/GenerarIndices.py --comprobar  # no escribe; 1 si hay deriva
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
INVENTARIO = RAIZ / "docs/Agents/INVENTARIO.md"
CONFIGURACION = RAIZ / "docs/BlenderPlugin/CONFIGURACION_GENERADA.md"
CARPETA_CONFIG = RAIZ / "GenerateModelsApp/config"

ORDEN = "python docs/Agents/Scripts/GenerarIndices.py"
CABECERA_SIMBOLOS = f"> Generado por `{ORDEN}`. No editar a mano."
CABECERA_INVENTARIO = (
    f"> Generado por `{ORDEN}`. Incluye archivos versionados y nuevos no ignorados; "
    "excluye Git, dependencias y salidas locales ignoradas. Las descripciones de la tabla se editan "
    "a mano y el script las conserva."
)
SIN_SIMBOLOS = "| — | Sin clases/funciones | — | Declaraciones o marcador de paquete |"
SIN_DOCSTRING = "Sin docstring; consultar el catálogo de módulos y el código."
SIN_DESCRIPCION = "Sin descripción; completar en INVENTARIO.md."
EXCLUIDOS = re.compile(r"__pycache__/|^\.codegraph/(?!\.gitignore$)|\.log$")
FRONTEND = re.compile(r"^(rxconfig\.py|web/(Estado|Pagina|Sesion|GenerateModelsApp)\w*\.py)$")
ENLACE = re.compile(r"\]\(([^)#\s]+)(#[^)]*)?\)")


def Archivos() -> list[str]:
    """Archivos versionados más nuevos no ignorados que existen en disco."""
    salida = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.splitlines()
    versionados = set(
        subprocess.run(
            ["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=True
        ).stdout.splitlines()
    )
    return sorted(
        {
            ruta for ruta in salida
            if (RAIZ / ruta).is_file() and (ruta in versionados or not EXCLUIDOS.search(ruta))
            and "__pycache__/" not in ruta
        }
    )


def Relativa(destino: Path, documento: Path) -> str:
    return Path(os.path.relpath(destino, documento.parent)).as_posix()


def Celda(texto: str) -> str:
    return texto.replace("|", "\\|").replace("\n", " ").strip()


def PrimerRenglon(texto: str | None) -> str:
    return texto.strip().splitlines()[0].strip() if texto and texto.strip() else ""


def Docstring(ruta: Path) -> str:
    try:
        return PrimerRenglon(ast.get_docstring(ast.parse(ruta.read_text(encoding="utf-8"))))
    except (SyntaxError, UnicodeDecodeError):
        return ""


def Titulo(ruta: Path) -> str:
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("# "):
            return linea[2:].strip()
    return ""


def DescripcionesPrevias() -> dict[str, str]:
    if not INVENTARIO.exists():
        return {}
    previas = {}
    for linea in INVENTARIO.read_text(encoding="utf-8").splitlines():
        coincidencia = re.match(r"\| \[([^\]]+)\]\([^)]*\) \| (.*) \|$", linea)
        if coincidencia:
            previas[coincidencia.group(1)] = coincidencia.group(2)
    return previas


def Descripcion(ruta: str, previas: dict[str, str]) -> str:
    if ruta in previas:
        return previas[ruta]
    archivo = RAIZ / ruta
    if ruta.endswith(".md"):
        return Celda(Titulo(archivo)) or SIN_DESCRIPCION
    if ruta.endswith(".py"):
        return Celda(Docstring(archivo) or "Marcador de paquete.")
    return SIN_DESCRIPCION


def Simbolos(ruta: Path, documento: Path) -> list[str]:
    """Clases y funciones en orden de aparición, incluidas privadas y anidadas."""
    filas: list[str] = []

    def Visitar(nodo: ast.AST, prefijo: str) -> None:
        for hijo in ast.iter_child_nodes(nodo):
            if isinstance(hijo, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                nombre = f"{prefijo}{hijo.name}"
                tipo = "Clase" if isinstance(hijo, ast.ClassDef) else "Función/método"
                descripcion = PrimerRenglon(ast.get_docstring(hijo)) or SIN_DOCSTRING
                enlace = f"{Relativa(ruta, documento)}#L{hijo.lineno}"
                filas.append(f"| `{nombre}` | {tipo} | [{hijo.lineno}]({enlace}) | {Celda(descripcion)} |")
                Visitar(hijo, f"{nombre}.")

    Visitar(ast.parse(ruta.read_text(encoding="utf-8")), "")
    return filas


def IndiceSimbolos(titulo: str, rutas: list[str], documento: Path, previas: dict[str, str]) -> str:
    lineas = [
        f"# Índice de símbolos: {titulo}",
        "",
        CABECERA_SIMBOLOS,
        "",
        "Incluye funciones anidadas y métodos privados para localizar todas las piezas. "
        "Las líneas son una ayuda de navegación; el nombre del símbolo es la referencia estable.",
        "",
    ]
    for ruta in sorted(rutas, key=str.lower):
        lineas += [
            f"## `{ruta}`",
            "",
            Descripcion(ruta, previas),
            "",
            "| Símbolo | Tipo | Línea | Descripción declarada |",
            "|---|---|---:|---|",
            *(Simbolos(RAIZ / ruta, documento) or [SIN_SIMBOLOS]),
            "",
        ]
    return "\n".join(lineas)


def Inventario(archivos: list[str], previas: dict[str, str]) -> str:
    texto = INVENTARIO.read_text(encoding="utf-8")
    cabeza = texto[: texto.index("| Archivo | Propósito |")]
    cabeza = re.sub(r"^> .*$", lambda _: CABECERA_INVENTARIO, cabeza, count=1, flags=re.M)
    cola = texto[texto.index("## Carpetas y artefactos locales"):]
    filas = [f"| [{ruta}]({Relativa(RAIZ / ruta, INVENTARIO)}) | {Descripcion(ruta, previas)} |" for ruta in archivos]
    return cabeza + "| Archivo | Propósito |\n|---|---|\n" + "\n".join(filas) + "\n\n" + cola


def Configuracion() -> str:
    lineas = [
        "# Configuración exacta del núcleo",
        "",
        f"> Generado por `{ORDEN}` desde los JSON del paquete. "
        "Para significado y efectos consultar [PARAMETROS.md](PARAMETROS.md).",
        "",
    ]
    for archivo in sorted(CARPETA_CONFIG.glob("*.json")):
        datos = json.loads(archivo.read_text(encoding="utf-8"))
        lineas += [
            f"## [{archivo.name}]({Relativa(archivo, CONFIGURACION)})",
            "",
            "```json",
            json.dumps(datos, indent=2, ensure_ascii=False),
            "```",
            "",
        ]
    return "\n".join(lineas)


def Generados() -> dict[Path, str]:
    archivos = Archivos()
    previas = DescripcionesPrevias()
    python = [ruta for ruta in archivos if ruta.endswith(".py")]
    backend = [r for r in python if r == "rxconfig.py" or r.startswith(("scripts/", "src/", "web/"))]
    frontend = [r for r in python if FRONTEND.match(r)]
    blender = [r for r in python if r.startswith("GenerateModelsApp/")]
    return {
        RAIZ / "docs/AppBackend/SIMBOLOS.md": IndiceSimbolos(
            "AppBackend", backend, RAIZ / "docs/AppBackend/SIMBOLOS.md", previas
        ),
        RAIZ / "docs/AppFrontend/SIMBOLOS.md": IndiceSimbolos(
            "AppFrontend", frontend, RAIZ / "docs/AppFrontend/SIMBOLOS.md", previas
        ),
        RAIZ / "docs/BlenderPlugin/SIMBOLOS.md": IndiceSimbolos(
            "BlenderPlugin", blender, RAIZ / "docs/BlenderPlugin/SIMBOLOS.md", previas
        ),
        CONFIGURACION: Configuracion(),
        INVENTARIO: Inventario(archivos, previas),
    }


def EnlacesRotos() -> list[str]:
    """Enlaces relativos de Markdown sin destino. Los registros de docs/Audit tienen ciclo propio."""
    documentos = [RAIZ / "README.md", *(RAIZ / "docs").rglob("*.md")]
    rotos = []
    for documento in documentos:
        if "Audit" in documento.relative_to(RAIZ).parts:
            continue
        for coincidencia in ENLACE.finditer(documento.read_text(encoding="utf-8")):
            destino = coincidencia.group(1)
            if destino.startswith(("http:", "https:", "mailto:")):
                continue
            if not (documento.parent / destino).exists():
                rotos.append(f"{documento.relative_to(RAIZ).as_posix()}: {destino}")
    return rotos


def Normalizar(texto: str) -> str:
    return texto.replace("\r\n", "\n").rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--comprobar", action="store_true", help="No escribe; termina con 1 si hay deriva o enlaces rotos.")
    argumentos = parser.parse_args()

    deriva = []
    for ruta, contenido in Generados().items():
        nuevo = Normalizar(contenido)
        actual = Normalizar(ruta.read_text(encoding="utf-8")) if ruta.exists() else ""
        if nuevo == actual:
            continue
        deriva.append(ruta.relative_to(RAIZ).as_posix())
        if not argumentos.comprobar:
            ruta.write_text(nuevo, encoding="utf-8", newline="\n")

    rotos = EnlacesRotos()
    verbo = "Desactualizado" if argumentos.comprobar else "Actualizado"
    for ruta in deriva:
        print(f"{verbo}: {ruta}")
    for enlace in rotos:
        print(f"Enlace roto: {enlace}")
    pendientes = [r for r in Archivos() if Descripcion(r, DescripcionesPrevias()) == SIN_DESCRIPCION]
    for ruta in pendientes:
        print(f"Sin descripción en el inventario: {ruta}")
    if not deriva and not rotos:
        print("Catálogos al día y enlaces correctos.")
    return 1 if rotos or (argumentos.comprobar and deriva) else 0


if __name__ == "__main__":
    sys.exit(main())
