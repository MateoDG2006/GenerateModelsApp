"""Carga y lectura de la superficie interior dentro de Blender.

Este módulo sí depende de Blender. El análisis geométrico está en AnalizadorMalla.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .ApiBlender import bpy, bmesh
from .EscalaMalla import EscalaMalla
from .Excepciones import (
    ArchivoSuperficieIlegible,
    ArchivoSuperficieNoEncontrado,
    EscalaSinAplicar,
    ModificadoresSinAplicar,
    SuperficieNoEsMalla,
    SuperficieInvalida,
)
from .Malla import AnalizadorMalla
from .constants.Nombres import (
    ARCHIVO_SUPERFICIE,
    ATTR_NORMAL,
    PROP_ROL,
    ROL_SUPERFICIE,
    SOURCE,
    RESULT,
    ROL_RESULTADO,
)
from .util.Utilidades import Configuracion, Registro


class SuperficieInterior:
    """Prepara una copia de la superficie elegida, sin cerrar sus aberturas."""

    diagnostico_escala: dict = {
        "factor": 1.0,
        "factor_sugerido": 1.0,
        "dimension_antes_mm": 0.0,
        "dimension_despues_mm": 0.0,
        "advertencia": "",
    }

    @staticmethod
    def _Candidatos(path=None) -> list[Path]:
        # Orden de búsqueda: ruta pedida, assets del repo, junto al módulo y junto al blend.
        rutas = []
        if path:
            rutas.append(Path(path))
        if "__file__" in globals():
            rutas.append(Path(__file__).resolve().parent.parent / "assets" / ARCHIVO_SUPERFICIE)
            rutas.append(Path(__file__).resolve().parent / ARCHIVO_SUPERFICIE)
        if bpy.data.filepath:
            rutas.append(Path(bpy.data.filepath).parent / ARCHIVO_SUPERFICIE)
        return rutas

    @staticmethod
    def Cargar(path=None):
        # Trae la superficie en milímetros, sin volver a escalar, y la oculta.
        logger = Registro.Obtener("superficie")
        obj = bpy.data.objects.get(SOURCE)
        if obj is not None:
            logger.info("Superficie ya presente en la escena: %s", obj.name)
            return obj

        candidatos = SuperficieInterior._Candidatos(path)
        elegido = next((ruta for ruta in candidatos if ruta.is_file()), None)
        if elegido is None:
            raise ArchivoSuperficieNoEncontrado(
                detalle="; ".join(str(ruta) for ruta in candidatos) or "sin rutas candidatas"
            )
        logger.info("Cargando superficie desde %s", elegido)
        try:
            with np.load(elegido, allow_pickle=False) as datos:
                vertices = datos["vertices"]
                faces = datos["faces"]
                normals = datos["normals"]
        except (OSError, ValueError, KeyError) as exc:
            raise ArchivoSuperficieIlegible(str(elegido), str(exc)) from exc

        malla = bpy.data.meshes.new(SOURCE)
        malla.from_pydata(vertices, [], faces)
        malla.update()
        atributo = malla.attributes.new(ATTR_NORMAL, "FLOAT_VECTOR", "POINT")
        atributo.data.foreach_set("vector", normals.astype(np.float32).ravel())
        obj = bpy.data.objects.new(SOURCE, malla)
        bpy.context.scene.collection.objects.link(obj)
        unidades = bpy.context.scene.unit_settings
        unidades.system = "METRIC"
        unidades.scale_length = 0.001
        unidades.length_unit = "MILLIMETERS"
        obj[PROP_ROL] = ROL_SUPERFICIE
        obj.hide_render = True
        obj.hide_set(True)
        logger.info(
            "Superficie cargada (%s vértices) y unidades de la escena fijadas en milímetros.",
            len(vertices),
        )
        return obj

    @staticmethod
    def _CorregirUnidades(puntos: np.ndarray, autoescalar: bool) -> tuple[np.ndarray, float]:
        # La copia de trabajo pasa a milímetros. La malla de la escena no se modifica.
        dimension = float(np.max(np.ptp(puntos, axis=0))) if len(puntos) else 0.0
        diagnostico = EscalaMalla.Resolver(dimension, autoescalar=autoescalar)
        SuperficieInterior.diagnostico_escala = diagnostico
        factor = float(diagnostico["factor"])
        logger = Registro.Obtener("superficie")
        if diagnostico["advertencia"]:
            logger.warning("%s", diagnostico["advertencia"])
        elif factor != 1.0:
            logger.info(
                "Autoescala x%g: %.2f a %.2f mm.",
                factor,
                diagnostico["dimension_antes_mm"],
                diagnostico["dimension_despues_mm"],
            )
            puntos = puntos * factor
        return puntos, factor

    @staticmethod
    def Leer(source, *, paso_mm=None, autoescalar: bool = True):
        # Lee la malla de Blender y devuelve vértices, caras, normales y distancia al borde.
        logger = Registro.Obtener("superficie")
        if source is None or getattr(source, "type", None) != "MESH":
            raise SuperficieNoEsMalla()
        if source.name == RESULT or source.get(PROP_ROL) == ROL_RESULTADO:
            raise SuperficieInvalida("Seleccione la superficie base, no la ortesis ya generada.")
        if source.mode != 'OBJECT':
            raise SuperficieInvalida("Salga de Edit Mode antes de generar para usar las caras actuales.")
        if source.modifiers:
            raise ModificadoresSinAplicar(getattr(source, "name", SOURCE))
        escala = tuple(source.scale)
        tolerancia = Configuracion.ValorLimite("scale_tolerance")
        if any(abs(valor - 1) > tolerancia for valor in escala):
            raise EscalaSinAplicar(escala)

        malla = source.data
        malla.calc_loop_triangles()
        coordenadas = np.empty(len(malla.vertices) * 3)
        malla.vertices.foreach_get("co", coordenadas)
        puntos = coordenadas.reshape(-1, 3)
        caras = np.array([triangulo.vertices[:] for triangulo in malla.loop_triangles], dtype=np.int32)
        # Siempre leer caras y normales actuales: un atributo antiguo o una caché
        # basada en sumas puede ignorar la apertura recién editada del dedo.
        if paso_mm is None:
            normales = np.array([vertice.normal[:] for vertice in malla.vertices])
            puntos, _factor = SuperficieInterior._CorregirUnidades(puntos, autoescalar)
            return AnalizadorMalla.Preparar(puntos, caras, normales, suavizarNormales=False)
        if not np.isfinite(paso_mm) or paso_mm <= 0:
            raise SuperficieInvalida("El paso de la superficie debe ser positivo y finito.")

        dimension = float(np.max(np.ptp(puntos, axis=0))) if len(puntos) else 0.0
        arista = SuperficieInterior._AristaMayor(puntos, caras)
        resultado, diagnostico = EscalaMalla.Aplicar(
            dimension,
            autoescalar,
            lambda factor: SuperficieInterior._Subdividir(malla, factor, paso_mm),
            arista_maxima=arista,
            paso_mm=paso_mm,
            n_caras=len(caras),
        )
        SuperficieInterior.diagnostico_escala = diagnostico
        factor = float(diagnostico["factor"])
        if diagnostico["advertencia"]:
            logger.warning("%s", diagnostico["advertencia"])
        elif factor != 1.0:
            logger.info(
                "Autoescala x%g: %.2f a %.2f mm.",
                factor,
                diagnostico["dimension_antes_mm"],
                diagnostico["dimension_despues_mm"],
            )
        logger.info(
            "Superficie subdividida en una copia: %s vértices, paso %.3f mm.",
            len(resultado[0]),
            paso_mm,
        )
        return resultado

    @staticmethod
    def _AristaMayor(puntos: np.ndarray, caras: np.ndarray) -> float:
        if len(caras) == 0 or len(puntos) == 0:
            return 0.0
        pares = np.vstack((caras[:, [0, 1]], caras[:, [1, 2]], caras[:, [2, 0]]))
        return float(np.linalg.norm(puntos[pares[:, 0]] - puntos[pares[:, 1]], axis=1).max())

    @staticmethod
    def _Subdividir(malla, factor: float, paso_mm: float):
        # Cada intento parte de la malla original. La base de la escena no cambia.
        bm = bmesh.new()
        try:
            bm.from_mesh(malla)
            SuperficieInterior._Tablas(bm)
            if factor != 1.0:
                for vertice in bm.verts:
                    vertice.co *= factor
            SuperficieInterior._Triangulo(bm)
            limite = int(Configuracion.ValorLimite("max_surface_vertices"))
            rondas = int(Configuracion.ValorLimite("surface_subdivision_iterations"))
            detenida = False
            for _ in range(rondas):
                SuperficieInterior._Tablas(bm)
                largas = [e for e in bm.edges if e.calc_length() > paso_mm * 1.001]
                if not largas:
                    break
                # El operador revienta Blender si la pasada cuadruplica una malla ya grande.
                if (
                    len(bm.verts) + len(largas) > limite
                    or len(largas) > limite // 2
                    or (
                        len(bm.edges) > 0
                        and len(largas) * 2 > len(bm.edges)
                        and len(bm.faces) * 4 > limite
                    )
                ):
                    detenida = True
                    break
                bmesh.ops.subdivide_edges(bm, edges=largas, cuts=1, use_grid_fill=True)
                SuperficieInterior._Tablas(bm)
                SuperficieInterior._Triangulo(bm)
            SuperficieInterior._Tablas(bm)
            if not detenida and (
                len(bm.verts) > limite
                or any(e.calc_length() > paso_mm * 1.001 for e in bm.edges)
            ):
                raise SuperficieInvalida(
                    "No se alcanzó el paso de superficie. Aumente el paso o revise las unidades en mm."
                )
            if detenida:
                Registro.Obtener("superficie").info(
                    "Subdivisión detenida en %s vértices, por debajo del paso %.3f mm.",
                    len(bm.verts),
                    paso_mm,
                )
            bm.normal_update()
            bm.verts.index_update()
            bm.faces.index_update()
            SuperficieInterior._Tablas(bm)
            puntos = np.array([v.co[:] for v in bm.verts])
            caras = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=np.int32)
            normales = np.array([v.normal[:] for v in bm.verts])
        finally:
            bm.free()
        return AnalizadorMalla.Preparar(puntos, caras, normales, suavizarNormales=True)

    @staticmethod
    def _Tablas(bm) -> None:
        # Sin esto, la pasada siguiente recorre punteros ya liberados y Blender se cierra.
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

    @staticmethod
    def _Triangulo(bm) -> None:
        SuperficieInterior._Tablas(bm)
        pendientes = [cara for cara in bm.faces if len(cara.verts) != 3]
        if pendientes:
            bmesh.ops.triangulate(bm, faces=pendientes)
            SuperficieInterior._Tablas(bm)
