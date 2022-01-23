from flask import Blueprint

from endpoint import crud
from endpoint import schemas


endpoint = Blueprint("endpoint", __name__)


@endpoint.route("/search/<search_by>/<value>", methods=["GET"])
def search(search_by, value):
    results = crud.search(search_by, value)
    return {"results": schemas.SearchResultSchema(results, many=True).data()}
