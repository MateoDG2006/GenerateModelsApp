-- Fixture local e idempotente. El issuer urn:ortesislab:seed no lo emite ningún
-- proveedor OIDC, así que este usuario no da acceso real a la aplicación.
\set ON_ERROR_STOP on

DO $$
BEGIN
    IF current_database() <> 'ortesislab_dev' THEN
        RAISE EXCEPTION 'El seed solo se aplica a ortesislab_dev, no a %', current_database();
    END IF;
    IF to_regclass('ortesislab.history_events') IS NULL THEN
        RAISE EXCEPTION 'Falta el esquema; aplique las migraciones de Alembic (docs/AppBackend/OPERACION_Y_PRUEBAS.md)';
    END IF;
END
$$;

BEGIN;

INSERT INTO ortesislab.app_users (id, auth_issuer, auth_subject, display_name, status)
VALUES ('00000000-0000-4000-8000-000000000001', 'urn:ortesislab:seed', 'demo', 'Usuario demo', 'active')
ON CONFLICT (auth_issuer, auth_subject) DO NOTHING;

INSERT INTO ortesislab.user_preferences (user_id, auto_scale, locale)
VALUES ('00000000-0000-4000-8000-000000000001', true, 'es-CO')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO ortesislab.projects (id, user_id, name, description)
VALUES (
    '00000000-0000-4000-8000-000000000002',
    '00000000-0000-4000-8000-000000000001',
    'Proyecto demo',
    'Proyecto de ejemplo sin datos personales.'
)
ON CONFLICT (id) DO NOTHING;

COMMIT;
