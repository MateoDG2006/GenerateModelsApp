"""Almacén de bytes en un bucket S3 (MinIO en desarrollo).

Cliente boto3 síncrono, direccionamiento por ruta. Los handlers lo llaman desde
``asyncio.to_thread``; ninguna transacción SQL queda abierta durante la subida.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from urllib.parse import quote

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError

from web.Ajustes import Ajustes
from web.ConfiguracionBackend import ConfiguracionBackend

from .AlmacenamientoPrivado import AlmacenamientoNoDisponible, ObjetoAusente

AUSENTE = {"404", "NoSuchKey", "NotFound"}


class StorageS3:
    def __init__(self, endpoint: str, url_publica: str, clave: str, secreto: str, bucket: str, region: str):
        config = ConfiguracionBackend.Cargar("almacen")
        self.bucket = bucket
        self.base = f"{(url_publica or endpoint).rstrip('/')}/{bucket}"
        self.cliente = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=clave,
            aws_secret_access_key=secreto,
            region_name=region,
            config=Config(
                s3={"addressing_style": "path"},
                connect_timeout=config["timeout_conexion_s"],
                read_timeout=config["timeout_lectura_s"],
                retries={"max_attempts": config["intentos"], "mode": "standard"},
            ),
        )

    @staticmethod
    def DesdeAjustes() -> "StorageS3":
        ajustes = Ajustes.Cargar()
        return StorageS3(
            ajustes.s3_endpoint,
            ajustes.s3_public_url,
            ajustes.s3_access_key,
            ajustes.s3_secret_key,
            ajustes.s3_bucket,
            ajustes.s3_region,
        )

    def Url(self, clave: str) -> str:
        return f"{self.base}/{quote(clave)}"

    def Publicar(self, clave: str, datos: bytes, media_type: str, sha256: str, nombre: str | None = None) -> str:
        extra = {"ContentType": media_type, "Metadata": {"sha256": sha256}}
        if nombre:
            extra["ContentDisposition"] = f'attachment; filename="{nombre}"'
        try:
            self.cliente.put_object(Bucket=self.bucket, Key=clave, Body=datos, **extra)
            cabecera = self.cliente.head_object(Bucket=self.bucket, Key=clave)
        except (BotoCoreError, ClientError) as exc:
            raise AlmacenamientoNoDisponible() from exc
        if cabecera["ContentLength"] != len(datos) or cabecera.get("Metadata", {}).get("sha256") != sha256:
            raise AlmacenamientoNoDisponible("El objeto subido no coincide con el original.")
        return self.Url(clave)

    def Leer(self, clave: str) -> bytes:
        try:
            respuesta = self.cliente.get_object(Bucket=self.bucket, Key=clave)
            return respuesta["Body"].read()
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in AUSENTE:
                raise ObjetoAusente() from exc
            raise AlmacenamientoNoDisponible() from exc
        except (BotoCoreError, EndpointConnectionError) as exc:
            raise AlmacenamientoNoDisponible() from exc

    def Existe(self, clave: str) -> bool:
        try:
            self.cliente.head_object(Bucket=self.bucket, Key=clave)
            return True
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in AUSENTE:
                return False
            raise AlmacenamientoNoDisponible() from exc
        except BotoCoreError as exc:
            raise AlmacenamientoNoDisponible() from exc

    def Borrar(self, clave: str) -> None:
        try:
            self.cliente.delete_object(Bucket=self.bucket, Key=clave)
        except (BotoCoreError, ClientError) as exc:
            raise AlmacenamientoNoDisponible() from exc

    def Claves(self, prefijo: str) -> Iterator[tuple[str, datetime]]:
        try:
            paginas = self.cliente.get_paginator("list_objects_v2").paginate(Bucket=self.bucket, Prefix=prefijo)
            for pagina in paginas:
                for objeto in pagina.get("Contents", []):
                    yield objeto["Key"], objeto["LastModified"]
        except (BotoCoreError, ClientError) as exc:
            raise AlmacenamientoNoDisponible() from exc
