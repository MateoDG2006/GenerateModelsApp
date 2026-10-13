"""Pantalla /historial: generaciones del usuario, comparación y restauración."""

from __future__ import annotations

import reflex as rx

from .EstadoHistorial import ESTADOS_VISIBLES, TODOS, EstadoHistorial
from .GeneradorWeb import PATRONES
from .PaginaComparacion import PaginaComparacion
from .Sesion import Sesion


class PaginaHistorial:
    """Filtros, tabla paginada por cursor y visores de las versiones elegidas."""

    @staticmethod
    def Index() -> rx.Component:
        return rx.box(
            rx.color_mode.button(position="top-right"),
            rx.vstack(
                Sesion.Barra(EstadoHistorial.autenticado, EstadoHistorial.usuario_nombre),
                rx.heading("Historial", size="8"),
                rx.text(
                    "Cada generación queda como una versión con sus parámetros, métricas y STL. "
                    "Restaurar crea una versión nueva; la original no cambia.",
                    size="3",
                    color_scheme="gray",
                ),
                PaginaHistorial.Filtros(),
                rx.cond(EstadoHistorial.mensaje != "", rx.callout(EstadoHistorial.mensaje, size="1"), rx.box()),
                PaginaHistorial.Tabla(),
                PaginaHistorial.Comparacion(),
                spacing="5",
                width="100%",
            ),
            padding="6",
            max_width="1200px",
            margin="0 auto",
        )

    @staticmethod
    def Filtros() -> rx.Component:
        return rx.card(
            rx.hstack(
                rx.box(
                    PaginaComparacion.Selector(
                        "Patrón",
                        EstadoHistorial.filtro_patron,
                        EstadoHistorial.set_filtro_patron,
                        [(TODOS, "Todos"), *PATRONES.items()],
                    ),
                    width="200px",
                ),
                rx.box(
                    PaginaComparacion.Selector(
                        "Estado",
                        EstadoHistorial.filtro_estado,
                        EstadoHistorial.set_filtro_estado,
                        [(TODOS, "Todos"), *ESTADOS_VISIBLES.items()],
                    ),
                    width="160px",
                ),
                PaginaHistorial.Fecha("Desde", EstadoHistorial.filtro_desde, EstadoHistorial.set_filtro_desde),
                PaginaHistorial.Fecha("Hasta", EstadoHistorial.filtro_hasta, EstadoHistorial.set_filtro_hasta),
                rx.button("Filtrar", on_click=EstadoHistorial.Cargar, loading=EstadoHistorial.cargando),
                align="end",
                spacing="4",
                wrap="wrap",
                width="100%",
            ),
            width="100%",
        )

    @staticmethod
    def Fecha(etiqueta: str, valor, cambio) -> rx.Component:
        return rx.vstack(
            rx.text(etiqueta, size="2", weight="medium", as_="label"),
            rx.input(value=valor, on_change=cambio, type="date"),
            spacing="1",
        )

    @staticmethod
    def Tabla() -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Versión"),
                                rx.table.column_header_cell("Fecha"),
                                rx.table.column_header_cell("Patrón"),
                                rx.table.column_header_cell("Parámetros"),
                                rx.table.column_header_cell("Estado"),
                                rx.table.column_header_cell("Volumen"),
                                rx.table.column_header_cell("Peso"),
                                rx.table.column_header_cell("Precio"),
                                rx.table.column_header_cell(""),
                            ),
                        ),
                        rx.table.body(rx.foreach(EstadoHistorial.filas, PaginaHistorial.Fila)),
                        width="100%",
                    ),
                    overflow_x="auto",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Anterior",
                        size="1",
                        variant="soft",
                        on_click=EstadoHistorial.Anterior,
                        disabled=EstadoHistorial.pagina <= 1,
                    ),
                    rx.text("Página ", EstadoHistorial.pagina, size="2"),
                    rx.button(
                        "Siguiente",
                        size="1",
                        variant="soft",
                        on_click=EstadoHistorial.Siguiente,
                        disabled=~EstadoHistorial.hay_siguiente,
                    ),
                    align="center",
                    spacing="3",
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
        )

    @staticmethod
    def Fila(fila) -> rx.Component:
        elegida = EstadoHistorial.seleccion.contains(fila["version_id"])
        return rx.table.row(
            rx.table.cell(fila["version"]),
            rx.table.cell(fila["fecha"]),
            rx.table.cell(fila["patron"]),
            rx.table.cell(rx.vstack(rx.text(fila["detalle"], size="1"), rx.text(fila["aviso"], size="1", color_scheme="red"))),
            rx.table.cell(fila["estado"]),
            rx.table.cell(fila["volumen"]),
            rx.table.cell(fila["peso"]),
            rx.table.cell(fila["precio"]),
            rx.table.cell(
                rx.hstack(
                    rx.button(
                        rx.cond(elegida, "Quitar", "Comparar"),
                        size="1",
                        variant=rx.cond(elegida, "solid", "soft"),
                        on_click=EstadoHistorial.Seleccionar(fila["version_id"]),
                    ),
                    rx.button(
                        "Restaurar",
                        size="1",
                        variant="outline",
                        on_click=EstadoHistorial.Restaurar(fila["version_id"]),
                    ),
                    rx.button(
                        "Reintentar",
                        size="1",
                        variant="outline",
                        on_click=EstadoHistorial.Reintentar(fila["version_id"]),
                    ),
                    rx.button(
                        "STL",
                        size="1",
                        variant="outline",
                        on_click=EstadoHistorial.Descargar(fila["item_id"]),
                        disabled=fila["url"] == "",
                    ),
                    spacing="2",
                )
            ),
        )

    @staticmethod
    def Comparacion() -> rx.Component:
        return rx.cond(
            EstadoHistorial.comparacion.length() > 0,
            rx.vstack(
                rx.heading("Comparación de versiones", size="5"),
                rx.hstack(
                    rx.foreach(EstadoHistorial.comparacion, PaginaHistorial.Tarjeta),
                    align="start",
                    spacing="4",
                    wrap="wrap",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            rx.box(),
        )

    @staticmethod
    def Tarjeta(tarjeta) -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.heading(tarjeta["titulo"], size="4"),
                rx.cond(
                    tarjeta["url"] != "",
                    PaginaComparacion.Visor(tarjeta["url"], "300px"),
                    rx.center(rx.text("Sin STL disponible.", size="2", color_scheme="gray"), min_height="120px"),
                ),
                rx.text(tarjeta["detalle"], size="2", weight="medium"),
                rx.text(tarjeta["cambios"], size="1", color_scheme="gray"),
                rx.hstack(
                    PaginaComparacion.Medida("Volumen", tarjeta["volumen"]),
                    PaginaComparacion.Medida("Peso", tarjeta["peso"]),
                    PaginaComparacion.Medida("Precio", tarjeta["precio"]),
                    spacing="4",
                    wrap="wrap",
                ),
                rx.text(tarjeta["intentos"], size="1"),
                rx.text(tarjeta["nota"], size="1", color_scheme="gray"),
                spacing="2",
                width="100%",
            ),
            flex="1",
            min_width="280px",
        )
