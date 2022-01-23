import typing as t

import os

from abc import ABC
from abc import abstractmethod

from core import database as db
from core import dataframe
from shared import models


class BaseDataLoader(ABC):
    def __init__(self, data_source: str) -> None:
        self.data_source = data_source

    @abstractmethod
    def get_database(self) -> None:
        ...

    @abstractmethod
    def get_data_model(self) -> None:
        ...

    @abstractmethod
    def get_data(self) -> None:
        ...

    @abstractmethod
    def save_data(self) -> None:
        ...

    @abstractmethod
    def validate_data(self) -> None:
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
        model_manager = self.get_data_model()

        for data in self.get_data():
            model = model_manager.model(**data)
            model_manager.save(model)

    def load(self) -> None:
        self.save_data()

    async def alaod(self) -> None:
        self.load()

    def validate_data(self) -> bool:
        pass


class CampaignLoader(DataLoader):
    def get_data_model(self) -> db.Manager:
        manager = db.Manager(
            self.get_database(),
            models.Campaign,
        )

        return manager


class AdGroupLoader(DataLoader):
    def get_data_model(self) -> db.Manager:
        manager = db.Manager(
            self.get_database(),
            models.AdGroup,
        )

        return manager


class SearchTerm(DataLoader):
    def get_data_model(self) -> db.Manager:
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
