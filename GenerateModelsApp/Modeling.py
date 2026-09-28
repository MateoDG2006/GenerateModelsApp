"""Modelo de impresión y construcción de la geometría.

El identificador 3DModelForPrinting no es válido en Python.
Esta clase calcula el cascarón y, aparte, volumen, peso y precio.
Esos tres números son del cascarón anterior al voxel: no predicen
el filamento real ni la resistencia.
"""

from __future__ import annotations

import math

import numpy as np

from .Cascaron import Cascaron
from .Excepciones import (
    BordeNegativo,
    CeldaDemasiadoPequena,
    ModeloSinGeometria,
    NervaduraDemasiadoAncha,
    ParametroNoFinito,
    ParametroNoPositivo,
    ParametrosNoReconocidos,
    PatronNoImplementado,
    PatronNoReconocido,
    ResolucionNoPositiva,
    SemillaInvalida,
    GeometriaInconsistente,
)
from .constants.Materials import PETG
from .constants.Paterns import Patron
from .util.Utilidades import Configuracion, Registro

_POSITIVOS = ("cell_mm", "rib_width_mm", "rib_height_mm", "skin_mm", "solid_mm", "surface_step_mm")
_FINITOS = (
    "border_mm",
    "rounding_mm",
    "angle_deg",
    "reinforce_y_mm",
    "reinforce_width_mm",
    "resolution_mm",
)
_BORDES = ("border_mm", "rounding_mm", "reinforce_width_mm")


class Model3DForPrinting:
    """Pieza paramétrica: geometría, volumen, peso y precio de material."""

    def __init__(self, material=None):
        self.material = material or PETG()
        self.pattern: Patron = Patron.Obtener("VORONOI")
        self.opciones = Configuracion.ParametrosDefecto()
        self.vertices = None
        self.faces = None
        self.config = None
        self.vertices_interiores = 0
        self.caras_interiores = 0
        self._volumen_mm3 = None

    @staticmethod
    def ValidarOpciones(options: dict | None = None) -> dict:
        # Une lo recibido con el JSON y rechaza valores que romperían la malla.
        logger = Registro.Obtener("modelo")
        opciones = {} if options is None else options
        if not isinstance(opciones, dict):
            raise ParametrosNoReconocidos({"options"})
        plantilla = Configuracion.ParametrosDefecto()
        desconocidos = set(opciones) - set(plantilla)
        if desconocidos:
            raise ParametrosNoReconocidos(desconocidos)
        cfg = plantilla | dict(opciones)
        for clave in ("flip_normals", "repair", "liner"):
            if not isinstance(cfg[clave], bool):
                raise GeometriaInconsistente(f"{clave} debe ser verdadero o falso.")

        for clave in _POSITIVOS:
            numero = cfg[clave]
            if isinstance(numero, bool) or not isinstance(numero, (int, float)):
                raise ParametroNoPositivo(clave)
            if not math.isfinite(numero) or numero <= 0:
                raise ParametroNoPositivo(clave)

        if cfg["pattern"] not in Patron.Geometricos():
            raise PatronNoReconocido()

        minimo_celda = Configuracion.ValorLimite("min_cell_mm")
        if cfg["cell_mm"] < minimo_celda:
            raise CeldaDemasiadoPequena(minimo_celda)

        relacion = Configuracion.ValorLimite("max_rib_width_ratio")
        if cfg["pattern"] != "SOLID" and cfg["rib_width_mm"] >= cfg["cell_mm"] * relacion:
            raise NervaduraDemasiadoAncha(int(round(relacion * 100)))

        for clave in _FINITOS:
            numero = cfg[clave]
            if isinstance(numero, bool) or not isinstance(numero, (int, float)) or not math.isfinite(numero):
                raise ParametroNoFinito(clave)

        if cfg["resolution_mm"] <= 0:
            raise ResolucionNoPositiva()
        if isinstance(cfg["seed"], bool) or not isinstance(cfg["seed"], int) or cfg["seed"] < 0:
            raise SemillaInvalida()

        negativos = [clave for clave in _BORDES if cfg[clave] < 0]
        if negativos:
            raise BordeNegativo(detalle=", ".join(negativos))
        logger.debug("Parámetros aceptados: patrón %s, celda %s mm", cfg["pattern"], cfg["cell_mm"])
        return cfg

    @staticmethod
    def ConstruirGeometria(vertices, caras, normales, distanciaBorde, **options):
        # Arma el cascarón a partir de una superficie que ya fue analizada.
        logger = Registro.Obtener("modelo")
        cfg = Model3DForPrinting.ValidarOpciones(options)
        puntos = np.asarray(vertices, dtype=np.float64)
        faces = np.asarray(caras)
        normales_superficie = np.asarray(normales, dtype=np.float64)
        if cfg["flip_normals"]:
            normales_superficie = -normales_superficie
            faces = faces[:, ::-1]
        borde = np.asarray(distanciaBorde, dtype=np.float64)
        patron = Patron.Geometricos()[cfg["pattern"]]
        logger.info(
            "Construyendo geometría %s: celda %.2f mm, nervadura %.2f x %.2f mm, capa %s.",
            cfg["pattern"],
            cfg["cell_mm"],
            cfg["rib_width_mm"],
            cfg["rib_height_mm"],
            "continua" if cfg["liner"] else "abierta",
        )
        distancia = patron.Distancia(puntos, cfg["cell_mm"], cfg["angle_deg"], cfg["seed"])
        nervadura = cfg["rib_width_mm"] * 0.5 - distancia
        if cfg["border_mm"] > 0:
            nervadura = np.maximum(nervadura, cfg["border_mm"] - borde)
        if cfg["reinforce_width_mm"] > 0:
            nervadura = np.maximum(
                nervadura,
                cfg["reinforce_width_mm"] * 0.5 - np.abs(puntos[:, 1] - cfg["reinforce_y_mm"]),
            )
        if cfg["pattern"] == "SOLID":
            espesor = np.full(len(puntos), cfg["solid_mm"])
        elif cfg["liner"]:
            ancho = max(Configuracion.ValorLimite("min_rounding_width_mm"), cfg["rounding_mm"])
            perfil = Cascaron.Smooth01(nervadura / ancho + 0.5)
            espesor = cfg["skin_mm"] + cfg["rib_height_mm"] * perfil
        else:
            puntos, faces, normales_superficie = Cascaron.Recortar(
                puntos, faces, normales_superficie, nervadura
            )
            espesor = np.full(len(puntos), cfg["rib_height_mm"])
        vertices_finales, caras_finales = Cascaron.Engrosar(puntos, faces, normales_superficie, espesor)
        return vertices_finales, caras_finales, cfg, len(puntos), len(faces)

    def ChangePatern(self, patron):
        # Elige el patrón por código (HEX) o por nombre (HoneyComb).
        logger = Registro.Obtener("modelo")
        if isinstance(patron, Patron):
            if not patron.codigo:
                raise PatronNoImplementado(patron.name or type(patron).__name__)
            instancia = patron
            codigo = patron.codigo
        else:
            instancia = Patron.Obtener(patron)
            codigo = instancia.codigo
        self.pattern = instancia
        self.opciones["pattern"] = codigo
        self._volumen_mm3 = None
        logger.info("Patrón activo: %s (%s)", instancia.name, codigo)
        return instancia

    def ChangePattern(self, patron):
        # Mismo cambio de patrón, con el nombre en inglés.
        return self.ChangePatern(patron)

    def Construir(self, vertices, caras, normales, distanciaBorde, **options):
        # Guarda el cascarón en la instancia para poder cubicar después.
        opciones = dict(self.opciones)
        opciones.update(options)
        resultado = self.ConstruirGeometria(vertices, caras, normales, distanciaBorde, **opciones)
        (
            self.vertices,
            self.faces,
            self.config,
            self.vertices_interiores,
            self.caras_interiores,
        ) = resultado
        self.opciones = dict(self.config)
        self.ChangePatern(self.config["pattern"])
        self._volumen_mm3 = None
        return resultado

    def CalculateVolume(self) -> float:
        # Volumen del cascarón guardado, en mm³, antes de la reconstrucción voxel.
        logger = Registro.Obtener("modelo")
        if self._volumen_mm3 is not None:
            logger.debug("Volumen reutilizado: %.3f mm³", self._volumen_mm3)
            return self._volumen_mm3
        if self.vertices is None or self.faces is None:
            raise ModeloSinGeometria("No hay geometría para calcular el volumen.")
        volumen = Cascaron.VolumenMm3(self.vertices, self.faces)
        self._volumen_mm3 = volumen
        logger.info(
            "Volumen geométrico del cascarón, antes de la reconstrucción voxel: %.3f mm³. "
            "No es una predicción de fabricación.",
            volumen,
        )
        return volumen

    def CalculateWeight(self) -> float:
        # Peso en gramos a partir del volumen y de la densidad del material.
        if self.material is None:
            raise ModeloSinGeometria("Asigne un material antes de calcular el peso.")
        peso = self.material.Gramos(self.CalculateVolume())
        Registro.Obtener("modelo").info("Peso estimado: %.4f g con %s.", peso, self.material.name)
        return peso

    def CalculatePrice(self) -> float:
        # Precio estimado = peso en gramos * precio por gramo del material.
        if self.material is None:
            raise ModeloSinGeometria("Asigne un material antes de calcular el precio.")
        precio = self.CalculateWeight() * self.material.price
        Registro.Obtener("modelo").info(
            "Precio estimado: %.4f, a %.4f por gramo de %s. La unidad monetaria es la declarada en el material.",
            precio,
            self.material.price,
            self.material.name,
        )
        return precio
