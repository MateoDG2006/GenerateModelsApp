-- Prepara una base vacía (ortesislab_dev u ortesislab_test) con los mismos
-- permisos que crea infra/database/init/01_roles.sh. Los roles ya existen porque
-- son globales del clúster. Uso: psql -v base=<nombre> -d <nombre> -f este archivo.
-- No crea tablas: el esquema lo aplica Alembic con el rol migrador.
REVOKE ALL ON DATABASE :"base" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE :"base"
    TO ortesislab_migrator, ortesislab_app, ortesislab_worker, ortesislab_backup;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA ortesislab AUTHORIZATION ortesislab_migrator;
GRANT USAGE ON SCHEMA ortesislab TO ortesislab_app, ortesislab_worker, ortesislab_backup;
