"""El contorno exterior pierde los dientes y conserva la forma general."""

import unittest

import numpy as np

from GenerateModelsApp.Malla import AnalizadorMalla
from GenerateModelsApp.Modeling import Model3DForPrinting
from GenerateModelsApp.SuavizadoBorde import SuavizadoBorde


class SuavizadoDeContorno(unittest.TestCase):
    def _AbanicoDentado(self):
        # Círculo de 30 mm con un diente de ±1,2 mm en cada vértice del borde.
        cantidad = 96
        angulo = np.linspace(0.0, 2.0 * np.pi, cantidad, endpoint=False)
        signo = np.where(np.arange(cantidad) % 2 == 0, 1.2, -1.2)
        radio = 30.0 + signo
        borde = np.column_stack(
            (radio * np.cos(angulo), radio * np.sin(angulo), np.zeros(cantidad))
        )
        puntos = np.vstack(([[0.0, 0.0, 0.0]], borde))
        caras = np.array(
            [[0, 1 + i, 1 + ((i + 1) % cantidad)] for i in range(cantidad)],
            dtype=np.int32,
        )
        normales = np.tile([0.0, 0.0, 1.0], (cantidad + 1, 1))
        normales[1::2, 0] = 0.6
        normales[2::2, 0] = -0.6
        normales /= np.linalg.norm(normales, axis=1)[:, None]
        return puntos, caras, normales

    def test_los_dientes_del_borde_desaparecen_y_el_centro_queda_quieto(self):
        puntos, caras, normales = self._AbanicoDentado()
        suavizados, normales_suaves, desplazamiento = SuavizadoBorde.Aplicar(
            puntos, caras, normales
        )
        np.testing.assert_allclose(suavizados[0], puntos[0])
        radios = np.linalg.norm(suavizados[1:, :2], axis=1)
        self.assertLess(float(np.max(np.abs(radios - 30.0))), 0.2)
        self.assertGreater(desplazamiento, 1.0)
        self.assertLess(float(np.max(np.abs(normales_suaves[1:, 0]))), 0.05)
        np.testing.assert_allclose(normales_suaves[0], normales[0])

        cruz_original = np.cross(
            puntos[caras[:, 1]] - puntos[caras[:, 0]],
            puntos[caras[:, 2]] - puntos[caras[:, 0]],
        )
        cruz = np.cross(
            suavizados[caras[:, 1]] - suavizados[caras[:, 0]],
            suavizados[caras[:, 2]] - suavizados[caras[:, 0]],
        )
        self.assertTrue(np.all(np.einsum("ij,ij->i", cruz, cruz_original) > 0))

    def test_el_peine_desaparece_y_el_tramo_recto_se_queda(self):
        # Borde superior con dientes de 0,9 mm cada milímetro. El resto es recto.
        columnas, filas = 81, 17
        eje_x = np.linspace(0.0, 80.0, columnas)
        eje_y = np.linspace(0.0, 16.0, filas)
        grilla_x, grilla_y = np.meshgrid(eje_x, eje_y, indexing="xy")
        grilla_y[-1, 1:-1] += np.where(np.arange(columnas - 2) % 2 == 0, 0.9, -0.9)
        puntos = np.column_stack(
            (grilla_x.ravel(), grilla_y.ravel(), np.zeros(columnas * filas))
        )
        caras = []
        for fila in range(filas - 1):
            for columna in range(columnas - 1):
                inicio = fila * columnas + columna
                caras.append((inicio, inicio + 1, inicio + columnas))
                caras.append((inicio + 1, inicio + 1 + columnas, inicio + columnas))
        normales = np.tile([0.0, 0.0, 1.0], (len(puntos), 1))
        suavizados, _, _ = SuavizadoBorde.Aplicar(
            puntos, np.asarray(caras, dtype=np.int32), normales
        )

        interior = np.zeros(len(puntos), dtype=bool)
        for fila in range(1, filas - 1):
            interior[fila * columnas + 1 : (fila + 1) * columnas - 1] = True
        self.assertEqual(
            float(np.linalg.norm(suavizados[interior] - puntos[interior], axis=1).max()),
            0.0,
        )
        abajo = suavizados[:columnas]
        self.assertLess(float(np.max(np.abs(abajo[20:60, 1]))), 0.05)
        arriba = suavizados[(filas - 1) * columnas :, 1]
        dientes = arriba[20:60:2] - arriba[21:60:2]
        self.assertLess(float(np.max(np.abs(dientes))), 0.05)

    def test_un_contorno_corto_y_liso_no_se_mueve(self):
        puntos = np.array(
            [[-10.0, 0.0, 5.0], [0.0, 0.0, 0.0], [10.0, 0.0, 5.0],
             [-10.0, 30.0, 5.0], [0.0, 30.0, 0.0], [10.0, 30.0, 5.0]]
        )
        caras = np.array([[0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4]])
        normales = np.tile([0.0, 0.0, 1.0], (6, 1))
        suavizados, normales_suaves, desplazamiento = SuavizadoBorde.Aplicar(
            puntos, caras, normales
        )
        np.testing.assert_array_equal(suavizados, puntos)
        np.testing.assert_array_equal(normales_suaves, normales)
        self.assertEqual(desplazamiento, 0.0)

    def test_el_cascaron_hereda_el_borde_liso_y_el_marco_sigue_en_cero(self):
        puntos, caras, normales = self._AbanicoDentado()
        _preparados, caras_ok, normales_ok, borde = AnalizadorMalla.Preparar(
            puntos, caras, normales, suavizarNormales=False
        )
        vertices, _faces, _cfg, _interiores, _caras = Model3DForPrinting.ConstruirGeometria(
            puntos,
            caras_ok,
            normales_ok,
            borde,
            pattern="SOLID",
            solid_mm=2.0,
        )
        radios = np.linalg.norm(vertices[1:97, :2], axis=1)
        self.assertLess(float(np.max(np.abs(radios - 30.0))), 0.2)
        self.assertLess(float(np.linalg.norm(vertices[0])), 1e-9)


if __name__ == "__main__":
    unittest.main()
