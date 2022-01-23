SHELL=/bin/bash

ENDPOINT_SERVICE_NAME = "endpoint"
LOAD_SERVICE_NAME = "endpoint"


default: stop build test endpoint

build:
	docker-compose build --no-cache

endpoint:
	docker-compose up -d $(ENDPOINT_SERVICE_NAME)

load:
	docker-compose up -d $(LOAD_SERVICE_NAME)

stop:
	docker-compose down

test:
	docker-compose run --rm $(ENDPOINT_SERVICE_NAME) test