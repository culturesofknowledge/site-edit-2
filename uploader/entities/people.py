import logging
from typing import List

from person.models import CofkCollectPerson, CofkUnionPerson
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkPeople(CofkEntity):
    def __init__(self, upload: CofkCollectUpload, sheet):
        super().__init__(upload, sheet)
        self.people: List[CofkCollectPerson] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            per_dict = self.get_row(row)
            self.check_required(per_dict, index)
            self.check_data_types(per_dict, index)

            if not self.errors:
                if 'iperson_id' in per_dict and 'primary_name' in per_dict:
                    ids, names = self.clean_lists(per_dict, 'iperson_id', 'primary_name')
                    for _id, name in zip(ids, names):
                        if _id not in self.ids:
                            person = {'iperson_id': _id,
                                      'primary_name': name,
                                      'union_iperson': CofkUnionPerson.objects.filter(iperson_id=_id).first(),
                                      'upload': upload,
                                      'editors_notes': per_dict['editors_notes'] if 'editors_notes' in per_dict else None}
                            self.people.append(CofkCollectPerson(**person))
                            self.ids.append(_id)
                        else:
                            log.warning(f'{_id} duplicated in People sheet.')
                else:
                    log.warning(f'{per_dict} missing an id')

        if self.people:
            self.bulk_create(self.people)
