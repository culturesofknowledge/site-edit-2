import logging
from typing import List, Generator, Tuple

from django.core.exceptions import ValidationError
from openpyxl.cell import Cell

from person.models import CofkCollectPerson, CofkUnionPerson
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload
from work.models import CofkCollectAuthorOfWork, CofkCollectPersonMentionedInWork, CofkCollectAddresseeOfWork

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
        # self.authors: List[CofkCollectAuthorOfWork] = []
        # self.mentioned: List[CofkCollectPersonMentionedInWork] = []
        # self.addressees: List[CofkCollectAddresseeOfWork] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            per_dict = {self.get_column_name_by_index(cell.column): cell.value for cell in row}
            self.check_required(per_dict, index)
            self.check_data_types(per_dict, index)

            if not self.errors:
                if 'iperson_id' in per_dict:
                    per_dict['union_iperson'] = CofkUnionPerson.objects.filter(
                        iperson_id=per_dict['iperson_id']).first()
                    del per_dict['iperson_id']

                per_dict['upload'] = upload
                self.people.append(CofkCollectPerson(**per_dict))

        if self.people:
            CofkCollectPerson.objects.bulk_create(self.people, batch_size=500)

        '''unique_sheet_people = self.process_people_sheet()
        unique_work_people = self.process_work_sheet()

        if len(unique_work_people) > len(unique_sheet_people):
            ppl = [f'{unique_work_people[f]} (#{f})' for f in unique_work_people if f not in unique_sheet_people]
            ppl_joined = ', '.join(ppl)
            plural = 'person is' if len(ppl) == 1 else f'following {len(ppl)} people are'
            tense = 'is' if len(ppl) == 1 else 'are'
            self.add_error(ValidationError(f'The {plural} referenced in the Work spreadsheet'
                                           f' but {tense} missing from the People spreadsheet: {ppl_joined}'))
        elif len(unique_work_people) < len(unique_sheet_people):
            ppl = [f'{unique_sheet_people[f]} (#{f})' for f in unique_sheet_people if f not in unique_work_people]
            ppl_joined = ', '.join(ppl)
            plural = 'person is' if len(ppl) == 1 else f'following {len(ppl)} people are'
            tense = 'is' if len(ppl) == 1 else 'are'
            self.add_error(ValidationError(f'The {plural} referenced in the People spreadsheet'
                                           f' but {tense} missing from the Work spreadsheet: {ppl_joined}'))'''
