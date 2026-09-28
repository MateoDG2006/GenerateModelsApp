"""Regresiones del espesor: pared cerrada, canal superior abierto."""
import unittest
from collections import Counter

import numpy as np

from GenerateModelsApp.Cascaron import Cascaron
from GenerateModelsApp.Malla import AnalizadorMalla
from GenerateModelsApp.Modeling import Model3DForPrinting
from GenerateModelsApp.Excepciones import SuperficieInvalida, VerticesSueltos


class SuperficieAbierta(unittest.TestCase):
    def setUp(self):
        self.p = np.array([[-10., 0., 5.], [0., 0., 0.], [10., 0., 5.],
                           [-10., 30., 5.], [0., 30., 0.], [10., 30., 5.]])
        self.f = np.array([[0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4]])
        self.n = np.tile([0., 0., 1.], (6, 1))

    def test_engrosado_solo_une_cada_borde_con_su_copia(self):
        p, f, n, _ = AnalizadorMalla.Preparar(self.p, self.f, self.n, suavizarNormales=False)
        vertices, faces = Cascaron.Engrosar(p, f, n, 2.)
        np.testing.assert_array_equal(vertices[:len(p)], p)
        np.testing.assert_array_equal(np.asarray(faces[:len(f)]), f)
        edges = Counter(tuple(sorted(e)) for face in f for e in zip(face, np.roll(face, -1)))
        boundary = {e for e, count in edges.items() if count == 1}
        walls = faces[len(f)*2:]
        self.assertEqual(len(walls), len(boundary))
        for wall in walls:
            self.assertIn(tuple(sorted({v % len(p) for v in wall})), boundary)
        all_edges = Counter(tuple(sorted(e)) for face in faces for e in zip(face, face[1:]+face[:1]))
        self.assertTrue(all(count == 2 for count in all_edges.values()))

    def test_invertir_lado_conserva_base_y_orientacion_del_volumen(self):
        args = AnalizadorMalla.Preparar(self.p, self.f, self.n, suavizarNormales=False)
        a = Model3DForPrinting.ConstruirGeometria(*args, pattern='SOLID', solid_mm=2.)
        b = Model3DForPrinting.ConstruirGeometria(*args, pattern='SOLID', solid_mm=2., flip_normals=True)
        np.testing.assert_allclose(a[0][6:], self.p + self.n*2)
        np.testing.assert_allclose(b[0][6:], self.p - self.n*2)
        np.testing.assert_array_equal(b[1][:len(self.f)], self.f[:, ::-1])
        self.assertAlmostEqual(Cascaron.VolumenMm3(a[0], a[1]), Cascaron.VolumenMm3(b[0], b[1]))

    def test_capas_separadas_y_caras_duplicadas_se_rechazan(self):
        with self.assertRaises(SuperficieInvalida):
            AnalizadorMalla.Preparar(np.vstack([self.p, self.p+[0, 0, -2]]),
                                     np.vstack([self.f, self.f+6]), np.vstack([self.n, self.n]),
                                     suavizarNormales=False)
        with self.assertRaises(SuperficieInvalida):
            AnalizadorMalla.Preparar(self.p, np.vstack([self.f, self.f[0]]), self.n, suavizarNormales=False)

    def test_sueltos_se_rechazan_incluso_con_normales_guardadas(self):
        with self.assertRaises(VerticesSueltos):
            AnalizadorMalla.Preparar(np.vstack([self.p, [1, 1, 1]]), self.f,
                                     np.vstack([self.n, [0, 0, 1]]), suavizarNormales=False)

    def test_normal_no_finita_y_orientacion_inconsistente(self):
        normals = self.n.copy(); normals[0, 0] = np.nan
        with self.assertRaises(SuperficieInvalida):
            AnalizadorMalla.Preparar(self.p, self.f, normals, suavizarNormales=False)
        faces = self.f.copy(); faces[0] = faces[0, ::-1]
        with self.assertRaises(SuperficieInvalida):
            AnalizadorMalla.Preparar(self.p, faces, self.n, suavizarNormales=False)


if __name__ == '__main__':
    unittest.main()
