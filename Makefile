SHELL=/bin/bash

ENDPOINT_SERVICE_NAME = "endpoint"
LOAD_SERVICE_NAME = "loader"
DB_SERVICE_NAME = "database"


default: install

# Create python virtual environment.
venv:
	virtualenv -p `which python3.9` .venv

# Install dependencies and developing dependencies.
# Depends on the creation of a python virtual environment.
install: venv
	.venv/bin/pip install -Ur requirements.develop.txt

# Load CSV data in data/ into database.
#
# Target assumes that `install` as already been called.
data:
	.venv/bin/python load.py

# Run Fask application serving at port 8000
#
# Target assumes that `install` as already been called.
endpoint:
	.venv/bin/gunicorn --workers=1 --reload wsgi:app -b 0.0.0.0:8000

# Required by Tech Test.
# Run python black code formatter.
#
# Target assumes that `install` as already been called.
black:
	.venv/bin/black *.py

# Required by Tech Test.
# Run python style guide enforcement.
#
# Target assumes that `install` as already been called.
flake8:
	.venv/bin/flake8 *.py

# Run unit tests.
#
# Target assumes that `install` as already been called.
test:
	.venv/bin/py.test tests/

# Build docker images for database, endpoint and data loader
dbuild:
	docker-compose build --no-cache

# Run docker database container.
ddatabase:
	docker-compose up -d $(DB_SERVICE_NAME)

# Run endpoint container.
dendpoint:
	docker-compose up -d $(ENDPOINT_SERVICE_NAME)

# Load CSV data in data/ into database.
dload:
	docker-compose up -d $(LOAD_SERVICE_NAME)

# Stop all running containers
dstop:
	docker-compose down

# Run unit test
dtest: dbuild
	docker-compose run --rm $(ENDPOINT_SERVICE_NAME) test