"""Importación de superficies: original y NPZ normalizado en el bucket.

Orden: registrar el asset en ``staged``, subir, normalizar fuera de cualquier
transacción, subir el NPZ y marcar ambos ``ready`` con su ``object_url`` en una
sola transacción. Un fallo deja filas ``staged`` que el conciliador retira.
"""

from __future__ import annotations

import io
import uuid
from collections.abc import Callable
from pathlib import Path
from uuid import UUID

import numpy as np

from GenerateModelsApp.EscalaMalla import EscalaMalla
from GenerateModelsApp.Excepciones import ArchivoSuperficieIlegible, OrtesisLabError
from GenerateModelsApp.Malla import AnalizadorMalla
from GenerateModelsApp.constants.Nombres import ARCHIVO_SUPERFICIE
from web.cache.CacheRedis import CacheRedis
from web.enums import ExtensionSuperficie, FormatoImport, OrigenImport, TipoAsset, TipoEvento
from web.LectorSuperficie import LectorSuperficie
from web.persistence.ConexionPostgres import ConexionPostgres
from web.persistence.Contratos import (
    ESQUEMA_NORMALIZACION,
    VERSION_LECTOR,
    AccesoDenegado,
    ImportDTO,
    UsuarioAutenticado,
)
from web.persistence.repositorios import RepositorioAssets, RepositorioHistorial, RepositorioImports
from web.storage.AlmacenamientoPrivado import Almacen

PLANTILLA = Path(__file__).resolve().parents[2] / "assets" / ARCHIVO_SUPERFICIE
PREFIJO_SUPERFICIE = "superficie-"
MEDIA_NPZ = "application/x-npz"


class ServicioImports:
    @staticmethod
    def NombreSuperficie(asset_id: UUID) -> str:
        """Identificador que la página guarda en ``superficie_archivo``."""
        return f"{PREFIJO_SUPERFICIE}{asset_id.hex}{ExtensionSuperficie.NPZ}"

    @staticmethod
    def AssetDeNombre(nombre: str) -> UUID:
        identificador = nombre[len(PREFIJO_SUPERFICIE) : -len(ExtensionSuperficie.NPZ)]
        if (
            not nombre.startswith(PREFIJO_SUPERFICIE)
            or not nombre.endswith(ExtensionSuperficie.NPZ)
            or len(identificador) != 32
            or any(caracter not in "0123456789abcdef" for caracter in identificador)
        ):
            raise ValueError("La superficie subida no tiene un identificador válido.")
        return UUID(hex=identificador)

    @staticmethod
    def TuplaANpz(tupla: tuple) -> bytes:
        vertices, caras, normales, borde = tupla
        salida = io.BytesIO()
        np.savez_compressed(salida, vertices=vertices, faces=caras, normals=normales, border=borde)
        return salida.getvalue()

    @staticmethod
    def NpzATupla(datos: bytes, nombre: str = "superficie") -> tuple:
        try:
            with np.load(io.BytesIO(datos), allow_pickle=False) as archivo:
                return (
                    np.asarray(archivo["vertices"], dtype=np.float64),
                    np.asarray(archivo["faces"], dtype=np.int32),
                    np.asarray(archivo["normals"], dtype=np.float64),
                    np.asarray(archivo["border"], dtype=np.float64),
                )
        except (OSError, ValueError, KeyError) as exc:
            raise ArchivoSuperficieIlegible(nombre, str(exc)) from exc

    @staticmethod
    def PrepararPlantilla(contenido: bytes) -> tuple:
        # Misma preparación que la plantilla incluida tuvo siempre: sin suavizar normales.
        try:
            with np.load(io.BytesIO(contenido), allow_pickle=False) as datos:
                vertices, caras, normales = datos["vertices"], datos["faces"], datos["normals"]
                return AnalizadorMalla.Preparar(vertices, caras, normales, suavizarNormales=False)
        except (OSError, ValueError, KeyError) as exc:
            raise ArchivoSuperficieIlegible(ARCHIVO_SUPERFICIE, str(exc)) from exc

    @staticmethod
    def Importar(
        usuario: UsuarioAutenticado, nombre: str, contenido: bytes, autoescalar: bool = True
    ) -> tuple[ImportDTO, dict]:
        """Entrada: archivo subido. Proceso: lo guarda y normaliza. Salida: import
        ready y resumen para la página. Errores: ArchivoSuperficieIlegible,
        OrtesisLabError o ValueError con el import marcado ``rejected``."""
        archivo = Path(nombre).name or "superficie"
        extension = Path(archivo).suffix.lower()
        if extension not in LectorSuperficie.EXTENSIONES:
            raise ArchivoSuperficieIlegible(archivo, "Use un archivo STL o NPZ.")
        if not contenido:
            raise ArchivoSuperficieIlegible(archivo, "El archivo está vacío.")
        if len(contenido) > LectorSuperficie.MAXIMO_BYTES:
            raise ArchivoSuperficieIlegible(
                archivo, f"El archivo supera {LectorSuperficie.MAXIMO_BYTES // (1024 * 1024)} MB."
            )
        if extension == ExtensionSuperficie.NPZ:
            formato, media = FormatoImport.NPZ, MEDIA_NPZ
        else:
            binario = len(contenido) >= 84 and 84 + int.from_bytes(contenido[80:84], "little") * 50 == len(contenido)
            formato, media = (FormatoImport.STL_BINARY if binario else FormatoImport.STL_ASCII), "model/stl"

        def normalizar(datos: bytes) -> tuple:
            resultado, _info = LectorSuperficie.Preparar(archivo, datos, autoescalar=False)
            return resultado

        importacion = ServicioImports._Registrar(usuario, archivo, contenido, OrigenImport.UPLOAD, formato, media, normalizar)
        return importacion, ServicioImports.Info(importacion, archivo, autoescalar)

    @staticmethod
    def AsegurarPlantilla(usuario: UsuarioAutenticado) -> ImportDTO:
        """La plantilla incluida pasa a ser un import del proyecto del usuario."""
        contenido = PLANTILLA.read_bytes()
        return ServicioImports._Registrar(
            usuario, ARCHIVO_SUPERFICIE, contenido, OrigenImport.INCLUDED_TEMPLATE, FormatoImport.NPZ, MEDIA_NPZ,
            ServicioImports.PrepararPlantilla,
        )

    @staticmethod
    def Resolver(usuario: UsuarioAutenticado, superficie_archivo: str) -> ImportDTO:
        """``""`` es la plantilla; otro valor es el NPZ de un import del usuario."""
        if not superficie_archivo:
            return ServicioImports.AsegurarPlantilla(usuario)
        asset_id = ServicioImports.AssetDeNombre(superficie_archivo)
        importacion = ConexionPostgres.Ejecutar(
            lambda conexion: RepositorioImports.ListoPorNormalizado(conexion, usuario.user_id, asset_id)
        )
        if importacion is None:
            raise AccesoDenegado("La superficie no existe o no le pertenece.")
        return importacion

    @staticmethod
    def Info(importacion: ImportDTO, nombre: str, autoescalar: bool) -> dict:
        dimensiones = np.asarray(importacion.raw_dimensions_mm or [0.0, 0.0, 0.0], dtype=np.float64)
        eje = float(dimensiones.max()) if dimensiones.size else 0.0
        diagnostico = EscalaMalla.Resolver(eje, autoescalar=autoescalar)
        factor = float(diagnostico["factor"])
        return {
            "nombre": nombre,
            "vertices": importacion.vertex_count or 0,
            "caras": importacion.face_count or 0,
            "eje_mm": eje,
            "factor_escala": factor,
            "dimensiones": " × ".join(f"{valor:.1f}" for valor in dimensiones * factor) + " mm",
            "aviso": f"Escala corregida ×{factor:g}. " if factor != 1.0 else diagnostico["advertencia"],
        }

    @staticmethod
    def _Registrar(
        usuario: UsuarioAutenticado,
        nombre: str,
        contenido: bytes,
        source_kind: str,
        formato: str,
        media: str,
        normalizar: Callable[[bytes], tuple],
    ) -> ImportDTO:
        user_id, project_id = usuario.user_id, usuario.project_id
        sha = Almacen.Sha256(contenido)
        existente = ConexionPostgres.Ejecutar(
            lambda conexion: RepositorioImports.ListoPorOriginal(conexion, user_id, project_id, sha, source_kind)
        )
        if existente is not None:
            return existente

        import_id, original_id, normal_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        clave_original = Almacen.Clave(user_id, original_id)

        def recibir(conexion) -> None:
            RepositorioAssets.CrearStaged(
                conexion, user_id, original_id, clave_original, TipoAsset.IMPORT_ORIGINAL, nombre[:255], media,
                len(contenido), sha,
            )
            RepositorioImports.Crear(
                conexion, usuario, import_id, original_id, source_kind, formato, VERSION_LECTOR, ESQUEMA_NORMALIZACION
            )
            RepositorioHistorial.Evento(
                conexion, user_id, project_id, TipoEvento.IMPORT_RECEIVED,
                payload={"import_id": str(import_id), "name": nombre[:255], "size_bytes": len(contenido)},
            )

        ConexionPostgres.Ejecutar(recibir)
        url_original = Almacen.Actual().Publicar(clave_original, contenido, media, sha)

        try:
            resultado = normalizar(contenido)
        except (ValueError, OrtesisLabError) as exc:
            def rechazar(conexion) -> None:
                RepositorioAssets.MarcarListo(conexion, user_id, original_id, url_original)
                RepositorioImports.MarcarRechazado(conexion, user_id, import_id, type(exc).__name__, str(exc))
                RepositorioHistorial.Evento(
                    conexion, user_id, project_id, TipoEvento.IMPORT_REJECTED,
                    payload={"import_id": str(import_id), "error_code": type(exc).__name__},
                )

            ConexionPostgres.Ejecutar(rechazar)
            raise

        npz = ServicioImports.TuplaANpz(resultado)
        sha_npz = Almacen.Sha256(npz)
        clave_npz = Almacen.Clave(user_id, normal_id)
        ConexionPostgres.Ejecutar(
            lambda conexion: RepositorioAssets.CrearStaged(
                conexion, user_id, normal_id, clave_npz, TipoAsset.SURFACE_NPZ, None, MEDIA_NPZ, len(npz), sha_npz
            )
        )
        url_npz = Almacen.Actual().Publicar(clave_npz, npz, MEDIA_NPZ, sha_npz)
        CacheRedis.GuardarTupla(CacheRedis.ClaveCruda(sha_npz), resultado)
        vertices, caras = resultado[0], resultado[1]
        dimensiones = [float(valor) for valor in np.ptp(vertices, axis=0)] if len(vertices) else [0.0, 0.0, 0.0]

        def publicar(conexion) -> ImportDTO:
            RepositorioAssets.MarcarListo(conexion, user_id, original_id, url_original)
            RepositorioAssets.MarcarListo(conexion, user_id, normal_id, url_npz)
            RepositorioImports.MarcarListo(conexion, user_id, import_id, normal_id, len(vertices), len(caras), dimensiones)
            RepositorioHistorial.Evento(
                conexion, user_id, project_id, TipoEvento.IMPORT_READY,
                payload={"import_id": str(import_id), "vertices": len(vertices), "faces": len(caras)},
            )
            return RepositorioImports.Obtener(conexion, user_id, import_id)

        return ConexionPostgres.Ejecutar(publicar)
