"""API de Blender, separada del núcleo geométrico.

Importar este módulo fuera de Blender registra el error y detiene la carga.
El resto del paquete (patrones, materiales, malla y modelo) no lo necesita.
"""

from __future__ import annotations

from .Excepciones import EntornoBlenderRequerido

try:
    import bmesh
    import bpy
    from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
    )
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import intersect_ray_tri
except ImportError as exc:
    raise EntornoBlenderRequerido(
        "Este módulo solo puede ejecutarse dentro de Blender.",
        detalle=str(exc),
    ) from exc

__all__ = [
    "BVHTree",
    "BoolProperty",
    "EnumProperty",
    "FloatProperty",
    "IntProperty",
    "PointerProperty",
    "StringProperty",
    "bmesh",
    "bpy",
    "intersect_ray_tri",
]
