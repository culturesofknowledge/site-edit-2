import datetime
import logging
from typing import List, Generator

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from openpyxl.cell import Cell
from openpyxl.cell.read_only import EmptyCell

from uploader.constants import MANDATORY_SHEETS, MAX_YEAR, MIN_YEAR, SEPARATOR
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


def int_or_empty_string(value) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        if value == '':
            return True

    return False


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

    def has_valid_value(self, cell: Cell):
        column_count = len(self.fields['columns'])
        return (not isinstance(cell, EmptyCell) and cell.column <= column_count
                and cell.value is not None and cell.value != '')

    def get_row(self, row: Generator[Cell, None, None], row_number: int) -> dict:
        self.row = row_number
        return {self.get_column_name_by_index(cell.column): cell.value for cell in row if self.has_valid_value(cell)}

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
                                val_len = len(value)
                                self.add_error(f'A value in the field {str_field[0]} is {val_len} '
                                               f'characters, which is longer than the limit of '
                                               f'{str_field[1]} characters.')
                    else:
                        if len(entity[str_field[0]]) > str_field[1]:
                            val_len = len(entity[str_field[0]])
                            self.add_error(f'A value in the field {str_field[0]} is {val_len} '
                                           f'characters, which is longer than the limit of '
                                           f'{str_field[1]} characters.')
                else:
                    entity[str_field] = str(entity[str_field]).strip()

        # ids can be ints or strings that are ints separated by a semicolon and no space
        if 'ids' in self.fields:
            for id_field in [t for t in self.fields['ids'] if t in entity]:
                if isinstance(entity[id_field], int) and entity[id_field] < 1:
                    self.add_error(f'Column {id_field} in {self.sheet.name} sheet is not'
                                   f' a valid positive integer (value: {entity[id_field]}).')
                elif isinstance(entity[id_field], str):
                    for int_value in [i for i in entity[id_field].split(SEPARATOR) if i != '']:
                        try:
                            if int(int_value) < 1:
                                self.add_error(f'Column {id_field} in {self.sheet.name}'
                                               f' sheet contains an invalid value (value: {int_value}).')
                        except ValueError:
                            self.add_error(f'Column {id_field} in {self.sheet.name}'
                                           f' sheet contains an invalid value (value: {int_value}).')

        if 'ints' in self.fields:
            for int_value in [t for t in self.fields['ints'] if t in entity and not isinstance(entity[t], int)]:
                try:
                    entity[int_value] = int(entity[int_value])
                except ValueError:
                    self.add_error(f'Column {int_value} in {self.sheet.name} sheet is not'
                                   f' a valid integer (value: {entity[int_value]}).')

        if 'bools' in self.fields:
            for bool_value in [t for t in self.fields['bools'] if t in entity]:
                try:
                    if int(entity[bool_value]) not in [0, 1]:
                        self.add_error(f'Column {bool_value} in {self.sheet.name} sheet'
                                       f' is not a boolean value of either 0 or 1 (value: {entity[bool_value]}).')
                except ValueError:
                    self.add_error(f'Column {bool_value} in {self.sheet.name}'
                                   f' sheet is not a boolean value of either 0 or 1 (value: {entity[bool_value]}).')

        if 'combos' in self.fields:
            for combo in self.fields['combos']:
                if combo[0] in entity and combo[1] in entity and isinstance(entity[combo[0]], str) and \
                        (SEPARATOR in entity[combo[0]] or (combo[1] in entity and SEPARATOR in entity[combo[1]])):
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
                month_field = date_field.replace('_day', '_month')
                self.check_date(date_field, entity[date_field], entity.get(month_field))

        if 'ranges' in self.fields and 'date_of_work_std_is_range' in entity and \
                entity['date_of_work_std_is_range'] == 1:
            for range_columns in self.fields['ranges'][0]['date_of_work_std_is_range']:
                log.info(range_columns)
                if range_columns[0] not in entity:
                    self.add_error(f'Column {range_columns[0]} not present but needed when date of work is a range.')
                elif range_columns[1] not in entity:
                    self.add_error(f'Column {range_columns[1]} not present but needed when date of work is a range.')
                elif isinstance(entity[range_columns[0]], int) and isinstance(entity[range_columns[1]], int) \
                        and entity[range_columns[0]] > entity[range_columns[1]]:
                    self.add_error(f'Column {range_columns[0]} can not be greater than {range_columns[1]}.')
            self.check_date_range(entity)

        if 'notes' in self.fields:
            for notes_field in [n for n in self.fields['notes'] if n in entity and entity[n]]:
                self.check_notes(notes_field, entity[notes_field])

        if 'place_pairs' in self.fields:
            for id_field, name_field in self.fields['place_pairs']:
                self.check_place(id_field, name_field, entity)

        if 'keywords' in self.fields:
            for kw_field in [k for k in self.fields['keywords'] if k in entity and entity[k]]:
                self.check_keywords(kw_field, entity[kw_field])

        if 'shelfmarks' in self.fields:
            for shelfmark_field in [s for s in self.fields['shelfmarks'] if s in entity and entity[s]]:
                self.check_shelfmark(shelfmark_field, entity[shelfmark_field])

        if 'bibliographies' in self.fields:
            for bib_field in [b for b in self.fields['bibliographies'] if b in entity and entity[b]]:
                self.check_bibliography(bib_field, entity[bib_field])

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

    def clean_lists(self, entity_dict: dict, ids_key: str, names_key: str) -> List[dict]:
        """
        Validates lists of either people or locations and returns a tuple of lists.
        """
        ids = None
        names = None

        # Ids are normalised as a list of strings
        if ids_key in entity_dict:
            if isinstance(entity_dict[ids_key], str):
                ids = entity_dict[ids_key].split(SEPARATOR)
            else:
                ids = [str(entity_dict[ids_key])]

        # Names are normalised as a list of strings
        if names_key in entity_dict and isinstance(entity_dict[names_key], str):
            names = entity_dict[names_key].split(SEPARATOR)

        if names is None:
            return [{ids_key: _id, names_key: None} for _id in ids]
        elif ids is None:
            return [{ids_key: None, names_key: name} for name in names]
        elif len(names) < len(ids):
            return [{ids_key: _id, names_key: names[ix] if ix < len(names) else None} for ix, _id in enumerate(ids)]
        elif len(names) > len(ids):
            return [{ids_key: ids[ix] if ix < len(ids) else None, names_key: name} for ix, name in
                    enumerate(names)]

        return [{ids_key: _id, names_key: name} for _id, name in zip(ids, names)]

    def bulk_create(self, objects: List[models.Model]):
        if len(objects):
            try:
                type(objects[0]).objects.bulk_create(objects, batch_size=500)
            except IntegrityError as ie:
                log.error(ie)
                self.add_error(f'Could not create {type(objects[0])} objects in database.')

    def check_year(self, year_field: str, year: int):
        if isinstance(year, int) and not MAX_YEAR >= year >= MIN_YEAR:
            self.add_error(f'{year_field}: is {year} but must be between {MIN_YEAR} and {MAX_YEAR}.')

    def check_month(self, month_field: str, month: int):
        if isinstance(month, int) and not 1 <= month <= 12:
            self.add_error(f'{month_field}: is {month} but must be between 1 and 12.')

    def check_date(self, date_field: str, date: int, month: int = None):
        if date > 31:
            self.add_error(f'{date_field}: is {date} but can not be greater than 31.')
        elif month is not None and isinstance(month, int):
            if month in [4, 6, 9, 11] and date > 30:
                self.add_error(f'{date_field}: is {date} but must be 30 or less for April, June, September or November.')
            elif month == 2 and date > 29:
                self.add_error(f'{date_field}: is {date} but must be 29 or less for February.')

    def check_date_range(self, entity: dict):
        y1 = entity.get('date_of_work_std_year')
        m1 = entity.get('date_of_work_std_month')
        d1 = entity.get('date_of_work_std_day')
        y2 = entity.get('date_of_work2_std_year')
        m2 = entity.get('date_of_work2_std_month')
        d2 = entity.get('date_of_work2_std_day')

        if not (isinstance(y1, int) and isinstance(y2, int)):
            return

        if all(isinstance(v, int) for v in [m1, d1, m2, d2]):
            try:
                if datetime.datetime(y1, m1, d1) >= datetime.datetime(y2, m2, d2):
                    self.add_error('The start date in a date range can not be after the end date.')
            except ValueError:
                pass
        elif isinstance(m1, int) and isinstance(m2, int):
            if (y1, m1) > (y2, m2):
                self.add_error('The start date in a date range can not be after the end date.')

    def check_notes(self, field: str, value: str):
        if value[0].islower():
            self.add_error(f'{field}: Notes must start with an upper case letter.')
        if value[-1] != '.':
            self.add_error(f'{field}: Notes must end with a full stop.')

    def check_place(self, id_field: str, name_field: str, entity: dict):
        place_id = entity.get(id_field)
        place_name = entity.get(name_field)

        if not (place_id or place_name):
            self.add_error(f'There is neither a {id_field} nor a {name_field}.')
        elif place_name and not place_id and place_name.strip().lower() == 'unknown':
            self.add_error(f'{name_field}: must not be "unknown" without a corresponding id.')

    def check_keywords(self, field: str, value: str):
        if len(value.split('; ')) - 1 != value.count(';'):
            self.add_error(f'{field}: Keywords must be separated with "; " (semicolon followed by a space).')

    def check_shelfmark(self, field: str, value: str):
        if '-' in value:
            self.add_error(f'{field}: Use an en dash between folio numbers, not a hyphen.')
        if value.endswith('.'):
            self.add_error(f'{field}: There should not be a full stop at the end of a shelfmark.')

    def check_bibliography(self, field: str, value: str):
        if value.endswith('.'):
            self.add_error(f'{field}: There should not be a full stop at the end of bibliographic details.')
        if '-' in value and '–' not in value:
            self.add_error(f'{field}: Use en dashes for page ranges, not hyphens.')
