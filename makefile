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
django-%:
	docker-compose run web python manage.py $*

shell:
	$(MAKE) manage-shell

collect-static:
	$(MAKE) manage-collectstatic


# pip-tools
pip-compile-dev:
	pip-compile --output-file requirements/base.txt requirements/base.in
	pip-compile --output-file requirements/dev.txt requirements/dev.in

pip-compile-production:
	pip-compile --output-file requirements/base.txt requirements/base.in

pip-sync-dev:
	pip-sync requirements/dev.txt

pip-sync-production:
	pip-sync requirements/base.txt
