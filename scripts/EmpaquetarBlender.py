"""Genera el ZIP instalable de Blender, sin Reflex, logs ni la base v5."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil

ROOT = Path(__file__).resolve().parents[1]


def empaquetar():
    paquete = ROOT / 'GenerateModelsApp'
    destino = ROOT / 'GenerateModelsApp.zip'
    temporal = ROOT / 'GenerateModelsApp.nuevo.zip'
    archivos = sorted(p for p in paquete.rglob('*') if p.is_file()
                      and p.suffix in {'.py', '.json'}
                      and not any(part in {'__pycache__', 'logs'} for part in p.relative_to(paquete).parts))
    with ZipFile(temporal, 'w', ZIP_DEFLATED) as zipfile:
        for archivo in archivos:
            zipfile.write(archivo, 'GenerateModelsApp/' + archivo.relative_to(paquete).as_posix())
        zipfile.write(ROOT / 'docs' / 'LEEME.md', 'GenerateModelsApp/LEEME.md')
    with ZipFile(temporal) as zipfile:
        assert zipfile.testzip() is None
        assert 'GenerateModelsApp/__init__.py' in zipfile.namelist()
    anterior = ROOT / 'dist' / 'GenerateModelsApp-anterior.zip'
    if destino.exists() and not anterior.exists():
        anterior.parent.mkdir(exist_ok=True)
        shutil.copy2(destino, anterior)
    temporal.replace(destino)
    print(f'ZIP de Blender actualizado: {destino}')


if __name__ == '__main__':
    empaquetar()
