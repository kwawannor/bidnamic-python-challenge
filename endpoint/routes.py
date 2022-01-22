from flask import Blueprint


endpoint = Blueprint("endpoint", __name__)


@endpoint.route("/search")
def search():
    return "This is an example app"
