from unittest import mock

from psycopg2.errors import OperationalError

from core.database import Manager
from core.database import create_table

from shared.models import Campaign

from loader.dataloader import DataLoader
from loader.dataloader import RETRY_QUEUE


test_campaign_data = (
    "campaign_id,structure_value,status\n"
    "1578451881,venum,ENABLED\n"
    "1578451584,ellesse,ENABLED\n"
    "1578451386,converse,ENABLED\n"
    "1578412457,wilson,ENABLED\n"
    "9872103720,wham-o,ENABLED\n"
    "9872103720,wham-o,ENABLED\n"
    "1578451386,converse,ENABLED\n"
    "1578451623,spalding,ENABLED\n"
    "1578451386,converse,ENABLED\n"
)


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data=test_campaign_data,
)
def test_save_data(mock_open, testdatabase, droptable):
    droptable("testcampaign")

    class TestCampaign(Campaign):
        ...

    class TestCampaignLoader(DataLoader):
        def get_data_manager(self):
            manager = Manager(
                testdatabase,
                TestCampaign,
            )

            return manager

    create_table(testdatabase, TestCampaign)

    loader = TestCampaignLoader("somefile.csv")
    loader.save_data()

    db_manager = loader.get_data_manager()
    loaded_data = db_manager.find()

    assert loaded_data[0].campaign_id == 1578451881
    assert loaded_data[1].campaign_id == 1578451584
    assert loaded_data[-1].campaign_id == 1578451386


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data=test_campaign_data,
)
@mock.patch.object(Manager, "save", side_effect=OperationalError(""))
def test_save_data_error(mock_save, mock_open, testdatabase, droptable, testqueue):
    droptable("testcampaign")

    class TestCampaign(Campaign):
        ...

    class TestCampaignLoader(DataLoader):
        def get_data_manager(self):
            manager = Manager(
                testdatabase,
                TestCampaign,
            )

            return manager

    create_table(testdatabase, TestCampaign)

    loader = TestCampaignLoader("somefile.csv")
    loader.save_data()

    db_manager = loader.get_data_manager()
    loaded_data = db_manager.find()

    assert not loaded_data
    assert testqueue.qsize() == 5
    assert testqueue.full()

    first_fail = testqueue.get_nowait()

    assert first_fail[0] == TestCampaignLoader
    assert first_fail[1] == {
        "campaign_id": "1578451881",
        "structure_value": "venum",
        "status": "ENABLED",
    }
    assert isinstance(first_fail[2], OperationalError)
