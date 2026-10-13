"""Estado de la página de comparación.

Los arreglos de la malla no viven aquí: el visor lee el STL de su object_url.
Los lotes, versiones y métricas están en PostgreSQL; la página solo guarda
filtros, identificadores y la ficha visible.
"""

from __future__ import annotations

import asyncio
import math
import uuid

import reflex as rx

from GenerateModelsApp.EscalaMalla import EscalaMalla
from GenerateModelsApp.Excepciones import OrtesisLabError
from GenerateModelsApp.util.Utilidades import Configuracion, Registro

from .ConfiguracionBackend import ConfiguracionBackend
from .enums import ITEMS_TERMINALES
from .GeneradorWeb import EJES, MAXIMO_VARIANTES, GeneradorWeb
from .LectorSuperficie import LectorSuperficie
from .persistence.Contratos import (
    ConflictoRevision,
    ErrorPersistencia,
    ProgresoLote,
    SesionInvalida,
    SolicitudLote,
    UsuarioAutenticado,
)
from .services.ContextoUsuario import ContextoUsuario
from .services.ServicioHistorial import ServicioHistorial
from .services.ServicioImports import ServicioImports
from .services.ServicioLotes import ServicioLotes
from .services.ServicioPreferencias import ServicioPreferencias
from .storage.AlmacenamientoPrivado import PATRON_CLAVE

ID_SUBIDA_SUPERFICIE = "superficie-entrada"
INTERVALO_PROGRESO_S = ConfiguracionBackend.Cargar("web")["intervalo_progreso_s"]
TERMINALES = ITEMS_TERMINALES


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
    autenticado: bool = False
    usuario_nombre: str = ""
    lote_id: str = ""
    _trabajando: int = 0
    _solicitud: str = ""
    _revision_preferencias: int = 0
    _propietario: str = ""

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
    async def set_autoescalar_superficie(self, valor: bool):
        # La preferencia se guarda por usuario; otra pestaña puede haberla cambiado antes.
        self.autoescalar_superficie = valor
        usuario = await self._Usuario()
        if usuario is None:
            return
        try:
            preferencias = await asyncio.to_thread(
                ServicioPreferencias.GuardarAutoescala, usuario, valor, self._revision_preferencias
            )
        except ConflictoRevision as exc:
            preferencias = await asyncio.to_thread(ServicioPreferencias.Obtener, usuario)
            self.autoescalar_superficie = preferencias.auto_scale
            self.mensaje = str(exc)
        except ErrorPersistencia as exc:
            self.mensaje = str(exc)
            return
        self._revision_preferencias = preferencias.revision

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
        # La subida queda como import del usuario: original y NPZ en el bucket.
        if len(archivos) != 1:
            self.superficie_error = "Seleccione un único archivo STL o NPZ."
            return rx.clear_selected_files(ID_SUBIDA_SUPERFICIE)
        usuario = await self._Usuario()
        if usuario is None:
            self.superficie_error = "Inicie sesión para guardar la superficie."
            return rx.clear_selected_files(ID_SUBIDA_SUPERFICIE)
        self.subiendo_superficie = True
        self.superficie_error = ""
        archivo = archivos[0]
        try:
            contenido = await archivo.read(LectorSuperficie.MAXIMO_BYTES + 1)
            with ContextoUsuario.Activar(usuario):
                nombre_interno, info = await asyncio.to_thread(
                    GeneradorWeb.GuardarSuperficie,
                    archivo.name,
                    contenido,
                    self.autoescalar_superficie,
                )
        except (ValueError, OrtesisLabError) as exc:
            self.superficie_error = str(exc)
            self.mensaje = "La superficie subida no es válida."
        except ErrorPersistencia as exc:
            self.superficie_error = str(exc)
            self.mensaje = "No se pudo guardar la superficie."
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
    async def UsarSuperficieIncluida(self):
        self.superficie_archivo = ""
        self.superficie_nombre = "Superficie incluida"
        self.superficie_detalle = "Plantilla incluida en el proyecto."
        self.superficie_eje_mm = await asyncio.to_thread(GeneradorWeb.EjeMayor, "")
        self.superficie_error = ""
        self.resultados = []
        self.vistas = []
        self.archivo = ""
        self.mensaje = "Superficie incluida seleccionada."

    @rx.event
    async def CargarPredeterminados(self):
        # Valores del JSON del complemento, preferencias guardadas y último lote del usuario.
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
        usuario = await self._Usuario()
        propietario = "" if usuario is None else str(usuario.user_id)
        if propietario != self._propietario and not self.ocupado:
            # La pestaña conserva el estado entre sesiones: nada del usuario anterior queda visible.
            self._OlvidarTrabajo()
            self._propietario = propietario
        if not self.superficie_archivo:
            self.superficie_eje_mm = await asyncio.to_thread(GeneradorWeb.EjeMayor, "")
        if usuario is None:
            self.mensaje = "Inicie sesión para generar y guardar su trabajo."
            return
        try:
            preferencias = await asyncio.to_thread(ServicioPreferencias.Obtener, usuario)
            ultimo = await asyncio.to_thread(ServicioLotes.Ultimo, usuario)
        except ErrorPersistencia as exc:
            self.mensaje = str(exc)
            return
        self.autoescalar_superficie = preferencias.auto_scale
        self._revision_preferencias = preferencias.revision
        if not self.ocupado:
            self.mensaje = "Listo para generar. Cada variante tarda cerca de 20 segundos."
        if ultimo is None or self.ocupado:
            return
        self.lote_id = str(ultimo.lote.id)
        self._Publicar(ultimo)
        if ultimo.abierto:
            return EstadoApp.SeguirLote

    @rx.event
    def Previsualizar(self):
        self.modo_lote = False
        self._solicitud = uuid.uuid4().hex
        return EstadoApp.Generar

    @rx.event
    def PedirLote(self):
        self.modo_lote = True
        self._solicitud = uuid.uuid4().hex
        return EstadoApp.Generar

    @rx.event(background=True)
    async def Generar(self):
        # Registra el lote en la base y sigue su avance; el trabajador construye las variantes.
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
            cookie = self.router.headers.cookie
            request_id = uuid.UUID(hex=self._solicitud) if self._solicitud else uuid.uuid4()
            definicion = {
                "modo": "lote" if self.modo_lote else "una",
                "eje": self.eje,
                "superficie": superficie_archivo or "plantilla",
            }

        try:
            usuario = await asyncio.to_thread(ContextoUsuario.Requerir, cookie)
            importacion = await asyncio.to_thread(ServicioImports.Resolver, usuario, superficie_archivo)
            lote = await asyncio.to_thread(
                ServicioLotes.Solicitar,
                usuario,
                SolicitudLote(
                    import_id=importacion.id,
                    request_id=request_id,
                    mode="sweep" if len(variantes) > 1 else "single",
                    definition=definicion,
                    variantes=variantes,
                    auto_scale=autoescalar,
                ),
            )
        except (ValueError, OrtesisLabError, ErrorPersistencia) as exc:
            async with self:
                self.mensaje = str(exc)
                self.ocupado = False
                self._trabajando = 0
                self._solicitud = ""
            return
        except Exception:
            Registro.Obtener("web").exception("Fallo no previsto al registrar el lote")
            async with self:
                self.mensaje = "No se pudo registrar la generación."
                self.ocupado = False
                self._trabajando = 0
                self._solicitud = ""
            return

        async with self:
            self.lote_id = str(lote.id)
            self._solicitud = ""
            self.mensaje = "En cola. El trabajador construye cada variante."
        await self._Seguir(usuario, lote.id)

    @rx.event(background=True)
    async def SeguirLote(self):
        # Retoma el avance de un lote abierto tras recargar la página o reiniciar el backend.
        async with self:
            if self._trabajando or not self.lote_id:
                return
            self._trabajando = 1
            self.ocupado = True
            cookie = self.router.headers.cookie
            lote_id = uuid.UUID(self.lote_id)
        try:
            usuario = await asyncio.to_thread(ContextoUsuario.Requerir, cookie)
        except ErrorPersistencia as exc:
            async with self:
                self.mensaje = str(exc)
                self.ocupado = False
                self._trabajando = 0
            return
        await self._Seguir(usuario, lote_id)

    @rx.event
    async def CancelarLote(self):
        usuario = await self._Usuario()
        if usuario is None or not self.lote_id:
            return
        try:
            cancelado = await asyncio.to_thread(ServicioLotes.Cancelar, usuario, uuid.UUID(self.lote_id))
        except ErrorPersistencia as exc:
            self.mensaje = str(exc)
            return
        self.mensaje = "Cancelación pedida; la variante en curso termina antes de parar." if cancelado else self.mensaje

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
    async def Descargar(self, identificador: str):
        # Entrega el mismo objeto del bucket que abre el visor y deja constancia en el historial.
        ficha = next((item for item in self.resultados if item["id"] == identificador), None)
        if ficha is None or not ficha["archivo"]:
            return
        usuario = await self._Usuario()
        coincidencia = PATRON_CLAVE.search(ficha["archivo"])
        if usuario is None or coincidencia is None:
            self.mensaje = "Inicie sesión para descargar el STL."
            return
        try:
            url = await asyncio.to_thread(
                ServicioHistorial.RegistrarDescarga, usuario, uuid.UUID(coincidencia.group("asset"))
            )
        except ErrorPersistencia as exc:
            self.mensaje = str(exc)
            return
        return rx.download(url=url, filename=f"ortesis-{coincidencia.group('asset')[:8]}.stl")

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

    async def _Usuario(self) -> UsuarioAutenticado | None:
        # La identidad sale de la cookie de sesión del servidor, nunca de un campo del navegador.
        try:
            usuario = await asyncio.to_thread(ContextoUsuario.Requerir, self.router.headers.cookie)
        except SesionInvalida:
            self.autenticado = False
            self.usuario_nombre = ""
            return None
        except ErrorPersistencia as exc:
            self.mensaje = str(exc)
            return None
        self.autenticado = True
        self.usuario_nombre = usuario.display_name
        return usuario

    async def _Seguir(self, usuario: UsuarioAutenticado, lote_id: uuid.UUID) -> None:
        # Lee el lote de la base hasta que se cierra; la página no guarda la malla.
        try:
            while True:
                progreso = await asyncio.to_thread(ServicioLotes.Progreso, usuario, lote_id)
                async with self:
                    self._Publicar(progreso)
                if not progreso.abierto:
                    break
                await asyncio.sleep(INTERVALO_PROGRESO_S)
        except ErrorPersistencia as exc:
            async with self:
                self.mensaje = f"{exc} El lote sigue guardado; recargue para retomarlo."
        finally:
            async with self:
                self.ocupado = False
                self._trabajando = 0

    def _Publicar(self, progreso: ProgresoLote) -> None:
        fichas = [GeneradorWeb._FichaDeItem(item) for item in progreso.items if item.status in TERMINALES]
        self.total = progreso.lote.total_items
        self.hechos = progreso.terminados
        self.resultados = fichas
        if not self.archivo:
            visible = next((ficha for ficha in fichas if ficha["archivo"]), None)
            if visible is not None:
                self._Mostrar(visible)
        if progreso.abierto:
            if progreso.lote.status == "queued" and self.hechos == 0:
                self.mensaje = "En cola, esperando al trabajador."
            else:
                self.mensaje = f"{self.hechos} de {self.total}"
            return
        errores = sum(1 for ficha in fichas if ficha["error"])
        if progreso.lote.status == "cancelled":
            self.mensaje = f"Lote cancelado. {self.hechos} de {self.total} cerradas."
        elif errores:
            self.mensaje = f"Listo. {errores} de {len(fichas)} no se pudieron construir."
        else:
            self.mensaje = f"Listo. {len(fichas)} variante{'s' if len(fichas) != 1 else ''}."

    def _OlvidarTrabajo(self) -> None:
        self.resultados = []
        self.vistas = []
        self.archivo = ""
        self.lote_id = ""
        self.hechos = 0
        self.total = 0
        self.superficie_archivo = ""
        self.superficie_nombre = "Superficie incluida"
        self.superficie_detalle = "Plantilla incluida en el proyecto."
        self.superficie_error = ""

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
