"""Crea o actualiza el objeto OL_Ortesis en la escena de Blender."""

from __future__ import annotations

import json

from .ApiBlender import bmesh, bpy
from .Excepciones import (
    GeometriaFragmentada,
    MallaNoConstruida,
    ReconstruccionFallida,
    ResolucionDemasiadoFina,
)
from .Modeling import Model3DForPrinting
from .Superficie import SuperficieInterior
from .constants.Nombres import (
    ALCANCE,
    MALLA_GEOMETRIA,
    MOD_RECONSTRUCCION,
    MOD_SUAVIZADO,
    PROP_ALCANCE,
    PROP_CARAS,
    PROP_CONFIG,
    PROP_FRAGMENTOS,
    PROP_RESOLUCION,
    PROP_ROL,
    PROP_VALIDACION,
    PROP_VERTICES,
    RESULT,
    ROL_RESULTADO,
    VALIDACION_PENDIENTE,
)
from .util.Utilidades import Configuracion, Registro


class GeneradorObjeto:
    """Escribe el cascarón en la escena y, si se pide, lo reconstruye con voxel."""

    @staticmethod
    def _EspesorMinimo(cfg: dict) -> float:
        # El voxel no puede ser más fino que un tercio de este espesor.
        if cfg["pattern"] == "SOLID":
            return cfg["solid_mm"]
        if cfg["liner"]:
            return cfg["skin_mm"]
        return min(cfg["rib_height_mm"], cfg["rib_width_mm"])

    @staticmethod
    def _Componentes(bm):
        # Agrupa vértices unidos por aristas. El grupo mayor es la pieza que se conserva.
        vistos = set()
        grupos = []
        for vertice in bm.verts:
            if vertice in vistos:
                continue
            vistos.add(vertice)
            pendientes = [vertice]
            grupo = []
            while pendientes:
                actual = pendientes.pop()
                grupo.append(actual)
                for arista in actual.link_edges:
                    vecino = arista.other_vert(actual)
                    if vecino not in vistos:
                        vistos.add(vecino)
                        pendientes.append(vecino)
            grupos.append(grupo)
        grupos.sort(key=len, reverse=True)
        return grupos

    @staticmethod
    def _AplicarModificador(objeto, modificador):
        try:
            bpy.ops.object.modifier_apply(modifier=modificador.name)
        except RuntimeError as exc:
            raise ReconstruccionFallida(str(exc)) from exc

    @staticmethod
    def Crear(source, **options):
        # Genera o sustituye OL_Ortesis a partir de la superficie interior.
        logger = Registro.Obtener("objeto")
        autoescalar = bool(options.pop("autoescalar", True))
        opciones = Model3DForPrinting.ValidarOpciones(options)
        paso = opciones["surface_step_mm"]
        if opciones["pattern"] != "SOLID":
            paso = min(paso, opciones["rib_width_mm"] / 3, opciones["cell_mm"] / 6)
        puntos, caras, normales, borde = SuperficieInterior.Leer(
            source,
            paso_mm=paso,
            autoescalar=autoescalar,
        )
        modelo = Model3DForPrinting()
        vertices, faces, cfg, interiores, caras_interiores = modelo.Construir(
            puntos, caras, normales, borde, **opciones
        )
        minimo = GeneradorObjeto._EspesorMinimo(cfg)
        voxel = min(cfg["resolution_mm"], minimo / 3.0)
        if cfg["repair"] and voxel < Configuracion.ValorLimite("min_voxel_repair_mm"):
            raise ResolucionDemasiadoFina(Configuracion.ValorLimite("min_voxel_repair_mm") * 3)

        malla = bpy.data.meshes.new(MALLA_GEOMETRIA)
        try:
            malla.from_pydata(vertices, [], faces)
            malla.update()
        except (ValueError, RuntimeError) as exc:
            bpy.data.meshes.remove(malla)
            raise MallaNoConstruida(str(exc)) from exc

        objeto = bpy.data.objects.get(RESULT)
        if objeto is not None:
            anterior = objeto.data
            objeto.data = malla
            if anterior.users == 0:
                bpy.data.meshes.remove(anterior)
            logger.info("Objeto %s actualizado.", RESULT)
        else:
            objeto = bpy.data.objects.new(RESULT, malla)
            bpy.context.scene.collection.objects.link(objeto)
            logger.info("Objeto %s creado.", RESULT)

        objeto.matrix_world = source.matrix_world.copy()
        for poligono in malla.polygons:
            poligono.use_smooth = True
        objeto[PROP_CONFIG] = json.dumps(cfg, ensure_ascii=False)
        objeto[PROP_ROL] = ROL_RESULTADO
        objeto[PROP_VERTICES] = interiores
        objeto[PROP_CARAS] = caras_interiores
        objeto[PROP_VALIDACION] = VALIDACION_PENDIENTE
        objeto[PROP_ALCANCE] = ALCANCE
        objeto["ol_source_object"] = source.name
        objeto["ol_surface_step_mm"] = paso
        source.hide_set(True)
        source.hide_render = True
        objeto.hide_set(False)
        objeto.hide_render = False
        bpy.ops.object.select_all(action="DESELECT")
        objeto.select_set(True)
        bpy.context.view_layer.objects.active = objeto

        # Si un intento anterior dejó el modificador sin aplicar, se retira antes de crear otro.
        for nombre in (MOD_RECONSTRUCCION, MOD_SUAVIZADO):
            pendiente = objeto.modifiers.get(nombre)
            if pendiente is not None:
                objeto.modifiers.remove(pendiente)
                logger.warning("Se retiró un modificador que había quedado sin aplicar: %s", nombre)

        if not cfg["repair"]:
            logger.info("Pared engrosada; las aberturas de la superficie se conservan sin voxel.")
            return objeto

        remesh = objeto.modifiers.new(MOD_RECONSTRUCCION, "REMESH")
        remesh.mode = "VOXEL"
        remesh.voxel_size = voxel
        remesh.adaptivity = 0.0
        remesh.use_smooth_shade = True
        logger.info("Reconstrucción voxel a %.3f mm.", voxel)
        try:
            GeneradorObjeto._AplicarModificador(objeto, remesh)
        except ReconstruccionFallida:
            if objeto.modifiers.get(MOD_RECONSTRUCCION) is not None:
                objeto.modifiers.remove(remesh)
            raise

        bm = bmesh.new()
        try:
            bm.from_mesh(objeto.data)
            grupos = GeneradorObjeto._Componentes(bm)
            eliminados = sum(len(grupo) for grupo in grupos[1:])
            umbral = max(
                Configuracion.ValorLimite("fragment_vertex_floor"),
                len(bm.verts) * Configuracion.ValorLimite("fragment_vertex_ratio"),
            )
            if eliminados > umbral:
                raise GeometriaFragmentada(eliminados, umbral)
            if eliminados:
                bmesh.ops.delete(
                    bm,
                    geom=[vertice for grupo in grupos[1:] for vertice in grupo],
                    context="VERTS",
                )
                logger.info("Fragmentos residuales eliminados: %s vértices.", eliminados)
            bm.to_mesh(objeto.data)
        finally:
            bm.free()

        objeto[PROP_FRAGMENTOS] = eliminados
        suavizado = objeto.modifiers.new(MOD_SUAVIZADO, "SMOOTH")
        suavizado.factor = Configuracion.ValorLimite("smooth_factor")
        suavizado.iterations = int(Configuracion.ValorLimite("smooth_iterations"))
        try:
            GeneradorObjeto._AplicarModificador(objeto, suavizado)
        except ReconstruccionFallida:
            if objeto.modifiers.get(MOD_SUAVIZADO) is not None:
                objeto.modifiers.remove(suavizado)
            raise
        objeto[PROP_RESOLUCION] = voxel
        objeto[PROP_VERTICES] = 0
        objeto[PROP_CARAS] = 0
        logger.info("Reconstrucción y suavizado aplicados sobre %s.", objeto.name)
        return objeto
