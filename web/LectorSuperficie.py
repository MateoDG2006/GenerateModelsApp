"""Lectura de superficies subidas a la aplicación web."""

from __future__ import annotations

import io
import struct
from pathlib import Path

import numpy as np

from GenerateModelsApp.EscalaMalla import EscalaMalla
from GenerateModelsApp.Excepciones import ArchivoSuperficieIlegible
from GenerateModelsApp.Malla import AnalizadorMalla
from GenerateModelsApp.util.Utilidades import Configuracion


class LectorSuperficie:
    """Convierte STL o NPZ en los arreglos que consume el núcleo geométrico."""

    MAXIMO_BYTES = 50 * 1024 * 1024
    EXTENSIONES = {".stl", ".npz"}

    @staticmethod
    def Preparar(
        nombre: str,
        contenido: bytes,
        autoescalar: bool = True,
    ) -> tuple[tuple, dict]:
        archivo = Path(nombre).name
        extension = Path(archivo).suffix.lower()
        if extension not in LectorSuperficie.EXTENSIONES:
            raise ArchivoSuperficieIlegible(
                archivo,
                "Use un archivo STL o NPZ.",
            )
        if not contenido:
            raise ArchivoSuperficieIlegible(archivo, "El archivo está vacío.")
        if len(contenido) > LectorSuperficie.MAXIMO_BYTES:
            raise ArchivoSuperficieIlegible(
                archivo,
                f"El archivo supera {LectorSuperficie.MAXIMO_BYTES // (1024 * 1024)} MB.",
            )

        if extension == ".stl":
            vertices, caras, normales = LectorSuperficie._Stl(contenido, archivo)
        else:
            vertices, caras, normales = LectorSuperficie._Npz(contenido, archivo)

        if not np.isfinite(vertices).all():
            raise ArchivoSuperficieIlegible(
                archivo,
                "La superficie contiene coordenadas no finitas.",
            )

        extension_mm = np.ptp(vertices, axis=0)
        diagnostico = EscalaMalla.Resolver(
            float(np.max(extension_mm)),
            autoescalar=autoescalar,
        )
        factor = diagnostico["factor"]
        if factor != 1:
            vertices = vertices * factor

        resultado = AnalizadorMalla.Preparar(
            vertices,
            caras,
            normales,
            suavizarNormales=False,
        )
        puntos, faces, normales_preparadas, borde = resultado
        dimensiones = np.ptp(puntos, axis=0)
        detalle_escala = (
            f"Escala corregida ×{factor:g}. "
            if factor != 1
            else diagnostico["advertencia"]
        )
        info = {
            "nombre": archivo,
            "vertices": len(puntos),
            "caras": len(faces),
            "dimensiones": " × ".join(f"{valor:.1f}" for valor in dimensiones) + " mm",
            "factor_escala": factor,
            "aviso": detalle_escala,
        }
        return (puntos, faces, normales_preparadas, borde), info

    @staticmethod
    def _Npz(contenido: bytes, nombre: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        try:
            with np.load(io.BytesIO(contenido), allow_pickle=False) as datos:
                vertices = np.asarray(datos["vertices"], dtype=np.float64)
                caras = np.asarray(datos["faces"], dtype=np.int32)
                normales = np.asarray(datos["normals"], dtype=np.float64)
        except (OSError, ValueError, KeyError) as exc:
            raise ArchivoSuperficieIlegible(nombre, str(exc)) from exc
        return vertices, caras, normales

    @staticmethod
    def _Stl(contenido: bytes, nombre: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        triangulos = LectorSuperficie._StlBinario(contenido)
        if triangulos is None:
            triangulos = LectorSuperficie._StlAscii(contenido, nombre)
        if len(triangulos) == 0:
            raise ArchivoSuperficieIlegible(nombre, "El STL no contiene triángulos.")

        crudos = triangulos.reshape(-1, 3).astype(np.float64)
        tolerancia = Configuracion.ValorLimite("clip_snap_mm")
        claves = np.round(crudos / tolerancia)
        _claves, indices, inversa = np.unique(
            claves,
            axis=0,
            return_index=True,
            return_inverse=True,
        )
        vertices = crudos[indices]
        caras = inversa.reshape(-1, 3).astype(np.int32)
        normales = LectorSuperficie._Normales(vertices, caras)
        return vertices, caras, normales

    @staticmethod
    def _StlBinario(contenido: bytes) -> np.ndarray | None:
        if len(contenido) < 84:
            return None
        cantidad = struct.unpack_from("<I", contenido, 80)[0]
        if 84 + cantidad * 50 != len(contenido):
            return None
        registro = np.dtype(
            [
                ("normal", "<f4", (3,)),
                ("vertices", "<f4", (3, 3)),
                ("atributo", "<u2"),
            ]
        )
        datos = np.frombuffer(contenido, dtype=registro, count=cantidad, offset=84)
        return datos["vertices"].astype(np.float64)

    @staticmethod
    def _StlAscii(contenido: bytes, nombre: str) -> np.ndarray:
        vertices = []
        try:
            for linea in contenido.decode("utf-8", errors="strict").splitlines():
                partes = linea.strip().split()
                if partes and partes[0].lower() == "vertex" and len(partes) == 4:
                    vertices.append(tuple(float(valor) for valor in partes[1:]))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ArchivoSuperficieIlegible(nombre, "El STL no es binario ni ASCII válido.") from exc
        if len(vertices) % 3:
            raise ArchivoSuperficieIlegible(nombre, "El STL ASCII tiene un triángulo incompleto.")
        return np.asarray(vertices, dtype=np.float64).reshape(-1, 3, 3)

    @staticmethod
    def _Normales(vertices: np.ndarray, caras: np.ndarray) -> np.ndarray:
        triangulos = vertices[caras]
        normales_cara = np.cross(
            triangulos[:, 1] - triangulos[:, 0],
            triangulos[:, 2] - triangulos[:, 0],
        )
        normales = np.zeros_like(vertices)
        for posicion in range(3):
            np.add.at(normales, caras[:, posicion], normales_cara)
        longitudes = np.linalg.norm(normales, axis=1)
        epsilon = Configuracion.ValorLimite("normal_epsilon")
        return normales / np.maximum(longitudes, epsilon)[:, None]
