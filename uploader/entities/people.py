import numpy as np
import pandas as pd
from django.core.exceptions import ValidationError

from person.models import CofkCollectPerson
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload


class CofkPeople(CofkEntity):
    """
    This class process the People sheet in the uploaded workbook.
    """

    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, work_data: pd.DataFrame):
        """
        sheet_data: all data from the "People" sheet
        word_data: all data from the "Work" sheet, from which a few columns are required
        # TODO editor's notes from people sheet need to be added
        """
        super().__init__(upload, sheet_data)
        self.upload_id = upload.upload_id
        self.work_data = work_data

        self.ids = []

        sheet_people = []
        work_people = []

        # Get all people from people spreadsheet
        for i in range(1, len(self.sheet_data.index)):
            self.row_data = {k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None}

            self.check_data_types('People')
            # TODO handle multiple people in same row
            iperson_id = self.row_data['iperson_id'] if 'iperson_id' in self.row_data else None
            sheet_people.append((self.row_data['primary_name'], iperson_id))

        # Get all people from references in Work spreadsheet
        for i in range(1, len(work_data.index)):
            row = work_data.iloc[i].to_dict()
            # log.debug(row)
            # TODO handle multiple people in same row
            if row['author_names']:
                work_people.append((row['author_names'], row['author_ids']))

            if row['addressee_names']:
                work_people.append((row['addressee_names'], row['addressee_ids']))

            if row['mention_id']:
                work_people.append((row['mention_id'], row['emlo_mention_id']))

        unique_sheet_people = set(sheet_people)
        unique_work_people = set(work_people)

        if unique_work_people > unique_sheet_people:
            ppl = [f'{p[0]} #{p[1]}' for p in list(unique_sheet_people - unique_work_people)]
            ppl_joined = ', '.join(ppl)
            self.add_error(ValidationError(f'The person {ppl_joined} is referenced in the Work spreadsheet but is '
                                           f'missing from the People spreadsheet'))
        elif unique_work_people < unique_sheet_people:
            ppl = [str(p) for p in list(unique_work_people - unique_sheet_people)]
            ppl_joined = ', '.join(ppl)
            self.add_error(ValidationError(f'The person {ppl_joined} is referenced in the People spreadsheet but is '
                                           f'missing from the Work spreadsheet'))

        for p in [p for p in list(unique_work_people.union(unique_sheet_people)) if p[1] is not None]:
            try:
                if CofkCollectPerson.objects.filter(iperson_id=p[1], upload_id=upload.upload_id).exists():
                    self.add_error(ValidationError(f'The person {p[0]} #{p[1]} is referenced in either the Work or the'
                                                   f' People spreadsheet but does not exist'))
            except ValueError:
                # Will fail if iperson_id column in People sheet contains incorrect data type
                pass

        for new_p in [p[0] for p in list(unique_work_people.union(unique_sheet_people)) if p[1] is None]:
            rows, cols = np.where(work_data == new_p)

            last_person_by_iperson_id = CofkCollectPerson.objects.order_by('-iperson_id').first()

            iperson_id = 1

            if last_person_by_iperson_id:
                iperson_id = last_person_by_iperson_id.iperson_id + 1

            person = CofkCollectPerson()
            person.upload = upload
            person.iperson_id = iperson_id
            person.primary_name = new_p
            person.date_of_birth_is_range = 0
            person.date_of_birth_inferred = 0
            person.date_of_birth_uncertain = 0
            person.date_of_birth_approx = 0
            person.date_of_birth_inferred = 0
            person.date_of_death_is_range = 0
            person.date_of_death_inferred = 0
            person.date_of_death_uncertain = 0
            person.date_of_death_approx = 0
            person.flourished_is_range = 0

            person.save()
            self.work_data.iloc[rows, cols + 1] = person.iperson_id