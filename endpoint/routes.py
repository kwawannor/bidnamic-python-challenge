from flask import Blueprint
from flask import jsonify
from flask import request

from core.exceptions import ValidationException

from endpoint import crud
from endpoint import schemas


endpoint = Blueprint("endpoint", __name__)


@endpoint.route("/search", methods=["GET"])
def search():
    def validate(args):

        # TODO: create schema.Schema.validate
        # for validation
        #
        # SPECS
        # class Schema:
        #     def _deserialize(self, ...):
        #          self._validate() # raise ValidationException
        #          ...
        #          return valid_data
        #
        #     def validate(self, ...):
        #          return self._deserialize()

        search_term = args.get("term")
        search_value = args.get("value")

        if not (search_term and search_value):
            raise ValidationException("term and value are required.")

        return search_term, search_value

    results = crud.search(*validate(request.args))
    results = schemas.SearchResultSchema(results, many=True).data()

    return jsonify({"results": results})
