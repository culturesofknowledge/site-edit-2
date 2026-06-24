import logging
from abc import ABC
from typing import List

from django.db.models import Max

from person.models import CofkUnionPerson
from uploader.constants import BULK_PEOPLE_SHEET
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
                    log.info(per_dict['primary_name'] + "  " + str(latest_iperson_id))
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

        for index, row in enumerate(self.sheet.worksheet.iter_rows(), start=1):
            row_dict = self.get_row(row, index)

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

            for field in ['alternative_names', 'roles_or_titles', 'gender', 'is_organisation',
                          'date_of_birth_year', 'date_of_birth_inferred', 'date_of_birth_uncertain',
                          'date_of_birth_approx', 'date_of_death_year', 'date_of_death_inferred',
                          'date_of_death_uncertain', 'date_of_death_approx',
                          'flourished_year', 'flourished2_year', 'flourished_is_range',
                          'notes_on_person', 'editors_notes']:
                if field in row_dict:
                    person_kwargs[field] = row_dict[field]

            self.people.append(CofkCollectPerson(**person_kwargs))

    def person_exists_by_name(self, name: str) -> bool:
        return any(p.primary_name and p.primary_name.lower() == name.lower() for p in self.people)
