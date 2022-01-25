import typing as t

import sys
import logging


class CSVLoader:
    """

    Service for loading large csv files
    """

    def __init__(self, filename: str, /) -> None:
        """

        filename as the path to the file.
        """
        self.filename = filename

    def readfile(self) -> t.Iterator[str]:
        """

        stream file data
        """
        file = open(self.filename, "r")

        line = file.readline()
        while line:
            yield line.strip()
            line = file.readline()

        file.close()

    @property
    def data(self) -> t.Tuple[t.List[t.Any], t.Iterator[t.List[t.Any]]]:
        """
        get csv header and data as tuple
        """
        raw_file_data = self.readfile()

        header_string = next(raw_file_data)
        header = header_string.split(",")

        def _data():
            while True:
                try:
                    row_data = next(raw_file_data)
                    yield row_data.split(",")
                except StopIteration:
                    break

        return header, _data()


class CSVFrame:
    def __init__(self, filename: str) -> None:
        self.filename = filename

        self.loader = CSVLoader(self.filename)
        self.headers, self.data = self.loader.data

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = next(self.data)
            return item
        except FileNotFoundError as ex:
            logging.error("File %s does not exist.", self.filename)
            raise ex
