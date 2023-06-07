import logging
from typing import Tuple, List, Any, Generator

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from openpyxl.cell import Cell
from openpyxl.cell.read_only import EmptyCell

from uploader.constants import MANDATORY_SHEETS, MAX_YEAR, MIN_YEAR, SEPARATOR
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkEntity:
    errors: dict[int, List[ValidationError]]
    other_errors: dict[int, List[dict]]

    def __init__(self, upload: CofkCollectUpload, sheet):
        self.upload: CofkCollectUpload = upload
        self.sheet = sheet
        self.log_summary: list[str] = []
        self.ids: List[int] = []
        self.errors: dict[int, List[ValidationError]] = {}
        self.other_errors: dict[int, List[dict]] = {}
        self.row: int = 1

    @property
    def fields(self) -> dict:
        return MANDATORY_SHEETS[self.sheet.name]

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
        if 'strings' in self.fields:
            for str_field in [s for s in self.fields['strings'] if
                              (isinstance(s, str) and s in entity and not isinstance(entity[s], str) or
                              isinstance(s, tuple) and s[0] in entity)]:
                if isinstance(str_field, tuple):
                    entity[str_field[0]] = str(entity[str_field[0]]).strip()

                    # People names can be multiple names separated by a semicolon
                    if 'primary_name' == str_field[0]:
                        for value in entity[str_field[0]].split(SEPARATOR):
                            if len(value) > str_field[1]:
                                self.add_error(f'A value in the field {str_field[0]} is longer than the limit of'
                                               f' {str_field[1]} characters.')
                    else:
                        if len(entity[str_field[0]]) > str_field[1]:
                            self.add_error(f'A value in the field {str_field[0]} is longer than the limit of'
                                           f' {str_field[1]} characters.')
                else:
                    entity[str_field] = str(entity[str_field]).strip()

        # ids can be ints or strings that are ints separated by a semicolon and no space
        if 'ids' in self.fields:
            for id_field in [t for t in self.fields['ids'] if t in entity]:
                if isinstance(entity[id_field], int) and entity[id_field] < 1:
                    self.add_error(f'Column {id_field} in {self.sheet.name} sheet is not a valid positive integer.')
                    # self.ids.append(entity[id_field])
                elif isinstance(entity[id_field], str):
                    for int_value in entity[id_field].split(SEPARATOR):
                        try:
                            if int(int_value) < 0:
                                self.add_error(f'Column {id_field} in {self.sheet.name}'
                                               f' sheet contains a non-valid value.')
                            # self.ids.append(int(int_value))
                        except ValueError as ve:
                            self.add_error(f'Column {id_field} in {self.sheet.name}'
                                           f' sheet contains a non-valid value.')

        if 'ints' in self.fields:
            for int_value in [t for t in self.fields['ints'] if t in entity and not isinstance(t, int)]:
                try:
                    entity[int_value] = int(entity[int_value])
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
                if combo[0] in entity and combo[1] in entity and isinstance(entity[combo[0]], str) and\
                        SEPARATOR in entity[combo[0]] or (combo[1] in entity and SEPARATOR in entity[combo[1]]):
                    if len(entity[combo[0]].split(SEPARATOR)) < len(entity[combo[1]].split(SEPARATOR)):
                        self.add_error(f'Column {combo[0]} has fewer ids than there are names in {combo[1]}.')
                    elif len(entity[combo[1]].split(SEPARATOR)) < len(entity[combo[0]].split(SEPARATOR)):
                        self.add_error(f'Column {combo[1]} has fewer names than there are ids in {combo[0]}.')

        if 'years' in self.fields:
            for year_field in [y for y in self.fields['years'] if y in entity]:
                self.check_year(year_field, entity[year_field])

        if 'months' in self.fields:
            for month_field in [m for m in self.fields['months'] if m in entity]:
                self.check_month(month_field, entity[month_field])

        if 'dates' in self.fields:
            for date_field in [m for m in self.fields['dates'] if m in entity]:
                self.check_date(date_field, entity[date_field])

        if 'ranges' in self.fields and 'date_of_work_std_is_range' in entity and\
                entity['date_of_work_std_is_range'] == 1:

            for range_columns in self.fields['ranges'][0]['date_of_work_std_is_range']:
                if range_columns[0] not in entity:
                    self.add_error(f'Column {range_columns[0]} not present but needed when date of work is a range.')
                elif range_columns[1] not in entity:
                    self.add_error(f'Column {range_columns[1]} not present but needed when date of work is a range.')
                elif isinstance(entity[range_columns[0]], int) and isinstance(entity[range_columns[1]], int)\
                        and entity[range_columns[0]] > entity[range_columns[1]]:
                    self.add_error(f'Column {range_columns[0]} can not be greater than {range_columns[1]}.')


    def add_error(self, error_msg: str | None, entity=None, row=None):
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

    def clean_lists(self, entity_dict: dict, ids_key, names_key) -> Tuple[List[int], List[int]]:
        """
        Validates lists of either people or locations and returns a tuple of lists.
        """
        if isinstance(entity_dict[ids_key], str):
            try:
                id_list = [int(i) for i in entity_dict[ids_key].split(SEPARATOR)]
            except ValueError:
                return [], []
        else:
            id_list = [entity_dict[ids_key]]

        name_list = entity_dict[names_key].split(SEPARATOR)

        if '' in id_list:
            self.add_error(f'Empty string in ids in {ids_key}')
        if '' in name_list:
            self.add_error(f'Empty string in names in {names_key}')

        return id_list, name_list

    def bulk_create(self, objects: List[models.Model]):
        if len(objects):
            try:
                type(objects[0]).objects.bulk_create(objects, batch_size=500)
            except IntegrityError as ie:
                log.error(ie)
                self.add_error(f'Could not create {type(objects[0])} objects in database.')

    def check_year(self, year_field: str, year: int):
        if isinstance(year, int) and not MAX_YEAR >= year >= MIN_YEAR:
            self.add_error(f'{year_field}: is {year} but must be between {MIN_YEAR} and {MAX_YEAR}')

    def check_month(self, month_field: str, month: int):
        if isinstance(month, int) and not 1 <= month <= 12:
            self.add_error(f'{month_field}: is {month} but must be between 1 and 12')

    def check_date(self, date_field: str, date: int):
        if date > 31:
            self.add_error(f'{date_field}: is {date} but can not be greater than 31')

        # If month is April, June, September or November then day must be not more than 30
        '''elif month in [4, 6, 9, 11] and field > 30:
            self.add_error('%(field)s: can not be more than 30 for April, June, September or November',
                           {'field': field_name})
        # For February not more than 29
        elif month == 2 and field > 29:
            self.add_error('%(field)s: can not be more than 29 for February', {'field': field_name})'''
