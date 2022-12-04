import logging
from typing import Generator, Tuple, Union, List, Any

import pandas as pd
from django.core.exceptions import ValidationError
from openpyxl.cell import Cell
from openpyxl.cell.read_only import EmptyCell

from uploader.constants import mandatory_sheets
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkEntity:
    def __init__(self, upload: CofkCollectUpload, sheet_data: Generator[Tuple[Cell], None, None],
                 sheet_name: str):
        self.upload: CofkCollectUpload = upload
        self.sheet_data: Generator[Tuple[Cell], None, None] = sheet_data
        self.sheet_name: str = sheet_name
        self.ids: List[int] = []
        self.ids_to_be_created: List[int] = []
        self.row_data = None
        self.errors = {}
        self.other_errors = {}
        self.row = 1

    @property
    def fields(self):
        return mandatory_sheets[self.sheet_name]

    def get_column_name_by_index(self, index: int) -> str:
        # openpyxl starts column count at 1
        return self.fields['columns'][index - 1]

    def iter_rows(self):
        return ((c for c in r if not isinstance(c, EmptyCell)
                 and c.column <= len(self.fields['columns'])) for r in self.sheet_data)

    def get_column_by_name(self, name: str) -> List[Any]:
        return [[c.value for c in r if not isinstance(c, EmptyCell) and c.column <= len(self.fields['columns'])
                 and self.get_column_name_by_index(c.column) == name][0] for r in self.sheet_data]

    def get_all_values_by_column_name(self, name: str) -> List[int]:
        values = []
        for v in self.get_column_by_name(name):
            if isinstance(v, int):
                values.append(v)
            elif isinstance(v, str):
                values += [int(i) for i in v.split(';')]
            else:
                log.warning(f'Value in {name} of {self.sheet_name} is {v}')

        return values

    def check_required(self, entity: dict, row_number: int):
        for missing in [m for m in self.fields['required'] if m not in entity]:
            msg = f'Column {missing} in {self.sheet_name} is missing.'
            log.error(msg)
            self.add_error(ValidationError(msg), row_number)

    def check_data_types(self, entity: dict, row_number: int):
        self.row = row_number
        log.debug(entity)

        # ids can be ints or strings that are ints separated by a semicolon and no space
        if 'ids' in self.fields:
            for id_value in [t for t in self.fields['ids'] if t in entity]:
                if isinstance(entity[id_value], int) and entity[id_value] > 0:
                    self.ids.append(entity[id_value])
                elif isinstance(entity[id_value], str):
                    for int_value in entity[id_value].split(';'):
                        try:
                            if int(int_value) < 0:
                                raise ValueError()

                            self.ids.append(int(int_value))
                        except ValueError as ve:
                            msg = f'Column {int_value} in {self.sheet_name} sheet is not a valid positive integer.'
                            log.error(msg)
                            self.add_error(ValidationError(msg))
                else:
                    msg = f'Column {entity[id_value]} in {self.sheet_name} sheet is not a valid positive integer.'
                    log.error(msg)
                    self.add_error(ValidationError(msg))

        if 'ints' in self.fields:
            for int_value in [t for t in self.fields['ints'] if t in entity and not isinstance(t, int)]:
                try:
                    int(entity[int_value])
                except ValueError as ve:
                    msg = f'Column {int_value} in {self.sheet_name} sheet is not a valid integer.'
                    log.error(msg)
                    self.add_error(ValidationError(msg))

        if 'bools' in self.fields:
            for bool_value in [t for t in self.fields['bools'] if t in self.row_data]:
                try:
                    if int(entity[bool_value]) not in [0, 1]:
                        msg = f'Column {bool_value} in {self.sheet_name} sheet is not a boolean value of either 0 or 1.'
                        log.error(msg)
                        self.add_error(ValidationError(msg))
                except ValueError as ve:
                    msg = f'Column {bool_value} in {self.sheet_name} sheet is not a boolean value of either 0 or 1.'
                    log.error(msg)
                    self.add_error(ValidationError(msg))

        if 'combos' in self.fields:
            for combo in self.fields['combos']:
                if isinstance(entity[combo[0]], str) and ';' in entity[combo[0]] or ';' in entity[combo[1]]:
                    if len(entity[combo[0]].split(';')) < len(entity[combo[1]].split(';')):
                        msg = f'Column {combo[0]} has fewer ids than there are names in {combo[1]}.'
                        log.error(msg)
                        self.add_error(ValidationError(msg))
                    elif len(entity[combo[1]].split(';')) < len(entity[combo[0]].split(';')):
                        # TODO this should be a warning
                        msg = f'Column {combo[1]} has fewer names than there are ids in {combo[0]}.'
                        log.error(msg)
                        self.add_error(ValidationError(msg))

        if 'strings' in self.fields:
            for str_field in self.fields['strings']:
                log.debug(str_field)

    def add_error(self, error: ValidationError, entity=None, row=None):
        if not row:
            row = self.row

        if entity:
            if self.row not in self.other_errors:
                self.other_errors[row] = []

            self.other_errors[row].append({'entity': entity, 'error': error})
            return

        if self.row not in self.errors:
            self.errors[row] = []

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
