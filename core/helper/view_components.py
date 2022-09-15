from pathlib import Path
from typing import Iterable

import csv


class DownloadCsvHandler:
    """ define how to convert objects to csv rows
    """

    @staticmethod
    def get_delimiter() -> str:
        return ','

    def get_header_list(self) -> list[str]:
        raise NotImplementedError('missing csv header list')

    def obj_to_values(self, obj) -> Iterable[str]:
        raise NotImplementedError('missing obj_to_csv_row')

    def create_csv_file(self, file_path: str | Path, objects: Iterable):
        writer = csv.writer(open(file_path, 'w'), delimiter=self.get_delimiter())
        writer.writerow(self.get_header_list())
        writer.writerows(map(self.obj_to_values, objects))
