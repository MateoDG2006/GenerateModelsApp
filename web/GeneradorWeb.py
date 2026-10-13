"""Genera cascarones para la aplicación web.

Usa el núcleo del paquete y no abre Blender. El refinamiento de la superficie
se hace con NumPy; la reconstrucción voxel sigue siendo exclusiva del complemento.
Las superficies se leen del bucket por la fila de ``file_assets`` del usuario
activo y se guardan en Redis; los STL se publican en el bucket y se abren por
su ``object_url``.
"""

from __future__ import annotations

import struct
import uuid
import math
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

import numpy as np

from GenerateModelsApp.EscalaMalla import EscalaMalla
from GenerateModelsApp.Excepciones import ArchivoSuperficieNoEncontrado
from GenerateModelsApp.RefinadorMalla import RefinadorMalla

from .cache.CacheRedis import CacheRedis
from .ConfiguracionBackend import ConfiguracionBackend
from .persistence.ConexionPostgres import ConexionPostgres
from .persistence.Contratos import ItemLote, SolicitudLote
from .persistence.repositorios import RepositorioAssets
from .services.ContextoUsuario import ContextoUsuario
from .services.ServicioImports import PLANTILLA, ServicioImports
from .storage.AlmacenamientoPrivado import PATRON_CLAVE, Almacen

_CONFIG = ConfiguracionBackend.Cargar("web")
# Un lote más grande deja la página esperando varios minutos.
MAXIMO_VARIANTES = _CONFIG["maximo_variantes"]
# Tiempo máximo que Crear espera al trabajador para una variante suelta.
ESPERA_CREAR_S = _CONFIG["espera_crear_s"]

PATRONES = _CONFIG["patrones"]
EJES = _CONFIG["ejes"]


@lru_cache(maxsize=1)
def _HuellaPlantilla() -> str:
    if not PLANTILLA.is_file():
        raise ArchivoSuperficieNoEncontrado(detalle=str(PLANTILLA))
    return Almacen.Sha256(PLANTILLA.read_bytes())


class GeneradorWeb:
    """Prepara la superficie y traduce resultados persistidos a fichas de la página."""

    @staticmethod
    def _Origen(archivo: str):
        # Hash del contenido y lector diferido. "" es la plantilla incluida.
        if not archivo:
            return _HuellaPlantilla(), lambda: ServicioImports.PrepararPlantilla(PLANTILLA.read_bytes())
        asset_id = ServicioImports.AssetDeNombre(archivo)
        usuario = ContextoUsuario.Actual()
        asset = ConexionPostgres.Ejecutar(lambda conexion: RepositorioAssets.Obtener(conexion, usuario.user_id, asset_id))
        if asset.status != "ready" or asset.kind != "surface_npz":
            raise ArchivoSuperficieNoEncontrado(detalle=archivo)
        return asset.sha256, lambda: ServicioImports.NpzATupla(
            Almacen.LeerVerificado(asset.storage_key, asset.sha256), archivo
        )

    @staticmethod
    def Cruda(archivo: str = ""):
        # Conserva las coordenadas del archivo. La escala se decide al generar.
        huella, cargar = GeneradorWeb._Origen(archivo)
        clave = CacheRedis.ClaveCruda(huella)
        resultado = CacheRedis.LeerTupla(clave)
        if resultado is not None and len(resultado) == 4:
            return resultado
        resultado = cargar()
        CacheRedis.GuardarTupla(clave, resultado)
        return resultado

    @staticmethod
    def EjeMayor(archivo: str = "") -> float:
        puntos = GeneradorWeb.Cruda(archivo)[0]
        if len(puntos) == 0:
            return 0.0
        return float(np.max(np.ptp(puntos, axis=0)))

    @staticmethod
    def Superficie(archivo: str = "", autoescalar: bool = True):
        return GeneradorWeb._SuperficieConDiagnostico(archivo, autoescalar)[0]

    @staticmethod
    def _SuperficieConDiagnostico(archivo: str, autoescalar: bool):
        # Aplica o reserva la corrección decimal según la preferencia actual.
        puntos, caras, normales, borde = GeneradorWeb.Cruda(archivo)
        puntos = np.array(puntos, dtype=np.float64, copy=True)
        caras = np.array(caras, dtype=np.int32, copy=True)
        normales = np.array(normales, dtype=np.float64, copy=True)
        borde = np.array(borde, dtype=np.float64, copy=True)
        dimension = float(np.max(np.ptp(puntos, axis=0))) if len(puntos) else 0.0
        diagnostico = EscalaMalla.Resolver(dimension, autoescalar=autoescalar)
        factor = float(diagnostico["factor"])
        if factor != 1.0:
            puntos *= factor
            borde *= factor
        return (puntos, caras, normales, borde), diagnostico

    @staticmethod
    def SuperficieRefinada(archivo: str, pasoMm: float, autoescalar: bool = True):
        return GeneradorWeb._SuperficieRefinadaConDiagnostico(archivo, pasoMm, autoescalar)[0]

    @staticmethod
    def _SuperficieRefinadaConDiagnostico(archivo: str, pasoMm: float, autoescalar: bool):
        huella, _cargar = GeneradorWeb._Origen(archivo)
        clave = CacheRedis.ClaveRefinada(huella, pasoMm, autoescalar)
        clave_diagnostico = CacheRedis.ClaveDiagnostico(huella, autoescalar, pasoMm)
        refinado = CacheRedis.LeerTupla(clave)
        diagnostico = CacheRedis.LeerDiagnostico(clave_diagnostico)
        if refinado is not None and diagnostico is not None:
            return refinado, diagnostico

        puntos, caras, normales, _borde = GeneradorWeb.Cruda(archivo)
        puntos = np.array(puntos, dtype=np.float64, copy=True)
        caras = np.array(caras, dtype=np.int32, copy=True)
        normales = np.array(normales, dtype=np.float64, copy=True)
        dimension = float(np.max(np.ptp(puntos, axis=0))) if len(puntos) else 0.0
        arista = RefinadorMalla.AristaMayor(puntos, caras)

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
        CacheRedis.GuardarTupla(clave, refinado)
        CacheRedis.GuardarDiagnostico(clave_diagnostico, diagnostico)
        return refinado, diagnostico

    @staticmethod
    def GuardarSuperficie(
        nombre: str,
        contenido: bytes,
        autoescalar: bool = True,
    ) -> tuple[str, dict]:
        # Registra el import del usuario activo; original y NPZ quedan en el bucket.
        importacion, info = ServicioImports.Importar(ContextoUsuario.Actual(), nombre, contenido, autoescalar)
        return ServicioImports.NombreSuperficie(importacion.normalized_asset_id), info

    @staticmethod
    def Crear(opciones: dict, superficieArchivo: str = "", autoescalar: bool = True) -> dict:
        # Encola una versión suelta, espera al trabajador y devuelve su ficha persistida.
        from .services.ServicioLotes import ServicioLotes

        usuario = ContextoUsuario.Actual()
        importacion = ServicioImports.Resolver(usuario, superficieArchivo)
        lote = ServicioLotes.Solicitar(
            usuario,
            SolicitudLote(
                import_id=importacion.id,
                request_id=uuid.uuid4(),
                mode="single",
                definition={"origen": "Crear"},
                variantes=[dict(opciones)],
                auto_scale=bool(autoescalar),
            ),
        )
        progreso = ServicioLotes.Esperar(usuario, lote.id, ESPERA_CREAR_S)
        if progreso.abierto:
            return GeneradorWeb.FichaError(opciones, TimeoutError("El trabajador no terminó a tiempo."))
        return GeneradorWeb._FichaDeItem(progreso.items[0])

    @staticmethod
    def _FichaDeItem(item: ItemLote) -> dict:
        # La ficha visible sale de la fila persistida, nunca de un archivo local.
        resultado = item.resultado
        if item.status == "succeeded" and resultado is not None:
            if resultado.stl_status != "ready" or not resultado.stl_url:
                return GeneradorWeb.Ficha(
                    str(item.id), "", item.parameters, error="El STL ya no está en el almacén."
                )
            ficha = GeneradorWeb.Ficha(
                str(item.id),
                resultado.stl_url,
                item.parameters,
                volumen=resultado.volume_mm3,
                peso=resultado.weight_g,
                precio=float(resultado.estimated_price),
                error="",
            )
            factor = float(resultado.effective_scale or 1.0)
            if factor != 1.0:
                ficha["detalle"] += f" · escala ×{factor:g}"
            return ficha
        if item.status == "cancelled":
            return GeneradorWeb.Ficha(str(item.id), "", item.parameters, error="Cancelada.")
        texto = (item.error_message or "").strip() or "No se pudo construir esta variante."
        if len(texto) > 180:
            texto = texto[:177] + "..."
        return GeneradorWeb.Ficha(str(item.id), "", item.parameters, error=texto)

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
        """Entrada: patrones, rango y paso. Proceso: acota el barrido antes de
        crear variantes. Salida: opciones dentro del rango. Errores: ValueError
        ante parámetros inválidos o lote excesivo. Efectos: ninguno.
        """
        if not patrones:
            raise ValueError("Elija al menos un patrón.")
        desconocidos = [patron for patron in patrones if patron not in PATRONES]
        if desconocidos:
            raise ValueError("Hay un patrón que el complemento no construye.")
        if eje and eje != "ninguno" and eje not in EJES:
            raise ValueError("Ese parámetro no forma parte del complemento.")

        multiplicador = sum(1 if patron == "SOLID" or not ambos_revestimientos else 2 for patron in patrones)
        valores: list[float | int] | None = None
        if eje and eje != "ninguno":
            if not all(math.isfinite(valor) for valor in (desde, hasta, paso)):
                raise ValueError("El barrido requiere números finitos.")
            if paso <= 0:
                raise ValueError("El paso del barrido tiene que ser mayor que cero.")
            if desde > hasta:
                raise ValueError("El valor inicial no puede ser mayor que el final.")
            if eje == "seed":
                if desde < 0 or not all(valor.is_integer() for valor in (desde, hasta, paso)):
                    raise ValueError("El barrido de semillas requiere enteros no negativos y paso entero.")
            inicio = Decimal(str(desde))
            final = Decimal(str(hasta))
            incremento = Decimal(str(paso))
            maximo_valores = MAXIMO_VARIANTES // multiplicador
            if final - inicio >= incremento * maximo_valores:
                raise ValueError(
                    f"El lote tiene más de {MAXIMO_VARIANTES} variantes. "
                    "Amplíe el paso o quite un patrón."
                )
            cantidad = int((final - inicio) // incremento) + 1
            valores = [
                int(inicio + indice * incremento) if eje == "seed"
                else float(inicio + indice * incremento)
                for indice in range(cantidad)
            ]
        elif multiplicador > MAXIMO_VARIANTES:
            raise ValueError(f"El lote supera el máximo de {MAXIMO_VARIANTES} variantes.")

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
                        opciones[eje] = numero
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
        # Repone el objeto de un STL registrado; solo acepta los bytes que su fila declara.
        clave = GeneradorWeb.Ruta(nombre).as_posix()
        usuario = ContextoUsuario.Actual()
        asset = ConexionPostgres.Ejecutar(lambda conexion: RepositorioAssets.PorClave(conexion, usuario.user_id, clave))
        huella = Almacen.Sha256(datos)
        if huella != asset.sha256:
            raise ValueError("Los datos no coinciden con la malla registrada.")
        Almacen.Actual().Publicar(clave, datos, asset.media_type, huella, f"ortesis-{asset.id.hex[:8]}.stl")

    @staticmethod
    def Leer(nombre: str) -> bytes:
        clave = GeneradorWeb.Ruta(nombre).as_posix()
        usuario = ContextoUsuario.Actual()
        asset = ConexionPostgres.Ejecutar(lambda conexion: RepositorioAssets.PorClave(conexion, usuario.user_id, clave))
        return Almacen.LeerVerificado(asset.storage_key, asset.sha256)

    @staticmethod
    def Ruta(nombre: str) -> Path:
        # Clave del objeto de una object_url del usuario activo; rechaza cualquier otra.
        coincidencia = PATRON_CLAVE.search(nombre)
        if coincidencia is None or not nombre.endswith(".stl"):
            raise ValueError("Esa malla no está en el lote.")
        clave = coincidencia.group(0)
        if nombre != Almacen.Actual().Url(clave) or coincidencia.group("user") != str(ContextoUsuario.Actual().user_id):
            raise ValueError("Esa malla no está en el lote.")
        return Path(clave)

    @staticmethod
    def RutaSuperficie(nombre: str) -> Path:
        # Clave del NPZ normalizado de un import del usuario activo.
        asset_id = ServicioImports.AssetDeNombre(nombre)
        usuario = ContextoUsuario.Actual()
        asset = ConexionPostgres.Ejecutar(lambda conexion: RepositorioAssets.Obtener(conexion, usuario.user_id, asset_id))
        if asset.kind != "surface_npz":
            raise ValueError("La superficie subida no tiene un identificador válido.")
        return Path(asset.storage_key)
