"""Errores de OrtesisLab.

Cada situación prevista tiene su clase. Al construirse, el mensaje
se escribe en el registro y después puede mostrarse en el panel.
"""

from __future__ import annotations


class OrtesisLabError(Exception):
    """Base de los errores previstos del generador."""

    def __init__(self, message: str, *, detalle: str | None = None):
        super().__init__(message)
        # Cada error previsto queda en el log en el momento de crearse.
        try:
            from .util.Utilidades import Registro

            texto = f"{type(self).__name__}: {message}"
            if detalle:
                texto = f"{texto} | {detalle}"
            Registro.Obtener("errores").error("%s", texto)
        except Exception:
            pass


class ConfiguracionInvalida(OrtesisLabError):
    """Un archivo de ``config`` falta, no es JSON o no tiene las claves exigidas."""


class EntornoBlenderRequerido(OrtesisLabError):
    """El módulo usa la API de Blender y se importó fuera de Blender."""


class ArchivoSuperficieNoEncontrado(OrtesisLabError):
    def __init__(self, *, detalle: str | None = None):
        super().__init__(
            "Abra OrtesisLab.blend o coloque superficie_interior_mm.npz junto al script.",
            detalle=detalle,
        )


class ArchivoSuperficieIlegible(OrtesisLabError):
    def __init__(self, ruta: str, motivo: str):
        super().__init__(
            f"No se pudo leer la superficie en '{ruta}'.",
            detalle=motivo,
        )


class SuperficieNoEsMalla(OrtesisLabError):
    def __init__(self):
        super().__init__("Seleccione una malla de una sola capa de caras, sin espesor y abierta por arriba.")


class SuperficieInvalida(OrtesisLabError):
    """La base no es una superficie conectada y orientada de una sola capa."""


class ModificadoresSinAplicar(OrtesisLabError):
    def __init__(self, nombre: str):
        super().__init__(
            "La superficie base debe tener sus modificadores aplicados.",
            detalle=nombre,
        )


class EscalaSinAplicar(OrtesisLabError):
    def __init__(self, escala: tuple):
        super().__init__(
            "Aplique la escala a la superficie base antes de usarla.",
            detalle=str(escala),
        )


class SuperficieSinCaras(OrtesisLabError):
    def __init__(self):
        super().__init__("La superficie no contiene caras.")


class SolidoCerrado(OrtesisLabError):
    def __init__(self):
        super().__init__(
            "La base es un sólido cerrado. Use una sola capa de caras sin espesor, "
            "con la parte superior y la zona del dedo abiertas."
        )


class AristasNoManifold(OrtesisLabError):
    def __init__(self):
        super().__init__("La superficie base contiene aristas no manifold.")


class VerticesSueltos(OrtesisLabError):
    def __init__(self):
        super().__init__("La superficie contiene vértices sueltos.")


class NormalesInvalidas(OrtesisLabError):
    def __init__(self, *, detalle: str | None = None):
        super().__init__("Normales de la superficie inválidas.", detalle=detalle)


class ParametrosNoReconocidos(OrtesisLabError):
    def __init__(self, nombres: set[str]):
        texto = ", ".join(sorted(nombres))
        super().__init__(f"Parámetros no reconocidos: {texto}")


class ParametroNoPositivo(OrtesisLabError):
    def __init__(self, clave: str):
        super().__init__(f"{clave} debe ser positivo.")


class PatronNoReconocido(OrtesisLabError):
    def __init__(self):
        super().__init__("Patrón no reconocido.")


class PatronNoImplementado(OrtesisLabError):
    def __init__(self, nombre: str):
        super().__init__(
            f"El patrón {nombre} no tiene una geometría definida.",
            detalle="Disponibles: VORONOI, HEX, DIAMOND, SQUARE, SOLID",
        )


class CeldaDemasiadoPequena(OrtesisLabError):
    def __init__(self, minimo_mm: float):
        super().__init__(
            f"Use celdas de al menos {minimo_mm:g} mm con esta superficie base."
        )


class NervaduraDemasiadoAncha(OrtesisLabError):
    def __init__(self, porcentaje: int):
        super().__init__(
            f"El ancho de nervadura debe ser menor que {porcentaje}% de la celda."
        )


class ParametroNoFinito(OrtesisLabError):
    def __init__(self, clave: str):
        super().__init__(f"{clave} debe ser finito.")


class ResolucionNoPositiva(OrtesisLabError):
    def __init__(self):
        super().__init__("La resolución debe ser positiva.")


class SemillaInvalida(OrtesisLabError):
    def __init__(self):
        super().__init__("La semilla debe ser un entero no negativo.")


class BordeNegativo(OrtesisLabError):
    def __init__(self, *, detalle: str | None = None):
        super().__init__(
            "Los parámetros de borde no pueden ser negativos.",
            detalle=detalle,
        )


class SuperficieEliminadaPorPatron(OrtesisLabError):
    def __init__(self):
        super().__init__("El patrón eliminó toda la superficie; aumente el ancho.")


class ResolucionDemasiadoFina(OrtesisLabError):
    def __init__(self, espesor_minimo_mm: float):
        super().__init__(
            "Resolución demasiado fina. Aumente el espesor mínimo a "
            f"{espesor_minimo_mm:.2f} mm o desactive la reconstrucción."
        )


class GeometriaFragmentada(OrtesisLabError):
    def __init__(self, eliminados: int, limite: float):
        super().__init__(
            "La geometría se separó en varias piezas; aumente el ancho/espesor "
            "o reduzca el tamaño de celda.",
            detalle=f"vértices en fragmentos={eliminados}, límite={limite:g}",
        )


class GeometriaInconsistente(OrtesisLabError):
    """Los arreglos internos no coinciden entre sí. Indica un fallo del generador."""


class MallaNoConstruida(OrtesisLabError):
    def __init__(self, motivo: str):
        super().__init__(f"No se pudo construir la malla: {motivo}")


class ReconstruccionFallida(OrtesisLabError):
    def __init__(self, motivo: str):
        super().__init__(
            f"No se pudo reconstruir la malla: {motivo}",
            detalle=motivo,
        )


class ModeloNoGenerado(OrtesisLabError):
    def __init__(self):
        super().__init__("Genere un modelo primero.")


class MallaNoValida(OrtesisLabError):
    def __init__(self, informe: str):
        super().__init__(
            f"Geometría no válida: {informe}. Reduzca altura o cambie ancho/celda."
        )


class ExportacionFallida(OrtesisLabError):
    def __init__(self, ruta: str, motivo: str):
        super().__init__(
            f"No se pudo exportar '{ruta}'.",
            detalle=motivo,
        )


class ModeloSinGeometria(OrtesisLabError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class MaterialInvalido(OrtesisLabError):
    """Densidad, precio o volumen incompatibles con el cálculo de material."""
