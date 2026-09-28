"""Patrones de nervadura.

La distancia se mide en la proyección XY, en milímetros, hasta el eje
de la nervadura. HoneyComb y Square conservan su nombre de catálogo;
su código geométrico es HEX y SQUARE.
Triangle y Minimalistic siguen en el catálogo y todavía no generan malla.
"""

from __future__ import annotations

import math

import numpy as np

from ..Excepciones import PatronNoImplementado, PatronNoReconocido
from ..util.Utilidades import Configuracion

_IMAGEN = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"


class Patron:
    """Catálogo y, cuando existe, distancia al eje de la nervadura."""

    codigo = ""

    def __init__(self):
        self.name = ""
        self.description = ""
        self.image = _IMAGEN

    def Distancia(self, puntos, celdaMm: float, anguloGrados: float, semilla: int):
        # Las subclases que generan malla reemplazan este método.
        raise PatronNoImplementado(self.name or type(self).__name__)

    @staticmethod
    def RotarXy(puntos, anguloGrados: float):
        # Gira la proyección XY. El macizo no la usa.
        angulo = math.radians(anguloGrados)
        coseno, seno = math.cos(angulo), math.sin(angulo)
        return puntos[:, :2] @ np.array([[coseno, -seno], [seno, coseno]])

    @staticmethod
    def DistanciaCuadricula(uv, celda: float):
        # Distancia al eje más cercano de una retícula cuadrada.
        return np.min(np.abs((uv + celda * 0.5) % celda - celda * 0.5), axis=1)

    @staticmethod
    def DistanciaSemillas(uv, celda: float, semilla: int, organico: bool):
        # Retícula hexagonal. Si organico es verdadero, cada semilla se desplaza.
        bajo = uv.min(0) - 3 * celda
        alto = uv.max(0) + 3 * celda
        paso_y = celda * math.sqrt(3) / 2
        generador = np.random.default_rng(semilla)
        jitter = Configuracion.ValorLimite("voronoi_jitter")
        epsilon = Configuracion.ValorLimite("seed_separation_epsilon")
        lote = int(Configuracion.ValorLimite("pattern_batch"))
        semillas = []
        for fila, y in enumerate(np.arange(bajo[1], alto[1] + paso_y, paso_y)):
            for x in np.arange(bajo[0], alto[0] + celda, celda):
                punto = np.array([x + (fila % 2) * celda * 0.5, y])
                if organico:
                    punto = punto + generador.uniform(-jitter, jitter, 2) * celda
                semillas.append(punto)
        semillas = np.array(semillas)
        resultado = np.empty(len(uv))
        for inicio in range(0, len(uv), lote):
            puntos = uv[inicio : inicio + lote]
            distancias2 = np.sum((puntos[:, None, :] - semillas[None, :, :]) ** 2, axis=2)
            cercano = np.argmin(distancias2, axis=1)
            centro = semillas[cercano]
            separacion = np.linalg.norm(semillas[None, :, :] - centro[:, None, :], axis=2)
            denominador = np.where(separacion > epsilon, 2 * separacion, 1)
            plano = (distancias2 - distancias2[np.arange(len(puntos)), cercano, None]) / denominador
            plano[np.arange(len(puntos)), cercano] = np.inf
            resultado[inicio : inicio + len(puntos)] = np.min(plano, axis=1)
        return resultado

    @staticmethod
    def Geometricos() -> dict[str, Patron]:
        # Solo los patrones que sí construyen malla.
        return {
            "VORONOI": Voronoi(),
            "HEX": HoneyComb(),
            "DIAMOND": Diamond(),
            "SQUARE": Square(),
            "SOLID": Solid(),
        }

    @staticmethod
    def Obtener(codigoONombre: str) -> Patron:
        # Acepta el código (HEX) o el nombre de catálogo (HoneyComb, macizo).
        if not isinstance(codigoONombre, str) or not codigoONombre.strip():
            raise PatronNoReconocido()
        clave = codigoONombre.strip().upper()
        if clave in {"TRIANGLE", "MINIMALISTIC"}:
            raise PatronNoImplementado(codigoONombre.strip())
        clave = _ALIAS.get(clave, clave)
        tabla = Patron.Geometricos()
        if clave not in tabla:
            raise PatronNoReconocido()
        return tabla[clave]


class HoneyComb(Patron):
    # Hexágonos regulares. En la geometría el código es HEX.
    codigo = "HEX"

    def __init__(self):
        super().__init__()
        self.name = "HoneyComb"
        self.description = "A honeycomb pattern"
        self.image = _IMAGEN

    def Distancia(self, puntos, celdaMm: float, anguloGrados: float, semilla: int):
        return Patron.DistanciaSemillas(Patron.RotarXy(puntos, anguloGrados), celdaMm, semilla, False)


class Square(Patron):
    codigo = "SQUARE"

    def __init__(self):
        super().__init__()
        self.name = "Square"
        self.description = "A square pattern"
        self.image = _IMAGEN

    def Distancia(self, puntos, celdaMm: float, anguloGrados: float, semilla: int):
        return Patron.DistanciaCuadricula(Patron.RotarXy(puntos, anguloGrados), celdaMm)


class Triangle(Patron):
    # Sigue en el catálogo. Pedirla para generar es un error.
    def __init__(self):
        super().__init__()
        self.name = "Triangle"
        self.description = "A triangle pattern"
        self.image = _IMAGEN


class Minimalistic(Patron):
    # Sigue en el catálogo. Pedirla para generar es un error.
    def __init__(self):
        super().__init__()
        self.name = "Minimalistic"
        self.description = "A minimalistic pattern"
        self.image = _IMAGEN


class Diamond(Patron):
    codigo = "DIAMOND"

    def __init__(self):
        super().__init__()
        self.name = "Diamond"
        self.description = "Rombos"
        self.image = _IMAGEN

    def Distancia(self, puntos, celdaMm: float, anguloGrados: float, semilla: int):
        # La cuadrícula se gira 45° para que las celdas queden en rombo.
        uv = Patron.RotarXy(puntos, anguloGrados)
        diagonal = math.sqrt(0.5)
        uv = uv @ np.array([[diagonal, -diagonal], [diagonal, diagonal]])
        return Patron.DistanciaCuadricula(uv, celdaMm)


class Voronoi(Patron):
    codigo = "VORONOI"

    def __init__(self):
        super().__init__()
        self.name = "Voronoi"
        self.description = "Orgánico / Voronoi"
        self.image = _IMAGEN

    def Distancia(self, puntos, celdaMm: float, anguloGrados: float, semilla: int):
        return Patron.DistanciaSemillas(Patron.RotarXy(puntos, anguloGrados), celdaMm, semilla, True)


class Solid(Patron):
    codigo = "SOLID"

    def __init__(self):
        super().__init__()
        self.name = "Solid"
        self.description = "Macizo"
        self.image = _IMAGEN

    def Distancia(self, puntos, celdaMm: float, anguloGrados: float, semilla: int):
        # El macizo no tiene huecos: la distancia al eje es cero en todos los puntos.
        return np.zeros(len(puntos))


CATALOGO = (HoneyComb, Square, Triangle, Minimalistic, Diamond, Voronoi, Solid)

_ALIAS = {
    "HONEYCOMB": "HEX",
    "ROMBOS": "DIAMOND",
    "CUADRICULA": "SQUARE",
    "CUADRÍCULA": "SQUARE",
    "MACIZO": "SOLID",
    "ORGANICO": "VORONOI",
    "ORGÁNICO": "VORONOI",
    "VORONOI": "VORONOI",
    "HEX": "HEX",
    "DIAMOND": "DIAMOND",
    "SQUARE": "SQUARE",
    "SOLID": "SOLID",
}
