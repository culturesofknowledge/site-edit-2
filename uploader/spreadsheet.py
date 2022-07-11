import logging
from typing import List

import pandas as pd
from pandas import ExcelFile

from institution.models import CofkCollectInstitution
from location.models import CofkCollectLocation
from manifestation.models import CofkCollectManifestation
from person.models import CofkCollectPerson
from uploader import OpenpyxlReaderWOFormatting
from uploader.constants import mandatory_sheets
from uploader.models import CofkCollectUpload, Iso639LanguageCode
from uploader.validation import validate_work, validate_manifestation, CofkExcelFileError
from work.models import CofkCollectAuthorOfWork, CofkCollectAddresseeOfWork, CofkCollectWork, \
    CofkCollectPersonMentionedInWork, CofkCollectLanguageOfWork, CofkCollectWorkResource

log = logging.getLogger(__name__)


class CofkRepositories:
    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, limit=None):
        self.upload = upload

        self.__institution_id = None
        self.sheet = sheet_data
        self.__repository_data = {}
        limit = limit if limit else len(self.sheet.index)
        self.ids = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_repository({k: v for k, v in self.sheet.iloc[i].to_dict().items() if v is not None})

    def process_repository(self, repository_data):
        self.__repository_data = repository_data
        self.__repository_data['upload_id'] = self.upload
        self.__institution_id = repository_data['institution_id']

        log.info("Processing repository, institution_id #{}, upload_id #{}".format(
            self.__institution_id, self.upload.upload_id))

        if not self.already_exists():
            repository = CofkCollectInstitution(**self.__repository_data)
            repository.save()
            self.ids.append(self.__institution_id)
            log.info("Repository created.")

    def already_exists(self) -> bool:
        return CofkCollectInstitution.objects \
            .filter(institution_id=self.__institution_id, upload_id=self.upload) \
            .exists()


class CofkLocations:
    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, limit=None):
        self.upload = upload

        self.__location_id = None
        self.sheet = sheet_data
        self.__location_data = {}
        limit = limit if limit else len(self.sheet.index)
        self.ids = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_location({k: v for k, v in self.sheet.iloc[i].to_dict().items() if v is not None})

    def process_location(self, repository_data):
        self.__location_data = repository_data
        self.__location_data['upload_id'] = self.upload.upload_id
        self.__location_id = repository_data['location_id']

        log.info("Processing location, location_id #{}, upload_id #{}".format(
            1, self.upload.upload_id))

        if not self.already_exists():
            # Name, city and country are required
            location = CofkCollectLocation(**self.__location_data)
            location.save()
            self.ids.append(self.__location_id)
            log.info("Location created.")

    def already_exists(self) -> bool:
        return CofkCollectLocation.objects \
            .filter(upload_id=self.upload) \
            .exists()


class CofkPeople:
    def __init__(self, upload_id: CofkCollectUpload, sheet_data: pd.DataFrame, limit=None):
        self.upload_id = upload_id

        self.__person_id = None
        self.sheet = sheet_data
        self.__person_data = {}
        limit = limit if limit else len(self.sheet.index)
        self.ids = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_people({k: v for k, v in self.sheet.iloc[i].to_dict().items() if v is not None})

    def process_people(self, person_data):
        self.__person_data = person_data
        self.__person_data['upload_id'] = self.upload_id
        self.__person_id = str(person_data['iperson_id'])

        log.info("Processing person, iperson_id #{}, upload_id #{}".format(
            self.__person_id, self.upload_id))

        if not self.already_exists():
            person = CofkCollectPerson(**self.__person_data)
            person.save()
            self.ids.append(self.__person_id)
            log.info("Person created.")

    def already_exists(self) -> bool:
        return CofkCollectPerson.objects \
            .filter(person_id=self.__person_id, upload_id=self.upload_id) \
            .exists()


class CofkManifestations:

    def __init__(self, upload_id: CofkCollectUpload, sheet_data: pd.DataFrame, limit=None):
        self.upload_id = upload_id

        self.__manifestation_id = None
        self.sheet = sheet_data
        self.__non_manifestation_data = {}
        self.__manifestation_data = {}
        limit = limit if limit else len(self.sheet.index)
        self.ids = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_manifestation({k: v for k, v in self.sheet.iloc[i].to_dict().items() if v is not None})

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

        self.__manifestation_data['upload_id'] = self.upload_id
        self.__manifestation_id = str(manifestation_data['manifestation_id'])

        log.info("Processing manifestation, manifestation_id #{}, upload_id #{}".format(
            self.__manifestation_id, self.upload_id))

        if not self.already_exists():
            manifestation = CofkCollectManifestation(**self.__manifestation_data)
            manifestation.save()

            self.ids.append(self.__manifestation_id)
            log.info("Manifestation created.")

    def already_exists(self) -> bool:
        return CofkCollectManifestation.objects \
            .filter(manifestation_id=self.__manifestation_id, upload_id=self.upload_id) \
            .exists()


class CofkWork:

    def __init__(self, upload_id: CofkCollectUpload, sheet_data: pd.DataFrame,
                 limit=None):
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
        self.upload_id = upload_id

        self.iwork_id = None
        self.sheet = sheet_data
        self.work_data = {}
        self.non_work_data = {}
        self.ids = []

        limit = limit if limit else len(self.sheet.index)

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_work({k: v for k, v in self.sheet.iloc[i].to_dict().items() if v is not None})

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
                self.iwork_id, self.upload_id))
            self.process_languages(work_languages)

    def process_authors(self, author_ids, author_names):
        author_ids = str(self.non_work_data[author_ids])
        author_names = str(self.non_work_data[author_names])

        authors = self.process_people(author_ids, author_names)

        for p in authors:
            author = CofkCollectAuthorOfWork(
                # author_id=author_id,
                upload_id=self.upload_id,
                # iwork_id=self.iwork_id,
                iperson_id=p)

            author.save()

    def process_addressees(self, addressee_ids, addressee_names):
        addressee_ids = str(self.non_work_data[addressee_ids])
        addressee_names = str(self.non_work_data[addressee_names])

        addressees = self.process_people(addressee_ids, addressee_names)

        for p in addressees:
            addressee = CofkCollectAddresseeOfWork(
                # addressee_id=addressee_id,
                upload_id=self.upload_id,
                # iwork_id=self.iwork_id,
                iperson_id=p)

            addressee.save()

    def preprocess_data(self):
        # Isolating data relevant to a work
        non_work_keys = list(set(self.work_data.keys()) - set([c for c in CofkCollectWork.__dict__.keys()]))
        # log.debug(self.work_data)

        # Removing non-work data so that variable work_data_raw can be used to pass parameters
        # to create a CofkCollectWork object
        for m in non_work_keys:
            self.non_work_data[m] = self.work_data[m]
            del self.work_data[m]

        # log.debug(self.non_work_data)

    def process_work(self, work_data):
        """
        This method processes one row of data from the Excel sheet.

        :param work_data:
        :return:
        """
        self.work_data = work_data

        self.work_data['upload_id'] = self.upload_id
        self.iwork_id = work_data['iwork_id']

        log.info("Processing work, iwork_id #{}, upload_id #{}".format(
            self.iwork_id, self.upload_id))

        self.preprocess_data()

        # Origin location needs to be processed before work is created
        # Is it possible that a work has more than one origin?
        if 'origin_id' in self.work_data:
            self.work_data['origin_id'] = self.process_location(
                loc_id=self.work_data['origin_id'],
                name=self.non_work_data['origin_name'])

        # Destination location needs to be processed before work is created
        # Is it possible that a work has more than one destination?
        if 'destination_id' in self.work_data:
            work_data['destination_id'] = self.process_location(
                loc_id=self.work_data['destination_id'],
                name=self.non_work_data['destination_name'])

        # Creating the work itself
        work = CofkCollectWork(**work_data)
        work.save()
        self.ids.append(self.iwork_id)

        log.info("Work created iwork_id #{}, upload_id #{}".format(
            self.iwork_id, self.upload_id))

        # Processing people mentioned in work
        if 'emlo_mention_id' in self.work_data and 'mention_id' in self.work_data:
            self.process_mentions('emlo_mention_id', 'mention_id')

        # Processing languages used in work
        self.preprocess_languages()

        # Processing resources in work
        if 'resource_name' in self.non_work_data or 'resource_url' in self.non_work_data:
            self.process_resource()

        self.process_authors('author_ids', 'author_names')

        self.process_addressees('addressee_ids', 'addressee_names')

    def process_mentions(self, emlo_mention_ids: str, mention_ids: str):
        emlo_mention_ids = str(self.non_work_data[emlo_mention_ids])
        mention_ids = str(self.non_work_data[mention_ids])

        log.info("Processing people mentioned , iwork_id #{}, upload_id #{}".format(
            self.iwork_id, self.upload_id))

        # Before mentions can be registered the people mentioned need
        # to be created
        people_mentioned = self.process_people(emlo_mention_ids, mention_ids)
        log.info(people_mentioned)

        for p in people_mentioned:
            person_mention = CofkCollectPersonMentionedInWork(
                # mention_id=mention_id,
                upload_id=self.upload_id,
                iwork_id=self.iwork_id,
                iperson_id=p)

            person_mention.save()

    def process_location(self, loc_id, name) -> int:
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
                                                         upload_id=self.upload_id).exists()

        if not location_id:
            loc = CofkCollectLocation(
                upload_id=self.upload_id.upload_id,
                # location_id=location_id,
                location_name=name)
            loc.save()

            log.info("Created location {}, upload_id #{}".format(
                name, self.upload_id))
            return loc.location_id

        return location_id

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
                    upload_id=self.upload_id,
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
                    upload_id=self.upload_id,
                    iperson_id=person[0],
                    primary_name=person[1])

                new_person.save()

                people.append(new_person.iperson_id)
            else:
                people.append(person_id[0])

        return people

    def process_languages(self, has_language: List[str]):
        for language in has_language:
            lan = Iso639LanguageCode.objects.filter(code_639_3=language).first()

            if lan is not None:
                lang = CofkCollectLanguageOfWork(
                    # language_of_work_id=language_id,
                    upload_id=self.upload_id,
                    # iwork_id=self.iwork_id,
                    language_code=lan)

                lang.save()
            else:
                log.debug(f'Upload {self.upload_id.upload_id}: Submitted {language} not a valid ISO639 language')

    def process_resource(self):
        resource_name = self.non_work_data['resource_name'] if 'resource_name' in self.non_work_data else None
        resource_url = self.non_work_data['resource_url'] if 'resource_url' in self.non_work_data else None
        resource_details = self.non_work_data['resource_details'] if 'resource_details' in self.non_work_data else None

        log.info("Processing resource , iwork_id #{}, upload_id #{}".format(
            self.iwork_id, self.upload_id))

        resource = CofkCollectWorkResource(
            upload_id=self.upload_id,
            # iwork_id=self.iwork_id,
            # resource_id=resource_id,
            resource_name=resource_name,
            resource_url=resource_url,
            resource_details=resource_details)
        resource.save()

        log.info("Resource created #{} iwork_id #{}, upload_id #{}".format(resource.id,
                                                                           self.iwork_id, self.upload_id))


class CofkUploadExcelFile:

    def __init__(self, upload: CofkCollectUpload, filename: str):
        """
        :param logger:
        :param filename:
        """
        self.errors = []
        self.works = None
        self.upload = upload
        self.filename = filename
        self.repositories = []
        self.locations = []
        self.people = []
        self.manifestations = []
        self.report = {}

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
            self.wb = pd.read_excel(filename, None, header=1,
                                    usecols=lambda c: not c.startswith('Unnamed:'),
                                    engine='openpyxl_wo_formatting')

        self.check_sheets()

        # self.validate_data()

        # self.upload = self.create_upload()

        # It's best to process the sheets in reverse order, starting with repositories/institutions
        self.process_repositories()

        # The next sheet is places/locations
        self.process_locations()

        # The next sheet is people
        self.process_people()

        # Second last but not least, the works themselves
        self.process_work()

        # The last sheet is manifestations
        self.process_manifestations()

        self.report = { 'manifestations': len(self.manifestations),
                        'people': len(self.people),
                        'repositories': len(self.repositories)}

    def check_sheets(self):
        # Verify all required sheets are present
        if not all(elem in list(self.wb.keys()) for elem in mandatory_sheets):
            msg = "Missing sheet/s: {}".format(", ".join(list(mandatory_sheets - self.wb.keys())))
            log.error(msg)
            raise ValueError(msg)

        log.debug("All {} sheets verified".format(len(mandatory_sheets)))

        #  TODO verify this is correct
        # if index length is less than 2 then there's only the header, no data
        if len(self.wb['Work'].where(pd.notnull(self.wb['Work'])).index) < 2:
            msg = "Spreadsheet contains no data"
            log.error(msg)
            raise ValueError(msg)

    def process_repositories(self):
        repositories = CofkRepositories(upload=self.upload,
                                        sheet_data=self.wb['Repositories'].where(pd.notnull(self.wb['Repositories']),
                                                                                 None))
        self.repositories = repositories.ids

    def process_locations(self):
        locations = CofkLocations(upload=self.upload,
                                  sheet_data=self.wb['Places'].where(pd.notnull(self.wb['Places']), None))
        self.locations = locations.ids

    def process_people(self):
        people = CofkPeople(upload_id=self.upload,
                            sheet_data=self.wb['People'].where(pd.notnull(self.wb['People']), None))
        self.people = people.ids

    def process_manifestations(self):
        manifestation = CofkManifestations(upload_id=self.upload,
                                           sheet_data=self.wb['Manifestation'].where(
                                               pd.notnull(self.wb['Manifestation']), None))
        self.manifestations = manifestation.ids

    def process_work(self):
        works = CofkWork(upload_id=self.upload,
                         sheet_data=self.wb['Work'].where(pd.notnull(self.wb['Work']), None))
        self.works = works.ids
        self.upload.total_works = len(works.ids)

    def validate_data(self):
        work_errors = validate_work(self.wb['Work'].where(pd.notnull(self.wb['Work']), None))

        manifestation_errors = validate_manifestation(
            self.wb['Manifestation'].where(pd.notnull(self.wb['Manifestation']), None))

        if work_errors or manifestation_errors:
            raise CofkExcelFileError(filename=self.filename,
                                     errors=work_errors + manifestation_errors)
