"""Repositorios SQLAlchemy, uno por archivo. Reciben una ``Session`` ya abierta y no hacen commit.

Toda consulta de un recurso filtra por ``user_id``. Las únicas operaciones que
recorren varios usuarios son las de la cola del trabajador. Las sentencias se
construyen sobre las tablas de ``Modelos`` (alias en ``Consultas``).
"""

from .RepositorioAssets import RepositorioAssets
from .RepositorioBase import RepositorioBase
from .RepositorioHistorial import RepositorioHistorial
from .RepositorioImports import RepositorioImports
from .RepositorioLotes import RepositorioLotes
from .RepositorioPreferencias import RepositorioPreferencias
from .RepositorioProyectos import NOMBRE_PROYECTO_PREDETERMINADO, RepositorioProyectos
from .RepositorioResultados import RepositorioResultados
from .RepositorioUsuarios import RepositorioUsuarios
from .RepositorioVersiones import RepositorioVersiones

__all__ = [
    "NOMBRE_PROYECTO_PREDETERMINADO",
    "RepositorioAssets",
    "RepositorioBase",
    "RepositorioHistorial",
    "RepositorioImports",
    "RepositorioLotes",
    "RepositorioPreferencias",
    "RepositorioProyectos",
    "RepositorioResultados",
    "RepositorioUsuarios",
    "RepositorioVersiones",
]
