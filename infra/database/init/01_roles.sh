#!/bin/sh
# Se ejecuta una sola vez, al crear el volumen. Roles separados: el migrador
# es dueño del esquema; la aplicación y el trabajador no tienen DDL.
set -eu

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -v base="$POSTGRES_DB" \
  -v clave_migrador="$ORTESISLAB_MIGRATOR_PASSWORD" \
  -v clave_app="$ORTESISLAB_APP_PASSWORD" \
  -v clave_trabajador="$ORTESISLAB_WORKER_PASSWORD" \
  -v clave_backup="$ORTESISLAB_BACKUP_PASSWORD" <<'SQL'
CREATE ROLE ortesislab_migrator LOGIN PASSWORD :'clave_migrador';
CREATE ROLE ortesislab_app LOGIN PASSWORD :'clave_app';
CREATE ROLE ortesislab_worker LOGIN PASSWORD :'clave_trabajador';
CREATE ROLE ortesislab_backup LOGIN PASSWORD :'clave_backup';

REVOKE ALL ON DATABASE :"base" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE :"base" TO ortesislab_migrator, ortesislab_app, ortesislab_worker, ortesislab_backup;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

CREATE SCHEMA ortesislab AUTHORIZATION ortesislab_migrator;
GRANT USAGE ON SCHEMA ortesislab TO ortesislab_app, ortesislab_worker, ortesislab_backup;

ALTER ROLE ortesislab_migrator SET search_path = ortesislab;
ALTER ROLE ortesislab_app SET search_path = ortesislab;
ALTER ROLE ortesislab_worker SET search_path = ortesislab;
ALTER ROLE ortesislab_backup SET search_path = ortesislab;

ALTER ROLE ortesislab_app SET statement_timeout = '15s';
ALTER ROLE ortesislab_worker SET statement_timeout = '15s';

GRANT pg_read_all_data TO ortesislab_backup;
SQL
