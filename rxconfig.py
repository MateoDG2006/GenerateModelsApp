import reflex as rx

config = rx.Config(
    app_name="GenerateModelsApp",
    # El paquete GenerateModelsApp es el complemento de Blender.
    # La página vive fuera, en web/.
    app_module_import="web.GenerateModelsApp",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(accent_color="indigo", gray_color="slate", radius="medium"),
        ),
    ],
)