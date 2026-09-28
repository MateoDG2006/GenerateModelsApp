"""Panel N y operadores de OrtesisLab en la vista 3D.

execute, invoke y draw conservan ese nombre: Blender los llama así.
"""

from .ApiBlender import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
    bpy,
)
from .Excepciones import ConfiguracionInvalida, ModeloNoGenerado, OrtesisLabError
from .Exportacion import ExportadorStl
from .Objeto import GeneradorObjeto
from .ReparacionMalla import ReparadorMalla
from .Superficie import SuperficieInterior
from .ValidacionMalla import ValidadorMalla
from .constants.Nombres import ARCHIVO_STL_DEFECTO, RESULT, PROP_ROL, ROL_RESULTADO
from .util.Utilidades import Configuracion, Registro

ESTADO_LISTO = "Listo para generar"
ESTADO_ACTUALIZADO = "Modelo actualizado; valide antes de exportar."
ESTADO_MALLA_OK = "Pared sólida y conectada; geometría válida"
AVISO_ALCANCE = "Modifica geometría; no evalúa resistencia."


class PanelAyuda:
    """Lee los controles del panel y muestra los errores en la interfaz."""

    @staticmethod
    def OrigenAutoescala(context):
        # La preferencia del complemento manda cuando Blender lo tiene instalado.
        # Si se ejecuta desde el repositorio, vale la casilla de la escena.
        registro = context.preferences.addons.get("GenerateModelsApp")
        if registro is not None and hasattr(registro.preferences, "auto_scale"):
            return registro.preferences
        return context.scene.ortesislab

    @staticmethod
    def AvisarEscala(operador, ajustes, *, aplicada: bool) -> None:
        from .Superficie import SuperficieInterior

        diagnostico = SuperficieInterior.diagnostico_escala
        factor = float(diagnostico.get("factor", 1))
        if factor != 1.0:
            verbo = "Escala corregida" if aplicada else "Al generar se aplicará"
            texto = (
                f"{verbo} x{factor:g}: "
                f"{diagnostico['dimension_antes_mm']:.2f} a "
                f"{diagnostico['dimension_despues_mm']:.2f} mm."
            )
            ajustes.status = texto
            operador.report({"WARNING"}, texto)
            return
        if diagnostico.get("advertencia"):
            ajustes.status = diagnostico["advertencia"]
            operador.report({"WARNING"}, diagnostico["advertencia"])

    @staticmethod
    def OpcionesDesdeAjustes(ajustes) -> dict:
        # Copia cada parámetro del panel. Las claves coinciden con el JSON.
        opciones = {}
        for clave in Configuracion.ParametrosDefecto():
            if not hasattr(ajustes, clave):
                raise ConfiguracionInvalida(f"El ajuste '{clave}' no está en el panel.")
            opciones[clave] = getattr(ajustes, clave)
        return opciones

    @staticmethod
    def Cancelar(operador, ajustes, exc: Exception):
        # Pinta el error en el panel. Si no estaba previsto, guarda también la traza.
        if not isinstance(exc, OrtesisLabError):
            Registro.Obtener("interfaz").exception("Fallo no previsto en %s", operador.bl_idname)
        operador.report({"ERROR"}, str(exc))
        if ajustes is not None:
            ajustes.status = str(exc)
        return {"CANCELLED"}


class OL_Preferences(bpy.types.AddonPreferences):
    # Edit > Preferences > Add-ons > OrtesisLab. Persiste al cerrar Blender.
    bl_idname = "GenerateModelsApp"
    auto_scale: BoolProperty(
        name="Autoescalar a milímetros",
        default=True,
        description=(
            "Al generar y al arreglar, corrige factores decimales evidentes. "
            "Desactívelo para conservar las dimensiones del archivo"
        ),
    )

    def draw(self, context):
        self.layout.prop(self, "auto_scale")


class OL_Settings(bpy.types.PropertyGroup):
    # Valores que el usuario edita en la pestaña Ortesis. No regeneran solos.
    source: PointerProperty(name="Superficie sin espesor", type=bpy.types.Object,
                            poll=lambda self, obj: obj.type == 'MESH' and obj.name != RESULT and obj.get(PROP_ROL) != ROL_RESULTADO)
    auto_scale: BoolProperty(
        name="Autoescalar a milímetros",
        default=True,
        description=(
            "Al generar y al arreglar, corrige factores decimales evidentes. "
            "Desactívelo para conservar las dimensiones del archivo"
        ),
    )
    flip_normals: BoolProperty(name="Generar hacia dentro (invertir)", default=False,
                              description="Desactivado añade material hacia fuera, siguiendo las normales")
    surface_step_mm: FloatProperty(name="Paso de superficie (mm)", default=1.0, min=0.15, max=5,
                                  description="Subdivide una copia para definir el patrón; conserva caras y contornos de la base")
    pattern: EnumProperty(
        name="Patrón",
        items=[
            ("VORONOI", "Orgánico / Voronoi", ""),
            ("HEX", "Hexagonal", ""),
            ("DIAMOND", "Rombos", ""),
            ("SQUARE", "Cuadrícula", ""),
            ("SOLID", "Macizo", ""),
        ],
        default="VORONOI",
    )
    cell_mm: FloatProperty(name="Tamaño de celda (mm)", default=15, min=5, max=40)
    rib_width_mm: FloatProperty(name="Ancho de nervadura (mm)", default=2.8, min=1.2, max=10)
    rib_height_mm: FloatProperty(name="Altura de nervadura (mm)", default=1.4, min=0.3, max=6)
    liner: BoolProperty(name="Capa interior continua", default=True)
    skin_mm: FloatProperty(name="Espesor de capa interior (mm)", default=1.0, min=0.3, max=5)
    solid_mm: FloatProperty(name="Espesor macizo (mm)", default=2.4, min=0.5, max=8)
    border_mm: FloatProperty(name="Ancho de marco perimetral (mm)", default=4, min=0, max=15)
    rounding_mm: FloatProperty(name="Transición de nervadura (mm)", default=0.8, min=0, max=3)
    angle_deg: FloatProperty(name="Giro del patrón (grados)", default=0, min=-180, max=180)
    seed: IntProperty(name="Semilla del patrón orgánico", default=7, min=0, max=99999)
    reinforce_y_mm: FloatProperty(name="Posición de banda, Y (mm)", default=0, min=-250, max=250)
    reinforce_width_mm: FloatProperty(name="Ancho de banda maciza (mm)", default=0, min=0, max=60)
    repair: BoolProperty(
        name="Reconstrucción voxel (opcional)",
        default=False,
        description="Aproxima la pared; puede alterar huecos estrechos. Desactivada conserva la superficie y sus aberturas",
    )
    resolution_mm: FloatProperty(
        name="Resolución geométrica (mm)",
        default=0.3,
        min=0.15,
        max=0.8,
        description="Menor valor: más detalle, más polígonos y más tiempo",
    )
    status: StringProperty(default=ESTADO_LISTO)


class OL_OT_generate(bpy.types.Operator):
    # Botón Generar / actualizar.
    bl_idname = "ortesislab.generate"
    bl_label = "Generar / actualizar"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ajustes = context.scene.ortesislab
        try:
            if ajustes.source is None:
                ajustes.source = context.active_object
            Registro.Obtener("interfaz").info(
                "Generación pedida para %s", getattr(ajustes.source, "name", "sin nombre")
            )
            opciones = PanelAyuda.OpcionesDesdeAjustes(ajustes)
            opciones["autoescalar"] = bool(PanelAyuda.OrigenAutoescala(context).auto_scale)
            GeneradorObjeto.Crear(ajustes.source, **opciones)
            ajustes.status = ESTADO_ACTUALIZADO
            PanelAyuda.AvisarEscala(self, ajustes, aplicada=True)
            return {"FINISHED"}
        except Exception as exc:
            return PanelAyuda.Cancelar(self, ajustes, exc)


class OL_OT_use_surface(bpy.types.Operator):
    bl_idname = "ortesislab.use_surface"
    bl_label = "Usar malla seleccionada"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ajustes = context.scene.ortesislab
        try:
            fuente = context.active_object
            SuperficieInterior.Leer(
                fuente,
                autoescalar=bool(PanelAyuda.OrigenAutoescala(context).auto_scale),
            )
            ajustes.source = fuente
            ajustes.status = "Superficie seleccionada; lista para engrosar."
            PanelAyuda.AvisarEscala(self, ajustes, aplicada=False)
            return {"FINISHED"}
        except Exception as exc:
            return PanelAyuda.Cancelar(self, ajustes, exc)


class OL_OT_repair_surface(bpy.types.Operator):
    # Limpia la selección sin añadir espesor ni cerrar sus aberturas.
    bl_idname = "ortesislab.repair_surface"
    bl_label = "Arreglar malla seleccionada"
    bl_description = (
        "Une duplicados, quita geometría suelta y fragmentos, triangula y recalcula normales; "
        "la entrada debe ser una sola capa de caras"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        objeto = context.active_object
        return objeto is not None and objeto.type == "MESH"

    def execute(self, context):
        ajustes = context.scene.ortesislab
        try:
            fuente = context.active_object
            resumen = ReparadorMalla.Arreglar(
                fuente,
                autoescalar=bool(PanelAyuda.OrigenAutoescala(context).auto_scale),
            )
            ajustes.source = fuente
            if resumen["factor_escala"] != 1.0:
                texto = (
                    f"Escala corregida x{resumen['factor_escala']:g}: "
                    f"{resumen['dimension_antes_mm']:.2f} a "
                    f"{resumen['dimension_despues_mm']:.2f} mm."
                )
                ajustes.status = texto
                self.report({"WARNING"}, texto)
            elif resumen["advertencia_escala"]:
                ajustes.status = resumen["advertencia_escala"]
                self.report({"WARNING"}, resumen["advertencia_escala"])
            else:
                ajustes.status = "Malla arreglada; escala en rango."
                texto = (
                    f"Malla arreglada: {resumen['fusionados']} vértices unidos, "
                    f"{resumen['fragmentos']} fragmentos retirados."
                )
                self.report({"INFO"}, texto)
            return {"FINISHED"}
        except Exception as exc:
            return PanelAyuda.Cancelar(self, ajustes, exc)


class OL_OT_validate(bpy.types.Operator):
    # Botón Comprobar malla. Un informe malo es un aviso, no una cancelación.
    bl_idname = "ortesislab.validate"
    bl_label = "Comprobar malla"

    def execute(self, context):
        ajustes = context.scene.ortesislab
        try:
            objeto = bpy.data.objects.get(RESULT)
            if objeto is None:
                raise ModeloNoGenerado()
            informe = ValidadorMalla.Comprobar(objeto)
            ajustes.status = ESTADO_MALLA_OK if informe["ok"] else "Revisar geometría: " + str(informe)
            self.report({"INFO"} if informe["ok"] else {"WARNING"}, ajustes.status)
            return {"FINISHED"}
        except Exception as exc:
            return PanelAyuda.Cancelar(self, ajustes, exc)


class OL_OT_export(bpy.types.Operator):
    # Botón Exportar STL en mm. Abre el selector de archivo.
    bl_idname = "ortesislab.export"
    bl_label = "Exportar STL en mm"
    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.stl", options={"HIDDEN"})

    def invoke(self, context, event):
        self.filepath = bpy.path.abspath(ARCHIVO_STL_DEFECTO)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        try:
            objeto = bpy.data.objects.get(RESULT)
            if objeto is None:
                raise ModeloNoGenerado()
            ExportadorStl.Exportar(objeto, bpy.path.ensure_ext(self.filepath, ".stl"))
            self.report({"INFO"}, "STL y parámetros guardados en mm.")
            Registro.Obtener("interfaz").info("Exportación terminada: %s", self.filepath)
            return {"FINISHED"}
        except Exception as exc:
            return PanelAyuda.Cancelar(self, context.scene.ortesislab, exc)


class OL_PT_panel(bpy.types.Panel):
    # Pestaña Ortesis de la vista 3D. El estado visible cabe en 48 caracteres.
    bl_label = "OrtesisLab"
    bl_idname = "OL_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Ortesis"

    def draw(self, context):
        layout = self.layout
        ajustes = context.scene.ortesislab
        layout.prop(ajustes, "source")
        layout.operator("ortesislab.use_surface", icon="MESH_DATA")
        layout.prop(PanelAyuda.OrigenAutoescala(context), "auto_scale")
        layout.operator(
            "ortesislab.repair_surface",
            text="Arreglar malla seleccionada",
            icon="TOOL_SETTINGS",
        )
        layout.label(text="Una capa de caras, abierta también en el dedo.")
        layout.prop(ajustes, "flip_normals")
        layout.prop(ajustes, "surface_step_mm")
        layout.prop(ajustes, "pattern")
        if ajustes.pattern == "SOLID":
            layout.prop(ajustes, "solid_mm")
        else:
            for clave in ("cell_mm", "rib_width_mm", "rib_height_mm", "liner"):
                layout.prop(ajustes, clave)
            if ajustes.liner:
                layout.prop(ajustes, "skin_mm")
                layout.prop(ajustes, "rounding_mm")
                layout.label(
                    text=f"Espesor total en nervadura: {ajustes.skin_mm + ajustes.rib_height_mm:.2f} mm"
                )
            else:
                layout.label(text="Rejilla abierta: altura = espesor total")
            layout.prop(ajustes, "angle_deg")
            if ajustes.pattern == "VORONOI":
                layout.prop(ajustes, "seed")
            layout.prop(ajustes, "border_mm")
            layout.prop(ajustes, "reinforce_width_mm")
            if ajustes.reinforce_width_mm > 0:
                layout.prop(ajustes, "reinforce_y_mm")
        layout.prop(ajustes, "repair")
        if ajustes.repair:
            layout.prop(ajustes, "resolution_mm")
            layout.label(text="Revise las aberturas tras reconstruir.", icon="INFO")
        layout.separator()
        layout.operator("ortesislab.generate", icon="MOD_BUILD")
        fila = layout.row()
        fila.operator("ortesislab.validate", icon="CHECKMARK")
        fila.operator("ortesislab.export", icon="EXPORT")
        layout.label(text=ajustes.status[:48])
        layout.label(text=AVISO_ALCANCE)


CLASSES = (
    OL_Preferences,
    OL_Settings,
    OL_OT_use_surface,
    OL_OT_repair_surface,
    OL_OT_generate,
    OL_OT_validate,
    OL_OT_export,
    OL_PT_panel,
)
