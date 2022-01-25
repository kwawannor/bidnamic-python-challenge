import operator
from dataclasses import dataclass

import pytest

from core import schema


def test_field():
    field = schema.Field()

    assert field.from_native(True) is True
    assert field.from_native(None) is None
    assert field.from_native(1) == 1
    assert field.from_native("one") == "one"

    field = schema.Field(name="my_field", label="my_field_label")

    assert field.name == "my_field"
    assert field.label == "my_field_label"
    assert field.required == True

    class TestField(schema.Field):
        def from_native(self, value: float):
            return str(value)

    test_field = TestField()
    assert test_field.from_native(1.9) == "1.9"


def test_meta_schema():
    class TestSchema(schema.BaseSchema, metaclass=schema.MetaSchema):
        default_getter = operator.attrgetter

    class TestSchemaFoo(TestSchema):
        field1 = schema.Field(name="dbfield1", label="field", required=False)
        field2 = schema.Field()
        field3 = schema.Field(name="dbfield3", label="field3", required=False)

    class TestSchemaBar(TestSchemaFoo):
        field3 = schema.Field()
        field4 = schema.Field()

    foo = TestSchemaFoo()
    bar = TestSchemaBar()

    with pytest.raises(AttributeError):
        foo.field1

    with pytest.raises(AttributeError):
        foo.field2

    with pytest.raises(AttributeError):
        foo.field3

    with pytest.raises(AttributeError):
        bar.field3

    with pytest.raises(AttributeError):
        bar.field4

    assert "field1" in foo._fields
    assert "field2" in foo._fields
    assert "field3" in foo._fields

    assert "field1" in bar._fields
    assert "field2" in bar._fields
    assert "field3" in bar._fields
    assert "field4" in bar._fields

    bar_field3 = bar._fields.get("field3")
    assert bar_field3.name is None
    assert bar_field3.label is None
    assert bar_field3.required is True

    foo_processed_fields = foo._processed_fields
    assert foo_processed_fields[0][0] == TestSchemaFoo._fields["field1"]
    assert foo_processed_fields[0][1] == "field"
    assert foo_processed_fields[1][0] == TestSchemaFoo._fields["field2"]
    assert foo_processed_fields[1][1] == "field2"
    assert foo_processed_fields[2][0] == TestSchemaFoo._fields["field3"]
    assert foo_processed_fields[2][1] == "field3"


def test_schema():
    @dataclass
    class Book:
        title: str
        author: str

    class TitleField(schema.Field):
        def from_native(self, value):
            return value.upper()

    class AuthorField(schema.Field):
        def from_native(self, value):
            return value.capitalize()

    class BookSchema(schema.Schema):
        title = TitleField()
        author = AuthorField()

    book = Book(title="book", author="john")
    serialized_book = BookSchema(book).data()

    assert serialized_book["title"] == "BOOK"
    assert serialized_book["author"] == "John"


def test_schema_schema_as_field():
    @dataclass
    class Author:
        name: str
        age: str

    @dataclass
    class Book:
        title: str
        author: Author

    class TitleField(schema.Field):
        def from_native(self, value):
            return value.upper()

    class NameField(schema.Field):
        def from_native(self, value):
            return value.capitalize()

    class AgeField(schema.Field):
        from_native = int

    class AuthorSchema(schema.Schema):
        name = NameField()
        age = AgeField()

    class BookSchema(schema.Schema):
        title = TitleField()
        author = AuthorSchema()

    author = Author(name="sam", age=45)
    book = Book(title="book", author=author)
    serialized_book = BookSchema(book).data()

    assert serialized_book["title"] == "BOOK"
    assert serialized_book["author"]["name"] == "Sam"
    assert serialized_book["author"]["age"] == 45


def test_schema_label():
    @dataclass
    class Book:
        title: str
        author: str

    class StrField(schema.Field):
        ...

    class BookSchema(schema.Schema):
        title = StrField(label="full_title")
        author = StrField(label="original_author")

    book = Book(title="Book", author="John")
    serialized_book = BookSchema(book).data()

    assert serialized_book["full_title"] == "Book"
    assert serialized_book["original_author"] == "John"


def test_schema_required():
    @dataclass
    class Book:
        title: str = None
        author: str = None

    class StrField(schema.Field):
        ...

    class BookSchema(schema.Schema):
        title = StrField(label="title", required=False)
        author = StrField(label="author")

    with pytest.raises(Exception):
        BookSchema(Book()).data()

    # control
    serialized_book = BookSchema(Book(author="Ken")).data()
    serialized_book["title"] == None
    serialized_book["author"] == "Ken"
