# Infraestructura local de OrtesisLab: PostgreSQL, MinIO (S3) y Redis.
# Requisitos: GNU Make, Docker Desktop y Python. Las recetas funcionan con
# cmd.exe y con sh. Los clientes PostgreSQL y MinIO corren dentro de contenedores.
# Las migraciones de esquema (Alembic) se ejecutan a mano; ver
# docs/AppBackend/OPERACION_Y_PRUEBAS.md.

.DEFAULT_GOAL := db-help
.NOTPARALLEL:

ENV_FILE ?= infra/database/.env
COMPOSE = docker compose -f infra/database/compose.yaml --env-file $(ENV_FILE)
DB_NAME ?= ortesislab_dev
DB_ADMIN ?= ortesislab_admin
PYTHON ?= python
BUCKET ?= ortesislab

# Valida NAME y FILE con una lista blanca antes de pasarlos a un comando.
VALIDAR = $(PYTHON) -c "import re,sys; sys.exit(0 if re.fullmatch(sys.argv[1], sys.argv[2]) else 'Valor no permitido: ' + sys.argv[2])"
EXIGIR_DESARROLLO = $(if $(filter ortesislab_dev,$(DB_NAME)),,$(error Solo se permite sobre ortesislab_dev))
EXIGIR_FILE = $(if $(FILE),,$(error Indique FILE=nombre.dump))

.PHONY: db-help db-config db-up db-init-s3 db-stop db-down db-logs db-health s3-health redis-health \
	db-seed db-shell db-backup db-restore s3-backup s3-restore db-drop db-destroy db-test-reset \
	auth-dev-up auth-dev-down

db-help:
	@echo Objetivos disponibles:
	@echo   db-config               Valida la configuracion de Compose sin imprimir secretos
	@echo   db-up                   Arranca PostgreSQL, MinIO y Redis y espera su salud
	@echo   db-init-s3              Crea bucket, politicas y cuenta de servicio en MinIO
	@echo   db-stop / db-down       Detiene o retira contenedores conservando volumenes
	@echo   db-logs                 Ultimas 200 lineas de cada servicio
	@echo   db-health               pg_isready contra la base
	@echo   s3-health / redis-health  Salud de MinIO y Redis
	@echo   db-seed                 Fixture idempotente solo para ortesislab_dev
	@echo   db-shell                psql interactivo como migrador
	@echo   db-backup FILE=x.dump   pg_dump formato custom en infra/database/backups
	@echo   db-restore FILE=x.dump CONFIRM=RESTAURAR  Restaura metadatos; no restaura objetos
	@echo   s3-backup / s3-restore CONFIRM=RESTAURAR  Copia del bucket con mc mirror
	@echo   db-drop CONFIRM=ELIMINAR      Elimina la base local
	@echo   db-destroy CONFIRM=ELIMINAR   Elimina volumenes de PostgreSQL y MinIO
	@echo   db-test-reset           Recrea ortesislab_test vacia con su esquema; migrar despues a mano
	@echo   auth-dev-up / auth-dev-down   Proveedor OIDC de pruebas en 127.0.0.1:8080

db-config:
	$(COMPOSE) config --quiet

db-up:
	$(COMPOSE) up -d --wait postgres minio redis

db-init-s3:
	$(COMPOSE) --profile init run --rm minio-init

db-stop:
	$(COMPOSE) stop

db-down:
	$(COMPOSE) down

db-logs:
	$(COMPOSE) logs --tail 200

db-health:
	$(COMPOSE) exec -T postgres pg_isready -d $(DB_NAME)

s3-health:
	$(COMPOSE) exec -T minio mc ready local

redis-health:
	$(COMPOSE) exec -T redis redis-cli ping

db-seed:
	$(EXIGIR_DESARROLLO)
	$(COMPOSE) exec -T postgres psql -v ON_ERROR_STOP=1 -U ortesislab_migrator -d $(DB_NAME) -f /seeds/development.sql

db-shell:
	$(COMPOSE) exec postgres psql -U ortesislab_migrator -d $(DB_NAME)

db-backup:
	$(EXIGIR_FILE)
	$(VALIDAR) "[A-Za-z0-9._-]{1,80}\.dump" "$(FILE)"
	$(PYTHON) -c "import pathlib,sys; sys.exit('Ya existe infra/database/backups/$(FILE)' if pathlib.Path('infra/database/backups/$(FILE)').exists() else 0)"
	$(COMPOSE) exec -T postgres pg_dump -Fc -U ortesislab_backup -d $(DB_NAME) -n ortesislab -f /backups/$(FILE)

db-restore:
	$(EXIGIR_FILE)
	$(EXIGIR_DESARROLLO)
	$(if $(filter RESTAURAR,$(CONFIRM)),,$(error Confirme con CONFIRM=RESTAURAR; reemplaza los metadatos de $(DB_NAME)))
	$(VALIDAR) "[A-Za-z0-9._-]{1,80}\.dump" "$(FILE)"
	$(COMPOSE) exec -T postgres pg_restore --list /backups/$(FILE)
	$(COMPOSE) exec -T postgres pg_restore --clean --if-exists --single-transaction --exit-on-error -U ortesislab_migrator -d $(DB_NAME) /backups/$(FILE)

s3-backup:
	$(COMPOSE) run --rm mc mirror --overwrite local/$(BUCKET) /backups/objetos

s3-restore:
	$(if $(filter RESTAURAR,$(CONFIRM)),,$(error Confirme con CONFIRM=RESTAURAR; sobrescribe objetos del bucket))
	$(COMPOSE) run --rm mc mirror --overwrite /backups/objetos local/$(BUCKET)

db-drop:
	$(EXIGIR_DESARROLLO)
	$(if $(filter ELIMINAR,$(CONFIRM)),,$(error Confirme con CONFIRM=ELIMINAR))
	$(COMPOSE) exec -T postgres dropdb --if-exists -U $(DB_ADMIN) $(DB_NAME)

db-destroy:
	$(if $(filter ELIMINAR,$(CONFIRM)),,$(error Confirme con CONFIRM=ELIMINAR; borra los volumenes locales))
	$(COMPOSE) down --volumes

db-test-reset:
	$(COMPOSE) exec -T postgres dropdb --if-exists --force -U $(DB_ADMIN) ortesislab_test
	$(COMPOSE) exec -T postgres createdb -U $(DB_ADMIN) -O ortesislab_migrator ortesislab_test
	$(COMPOSE) exec -T postgres psql -v ON_ERROR_STOP=1 -q -v base=ortesislab_test -U $(DB_ADMIN) -d ortesislab_test < db/test/preparar_base.sql

auth-dev-up:
	$(COMPOSE) --profile auth-dev up -d oidc

auth-dev-down:
	$(COMPOSE) --profile auth-dev stop oidc
