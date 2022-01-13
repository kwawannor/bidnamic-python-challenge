import typing as t

import os

from flask import Flask


config_variable_name = "FLASK_CONFIG_PATH"


def create_app(config_file: t.Optional[str] = None) -> Flask:
    app = Flask(__name__)

    app.config.from_object("config.base")
    if os.environ.get(config_variable_name):
        app.config.from_envvar(config_variable_name)

    if config_file:
        app.config.from_pyfile(config_file)

    return app
