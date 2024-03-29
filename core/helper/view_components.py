import csv
from pathlib import Path
from typing import Iterable, Any, Callable

from cllib import data_utils


class HeaderValues:
    def get_header_list(self) -> list[str]:
        raise NotImplementedError('missing header list')

    def obj_to_values(self, obj) -> Iterable:
        """
        convert object to values of columns
        """
        raise NotImplementedError('missing obj_to_values')


class DownloadCsvHandler:
    """ define how to convert objects to CSV file for export features
    """

    def __init__(self, header_values: HeaderValues):
        self.header_values = header_values

    @staticmethod
    def get_delimiter() -> str:
        return ','

    @staticmethod
    def _obj_to_str_values(obj_to_values: Callable, obj) -> Iterable[str]:
        values = obj_to_values(obj)
        values = data_utils.to_str_list_no_none(values)
        return map(str, values)

    def create_csv_file(self, objects: Iterable, file_path: str | Path):
        with open(file_path, 'w') as f:
            writer = csv.writer(f, delimiter=self.get_delimiter())
            writer.writerow(self.header_values.get_header_list())
            writer.writerows((self._obj_to_str_values(self.header_values.obj_to_values, obj)
                              for obj in objects))


class DownloadExcelHandler:
    """ define how to convert objects to Excel file for export features
    """

    def get_header_list(self) -> list[str]:
        raise NotImplementedError('missing excel header list')

    def obj_to_values(self, obj) -> Iterable[Any]:
        raise NotImplementedError('missing obj_to_excel_row')

    def obj_to_str_values(self, obj) -> Iterable[str]:
        values = (v if v is not None else '' for v in self.obj_to_values(obj))
        return map(str, values)

    def create_excel_file(self, file_path: str | Path, objects: Iterable):
        raise NotImplementedError('missing create_excel_file')
