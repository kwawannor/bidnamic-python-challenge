import typing as t

from dataclasses import dataclass


@dataclass
class Field:
    """

    Define what attribute to be serialized on a Serializer class.

    name is the attribute name on serializing object.
    label is for labeling the serialized field
    required, if truly and and value is falsely raises error
    """

    name: str = None
    label: str = None
    required: bool = True

    def from_native(
        self,
        value: t.Any,
    ) -> t.Any:
        # do some validations here
        return value

    def getter(
        self,
        field_name: str,
        schema_cls: "Schema",
    ) -> None:
        return


class BaseSchema(Field):
    _fields = {}


class MetaSchema(type):
    def __new__(
        cls,
        name: str,
        bases: t.Tuple[type, ...],
        attrs: t.Dict[str, t.Any],
    ) -> "MetaSchema":
        schema_fields = {}
        fields = {}
        processed_fields = []

        for name, field in attrs.items():
            if isinstance(field, Field):
                schema_fields[name] = field

        for field in schema_fields:
            attrs.pop(field)
            # TODO: replace schema fields with describtors.

        new_cls = super().__new__(cls, name, bases, attrs)

        # go through parent classes and get fields.
        # this is needed to enable Schema subclassing.
        for cls in new_cls.__mro__[::1]:
            if issubclass(cls, BaseSchema):
                fields.update(cls._fields)

        fields.update(schema_fields)

        for name, field in fields.items():
            getattr = field.getter(name, new_cls)
            if getattr is None:
                getattr = new_cls.default_getter(field.name or name)

                from_native = field.from_native
                name = field.label or name

            processed_fields.append(
                (
                    field,
                    name,
                    getattr,
                    from_native,
                )
            )

            new_cls._fields = fields
            new_cls._processed_fields = tuple(processed_fields)

        return new_cls


class Schema:
    ...
