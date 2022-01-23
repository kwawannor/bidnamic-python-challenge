SHELL=/bin/bash

ENDPOINT_SERVICE_NAME = "endpoint"
LOAD_SERVICE_NAME = "loader"


default: install

venv:
	virtualenv -p `which python3.9` .venv

install: venv
	.venv/bin/pip install -Ur requirements.develop.txt

# Required
black:
	.venv/bin/black *.py

# Required
flake8:
	.venv/bin/flake8 *.py

test:
	.venv/bin/py.test tests/

dbuild:
	docker-compose build --no-cache

dendpoint:
	docker-compose up -d $(ENDPOINT_SERVICE_NAME)

dload:
	docker-compose up -d $(LOAD_SERVICE_NAME)

dstop:
	docker-compose down

dtest: dbuild
	docker-compose run --rm $(ENDPOINT_SERVICE_NAME) test