.DEFAULT: help

SUB_PROJECTS = backoffice

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

run-background-services:  ## Start all backing helper services in the background
	docker-compose up -d backoffice_db frontend_db

run-%-debug:  ## Run a service in debug mode, eg. `make run-frontend-debug`. Available options: frontend, backoffice
	docker-compose run --use-aliases --service-ports $*

##@ Main
build:  ## Build the project
	docker-compose build

lint-all:  ## Run linting in all projects
	$(MAKE) lint-$(SUB_PROJECTS)

test-all:  ## Run tests in all projects
	$(MAKE) test-$(SUB_PROJECTS)


