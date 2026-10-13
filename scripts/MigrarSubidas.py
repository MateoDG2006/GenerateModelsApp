"""Traslada una sola vez ``uploaded_files/`` al bucket y registra cada objeto.

Los archivos previos no tienen cuenta: quedan a nombre del usuario semilla
``urn:ortesislab:seed`` en el proyecto «Importaciones locales previas». Cada
NPZ interno pasa a ser un import ``ready`` cuyo original y normalizado son el
mismo asset; cada STL pasa a ser un asset ``result_stl`` sin resultado ni
métricas, porque el archivo no las demuestra. La copia local se borra solo
después de comprobar el objeto en el bucket. Repetir no duplica objetos.

Uso: ``python scripts/MigrarSubidas.py [--directorio uploaded_files] [--simular]``
"""

from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from web.Ajustes import Ajustes  # noqa: E402
from web.enums import FormatoImport, OrigenImport, TipoAsset, TipoEvento  # noqa: E402
from web.persistence.ConexionPostgres import ConexionPostgres  # noqa: E402
from web.persistence.Contratos import ESQUEMA_NORMALIZACION, VERSION_LECTOR, UsuarioAutenticado  # noqa: E402
from web.persistence.repositorios import (  # noqa: E402
    RepositorioAssets,
    RepositorioHistorial,
    RepositorioImports,
    RepositorioProyectos,
    RepositorioUsuarios,
)
from web.services.ServicioImports import MEDIA_NPZ, ServicioImports  # noqa: E402
from web.storage.AlmacenamientoPrivado import Almacen, ObjetoAusente  # noqa: E402

ISSUER_SEMILLA = "urn:ortesislab:seed"
SUJETO_SEMILLA = "subidas-locales-previas"
PROYECTO = "Importaciones locales previas"
NPZ = re.compile(r"superficie-[0-9a-f]{32}\.npz")
STL = re.compile(r"ortesis-[0-9a-f]{8}\.stl")


def Propietario() -> UsuarioAutenticado:
    def asegurar(conexion) -> UsuarioAutenticado:
        user_id = RepositorioUsuarios.Upsert(conexion, ISSUER_SEMILLA, SUJETO_SEMILLA, None, "Subidas locales previas")
        proyecto = RepositorioProyectos.PorNombre(conexion, user_id, PROYECTO)
        if proyecto is None:
            proyecto = RepositorioProyectos.Crear(conexion, user_id, PROYECTO, "Archivos de uploaded_files/ sin cuenta.")
        return UsuarioAutenticado(user_id, "Subidas locales previas", None, proyecto)

    return ConexionPostgres.Ejecutar(asegurar)


def Migrar(ruta: Path, usuario: UsuarioAutenticado) -> str:
    datos = ruta.read_bytes()
    sha = Almacen.Sha256(datos)
    es_npz = NPZ.fullmatch(ruta.name) is not None
    kind = TipoAsset.SURFACE_NPZ if es_npz else TipoAsset.RESULT_STL
    existente = ConexionPostgres.Ejecutar(lambda c: RepositorioAssets.ListoPorSha(c, usuario.user_id, sha, kind))
    if existente is not None:
        try:
            Almacen.LeerVerificado(existente.storage_key, sha)
        except ObjetoAusente:
            # La fila declara este mismo sha: la copia local repone el objeto perdido.
            Almacen.Actual().Publicar(
                existente.storage_key, datos, existente.media_type, sha, None if es_npz else ruta.name
            )
            Almacen.LeerVerificado(existente.storage_key, sha)
            return existente.object_url
        return f"ya migrado ({existente.object_url})"

    if es_npz:
        resultado = ServicioImports.NpzATupla(datos, ruta.name)
    asset_id = uuid.uuid4()
    clave = Almacen.Clave(usuario.user_id, asset_id, stl_publico=not es_npz)
    media = MEDIA_NPZ if es_npz else "model/stl"
    ConexionPostgres.Ejecutar(
        lambda c: RepositorioAssets.CrearStaged(c, usuario.user_id, asset_id, clave, kind, ruta.name, media, len(datos), sha)
    )
    url = Almacen.Actual().Publicar(clave, datos, media, sha, None if es_npz else ruta.name)
    Almacen.LeerVerificado(clave, sha)

    def registrar(conexion) -> None:
        RepositorioAssets.MarcarListo(conexion, usuario.user_id, asset_id, url)
        if not es_npz:
            return
        import_id = uuid.uuid4()
        vertices, caras = resultado[0], resultado[1]
        dimensiones = [float(valor) for valor in (vertices.max(axis=0) - vertices.min(axis=0))] if len(vertices) else [0.0] * 3
        RepositorioImports.Crear(conexion, usuario, import_id, asset_id, OrigenImport.UPLOAD, FormatoImport.NPZ, VERSION_LECTOR, ESQUEMA_NORMALIZACION)
        RepositorioImports.MarcarListo(conexion, usuario.user_id, import_id, asset_id, len(vertices), len(caras), dimensiones)
        RepositorioHistorial.Evento(
            conexion, usuario.user_id, usuario.project_id, TipoEvento.IMPORT_READY,
            payload={"import_id": str(import_id), "migrated_from": ruta.name},
        )

    ConexionPostgres.Ejecutar(registrar)
    return url


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--directorio", type=Path, default=RAIZ / "uploaded_files")
    argumentos.add_argument("--simular", action="store_true", help="Lista lo que migraría sin escribir.")
    opciones = argumentos.parse_args()

    directorio: Path = opciones.directorio
    if not directorio.is_dir():
        print(f"No existe {directorio}; no hay nada que migrar.")
        return 0
    archivos = sorted(p for p in directorio.iterdir() if p.is_file() and (NPZ.fullmatch(p.name) or STL.fullmatch(p.name)))
    ajenos = sorted(p.name for p in directorio.iterdir() if p.is_file() and p not in archivos)
    if ajenos:
        print("Se ignoran archivos que la aplicación no generó:", ", ".join(ajenos))
    if opciones.simular or not archivos:
        print(f"{len(archivos)} archivo(s) para migrar.")
        for ruta in archivos:
            print(" ", ruta.name)
        return 0

    ajustes = Ajustes.Cargar()
    ConexionPostgres.Abrir(ajustes.database_url, 1, 2, "migracion")
    try:
        usuario = Propietario()
        fallos = 0
        for ruta in archivos:
            try:
                destino = Migrar(ruta, usuario)
            except Exception as exc:  # noqa: BLE001 - se informa y se conserva la copia local
                fallos += 1
                print(f"ERROR {ruta.name}: {exc}")
                continue
            ruta.unlink()
            print(f"{ruta.name} -> {destino}")
        return 1 if fallos else 0
    finally:
        ConexionPostgres.Cerrar()


if __name__ == "__main__":
    raise SystemExit(main())
