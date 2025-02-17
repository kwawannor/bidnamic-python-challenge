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
from psycopg2.extras import RealDictCursor


from core.utils import iter_to_str


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
            cursor = connection.cursor(cursor_factory=RealDictCursor)
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
            result = cursor.fetchone()["to_regclass"]

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
        fields_database_types = {}
        manager = None

    model_registry = OrderedDict()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        Model.model_registry.setdefault(cls.__name__, cls)

    @classmethod
    def manager(cls, database=None):
        _manager = getattr(cls.Meta, "manager")
        return (_manager or Manager)(
            database or cls.Meta.database,
            cls,
        )


PYTHON_POSTGRES_TYPES_MAPPING = {
    None: ("NULL",),
    bool: ("bool",),
    list: ("ARRAY",),
    int: ("integer",),
    str: ("varchar", "255"),
    float: ("numeric", 2, 2),
    decimal.Decimal: ("decimal",),
    datetime.date: ("date",),
    datetime.time: ("time",),
    datetime.datetime: ("datetime",),
    datetime.timedelta: ("interval",),
}


class Manager:
    """

    Orm driver.
    """

    def __init__(
        self,
        database: Database,
        model: t.Type[Model],
    ) -> None:
        self.database = database
        self.model = model

    @classmethod
    def _where(cls, kwargs):
        if kwargs:
            ands = " AND ".join(f"{k}=%s" for k, v in kwargs.items())
            return f"WHERE {ands}", tuple(kwargs.values())

        return "", ()

    def _modelize(self, **kwargs) -> Model:
        """

        Helper to convert keywords arguments into a model instance.
        If keywords contains 'id' remove and add after model
        object is created.

        """
        id = kwargs.pop("id", None)
        model = self.model(**kwargs)
        model.id = id

        return model

    def get_table_name(self) -> str:
        return getattr(
            self.model.Meta,
            "table_name",
            self.model.__name__.lower(),
        )

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
            custom_types = self.model.Meta.fields_database_types

            if field.name in custom_types:
                typ, *arg = custom_types[field.name]
            else:
                try:
                    typ, *arg = PYTHON_POSTGRES_TYPES_MAPPING[field.type]
                except KeyError:
                    typ, *arg = PYTHON_POSTGRES_TYPES_MAPPING[eval(field.type)]

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
                _data_type = f"{_type}({iter_to_str(_type_arg)})"
            else:
                _data_type = f"{_type}"

            default = get_default_value(field)

            column = f"{field_name} {_data_type} {default}"
            columns.append(column)

        return columns

    def get_models_fields_names(self):
        """

        Get database columns creation expressions.
        """
        fields = self.get_model_fields()

        return ", ".join(f"{_}" for _ in fields.keys())

    def get_pk_column(self) -> str:
        """

        Get PRIMARY KEY creation expression
        """
        return "id serial PRIMARY KEY,"

    def save(self, model) -> Model:
        """

        Insert into DB.
        """
        model_data = model.__dict__

        if model_data.get("id") is not None:
            raise ValueError("object already exist")

        model_values = list(model.__dict__.values())
        model_values_placeholder = ", ".join(_ for _ in ("%s",) * len(model_values))

        query = (
            f"INSERT INTO {self.get_table_name()} "
            f"({self.get_models_fields_names()}) VALUES "
            f"({model_values_placeholder})"
            "RETURNING id;"
        )

        with self.database.transact() as cursor:
            cursor.execute(query, model_values)
            model.id = cursor.fetchone()["id"]

        return model

    def get(self, **kwargs) -> t.Optional[Model]:
        """

        Fetch first one item in database table.
        Keyword arguments are converted into a where query clause.
        """

        results = self.find(**kwargs)
        return results and results[0]

    def find(self, **kwargs) -> t.Optional[Model]:
        """

        Fetch first one item in database table.
        Keyword arguments are converted into a where query clause.
        """

        where_clause, where_args = self._where(kwargs)

        with self.database.transact() as cursor:
            query = f"SELECT * FROM {self.get_table_name()} {where_clause}"

            cursor.execute(query, where_args)
            results = cursor.fetchall()

            return [self._modelize(**r) for r in results]

    def query(
        self,
        query: str,
        args: t.Union[t.Dict[str, str], t.List[str], None] = None,
    ):
        """

        Execute a query.
        """
        with self.database.transact() as cursor:
            cursor.execute(query, args)
            results = cursor.fetchall()

            return [self._modelize(**r) for r in results]


def create_table(database: Database, model: t.Type[Model]) -> None:
    """

    Create schema table.
    """
    manager = Manager(database, model)

    table_name = manager.get_table_name()
    pk_column = manager.get_pk_column()
    columns = ", ".join(manager.get_model_columns())

    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({pk_column} {columns})"
    database.execute(query)
