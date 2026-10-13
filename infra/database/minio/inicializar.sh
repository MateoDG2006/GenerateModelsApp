#!/bin/sh
# Bucket, política anónima de lectura de STL de resultado y cuenta de servicio.
set -eu

mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null
mc mb --ignore-existing "local/$ORTESISLAB_S3_BUCKET"

# Solo los STL de resultado (clave terminada en .stl) se leen sin firma. El
# original importado, el NPZ y el JSON de parámetros no tienen extensión y
# quedan privados. No se concede ListBucket: no se puede enumerar el bucket.
sed "s/__BUCKET__/$ORTESISLAB_S3_BUCKET/g" /config/politica-lectura-stl.json > /tmp/lectura.json
mc anonymous set-json /tmp/lectura.json "local/$ORTESISLAB_S3_BUCKET"

sed "s/__BUCKET__/$ORTESISLAB_S3_BUCKET/g" /config/politica-aplicacion.json > /tmp/aplicacion.json
mc admin policy create local ortesislab-aplicacion /tmp/aplicacion.json
if ! mc admin user info local "$ORTESISLAB_S3_ACCESS_KEY" >/dev/null 2>&1; then
  mc admin user add local "$ORTESISLAB_S3_ACCESS_KEY" "$ORTESISLAB_S3_SECRET_KEY"
fi
mc admin policy attach local ortesislab-aplicacion --user "$ORTESISLAB_S3_ACCESS_KEY" >/dev/null 2>&1 || true
echo "Bucket $ORTESISLAB_S3_BUCKET listo."
