"""Valores ajustables del backend, leídos de ``config/<area>.yaml`` en la raíz.

Los secretos y las URL van en el entorno (``Ajustes``); aquí solo hay límites,
tiempos y tamaños. Un archivo o una clave ausente es un error de despliegue.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

CARPETA = Path(__file__).resolve().parent.parent / "config"


class ConfiguracionBackend:
    @staticmethod
    @lru_cache(maxsize=None)
    def Cargar(area: str) -> dict:
        with (CARPETA / f"{area}.yaml").open(encoding="utf-8") as archivo:
            return yaml.safe_load(archivo)
