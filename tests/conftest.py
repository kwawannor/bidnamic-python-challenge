import os

import pytest
import psycopg2

from core import database


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
