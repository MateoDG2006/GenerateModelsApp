"""Suavizado del contorno exterior antes de dar espesor.

El borde de una superficie recortada sigue las aristas de la malla. Si ese
recorrido zigzaguea, cada arista se convierte en un muro y el canto queda
dentado. Aquí se quitan esas ondas cortas y se conserva la forma del contorno.
"""

from __future__ import annotations

import numpy as np

from .util.Utilidades import Configuracion, Registro


class SuavizadoBorde:
    """Aplana los dientes del contorno sin mover el interior de la superficie."""

    @staticmethod
    def Aplicar(vertices, caras, normales):
        """Entrada: superficie abierta ya validada. Proceso: filtra cada bucle
        del borde y sus normales. Salida: copias de vértices y normales, y el
        desplazamiento máximo en mm. Errores: ninguno; un bucle corto se deja
        igual. Efectos: registra el desplazamiento.
        """
        logger = Registro.Obtener("malla")
        puntos = np.array(vertices, dtype=np.float64, copy=True)
        normales_salida = np.array(normales, dtype=np.float64, copy=True)
        longitud = Configuracion.ValorLimite("border_smooth_wavelength_mm")
        if not np.isfinite(longitud) or longitud <= 0 or len(puntos) == 0:
            return puntos, normales_salida, 0.0

        caras_idx = np.asarray(caras, dtype=np.int32)
        bucles = SuavizadoBorde._Bucles(caras_idx)
        if not bucles:
            return puntos, normales_salida, 0.0

        originales = puntos.copy()
        delta = np.zeros_like(puntos)
        for bucle in bucles:
            coords = puntos[bucle]
            filtradas = SuavizadoBorde._Pasabajos(coords, longitud)
            if filtradas.shape != coords.shape or not np.isfinite(filtradas).all():
                continue
            delta[bucle] = filtradas - coords

        tope = Configuracion.ValorLimite("border_smooth_max_mm")
        if np.isfinite(tope) and tope > 0:
            distancia = np.linalg.norm(delta, axis=1)
            exceso = distancia > tope
            delta[exceso] *= (tope / distancia[exceso])[:, None]
        delta[np.linalg.norm(delta, axis=1) < 1e-6] = 0.0

        referencia = np.cross(
            puntos[caras_idx[:, 1]] - puntos[caras_idx[:, 0]],
            puntos[caras_idx[:, 2]] - puntos[caras_idx[:, 0]],
        )
        area_minima = Configuracion.ValorLimite("degenerate_area")
        for _ in range(12):
            if not SuavizadoBorde._CarasRotas(puntos + delta, caras_idx, referencia, area_minima):
                break
            culpables = np.unique(caras_idx[SuavizadoBorde._MascaraRota(
                puntos + delta, caras_idx, referencia, area_minima
            )])
            delta[culpables] *= 0.5
        else:
            rotas = SuavizadoBorde._MascaraRota(
                puntos + delta, caras_idx, referencia, area_minima
            )
            if np.any(rotas):
                delta[np.unique(caras_idx[rotas])] = 0.0
                logger.warning(
                    "Parte del contorno no se pudo suavizar sin voltear caras."
                )

        puntos += delta
        for bucle in bucles:
            normales_bucle = SuavizadoBorde._Pasabajos(normales_salida[bucle], longitud)
            if (
                normales_bucle.shape != normales_salida[bucle].shape
                or not np.isfinite(normales_bucle).all()
            ):
                continue
            largo = np.linalg.norm(normales_bucle, axis=1)
            validas = largo > Configuracion.ValorLimite("normal_epsilon")
            if not np.any(validas):
                continue
            propuestas = normales_salida[bucle].copy()
            propuestas[validas] = normales_bucle[validas] / largo[validas, None]
            acuerdo = np.einsum("ij,ij->i", propuestas, normales_salida[bucle])
            diferencia = np.linalg.norm(propuestas - normales_salida[bucle], axis=1)
            aceptar = validas & (acuerdo > 0) & (diferencia > 1e-6)
            normales_salida[bucle[aceptar]] = propuestas[aceptar]

        desplazamiento = float(np.linalg.norm(puntos - originales, axis=1).max())
        if desplazamiento > 0:
            logger.info(
                "Contorno suavizado: %s bucles, desplazamiento máximo %.3f mm.",
                len(bucles),
                desplazamiento,
            )
        return puntos, normales_salida, desplazamiento

    @staticmethod
    def _Bucles(caras: np.ndarray) -> list[np.ndarray]:
        # Cada arista libre se recorre una vez. Un diente necesita varios vértices.
        todas = np.vstack((caras[:, [0, 1]], caras[:, [1, 2]], caras[:, [2, 0]]))
        aristas, cuentas = np.unique(np.sort(todas, axis=1), axis=0, return_counts=True)
        contorno = aristas[cuentas == 1]
        if len(contorno) == 0:
            return []
        vecinos: dict[int, list[int]] = {}
        for origen, destino in contorno:
            vecinos.setdefault(int(origen), []).append(int(destino))
            vecinos.setdefault(int(destino), []).append(int(origen))
        vistos: set[int] = set()
        bucles = []
        for inicio in vecinos:
            if inicio in vistos:
                continue
            bucle = [inicio]
            vistos.add(inicio)
            anterior = -1
            actual = inicio
            while True:
                candidatos = [vecino for vecino in vecinos[actual] if vecino != anterior]
                if not candidatos:
                    break
                siguiente = candidatos[0]
                if siguiente == inicio or siguiente in vistos:
                    break
                bucle.append(siguiente)
                vistos.add(siguiente)
                anterior = actual
                actual = siguiente
            if len(bucle) >= 8:
                bucles.append(np.asarray(bucle, dtype=np.int32))
        return bucles

    @staticmethod
    def _Pasabajos(coords: np.ndarray, longitud_mm: float) -> np.ndarray:
        # Remuestrea el bucle cerrado y elimina las ondas más cortas que longitud_mm.
        cantidad = len(coords)
        segmentos = np.linalg.norm(np.roll(coords, -1, axis=0) - coords, axis=1)
        acumulada = np.concatenate((np.zeros(1), np.cumsum(segmentos)))
        for posicion in range(1, len(acumulada)):
            if acumulada[posicion] <= acumulada[posicion - 1]:
                acumulada[posicion] = acumulada[posicion - 1] + 1e-9
        perimetro = float(acumulada[-1])
        if perimetro <= 1e-8:
            return coords.copy()

        parametro = np.linspace(0.0, perimetro, cantidad, endpoint=False)
        extendida = np.vstack((coords, coords[:1]))
        uniforme = np.column_stack(
            [np.interp(parametro, acumulada, extendida[:, eje]) for eje in range(3)]
        )
        espectro = np.fft.rfft(uniforme, axis=0)
        frecuencias = np.fft.rfftfreq(cantidad, d=perimetro / cantidad)
        corte = 1.0 / longitud_mm
        inicio = 0.5 * corte
        transicion = np.clip((frecuencias - inicio) / (corte - inicio), 0.0, 1.0)
        ganancia = 1.0 - transicion * transicion * (3.0 - 2.0 * transicion)
        # Las dos primeras vueltas describen el óvalo del contorno, no un diente.
        ganancia[np.arange(len(espectro)) <= 2] = 1.0
        espectro *= ganancia[:, None]
        suave = np.fft.irfft(espectro, n=cantidad, axis=0)
        fraccion = acumulada[:-1] / perimetro
        suave_ext = np.vstack((suave, suave[:1]))
        eje_param = np.append(np.linspace(0.0, 1.0, cantidad, endpoint=False), 1.0)
        return np.column_stack(
            [np.interp(fraccion, eje_param, suave_ext[:, eje]) for eje in range(3)]
        )

    @staticmethod
    def _MascaraRota(propuesta, caras, referencia, area_minima) -> np.ndarray:
        cruz = np.cross(
            propuesta[caras[:, 1]] - propuesta[caras[:, 0]],
            propuesta[caras[:, 2]] - propuesta[caras[:, 0]],
        )
        return (np.einsum("ij,ij->i", cruz, referencia) <= 0) | (
            np.linalg.norm(cruz, axis=1) * 0.5 < area_minima
        )

    @staticmethod
    def _CarasRotas(propuesta, caras, referencia, area_minima) -> bool:
        return bool(np.any(SuavizadoBorde._MascaraRota(propuesta, caras, referencia, area_minima)))
