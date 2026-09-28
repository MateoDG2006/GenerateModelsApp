"""Análisis de la superficie abierta, sin Blender.

La distancia al contorno es geodésica sobre las aristas y queda en milímetros.
"""

from __future__ import annotations

import heapq

import numpy as np

from .Excepciones import (
    AristasNoManifold,
    GeometriaInconsistente,
    NormalesInvalidas,
    SolidoCerrado,
    SuperficieSinCaras,
    SuperficieInvalida,
    VerticesSueltos,
)
from .util.Utilidades import Configuracion, Registro


class AnalizadorMalla:
    """Comprueba que la base sea una superficie abierta y mide el borde."""

    @staticmethod
    def Preparar(vertices, caras, normales, *, suavizarNormales: bool):
        # Devuelve vértices, triángulos, normales unitarias y distancia al contorno.
        logger = Registro.Obtener("malla")
        puntos = np.asarray(vertices, dtype=np.float64)
        faces = np.asarray(caras, dtype=np.int32)
        normales_entrada = np.asarray(normales, dtype=np.float64)
        if puntos.ndim != 2 or puntos.shape[1] != 3:
            raise NormalesInvalidas(detalle="Los vértices no tienen forma (n, 3).")
        if faces.size == 0:
            raise SuperficieSinCaras()
        if faces.ndim != 2 or faces.shape[1] != 3:
            raise GeometriaInconsistente("La superficie de trabajo debe estar triangulada.")
        if normales_entrada.shape != puntos.shape:
            raise NormalesInvalidas(detalle="Las normales no coinciden con los vértices.")
        if not np.isfinite(puntos).all() or not np.isfinite(normales_entrada).all():
            raise SuperficieInvalida("La superficie contiene coordenadas o normales no finitas.")
        if faces.min() < 0 or faces.max() >= len(puntos):
            raise GeometriaInconsistente("Las caras hacen referencia a vértices inexistentes.")
        areas = np.linalg.norm(np.cross(puntos[faces[:, 1]] - puntos[faces[:, 0]],
                                       puntos[faces[:, 2]] - puntos[faces[:, 0]]), axis=1) / 2
        if np.any(areas < Configuracion.ValorLimite("degenerate_area")):
            raise SuperficieInvalida("La base contiene caras degeneradas; limpie la superficie antes de generar.")
        if len(np.unique(np.sort(faces, axis=1), axis=0)) != len(faces):
            raise SuperficieInvalida("La base contiene caras duplicadas; use una sola capa de caras.")

        # Cada triángulo aporta tres aristas. Las que aparecen una vez son el contorno.
        todas = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
        aristas, cuentas = np.unique(np.sort(todas, axis=1), axis=0, return_counts=True)
        contorno = aristas[cuentas == 1]
        if not len(contorno):
            raise SolidoCerrado()
        if np.max(cuentas) > 2:
            raise AristasNoManifold()
        if len(np.unique(todas, axis=0)) != len(todas):
            raise SuperficieInvalida("Hay caras con orientación inconsistente. Recalcule las normales de la base.")
        grado = np.bincount(aristas.ravel(), minlength=len(puntos))
        if np.any(grado == 0):
            raise VerticesSueltos()
        grado_borde = np.bincount(contorno.ravel(), minlength=len(puntos))
        if np.any((grado_borde != 0) & (grado_borde != 2)):
            raise SuperficieInvalida("El contorno se toca en un vértice; separe o conecte correctamente las caras.")

        normales_suaves = normales_entrada.copy()
        if suavizarNormales:
            grado = np.bincount(aristas.ravel(), minlength=len(puntos))
            if np.any(grado == 0):
                raise VerticesSueltos()
            epsilon = Configuracion.ValorLimite("normal_epsilon")
            # Promedia cada normal con las de sus vecinos, varias veces.
            for _ in range(int(Configuracion.ValorLimite("normal_smooth_iterations"))):
                promedio = np.zeros_like(normales_suaves)
                np.add.at(promedio, aristas[:, 0], normales_suaves[aristas[:, 1]])
                np.add.at(promedio, aristas[:, 1], normales_suaves[aristas[:, 0]])
                normales_suaves = 0.5 * normales_suaves + 0.5 * promedio / grado[:, None]
                normales_suaves /= np.maximum(
                    np.linalg.norm(normales_suaves, axis=1)[:, None],
                    epsilon,
                )

        longitudes = np.linalg.norm(normales_suaves, axis=1)
        if np.min(longitudes) < Configuracion.ValorLimite("min_normal_length"):
            raise NormalesInvalidas()
        normales_suaves = normales_suaves / longitudes[:, None]

        # Distancia geodésica: el camino más corto por las aristas hasta el contorno.
        adyacencia = [[] for _ in puntos]
        longitudes_arista = np.linalg.norm(puntos[aristas[:, 0]] - puntos[aristas[:, 1]], axis=1)
        for (origen, destino), longitud in zip(aristas, longitudes_arista):
            adyacencia[origen].append((int(destino), float(longitud)))
            adyacencia[destino].append((int(origen), float(longitud)))
        pendientes = [0]
        conectados = {0}
        while pendientes:
            for vecino, _ in adyacencia[pendientes.pop()]:
                if vecino not in conectados:
                    conectados.add(vecino)
                    pendientes.append(vecino)
        if len(conectados) != len(puntos):
            raise SuperficieInvalida("La base debe ser una sola superficie conectada, sin capas o piezas separadas.")

        distancia = np.full(len(puntos), np.inf)
        cola = []
        for vertice in np.unique(contorno):
            distancia[vertice] = 0
            heapq.heappush(cola, (0, int(vertice)))
        while cola:
            recorrida, actual = heapq.heappop(cola)
            if recorrida > distancia[actual]:
                continue
            for vecino, longitud in adyacencia[actual]:
                propuesta = recorrida + longitud
                if propuesta < distancia[vecino]:
                    distancia[vecino] = propuesta
                    heapq.heappush(cola, (propuesta, vecino))

        if not np.isfinite(distancia).all():
            logger.warning("Hay vértices sin camino al contorno; su distancia geodésica quedó infinita.")
        logger.info(
            "Superficie preparada: %s vértices, %s triángulos, %s aristas de contorno.",
            len(puntos),
            len(faces),
            len(contorno),
        )
        return puntos, faces, normales_suaves, distancia
