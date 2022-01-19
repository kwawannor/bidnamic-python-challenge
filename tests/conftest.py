import pytest

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
