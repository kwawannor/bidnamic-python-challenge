from unittest import mock

from core.exceptions import ValidationException


def test_handler404(testclient):
    response = testclient.get("/ko12-you-90")
    response_data = response.get_json()

    assert response.status_code == 404
    assert response_data["error"]["code"] == 4004
    assert response_data["error"]["message"] == "Not Found"


@mock.patch("endpoint.crud.search", side_effect=TypeError("Type Error"))
def test_handler_error(mocksearch, testclient):
    response = testclient.get("/search?term=foo&value=bar")
    response_data = response.get_json()

    assert response.status_code == 500
    assert response_data["error"]["code"] == 5000
    assert response_data["error"]["message"] == "Type Error"


@mock.patch("endpoint.crud.search", side_effect=ValidationException("Invalid Error"))
def validation_error(testclient):
    response = testclient.get("/search?term=foo&value=bar")
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data["error"]["code"] == 4000
    assert response_data["error"]["message"] == "Invalid Error"
