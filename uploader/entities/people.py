import logging
from typing import List

import pandas as pd
from django.core.exceptions import ValidationError

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

    def process_people_sheet(self) -> dict:
        """
        Get all people from people spreadsheet
        Populating a list of tuples of (Name, iperson_id)
        """
        sheet_people = {}
        for i in range(1, len(self.sheet_data.index)):
            self.row_data = {k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None}

            self.check_data_types('People')
            iperson_id = self.row_data['iperson_id'] if 'iperson_id' in self.row_data else None

            if iperson_id is not None:
                for ipi, pn in zip(str(iperson_id).split(';'), str(self.row_data['primary_name']).split(';')):
                    person = CofkCollectPerson()

                    try:
                        ipi = int(ipi)
                        person.person = CofkUnionPerson.objects.filter(iperson_id=ipi).first()
                    except ValueError:
                        log.info('So it goes')

                    person.upload = self.upload
                    person.iperson_id = ipi
                    person.primary_name = pn
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

                    if ipi not in sheet_people:
                        self.people.append(person)
                        sheet_people[ipi] = pn

                    log.info(f'Creating new person {person}')
            elif self.row_data['primary_name'] not in sheet_people.values():
                for name in str(self.row_data['primary_name']).split(';'):
                    # This is a new person and doesn't have id
                    sheet_people[name] = name

        try:
            CofkCollectPerson.objects.bulk_create(self.people)
        except ValueError:
            pass

        return sheet_people

    def list_people(self, names: str, ids) -> List[tuple]:
        """
        This function checks for multiple entries of people in the Work sheet
        and compares the resulting list of ids against the resulting list of names.
        TODO
        Currently this function presupposes that the number of ids and names will match.
        In other words, it will not create new authors.
        """

        if isinstance(self.row_data[ids], str) and ';' in self.row_data[names]:
            names_list = [n.strip() for n in self.row_data[names].split(';')]

            if '' in names_list:
                self.add_error(ValidationError(f'Encountered an empty value for a name in {names}.'), 'work')

            try:
                ids_list = [int(i) for i in self.row_data[ids].split(';') if i != '']

                if len(ids_list) < len(names_list):
                    # New people entries
                    ids_list += [None] * (len(names_list) - len(ids_list))

                return list(zip(names_list, ids_list))
            except ValueError:
                self.add_error(ValidationError(f'Values in {ids} could not be parsed as integers.'), 'work')

        elif isinstance(self.row_data[ids], str) or ';' in self.row_data[names]:
            self.add_error(ValidationError(f'Values in {ids} and {names} do not match.'), 'work')

        return [(self.row_data[names], self.row_data[ids])]

    def process_work_sheet(self) -> dict:
        """
        Get all people from references in Work spreadsheet.
        Work sheets can contain multiple values for people per work. If so, the values are separated by
        a semicolon with no space on either side.
        Populating a list of tuples of (Name, iperson_id)
        """
        work_people = {}
        work_people_fields = [('author_names', 'author_ids', 'notes_on_authors'),
                              ('addressee_names', 'addressee_ids', 'notes_on_addressees'),
                              ('mention_id', 'emlo_mention_id', 'notes_on_people_mentioned')]

        for i in range(1, len(self.work_data.index)):
            self.row_data = {k: v for k, v in self.work_data.iloc[i].to_dict().items() if v is not None}

            for people_relation in [w for w in work_people_fields if w[0] in self.row_data]:
                related_people = self.list_people(people_relation[0], people_relation[1])

                if 'author' in people_relation[0]:
                    for author in related_people:
                        if author[1] not in work_people:
                            self.authors.append({'name': author[0], 'id': author[1]})
                            work_people[author[1]] = author[0]
                elif 'addressee' in people_relation[0]:
                    for addressee in related_people:
                        if addressee[1] not in work_people:
                            self.addressees.append({'name': addressee[0], 'id': addressee[1]})
                            work_people[addressee[1]] = addressee[0]
                elif 'mention' in people_relation[0]:
                    for mentioned in related_people:
                        if mentioned[1] not in work_people:
                            self.mentioned.append({'name': mentioned[0], 'id': mentioned[1]})
                            work_people[mentioned[1]] = mentioned[0]

        return work_people

    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, work_data: pd.DataFrame):
        """
        sheet_data: all data from the "People" sheet
        word_data: all data from the "Work" sheet, from which a few columns are required
        # TODO editor's notes from people sheet need to be added
        """
        super().__init__(upload, sheet_data)
        self.work_data = work_data

        self.people = []
        self.authors = []
        self.mentioned = []
        self.addressees = []

        unique_sheet_people = self.process_people_sheet()
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
                                           f' but {tense} missing from the Work spreadsheet: {ppl_joined}'))
