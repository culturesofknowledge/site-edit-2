import logging
from typing import Generator, Tuple

import pandas as pd
from django.core.exceptions import ValidationError
from openpyxl.cell import Cell

from uploader.constants import mandatory_sheets
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkEntity:
    def __init__(self, upload: CofkCollectUpload, sheet_data: Generator[Tuple[Cell], None, None]):
        self.upload = upload
        self.sheet_data = sheet_data
        self.row_data = None
        self.errors = {}
        self.other_errors = {}
        self.row = 1

    def check_data_types(self, sheet_name: str):
        sheet = [s for s in mandatory_sheets if s['name'] == sheet_name][0]

        if 'ints' in sheet:
            for test_int_column in [t for t in sheet['ints'] if t in self.row_data]:
                try:
                    int(self.row_data[test_int_column])
                except ValueError as ve:
                    msg = f'Column {test_int_column} in {sheet_name} sheet is not a valid integer.'
                    log.error(msg)
                    self.add_error(ValidationError(msg))

        if 'bools' in sheet:
            for test_bool_column in [t for t in sheet['bools'] if t in self.row_data]:
                try:
                    if int(self.row_data[test_bool_column]) not in [0, 1]:
                        msg = f'Column {test_bool_column} in {sheet_name} sheet is not a boolean value of either 0 or 1.'
                        log.error(msg)
                        self.add_error(ValidationError(msg))
                except ValueError as ve:
                    msg = f'Column {test_bool_column} in {sheet_name} sheet is not a boolean value of either 0 or 1.'
                    log.error(msg)
                    self.add_error(ValidationError(msg))

    def add_error(self, error: ValidationError, entity=None, row=None):
        """

        """
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
