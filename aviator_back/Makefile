# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

.PHONY: help

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

black: ## black
	black . --line-length=79 --exclude migrations\

build: ## build
	docker compose build

up: ## up
	docker compose up

up-d: ## up d
	docker compose up -d

down: ## down
	docker compose down --remove-orphans

down-d: ## down
	docker compose down --remove-orphans --rmi local

run:  ## run
	docker compose run --rm --service-ports worker ${ARGS}

makemigrations:  ## makemigrations
	docker compose run --rm --entrypoint=python worker manage.py makemigrations

migrate: ## migrate
	docker compose run --rm --entrypoint=python worker manage.py migrate

load-fixtures: ## loaddata
	docker compose run --rm --entrypoint=python worker manage.py loaddata fixtures/*.json

create-model: ## create a sequential model
	docker compose run --rm --entrypoint=python worker manage.py create_model ${home_bet_id} ${model_type} ${seq_len}

generate-category-result: ## generate category result for all models
	docker compose run --rm --entrypoint=python worker manage.py generate_category_results

export-multipliers-to-csv: ## export multipliers to csv
	docker compose run --rm --entrypoint=python worker manage.py export_multipliers_to_csv ${home_bet_id}

create-super-user: ## loaddata
	docker compose run --rm --entrypoint=python worker manage.py createsuperuser

reset-db: ## reset_db
	docker compose run --rm --entrypoint=python worker manage.py reset_db -c

shell: ## shell
	docker compose run --rm --entrypoint=python worker manage.py shell_plus

run-tests:  # run-tests
	docker compose run --rm --entrypoint=pytest worker /tests/ $(ARGS)

celery: ## run celery
	docker compose run --rm --entrypoint=celery worker -A mo_manage.messaging.app worker -l info

exec-celery: ## exec celery
	docker compose exec worker celery -A mo_manage.messaging.app worker -l info

beat: ## run celery beat
	docker compose run --rm --entrypoint=celery worker -A mo_manage.messaging.app beat

docker-celery: ## docker celery
	docker exec -it ${CONTAINER_ID} celery -A mo_manage.messaging.app worker -l info

docker-attach: ## docker attach
	docker attach --detach-keys ctrl-d ${CONTAINER_ID}

