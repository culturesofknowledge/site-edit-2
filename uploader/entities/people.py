import logging
from abc import ABC
from typing import List

from person.models import CofkUnionPerson
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
        iperson_ids = list(CofkCollectPerson.objects.values_list('iperson_id').order_by('-iperson_id')[:1])
        latest_iperson_id = iperson_ids[0][0] if len(iperson_ids) == 1 else 0

        for index, row in enumerate(self.sheet.worksheet.iter_rows(), start=1):
            persons = self.get_row(row, index)

            if index <= self.sheet.header_length or persons == {}:
                continue

            self.check_required(persons)
            self.check_data_types(persons)

            for per_dict in self.clean_lists(persons, 'iperson_id', 'primary_name'):
                if 'iperson_id' in per_dict and per_dict['iperson_id'] is not None:
                    _id = per_dict['iperson_id']
                    name = per_dict['primary_name'] if 'primary_name' in per_dict else None

                    try:
                        int(_id)
                    except ValueError:
                        self.add_error(f'Iperson_id "{_id}" is not a number')
                        continue

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
                    elif name and not self.person_exists_by_name(name):
                        latest_iperson_id += 1
                        person = {'iperson_id': latest_iperson_id,
                                  'primary_name': name,
                                  'upload': upload,
                                  'editors_notes': per_dict[
                                      'editors_notes'] if 'editors_notes' in per_dict else None}
                        self.people.append(CofkCollectPerson(**person))
                    else:
                        log.info(f'{_id} duplicated in People sheet.')
                elif 'primary_name' in per_dict and not self.person_exists_by_name(per_dict['primary_name']):
                    latest_iperson_id += 1
                    person = {'iperson_id': latest_iperson_id,
                              'primary_name': per_dict['primary_name'],
                              'upload': upload,
                              'editors_notes': per_dict[
                                  'editors_notes'] if 'editors_notes' in per_dict else None}
                    self.people.append(CofkCollectPerson(**person))

    def person_exists_by_name(self, name: str) -> bool:
        return len([p for p in self.people if p.primary_name.lower() == name.lower() and p.union_iperson is None]) > 0
