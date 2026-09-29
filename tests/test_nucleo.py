"""Comprueba que el núcleo repartido conserva la geometría del script original."""

from __future__ import annotations

import math
import pathlib
import sys
import unittest

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from GenerateModelsApp.Cascaron import Cascaron
from GenerateModelsApp.Excepciones import (
    AristasNoManifold,
    CeldaDemasiadoPequena,
    EntornoBlenderRequerido,
    NervaduraDemasiadoAncha,
    ParametrosNoReconocidos,
    PatronNoImplementado,
    PatronNoReconocido,
    SemillaInvalida,
    SolidoCerrado,
    SuperficieEliminadaPorPatron,
    VerticesSueltos,
)
from GenerateModelsApp.Malla import AnalizadorMalla
from GenerateModelsApp.Modeling import Model3DForPrinting
from GenerateModelsApp.constants.Materials import PETG
from GenerateModelsApp.constants.Paterns import Patron
from GenerateModelsApp.util.Utilidades import Configuracion


class ReferenciaOriginal:
    # Copia del cálculo anterior, usada solo para comparar. No es código de la aplicación.

    @staticmethod
    def Distancia(p, pattern, cell, angle, seed):
        angle = math.radians(angle)
        c, s = math.cos(angle), math.sin(angle)
        uv = p[:, :2] @ np.array([[c, -s], [s, c]])
        if pattern == "SOLID":
            return np.zeros(len(p))
        if pattern == "DIAMOND":
            a = math.sqrt(0.5)
            uv = uv @ np.array([[a, -a], [a, a]])
        if pattern in {"SQUARE", "DIAMOND"}:
            return np.min(np.abs((uv + cell * 0.5) % cell - cell * 0.5), axis=1)
        low = uv.min(0) - 3 * cell
        high = uv.max(0) + 3 * cell
        dy = cell * math.sqrt(3) / 2
        rng = np.random.default_rng(seed)
        seeds = []
        for row, y in enumerate(np.arange(low[1], high[1] + dy, dy)):
            for x in np.arange(low[0], high[0] + cell, cell):
                v = np.array([x + (row % 2) * cell * 0.5, y])
                if pattern == "VORONOI":
                    v += rng.uniform(-0.28, 0.28, 2) * cell
                seeds.append(v)
        seeds = np.array(seeds)
        result = np.empty(len(p))
        for start in range(0, len(p), 384):
            points = uv[start : start + 384]
            d2 = np.sum((points[:, None, :] - seeds[None, :, :]) ** 2, axis=2)
            nearest = np.argmin(d2, axis=1)
            near = seeds[nearest]
            sep = np.linalg.norm(seeds[None, :, :] - near[:, None, :], axis=2)
            denom = np.where(sep > 1e-10, 2 * sep, 1)
            plane = (d2 - d2[np.arange(len(points)), nearest, None]) / denom
            plane[np.arange(len(points)), nearest] = np.inf
            result[start : start + len(points)] = np.min(plane, axis=1)
        return result


class GeometriaOriginal(unittest.TestCase):
    def setUp(self):
        self.puntos = np.array(
            [
                [0.0, 0.0, 0.2],
                [12.0, 1.0, 0.0],
                [3.0, 18.0, -0.4],
                [20.0, 9.0, 0.1],
                [8.0, 8.0, 0.3],
                [-4.0, 6.0, 0.0],
            ]
        )

    def test_distancia_identica_al_script_original(self):
        for codigo in ("SOLID", "SQUARE", "DIAMOND", "HEX", "VORONOI"):
            for angulo in (0.0, 17.5, -40.0):
                for semilla in (0, 7):
                    with self.subTest(codigo=codigo, angulo=angulo, semilla=semilla):
                        esperado = ReferenciaOriginal.Distancia(self.puntos, codigo, 15.0, angulo, semilla)
                        obtenido = Patron.Obtener(codigo).Distancia(self.puntos, 15.0, angulo, semilla)
                        np.testing.assert_allclose(obtenido, esperado, rtol=0, atol=0)

    def test_distancia_de_semillas_conserva_el_resultado_en_superficie_extensa(self):
        puntos = np.random.default_rng(31).uniform(-150, 150, size=(400, 3))
        for codigo in ("HEX", "VORONOI"):
            with self.subTest(codigo=codigo):
                esperado = ReferenciaOriginal.Distancia(puntos, codigo, 8.0, 19.0, 7)
                obtenido = Patron.Obtener(codigo).Distancia(puntos, 8.0, 19.0, 7)
                np.testing.assert_allclose(obtenido, esperado, rtol=0, atol=0)

    def test_recorte_y_cascaron_conservan_el_original(self):
        triangulos = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
        normales = np.tile(np.array([0.0, 0.0, 1.0]), (4, 1))
        puntos = self.puntos[:4]
        escalar = np.array([1.0, -0.4, 0.2, -1.0])
        recortados, caras, normales_recorte = Cascaron.Recortar(puntos, triangulos, normales, escalar)
        self.assertGreater(len(caras), 0)
        vertices, caras_cerradas = Cascaron.Cerrar(recortados, caras, normales_recorte, 1.2)
        self.assertEqual(len(vertices), len(recortados) * 2)
        self.assertGreaterEqual(len(caras_cerradas), len(caras) * 2)

    def test_smooth01_en_los_extremos(self):
        self.assertEqual(float(Cascaron.Smooth01(np.array(0.0))), 0.0)
        self.assertEqual(float(Cascaron.Smooth01(np.array(1.0))), 1.0)
        self.assertAlmostEqual(float(Cascaron.Smooth01(np.array(0.5))), 0.5)

    def test_triangulo_abierto_queda_en_el_contorno(self):
        puntos = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        caras = np.array([[0, 1, 2]], dtype=np.int32)
        normales = np.tile([0.0, 0.0, 1.0], (3, 1))
        _, _, normales_out, distancia = AnalizadorMalla.Preparar(
            puntos, caras, normales, suavizarNormales=True
        )
        np.testing.assert_allclose(distancia, 0)
        np.testing.assert_allclose(normales_out, normales)

    def test_solido_cerrado_arista_no_manifold_y_vertice_suelto(self):
        tetra = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        caras = np.array([[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]], dtype=np.int32)
        normales = np.ones((4, 3))
        with self.assertRaises(SolidoCerrado):
            AnalizadorMalla.Preparar(tetra, caras, normales, suavizarNormales=False)

        no_manifold = np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, -1.0, 0.0], [1.0, 1.0, 0.0]]
        )
        caras_nm = np.array([[0, 1, 2], [0, 1, 3], [0, 1, 4]], dtype=np.int32)
        with self.assertRaises(AristasNoManifold):
            AnalizadorMalla.Preparar(no_manifold, caras_nm, np.ones((5, 3)), suavizarNormales=False)

        suelto = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [5.0, 5.0, 0.0]])
        with self.assertRaises(VerticesSueltos):
            AnalizadorMalla.Preparar(
                suelto,
                np.array([[0, 1, 2]], dtype=np.int32),
                np.tile([0.0, 0.0, 1.0], (4, 1)),
                suavizarNormales=True,
            )

    def test_recorte_total_avisa_que_hay_que_ensanchar(self):
        puntos = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        with self.assertRaises(SuperficieEliminadaPorPatron):
            Cascaron.Recortar(
                puntos,
                np.array([[0, 1, 2]]),
                np.tile([0.0, 0.0, 1.0], (3, 1)),
                np.array([-1.0, -1.0, -1.0]),
            )

    def test_recorte_no_une_dos_regiones_solo_por_un_vertice(self):
        puntos = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.],
                           [-1., 0., 0.], [0., -1., 0.]])
        caras = np.array([[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1]])
        normales = np.tile([0., 0., 1.], (5, 1))
        escalar = np.array([0., -1., 1., -1., 1.])
        vertices, recortadas, normales_recortadas = Cascaron.Recortar(
            puntos, caras, normales, escalar
        )
        finales, caras_finales = Cascaron.Engrosar(
            vertices, recortadas, normales_recortadas, np.ones(len(vertices))
        )
        aristas = [tuple(sorted((a, b))) for cara in caras_finales
                   for a, b in zip(cara, cara[1:] + cara[:1])]
        _, cuentas = np.unique(aristas, axis=0, return_counts=True)
        self.assertTrue(np.all(cuentas == 2))


class ParametrosYMaterial(unittest.TestCase):
    def test_mensajes_de_cada_rechazo(self):
        casos = (
            ({"cell_mm": 4}, CeldaDemasiadoPequena, "al menos 5 mm"),
            ({"cell_mm": 10, "rib_width_mm": 8}, NervaduraDemasiadoAncha, "75%"),
            ({"pattern": "CUBOS"}, PatronNoReconocido, "Patrón no reconocido"),
            ({"seed": -1}, SemillaInvalida, "entero no negativo"),
            ({"seed": True}, SemillaInvalida, "entero no negativo"),
            ({"desconocido": 1}, ParametrosNoReconocidos, "desconocido"),
        )
        for opciones, error, texto in casos:
            with self.subTest(opciones=opciones):
                with self.assertRaises(error) as contexto:
                    Model3DForPrinting.ValidarOpciones(opciones)
                self.assertIn(texto, str(contexto.exception))

    def test_predeterminados_y_referencia(self):
        datos = Configuracion.ParametrosDefecto()
        self.assertEqual(datos["pattern"], "VORONOI")
        self.assertEqual(datos["seed"], 7)
        referencia = Configuracion.ComprobacionDeReferencia()
        self.assertTrue(referencia["example_continuous_liner"]["ok"])
        self.assertEqual(referencia["units"], "mm")

    def test_catalogo_y_patrones_sin_geometria(self):
        modelo = Model3DForPrinting()
        self.assertEqual(modelo.ChangePatern("HoneyComb").codigo, "HEX")
        self.assertEqual(modelo.ChangePattern("macizo").codigo, "SOLID")
        with self.assertRaises(PatronNoImplementado):
            modelo.ChangePatern("Triangle")
        with self.assertRaises(PatronNoImplementado):
            modelo.ChangePatern("Minimalistic")

    def test_volumen_peso_y_precio_del_tetraedro(self):
        modelo = Model3DForPrinting()
        modelo.vertices = np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        )
        modelo.faces = [(0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)]
        self.assertAlmostEqual(modelo.CalculateVolume(), 1.0 / 6.0)
        peso = modelo.CalculateWeight()
        self.assertAlmostEqual(peso, (1.0 / 6.0) * PETG().density / 1000.0)
        self.assertAlmostEqual(modelo.CalculatePrice(), peso * 0.15)
        self.assertEqual(PETG().name, "PETG")
        self.assertEqual(PETG().type, "filament")

    def test_volumen_de_cascaron_y_sin_geometria(self):
        puntos = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        vertices, caras = Cascaron.Cerrar(puntos, np.array([[0, 1, 2]]), np.tile([0.0, 0.0, 1.0], (3, 1)), 2.0)
        self.assertAlmostEqual(Cascaron.VolumenMm3(vertices, caras), 1.0)
        with self.assertRaises(Exception):
            Model3DForPrinting().CalculateVolume()

    def test_el_paquete_no_exige_blender(self):
        import GenerateModelsApp

        self.assertEqual(GenerateModelsApp.bl_info["name"], "OrtesisLab")
        with self.assertRaises(EntornoBlenderRequerido):
            import GenerateModelsApp.ApiBlender  # noqa: F401


if __name__ == "__main__":
    unittest.main()
