"""Complemento OrtesisLab dentro del paquete.

El archivo que se ejecuta desde disco está en scripts/EjecutarOrtesisLab.py.
Aquí vive el registro que Blender pide al activar el complemento.
register y unregister conservan ese nombre porque Blender los busca así.
"""

from __future__ import annotations

from .ApiBlender import PointerProperty, bpy
from .Interfaz import CLASSES, OL_Settings
from .util.Utilidades import Registro


class Complemento:
    """Registra el panel y construye geometría sin escribirla todavía en escena."""

    @staticmethod
    def BuildGeometry(source, **options):
        # Vértices y caras del cascarón. No crea el objeto OL_Ortesis.
        from .Modeling import Model3DForPrinting
        from .RefinadorMalla import RefinadorMalla
        from .Superficie import SuperficieInterior

        autoescalar = bool(options.pop("autoescalar", True))
        cfg = Model3DForPrinting.ValidarOpciones(options)
        paso = RefinadorMalla.PasoPatron(cfg)
        puntos, caras, normales, borde = SuperficieInterior.Leer(
            source,
            paso_mm=paso,
            autoescalar=autoescalar,
        )
        return Model3DForPrinting().Construir(puntos, caras, normales, borde, **cfg)

    @staticmethod
    def Retirar():
        # Quita las clases del complemento para poder volver a registrarlas.
        logger = Registro.Obtener("addon")
        logger.info("Retirando clases de OrtesisLab.")
        if hasattr(bpy.types.Scene, "ortesislab"):
            del bpy.types.Scene.ortesislab
        registradas = bpy.app.driver_namespace.pop("_ortesislab_classes", CLASSES)
        for cls in reversed(registradas):
            if getattr(cls, "is_registered", False):
                try:
                    bpy.utils.unregister_class(cls)
                except RuntimeError:
                    logger.warning("No se pudo retirar la clase %s.", cls.__name__, exc_info=True)

    @staticmethod
    def Registrar():
        # La fuente la elige el usuario; no reactivar automáticamente la plantilla v5.
        logger = Registro.Obtener("addon")
        logger.info("Registrando OrtesisLab.")
        Complemento.Retirar()
        registradas = []
        try:
            for cls in CLASSES:
                bpy.utils.register_class(cls)
                registradas.append(cls)
            bpy.app.driver_namespace["_ortesislab_classes"] = CLASSES
            bpy.types.Scene.ortesislab = PointerProperty(type=OL_Settings)
        except Exception:
            logger.exception("Falló el registro de OrtesisLab.")
            for cls in reversed(registradas):
                if getattr(cls, "is_registered", False):
                    try:
                        bpy.utils.unregister_class(cls)
                    except RuntimeError:
                        logger.warning("No se pudo deshacer el registro de %s.", cls.__name__)
            raise


def register():
    # Blender llama a esta función por su nombre al activar el complemento.
    Complemento.Registrar()


def unregister():
    # Blender llama a esta función por su nombre al desactivar el complemento.
    Complemento.Retirar()
