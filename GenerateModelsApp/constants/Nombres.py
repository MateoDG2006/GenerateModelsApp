"""Nombres estables de objetos, atributos y archivos.

No hay funciones: son textos que Blender y el STL deben encontrar siempre iguales.
"""

SOURCE = "OL_SuperficieInterior"
RESULT = "OL_Ortesis"
ROL_SUPERFICIE = "contact_surface_mm"
ROL_RESULTADO = "generated_geometry_mm"
ATTR_NORMAL = "ol_offset_normal"
ARCHIVO_SUPERFICIE = "superficie_interior_mm.npz"
MALLA_GEOMETRIA = "OL_Geometria"

PROP_CONFIG = "ol_config"
PROP_ROL = "ol_role"
PROP_VERTICES = "ol_inner_vertices"
PROP_CARAS = "ol_inner_faces"
PROP_VALIDACION = "ol_validation"
PROP_ALCANCE = "ol_scope"
PROP_FRAGMENTOS = "ol_removed_tiny_fragments"
PROP_RESOLUCION = "ol_reconstruction_resolution_mm"

ALCANCE = "Geometría; sin predicción de resistencia ni fabricación."
VALIDACION_PENDIENTE = "Pendiente"
UNIDADES_STL = "mm"

MOD_RECONSTRUCCION = "Reconstruccion geometrica"
MOD_SUAVIZADO = "Suavizado final"
ARCHIVO_STL_DEFECTO = "//Ortesis_configurada.stl"
