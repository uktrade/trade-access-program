.DEFAULT: help
help:
	@echo "Trade Access Program"
	@echo "------------------"
	@echo
	@echo "make lint"
	@echo "    Runs linters"
	@echo
	@echo "make clean"
	@echo "    Removes compiled artifacts"
	@echo

clean:
	find . -name '__pycache__' -exec rm -rf {} +

up:
	docker-compose up

build:
	docker-compose build

bash:
	docker-compose run web bash

test:
	docker-compose run web pytest

lint:
	docker-compose run web flake8

# Django
shell:
	docker-compose run web python manage.py shell

collectstatic:
	docker-compose run web python manage.py collectstatic

# pip-tools
dev-requirements:
	pip-compile --output-file requirements/base.txt requirements/base.in
	pip-compile --output-file requirements/dev.txt requirements/dev.in

production-requirements:
	pip-compile --output-file requirements/base.txt requirements.in/base.in
	pip-compile --output-file requirements/production.txt requirements.in/production.in