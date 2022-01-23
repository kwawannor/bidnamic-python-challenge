import typing as t

import operator
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


class IntegerField(Field):
    from_native = int


class StringField(Field):
    from_native = str


class FloatField(Field):
    from_native = float


class DecimalField(Field):
    from_native = str


class DateField(Field):
    def from_native(self, value):
        if value is not None:
            return value.isoformat()


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
            # TODO:
            # replace schema fields with descriptors.

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


class Schema(BaseSchema, metaclass=MetaSchema):
    """

    Service to serialize objects.
    """

    default_getter = operator.attrgetter

    def __init__(
        self,
        instance: t.Union[t.Any, t.List[t.Any], None] = None,
        many: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.instance = instance
        self.many = many

        self._data = None

    def from_native(
        self,
        instance: t.Union[t.Any, t.List[t.Any]],
    ) -> t.Any:
        if self.many:
            return [self._serialize(i) for i in instance]

        return self._serialize(instance)

    def data(self) -> t.Dict:
        if not self._data:
            self._data = self.from_native(self.instance)

        return self._data

    def _serialize(self, instance) -> t.Dict:
        serialized = {}

        for (
            field,
            name,
            getattr,
            from_native,
        ) in self._processed_fields:
            required = field.required

            if isinstance(field, BaseSchema):
                instance = getattr(instance)

                if field.instance is None:
                    field.instance = instance

                result = field.data()
            else:
                try:
                    result = getattr(instance)
                except (KeyError, AttributeError) as ex:
                    if required:
                        raise ex
                    else:
                        continue

                if required and result is None:
                    raise KeyError

                if result is not None:
                    if from_native:
                        try:
                            result = from_native(result)
                        except TypeError as ex:
                            raise ex

            serialized[name] = result

        return serialized
