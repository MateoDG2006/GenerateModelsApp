"""Script para abrir el complemento dentro de Blender.

No es código de la aplicación: solo localiza el paquete y llama a register.
Ejecutar este archivo desde disco, o instalar la carpeta GenerateModelsApp
como complemento. Un bloque de texto aislado no trae el resto de módulos.

Ejemplo, con la raíz del repositorio como carpeta de trabajo:
    blender --python scripts/EjecutarOrtesisLab.py
"""

import sys
from pathlib import Path

# La raíz del repositorio es el padre de esta carpeta scripts/.
_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from GenerateModelsApp.OrtesisLab import register  # noqa: E402


if __name__ == "__main__":
    # Blender exige una función llamada register; el script solo la dispara.
    register()
