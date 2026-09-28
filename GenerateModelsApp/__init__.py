"""Paquete del complemento de Blender y del núcleo de geometría.

La aplicación Reflex está en web/GenerateModelsApp.py y no forma parte
de este paquete. Reflex importa el núcleo sin cargar Blender.
``register`` y ``unregister`` solo se usan cuando Blender activa el complemento.
"""

bl_info = {
    "name": "OrtesisLab",
    "author": "Mateo Del Giudice | Codex",
    "version": (1, 3, 0),
    "blender": (5, 0, 0),
    "location": "Vista 3D > N > Ortesis",
    "description": "Ortesis abierta desde una superficie sin espesor",
    "category": "Object",
}


def register():
    from .OrtesisLab import register as registrar

    registrar()


def unregister():
    from .OrtesisLab import unregister as retirar

    retirar()
