import typing as t

from contextlib import contextmanager
from contextlib import closing

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
    def transact(self) -> t.Generator[t.Any]:
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
