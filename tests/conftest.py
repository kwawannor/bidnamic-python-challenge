import pytest
import psycopg2

from core import database


@pytest.fixture
def testdatabase():
    return database.Database(
        host="localhost",
        database="bidnamic",
        user="bidnamicuser",
        password="bidnamicpassword",
        port=55432,
    )


@pytest.fixture
def droptable(testdatabase):
    def _droptable(tablename):
        try:
            testdatabase.execute("DROP TABLE %s;" % tablename)
        except psycopg2.errors.UndefinedTable:
            pass

    return _droptable
