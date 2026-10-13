"""Proceso trabajador de OrtesisLab: cola de generación y conciliación.

Abre el pool con el rol ``ortesislab_worker`` (máximo 2 conexiones), usa el
mismo bucket y la misma caché Redis que la web y no importa Blender. Se detiene
con Ctrl+C; el ítem en curso termina o su lease vence y vuelve a la cola.

Uso: ``python scripts/EjecutarTrabajador.py [--una-vez]``
"""

from __future__ import annotations

import argparse
import signal
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from web.Ajustes import Ajustes  # noqa: E402
from web.jobs.TrabajadorGeneracion import TrabajadorGeneracion  # noqa: E402
from web.persistence.ConexionPostgres import ConexionPostgres  # noqa: E402
from web.storage.AlmacenamientoPrivado import Almacen  # noqa: E402


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--una-vez", action="store_true", help="Procesa la cola hasta vaciarla y termina.")
    opciones = argumentos.parse_args()

    # Crear el almacén aquí hace que una variable S3 ausente falle al arrancar y no en el primer trabajo.
    Almacen.Actual()
    ConexionPostgres.Abrir(Ajustes.Cargar().worker_database_url, 1, 2, "trabajador")
    trabajador = TrabajadorGeneracion()
    try:
        if opciones.una_vez:
            while trabajador.Ciclo():
                pass
            return 0
        detener = threading.Event()
        signal.signal(signal.SIGINT, lambda *_: detener.set())
        signal.signal(signal.SIGTERM, lambda *_: detener.set())
        trabajador.Ejecutar(detener)
        return 0
    finally:
        ConexionPostgres.Cerrar()


if __name__ == "__main__":
    raise SystemExit(main())
