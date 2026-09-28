"""Diagnóstico de unidades para una superficie de ortesis.

STL no guarda unidades. Esta clase solo corrige errores decimales inequívocos;
si ninguna potencia de diez deja la base en el rango configurado, devuelve una
advertencia para que la persona confirme las dimensiones.

Si la escala elegida no permite alcanzar el paso de superficie, se prueba la
siguiente potencia de diez, aunque el eje quede por debajo del rango.
"""

from __future__ import annotations

import math

from .Excepciones import SuperficieInvalida
from .util.Utilidades import Configuracion, Registro


class EscalaMalla:
    """Decide si el eje mayor parece expresado en una unidad distinta de mm."""

    EXPONENTE_MINIMO = -6
    EXPONENTE_MAXIMO = 6

    @staticmethod
    def Candidatos(dimensionMaximaMm: float) -> list[float]:
        # De la corrección más pequeña a la mayor. Incluye 1 cuando ya está en milímetros.
        minimo = Configuracion.ValorLimite("min_plausible_surface_extent_mm")
        maximo = Configuracion.ValorLimite("max_plausible_surface_extent_mm")
        dimension = float(dimensionMaximaMm)
        if not math.isfinite(dimension) or dimension <= 0:
            return []
        factores = []
        for exponente in range(EscalaMalla.EXPONENTE_MINIMO, EscalaMalla.EXPONENTE_MAXIMO + 1):
            factor = 10.0 ** exponente
            if minimo <= dimension * factor <= maximo:
                factores.append((exponente, factor))
        factores.sort(key=lambda item: (abs(item[0]), -item[0]))
        return [factor for _exponente, factor in factores]

    @staticmethod
    def Diagnosticar(dimensionMaximaMm: float) -> dict:
        minimo = Configuracion.ValorLimite("min_plausible_surface_extent_mm")
        maximo = Configuracion.ValorLimite("max_plausible_surface_extent_mm")
        dimension = float(dimensionMaximaMm)
        resultado = {
            "factor": 1.0,
            "dimension_antes_mm": dimension,
            "dimension_despues_mm": dimension,
            "advertencia": "",
        }
        if not math.isfinite(dimension) or dimension <= 0:
            resultado["advertencia"] = "No se pudo determinar una dimensión válida para revisar la escala."
            return resultado

        candidatos = EscalaMalla.Candidatos(dimension)
        if candidatos:
            factor = candidatos[0]
            resultado["factor"] = factor
            resultado["dimension_despues_mm"] = dimension * factor
            return resultado

        resultado["advertencia"] = (
            f"La malla mide {dimension:.2f} mm en su eje mayor, fuera del rango "
            f"esperado de {minimo:g} a {maximo:g} mm. Revise las unidades antes de generar."
        )
        return resultado

    @staticmethod
    def AlcanzaPaso(aristaMaxima: float, pasoMm: float, factor: float) -> bool:
        # 16 mitades tienen que dejar la arista más larga por debajo del paso.
        if not math.isfinite(aristaMaxima) or aristaMaxima <= 0:
            return True
        if not math.isfinite(pasoMm) or pasoMm <= 0:
            return True
        rondas = int(Configuracion.ValorLimite("surface_subdivision_iterations"))
        return aristaMaxima * factor <= pasoMm * 1.001 * (2 ** rondas)

    @staticmethod
    def Presupuesto(aristaMaxima: float, pasoMm: float, nCaras: int, factor: float) -> bool:
        # Cada pasada puede cuadruplicar los triángulos. Eso no debe arrancar.
        if not EscalaMalla.AlcanzaPaso(aristaMaxima, pasoMm, factor):
            return False
        if nCaras <= 0:
            return True
        limite = int(Configuracion.ValorLimite("max_surface_vertices"))
        if nCaras > limite:
            return False
        longitud = float(aristaMaxima) * float(factor)
        tope = float(pasoMm) * 1.001
        if longitud <= tope:
            return True
        niveles = math.ceil(math.log2(longitud / tope))
        if niveles >= 12:
            return False
        return nCaras <= limite / (4 ** niveles)

    @staticmethod
    def EsFalloDePaso(exc: BaseException) -> bool:
        # El paso no cupo: faltaron rondas o el detalle superó el límite de vértices.
        return isinstance(exc, SuperficieInvalida) and "paso de superficie" in str(exc)

    @staticmethod
    def Aplicar(
        dimensionMaximaMm: float,
        autoescalar: bool,
        operacion,
        *,
        arista_maxima: float | None = None,
        paso_mm: float | None = None,
        n_caras: int | None = None,
    ):
        # Prueba la corrección decimal y, si el paso no cabe, la siguiente más pequeña.
        dimension = float(dimensionMaximaMm)
        diagnostico = dict(EscalaMalla.Diagnosticar(dimension))
        candidatos = EscalaMalla.Candidatos(dimension)
        preferidos = candidatos
        if (
            arista_maxima is not None
            and paso_mm is not None
            and candidatos
        ):
            alcanzables = [
                factor
                for factor in candidatos
                if EscalaMalla.AlcanzaPaso(arista_maxima, float(paso_mm), factor)
            ]
            if alcanzables:
                preferidos = alcanzables
        if not preferidos:
            preferidos = [1.0]

        if autoescalar:
            preferido = preferidos[0]
            menores = sorted(
                (factor for factor in candidatos if factor < preferido),
                reverse=True,
            )
            intentos = [preferido, *menores]
            # Si ninguna escala del rango alcanza el paso, seguir bajando por décadas.
            siguiente = min(intentos) / 10.0
            while (
                siguiente + 1e-15 >= 10.0 ** EscalaMalla.EXPONENTE_MINIMO
                and len(intentos) < len(menores) + 4
            ):
                if not any(math.isclose(siguiente, factor, rel_tol=1e-6) for factor in intentos):
                    intentos.append(siguiente)
                siguiente /= 10.0
            diagnostico["factor"] = preferido
            diagnostico["factor_sugerido"] = preferido
            diagnostico["dimension_despues_mm"] = dimension * preferido
            if preferido != 1.0:
                diagnostico["advertencia"] = ""
            if n_caras and arista_maxima is not None and paso_mm is not None:
                seguros = [
                    factor
                    for factor in intentos
                    if EscalaMalla.Presupuesto(
                        arista_maxima, float(paso_mm), int(n_caras), factor
                    )
                ]
                # No se construye la malla intermedia que revienta la memoria.
                intentos = seguros or [min(intentos)]
        else:
            sugerido = preferidos[0] if candidatos else float(diagnostico["factor"])
            intentos = [1.0]
            diagnostico["factor"] = 1.0
            diagnostico["factor_sugerido"] = sugerido
            diagnostico["dimension_despues_mm"] = dimension
            if sugerido != 1.0:
                diagnostico["advertencia"] = (
                    "Autoescalado desactivado. "
                    f"La corrección sugerida es ×{sugerido:g}: "
                    f"{dimension:.2f} a {dimension * sugerido:.2f} mm."
                )

        logger = Registro.Obtener("escala")
        for indice, factor in enumerate(intentos):
            try:
                resultado = operacion(factor)
            except SuperficieInvalida as exc:
                if not EscalaMalla.EsFalloDePaso(exc) or indice == len(intentos) - 1:
                    raise
                logger.info(
                    "La escala x%g no alcanza el paso de superficie; se prueba x%g.",
                    factor,
                    intentos[indice + 1],
                )
                continue
            diagnostico["factor"] = float(factor)
            diagnostico["dimension_despues_mm"] = dimension * float(factor)
            if factor != 1.0:
                diagnostico["factor_sugerido"] = float(factor)
                diagnostico["advertencia"] = ""
            return resultado, diagnostico

    @staticmethod
    def Resolver(dimensionMaximaMm: float, autoescalar: bool = True) -> dict:
        """Devuelve el factor aplicado y conserva el factor sugerido para informar."""
        diagnostico = dict(EscalaMalla.Diagnosticar(dimensionMaximaMm))
        sugerido = float(diagnostico["factor"])
        diagnostico["factor_sugerido"] = sugerido
        if autoescalar:
            return diagnostico

        diagnostico["factor"] = 1.0
        diagnostico["dimension_despues_mm"] = diagnostico["dimension_antes_mm"]
        if sugerido != 1.0:
            diagnostico["advertencia"] = (
                "Autoescalado desactivado. "
                f"La corrección sugerida es ×{sugerido:g}: "
                f"{diagnostico['dimension_antes_mm']:.2f} a "
                f"{dimensionMaximaMm * sugerido:.2f} mm."
            )
        return diagnostico
