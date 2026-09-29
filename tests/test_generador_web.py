"""Comprueba el lote y el STL sin abrir Blender ni la superficie real."""

import struct
import unittest
import io
from pathlib import Path

import numpy as np

from web.GeneradorWeb import MAXIMO_VARIANTES, GeneradorWeb
from web.LectorSuperficie import LectorSuperficie
from GenerateModelsApp.Excepciones import ArchivoSuperficieIlegible, GeometriaInconsistente


def base():
    return {
        "pattern": "VORONOI",
        "cell_mm": 15.0,
        "rib_width_mm": 2.8,
        "rib_height_mm": 1.4,
        "liner": True,
        "skin_mm": 1.0,
        "solid_mm": 2.4,
        "border_mm": 4.0,
        "rounding_mm": 0.8,
        "angle_deg": 0.0,
        "seed": 7,
        "reinforce_y_mm": 0.0,
        "reinforce_width_mm": 0.0,
        "flip_normals": False,
        "repair": False,
        "resolution_mm": 0.3,
        "surface_step_mm": 1.0,
    }


class LoteYStl(unittest.TestCase):
    def test_un_patron_sin_barrido_es_una_variante(self):
        variantes = GeneradorWeb.Combinaciones(base(), ["HEX"], "ninguno", 0, 0, 1, False)
        self.assertEqual(len(variantes), 1)
        self.assertEqual(variantes[0]["pattern"], "HEX")
        self.assertTrue(variantes[0]["liner"])

    def test_patrones_por_celda_y_capa(self):
        variantes = GeneradorWeb.Combinaciones(
            base(), ["VORONOI", "SOLID"], "cell_mm", 10, 20, 10, True
        )
        # Voronoi se duplica con y sin capa. El macizo no.
        self.assertEqual(len(variantes), 6)
        self.assertEqual(variantes[0]["cell_mm"], 10)
        self.assertEqual(variantes[1]["cell_mm"], 10)
        self.assertFalse(variantes[1]["liner"])
        self.assertEqual(variantes[-1]["pattern"], "SOLID")
        self.assertTrue(variantes[-1]["liner"])

    def test_rechaza_un_lote_demasiado_grande(self):
        with self.assertRaises(ValueError):
            GeneradorWeb.Combinaciones(
                base(), ["HEX", "SQUARE"], "cell_mm", 5, 40, 1, True
            )
        self.assertGreater(
            len(["HEX", "SQUARE"]) * 36 * 2,
            MAXIMO_VARIANTES,
        )

    def test_la_semilla_del_barrido_es_entera(self):
        variantes = GeneradorWeb.Combinaciones(base(), ["VORONOI"], "seed", 1, 3, 1, False)
        self.assertEqual([item["seed"] for item in variantes], [1, 2, 3])

    def test_el_barrido_respeta_el_extremo_y_el_limite_antes_de_crear_variantes(self):
        variantes = GeneradorWeb.Combinaciones(base(), ["HEX"], "cell_mm", 0, 1, 0.6, False)
        self.assertEqual([item["cell_mm"] for item in variantes], [0, 0.6])
        with self.assertRaises(ValueError):
            GeneradorWeb.Combinaciones(base(), ["HEX"], "cell_mm", 0, 1, 1e-12, False)

    def test_el_barrido_rechaza_no_finitos_y_semillas_fraccionarias(self):
        for desde, hasta, paso, eje in (
            (float("-inf"), 20, 5, "cell_mm"),
            (1, float("nan"), 1, "cell_mm"),
            (1, 3, 0.4, "seed"),
        ):
            with self.subTest(desde=desde, hasta=hasta, paso=paso, eje=eje):
                with self.assertRaises(ValueError):
                    GeneradorWeb.Combinaciones(base(), ["VORONOI"], eje, desde, hasta, paso, False)

    def test_stl_de_un_triangulo(self):
        vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
        caras = [[0, 1, 2]]
        datos = GeneradorWeb.Stl(vertices, caras)
        self.assertEqual(len(datos), 84 + 50)
        self.assertEqual(struct.unpack_from("<I", datos, 80)[0], 1)
        normal = np.array(struct.unpack_from("<3f", datos, 84))
        self.assertAlmostEqual(abs(normal[2]), 1, places=5)
        muro = GeneradorWeb.Stl(vertices + [[0, 0, 1]], [[0, 1, 2, 3]])
        self.assertEqual(struct.unpack_from("<I", muro, 80)[0], 2)

    def test_carga_una_superficie_stl_abierta(self):
        vertices = [[0, 0, 0], [100, 0, 0], [100, 100, 0], [0, 100, 0]]
        caras = [[0, 1, 2], [0, 2, 3]]
        resultado, info = LectorSuperficie.Preparar(
            "superficie.stl",
            GeneradorWeb.Stl(vertices, caras),
        )
        self.assertEqual(len(resultado[0]), 4)
        self.assertEqual(len(resultado[1]), 2)
        self.assertEqual(info["factor_escala"], 1)
        self.assertEqual(info["nombre"], "superficie.stl")

    def test_autoescala_una_superficie_pequena(self):
        vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        caras = [[0, 1, 2], [0, 2, 3]]
        resultado, info = LectorSuperficie.Preparar(
            "superficie.stl",
            GeneradorWeb.Stl(vertices, caras),
            autoescalar=True,
        )
        self.assertEqual(info["factor_escala"], 100)
        self.assertAlmostEqual(float(np.ptp(resultado[0], axis=0).max()), 100)

    def test_la_preferencia_se_aplica_al_generar_y_se_puede_quitar(self):
        vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        caras = [[0, 1, 2], [0, 2, 3]]
        archivo, info = GeneradorWeb.GuardarSuperficie(
            "pieza.stl",
            GeneradorWeb.Stl(vertices, caras),
            autoescalar=True,
        )
        self.addCleanup(GeneradorWeb.RutaSuperficie(archivo).unlink, missing_ok=True)
        self.assertEqual(info["factor_escala"], 100)
        self.assertAlmostEqual(float(np.ptp(GeneradorWeb.Cruda(archivo)[0], axis=0).max()), 1)
        escalada = GeneradorWeb.Superficie(archivo, autoescalar=True)
        self.assertAlmostEqual(float(np.ptp(escalada[0], axis=0).max()), 100)
        original = GeneradorWeb.Superficie(archivo, autoescalar=False)
        self.assertAlmostEqual(float(np.ptp(original[0], axis=0).max()), 1)
        self.assertIn("Autoescalado desactivado", GeneradorWeb.diagnostico_escala["advertencia"])
        GeneradorWeb.SuperficieRefinada(archivo, 50, autoescalar=True)
        GeneradorWeb.SuperficieRefinada(archivo, 50, autoescalar=False)
        GeneradorWeb.SuperficieRefinada(archivo, 50, autoescalar=True)
        self.assertEqual(GeneradorWeb.diagnostico_escala["factor"], 100)

    def test_permite_desactivar_el_autoescalado_de_la_subida(self):
        vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        caras = [[0, 1, 2], [0, 2, 3]]
        resultado, info = LectorSuperficie.Preparar(
            "superficie.stl",
            GeneradorWeb.Stl(vertices, caras),
            autoescalar=False,
        )
        self.assertEqual(info["factor_escala"], 1)
        self.assertIn("Autoescalado desactivado", info["aviso"])
        self.assertAlmostEqual(float(np.ptp(resultado[0], axis=0).max()), 1.0)

    def test_carga_test_como_superficie_abierta(self):
        resultado, info = LectorSuperficie.Preparar(
            "Test.stl",
            Path(__file__).with_name("Test.stl").read_bytes(),
        )
        self.assertGreater(len(resultado[0]), 0)
        self.assertGreater(len(resultado[1]), 0)
        self.assertTrue(np.isfinite(resultado[3]).all())
        self.assertEqual(info["nombre"], "Test.stl")

    def test_npz_rechaza_indices_fraccionarios_y_expansion_excesiva(self):
        contenido = io.BytesIO()
        np.savez_compressed(
            contenido,
            vertices=np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]]),
            faces=np.array([[0., 1.9, 2.]]),
            normals=np.tile([0., 0., 1.], (3, 1)),
        )
        with self.assertRaises(GeometriaInconsistente):
            LectorSuperficie.Preparar("superficie.npz", contenido.getvalue())
        anterior = LectorSuperficie.MAXIMO_DESCOMPRIMIDO_BYTES
        self.addCleanup(setattr, LectorSuperficie, "MAXIMO_DESCOMPRIMIDO_BYTES", anterior)
        LectorSuperficie.MAXIMO_DESCOMPRIMIDO_BYTES = 100
        with self.assertRaises(ArchivoSuperficieIlegible):
            LectorSuperficie.Preparar("superficie.npz", contenido.getvalue())


if __name__ == "__main__":
    unittest.main()
