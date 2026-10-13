"""Estado de /historial: filtros, cursor y comparación de hasta tres versiones.

Cada evento vuelve a resolver el usuario desde la cookie de sesión; la página
solo guarda identificadores y textos ya formateados.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime, time, timezone

import reflex as rx

from GenerateModelsApp.util.Utilidades import Registro

from .ConfiguracionBackend import ConfiguracionBackend
from .enums import EstadoExport, EstadoItem
from .GeneradorWeb import PATRONES, GeneradorWeb
from .persistence.Contratos import (
    DetalleVersion,
    ErrorPersistencia,
    FilaHistorial,
    SesionInvalida,
    UsuarioAutenticado,
)
from .services.ContextoUsuario import ContextoUsuario
from .services.ServicioHistorial import MAXIMO_COMPARACION, ServicioHistorial
from .storage.AlmacenamientoPrivado import PATRON_CLAVE

ESTADOS_VISIBLES = ConfiguracionBackend.Cargar("web")["estados_visibles"]
TODOS = "todos"


class EstadoHistorial(rx.State):
    """Listado paginado del trabajo del usuario y comparación de versiones."""

    autenticado: bool = False
    usuario_nombre: str = ""
    cargando: bool = False
    mensaje: str = ""
    filtro_patron: str = TODOS
    filtro_estado: str = TODOS
    filtro_desde: str = ""
    filtro_hasta: str = ""
    filas: list[dict[str, str]] = []
    pagina: int = 1
    hay_siguiente: bool = False
    seleccion: list[str] = []
    comparacion: list[dict[str, str]] = []
    _cursores: list[str] = []
    _siguiente: str = ""

    @rx.event
    def set_filtro_patron(self, valor: str):
        self.filtro_patron = valor

    @rx.event
    def set_filtro_estado(self, valor: str):
        self.filtro_estado = valor

    @rx.event
    def set_filtro_desde(self, valor: str):
        self.filtro_desde = valor

    @rx.event
    def set_filtro_hasta(self, valor: str):
        self.filtro_hasta = valor

    @rx.event
    async def Cargar(self):
        self._cursores = [""]
        self.pagina = 1
        self.seleccion = []
        self.comparacion = []
        await self._Leer()

    @rx.event
    async def Siguiente(self):
        if not self._siguiente:
            return
        self._cursores = [*self._cursores, self._siguiente]
        self.pagina = len(self._cursores)
        await self._Leer()

    @rx.event
    async def Anterior(self):
        if len(self._cursores) <= 1:
            return
        self._cursores = self._cursores[:-1]
        self.pagina = len(self._cursores)
        await self._Leer()

    @rx.event
    async def Seleccionar(self, version_id: str):
        # Un segundo clic quita la versión; el máximo es el mismo que el del servicio.
        if version_id in self.seleccion:
            self.seleccion = [v for v in self.seleccion if v != version_id]
        elif len(self.seleccion) >= MAXIMO_COMPARACION:
            self.mensaje = f"Compare hasta {MAXIMO_COMPARACION} versiones a la vez."
            return
        else:
            self.seleccion = [*self.seleccion, version_id]
        await self._Comparar()

    @rx.event
    async def Restaurar(self, version_id: str):
        usuario = await self._Usuario()
        if usuario is None:
            return
        try:
            await asyncio.to_thread(ServicioHistorial.Restaurar, usuario, uuid.UUID(version_id))
        except (ValueError, ErrorPersistencia) as exc:
            self.mensaje = str(exc)
            return
        return rx.redirect("/")

    @rx.event
    async def Reintentar(self, version_id: str):
        usuario = await self._Usuario()
        if usuario is None:
            return
        try:
            await asyncio.to_thread(ServicioHistorial.Reintentar, usuario, [uuid.UUID(version_id)])
        except (ValueError, ErrorPersistencia) as exc:
            self.mensaje = str(exc)
            return
        return rx.redirect("/")

    @rx.event
    async def Descargar(self, fila_id: str):
        fila = next((f for f in self.filas if f["item_id"] == fila_id), None)
        if fila is None or not fila["asset_id"]:
            return
        usuario = await self._Usuario()
        if usuario is None:
            return
        try:
            url = await asyncio.to_thread(ServicioHistorial.RegistrarDescarga, usuario, uuid.UUID(fila["asset_id"]))
        except ErrorPersistencia as exc:
            self.mensaje = str(exc)
            return
        return rx.download(url=url, filename=f"ortesis-v{fila['version']}.stl")

    async def _Usuario(self) -> UsuarioAutenticado | None:
        try:
            usuario = await asyncio.to_thread(ContextoUsuario.Requerir, self.router.headers.cookie)
        except SesionInvalida as exc:
            self.autenticado = False
            self.usuario_nombre = ""
            self.filas = []
            self.seleccion = []
            self.comparacion = []
            self.hay_siguiente = False
            self.mensaje = str(exc)
            return None
        except ErrorPersistencia as exc:
            self.mensaje = str(exc)
            return None
        self.autenticado = True
        self.usuario_nombre = usuario.display_name
        return usuario

    async def _Leer(self) -> None:
        usuario = await self._Usuario()
        if usuario is None:
            return
        try:
            filtros = self._Filtros()
        except ValueError as exc:
            self.mensaje = str(exc)
            return
        self.cargando = True
        try:
            pagina = await asyncio.to_thread(
                ServicioHistorial.Listar, usuario, filtros, self._cursores[-1] or None
            )
        except (ValueError, ErrorPersistencia) as exc:
            self.mensaje = str(exc)
            return
        except Exception:
            Registro.Obtener("web").exception("Fallo al leer el historial")
            self.mensaje = "No se pudo leer el historial."
            return
        finally:
            self.cargando = False
        self.filas = [EstadoHistorial._Fila(fila) for fila in pagina.filas]
        self._siguiente = pagina.cursor_siguiente or ""
        self.hay_siguiente = bool(pagina.cursor_siguiente)
        self.mensaje = "" if self.filas else "No hay generaciones con esos filtros."

    async def _Comparar(self) -> None:
        if not self.seleccion:
            self.comparacion = []
            return
        usuario = await self._Usuario()
        if usuario is None:
            return
        try:
            detalles = await asyncio.to_thread(
                ServicioHistorial.Comparar, usuario, [uuid.UUID(v) for v in self.seleccion]
            )
        except (ValueError, ErrorPersistencia) as exc:
            self.mensaje = str(exc)
            return
        base = detalles[0].version.parameters
        self.comparacion = [EstadoHistorial._Tarjeta(detalle, base) for detalle in detalles]

    def _Filtros(self) -> dict:
        return {
            "pattern": "" if self.filtro_patron == TODOS else self.filtro_patron,
            "status": "" if self.filtro_estado == TODOS else self.filtro_estado,
            "desde": EstadoHistorial._Fecha(self.filtro_desde, time.min),
            "hasta": EstadoHistorial._Fecha(self.filtro_hasta, time.max),
        }

    @staticmethod
    def _Fecha(texto: str, hora: time) -> datetime | None:
        if not texto.strip():
            return None
        try:
            return datetime.combine(date.fromisoformat(texto.strip()), hora, tzinfo=timezone.utc)
        except ValueError as exc:
            raise ValueError("Las fechas del filtro tienen que tener formato AAAA-MM-DD.") from exc

    @staticmethod
    def _Fila(fila: FilaHistorial) -> dict[str, str]:
        url = fila.stl_url if fila.stl_status == EstadoExport.READY and fila.stl_url else ""
        aviso = fila.error_message or ""
        if fila.status == EstadoItem.SUCCEEDED and not url:
            aviso = "El STL ya no está en el almacén."
        coincidencia = PATRON_CLAVE.search(url) if url else None
        return {
            "item_id": str(fila.item_id),
            "version_id": str(fila.version_id),
            "version": str(fila.version_number),
            "proyecto": fila.project_name,
            "fecha": fila.created_at.astimezone().strftime("%Y-%m-%d %H:%M"),
            "patron": PATRONES.get(fila.pattern, fila.pattern),
            "detalle": GeneradorWeb.Detalle(fila.parameters),
            "estado": ESTADOS_VISIBLES.get(fila.status, fila.status),
            "volumen": "" if fila.volume_mm3 is None else f"{GeneradorWeb.Numero(fila.volume_mm3, 1)} mm³",
            "peso": "" if fila.weight_g is None else f"{GeneradorWeb.Numero(fila.weight_g, 2)} g",
            "precio": "" if fila.estimated_price is None else GeneradorWeb.Numero(float(fila.estimated_price), 2),
            "url": url,
            "asset_id": coincidencia.group("asset") if coincidencia else "",
            "aviso": aviso[:180],
        }

    @staticmethod
    def _Tarjeta(detalle: DetalleVersion, base: dict) -> dict[str, str]:
        version = detalle.version
        resultado = next(
            (r for r in reversed(detalle.resultados) if r.stl_status == EstadoExport.READY and r.stl_url), None
        )
        cambios = [
            f"{clave}: {base.get(clave)} → {valor}"
            for clave, valor in sorted(version.parameters.items())
            if base.get(clave) != valor
        ]
        ultimo = detalle.intentos[-1] if detalle.intentos else None
        return {
            "version_id": str(version.id),
            "titulo": f"Versión {version.version_number}",
            "detalle": GeneradorWeb.Detalle(version.parameters),
            "cambios": "; ".join(cambios) if cambios else "Parámetros de referencia.",
            "url": resultado.stl_url if resultado else "",
            "volumen": f"{GeneradorWeb.Numero(resultado.volume_mm3, 1)} mm³" if resultado else "",
            "peso": f"{GeneradorWeb.Numero(resultado.weight_g, 2)} g" if resultado else "",
            "precio": GeneradorWeb.Numero(float(resultado.estimated_price), 2) if resultado else "",
            "intentos": (
                f"{len(detalle.intentos)} intento(s); último: {ultimo.status}" if ultimo else "Sin intentos."
            ),
            "nota": version.change_note or "",
        }
