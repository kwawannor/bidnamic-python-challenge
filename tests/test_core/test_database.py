from core import database


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
