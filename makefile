.DEFAULT: help

##@ Misc
help:  ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nmake \033[36m<target>\033[0m\n"} /^([a-zA-Z_-]+|.*-%*):.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ docker-compose
clean:  ## Remove python cache files from project
	find . -name '__pycache__' -exec rm -rf {} +

up:  ## Run all services in docker-compose.yml
	docker-compose up

build:  ## Build all services in docker-compose.yml
	docker-compose build

bash:  ## Open a bash shell in the web service
	docker-compose run web bash

test:  ## Run all tests
	docker-compose run web pytest

test-ci:  ## Run all tests with output that is kind to CircleCI
	docker-compose run web pytest -p no:sugar -v

lint:  ## Run all linters
	docker-compose run web flake8


##@ Django
django-%:  ## Run a Django manage command in the web service. eg. `make django-makemigrations`
	docker-compose run web python manage.py $*

shell:  ## Open a Django python shell in the web service
	$(MAKE) django-shell

elevate:  ## Elevate a user account to admin (required because we use django-staff-sso-client and django-staff-sso-usermodel)
	$(MAKE) django-elevate_sso_user_permissions

seed-db:  # Seed the database with some fake data
	$(MAKE) django-seed_db

graph-models:  # Generate diagrams
	$(MAKE) django-graph_models

##@ pip-tools
pip-compile-dev:  ## Generate dev requirements file: `requirements/dev.txt`
	pip-compile --output-file requirements/base.txt requirements/base.in
	pip-compile --output-file requirements/dev.txt requirements/dev.in

pip-compile-production:  ## Generate prod requirements file: `requirements/base.txt`
	pip-compile --output-file requirements/base.txt requirements/base.in

pip-sync-dev:  ## Sync local virtualenv to dev requirements
	pip-sync requirements/dev.txt

pip-sync-production:  ## Sync local virtualenv to prod requirements
	pip-sync requirements/base.txt

pip-compile-and-sync-dev: pip-compile-dev pip-sync-dev  ## Run compile and sync to dev requirements

pip-compile-and-sync-production: pip-compile-production pip-sync-production  ## Run compile and sync to prod requirements
