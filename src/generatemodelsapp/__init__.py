def main() -> None:
    # pyproject.toml exige este nombre. El script está en scripts/IniciarConsola.py.
    from pathlib import Path
    import sys

    raiz = Path(__file__).resolve().parents[2]
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))
    from scripts.IniciarConsola import IniciarConsola

    IniciarConsola.Ejecutar()
