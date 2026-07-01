import logging
from abc import ABC
from typing import List

from django.db.models import Max

from person.models import CofkUnionPerson
from uploader.constants import BULK_PEOPLE_SHEET, BULK_PEOPLE_HEADER_MAP, normalize_header
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectPerson

log = logging.getLogger(__name__)


class CofkPeople(CofkEntity, ABC):
    """
    This class processes the People spreadsheet
    """
    def __init__(self, upload: CofkCollectUpload, sheet):
        super().__init__(upload, sheet)
        self.people: List[CofkCollectPerson] = []
        latest_iperson_id = CofkCollectPerson.objects.aggregate(Max('iperson_id'))['iperson_id__max'] or 0

        for index, row in enumerate(self.sheet.worksheet.iter_rows(), start=1):
            persons = self.get_row(row, index)

            if index <= self.sheet.header_length or persons == {}:
                continue

            self.check_required(persons)
            self.check_data_types(persons)

            for per_dict in self.clean_lists(persons, 'iperson_id', 'primary_name'):
                if per_dict['iperson_id'] is not None:
                    try:
                        _id = int(per_dict['iperson_id'])
                        per_dict['iperson_id'] = _id  # Update dict with integer value
                    except (ValueError, TypeError):
                        self.add_error(f'Iperson_id "{per_dict["iperson_id"]}" is not a number')
                        continue

                    name = per_dict['primary_name'] if 'primary_name' in per_dict else None

                    """
                    A row in a people sheet can contain any number of semi colon separated people.
                    New people will have a name but not an id.
                    """
                    if _id not in self.ids:
                        person = {'iperson_id': _id,
                                  'primary_name': name,
                                  'union_iperson': CofkUnionPerson.objects.filter(iperson_id=_id).first(),
                                  'upload': upload,
                                  'editors_notes': per_dict[
                                      'editors_notes'] if 'editors_notes' in per_dict else None}

                        if person['union_iperson'] is None:
                            self.add_error(f'There is no person with the id {_id} in the Union catalogue.')

                        self.people.append(CofkCollectPerson(**person))
                        self.ids.append(_id)
                    else:
                        log.warning(f'{_id} duplicated in People sheet.')
                elif not self.person_exists_by_name(per_dict['primary_name']):
                    latest_iperson_id += 1
                    person = {'iperson_id': latest_iperson_id,
                              'primary_name': per_dict['primary_name'],
                              'upload': upload,
                              'editors_notes': per_dict[
                                  'editors_notes'] if 'editors_notes' in per_dict else None}
                    self.people.append(CofkCollectPerson(**person))

    def person_exists_by_name(self, name: str) -> bool:
        return len([p for p in self.people if p.primary_name and p.primary_name.lower() == name.lower() and p.union_iperson is None]) > 0


class CofkBulkPeople(CofkEntity, ABC):
    """
    Processes the bulk People spreadsheet (BULKnewPEOPLErecordsTEMPLATE format).

    All records are treated as new people — no IDs referencing the Union catalogue.
    Columns are mapped by position using BULK_PEOPLE_SHEET.
    """

    @property
    def fields(self) -> dict:
        return BULK_PEOPLE_SHEET

    def __init__(self, upload: CofkCollectUpload, sheet):
        super().__init__(upload, sheet)
        self.people: List[CofkCollectPerson] = []
        latest_iperson_id = CofkCollectPerson.objects.aggregate(Max('iperson_id'))['iperson_id__max'] or 0

        col_to_field = {
            col: BULK_PEOPLE_HEADER_MAP[normalize_header(header)]
            for col, header in self.sheet.header_cols.items()
            if normalize_header(header) in BULK_PEOPLE_HEADER_MAP
        }

        for index, row in enumerate(self.sheet.worksheet.iter_rows(), start=1):
            row_dict = self.get_row_by_header_map(row, index, col_to_field)

            if index <= self.sheet.header_length or row_dict == {}:
                continue

            self.check_required(row_dict)
            self.check_data_types(row_dict)

            if 'primary_name' not in row_dict:
                continue

            primary_name = row_dict['primary_name']

            if self.person_exists_by_name(primary_name):
                log.warning(f'Duplicate person name "{primary_name}" in bulk People sheet, skipping.')
                continue

            latest_iperson_id += 1
            person_kwargs = {
                'iperson_id': latest_iperson_id,
                'upload': upload,
                'primary_name': primary_name,
            }

            _system_fields = {'primary_name', 'upload', 'iperson_id', 'union_iperson'}
            for field, value in row_dict.items():
                if field not in _system_fields:
                    if field == 'alternative_names' and value:
                        person_kwargs[field] = '\n'.join(p.strip() for p in str(value).split(';') if p.strip())
                    else:
                        person_kwargs[field] = value

            self.people.append(CofkCollectPerson(**person_kwargs))

    def person_exists_by_name(self, name: str) -> bool:
        return any(p.primary_name and p.primary_name.lower() == name.lower() for p in self.people)
