"""Comprueba el paquete distribuido en aislamiento, sin assets ni Reflex."""
import sys
import logging
import os
import runpy
from contextlib import nullcontext
from pathlib import Path
from zipfile import ZipFile

import bpy

ROOT = Path(__file__).resolve().parents[1]
test_root = (ROOT/'dist').resolve()
test_root.mkdir(exist_ok=True)
paquete = Path(os.environ.get('ORTESISLAB_ZIP', ROOT/'GenerateModelsApp.zip')).resolve()
with nullcontext(str(test_root/'zip_verificado')) as tmp:
    assert Path(tmp).resolve().is_relative_to(test_root)
    Path(tmp).mkdir(exist_ok=True)
    with ZipFile(paquete) as archive:
        assert archive.testzip() is None
        assert not any(name.endswith('.npz') for name in archive.namelist())
        assert not any(name.endswith(('.pyc', '.pyo')) or '__pycache__' in name
                       for name in archive.namelist())
        archive.extractall(tmp)
    sys.path.insert(0, tmp)
    import GenerateModelsApp
    assert Path(GenerateModelsApp.__file__).is_relative_to(Path(tmp))
    assert GenerateModelsApp.bl_info['version'] == runpy.run_path(
        str(ROOT/'GenerateModelsApp'/'__init__.py')
    )['bl_info']['version']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    GenerateModelsApp.register()
    settings = bpy.context.scene.ortesislab
    assert settings.source is None and not settings.repair
    bpy.ops.mesh.primitive_plane_add(size=30)
    base = bpy.context.object
    settings.pattern = 'SQUARE'
    assert bpy.ops.ortesislab.use_surface() == {'FINISHED'}
    assert bpy.ops.ortesislab.generate() == {'FINISHED'}
    assert len(base.data.vertices) == 4
    assert len(bpy.data.objects['OL_Ortesis'].data.vertices) > 8
    assert bpy.ops.ortesislab.validate() == {'FINISHED'}
    from GenerateModelsApp.Exportacion import ExportadorStl
    ExportadorStl.Exportar(bpy.data.objects['OL_Ortesis'], str(Path(tmp)/'pared.stl'))
    assert (Path(tmp)/'pared.stl').stat().st_size > 84
    GenerateModelsApp.unregister()
    sys.path.remove(tmp)
    logging.shutdown()  # Libera el archivo de log antes de limpiar la carpeta en Windows.
print('PASS_ZIP: paquete aislado, panel, plano de cuatro vértices, patrón y exportación.', flush=True)
