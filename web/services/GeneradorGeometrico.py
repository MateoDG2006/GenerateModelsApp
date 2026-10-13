"""Construcción numérica de una versión: métricas, STL y JSON de parámetros.

No escribe en el bucket ni formatea textos de la página. Requiere un usuario
activo en ``ContextoUsuario`` porque la superficie se lee de su asset.
"""

from __future__ import annotations

import struct
from decimal import Decimal

import numpy as np

from GenerateModelsApp.Modeling import Model3DForPrinting
from GenerateModelsApp.RefinadorMalla import RefinadorMalla
from GenerateModelsApp.constants.Materials import Material
from web.GeneradorWeb import GeneradorWeb
from web.enums import AlcanceGeometria, UnidadExport
from web.persistence.Contratos import ResultadoGeometrico

from .ServicioVersiones import ServicioVersiones

VERSION = "GeneradorGeometrico-1"


class GeneradorGeometrico:
    @staticmethod
    def MaterialDe(snapshot: dict) -> Material:
        return Material(
            name=snapshot["name"],
            density=float(snapshot["density_g_cm3"]),
            price=float(snapshot["price_per_gram"]),
            color=snapshot.get("color"),
            kind=snapshot.get("kind"),
            brand=snapshot.get("brand"),
        )

    @staticmethod
    def Construir(
        opciones: dict, superficie_archivo: str, autoescalar: bool, material: dict
    ) -> tuple[ResultadoGeometrico, bytes, bytes]:
        """Salida: resultado numérico, STL binario y JSON canónico de parámetros.
        Errores: OrtesisLabError si la geometría o los parámetros no son válidos."""
        if opciones["pattern"] == "SOLID":
            paso = None
            superficie, diagnostico = GeneradorWeb._SuperficieConDiagnostico(superficie_archivo, autoescalar)
        else:
            paso = RefinadorMalla.PasoPatron(opciones)
            superficie, diagnostico = GeneradorWeb._SuperficieRefinadaConDiagnostico(
                superficie_archivo, paso, autoescalar
            )
        puntos, caras, normales, borde = superficie
        modelo = Model3DForPrinting(GeneradorGeometrico.MaterialDe(material))
        vertices, faces, cfg, _interiores, _caras = modelo.Construir(puntos, caras, normales, borde, **opciones)
        volumen = float(modelo.CalculateVolume())
        peso = float(modelo.CalculateWeight())
        precio = float(modelo.CalculatePrice())
        stl = GeneradorWeb.Stl(vertices, faces)
        dimensiones = [float(valor) for valor in np.ptp(np.asarray(vertices), axis=0)] if len(vertices) else [0.0] * 3
        factor = float(diagnostico.get("factor", 1.0))
        avisos = [diagnostico["advertencia"]] if diagnostico.get("advertencia") else []
        escala = {clave: diagnostico[clave] for clave in sorted(diagnostico)}
        resultado = ResultadoGeometrico(
            volume_mm3=volumen,
            weight_g=peso,
            estimated_price=Decimal(repr(precio)),
            price_per_gram=Decimal(repr(float(material["price_per_gram"]))),
            density_g_cm3=Decimal(repr(float(material["density_g_cm3"]))),
            currency=material.get("currency"),
            vertices=len(vertices),
            triangles=struct.unpack_from("<I", stl, 80)[0],
            dimensions_mm=dimensiones,
            effective_scale=factor,
            effective_step_mm=paso,
            warnings=avisos,
            configuracion=dict(cfg),
            execution_parameters={"surface_step_mm": paso, "scale": escala, "generator": VERSION},
        )
        parametros = ServicioVersiones.Canonico(
            {
                "units": UnidadExport.MM,
                "geometry_scope": AlcanceGeometria.PRE_VOXEL_SHELL,
                "parameters": dict(cfg),
                "auto_scale": bool(autoescalar),
                "scale": escala,
                "material": material,
                "metrics": {"volume_mm3": volumen, "weight_g": peso, "estimated_price": precio},
            }
        ).encode("utf-8")
        return resultado, stl, parametros
