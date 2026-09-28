"""Pantalla para previsualizar una ortesis o un lote de variantes."""

from __future__ import annotations

import reflex as rx
from reflex_base.vars.base import Var

from .EstadoApp import (
    ETIQUETAS_EJE,
    ID_SUBIDA_SUPERFICIE,
    LIMITE_LOTE,
    EstadoApp,
)
from .GeneradorWeb import PATRONES
from .LectorSuperficie import LectorSuperficie


class PaginaComparacion:
    """Formulario con los parámetros del panel y los visores del lote."""

    @staticmethod
    def Index() -> rx.Component:
        return rx.box(
            rx.color_mode.button(position="top-right"),
            rx.vstack(
                rx.heading("OrtesisLab", size="8"),
                rx.text(
                    "Previsualice una ortesis o genere varias con los parámetros del complemento. "
                    "El cascarón, el volumen, el peso y el precio salen del mismo cálculo. "
                    "La página refina la superficie para dibujar los patrones; "
                    "la reconstrucción voxel queda en Blender.",
                    size="3",
                    color_scheme="gray",
                ),
                rx.hstack(
                    PaginaComparacion.Formulario(),
                    PaginaComparacion.Vista(),
                    align="start",
                    width="100%",
                    spacing="6",
                    wrap="wrap",
                ),
                PaginaComparacion.Lote(),
                spacing="5",
                width="100%",
            ),
            padding="6",
            max_width="1200px",
            margin="0 auto",
        )

    @staticmethod
    def Formulario() -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.heading("Una ortesis", size="5"),
                PaginaComparacion.Superficie(),
                rx.separator(size="4"),
                PaginaComparacion.Selector("Patrón", EstadoApp.pattern, EstadoApp.set_pattern, list(PATRONES.items())),
                rx.cond(
                    EstadoApp.pattern == "SOLID",
                    PaginaComparacion.Campo("Espesor macizo (mm)", EstadoApp.solid_mm, EstadoApp.set_solid_mm),
                    rx.vstack(
                        PaginaComparacion.Campo("Tamaño de celda (mm)", EstadoApp.cell_mm, EstadoApp.set_cell_mm),
                        PaginaComparacion.Campo("Ancho de nervadura (mm)", EstadoApp.rib_width_mm, EstadoApp.set_rib_width_mm),
                        PaginaComparacion.Campo("Altura de nervadura (mm)", EstadoApp.rib_height_mm, EstadoApp.set_rib_height_mm),
                        PaginaComparacion.Interruptor("Capa interior continua", EstadoApp.liner, EstadoApp.set_liner),
                        rx.cond(
                            EstadoApp.liner,
                            rx.vstack(
                                PaginaComparacion.Campo("Espesor de capa interior (mm)", EstadoApp.skin_mm, EstadoApp.set_skin_mm),
                                PaginaComparacion.Campo("Transición de nervadura (mm)", EstadoApp.rounding_mm, EstadoApp.set_rounding_mm),
                                rx.text(
                                    "Espesor total en nervadura: ",
                                    EstadoApp.espesor_total,
                                    " mm",
                                    size="2",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            rx.text("Rejilla abierta: la altura es el espesor total.", size="2"),
                        ),
                        PaginaComparacion.Campo("Giro del patrón (grados)", EstadoApp.angle_deg, EstadoApp.set_angle_deg),
                        rx.cond(
                            EstadoApp.pattern == "VORONOI",
                            PaginaComparacion.Campo("Semilla del patrón orgánico", EstadoApp.seed, EstadoApp.set_seed),
                            rx.box(),
                        ),
                        PaginaComparacion.Campo("Ancho de marco perimetral (mm)", EstadoApp.border_mm, EstadoApp.set_border_mm),
                        PaginaComparacion.Campo("Ancho de banda maciza (mm)", EstadoApp.reinforce_width_mm, EstadoApp.set_reinforce_width_mm),
                        PaginaComparacion.Campo("Posición de banda, Y (mm)", EstadoApp.reinforce_y_mm, EstadoApp.set_reinforce_y_mm),
                        spacing="3",
                        width="100%",
                    ),
                ),
                rx.cond(
                    EstadoApp.pattern != "SOLID",
                    PaginaComparacion.Campo(
                        "Paso de superficie para el patrón (mm)",
                        EstadoApp.surface_step_mm,
                        EstadoApp.set_surface_step_mm,
                    ),
                    rx.box(),
                ),
                PaginaComparacion.Interruptor("Invertir lado del espesor", EstadoApp.flip_normals, EstadoApp.set_flip_normals),
                rx.text(
                    "La reconstrucción voxel solo está disponible en Blender y está ",
                    rx.cond(EstadoApp.repair, "activada", "desactivada"),
                    ", resolución ",
                    EstadoApp.resolution_mm,
                    " mm.",
                    size="2",
                    color_scheme="gray",
                ),
                rx.button(
                    "Previsualizar",
                    on_click=EstadoApp.Previsualizar,
                    loading=EstadoApp.ocupado,
                    disabled=EstadoApp.ocupado,
                    size="3",
                ),
                rx.text(EstadoApp.mensaje, size="2"),
                spacing="3",
                width="100%",
            ),
            width="100%",
            max_width="420px",
        )

    @staticmethod
    def Superficie() -> rx.Component:
        return rx.vstack(
            rx.text("Superficie de entrada", size="2", weight="medium"),
            PaginaComparacion.Interruptor(
                "Autoescalar a milímetros",
                EstadoApp.autoescalar_superficie,
                EstadoApp.set_autoescalar_superficie,
            ),
            rx.text(EstadoApp.aviso_escala, size="1", color_scheme="gray"),
            rx.upload(
                rx.vstack(
                    rx.icon("upload", size=24),
                    rx.text("Arrastre un STL o NPZ, o haga clic para elegirlo.", size="2"),
                    rx.foreach(
                        rx.selected_files(ID_SUBIDA_SUPERFICIE),
                        lambda nombre: rx.badge(nombre, variant="soft"),
                    ),
                    spacing="2",
                    align="center",
                ),
                id=ID_SUBIDA_SUPERFICIE,
                accept={
                    "model/stl": [".stl"],
                    "application/octet-stream": [".stl", ".npz"],
                },
                max_files=1,
                max_size=LectorSuperficie.MAXIMO_BYTES,
                multiple=False,
                border="1px dashed var(--gray-7)",
                border_radius="10px",
                padding="4",
                width="100%",
                cursor="pointer",
            ),
            rx.hstack(
                rx.button(
                    "Cargar archivo",
                    on_click=EstadoApp.CargarSuperficie(
                        rx.upload_files(upload_id=ID_SUBIDA_SUPERFICIE)
                    ),
                    loading=EstadoApp.subiendo_superficie,
                    disabled=EstadoApp.ocupado | EstadoApp.subiendo_superficie,
                    size="2",
                ),
                rx.button(
                    "Usar incluida",
                    on_click=EstadoApp.UsarSuperficieIncluida,
                    disabled=EstadoApp.ocupado | EstadoApp.subiendo_superficie,
                    size="2",
                    variant="soft",
                ),
                spacing="2",
            ),
            rx.vstack(
                rx.text(EstadoApp.superficie_nombre, size="2", weight="bold"),
                rx.text(EstadoApp.superficie_detalle, size="1", color_scheme="gray"),
                rx.cond(
                    EstadoApp.superficie_error != "",
                    rx.text(EstadoApp.superficie_error, size="1", color_scheme="red"),
                    rx.box(),
                ),
                spacing="1",
                width="100%",
            ),
            spacing="2",
            width="100%",
        )

    @staticmethod
    def Vista() -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.heading("Vista previa", size="5"),
                rx.cond(
                    EstadoApp.archivo != "",
                    rx.vstack(
                        PaginaComparacion.Visor(EstadoApp.archivo, "560px"),
                        rx.text(EstadoApp.ficha_detalle, size="2", weight="medium"),
                        rx.hstack(
                            PaginaComparacion.Medida("Volumen", EstadoApp.ficha_volumen),
                            PaginaComparacion.Medida("Peso PETG", EstadoApp.ficha_peso),
                            PaginaComparacion.Medida("Precio", EstadoApp.ficha_precio),
                            spacing="4",
                            wrap="wrap",
                        ),
                        rx.text(
                            "PETG a 0,15 por gramo. La moneda no está declarada en el material. "
                            "El volumen es el del cascarón, antes del voxel, y no predice el filamento ni la resistencia.",
                            size="1",
                            color_scheme="gray",
                        ),
                        rx.cond(
                            EstadoApp.ficha_error != "",
                            rx.text(EstadoApp.ficha_error, size="2", color_scheme="red"),
                            rx.box(),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.center(
                        rx.text("La malla aparece aquí al pulsar Previsualizar.", size="2", color_scheme="gray"),
                        min_height="560px",
                        width="100%",
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            flex="1",
            min_width="320px",
        )

    @staticmethod
    def Lote() -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.heading("Varias a la vez", size="5"),
                rx.text(
                    f"Elija patrones y, si quiere, un parámetro que cambie de un valor a otro. "
                    f"El lote admite hasta {LIMITE_LOTE} variantes.",
                    size="2",
                    color_scheme="gray",
                ),
                rx.hstack(
                    PaginaComparacion.Interruptor("Orgánico / Voronoi", EstadoApp.usar_voronoi, EstadoApp.set_usar_voronoi),
                    PaginaComparacion.Interruptor("Hexagonal", EstadoApp.usar_hex, EstadoApp.set_usar_hex),
                    PaginaComparacion.Interruptor("Rombos", EstadoApp.usar_diamond, EstadoApp.set_usar_diamond),
                    PaginaComparacion.Interruptor("Cuadrícula", EstadoApp.usar_square, EstadoApp.set_usar_square),
                    PaginaComparacion.Interruptor("Macizo", EstadoApp.usar_solid, EstadoApp.set_usar_solid),
                    wrap="wrap",
                    spacing="4",
                ),
                PaginaComparacion.Selector("Parámetro a variar", EstadoApp.eje, EstadoApp.set_eje, ETIQUETAS_EJE),
                rx.cond(
                    EstadoApp.eje != "ninguno",
                    rx.hstack(
                        PaginaComparacion.Campo("Desde", EstadoApp.desde, EstadoApp.set_desde),
                        PaginaComparacion.Campo("Hasta", EstadoApp.hasta, EstadoApp.set_hasta),
                        PaginaComparacion.Campo("Cada", EstadoApp.paso, EstadoApp.set_paso),
                        spacing="3",
                        width="100%",
                        align="start",
                    ),
                    rx.box(),
                ),
                PaginaComparacion.Interruptor(
                    "Probar con capa continua y sin ella",
                    EstadoApp.ambos_revestimientos,
                    EstadoApp.set_ambos_revestimientos,
                ),
                rx.button(
                    "Generar lote",
                    on_click=EstadoApp.PedirLote,
                    loading=EstadoApp.ocupado,
                    disabled=EstadoApp.ocupado,
                    size="3",
                    variant="soft",
                ),
                rx.cond(
                    EstadoApp.total > 0,
                    rx.progress(value=EstadoApp.porcentaje, width="100%"),
                    rx.box(),
                ),
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Patrón"),
                                rx.table.column_header_cell("Parámetros"),
                                rx.table.column_header_cell("Volumen"),
                                rx.table.column_header_cell("Peso"),
                                rx.table.column_header_cell("Precio"),
                                rx.table.column_header_cell("Aviso"),
                                rx.table.column_header_cell(""),
                            ),
                        ),
                        rx.table.body(rx.foreach(EstadoApp.resultados, PaginaComparacion.Fila)),
                        width="100%",
                    ),
                    overflow_x="auto",
                    width="100%",
                ),
                rx.cond(
                    EstadoApp.vistas.length() > 0,
                    rx.vstack(
                        rx.heading("Comparación", size="4"),
                        rx.hstack(
                            rx.foreach(EstadoApp.vistas, PaginaComparacion.Marco),
                            align="start",
                            width="100%",
                            spacing="4",
                            wrap="wrap",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.box(),
                ),
                spacing="4",
                width="100%",
            ),
            width="100%",
        )

    @staticmethod
    def Fila(ficha) -> rx.Component:
        return rx.table.row(
            rx.table.cell(ficha["patron"]),
            rx.table.cell(ficha["detalle"]),
            rx.table.cell(ficha["volumen"]),
            rx.table.cell(ficha["peso"]),
            rx.table.cell(ficha["precio"]),
            rx.table.cell(ficha["error"]),
            rx.table.cell(
                rx.hstack(
                    rx.button("Ver", size="1", on_click=EstadoApp.Ver(ficha["id"]), disabled=ficha["archivo"] == ""),
                    rx.button(
                        "Comparar",
                        size="1",
                        variant="soft",
                        on_click=EstadoApp.Comparar(ficha["id"]),
                        disabled=ficha["archivo"] == "",
                    ),
                    rx.button(
                        "STL",
                        size="1",
                        variant="outline",
                        on_click=EstadoApp.Descargar(ficha["id"]),
                        disabled=ficha["archivo"] == "",
                    ),
                    spacing="2",
                )
            ),
        )

    @staticmethod
    def Marco(archivo) -> rx.Component:
        return rx.box(PaginaComparacion.Visor(archivo, "320px"), flex="1", min_width="260px")

    @staticmethod
    def Visor(archivo, alto: str) -> rx.Component:
        # El iframe carga el STL desde el backend. El HTML del visor está en assets.
        return rx.el.iframe(
            src=PaginaComparacion.Enlace(archivo),
            title="Vista previa de la ortesis",
            width="100%",
            height=alto,
            border_radius="12px",
            border="0",
        )

    @staticmethod
    def Enlace(archivo):
        url = rx.get_upload_url(archivo)
        expresion = f"`/visor.html?src=${{encodeURIComponent({url})}}`"
        return Var(_js_expr=expresion, _var_type=str, _var_data=url._get_all_var_data())

    @staticmethod
    def Campo(etiqueta: str, valor, cambio) -> rx.Component:
        return rx.vstack(
            rx.text(etiqueta, size="2", weight="medium", as_="label"),
            rx.input(value=valor, on_change=cambio, type="number", width="100%"),
            spacing="1",
            width="100%",
        )

    @staticmethod
    def Interruptor(etiqueta: str, valor, cambio) -> rx.Component:
        return rx.hstack(
            rx.switch(checked=valor, on_change=cambio),
            rx.text(etiqueta, size="2"),
            spacing="2",
            align="center",
        )

    @staticmethod
    def Selector(etiqueta: str, valor, cambio, opciones: list[tuple[str, str]]) -> rx.Component:
        return rx.vstack(
            rx.text(etiqueta, size="2", weight="medium"),
            rx.select.root(
                rx.select.trigger(width="100%"),
                rx.select.content(
                    *[rx.select.item(texto, value=codigo) for codigo, texto in opciones],
                ),
                value=valor,
                on_change=cambio,
                size="2",
            ),
            spacing="1",
            width="100%",
        )

    @staticmethod
    def Medida(etiqueta: str, valor) -> rx.Component:
        return rx.vstack(
            rx.text(etiqueta, size="1", color_scheme="gray"),
            rx.text(valor, size="4", weight="bold"),
            spacing="1",
        )
