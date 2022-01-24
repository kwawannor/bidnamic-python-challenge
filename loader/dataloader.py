import typing as t

import os
import logging

from abc import ABC
from abc import abstractmethod
from queue import Queue

from psycopg2.errors import OperationalError

from core import database as db
from core import dataframe
from shared import models


RETRY_QUEUE = Queue(maxsize=100)


class BaseDataLoader(ABC):
    def __init__(self, data_source: str) -> None:
        self.data_source = data_source

    @abstractmethod
    def get_database(self) -> None:
        ...

    @abstractmethod
    def get_data_manager(self) -> None:
        ...

    @abstractmethod
    def get_data(self) -> None:
        ...

    @abstractmethod
    def save_data(self) -> None:
        ...

    @abstractmethod
    def load(self) -> None:
        ...


class DataLoader(BaseDataLoader):
    def get_database(self) -> db.Database:
        return init_db()

    def get_data(self) -> t.Generator[t.Any, None, None]:
        df = dataframe.CSVFrame(self.data_source)

        headers = df.headers
        for data in df:
            yield dict(zip(headers, data))

    def save_data(self) -> None:
        model_manager = self.get_data_manager()

        for data in self.get_data():
            try:
                model = model_manager.model(**data)
                model_manager.save(model)
            except OperationalError as ex:
                logging.error(
                    "Error:%s for Loader:%s , Data: %s",
                    repr(ex),
                    self.__class__,
                    data,
                )
                if not RETRY_QUEUE.full():
                    RETRY_QUEUE.put_nowait((self.__class__, data, ex))

    def load(self) -> None:
        self.save_data()


class CampaignLoader(DataLoader):
    def get_data_manager(self) -> db.Manager:
        manager = db.Manager(
            self.get_database(),
            models.Campaign,
        )

        return manager


class AdGroupLoader(DataLoader):
    def get_data_manager(self) -> db.Manager:
        manager = db.Manager(
            self.get_database(),
            models.AdGroup,
        )

        return manager


class SearchTerm(DataLoader):
    def get_data_manager(self) -> db.Manager:
        manager = db.Manager(
            self.get_database(),
            models.SearchTerm,
        )

        return manager


def init_db() -> db.Database:
    return db.Database(
        host=os.environ["DATABASE_HOST"],
        database=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        port=int(os.environ["DATABASE_PORT"]),
    )


def init_loader() -> None:
    database = init_db()

    db.create_table(database, models.Campaign)
    db.create_table(database, models.AdGroup)
    db.create_table(database, models.SearchTerm)
