import typing as t

import os

from flask import Flask

from core.database import Database
from core.database import create_table
from core.exceptions import ValidationException

from shared.models import AdGroup
from shared.models import Campaign
from shared.models import SearchTerm

from endpoint.routes import endpoint
from endpoint.errors import handler404
from endpoint.errors import handler_error
from endpoint.errors import validation_error


config_variable_name = "FLASK_CONFIG_PATH"


def init_db(app: Flask) -> Database:
    database = Database(
        host=app.config["DATABASE_HOST"],
        database=app.config["DATABASE_NAME"],
        user=app.config["DATABASE_USER"],
        password=app.config["DATABASE_PASSWORD"],
        port=int(app.config["DATABASE_PORT"]),
    )

    create_table(database, AdGroup)
    create_table(database, Campaign)
    create_table(database, SearchTerm)

    app.database = database

    return database


def create_app(config_file: t.Optional[str] = None) -> Flask:
    app = Flask(__name__)

    app.config.from_object("endpoint.config.base")
    if os.environ.get(config_variable_name):
        app.config.from_envvar(config_variable_name)

    if config_file:
        app.config.from_pyfile(config_file)

    # instantiate database
    init_db(app)

    # register blueprint endpoint.
    app.register_blueprint(endpoint)

    # decorate error handlers.
    app.errorhandler(404)(handler404)
    app.errorhandler(Exception)(handler_error)
    app.errorhandler(ValidationException)(validation_error)

    return app
