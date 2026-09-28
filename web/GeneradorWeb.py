"""Genera cascarones para la aplicación web.

Usa el núcleo del paquete y no abre Blender. El refinamiento de la superficie
se hace con NumPy; la reconstrucción voxel sigue siendo exclusiva del complemento.
"""

from __future__ import annotations

import struct
import uuid
from pathlib import Path

import numpy as np

from GenerateModelsApp.EscalaMalla import EscalaMalla
from GenerateModelsApp.Excepciones import (
    ArchivoSuperficieIlegible,
    ArchivoSuperficieNoEncontrado,
    OrtesisLabError,
)
from GenerateModelsApp.Malla import AnalizadorMalla
from GenerateModelsApp.Modeling import Model3DForPrinting
from GenerateModelsApp.RefinadorMalla import RefinadorMalla
from GenerateModelsApp.constants.Materials import PETG
from GenerateModelsApp.constants.Nombres import ARCHIVO_SUPERFICIE
from GenerateModelsApp.util.Utilidades import Configuracion

from .LectorSuperficie import LectorSuperficie

# Un lote más grande deja la página esperando varios minutos.
MAXIMO_VARIANTES = 12

PATRONES = {
    "VORONOI": "Orgánico / Voronoi",
    "HEX": "Hexagonal",
    "DIAMOND": "Rombos",
    "SQUARE": "Cuadrícula",
    "SOLID": "Macizo",
}

EJES = {
    "cell_mm": "Tamaño de celda (mm)",
    "rib_width_mm": "Ancho de nervadura (mm)",
    "rib_height_mm": "Altura de nervadura (mm)",
    "skin_mm": "Espesor de capa interior (mm)",
    "solid_mm": "Espesor macizo (mm)",
    "border_mm": "Ancho de marco perimetral (mm)",
    "rounding_mm": "Transición de nervadura (mm)",
    "angle_deg": "Giro del patrón (grados)",
    "seed": "Semilla del patrón orgánico",
    "reinforce_width_mm": "Ancho de banda maciza (mm)",
    "reinforce_y_mm": "Posición de banda, Y (mm)",
}


class GeneradorWeb:
    """Prepara la superficie incluida y construye cada variante con el paquete."""

    _crudas: dict[str, tuple] = {}
    _superficies_refinadas: dict[tuple, tuple] = {}
    _maximo_superficies_refinadas = 2
    diagnostico_escala: dict = {
        "factor": 1.0,
        "factor_sugerido": 1.0,
        "dimension_antes_mm": 0.0,
        "dimension_despues_mm": 0.0,
        "advertencia": "",
    }

    @staticmethod
    def Cruda(archivo: str = ""):
        # Conserva las coordenadas del archivo. La escala se decide al generar.
        if archivo in GeneradorWeb._crudas:
            return GeneradorWeb._crudas[archivo]
        if archivo:
            ruta = GeneradorWeb.RutaSuperficie(archivo)
            try:
                with np.load(ruta, allow_pickle=False) as datos:
                    resultado = (
                        np.asarray(datos["vertices"], dtype=np.float64),
                        np.asarray(datos["faces"], dtype=np.int32),
                        np.asarray(datos["normals"], dtype=np.float64),
                        np.asarray(datos["border"], dtype=np.float64),
                    )
            except (OSError, ValueError, KeyError) as exc:
                raise ArchivoSuperficieIlegible(str(ruta), str(exc)) from exc
            GeneradorWeb._crudas[archivo] = resultado
            return resultado

        ruta = Path(__file__).resolve().parent.parent / "assets" / ARCHIVO_SUPERFICIE
        if not ruta.is_file():
            raise ArchivoSuperficieNoEncontrado(detalle=str(ruta))
        try:
            with np.load(ruta, allow_pickle=False) as datos:
                vertices = datos["vertices"]
                caras = datos["faces"]
                normales = datos["normals"]
        except (OSError, ValueError, KeyError) as exc:
            raise ArchivoSuperficieIlegible(str(ruta), str(exc)) from exc
        resultado = AnalizadorMalla.Preparar(
            vertices, caras, normales, suavizarNormales=False
        )
        GeneradorWeb._crudas[""] = resultado
        return resultado

    @staticmethod
    def EjeMayor(archivo: str = "") -> float:
        puntos = GeneradorWeb.Cruda(archivo)[0]
        if len(puntos) == 0:
            return 0.0
        return float(np.max(np.ptp(puntos, axis=0)))

    @staticmethod
    def Superficie(archivo: str = "", autoescalar: bool = True):
        # Aplica o reserva la corrección decimal según la preferencia actual.
        puntos, caras, normales, borde = GeneradorWeb.Cruda(archivo)
        puntos = np.array(puntos, dtype=np.float64, copy=True)
        caras = np.array(caras, dtype=np.int32, copy=True)
        normales = np.array(normales, dtype=np.float64, copy=True)
        borde = np.array(borde, dtype=np.float64, copy=True)
        dimension = float(np.max(np.ptp(puntos, axis=0))) if len(puntos) else 0.0
        diagnostico = EscalaMalla.Resolver(dimension, autoescalar=autoescalar)
        GeneradorWeb.diagnostico_escala = diagnostico
        factor = float(diagnostico["factor"])
        if factor != 1.0:
            puntos *= factor
            borde *= factor
        return puntos, caras, normales, borde

    @staticmethod
    def SuperficieRefinada(archivo: str, pasoMm: float, autoescalar: bool = True):
        clave = (archivo, bool(autoescalar), round(float(pasoMm), 6))
        if clave not in GeneradorWeb._superficies_refinadas:
            puntos, caras, normales, _borde = GeneradorWeb.Cruda(archivo)
            puntos = np.array(puntos, dtype=np.float64, copy=True)
            caras = np.array(caras, dtype=np.int32, copy=True)
            normales = np.array(normales, dtype=np.float64, copy=True)
            dimension = float(np.max(np.ptp(puntos, axis=0))) if len(puntos) else 0.0
            arista = GeneradorWeb._AristaMayor(puntos, caras)

            def refinar(factor: float):
                copia = puntos if factor == 1.0 else puntos * factor
                return RefinadorMalla.Refinar(copia, caras, normales, pasoMm)

            refinado, diagnostico = EscalaMalla.Aplicar(
                dimension,
                autoescalar,
                refinar,
                arista_maxima=arista,
                paso_mm=pasoMm,
                n_caras=len(caras),
            )
            GeneradorWeb.diagnostico_escala = diagnostico
            GeneradorWeb._superficies_refinadas[clave] = refinado
            while (
                len(GeneradorWeb._superficies_refinadas)
                > GeneradorWeb._maximo_superficies_refinadas
            ):
                primera = next(iter(GeneradorWeb._superficies_refinadas))
                if primera != clave:
                    GeneradorWeb._superficies_refinadas.pop(primera)
        return GeneradorWeb._superficies_refinadas[clave]

    @staticmethod
    def _AristaMayor(puntos, caras) -> float:
        if len(caras) == 0 or len(puntos) == 0:
            return 0.0
        pares = np.vstack((caras[:, [0, 1]], caras[:, [1, 2]], caras[:, [2, 0]]))
        return float(np.linalg.norm(puntos[pares[:, 0]] - puntos[pares[:, 1]], axis=1).max())

    @staticmethod
    def GuardarSuperficie(
        nombre: str,
        contenido: bytes,
        autoescalar: bool = True,
    ) -> tuple[str, dict]:
        # Normaliza la subida y guarda una copia privada para los lotes posteriores.
        resultado, info = LectorSuperficie.Preparar(
            nombre,
            contenido,
            autoescalar=False,
        )
        eje = float(np.max(np.ptp(resultado[0], axis=0))) if len(resultado[0]) else 0.0
        diagnostico = EscalaMalla.Resolver(eje, autoescalar=autoescalar)
        factor = float(diagnostico["factor"])
        dimensiones = np.ptp(resultado[0], axis=0) * factor if len(resultado[0]) else np.zeros(3)
        info["eje_mm"] = eje
        info["factor_escala"] = factor
        info["dimensiones"] = " × ".join(f"{valor:.1f}" for valor in dimensiones) + " mm"
        info["aviso"] = (
            f"Escala corregida ×{factor:g}. "
            if factor != 1.0
            else diagnostico["advertencia"]
        )
        archivo = f"superficie-{uuid.uuid4().hex}.npz"
        ruta = GeneradorWeb.RutaSuperficie(archivo)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        vertices, caras, normales, borde = resultado
        np.savez_compressed(
            ruta,
            vertices=vertices,
            faces=caras,
            normals=normales,
            border=borde,
        )
        GeneradorWeb._crudas[archivo] = resultado
        return archivo, info

    @staticmethod
    def Crear(opciones: dict, superficieArchivo: str = "", autoescalar: bool = True) -> dict:
        # Devuelve la ficha visible y deja el STL donde Reflex puede servirlo.
        if opciones["pattern"] == "SOLID":
            puntos, caras, normales, borde = GeneradorWeb.Superficie(
                superficieArchivo,
                autoescalar=autoescalar,
            )
        else:
            paso = min(
                float(opciones["surface_step_mm"]),
                float(opciones["rib_width_mm"]) / 3.0,
                float(opciones["cell_mm"]) / 6.0,
            )
            puntos, caras, normales, borde = GeneradorWeb.SuperficieRefinada(
                superficieArchivo,
                paso,
                autoescalar=autoescalar,
            )
        modelo = Model3DForPrinting(PETG())
        vertices, faces, cfg, _interiores, _caras = modelo.Construir(
            puntos, caras, normales, borde, **opciones
        )
        volumen = modelo.CalculateVolume()
        peso = modelo.CalculateWeight()
        precio = modelo.CalculatePrice()
        identificador = uuid.uuid4().hex[:8]
        archivo = f"ortesis-{identificador}.stl"
        GeneradorWeb.Escribir(archivo, GeneradorWeb.Stl(vertices, faces))
        ficha = GeneradorWeb.Ficha(
            identificador,
            archivo,
            cfg,
            volumen=volumen,
            peso=peso,
            precio=precio,
            error="",
        )
        factor = float(GeneradorWeb.diagnostico_escala.get("factor", 1))
        if factor != 1.0:
            ficha["detalle"] += f" · escala ×{factor:g}"
        return ficha

    @staticmethod
    def FichaError(opciones: dict, exc: Exception) -> dict:
        # Una variante fallida no corta el resto del lote.
        texto = str(exc).strip() or "No se pudo construir esta variante."
        if len(texto) > 180:
            texto = texto[:177] + "..."
        return GeneradorWeb.Ficha(uuid.uuid4().hex[:8], "", opciones, error=texto)

    @staticmethod
    def Ficha(
        identificador: str,
        archivo: str,
        opciones: dict,
        *,
        volumen: float | None = None,
        peso: float | None = None,
        precio: float | None = None,
        error: str,
    ) -> dict:
        patron = str(opciones.get("pattern", ""))
        return {
            "id": identificador,
            "archivo": archivo,
            "patron": PATRONES.get(patron, patron),
            "detalle": GeneradorWeb.Detalle(opciones),
            "volumen": "" if volumen is None else f"{GeneradorWeb.Numero(volumen, 1)} mm³",
            "peso": "" if peso is None else f"{GeneradorWeb.Numero(peso, 2)} g",
            "precio": "" if precio is None else GeneradorWeb.Numero(precio, 2),
            "error": error,
        }

    @staticmethod
    def Detalle(opciones: dict) -> str:
        # Resume los parámetros que sí cambian el cascarón.
        if opciones.get("pattern") == "SOLID":
            partes = [f"Espesor {GeneradorWeb.Numero(float(opciones['solid_mm']), 2)} mm"]
        else:
            capa = "capa continua" if opciones.get("liner") else "rejilla abierta"
            partes = [
                f"Celda {GeneradorWeb.Numero(float(opciones['cell_mm']), 1)} mm",
                (
                    f"nervadura {GeneradorWeb.Numero(float(opciones['rib_width_mm']), 2)}"
                    f" × {GeneradorWeb.Numero(float(opciones['rib_height_mm']), 2)} mm"
                ),
                capa,
            ]
            if opciones.get("liner"):
                partes.append(f"piel {GeneradorWeb.Numero(float(opciones['skin_mm']), 2)} mm")
            if float(opciones.get("border_mm", 0)) > 0:
                partes.append(f"marco {GeneradorWeb.Numero(float(opciones['border_mm']), 1)} mm")
            if opciones.get("pattern") == "VORONOI":
                partes.append(f"semilla {int(opciones['seed'])}")
            if float(opciones.get("angle_deg", 0)) != 0:
                partes.append(f"giro {GeneradorWeb.Numero(float(opciones['angle_deg']), 1)}°")
        if float(opciones.get("reinforce_width_mm", 0)) > 0:
            partes.append(
                f"banda {GeneradorWeb.Numero(float(opciones['reinforce_width_mm']), 1)} mm"
                f" en Y {GeneradorWeb.Numero(float(opciones['reinforce_y_mm']), 1)}"
            )
        if opciones.get("flip_normals"):
            partes.append("espesor invertido")
        return " · ".join(partes)

    @staticmethod
    def Combinaciones(
        base: dict,
        patrones: list[str],
        eje: str,
        desde: float,
        hasta: float,
        paso: float,
        ambos_revestimientos: bool,
    ) -> list[dict]:
        # Cruza los patrones elegidos con un barrido numérico y, si se pide, la capa.
        if not patrones:
            raise ValueError("Elija al menos un patrón.")
        desconocidos = [patron for patron in patrones if patron not in PATRONES]
        if desconocidos:
            raise ValueError("Hay un patrón que el complemento no construye.")
        if eje and eje != "ninguno" and eje not in EJES:
            raise ValueError("Ese parámetro no forma parte del complemento.")

        valores: list[float] | None = None
        if eje and eje != "ninguno":
            if paso <= 0:
                raise ValueError("El paso del barrido tiene que ser mayor que cero.")
            if desde > hasta:
                raise ValueError("El valor inicial no puede ser mayor que el final.")
            cantidad = int(round((hasta - desde) / paso)) + 1
            valores = [desde + indice * paso for indice in range(cantidad)]
            if eje == "seed":
                valores = [float(int(round(valor))) for valor in valores]

        revestimientos = [True, False] if ambos_revestimientos else [bool(base["liner"])]
        variantes = []
        for patron in patrones:
            capas = revestimientos if patron != "SOLID" else [bool(base["liner"])]
            numeros = valores if valores is not None else [None]
            for numero in numeros:
                for capa in capas:
                    opciones = dict(base)
                    opciones["pattern"] = patron
                    if patron != "SOLID":
                        opciones["liner"] = capa
                    if numero is not None:
                        opciones[eje] = int(numero) if eje == "seed" else float(numero)
                    variantes.append(opciones)
        if not variantes:
            raise ValueError("No hay variantes con esos parámetros.")
        if len(variantes) > MAXIMO_VARIANTES:
            raise ValueError(
                f"El lote tiene {len(variantes)} variantes y el máximo es {MAXIMO_VARIANTES}. "
                "Amplíe el paso o quite un patrón."
            )
        return variantes

    @staticmethod
    def Numero(valor: float, decimales: int) -> str:
        # Separador de miles y coma decimal, como se lee en español.
        texto = f"{valor:,.{decimales}f}"
        return texto.replace(",", " ").replace(".", ",").replace(" ", ".")

    @staticmethod
    def Stl(vertices, caras) -> bytes:
        # STL binario del cascarón, en milímetros, sin pasar por Blender.
        # Los muros del contorno llegan como cuadriláteros; el STL solo admite triángulos.
        puntos = np.asarray(vertices, dtype=np.float64)
        triangulos = GeneradorWeb.Triangulos(caras)
        coords = puntos[triangulos]
        arista_a = coords[:, 1] - coords[:, 0]
        arista_b = coords[:, 2] - coords[:, 0]
        normal = np.cross(arista_a, arista_b)
        longitud = np.linalg.norm(normal, axis=1)
        normal = normal / np.maximum(longitud, 1e-12)[:, None]
        registro = np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("atributo", "<u2")])
        datos = np.zeros(len(triangulos), dtype=registro)
        datos["normal"] = normal.astype(np.float32)
        datos["vertices"] = coords.astype(np.float32)
        cabecera = b"OrtesisLab cascaron geometrico".ljust(80, b"\0")
        return cabecera + struct.pack("<I", len(triangulos)) + datos.tobytes()

    @staticmethod
    def Triangulos(caras) -> np.ndarray:
        # Parte cada cara de más de tres vértices en un abanico de triángulos.
        salida = []
        for cara in caras:
            indices = [int(vertice) for vertice in cara]
            if len(indices) < 3:
                continue
            for posicion in range(1, len(indices) - 1):
                salida.append((indices[0], indices[posicion], indices[posicion + 1]))
        return np.asarray(salida, dtype=np.int32)

    @staticmethod
    def Escribir(nombre: str, datos: bytes) -> None:
        # El visor lee este archivo desde la carpeta de subidas de Reflex.
        import reflex as rx

        destino = GeneradorWeb.Ruta(nombre)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(datos)
        rx.get_upload_dir()

    @staticmethod
    def Leer(nombre: str) -> bytes:
        return GeneradorWeb.Ruta(nombre).read_bytes()

    @staticmethod
    def Ruta(nombre: str) -> Path:
        # Solo acepta el nombre que esta clase acaba de generar.
        if len(nombre) != len("ortesis-12345678.stl") or not nombre.startswith("ortesis-") or not nombre.endswith(".stl"):
            raise ValueError("Esa malla no está en el lote.")
        import reflex as rx

        return rx.get_upload_dir() / nombre

    @staticmethod
    def RutaSuperficie(nombre: str) -> Path:
        # La aplicación solo reabre los NPZ internos creados por GuardarSuperficie.
        prefijo = "superficie-"
        identificador = nombre[len(prefijo) : -len(".npz")]
        if (
            not nombre.startswith(prefijo)
            or not nombre.endswith(".npz")
            or len(identificador) != 32
            or any(caracter not in "0123456789abcdef" for caracter in identificador)
        ):
            raise ValueError("La superficie subida no tiene un identificador válido.")
        import reflex as rx

        return rx.get_upload_dir() / nombre
