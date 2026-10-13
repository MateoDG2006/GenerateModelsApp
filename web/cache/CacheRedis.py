"""Caché compartida de superficies preparadas.

Clave por hash del NPZ normalizado: cruda, refinada (paso y autoescala) y
diagnóstico de escala. Un fallo de Redis devuelve ``None`` o ignora la
escritura: quien llama recalcula desde el objeto del bucket.
"""

from __future__ import annotations

import io
import json
import time

import numpy as np
import redis

from GenerateModelsApp.util.Utilidades import Registro
from web.Ajustes import Ajustes
from web.ConfiguracionBackend import ConfiguracionBackend

_CONFIG = ConfiguracionBackend.Cargar("cache")
PREFIJO = "ortesislab:superficie:"
TTL_S = _CONFIG["ttl_s"]
REINTENTO_S = _CONFIG["reintento_s"]


class CacheRedis:
    _cliente: redis.Redis | None = None
    _apagada_hasta = 0.0

    @staticmethod
    def ClaveCruda(sha256: str) -> str:
        return f"{PREFIJO}cruda:{sha256}"

    @staticmethod
    def ClaveRefinada(sha256: str, paso_mm: float, autoescalar: bool) -> str:
        return f"{PREFIJO}refinada:{sha256}:{float(paso_mm)!r}:{int(bool(autoescalar))}"

    @staticmethod
    def ClaveDiagnostico(sha256: str, autoescalar: bool, paso_mm: float | None = None) -> str:
        # Con paso, el diagnóstico es el del refinado: puede elegir otra potencia de diez.
        paso = "" if paso_mm is None else f":{float(paso_mm)!r}"
        return f"{PREFIJO}diagnostico:{sha256}:{int(bool(autoescalar))}{paso}"

    @staticmethod
    def Usar(cliente: redis.Redis | None) -> None:
        CacheRedis._cliente = cliente
        CacheRedis._apagada_hasta = 0.0

    @staticmethod
    def _Cliente() -> redis.Redis | None:
        if time.monotonic() < CacheRedis._apagada_hasta:
            return None
        if CacheRedis._cliente is None:
            url = Ajustes.Cargar().redis_url
            if not url:
                return None
            espera = _CONFIG["timeout_s"]
            CacheRedis._cliente = redis.Redis.from_url(url, socket_timeout=espera, socket_connect_timeout=espera)
        return CacheRedis._cliente

    @staticmethod
    def _Fallo(exc: Exception) -> None:
        # Evita pagar el timeout en cada lectura mientras Redis está caído.
        CacheRedis._apagada_hasta = time.monotonic() + REINTENTO_S
        Registro.Obtener("cache").warning("Redis no responde; se sigue sin caché: %s", exc)

    @staticmethod
    def LeerTupla(clave: str) -> tuple | None:
        cliente = CacheRedis._Cliente()
        if cliente is None:
            return None
        try:
            datos = cliente.get(clave)
        except redis.RedisError as exc:
            CacheRedis._Fallo(exc)
            return None
        if datos is None:
            return None
        try:
            with np.load(io.BytesIO(datos), allow_pickle=False) as archivo:
                return tuple(np.asarray(archivo[f"a{indice}"]) for indice in range(len(archivo.files)))
        except (OSError, ValueError, KeyError):
            return None

    @staticmethod
    def GuardarTupla(clave: str, tupla: tuple) -> None:
        cliente = CacheRedis._Cliente()
        if cliente is None:
            return
        salida = io.BytesIO()
        np.savez(salida, **{f"a{indice}": np.asarray(valor) for indice, valor in enumerate(tupla)})
        try:
            cliente.set(clave, salida.getvalue(), ex=TTL_S)
        except redis.RedisError as exc:
            CacheRedis._Fallo(exc)

    @staticmethod
    def LeerDiagnostico(clave: str) -> dict | None:
        cliente = CacheRedis._Cliente()
        if cliente is None:
            return None
        try:
            datos = cliente.get(clave)
        except redis.RedisError as exc:
            CacheRedis._Fallo(exc)
            return None
        return None if datos is None else json.loads(datos)

    @staticmethod
    def GuardarDiagnostico(clave: str, diagnostico: dict) -> None:
        cliente = CacheRedis._Cliente()
        if cliente is None:
            return
        try:
            cliente.set(clave, json.dumps(diagnostico), ex=TTL_S)
        except redis.RedisError as exc:
            CacheRedis._Fallo(exc)
