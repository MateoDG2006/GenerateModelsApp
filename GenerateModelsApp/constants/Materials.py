"""Materiales de impresión.

``price`` se interpreta como precio por gramo. La unidad monetaria no está
definida en estos datos: el número se conserva tal como está declarado.
La densidad está en g/cm³. Un volumen en mm³ pasa a gramos dividiendo por 1000.
"""

from __future__ import annotations

import math

from ..Excepciones import MaterialInvalido
from ..util.Utilidades import Registro


class Material:
    # Densidad en g/cm³. price es el precio por gramo; la moneda no está declarada.

    def __init__(self, name, density, price, color, kind, brand):
        if not isinstance(name, str) or not name.strip():
            raise MaterialInvalido("El material necesita un nombre.")
        if isinstance(density, bool) or not isinstance(density, (int, float)) or not density > 0:
            raise MaterialInvalido(
                f"La densidad de {name} debe ser un número positivo.",
                detalle=str(density),
            )
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            raise MaterialInvalido(
                f"El precio de {name} no puede ser negativo.",
                detalle=str(price),
            )
        if not math.isfinite(density) or not math.isfinite(price):
            raise MaterialInvalido(f"Densidad y precio de {name} deben ser finitos.")
        self.name = name
        self.density = float(density)
        self.price = float(price)
        self.color = color
        self.type = kind
        self.brand = brand
        Registro.Obtener("materiales").debug(
            "Material %s: densidad %.3f g/cm³, precio por gramo %.4f",
            self.name,
            self.density,
            self.price,
        )

    def Gramos(self, volumenMm3: float) -> float:
        # mm³ * g/cm³ / 1000 = gramos, porque 1 cm³ son 1000 mm³.
        if isinstance(volumenMm3, bool) or not isinstance(volumenMm3, (int, float)):
            raise MaterialInvalido("El volumen debe ser numérico.")
        if not math.isfinite(volumenMm3) or volumenMm3 < 0:
            raise MaterialInvalido("El volumen debe ser un número finito y no negativo.")
        peso = float(volumenMm3) * self.density / 1000.0
        Registro.Obtener("materiales").debug("Peso de %s: %.4f g para %.3f mm³", self.name, peso, volumenMm3)
        return peso

    def Costo(self, volumenMm3: float) -> float:
        # Precio = gramos * precio por gramo.
        return self.Gramos(volumenMm3) * self.price


class PETG(Material):
    def __init__(self):
        super().__init__(
            name="PETG",
            density=1.27,
            price=0.15,
            color="black",
            kind="filament",
            brand="Prusament",
        )
