# Configuración exacta del núcleo

> Generado por `python docs/Agents/Scripts/GenerarIndices.py` desde los JSON del paquete. Para significado y efectos consultar [PARAMETROS.md](PARAMETROS.md).

## [comprobacion_geometrica.json](../../GenerateModelsApp/config/comprobacion_geometrica.json)

```json
{
  "blender": "5.2.2 LTS",
  "example_continuous_liner": {
    "open_edges": 0,
    "nonmanifold_edges": 0,
    "degenerate_faces": 0,
    "triangles": 2923508,
    "components": 1,
    "triangle_crossings": 0,
    "ok": true
  },
  "example_open_lattice": {
    "open_edges": 0,
    "nonmanifold_edges": 0,
    "degenerate_faces": 0,
    "triangles": 1766064,
    "components": 1,
    "triangle_crossings": 0,
    "ok": true
  },
  "units": "mm",
  "scope": "Geometry only",
  "flat_fixture_tests": "5 patterns; 4 open patterns; width, height, liner thickness, seed, UI operator and STL round trip."
}
```

## [limites.json](../../GenerateModelsApp/config/limites.json)

```json
{
  "min_cell_mm": 5,
  "max_rib_width_ratio": 0.75,
  "min_voxel_repair_mm": 0.15,
  "fragment_vertex_floor": 50,
  "fragment_vertex_ratio": 0.005,
  "normal_smooth_iterations": 20,
  "min_normal_length": 0.5,
  "scale_tolerance": 1e-06,
  "degenerate_area": 1e-08,
  "pattern_batch": 384,
  "voronoi_jitter": 0.28,
  "seed_separation_epsilon": 1e-10,
  "smooth_factor": 0.3,
  "smooth_iterations": 2,
  "min_rounding_width_mm": 0.02,
  "normal_epsilon": 1e-12,
  "max_surface_vertices": 500000,
  "max_refined_cache_entries": 2,
  "surface_subdivision_iterations": 16,
  "clip_snap_mm": 0.0001,
  "clip_connect_mm": 0.005,
  "border_smooth_wavelength_mm": 8.0,
  "border_smooth_max_mm": 3.0,
  "min_plausible_surface_extent_mm": 20,
  "max_plausible_surface_extent_mm": 1000
}
```

## [parametros_defecto.json](../../GenerateModelsApp/config/parametros_defecto.json)

```json
{
  "pattern": "VORONOI",
  "cell_mm": 15.0,
  "rib_width_mm": 2.8,
  "rib_height_mm": 1.4,
  "liner": true,
  "skin_mm": 1.0,
  "solid_mm": 2.4,
  "border_mm": 4.0,
  "rounding_mm": 0.8,
  "angle_deg": 0.0,
  "seed": 7,
  "reinforce_y_mm": 0.0,
  "reinforce_width_mm": 0.0,
  "repair": false,
  "flip_normals": false,
  "surface_step_mm": 1.0,
  "resolution_mm": 0.3
}
```

## [registro.json](../../GenerateModelsApp/config/registro.json)

```json
{
  "nivel_consola": "INFO",
  "nivel_archivo": "DEBUG",
  "archivo": "ortesislab.log"
}
```
