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

        for index, row in enumerate(self.iter_rows(), start=1 + self.sheet.header_length):
            per_dict = self.get_row(row, index)
            self.check_required(per_dict)
            self.check_data_types(per_dict)

            if 'iperson_id' in per_dict and 'primary_name' in per_dict:
                ids, names = self.clean_lists(per_dict, 'iperson_id', 'primary_name')
                for _id, name in zip(ids, names):
                    if _id not in self.ids:
                        person = {'iperson_id': _id,
                                  'primary_name': name,
                                  'union_iperson': CofkUnionPerson.objects.filter(iperson_id=_id).first(),
                                  'upload': upload,
                                  'editors_notes': per_dict[
                                      'editors_notes'] if 'editors_notes' in per_dict else None}
                        self.people.append(CofkCollectPerson(**person))
                        self.ids.append(_id)
                    else:
                        log.warning(f'{_id} duplicated in People sheet.')

