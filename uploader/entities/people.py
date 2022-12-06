import logging
from typing import List, Generator, Tuple

from openpyxl.cell import Cell

from person.models import CofkCollectPerson, CofkUnionPerson
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkPeople(CofkEntity):
    """
    This class process the People sheet in the uploaded workbook by creating entries in the
    CofkCollectPerson table.

    At a later stage, these entries are cross-referenced in the tables CofkCollectAuthorOfWork,
    CofkCollectPersonMentionedInWork and CofkCollectAddresseeOfWork.

    This means that the People sheet needs to be processed before the Work sheet. The Work sheet
    contains information about the nature of the relation (which of the above tables to link to).
    """
    def __init__(self, upload: CofkCollectUpload, sheet_data: Generator[Tuple[Cell], None, None],
                 work_data: Generator[Tuple[Cell], None, None], sheet_name: str):
        """
        sheet_data: all data from the "People" sheet
        word_data: all data from the "Work" sheet, from which a few columns are required
        # TODO editor's notes from people sheet need to be added
        """
        super().__init__(upload, sheet_data, sheet_name)
        self.work_data = work_data

        self.people: List[CofkCollectPerson] = []
        self._ids: List[int] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            per_dict = {self.get_column_name_by_index(cell.column): cell.value for cell in row}
            self.check_required(per_dict, index)
            self.check_data_types(per_dict, index)

            if not self.errors:
                ids, names = self.clean_lists(per_dict, 'iperson_id', 'primary_name')
                for _id, name in zip(ids, names):
                    if _id not in self._ids:
                        person = {'iperson_id': _id,
                                  'primary_name': name,
                                  'union_iperson': CofkUnionPerson.objects.filter(iperson_id=_id).first(),
                                  'upload': upload,
                                  'editors_notes': per_dict['editors_notes'] if 'editors_notes' in per_dict else None}
                        self.people.append(CofkCollectPerson(**person))
                        self._ids.append(_id)
                    else:
                        log.warning(f'{_id} duplicated in People sheet.')

        if self.people:
            self.bulk_create(self.people)
