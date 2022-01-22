from flask import jsonify


def handler404(*args):
    return (
        jsonify(
            {
                "error": {
                    "code": 4004,
                    "message": "Not Found",
                }
            }
        ),
        404,
    )


def handler_error(exception):
    return (
        jsonify(
            {
                "error": {
                    "code": 5000,
                    "message": str(exception),
                },
            },
        ),
        500,
    )
