.DEFAULT: help

##@ Misc
help:  ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nmake \033[36m<target>\033[0m\n"} /^([a-zA-Z_-]+|.*-%*):.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""


test-%:  ## Run tests for a specific project
	$(MAKE) -C $* test

lint-%:  ## Run linting for a specific project
	$(MAKE) -C $* lint

build-%:  ## Build a service
	docker-compose build $*

run-%-debug:  ## Run a service in debug mode, eg. `make run-frontend-debug`. Available options: frontend, backoffice
	$(MAKE) -C $* run-$*-debug

##@ Main
setup:  ## Setup a local environment
	cp -n backoffice/sample.env backoffice/.env
	cp -n frontend/sample.env frontend/.env

run-background-services:  ## Start all backing helper services in the background
	docker-compose up -d backoffice_db frontend_db

up:  ## Start all services
	docker-compose up

build: setup  ## Build the project
	docker-compose build

lint:  ## Run linting in all projects
	$(MAKE) lint-backoffice
	$(MAKE) lint-frontend

test:  ## Run tests in all projects
	$(MAKE) test-backoffice
	$(MAKE) test-frontend


