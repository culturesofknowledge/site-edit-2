import logging
from typing import List

import numpy as np
import pandas as pd
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from pandas import ExcelFile

from institution.models import CofkCollectInstitution
from location.models import CofkCollectLocation
from manifestation.models import CofkCollectManifestation
from person.models import CofkCollectPerson
from uploader.OpenpyxlReaderWOFormatting import OpenpyxlReaderWOFormatting
from uploader.constants import mandatory_sheets
from uploader.models import CofkCollectUpload, Iso639LanguageCode, CofkCollectStatus
from uploader.validation import validate_work, validate_manifestation, CofkExcelFileError, CofkMissingSheetError, \
    CofkMissingColumnError
from work.models import CofkCollectAuthorOfWork, CofkCollectAddresseeOfWork, CofkCollectWork, \
    CofkCollectPersonMentionedInWork, CofkCollectLanguageOfWork, CofkCollectWorkResource

log = logging.getLogger(__name__)


class CofkEntity:
    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame):
        self.upload = upload
        self.sheet_data = sheet_data
        self.row_data = None
        self.errors = {}
        self.row = 1

    def check_data_types(self, sheet_name: str):
        sheet = [s for s in mandatory_sheets if s['name'] == sheet_name][0]

        if 'ints' in sheet:
            for test_int_column in [t for t in sheet['ints'] if t in self.row_data]:
                try:
                    int(self.row_data[test_int_column])
                except ValueError as ve:
                    msg = f'Column {test_int_column} in {sheet_name} sheet is not a valid integer.'
                    log.error(msg)
                    self.add_error(ValidationError(msg))

        if 'bools' in sheet:
            for test_bool_column in [t for t in sheet['bools'] if t in self.row_data]:
                try:
                    if int(self.row_data[test_bool_column]) not in [0, 1]:
                        msg = f'Column {test_bool_column} in {sheet_name} sheet is not a boolean value of either 0 or 1.'
                        log.error(msg)
                        self.add_error(ValidationError(msg))
                except ValueError as ve:
                    msg = f'Column {test_bool_column} in {sheet_name} sheet is not a boolean value of either 0 or 1.'
                    log.error(msg)
                    self.add_error(ValidationError(msg))

    def add_error(self, error: ValidationError):
        if self.row not in self.errors:
            self.errors[self.row] = []

        self.errors[self.row].append(error)

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


class CofkRepositories(CofkEntity):
    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame):
        super().__init__(upload, sheet_data)

        self.__institution_id = None
        self.ids = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, len(self.sheet_data.index)):
            self.process_repository({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})

    def process_repository(self, repository_data):
        self.row_data = repository_data
        self.row_data['upload'] = self.upload
        self.__institution_id = repository_data['institution_id']

        log.info("Processing repository, institution_id #{}, upload_id #{}".format(
            self.__institution_id, self.upload.upload_id))

        self.check_data_types('Repositories')

        if not self.already_exists():
            repository = CofkCollectInstitution(**self.row_data)
            repository.save()
            self.ids.append(self.__institution_id)

            log.info("Repository created.")

    def already_exists(self) -> bool:
        try:
            return CofkCollectInstitution.objects \
                .filter(institution_id=self.__institution_id, upload=self.upload) \
                .exists()
        except ValueError:
            return True


class CofkLocations(CofkEntity):
    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, limit=None):
        super().__init__(upload, sheet_data)
        self.__location_id = None
        limit = limit if limit else len(self.sheet_data.index)
        self.ids = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_location({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})

    def process_location(self, repository_data):
        self.row_data = repository_data
        self.row_data['upload_id'] = self.upload.upload_id
        self.__location_id = repository_data['location_id']

        self.check_data_types('Places')

        log.info("Processing location, location_id #{}, upload_id #{}".format(
            1, self.upload.upload_id))

        if not self.already_exists():
            # Name, city and country are required
            location = CofkCollectLocation(**self.row_data)
            location.location_id = 1
            location.element_1_eg_room = 0
            location.element_2_eg_building = 0
            location.element_3_eg_parish = 0
            location.element_4_eg_city = 0
            location.element_5_eg_county = 0
            location.element_6_eg_country = 0
            location.element_7_eg_empire = 0

            try:
                location.save()
            except ValidationError as ve:
                self.add_error(ve)
                print(ve)

            self.ids.append(self.__location_id)

            log.info("Location created.")

    def already_exists(self) -> bool:
        return CofkCollectLocation.objects \
            .filter(upload_id=self.upload) \
            .exists()


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


class CofkManifestations(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, limit=None):
        super().__init__(upload, sheet_data)

        self.__manifestation_id = None
        self.__non_manifestation_data = {}
        self.__manifestation_data = {}
        limit = limit if limit else len(self.sheet_data.index)
        self.ids = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_manifestation({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})

    def preprocess_data(self):
        self.__manifestation_data = {k.replace(' ', '_'): v for k, v in self.__manifestation_data.items()}

        # Isolating data relevant to a work
        non_work_keys = list(
            set(self.__manifestation_data.keys()) - set([c for c in CofkCollectManifestation.__dict__.keys()]))

        # Removing non work data so that variable work_data_raw can be used to pass parameters
        # to create a CofkCollectWork object
        for m in non_work_keys:
            self.__non_manifestation_data[m] = self.__manifestation_data[m]
            del self.__manifestation_data[m]

    def process_manifestation(self, manifestation_data):
        self.__manifestation_data = manifestation_data
        self.preprocess_data()

        self.__manifestation_data['upload'] = self.upload
        self.__manifestation_id = str(manifestation_data['manifestation_id'])

        log.info("Processing manifestation, manifestation_id #{}, upload_id #{}".format(
            self.__manifestation_id, self.upload.upload_id))

        if not self.already_exists():
            manifestation = CofkCollectManifestation(**self.__manifestation_data)
            manifestation.save()

            self.ids.append(self.__manifestation_id)

            log.info("Manifestation created.")

    def already_exists(self) -> bool:
        return CofkCollectManifestation.objects \
            .filter(manifestation_id=self.__manifestation_id, upload_id=self.upload) \
            .exists()


class CofkWork(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, limit=None):
        """
        non_work_data will contain any raw data about:
        1. origin location
        2. destination location
        3. people mentioned
        4. languages used
        5. resources
        6. authors
        7. addressees
        :param upload_id:
        """
        # log = logger
        super().__init__(upload, sheet_data)

        self.iwork_id = None
        self.non_work_data = {}
        self.ids = []

        limit = limit if limit else len(self.sheet_data.index)

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_work({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})
            self.row += 1

    def preprocess_languages(self):
        '''
        TODO try catch below, sometimes work data?
        '''
        try:
            work_languages = self.non_work_data['language_id'].split(';')
        except KeyError:
            return

        if 'hashebrew' in self.non_work_data:
            work_languages.append("heb")

        if 'hasarabic' in self.non_work_data:
            work_languages.append("ara")

        if 'hasgreek' in self.non_work_data:
            work_languages.append("ell")

        if 'haslatin' in self.non_work_data:
            work_languages.append("lat")

        if len(work_languages):
            log.info("Foreign language in iwork_id #{}, upload_id #{}".format(
                self.iwork_id, self.upload.upload_id))
            self.process_languages(work_languages)

    '''def process_authors(self, author_ids, author_names):
        author_ids = str(self.non_work_data[author_ids])
        author_names = str(self.non_work_data[author_names])

        authors = self.process_people(author_ids, author_names)
        try:
            a_id = CofkCollectAuthorOfWork.objects.order_by('-author_id').first().author_id
        except AttributeError:
            a_id = 0

        for p in authors:
            author = CofkCollectAuthorOfWork(
                author_id=a_id,
                upload_id=self.upload.upload_id,
                iwork_id=self.iwork_id,
                iperson_id=p)

            a_id = a_id + 1

            try:
                author.save()
            except IntegrityError as ie:
                log.error(ie)

    def process_addressees(self, addressee_ids, addressee_names):
        addressee_ids = str(self.non_work_data[addressee_ids])
        addressee_names = str(self.non_work_data[addressee_names])

        addressees = self.process_people(addressee_ids, addressee_names)

        try:
            a_id = CofkCollectAddresseeOfWork.objects.order_by('-addressee_id').first().addressee_id
        except AttributeError:
            a_id = 0

        for p in addressees:
            addressee = CofkCollectAddresseeOfWork(
                addressee_id=a_id,
                upload_id=self.upload.upload_id,
                iwork_id=self.iwork_id,
                iperson_id=p)

            try:
                addressee.save()
            except IntegrityError as ie:
                log.error(ie)

            a_id = a_id + 1'''

    def preprocess_data(self):
        # Isolating data relevant to a work
        non_work_keys = list(set(self.row_data.keys()) - set([c for c in CofkCollectWork.__dict__.keys()]))
        # log.debug(self.row_data)

        # Removing non-work data so that variable row_data_raw can be used to pass parameters
        # to create a CofkCollectWork object
        for m in non_work_keys:
            self.non_work_data[m] = self.row_data[m]
            del self.row_data[m]

        # log.debug(self.non_work_data)

    def process_work(self, work_data):
        """
        This method processes one row of data from the Excel sheet.

        :param work_data:
        :return:
        """
        self.row_data = work_data

        self.row_data['upload_id'] = self.upload.upload_id
        self.iwork_id = work_data['iwork_id']

        self.check_data_types('Work')

        log.info("Processing work, iwork_id #{}, upload_id #{}".format(
            self.iwork_id, self.upload.upload_id))

        self.preprocess_data()

        # Origin location needs to be processed before work is created
        # Is it possible that a work has more than one origin?
        if 'origin_id' in self.row_data:
            self.row_data['origin_id'] = self.process_location(
                loc_id=self.row_data['origin_id'],
                name=self.non_work_data['origin_name'])

        # Destination location needs to be processed before work is created
        # Is it possible that a work has more than one destination?
        if False and 'destination_id' in self.row_data:
            self.row_data['destination_id'] = self.process_location(
                loc_id=self.row_data['destination_id'],
                name=self.non_work_data['destination_name'])

        # Creating the work itself
        work = CofkCollectWork(**self.row_data)

        # These repetitive ifs are required because it's not possible to set default values
        # to the database fields
        if 'mentioned_inferred' not in self.row_data:
            work.mentioned_inferred = 0

        if 'mentioned_uncertain' not in self.row_data:
            work.mentioned_uncertain = 0

        if 'place_mentioned_inferred' not in self.row_data:
            work.place_mentioned_inferred = 0

        if 'place_mentioned_uncertain' not in self.row_data:
            work.place_mentioned_uncertain = 0

        if 'date_of_work2_approx' not in self.row_data:
            work.date_of_work2_approx = 0

        if 'date_of_work2_inferred' not in self.row_data:
            work.date_of_work2_inferred = 0

        if 'date_of_work2_uncertain' not in self.row_data:
            work.date_of_work2_uncertain = 0

        if 'date_of_work_std_is_range' not in self.row_data:
            work.date_of_work_std_is_range = 0

        if 'date_of_work_inferred' not in self.row_data:
            work.date_of_work_inferred = 0

        if 'date_of_work_uncertain' not in self.row_data:
            work.date_of_work_uncertain = 0

        if 'date_of_work_approx' not in self.row_data:
            work.date_of_work_approx = 0

        if 'authors_inferred' not in self.row_data:
            work.authors_inferred = 0

        if 'authors_uncertain' not in self.row_data:
            work.authors_uncertain = 0

        if 'addressees_inferred' not in self.row_data:
            work.addressees_inferred = 0

        if 'addressees_uncertain' not in self.row_data:
            work.addressees_uncertain = 0

        if 'destination_inferred' not in self.row_data:
            work.destination_inferred = 0

        if 'destination_uncertain' not in self.row_data:
            work.destination_uncertain = 0

        if 'origin_inferred' not in self.row_data:
            work.origin_inferred = 0

        if 'origin_uncertain' not in self.row_data:
            work.origin_uncertain = 0

        work.upload_status = CofkCollectStatus.objects.filter(status_id=1).first()

        try:
            work.save()
        except ValidationError as ve:
            self.add_error(ve)
            log.warning(ve)
        except TypeError as te:
            log.warning(te)

        self.ids.append(self.iwork_id)

        log.info("Work created iwork_id #{}, upload_id #{}".format(
            self.iwork_id, self.upload.upload_id))

        # Processing people mentioned in work
        # if 'emlo_mention_id' in self.work_data and 'mention_id' in self.work_data:
        # self.process_mentions('emlo_mention_id', 'mention_id')

        # Processing languages used in work
        self.preprocess_languages()

        # Processing resources in work
        if 'resource_name' in self.non_work_data or 'resource_url' in self.non_work_data:
            self.process_resource()

        # self.process_authors('author_ids', 'author_names')

        # self.process_addressees('addressee_ids', 'addressee_names')

    '''def process_mentions(self, emlo_mention_ids: str, mention_ids: str):
        emlo_mention_ids = str(self.non_work_data[emlo_mention_ids])
        mention_ids = str(self.non_work_data[mention_ids])

        log.info("Processing people mentioned , iwork_id #{}, upload_id #{}".format(
            self.iwork_id, self.upload.upload_id))

        # Before mentions can be registered the people mentioned need
        # to be created
        people_mentioned = self.process_people(emlo_mention_ids, mention_ids)
        log.info(people_mentioned)

        for p in people_mentioned:
            person_mention = CofkCollectPersonMentionedInWork(
                # mention_id=mention_id,
                upload_id=self.upload.upload_id,
                iwork_id=self.iwork_id,
                iperson_id=p)

            person_mention.save()'''

    def process_location(self, loc_id, name) -> CofkCollectLocation:
        """
        Method that checks if a location specific to the location id and upload exists,
        if so it returns the id provided id if not a new location is created incrementing
        the highest location id by one.
        :param loc_id:
        :param name:
        :return:
        """

        loc_id = int(loc_id)

        location_id = CofkCollectLocation.objects.filter(location_id=loc_id,
                                                         upload_id=self.upload.upload_id).first()

        if not location_id:
            location_id = CofkCollectLocation.objects.order_by('-location_id').first().location_id + 1
            loc = CofkCollectLocation(
                upload_id=self.upload.upload_id,
                location_id=location_id,
                location_name=name)
            loc.save()

            log.info("Created location {}, upload_id #{}".format(
                name, self.upload.upload_id))
            return loc

        return location_id

    '''
    def process_people(self, ids: str, names: str) -> List[int]:
        """
        This method assumes that the data holds correct information on persons.
        That means that if the id and name specific to the current upload do not exist,
        they are created.

        Persons created seem to be specific to the upload. The cofk_collect_person table
        has upload_id as a primary key. This means that persons at this stage (pre-review)
        do not seem to be global and there is likely massive duplication in the
        cofk_collect_person table.
        :param ids:
        :param names:
        :return:
        """
        ids = ids.split(';')
        names = names.split(';')
        people = []

        # If there are more names than ids then a new person needs to be created
        if len(ids) < len(names):
            log.debug("More names than ids.")
            new_names = names[len(ids):]

            for name in new_names:
                new_person = CofkCollectPerson(
                    upload_id=self.upload.upload_id,
                    # iperson_id=last_person_id,
                    primary_name=name)

                new_person.save()
                people.append(new_person.id)

        for person in zip(ids, names):
            # Check if person already exists
            person_id = person[0]

            if not CofkCollectPerson.objects.filter(iperson_id=person_id).exists():
                log.info("Creating new person {}-{}".format(person[0], person[1]))
                # Person does not exist, so we need to create it
                new_person = CofkCollectPerson(
                    upload_id=self.upload.upload_id,
                    iperson_id=person[0],
                    primary_name=person[1])

                new_person.save()

                people.append(new_person.iperson_id)
            else:
                people.append(person_id[0])

        return people'''

    def process_languages(self, has_language: List[str]):
        for language in has_language:
            lan = Iso639LanguageCode.objects.filter(code_639_3=language).first()

            if lan is not None:
                first_language = CofkCollectLanguageOfWork.objects.order_by('-language_of_work_id').first()

                if first_language:
                    l_id = CofkCollectLanguageOfWork.objects.order_by('-language_of_work_id').first() \
                        .language_of_work_id
                else:
                    l_id = 0

                lang = CofkCollectLanguageOfWork(
                    language_of_work_id=l_id + 1,
                    upload_id=self.upload.upload_id,
                    iwork_id=self.iwork_id,
                    language_code=lan)

                lang.save()
            else:
                log.debug(f'Upload {self.upload.upload_id}: Submitted {language} not a valid ISO639 language')

    def process_resource(self):
        resource_name = self.non_work_data['resource_name'] if 'resource_name' in self.non_work_data else ''
        resource_url = self.non_work_data['resource_url'] if 'resource_url' in self.non_work_data else ''
        resource_details = self.non_work_data['resource_details'] if 'resource_details' in self.non_work_data else ''

        log.info("Processing resource , iwork_id #{}, upload_id #{}".format(
            self.iwork_id, self.upload.upload_id))

        try:
            r_id = CofkCollectWorkResource.objects.order_by('-resource_id').first().resource_id
        except AttributeError:
            r_id = 0

        resource = CofkCollectWorkResource(
            upload_id=self.upload.upload_id,
            iwork_id=self.iwork_id,
            resource_id=r_id + 1,
            resource_name=resource_name,
            resource_url=resource_url,
            resource_details=resource_details)
        resource.save()

        log.info("Resource created #{} iwork_id #{}, upload_id #{}".format(resource.resource_id,
                                                                           self.iwork_id, self.upload.upload_id))


class CofkUploadExcelFile:

    def __init__(self, upload: CofkCollectUpload, filename: str):
        """
        :param logger:
        :param filename:
        """
        self.errors = {}
        self.works = None
        self.upload = upload
        self.filename = filename
        self.repositories = None
        self.locations = None
        self.people = None
        self.manifestations = None
        self.total_errors = 0
        self.data = {}

        """
        Setting sheet_name to None returns a dict with sheet name as key and data frame as value
        Occasionally additional data is included that we cannot parse, so we ignore "Unnamed:" columns
        Supports xls, xlsx, xlsm, xlsb, odf, ods and odt file extensions read from a local filesystem or URL.
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
        """
        try:
            self.wb = pd.read_excel(filename, sheet_name=None, usecols=lambda c: not c.startswith('Unnamed:'))
        except ValueError:
            ExcelFile._engines['openpyxl_wo_formatting'] = OpenpyxlReaderWOFormatting
            self.wb = pd.read_excel(filename, sheet_name=None,
                                    usecols=lambda c: not c.startswith('Unnamed:'),
                                    engine='openpyxl_wo_formatting')

        self.check_sheets()

        for sheet in [s['name'] for s in mandatory_sheets]:
            self.data[sheet.lower()] = self.get_sheet_data(sheet)

        self.check_columns()

        self.check_data_present()

        # It's best to process the sheets in reverse order, starting with repositories/institutions
        self.repositories = CofkRepositories(upload=self.upload,
                                             sheet_data=self.data['repositories'])

        # The next sheet is places/locations
        self.locations = CofkLocations(upload=self.upload,
                                       sheet_data=self.data['places'])

        # The next sheet is people
        self.people = CofkPeople(upload=self.upload,
                                 sheet_data=self.data['people'],
                                 work_data=self.data['work'])

        # Second last but not least, the works themselves
        self.works = CofkWork(upload=self.upload, sheet_data=self.data['work'])
        self.upload.total_works = len(self.works.ids)

        # The last sheet is manifestations
        self.manifestations = CofkManifestations(upload=self.upload, sheet_data=self.data['manifestation'])

        if self.works.errors:
            self.errors['work'] = self.works.format_errors_for_template()
            self.total_errors += self.errors['work']['total']

        if self.people.errors:
            self.errors['people'] = self.people.format_errors_for_template()
            self.total_errors += self.errors['people']['total']

        if self.repositories.errors:
            self.errors['repositories'] = self.repositories.format_errors_for_template()
            self.total_errors += self.errors['repositories']['total']

        if self.locations.errors:
            self.errors['locations'] = self.locations.format_errors_for_template()
            self.total_errors += self.errors['locations']['total']

        if self.manifestations.errors:
            self.errors['manifestations'] = self.manifestations.format_errors_for_template()
            self.total_errors += self.errors['manifestations']['total']

    def get_sheet_data(self, sheet_name: str) -> pd.DataFrame:
        return self.wb[sheet_name].where(pd.notnull(self.wb[sheet_name]), None)

    def check_data_present(self):
        # if index length is less than 2 then there's only the header, no data
        if len(self.data['work'].index) < 2:
            msg = "Spreadsheet contains no data"
            log.error(msg)

            raise ValueError(msg)

    def check_sheets(self):
        # Verify all required sheets are present
        sheet_names = [s['name'] for s in mandatory_sheets]

        if not all(elem in list(self.wb.keys()) for elem in sheet_names):
            msg = "Missing sheet/s: {}".format(", ".join(list(sheet_names - self.wb.keys())))
            log.error(msg)
            raise CofkMissingSheetError(msg)

        log.debug("All {} sheets verified".format(len(mandatory_sheets)))

    def check_columns(self):
        total_missing_columns = []
        for sheet in mandatory_sheets:
            missing_columns = []
            sheet_name = sheet['name']
            for ms in set(sheet['columns']).difference(set(self.data[sheet_name.lower()].columns)):
                missing_columns.append(ms)

            if missing_columns:
                if len(missing_columns) > 1:
                    ms = ', '.join(missing_columns)
                    missing_columns.append(CofkMissingColumnError(f'Missing columns {ms} from the sheet {sheet_name}'))
                else:
                    missing_columns.append(
                        CofkMissingColumnError(f'Missing column {missing_columns[0]} from the sheet {sheet_name}'))
                total_missing_columns += missing_columns

        if total_missing_columns:
            log.info(total_missing_columns)
            raise CofkMissingColumnError(total_missing_columns)
