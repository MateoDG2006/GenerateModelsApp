"""Ejecutar con Blender --background --factory-startup --python-exit-code 1 --python este_archivo.

La probeta es una bandeja con un canal lateral que representa el dedo. No es un
modelo anatómico. Las pruebas comprueban que ambas bocas permanezcan abiertas.
"""
import json
import sys
from pathlib import Path

import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import GenerateModelsApp as addon
from GenerateModelsApp.Objeto import GeneradorObjeto
from GenerateModelsApp.Superficie import SuperficieInterior
from GenerateModelsApp.ValidacionMalla import ValidadorMalla
from GenerateModelsApp.OrtesisLab import Complemento
from GenerateModelsApp.Excepciones import SolidoCerrado, SuperficieInvalida

bpy.ops.wm.read_factory_settings(use_empty=True)
addon.register()
assert hasattr(bpy.context.scene.ortesislab, 'source'), 'Las propiedades RNA deben registrarse, no ser anotaciones diferidas.'
assert bpy.context.scene.ortesislab.auto_scale
assert not bpy.context.scene.ortesislab.repair
assert bpy.context.scene.ortesislab.source is None
# Sin selección no debe cargarse el NPZ antiguo.
try:
    bpy.ops.ortesislab.generate()
except RuntimeError:
    pass
assert len(bpy.data.objects) == 0

points = []; faces = []; index = {}
def vertex(x, y):
    key = (x, y)
    if key not in index:
        z = .02*x*x if x >= -20 else 8 + .05*(y-40)**2*min(1, (-x-20)/20)
        index[key] = len(points); points.append((x, y, z))
    return index[key]
for y in range(0, 80, 2):
    for x in range(-40, 20, 2):
        if x >= -20 or 30 <= y < 50:
            faces.append(tuple(vertex(a, b) for a, b in [(x,y),(x+2,y),(x+2,y+2),(x,y+2)]))
mesh = bpy.data.meshes.new('Una_capa'); mesh.from_pydata(points, [], faces); mesh.update()
base = bpy.data.objects.new('Base_abierta_mano_y_dedo', mesh); bpy.context.scene.collection.objects.link(base)
bpy.context.view_layer.objects.active = base; base.select_set(True)
assert bpy.ops.ortesislab.use_surface() == {'FINISHED'}
original = np.array([v.co[:] for v in mesh.vertices])
original_faces = [tuple(f.vertices) for f in mesh.polygons]

# El botón de arreglo conserva una sola capa y retira defectos seguros.
dirty_points = [
    (0, 0, 0), (10, 0, 0), (20, 0, 0),
    (0, 10, 0), (10, 10, 0), (20, 10, 0),
    (0, 0, 0), (99, 99, 99),
    (30, 0, 0), (31, 0, 0), (30, 1, 0),
]
dirty_faces = [
    (6, 1, 4, 3), (1, 2, 5, 4),
    (0, 1, 4, 3), (8, 9, 10),
]
dirty_mesh = bpy.data.meshes.new('Base_con_defectos')
dirty_mesh.from_pydata(dirty_points, [], dirty_faces)
dirty_mesh.update()
dirty = bpy.data.objects.new('Base_con_defectos', dirty_mesh)
bpy.context.scene.collection.objects.link(dirty)
bpy.ops.object.select_all(action='DESELECT')
dirty.select_set(True)
bpy.context.view_layer.objects.active = dirty
dirty.scale = (2, 1, 1)
assert bpy.ops.ortesislab.repair_surface() == {'FINISHED'}
assert tuple(dirty.scale) == (1, 1, 1)
assert len(dirty.data.vertices) == 6
assert len(dirty.data.polygons) == 4
SuperficieInterior.Leer(dirty)
assert bpy.context.scene.ortesislab.source == dirty

bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
bpy.context.view_layer.objects.active = base

def comprobar_bocas(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); tree = BVHTree.FromBMesh(bm)
    # El fondo puede engrosarse hasta 3 mm: buscar techos por encima de él.
    for x, y, floor in [(0, 12, 0), (0, 40, 0), (0, 68, 0), (-28, 40, 8), (-36, 40, 8)]:
        hit = tree.ray_cast(Vector((x, y, 40)), Vector((0, 0, -1)), 40-floor-4)
        assert hit[0] is None, (x, y, tuple(hit[0]))
    bm.free()

records = []
for pattern in ('SOLID', 'SQUARE', 'DIAMOND', 'HEX', 'VORONOI'):
    for liner in ([True] if pattern == 'SOLID' else [True, False]):
        ob = GeneradorObjeto.Crear(base, pattern=pattern, liner=liner, rib_height_mm=2.0)
        report = ValidadorMalla.Comprobar(ob)
        assert report['ok'], (pattern, liner, report)
        comprobar_bocas(ob)
        np.testing.assert_array_equal(np.array([v.co[:] for v in mesh.vertices]), original)
        assert [tuple(f.vertices) for f in mesh.polygons] == original_faces
        records.append({'pattern': pattern, 'liner': liner, 'validation': report})

# El botón y BuildGeometry deben usar la misma preparación de la base.
s = bpy.context.scene.ortesislab; s.pattern = 'HEX'; s.source = base
assert bpy.ops.ortesislab.generate() == {'FINISHED'}
expected = Complemento.BuildGeometry(base, pattern='HEX')
ob = bpy.data.objects['OL_Ortesis']; assert len(ob.data.vertices) == len(expected[0])
comprobar_bocas(ob)
# Verificar también la reconstrucción opcional en esta probeta de aberturas amplias.
ob = GeneradorObjeto.Crear(base, pattern='VORONOI', repair=True)
assert ValidadorMalla.Comprobar(ob)['ok']; comprobar_bocas(ob)

# Una base cerrada no reemplaza el resultado válido ni se interpreta como una sola capa.
old_mesh = ob.data
bpy.ops.mesh.primitive_cube_add(size=10)
cube = bpy.context.object
cube_vertices = len(cube.data.vertices)
cube_faces = len(cube.data.polygons)
try:
    assert bpy.ops.ortesislab.repair_surface() == {'CANCELLED'}
except RuntimeError as exc:
    # Blender 5.2 propaga como RuntimeError el mensaje del operador cancelado.
    assert 'sólido cerrado' in str(exc).lower()
assert len(cube.data.vertices) == cube_vertices
assert len(cube.data.polygons) == cube_faces
try:
    GeneradorObjeto.Crear(cube)
    raise AssertionError('Aceptó un sólido cerrado')
except SolidoCerrado:
    pass
assert ob.data == old_mesh

# Releer siempre las caras editadas, aunque sus coordenadas y sus sumas no cambien.
before = SuperficieInterior.Leer(base)[1].copy()
bm = bmesh.new(); bm.from_mesh(mesh)
bmesh.ops.reverse_faces(bm, faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
after = SuperficieInterior.Leer(base)[1]
assert not np.array_equal(before, after)
assert np.mean(SuperficieInterior.Leer(base)[2][:,2]) < 0

# Generar corrige las unidades en una copia y deja la base como está.
tiny_mesh = bpy.data.meshes.new('Unidades_cm')
tiny_mesh.from_pydata([(0, 0, 0), (1.6, 0, 0), (1.6, 1, 0), (0, 1, 0)], [], [(0, 1, 2, 3)])
tiny_mesh.update()
tiny = bpy.data.objects.new('Unidades_cm', tiny_mesh)
bpy.context.scene.collection.objects.link(tiny)
bpy.ops.object.select_all(action='DESELECT')
tiny.select_set(True)
bpy.context.view_layer.objects.active = tiny
ajustes = bpy.context.scene.ortesislab
ajustes.auto_scale = True
ajustes.pattern = 'SOLID'
ajustes.surface_step_mm = 5
ajustes.source = tiny
assert bpy.ops.ortesislab.generate() == {'FINISHED'}
resultado = np.array([v.co[:] for v in bpy.data.objects['OL_Ortesis'].data.vertices])
assert np.ptp(resultado, axis=0).max() > 100
assert np.ptp(np.array([v.co[:] for v in tiny.data.vertices]), axis=0).max() < 2
ajustes.auto_scale = False
assert bpy.ops.ortesislab.generate() == {'FINISHED'}
resultado = np.array([v.co[:] for v in bpy.data.objects['OL_Ortesis'].data.vertices])
assert np.ptp(resultado, axis=0).max() < 10

# Una arista de millones de unidades no cabe en el paso: el autoescalado la corrige.
larga_malla = bpy.data.meshes.new('Unidades_demasiado_grandes')
larga_malla.from_pydata(
    [(0, 0, 0), (2_000_000, 0, 0), (0, 2_000_000, 0)],
    [],
    [(0, 1, 2)],
)
larga_malla.update()
larga = bpy.data.objects.new('Unidades_demasiado_grandes', larga_malla)
bpy.context.scene.collection.objects.link(larga)
ajustes.auto_scale = True
ajustes.pattern = 'SOLID'
ajustes.surface_step_mm = 1
ajustes.source = larga
assert bpy.ops.ortesislab.generate() == {'FINISHED'}
resultado = np.array([v.co[:] for v in bpy.data.objects['OL_Ortesis'].data.vertices])
assert 20 <= float(np.ptp(resultado, axis=0).max()) <= 1000
assert float(np.ptp(np.array([v.co[:] for v in larga_malla.vertices]), axis=0).max()) > 1_000_000

addon.unregister(); addon.register(); addon.unregister()
(ROOT/'tests'/'resultado_blender.json').write_text(json.dumps({'blender': bpy.app.version_string,
    'upper_and_finger_openings': True, 'base_unchanged': True, 'patterns': records}, indent=2), encoding='utf-8')
print('PASS_BLENDER: nueve variantes, dos canales abiertos, edición de base, panel, reconstrucción y rechazo de sólidos.', flush=True)
