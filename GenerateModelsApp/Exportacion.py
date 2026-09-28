"""Exporta el STL en milímetros y un JSON con parámetros y comprobación."""

from __future__ import annotations

import json
from pathlib import Path

from .ApiBlender import bpy
from .Excepciones import ExportacionFallida, MallaNoValida, ModeloNoGenerado
from .ValidacionMalla import ValidadorMalla
from .constants.Nombres import PROP_CONFIG, UNIDADES_STL
from .util.Utilidades import Registro


class ExportadorStl:
    """Escribe el STL solo si la malla pasó la comprobación."""

    @staticmethod
    def Exportar(ob, path):
        # El JSON hermano guarda los parámetros y el informe, en milímetros.
        logger = Registro.Obtener("exportacion")
        if ob is None:
            raise ModeloNoGenerado()
        if PROP_CONFIG not in ob:
            raise ExportacionFallida(
                str(path),
                "El objeto no tiene la configuración ol_config. Genere el modelo de nuevo.",
            )
        informe = ValidadorMalla.Comprobar(ob)
        if not informe["ok"]:
            raise MallaNoValida(json.dumps(informe))

        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        destino = str(path)
        logger.info("Exportando STL en milímetros: %s", destino)
        try:
            bpy.ops.wm.stl_export(
                filepath=destino,
                export_selected_objects=True,
                apply_modifiers=True,
                ascii_format=False,
                global_scale=1.0,
                use_scene_unit=False,
            )
        except RuntimeError as exc:
            raise ExportacionFallida(destino, str(exc)) from exc

        sidecar = Path(destino + ".json")
        contenido = {
            "parameters": json.loads(ob[PROP_CONFIG]),
            "validation": informe,
            "stl_units": UNIDADES_STL,
        }
        try:
            sidecar.write_text(json.dumps(contenido, indent=2), encoding="utf-8")
        except (OSError, TypeError, json.JSONDecodeError) as exc:
            raise ExportacionFallida(str(sidecar), str(exc)) from exc
        logger.info("Parámetros guardados en %s", sidecar)
        return informe
