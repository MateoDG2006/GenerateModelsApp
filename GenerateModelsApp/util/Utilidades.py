"""Registro de mensajes y lectura de la carpeta config.

No calcula geometría. Las clases de dominio piden aquí el logger
y los JSON de parámetros, límites y ejemplos ya medidos.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

# La carpeta del paquete, no la de util/: ahí están config/ y logs/.
_PAQUETE = Path(__file__).resolve().parent.parent


class Registro:
    """Escribe en consola y en logs/ortesislab.log.

    El nivel sale de config/registro.json. Si ese archivo falla,
    se usan INFO en consola y DEBUG en el archivo.
    """

    _PREDETERMINADAS = {
        "nivel_consola": "INFO",
        "nivel_archivo": "DEBUG",
        "archivo": "ortesislab.log",
    }

    @staticmethod
    def _Preferencias() -> dict:
        # Lee el JSON de niveles. Un archivo ausente no detiene el programa.
        ruta = _PAQUETE / "config" / "registro.json"
        preferencias = dict(Registro._PREDETERMINADAS)
        try:
            with ruta.open(encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (OSError, json.JSONDecodeError) as exc:
            preferencias["_aviso"] = f"No se pudo leer {ruta.name}: {exc}"
            return preferencias
        if not isinstance(datos, dict):
            preferencias["_aviso"] = f"{ruta.name} debe contener un objeto JSON."
            return preferencias
        for clave in Registro._PREDETERMINADAS:
            if clave in datos and isinstance(datos[clave], str) and datos[clave].strip():
                preferencias[clave] = datos[clave].strip()
        return preferencias

    @staticmethod
    def _Nivel(nombre: str, respaldo: int) -> int:
        # Traduce "INFO" al número de logging. Un nombre desconocido usa el respaldo.
        try:
            return getattr(logging, str(nombre).upper())
        except AttributeError:
            return respaldo

    @staticmethod
    def Configurar() -> logging.Logger:
        # Prepara el logger raíz una sola vez por proceso.
        logger = logging.getLogger("ortesislab")
        if getattr(logger, "_ortesislab_configurado", False):
            return logger

        preferencias = Registro._Preferencias()
        logger.setLevel(logging.DEBUG)
        formato = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

        consola = logging.StreamHandler()
        consola.setLevel(Registro._Nivel(preferencias["nivel_consola"], logging.INFO))
        consola.setFormatter(formato)
        logger.addHandler(consola)

        try:
            carpeta = _PAQUETE / "logs"
            carpeta.mkdir(exist_ok=True)
            archivo = logging.FileHandler(carpeta / preferencias["archivo"], encoding="utf-8")
            archivo.setLevel(Registro._Nivel(preferencias["nivel_archivo"], logging.DEBUG))
            archivo.setFormatter(formato)
            logger.addHandler(archivo)
        except OSError as exc:
            logger.warning("No se pudo abrir el archivo de registro: %s", exc)

        aviso = preferencias.get("_aviso")
        if aviso:
            logger.warning("%s Se usan los niveles predeterminados.", aviso)

        logger.propagate = False
        logger._ortesislab_configurado = True
        return logger

    @staticmethod
    def Obtener(nombre: str) -> logging.Logger:
        # Devuelve un logger hijo, por ejemplo ortesislab.malla.
        Registro.Configurar()
        return logging.getLogger(f"ortesislab.{nombre}")


class Configuracion:
    """Carga los JSON de config y comprueba que traigan las claves esperadas."""

    _DIR = _PAQUETE / "config"
    _CACHE: dict[str, dict] = {}

    CLAVES_PARAMETROS = (
        "pattern",
        "cell_mm",
        "rib_width_mm",
        "rib_height_mm",
        "liner",
        "skin_mm",
        "solid_mm",
        "border_mm",
        "rounding_mm",
        "angle_deg",
        "seed",
        "reinforce_y_mm",
        "reinforce_width_mm",
        "repair",
        "resolution_mm",
        "flip_normals",
        "surface_step_mm",
    )
    CLAVES_LIMITES = (
        "min_cell_mm",
        "max_rib_width_ratio",
        "min_voxel_repair_mm",
        "fragment_vertex_floor",
        "fragment_vertex_ratio",
        "normal_smooth_iterations",
        "min_normal_length",
        "scale_tolerance",
        "degenerate_area",
        "pattern_batch",
        "voronoi_jitter",
        "seed_separation_epsilon",
        "smooth_factor",
        "smooth_iterations",
        "min_rounding_width_mm",
        "normal_epsilon",
        "max_surface_vertices",
        "surface_subdivision_iterations",
        "clip_snap_mm",
        "min_plausible_surface_extent_mm",
        "max_plausible_surface_extent_mm",
    )
    CLAVES_COMPROBACION = (
        "blender",
        "example_continuous_liner",
        "example_open_lattice",
        "units",
        "scope",
    )

    @staticmethod
    def _Error(mensaje: str, *, detalle: str | None = None):
        # Importación tardía: Excepciones también usa Registro y no debe cerrar un ciclo.
        from ..Excepciones import ConfiguracionInvalida

        raise ConfiguracionInvalida(mensaje, detalle=detalle)

    @staticmethod
    def Recargar() -> None:
        # Olvida lo ya leído para que el siguiente acceso vuelva a disco.
        Configuracion._CACHE.clear()
        Registro.Obtener("configuracion").info("Caché de configuración vaciada.")

    @staticmethod
    def CargarJson(nombre: str) -> dict:
        # Devuelve una copia. Quien la modifique no altera la caché.
        logger = Registro.Obtener("configuracion")
        if nombre in Configuracion._CACHE:
            logger.debug("Configuración en caché: %s", nombre)
            return dict(Configuracion._CACHE[nombre])

        ruta = Configuracion._DIR / nombre
        if not ruta.is_file():
            Configuracion._Error(f"No se encontró la configuración '{nombre}'.", detalle=str(ruta))
        try:
            with ruta.open(encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except json.JSONDecodeError as exc:
            Configuracion._Error(f"El archivo '{nombre}' no es JSON válido.", detalle=str(exc))
        except OSError as exc:
            Configuracion._Error(f"No se pudo leer '{nombre}'.", detalle=str(exc))
        if not isinstance(datos, dict):
            Configuracion._Error(f"'{nombre}' debe contener un objeto JSON.")

        Configuracion._CACHE[nombre] = datos
        logger.info("Configuración cargada: %s", ruta.name)
        return dict(datos)

    @staticmethod
    def _ExigirClaves(datos: dict, claves: tuple[str, ...], nombre: str) -> None:
        faltan = [clave for clave in claves if clave not in datos]
        sobran = sorted(set(datos) - set(claves))
        if faltan or sobran:
            Configuracion._Error(
                f"'{nombre}' no coincide con las claves esperadas.",
                detalle=f"faltan={faltan}; sobran={sobran}",
            )

    @staticmethod
    def ParametrosDefecto() -> dict:
        # Valores iniciales de patrón, celda, nervadura y resolución.
        datos = Configuracion.CargarJson("parametros_defecto.json")
        Configuracion._ExigirClaves(datos, Configuracion.CLAVES_PARAMETROS, "parametros_defecto.json")
        return datos

    @staticmethod
    def Limites() -> dict:
        # Umbrales del algoritmo: celda mínima, voxel, fragmentos, suavizado.
        datos = Configuracion.CargarJson("limites.json")
        Configuracion._ExigirClaves(datos, Configuracion.CLAVES_LIMITES, "limites.json")
        return datos

    @staticmethod
    def ValorLimite(clave: str) -> float:
        datos = Configuracion.Limites()
        if clave not in datos:
            Configuracion._Error(f"Falta el límite '{clave}' en limites.json.")
        numero = datos[clave]
        if isinstance(numero, bool) or not isinstance(numero, (int, float)):
            Configuracion._Error(f"El límite '{clave}' debe ser numérico.")
        return float(numero)

    @staticmethod
    def ComprobacionDeReferencia() -> dict:
        # Resultado ya medido de los dos ejemplos. No son umbrales de rechazo.
        datos = Configuracion.CargarJson("comprobacion_geometrica.json")
        faltan = [clave for clave in Configuracion.CLAVES_COMPROBACION if clave not in datos]
        if faltan:
            Configuracion._Error(
                "comprobacion_geometrica.json no tiene los ejemplos esperados.",
                detalle=str(faltan),
            )
        return datos
