"""Refinamiento triangular independiente de Blender para evaluar patrones."""

from __future__ import annotations

import numpy as np

from .Excepciones import NormalesInvalidas, SuperficieInvalida
from .Malla import AnalizadorMalla
from .util.Utilidades import Configuracion, Registro


class RefinadorMalla:
    """Divide únicamente las aristas largas y conserva una superficie conectada."""

    @staticmethod
    def Refinar(vertices, caras, normales, pasoMm: float):
        if not np.isfinite(pasoMm) or pasoMm <= 0:
            raise SuperficieInvalida("El paso de la superficie debe ser positivo y finito.")

        puntos = np.asarray(vertices, dtype=np.float64)
        faces = np.asarray(caras, dtype=np.int32)
        normals = np.asarray(normales, dtype=np.float64)
        limite = int(Configuracion.ValorLimite("max_surface_vertices"))
        rondas = int(Configuracion.ValorLimite("surface_subdivision_iterations"))
        epsilon = Configuracion.ValorLimite("normal_epsilon")

        for _ in range(rondas):
            todas = np.vstack(
                [faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]
            )
            aristas = np.unique(np.sort(todas, axis=1), axis=0)
            longitudes = np.linalg.norm(
                puntos[aristas[:, 0]] - puntos[aristas[:, 1]],
                axis=1,
            )
            largas = aristas[longitudes > pasoMm * 1.001]
            if not len(largas):
                break
            if len(puntos) + len(largas) > limite:
                raise SuperficieInvalida(
                    "La subdivisión supera el límite de detalle. "
                    "Aumente el paso de superficie."
                )

            inicio = len(puntos)
            indices = {
                (int(a), int(b)): inicio + posicion
                for posicion, (a, b) in enumerate(largas)
            }
            nuevos_puntos = (puntos[largas[:, 0]] + puntos[largas[:, 1]]) * 0.5
            nuevas_normales = normals[largas[:, 0]] + normals[largas[:, 1]]
            longitudes_normales = np.linalg.norm(nuevas_normales, axis=1)
            if np.any(longitudes_normales < epsilon):
                raise NormalesInvalidas(
                    detalle="Dos normales opuestas impiden refinar una arista."
                )
            nuevas_normales /= longitudes_normales[:, None]

            nuevas_caras = []
            for a, b, c in faces:
                a, b, c = int(a), int(b), int(c)
                ab = indices.get((min(a, b), max(a, b)))
                bc = indices.get((min(b, c), max(b, c)))
                ca = indices.get((min(c, a), max(c, a)))
                mascara = (ab is not None, bc is not None, ca is not None)

                if mascara == (False, False, False):
                    nuevas_caras.append((a, b, c))
                elif mascara == (True, False, False):
                    nuevas_caras.extend(((a, ab, c), (ab, b, c)))
                elif mascara == (False, True, False):
                    nuevas_caras.extend(((b, bc, a), (bc, c, a)))
                elif mascara == (False, False, True):
                    nuevas_caras.extend(((c, ca, b), (ca, a, b)))
                elif mascara == (True, True, False):
                    nuevas_caras.extend(((b, bc, ab), (a, ab, bc), (a, bc, c)))
                elif mascara == (False, True, True):
                    nuevas_caras.extend(((c, ca, bc), (b, bc, ca), (b, ca, a)))
                elif mascara == (True, False, True):
                    nuevas_caras.extend(((a, ab, ca), (c, ca, ab), (c, ab, b)))
                else:
                    nuevas_caras.extend(
                        (
                            (a, ab, ca),
                            (ab, b, bc),
                            (ca, bc, c),
                            (ab, bc, ca),
                        )
                    )

            puntos = np.vstack((puntos, nuevos_puntos))
            normals = np.vstack((normals, nuevas_normales))
            faces = np.asarray(nuevas_caras, dtype=np.int32)

        todas = np.vstack(
            [faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]
        )
        aristas = np.unique(np.sort(todas, axis=1), axis=0)
        if np.any(
            np.linalg.norm(
                puntos[aristas[:, 0]] - puntos[aristas[:, 1]],
                axis=1,
            )
            > pasoMm * 1.001
        ):
            raise SuperficieInvalida(
                "No se alcanzó el paso de superficie. "
                "Aumente el paso o revise las unidades en mm."
            )

        Registro.Obtener("malla").info(
            "Superficie refinada sin Blender: %s vértices, %s triángulos, paso %.3f mm.",
            len(puntos),
            len(faces),
            pasoMm,
        )
        return AnalizadorMalla.Preparar(
            puntos,
            faces,
            normals,
            suavizarNormales=True,
        )
