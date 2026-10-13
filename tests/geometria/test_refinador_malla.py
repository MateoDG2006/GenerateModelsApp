"""Refinamiento de patrones web sin depender de Blender."""

import unittest

import numpy as np

from GenerateModelsApp.EscalaMalla import EscalaMalla
from GenerateModelsApp.Modeling import Model3DForPrinting
from GenerateModelsApp.RefinadorMalla import RefinadorMalla
from GenerateModelsApp.util.Utilidades import Configuracion


class RefinamientoWeb(unittest.TestCase):
    def setUp(self):
        self.vertices = np.array(
            [[0.0, 0.0, 0.0], [40.0, 0.0, 0.0], [40.0, 40.0, 0.0], [0.0, 40.0, 0.0]]
        )
        self.caras = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
        self.normales = np.tile([0.0, 0.0, 1.0], (4, 1))

    def test_refina_aristas_y_conserva_superficie_abierta(self):
        puntos, caras, normales, borde = RefinadorMalla.Refinar(
            self.vertices,
            self.caras,
            self.normales,
            5.0,
        )
        aristas = np.unique(
            np.sort(
                np.vstack(
                    [caras[:, [0, 1]], caras[:, [1, 2]], caras[:, [2, 0]]]
                ),
                axis=1,
            ),
            axis=0,
        )
        longitudes = np.linalg.norm(
            puntos[aristas[:, 0]] - puntos[aristas[:, 1]],
            axis=1,
        )
        self.assertGreater(len(puntos), len(self.vertices))
        self.assertLessEqual(float(np.max(longitudes)), 5.005)
        self.assertTrue(np.isfinite(borde).all())
        np.testing.assert_allclose(normales[:, 2], 1.0)

    def test_el_patron_abierto_recorta_la_superficie_refinada(self):
        puntos, caras, normales, borde = RefinadorMalla.Refinar(
            self.vertices,
            self.caras,
            self.normales,
            2.0,
        )
        opciones = Configuracion.ParametrosDefecto()
        opciones.update(
            pattern="SQUARE",
            cell_mm=10.0,
            rib_width_mm=2.0,
            rib_height_mm=1.0,
            liner=False,
            border_mm=0.0,
        )
        _vertices, _caras, _cfg, interiores, caras_interiores = (
            Model3DForPrinting.ConstruirGeometria(
                puntos,
                caras,
                normales,
                borde,
                **opciones,
            )
        )
        self.assertGreater(interiores, 0)
        self.assertLess(caras_interiores, len(caras))

    def test_autoescala_una_arista_que_no_alcanza_el_paso(self):
        lado = 2_000_000.0
        vertices = np.array([[0.0, 0.0, 0.0], [lado, 0.0, 0.0], [0.0, 1.0, 0.0]])
        caras = np.array([[0, 1, 2]], dtype=np.int32)
        normales = np.tile([0.0, 0.0, 1.0], (3, 1))

        def refinar(factor):
            return RefinadorMalla.Refinar(vertices * factor, caras, normales, 1.0)

        _resultado, diagnostico = EscalaMalla.Aplicar(
            lado,
            True,
            refinar,
            arista_maxima=lado,
            paso_mm=1.0,
        )
        self.assertEqual(diagnostico["factor"], 0.0001)
        self.assertAlmostEqual(diagnostico["dimension_despues_mm"], 200)


if __name__ == "__main__":
    unittest.main()
