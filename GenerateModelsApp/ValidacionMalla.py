"""Comprobación geométrica de la malla ya generada.

Revisa bordes abiertos, aristas no manifold, caras degeneradas, piezas
separadas y cruces entre triángulos que no comparten vértices.
No certifica resistencia ni ajuste.
"""

from __future__ import annotations

import json

from .ApiBlender import BVHTree, bmesh, intersect_ray_tri
from .Excepciones import MallaNoConstruida, ModeloNoGenerado
from .constants.Nombres import PROP_VALIDACION
from .util.Utilidades import Configuracion, Registro


class ValidadorMalla:
    """Informa si OL_Ortesis es una sola pieza cerrada."""

    @staticmethod
    def _Componentes(bm) -> int:
        # Cuenta grupos de vértices conectados. Una ortesis válida tiene uno.
        vistos = set()
        piezas = 0
        for vertice in bm.verts:
            if vertice in vistos:
                continue
            piezas += 1
            pendientes = [vertice]
            vistos.add(vertice)
            while pendientes:
                actual = pendientes.pop()
                for arista in actual.link_edges:
                    vecino = arista.other_vert(actual)
                    if vecino not in vistos:
                        vistos.add(vecino)
                        pendientes.append(vecino)
        return piezas

    @staticmethod
    def _Cruces(bm, tree) -> int:
        # Cuenta triángulos que se atraviesan sin compartir vértices.
        cruces = 0
        for primera, segunda in tree.overlap(tree):
            if primera >= segunda:
                continue
            cara_a, cara_b = bm.faces[primera], bm.faces[segunda]
            if set(cara_a.verts) & set(cara_b.verts):
                continue
            hay_cruce = False
            for origen, destino in ((cara_a, cara_b), (cara_b, cara_a)):
                triangulo = [vertice.co for vertice in destino.verts]
                for arista in origen.edges:
                    inicio, fin = [vertice.co for vertice in arista.verts]
                    direccion = fin - inicio
                    if direccion.length_squared < 1e-15:
                        continue
                    posicion = intersect_ray_tri(*triangulo, direccion, inicio, True)
                    if posicion is None:
                        continue
                    avance = (posicion - inicio).dot(direccion) / direccion.length_squared
                    if 1e-6 < avance < 1 - 1e-6:
                        hay_cruce = True
            if hay_cruce:
                cruces += 1
        return cruces

    @staticmethod
    def Comprobar(ob, intersections=True):
        # Guarda el informe en la propiedad ol_validation del objeto.
        logger = Registro.Obtener("validacion")
        if ob is None:
            raise ModeloNoGenerado()
        if getattr(ob, "type", None) != "MESH" or ob.data is None:
            raise MallaNoConstruida("El objeto a comprobar no es una malla.")

        bm = bmesh.new()
        bm.from_mesh(ob.data)
        try:
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            bm.faces.ensure_lookup_table()
            area_minima = Configuracion.ValorLimite("degenerate_area")
            informe = {
                "open_edges": sum(arista.is_boundary for arista in bm.edges),
                "nonmanifold_edges": sum(not arista.is_manifold for arista in bm.edges),
                "degenerate_faces": sum(cara.calc_area() < area_minima for cara in bm.faces),
                "triangles": len(bm.faces),
            }
            informe["components"] = ValidadorMalla._Componentes(bm)
            informe["triangle_crossings"] = 0
            if intersections:
                arbol = BVHTree.FromBMesh(bm, epsilon=0)
                informe["triangle_crossings"] = ValidadorMalla._Cruces(bm, arbol)
        except (RuntimeError, ValueError) as exc:
            raise MallaNoConstruida(str(exc)) from exc
        finally:
            bm.free()

        informe["ok"] = (
            not any(
                informe[clave]
                for clave in ("open_edges", "nonmanifold_edges", "degenerate_faces", "triangle_crossings")
            )
            and informe["components"] == 1
        )
        ob[PROP_VALIDACION] = json.dumps(informe)
        if informe["ok"]:
            logger.info("Malla cerrada y conectada: %s triángulos.", informe["triangles"])
        else:
            logger.warning("Geometría a revisar: %s", informe)
        return informe
