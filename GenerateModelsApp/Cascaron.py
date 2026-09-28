"""Recorte de celdas y cascarón de espesor variable.

El material se añade en contra de la normal: la normal apunta al contacto.
"""

from __future__ import annotations

import numpy as np

from .Excepciones import GeometriaInconsistente, NormalesInvalidas, SuperficieEliminadaPorPatron
from .util.Utilidades import Configuracion, Registro


class Cascaron:
    """Pasa de una superficie abierta a un sólido de espesor conocido."""

    @staticmethod
    def Smooth01(t):
        # Curva de Hermite: entra y sale con pendiente cero entre 0 y 1.
        t = np.clip(t, 0, 1)
        return t * t * (3 - 2 * t)

    @staticmethod
    def Recortar(p, f, n, scalar):
        # Recorta donde el escalar es negativo y comparte el corte de cada arista.
        logger = Registro.Obtener("cascaron")
        puntos = np.asarray(p, dtype=np.float64)
        caras = np.asarray(f, dtype=np.int32)
        normales = np.asarray(n, dtype=np.float64)
        valores = np.asarray(scalar, dtype=np.float64)
        if len(valores) != len(puntos) or normales.shape != puntos.shape:
            raise GeometriaInconsistente(
                "El recorte recibió arreglos de distinta longitud.",
                detalle=f"puntos={len(puntos)}, escalar={len(valores)}, normales={normales.shape}",
            )
        # Evita cuñas por intersecciones casi coincidentes al pasar a float32 en Blender.
        valores = np.where(np.abs(valores) < Configuracion.ValorLimite("clip_snap_mm"), 0.0, valores)
        epsilon = Configuracion.ValorLimite("normal_epsilon")
        verts = []
        normals = []
        faces = []
        original = {}
        crossings = {}
        descartadas = 0

        def verticeOriginal(indice):
            # Reutiliza el vértice interior para no duplicarlo en cada cara.
            if indice not in original:
                original[indice] = len(verts)
                verts.append(puntos[indice])
                normals.append(normales[indice])
            return original[indice]

        def cruce(a, b):
            # Punto de la arista donde el escalar cambia de signo.
            if valores[a] == 0:
                return verticeOriginal(a)
            if valores[b] == 0:
                return verticeOriginal(b)
            clave = tuple(sorted((a, b)))
            if clave not in crossings:
                t = float(valores[a] / (valores[a] - valores[b]))
                coordenada = (1 - t) * puntos[a] + t * puntos[b]
                normal = (1 - t) * normales[a] + t * normales[b]
                norma = float(np.linalg.norm(normal))
                if norma < epsilon:
                    raise NormalesInvalidas(detalle=f"Normal nula al cortar la arista {clave}.")
                normal = normal / norma
                crossings[clave] = len(verts)
                verts.append(coordenada)
                normals.append(normal)
            return crossings[clave]

        for face in caras:
            poly = []
            for a, b in zip(face, np.roll(face, -1)):
                a, b = int(a), int(b)
                inside = valores[a] >= 0
                other = valores[b] >= 0
                if inside:
                    poly.append(verticeOriginal(a))
                if inside != other:
                    poly.append(cruce(a, b))
            poly = list(dict.fromkeys(poly))
            if len(poly) < 3:
                descartadas += 1
                continue
            for j in range(1, len(poly) - 1):
                faces.append((poly[0], poly[j], poly[j + 1]))
        if descartadas:
            logger.debug("Caras colapsadas al recortar: %s", descartadas)
        if not faces:
            raise SuperficieEliminadaPorPatron()
        faces = np.array(faces, dtype=np.int32)
        used, remap = np.unique(faces, return_inverse=True)
        logger.info("Superficie recortada: %s vértices, %s triángulos.", len(used), len(faces))
        return np.array(verts)[used], remap.reshape(-1, 3), np.array(normals)[used]

    @staticmethod
    def Engrosar(p, f, n, t):
        """Añade espesor a las caras existentes; nunca rellena una abertura.

        Cada arista libre se une únicamente con su copia exterior. Los labios
        opuestos del canal y el contorno del dedo no se conectan entre sí.
        El volumen de la pared es cerrado, aunque la ortesis siga abierta arriba.
        """
        logger = Registro.Obtener("cascaron")
        puntos = np.asarray(p, dtype=np.float64)
        caras = np.asarray(f)
        normales = np.asarray(n, dtype=np.float64)
        espesor = np.asarray(t, dtype=np.float64).reshape(-1)
        if espesor.size not in (1, len(puntos)):
            raise GeometriaInconsistente(
                "El espesor no coincide con la cantidad de vértices.",
                detalle=f"espesor={espesor.size}, vértices={len(puntos)}",
            )
        if not np.isfinite(espesor).all() or np.any(espesor < 0):
            raise GeometriaInconsistente("El espesor debe ser finito y no negativo.")
        cantidad = len(puntos)
        # Las normales coherentes de Blender apuntan fuera de la superficie.
        # El comportamiento predeterminado debe añadir material en ese sentido.
        exterior = puntos + normales * espesor.reshape(-1, 1)
        faces = [tuple(int(v) for v in cara) for cara in caras]
        completo = faces + [tuple(v + cantidad for v in cara[::-1]) for cara in faces]
        aristas = {}
        for face in faces:
            for a, b in zip(face, face[1:] + face[:1]):
                clave = (min(a, b), max(a, b))
                if clave in aristas:
                    aristas[clave] = None
                else:
                    aristas[clave] = (a, b)
        muros = 0
        for extremos in aristas.values():
            if extremos:
                a, b = extremos
                completo.append((b, a, a + cantidad, b + cantidad))
                muros += 1
        logger.info(
            "Cascarón cerrado: %s vértices, %s caras, %s muros de contorno.",
            cantidad * 2,
            len(completo),
            muros,
        )
        return np.vstack([puntos, exterior]), completo

    @staticmethod
    def Cerrar(p, f, n, t):
        """Alias compatible: cerrar el espesor no significa tapar el canal."""
        return Cascaron.Engrosar(p, f, n, t)

    @staticmethod
    def VolumenMm3(vertices, faces) -> float:
        # Volumen del cascarón antes del voxel. No es el filamento de la impresora.
        logger = Registro.Obtener("cascaron")
        puntos = np.asarray(vertices, dtype=np.float64)
        total = 0.0
        triangulos = 0
        for cara in faces:
            indices = [int(indice) for indice in cara]
            if len(indices) < 3:
                continue
            for posicion in range(1, len(indices) - 1):
                a, b, c = indices[0], indices[posicion], indices[posicion + 1]
                total += float(np.dot(puntos[a], np.cross(puntos[b], puntos[c])))
                triangulos += 1
        if triangulos == 0:
            raise GeometriaInconsistente("No hay caras para calcular el volumen.")
        volumen = abs(total) / 6.0
        if total < 0:
            logger.debug("El cascarón tiene orientación negativa; el volumen se toma en valor absoluto.")
        return float(volumen)
