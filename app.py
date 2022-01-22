import typing as t

import os

from flask import Flask

from endpoint.routes import endpoint
from endpoint.errors import handler404
from endpoint.errors import handler_error


config_variable_name = "FLASK_CONFIG_PATH"


def create_app(config_file: t.Optional[str] = None) -> Flask:
    app = Flask(__name__)

    app.config.from_object("endpoint.config.base")
    if os.environ.get(config_variable_name):
        app.config.from_envvar(config_variable_name)

    if config_file:
        app.config.from_pyfile(config_file)

    # register blueprint endpoint.
    app.register_blueprint(endpoint)

    # decorate error handlers.
    app.errorhandler(404)(handler404)
    app.errorhandler(Exception)(handler_error)

    return app
