import os

import psycopg2

import pytest
from _pytest.monkeypatch import MonkeyPatch

from core import database
from shared import models

from app import create_app


@pytest.fixture
def testdatabase():
    return database.Database(
        host=os.environ["DATABASE_HOST"],
        database=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        port=int(os.environ["DATABASE_PORT"]),
    )


@pytest.fixture
def droptable(testdatabase):
    def _droptable(tablename):
        try:
            testdatabase.execute("DROP TABLE %s;" % tablename)
        except psycopg2.errors.UndefinedTable:
            pass

    return _droptable


@pytest.fixture(scope="session")
def monkeysession(request):
    patch = MonkeyPatch()
    yield patch
    patch.undo()


@pytest.fixture
def testclient(monkeysession, testdatabase):
    def init_db(app):
        database.create_table(testdatabase, models.AdGroup)
        database.create_table(testdatabase, models.Campaign)
        database.create_table(testdatabase, models.SearchTerm)

        app.database = testdatabase

        return testdatabase

    monkeysession.setattr("app.init_db", init_db)

    app = create_app()

    with app.test_client() as client:
        client.testapp = app

        yield client
