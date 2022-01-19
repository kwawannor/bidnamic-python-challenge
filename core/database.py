import typing as t

import datetime
import decimal

from contextlib import contextmanager
from contextlib import closing
from dataclasses import dataclass
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

        query
        string, query to execute on server
        args
        sequence or mapping, parameters to use with query.

        """
        with self.transact() as cursor:
            cursor.executemany(query, args)

            return cursor


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

    database = None
    model_registry = OrderedDict()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        Model.model_registry.setdefault(cls.__name__, cls)

    @classmethod
    def manager(cls, database=None):
        return Manager(database or cls.database, cls)


PYTHON_POSTGRES_TYPES_MAPPING = {
    None: ("NULL", None),
    bool: ("bool", None),
    list: ("ARRAY", None),
    int: ("integer", None),
    str: ("varchar", None),
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
