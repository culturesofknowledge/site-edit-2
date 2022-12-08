import logging
from typing import Tuple, List, Any, Type, Generator

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from openpyxl.cell import Cell
from openpyxl.cell.read_only import EmptyCell

from uploader.constants import mandatory_sheets
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkEntity:
    def __init__(self, upload: CofkCollectUpload, sheet):
        self.upload: CofkCollectUpload = upload
        self.sheet = sheet
        self.ids: List[int] = []
        self.errors: dict = {}
        self.other_errors: dict = {}
        self.row: int = 1

    @property
    def fields(self) -> dict:
        return mandatory_sheets[self.sheet.name]

    def get_column_name_by_index(self, index: int) -> str:
        # openpyxl starts column count at 1
        return self.fields['columns'][index - 1]

    def iter_rows(self) -> Generator[Generator[Cell, None, None], None, None]:
        return ((c for c in r if not isinstance(c, EmptyCell)
                 and c.column <= len(self.fields['columns'])) for r in self.sheet.data)

    def get_row(self, row: Generator[Cell, None, None], row_number: int) -> dict:
        self.row = row_number
        return {self.get_column_name_by_index(cell.column): cell.value for cell in row if cell.value is not None}

    def get_column_by_name(self, name: str) -> List[Any]:
        return [[c.value for c in r if not isinstance(c, EmptyCell) and c.column <= len(self.fields['columns'])
                 and self.get_column_name_by_index(c.column) == name][0] for r in self.sheet.data]

    def check_required(self, entity: dict):
        for missing in [m for m in self.fields['required'] if m not in entity]:
            self.add_error(f'Column {missing} in {self.sheet.name} is missing.')

    def check_data_types(self, entity: dict):
        log.debug(f'Checking data type: {self.sheet.name}, row {self.row}')

        if 'strings' in self.fields:
            for str_field in [s for s in self.fields['strings'] if
                              (isinstance(s, str) and s in entity and not isinstance(entity[s], str) or
                              isinstance(s, tuple) and s[0] in entity)]:
                if isinstance(str_field, tuple):
                    entity[str_field[0]] = str(entity[str_field[0]])

                    if len(entity[str_field[0]]) > str_field[1]:
                        self.add_error(f'The field {str_field[0]} is longer than the limit of {str_field[1]} '
                                       f'characters for that field.')
                else:
                    entity[str_field] = str(entity[str_field])

        # ids can be ints or strings that are ints separated by a semicolon and no space
        if 'ids' in self.fields:
            for id_field in [t for t in self.fields['ids'] if t in entity]:
                log.debug(f'----{id_field}')
                if isinstance(entity[id_field], int) and entity[id_field] < 1:
                    self.add_error(f'Column {id_field} in {self.sheet.name} sheet is not a valid positive integer.')
                    # self.ids.append(entity[id_field])
                elif isinstance(entity[id_field], str):
                    for int_value in entity[id_field].split(';'):
                        try:
                            if int(int_value) < 0:
                                self.add_error(f'Column {id_field} in {self.sheet.name}'
                                               f' sheet is not a valid positive integer.')
                            # self.ids.append(int(int_value))
                        except ValueError as ve:
                            self.add_error(f'Column {id_field} in {self.sheet.name}'
                                           f' sheet is not a valid positive integer.')

        if 'ints' in self.fields:
            for int_value in [t for t in self.fields['ints'] if t in entity and not isinstance(t, int)]:
                try:
                    int(entity[int_value])
                except ValueError as ve:
                    self.add_error(f'Column {int_value} in {self.sheet.name} sheet is not a valid integer.')

        if 'bools' in self.fields:
            for bool_value in [t for t in self.fields['bools'] if t in entity]:
                try:
                    if int(entity[bool_value]) not in [0, 1]:
                        self.add_error(f'Column {bool_value} in {self.sheet.name} sheet'
                                       f' is not a boolean value of either 0 or 1.')
                except ValueError as ve:

                    self.add_error(f'Column {bool_value} in {self.sheet.name}'
                                   f' sheet is not a boolean value of either 0 or 1.')

        if 'combos' in self.fields:
            for combo in self.fields['combos']:
                log.debug(f'---- {combo}')
                if combo[0] in entity and isinstance(entity[combo[0]], str) and ';' in entity[combo[0]]\
                        or (combo[1] in entity and ';' in entity[combo[1]]):
                    if len(entity[combo[0]].split(';')) < len(entity[combo[1]].split(';')):
                        self.add_error(f'Column {combo[0]} has fewer ids than there are names in {combo[1]}.')
                    elif len(entity[combo[1]].split(';')) < len(entity[combo[0]].split(';')):
                        self.add_error(f'Column {combo[1]} has fewer names than there are ids in {combo[0]}.')

        if 'years' in self.fields:
            for year_field in [y for y in self.fields['years'] if y in entity]:
                self.check_year(year_field, entity[year_field])

        if 'months' in self.fields:
            for month_field in [m for m in self.fields['months'] if m in entity]:
                self.check_month(month_field, entity[month_field])

        if 'dates' in self.fields:
            for date_field in [m for m in self.fields['months'] if m in entity]:
                self.check_date(date_field, entity[date_field])

    def add_error(self, error_msg: str, entity=None, row=None):
        if not row:
            row = self.row

        error = ValidationError(error_msg)

        if entity:
            if self.row not in self.other_errors:
                self.other_errors[row] = []

            self.other_errors[row].append({'entity': entity, 'error': error})
            return

        if self.row not in self.errors:
            self.errors[row] = []

        log.error(error.message)

        self.errors[row].append(error)

    def format_errors_for_template(self) -> dict:
        errors = []
        total_errors = 0

        for k, value_array in self.errors.items():
            row_errors = []
            for v in value_array:
                if hasattr(v, 'error_dict'):
                    if '__all__' in v.error_dict:
                        row_errors += [str(e)[2:-2] for e in v.error_dict['__all__']]
                    else:
                        row_errors += [str(e) for e in v]
                if hasattr(v, 'message'):
                    row_errors += [str(e) for e in v]

            total_errors += len(row_errors)
            errors.append({'row': k, 'errors': row_errors})

        return {'errors': errors,
                'total': total_errors}

    def clean_lists(self, entity_dict: dict, ids, names) -> Tuple[List[int], List[int]]:
        if isinstance(entity_dict[ids], str):
            try:
                id_list = [int(i) for i in entity_dict[ids].split(';')]
            except ValueError:
                return [], []
        else:
            id_list = [entity_dict[ids]]

        name_list = entity_dict[names].split(';')

        if len(id_list) < len(name_list):
            self.add_error(f'Fewer ids in {ids} than names in {names}.')
        elif len(id_list) > len(name_list):
            self.add_error(f'Fewer names in {names} than ids in {ids}')

        if '' in id_list:
            self.add_error(f'Empty string in ids in {ids}')
        if '' in name_list:
            self.add_error(f'Empty string in names in {names}')

        return id_list, name_list

    def bulk_create(self, objects: List[Type[models.Model]]):
        try:
            type(objects[0]).objects.bulk_create(objects, batch_size=500)
        except IntegrityError as ie:
            log.error(ie)
            self.add_error('Could not create objects in database.')

    def check_year(self, year_field: str, year: int):
        raise NotImplementedError()

    def check_month(self, month_field: str, month: int):
        raise NotImplementedError()

    def check_date(self, date_field: str, date: int):
        raise NotImplementedError()
