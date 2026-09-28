"""Script del comando de consola del proyecto.

Imprime el saludo de arranque. No genera ortesis ni abre Blender.
Se puede lanzar con: python scripts/IniciarConsola.py
"""


class IniciarConsola:
    """Punto de entrada del saludo. El paquete no depende de este archivo."""

    @staticmethod
    def Ejecutar() -> None:
        # Mensaje del esqueleto creado por uv. No arranca Reflex ni el generador.
        print("Hello from generatemodelsapp!")


if __name__ == "__main__":
    IniciarConsola.Ejecutar()
