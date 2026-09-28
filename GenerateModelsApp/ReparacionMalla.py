"""Limpieza segura de la superficie base dentro de Blender.

La reparación conserva una sola capa de caras. No añade espesor ni intenta
extraer una capa de un sólido cerrado, porque no puede decidir de forma fiable
qué lado de una ortesis debe conservar.
"""

from __future__ import annotations

import numpy as np

from .ApiBlender import bmesh, bpy
from .EscalaMalla import EscalaMalla
from .Excepciones import (
    ModificadoresSinAplicar,
    SuperficieInvalida,
    SuperficieNoEsMalla,
)
from .Malla import AnalizadorMalla
from .constants.Nombres import PROP_ROL, RESULT, ROL_RESULTADO, ROL_SUPERFICIE
from .util.Utilidades import Configuracion, Registro


class ReparadorMalla:
    """Limpia una superficie abierta sin convertirla en un volumen."""

    DISTANCIA_FUSION_MM = 1e-6

    @staticmethod
    def _ComponentesCaras(bm) -> list[list]:
        # Las caras conectadas por una arista forman una pieza de superficie.
        pendientes = set(bm.faces)
        componentes = []
        while pendientes:
            inicial = pendientes.pop()
            componente = [inicial]
            cola = [inicial]
            while cola:
                actual = cola.pop()
                for arista in actual.edges:
                    for vecina in arista.link_faces:
                        if vecina in pendientes:
                            pendientes.remove(vecina)
                            componente.append(vecina)
                            cola.append(vecina)
            componentes.append(componente)
        componentes.sort(key=len, reverse=True)
        return componentes

    @staticmethod
    def _EliminarCarasDuplicadas(bm) -> int:
        # Dos caras con los mismos vértices representan dos capas superpuestas.
        bm.verts.index_update()
        vistas = set()
        repetidas = []
        for cara in bm.faces:
            clave = tuple(sorted(vertice.index for vertice in cara.verts))
            if clave in vistas:
                repetidas.append(cara)
            else:
                vistas.add(clave)
        if repetidas:
            bmesh.ops.delete(bm, geom=repetidas, context="FACES_ONLY")
        return len(repetidas)

    @staticmethod
    def _EliminarSinCaras(bm) -> int:
        # Retira vértices y aristas sueltos: no aportan una superficie utilizable.
        sueltos = [vertice for vertice in bm.verts if not vertice.link_faces]
        cantidad = len(sueltos)
        if sueltos:
            bmesh.ops.delete(bm, geom=sueltos, context="VERTS")
        return cantidad

    @staticmethod
    def _ArreglarBmesh(
        bm,
        escala: tuple[float, float, float],
        autoescalar: bool = True,
    ) -> dict:
        # Hornea la escala en las coordenadas para dejar el objeto en (1, 1, 1).
        for vertice in bm.verts:
            vertice.co.x *= escala[0]
            vertice.co.y *= escala[1]
            vertice.co.z *= escala[2]

        # STL no declara unidades. Solo se corrigen factores decimales que dejan
        # el eje mayor dentro del rango de una superficie de ortesis.
        if bm.verts:
            coordenadas = np.array([vertice.co[:] for vertice in bm.verts], dtype=np.float64)
            dimension_maxima = float(np.max(np.ptp(coordenadas, axis=0)))
        else:
            dimension_maxima = 0.0
        diagnostico_escala = EscalaMalla.Resolver(
            dimension_maxima,
            autoescalar=autoescalar,
        )
        factor_escala = diagnostico_escala["factor"]
        if factor_escala != 1.0:
            for vertice in bm.verts:
                vertice.co *= factor_escala

        vertices_antes = len(bm.verts)
        bmesh.ops.remove_doubles(
            bm,
            verts=list(bm.verts),
            dist=ReparadorMalla.DISTANCIA_FUSION_MM,
        )
        bm.verts.ensure_lookup_table()
        fusionados = vertices_antes - len(bm.verts)

        # Las caras sin área pueden aparecer después de unir vértices coincidentes.
        limite_area = Configuracion.ValorLimite("degenerate_area")
        degeneradas = [cara for cara in bm.faces if cara.calc_area() < limite_area]
        if degeneradas:
            bmesh.ops.delete(bm, geom=degeneradas, context="FACES_ONLY")
        cantidad_degeneradas = len(degeneradas)

        duplicadas = ReparadorMalla._EliminarCarasDuplicadas(bm)
        sueltos = ReparadorMalla._EliminarSinCaras(bm)

        # La base de una ortesis debe ser una sola pieza. Se conserva la mayor.
        componentes = ReparadorMalla._ComponentesCaras(bm)
        caras_fragmentos = sum(len(componente) for componente in componentes[1:])
        if caras_fragmentos:
            bmesh.ops.delete(
                bm,
                geom=[cara for componente in componentes[1:] for cara in componente],
                context="FACES",
            )
            sueltos += ReparadorMalla._EliminarSinCaras(bm)

        if not bm.faces:
            raise SuperficieInvalida("La reparación no encontró una capa de caras utilizable.")

        # El núcleo trabaja con triángulos y exige orientación consistente.
        bmesh.ops.triangulate(bm, faces=list(bm.faces))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.normal_update()
        bm.verts.index_update()
        bm.faces.index_update()

        return {
            "fusionados": fusionados,
            "degeneradas": cantidad_degeneradas,
            "duplicadas": duplicadas,
            "sueltos": sueltos,
            "fragmentos": max(0, len(componentes) - 1),
            "caras_fragmentos": caras_fragmentos,
            "factor_escala": factor_escala,
            "dimension_antes_mm": diagnostico_escala["dimension_antes_mm"],
            "dimension_despues_mm": diagnostico_escala["dimension_despues_mm"],
            "advertencia_escala": diagnostico_escala["advertencia"],
        }

    @staticmethod
    def _ValidarBmesh(bm) -> None:
        # Valida antes de escribir para que un fallo no destruya la malla original.
        vertices = np.array([vertice.co[:] for vertice in bm.verts], dtype=np.float64)
        caras = np.array(
            [[vertice.index for vertice in cara.verts] for cara in bm.faces],
            dtype=np.int32,
        ).reshape(-1, 3)
        normales = np.array([vertice.normal[:] for vertice in bm.verts], dtype=np.float64)
        AnalizadorMalla.Preparar(
            vertices,
            caras,
            normales,
            suavizarNormales=False,
        )

    @staticmethod
    def Arreglar(objeto, autoescalar: bool = True) -> dict:
        """Repara la malla activa y devuelve un resumen de lo retirado."""
        if objeto is None or getattr(objeto, "type", None) != "MESH":
            raise SuperficieNoEsMalla()
        if objeto.name == RESULT or objeto.get(PROP_ROL) == ROL_RESULTADO:
            raise SuperficieInvalida("Seleccione la superficie base, no la ortesis ya generada.")
        if objeto.mode != "OBJECT":
            raise SuperficieInvalida("Salga de Edit Mode antes de arreglar la superficie.")
        if objeto.modifiers:
            raise ModificadoresSinAplicar(objeto.name)

        logger = Registro.Obtener("reparacion")
        escala = tuple(float(valor) for valor in objeto.scale)
        bm = bmesh.new()
        try:
            bm.from_mesh(objeto.data)
            resumen = ReparadorMalla._ArreglarBmesh(
                bm,
                escala,
                autoescalar=autoescalar,
            )
            ReparadorMalla._ValidarBmesh(bm)

            # Una malla compartida se separa para no modificar otros objetos.
            if objeto.data.users > 1:
                objeto.data = objeto.data.copy()
            bm.to_mesh(objeto.data)
            objeto.data.update()
        finally:
            bm.free()

        objeto.scale = (1.0, 1.0, 1.0)
        objeto[PROP_ROL] = ROL_SUPERFICIE
        bpy.context.view_layer.objects.active = objeto
        objeto.select_set(True)
        logger.info(
            "Superficie reparada: %s vértices fusionados, %s caras degeneradas, "
            "%s caras duplicadas, %s elementos sueltos, %s fragmentos retirados y "
            "factor de escala %.4g.",
            resumen["fusionados"],
            resumen["degeneradas"],
            resumen["duplicadas"],
            resumen["sueltos"],
            resumen["fragmentos"],
            resumen["factor_escala"],
        )
        if resumen["advertencia_escala"]:
            logger.warning("%s", resumen["advertencia_escala"])
        return resumen
