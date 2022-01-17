from unittest import mock
import pytest

from core import dataframe


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data="name,age\nSam Jay, 20\nFan Bill, 25",
)
def test_csv_loader_readfile(*args):
    csv_loader = dataframe.CSVLoader("somefile.csv")

    file_data = csv_loader.readfile()

    assert next(file_data) == "name,age"
    assert next(file_data) == "Sam Jay, 20"
    assert next(file_data) == "Fan Bill, 25"

    with pytest.raises(StopIteration):
        next(file_data)


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data="name,age\nSam Jay, 20\nFan Bill, 25",
)
def test_csv_loader_data(*args):
    csv_loader = dataframe.CSVLoader("somefile.csv")

    header, data = csv_loader.data

    assert header == ["name", "age"]
    assert list(data) == [["Sam Jay", " 20"], ["Fan Bill", " 25"]]


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data="name,age\nSam Jay, 20\nFan Bill, 25",
)
def test_csv_frame(*args):
    cf = dataframe.CSVFrame("somefile.csv")

    assert cf.headers == ["name", "age"]
    assert next(cf) == ["Sam Jay", " 20"]
    assert next(cf) == ["Fan Bill", " 25"]

    with pytest.raises(StopIteration):
        next(cf)
