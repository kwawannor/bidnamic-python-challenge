import typing as t

import datetime
import decimal

from contextlib import contextmanager
from contextlib import closing
from dataclasses import dataclass
from dataclasses import _MISSING_TYPE
from collections import OrderedDict

from psycopg2 import connect
from psycopg2.extensions import cursor


class Database:
    """

    Postgres database wrapper.
    """

    def __init__(self, *args, **kwargs) -> None:
        """

        args & kwargs are directly passed to  psycopg2.connect
        """
        self.args = args
        self.kwargs = kwargs

        self._connection = None

    @property
    def connection(self) -> t.Any:
        self._connection = connect(*self.args, **self.kwargs)

        return self._connection

    @contextmanager
    def transact(self) -> t.Generator[t.Any, None, None]:
        """

        Context manager to create a database transaction
        """
        with closing(self.connection) as connection:
            cursor = connection.cursor()
            yield cursor
            connection.commit()

    def execute(
        self,
        query: str,
        args: t.Union[t.Dict[str, str], t.List[str], None] = None,
    ) -> cursor:
        """

        Execute a query.
        """
        with self.transact() as cursor:
            cursor.execute(query, vars=args)

            return cursor

    def executemany(
        self,
        query: str,
        args: t.Union[t.Dict[str, str], t.List[str]],
    ) -> cursor:
        """

        Execute a multi-row query.
        """
        with self.transact() as cursor:
            cursor.executemany(query, args)

            return cursor

    def table_exist(self, table_name: str) -> bool:
        query = "SELECT to_regclass(%s);"
        query_args = (table_name,)

        with self.transact() as cursor:
            cursor.execute(query, query_args)
            result = cursor.fetchone()[0]

            return bool(result)


class ModelMeta(type):
    """

    Meta programmer for database relational mapper.
    Create a new model class decorated by a dataclass.
    """

    def __new__(
        cls,
        name: str,
        bases: t.Tuple[type, ...],
        attrs: t.Dict[str, t.Any],
    ) -> t.Type["ModelMeta"]:
        new_cls = super().__new__(cls, name, bases, attrs)
        new_cls = dataclass(new_cls)

        return new_cls


class Model(metaclass=ModelMeta):
    """

    Database relational mapping.
    """

    class Meta:
        database = None

    model_registry = OrderedDict()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        Model.model_registry.setdefault(cls.__name__, cls)

    @classmethod
    def manager(cls, database=None):
        return Manager(database or cls.Meta.database, cls)


PYTHON_POSTGRES_TYPES_MAPPING = {
    None: ("NULL", None),
    bool: ("bool", None),
    list: ("ARRAY", None),
    int: ("integer", None),
    str: ("varchar", "255"),
    float: ("double", None),
    decimal.Decimal: ("numeric", None),
    datetime.date: ("date", None),
    datetime.time: ("time", None),
    datetime.datetime: ("datetime", None),
    datetime.timedelta: ("interval", None),
}


class Manager:
    """

    Orm driver.
    """

    def __init__(
        self,
        database: Database,
        model: Model,
    ) -> None:
        self.database = database
        self.model = model

    def get_model_fields(self) -> t.Dict:
        """

        Get fields set on the realted model as a dict
        """
        return dict(
            (name, field)
            for name, field in vars(
                self.model,
            )["__dataclass_fields__"].items()
        )

    def get_model_columns(self) -> t.List[str]:
        """

        Get related model fields and as a translated
        as database columns.
        """
        cursor = self.database.connection.cursor()

        def get_type_default_arg(field):
            try:
                typ, arg = PYTHON_POSTGRES_TYPES_MAPPING[field.type]
            except KeyError:
                typ, arg = PYTHON_POSTGRES_TYPES_MAPPING[eval(field.type)]

            return typ, arg

        def get_default_value(field):
            default = field.default

            if isinstance(default, _MISSING_TYPE):
                return "NOT NULL"

            return cursor.mogrify(
                "DEFAULT %s",
                (default,),
            ).decode()

        columns = []
        model_fields = self.get_model_fields().items()

        for field_name, field in model_fields:
            _type, _type_arg = get_type_default_arg(field)
            if _type_arg:
                _data_type = f"{_type}({_type_arg})"
            else:
                _data_type = f"{_type}"

            default = get_default_value(field)

            column = f"{field_name} {_data_type} {default}"
            columns.append(column)

        return columns
