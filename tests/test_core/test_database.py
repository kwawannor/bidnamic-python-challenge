from unittest import mock
from dataclasses import Field

import datetime

import pytest

from core import database


@pytest.mark.skip
@mock.patch("psycopg2.connect")
def test_database_connection(mock_connect):
    connect_parameters = {"host": "localhost", "password": "password"}
    database.Database(**connect_parameters).connection

    mock_connect.assert_called_with(**connect_parameters)


def test_database_table_exists(testdatabase):
    table_not_exist_test = testdatabase.table_exist("test")
    testdatabase.execute("CREATE TABLE test (id serial PRIMARY KEY);")
    table_exist_test = testdatabase.table_exist("test")
    testdatabase.execute("DROP TABLE test;")

    assert table_not_exist_test is False
    assert table_exist_test is True


def test_model_instantiation():
    class Author(database.Model):
        name: str
        age: int
        height: int

    author_instance = Author(name="Per Son", age=30, height=130)

    assert author_instance.name == "Per Son"
    assert author_instance.age == 30
    assert author_instance.height == 130


def test_inheritance():
    class Person(database.Model):
        name: str
        age: int

    class Author(Person):
        height: int

    author_instance = Author(name="Per Son", age=30, height=130)

    assert author_instance.name == "Per Son"
    assert author_instance.age == 30
    assert author_instance.height == 130


def test_model_registry():
    database.Model.model_registry = {}

    class Author(database.Model):
        name: str
        age: int
        height: int

    class Person(database.Model):
        name: str
        age: int

    model_registry_name_list = list(database.Model.model_registry.keys())
    model_registry_model_list = list(database.Model.model_registry.values())

    assert model_registry_name_list == ["Author", "Person"]
    for model in model_registry_model_list:
        assert type(database.Model) == database.ModelMeta


def test_manager_get_model_fields(testdatabase):
    class Author(database.Model):
        name: str
        age: int = 23
        height: int = None
        book_title: str = "my book"

    manager = database.Manager(testdatabase, Author)
    fields = manager.get_model_fields()

    assert isinstance(fields["name"], Field)
    assert isinstance(fields["age"], Field)
    assert isinstance(fields["height"], Field)
    assert isinstance(fields["book_title"], Field)


def test_manager_get_model_columns(testdatabase):
    class Author(database.Model):
        name: str
        age: int = 23
        height: int = None
        book_title: str = "my book"
        create_date: datetime.date = datetime.date(2022, 10, 15)
        create_datetime: datetime.datetime = datetime.datetime(2022, 10, 15, 10, 19, 10)

    manager = database.Manager(testdatabase, Author)
    columns = manager.get_model_columns()

    assert columns[0] == "name varchar(255) NOT NULL"
    assert columns[1] == "age integer DEFAULT 23"
    assert columns[2] == "height integer DEFAULT NULL"
    assert columns[3] == "book_title varchar(255) DEFAULT 'my book'"
    assert columns[4] == "create_date date DEFAULT '2022-10-15'::date"
    assert (
        columns[5]
        == "create_datetime datetime DEFAULT '2022-10-15T10:19:10'::timestamp"
    )


def test_manager_insert(testdatabase, droptable):
    droptable("author")

    class Author(database.Model):
        name: str
        age: int = 23

    database.create_table(testdatabase, Author)
    manager = database.Manager(testdatabase, Author)

    author = Author(name="Ken", age=100)
    manager.save(author)

    assert author.id == 1

    droptable("author")


def test_manager_get(testdatabase, droptable):
    droptable("author")

    class Author(database.Model):
        name: str
        age: int = 23

    database.create_table(testdatabase, Author)
    manager = database.Manager(testdatabase, Author)

    author = Author(name="Ken")
    manager.save(author)

    saved_author = manager.get(id=1)

    assert saved_author.id == 1
    assert saved_author.name == "Ken"
    assert saved_author.age == 23

    droptable("author")


def test_create_table(testdatabase, droptable):
    droptable("author")

    class Author(database.Model):
        name: str
        age: int = 23

    database.create_table(testdatabase, Author)

    assert testdatabase.table_exist("author")

    droptable("author")
