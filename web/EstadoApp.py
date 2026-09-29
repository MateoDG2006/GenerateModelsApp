"""Estado de la página de comparación.

Los arreglos de la malla no viven aquí: el visor los lee del archivo STL.
"""

from __future__ import annotations

import asyncio
import math

import reflex as rx

from GenerateModelsApp.EscalaMalla import EscalaMalla
from GenerateModelsApp.Excepciones import OrtesisLabError
from GenerateModelsApp.util.Utilidades import Configuracion, Registro

from .GeneradorWeb import EJES, MAXIMO_VARIANTES, GeneradorWeb
from .LectorSuperficie import LectorSuperficie

ID_SUBIDA_SUPERFICIE = "superficie-entrada"


class EstadoApp(rx.State):
    """Parámetros del complemento, lote en curso y fichas ya generadas."""

    pattern: str = "VORONOI"
    cell_mm: str = "15"
    rib_width_mm: str = "2.8"
    rib_height_mm: str = "1.4"
    liner: bool = True
    skin_mm: str = "1"
    solid_mm: str = "2.4"
    border_mm: str = "4"
    rounding_mm: str = "0.8"
    angle_deg: str = "0"
    seed: str = "7"
    reinforce_y_mm: str = "0"
    reinforce_width_mm: str = "0"
    flip_normals: bool = False
    repair: bool = False
    resolution_mm: str = "0.3"
    surface_step_mm: str = "1"

    usar_voronoi: bool = True
    usar_hex: bool = False
    usar_diamond: bool = False
    usar_square: bool = False
    usar_solid: bool = False
    eje: str = "ninguno"
    desde: str = "10"
    hasta: str = "20"
    paso: str = "5"
    ambos_revestimientos: bool = False

    ocupado: bool = False
    mensaje: str = "Listo para generar. Cada variante tarda cerca de 20 segundos."
    hechos: int = 0
    total: int = 0
    modo_lote: bool = False
    archivo: str = ""
    ficha_detalle: str = ""
    ficha_volumen: str = ""
    ficha_peso: str = ""
    ficha_precio: str = ""
    ficha_error: str = ""
    resultados: list[dict[str, str]] = []
    vistas: list[str] = []
    superficie_archivo: str = ""
    superficie_nombre: str = "Superficie incluida"
    superficie_detalle: str = "Plantilla incluida en el proyecto."
    superficie_error: str = ""
    subiendo_superficie: bool = False
    autoescalar_superficie: bool = True
    superficie_eje_mm: float = 0.0
    _trabajando: int = 0

    @rx.event
    def set_pattern(self, valor: str):
        self.pattern = valor

    @rx.event
    def set_cell_mm(self, valor: str):
        self.cell_mm = valor

    @rx.event
    def set_rib_width_mm(self, valor: str):
        self.rib_width_mm = valor

    @rx.event
    def set_rib_height_mm(self, valor: str):
        self.rib_height_mm = valor

    @rx.event
    def set_liner(self, valor: bool):
        self.liner = valor

    @rx.event
    def set_skin_mm(self, valor: str):
        self.skin_mm = valor

    @rx.event
    def set_solid_mm(self, valor: str):
        self.solid_mm = valor

    @rx.event
    def set_border_mm(self, valor: str):
        self.border_mm = valor

    @rx.event
    def set_rounding_mm(self, valor: str):
        self.rounding_mm = valor

    @rx.event
    def set_angle_deg(self, valor: str):
        self.angle_deg = valor

    @rx.event
    def set_seed(self, valor: str):
        self.seed = valor

    @rx.event
    def set_reinforce_y_mm(self, valor: str):
        self.reinforce_y_mm = valor

    @rx.event
    def set_reinforce_width_mm(self, valor: str):
        self.reinforce_width_mm = valor

    @rx.event
    def set_flip_normals(self, valor: bool):
        self.flip_normals = valor

    @rx.event
    def set_surface_step_mm(self, valor: str):
        self.surface_step_mm = valor

    @rx.event
    def set_autoescalar_superficie(self, valor: bool):
        self.autoescalar_superficie = valor

    @rx.event
    def set_usar_voronoi(self, valor: bool):
        self.usar_voronoi = valor

    @rx.event
    def set_usar_hex(self, valor: bool):
        self.usar_hex = valor

    @rx.event
    def set_usar_diamond(self, valor: bool):
        self.usar_diamond = valor

    @rx.event
    def set_usar_square(self, valor: bool):
        self.usar_square = valor

    @rx.event
    def set_usar_solid(self, valor: bool):
        self.usar_solid = valor

    @rx.event
    def set_eje(self, valor: str):
        self.eje = valor

    @rx.event
    def set_desde(self, valor: str):
        self.desde = valor

    @rx.event
    def set_hasta(self, valor: str):
        self.hasta = valor

    @rx.event
    def set_paso(self, valor: str):
        self.paso = valor

    @rx.event
    def set_ambos_revestimientos(self, valor: bool):
        self.ambos_revestimientos = valor

    @rx.event
    async def CargarSuperficie(self, archivos: list[rx.UploadFile]):
        # La subida se normaliza a NPZ y se valida antes de habilitar la generación.
        if len(archivos) != 1:
            self.superficie_error = "Seleccione un único archivo STL o NPZ."
            return rx.clear_selected_files(ID_SUBIDA_SUPERFICIE)
        self.subiendo_superficie = True
        self.superficie_error = ""
        archivo = archivos[0]
        try:
            contenido = await archivo.read(LectorSuperficie.MAXIMO_BYTES + 1)
            nombre_interno, info = await asyncio.to_thread(
                GeneradorWeb.GuardarSuperficie,
                archivo.name,
                contenido,
                self.autoescalar_superficie,
            )
        except (ValueError, OrtesisLabError) as exc:
            self.superficie_error = str(exc)
            self.mensaje = "La superficie subida no es válida."
        except Exception:
            Registro.Obtener("web").exception("Fallo no previsto al cargar una superficie")
            self.superficie_error = "No se pudo leer la superficie."
            self.mensaje = self.superficie_error
        else:
            self.superficie_archivo = nombre_interno
            self.superficie_nombre = info["nombre"]
            self.superficie_detalle = (
                f"{info['dimensiones']} · {info['vertices']} vértices · "
                f"{info['caras']} triángulos"
            )
            self.superficie_eje_mm = float(info.get("eje_mm", 0))
            if info["aviso"]:
                self.superficie_detalle += f" · {info['aviso']}"
            self.resultados = []
            self.vistas = []
            self.archivo = ""
            self.mensaje = "Superficie cargada; lista para generar."
        finally:
            self.subiendo_superficie = False
        return rx.clear_selected_files(ID_SUBIDA_SUPERFICIE)

    @rx.event
    def UsarSuperficieIncluida(self):
        self.superficie_archivo = ""
        self.superficie_nombre = "Superficie incluida"
        self.superficie_detalle = "Plantilla incluida en el proyecto."
        self.superficie_eje_mm = GeneradorWeb.EjeMayor("")
        self.superficie_error = ""
        self.resultados = []
        self.vistas = []
        self.archivo = ""
        self.mensaje = "Superficie incluida seleccionada."

    @rx.event
    def CargarPredeterminados(self):
        # Los valores iniciales salen del mismo JSON que usa el complemento.
        datos = Configuracion.ParametrosDefecto()
        self.pattern = str(datos["pattern"])
        self.cell_mm = str(datos["cell_mm"])
        self.rib_width_mm = str(datos["rib_width_mm"])
        self.rib_height_mm = str(datos["rib_height_mm"])
        self.liner = bool(datos["liner"])
        self.skin_mm = str(datos["skin_mm"])
        self.solid_mm = str(datos["solid_mm"])
        self.border_mm = str(datos["border_mm"])
        self.rounding_mm = str(datos["rounding_mm"])
        self.angle_deg = str(datos["angle_deg"])
        self.seed = str(datos["seed"])
        self.reinforce_y_mm = str(datos["reinforce_y_mm"])
        self.reinforce_width_mm = str(datos["reinforce_width_mm"])
        self.flip_normals = bool(datos["flip_normals"])
        self.repair = bool(datos["repair"])
        self.resolution_mm = str(datos["resolution_mm"])
        self.surface_step_mm = str(datos["surface_step_mm"])
        if not self.superficie_archivo:
            self.superficie_eje_mm = GeneradorWeb.EjeMayor("")

    @rx.event
    def Previsualizar(self):
        self.modo_lote = False
        return EstadoApp.Generar

    @rx.event
    def PedirLote(self):
        self.modo_lote = True
        return EstadoApp.Generar

    @rx.event(background=True)
    async def Generar(self):
        # Construye fuera del bloqueo de la página para que el avance se pueda pintar.
        async with self:
            if self._trabajando:
                return
            self._trabajando = 1
            self.ocupado = True
            self.hechos = 0
            self.mensaje = "Preparando la superficie…"
            try:
                variantes = self._Variantes()
            except (ValueError, OrtesisLabError) as exc:
                self.mensaje = str(exc)
                self.ocupado = False
                self._trabajando = 0
                return
            except Exception:
                Registro.Obtener("web").exception("Fallo al preparar el lote")
                self.mensaje = "No se pudo preparar la generación."
                self.ocupado = False
                self._trabajando = 0
                return
            self.total = len(variantes)
            self.resultados = []
            self.vistas = []
            self.archivo = ""
            superficie_archivo = self.superficie_archivo
            autoescalar = self.autoescalar_superficie

        fichas = []
        try:
            for indice, opciones in enumerate(variantes, start=1):
                try:
                    ficha = await asyncio.to_thread(
                        GeneradorWeb.Crear,
                        opciones,
                        superficie_archivo,
                        autoescalar,
                    )
                except OrtesisLabError as exc:
                    ficha = GeneradorWeb.FichaError(opciones, exc)
                except Exception:
                    Registro.Obtener("web").exception("Fallo no previsto al construir una variante")
                    ficha = GeneradorWeb.FichaError(opciones, RuntimeError("fallo"))
                fichas.append(ficha)
                async with self:
                    self.hechos = indice
                    self.resultados = list(fichas)
                    self.mensaje = f"{indice} de {len(variantes)}"
                    if ficha["archivo"] and not self.archivo:
                        self._Mostrar(ficha)
            async with self:
                errores = sum(1 for ficha in fichas if ficha["error"])
                if errores:
                    self.mensaje = f"Listo. {errores} de {len(fichas)} no se pudieron construir."
                else:
                    self.mensaje = f"Listo. {len(fichas)} variante{'s' if len(fichas) != 1 else ''}."
        finally:
            async with self:
                if self.hechos < self.total:
                    self.mensaje = "Generación interrumpida; puede intentarlo de nuevo."
                self.ocupado = False
                self._trabajando = 0

    @rx.event
    def Ver(self, identificador: str):
        for ficha in self.resultados:
            if ficha["id"] == identificador:
                self._Mostrar(ficha)
                return

    @rx.event
    def Comparar(self, identificador: str):
        # Hasta tres visores a la vez. Un segundo clic quita esa variante.
        ficha = next((item for item in self.resultados if item["id"] == identificador), None)
        if ficha is None or not ficha["archivo"]:
            return
        if ficha["archivo"] in self.vistas:
            self.vistas = [nombre for nombre in self.vistas if nombre != ficha["archivo"]]
            return
        if len(self.vistas) >= 3:
            self.mensaje = "La comparación muestra tres ortesis a la vez. Quite una para añadir otra."
            return
        self.vistas = [*self.vistas, ficha["archivo"]]
        self._Mostrar(ficha)

    @rx.event
    def Descargar(self, identificador: str):
        ficha = next((item for item in self.resultados if item["id"] == identificador), None)
        if ficha is None or not ficha["archivo"]:
            return
        datos = GeneradorWeb.Leer(ficha["archivo"])
        return rx.download(data=datos, filename=ficha["archivo"])

    @rx.var
    def aviso_escala(self) -> str:
        # El texto sigue a la casilla, también después de haber cargado el archivo.
        if self.superficie_eje_mm <= 0:
            return (
                "Corrige un archivo en centímetros o metros al generar. "
                "Desactívelo para conservar el tamaño original."
            )
        diagnostico = EscalaMalla.Resolver(
            self.superficie_eje_mm,
            autoescalar=self.autoescalar_superficie,
        )
        factor = float(diagnostico["factor"])
        if factor != 1.0:
            return (
                f"Al generar se aplicará ×{factor:g}: "
                f"{diagnostico['dimension_antes_mm']:.2f} a "
                f"{diagnostico['dimension_despues_mm']:.2f} mm."
            )
        if diagnostico["advertencia"]:
            return diagnostico["advertencia"]
        return (
            f"Eje mayor {self.superficie_eje_mm:.1f} mm, dentro del rango de una ortesis."
        )

    @rx.var
    def espesor_total(self) -> str:
        # El panel también muestra capa + altura cuando la capa continua está activa.
        try:
            total = EstadoApp._Numero(self.skin_mm, "Capa") + EstadoApp._Numero(self.rib_height_mm, "Altura")
        except ValueError:
            return ""
        return GeneradorWeb.Numero(total, 2)

    @rx.var
    def porcentaje(self) -> int:
        if self.total <= 0:
            return 0
        return int(self.hechos * 100 / self.total)

    def _Mostrar(self, ficha: dict):
        self.archivo = ficha["archivo"]
        self.ficha_detalle = ficha["detalle"]
        self.ficha_volumen = ficha["volumen"]
        self.ficha_peso = ficha["peso"]
        self.ficha_precio = ficha["precio"]
        self.ficha_error = ficha["error"]

    def _Variantes(self) -> list[dict]:
        base = self._Opciones()
        if not self.modo_lote:
            return [base]
        patrones = [
            codigo
            for codigo, activo in (
                ("VORONOI", self.usar_voronoi),
                ("HEX", self.usar_hex),
                ("DIAMOND", self.usar_diamond),
                ("SQUARE", self.usar_square),
                ("SOLID", self.usar_solid),
            )
            if activo
        ]
        desde, hasta, paso = (0.0, 0.0, 1.0) if self.eje in ("", "ninguno") else (
            self._Numero(self.desde, "Valor inicial"),
            self._Numero(self.hasta, "Valor final"),
            self._Numero(self.paso, "Paso"),
        )
        return GeneradorWeb.Combinaciones(
            base,
            patrones,
            self.eje,
            desde,
            hasta,
            paso,
            self.ambos_revestimientos,
        )

    def _Opciones(self) -> dict:
        semilla = self._Numero(self.seed, "Semilla")
        if semilla < 0 or semilla != int(semilla):
            raise ValueError("La semilla debe ser un entero no negativo.")
        return {
            "pattern": self.pattern,
            "cell_mm": self._Numero(self.cell_mm, "Tamaño de celda"),
            "rib_width_mm": self._Numero(self.rib_width_mm, "Ancho de nervadura"),
            "rib_height_mm": self._Numero(self.rib_height_mm, "Altura de nervadura"),
            "liner": self.liner,
            "skin_mm": self._Numero(self.skin_mm, "Espesor de capa"),
            "solid_mm": self._Numero(self.solid_mm, "Espesor macizo"),
            "border_mm": self._Numero(self.border_mm, "Marco"),
            "rounding_mm": self._Numero(self.rounding_mm, "Transición"),
            "angle_deg": self._Numero(self.angle_deg, "Giro"),
            "seed": int(semilla),
            "reinforce_y_mm": self._Numero(self.reinforce_y_mm, "Posición de banda"),
            "reinforce_width_mm": self._Numero(self.reinforce_width_mm, "Ancho de banda"),
            "flip_normals": self.flip_normals,
            "repair": self.repair,
            "resolution_mm": self._Numero(self.resolution_mm, "Resolución"),
            "surface_step_mm": self._Numero(self.surface_step_mm, "Paso de superficie"),
        }

    @staticmethod
    def _Numero(texto: str, etiqueta: str) -> float:
        limpio = texto.strip().replace(",", ".")
        try:
            valor = float(limpio)
        except ValueError as exc:
            raise ValueError(f"{etiqueta} tiene que ser un número.") from exc
        if not math.isfinite(valor):
            raise ValueError(f"{etiqueta} tiene que ser un número finito.")
        return valor


# El máximo se muestra en la página sin duplicar la constante en el texto fijo.
LIMITE_LOTE = MAXIMO_VARIANTES
ETIQUETAS_EJE = [("ninguno", "No variar números"), *EJES.items()]
