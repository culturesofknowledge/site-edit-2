import logging

from typing import List, Generator, Tuple, Type, Any

from django.core.exceptions import ValidationError
from django.db import models
from openpyxl.cell import Cell

from location.models import CofkCollectLocation
from person.models import CofkCollectPerson
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, Iso639LanguageCode
from work.models import CofkCollectWork, CofkCollectLanguageOfWork, CofkCollectWorkResource, \
    CofkCollectPersonMentionedInWork, CofkCollectAuthorOfWork, CofkCollectAddresseeOfWork, CofkCollectOriginOfWork, \
    CofkCollectDestinationOfWork

log = logging.getLogger(__name__)


class CofkWork(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet_data: Generator[Tuple[Cell], None, None], people, locations,
                 sheet_name: str):
        super().__init__(upload, sheet_data, sheet_name)

        self.iwork_id = None
        self.non_work_data = {}
        self.ids = []
        self.works: List[CofkCollectWork] = []
        self.people: List[CofkCollectPerson] = people
        self.authors: List[CofkCollectAuthorOfWork] = []
        self.mentioned: List[CofkCollectPersonMentionedInWork] = []
        self.addressees: List[CofkCollectAddresseeOfWork] = []
        self.locations: List[CofkCollectLocation] = locations
        self.origins: List[CofkCollectOriginOfWork] = []
        self.destinations: List[CofkCollectDestinationOfWork] = []
        self.resources: List[CofkCollectWorkResource] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            work_dict = {self.get_column_name_by_index(cell.column): cell.value for cell in row if
                         cell.value is not None}
            self.check_required(work_dict, index)
            # TODO check work data types
            # self.check_data_types(work_dict, index)
            work_dict['upload_status_id'] = 1
            work_dict['upload'] = upload
            # log.debug(work_dict)

            w = CofkCollectWork(**{k: work_dict[k] for k in work_dict if k in CofkCollectWork.__dict__.keys()})
            w.save()
            self.works.append(w)
            # log.debug({k: work_dict[k] for k in work_dict if k in CofkCollectWork.__dict__.keys()})

            self.process_people(w, self.authors, CofkCollectAuthorOfWork, work_dict, 'author_ids', 'author_names')

            if 'emlo_mention_id' in work_dict and 'mention_id' in work_dict:
                self.process_people(w, self.mentioned, CofkCollectPersonMentionedInWork, work_dict, 'emlo_mention_id',
                                    'mention_id')
            if 'addressee_ids' in work_dict and 'addressee_names' in work_dict:
                self.process_people(w, self.addressees, CofkCollectAddresseeOfWork, work_dict, 'addressee_ids',
                                    'addressee_names')

            if 'origin_id' in work_dict and 'origin_name' in work_dict:
                self.process_locations(w, self.origins, CofkCollectOriginOfWork, work_dict, 'origin_id',
                                       'origin_name')

            if 'destination_id' in work_dict and 'destination_name' in work_dict:
                self.process_locations(w, self.destinations, CofkCollectDestinationOfWork, work_dict, 'destination_id',
                                       'destination_name')

            resource_dict = {k: work_dict[k] for k in work_dict if
                             k in ['resource_name', 'resource_url', 'resource_details']}
            if resource_dict:
                resource_dict['upload'] = upload
                resource_dict['iwork'] = w
                self.resources.append(CofkCollectWorkResource(**resource_dict))

        upload.total_works = len(self.works)
        upload.save()

    def get_person(self, person_id: str):
        person = [p for p in self.people if
                  p.union_iperson is not None and p.union_iperson.iperson_id == int(person_id)]

        if person:
            return person[0]

    def get_location(self, location_id: str):
        location = [l for l in self.locations if
                    l.union_location is not None and l.union_location.location_id == int(location_id)]

        if location:
            return location[0]

    def process_people(self, work: CofkCollectWork, people_list: List[Any], people_model: Type[models.Model],
                       work_dict: dict, ids, names):
        id_list, name_list = self.clean_lists(work_dict, ids, names)

        if not self.errors:
            for _id, name in zip(id_list, name_list):
                log.debug(f'{_id} {name} {self.get_person(_id)}')
                people_list.append(people_model(upload=self.upload, iwork=work,
                                                iperson=self.get_person(_id)))
        else:
            log.info(self.errors)

    def process_locations(self, work: CofkCollectWork, location_list: List[Any], location_model: Type[models.Model],
                          work_dict: dict, ids: str, names: str):
        id_list, name_list = self.clean_lists(work_dict, ids, names)

        if not self.errors:
            for _id, name in zip(id_list, name_list):
                log.debug(f'{_id} {name} {self.get_location(_id)}')
                location_list.append(location_model(upload=self.upload, iwork=work,
                                                    location=self.get_location(_id)))
        else:
            log.info(self.errors)

    def preprocess_languages(self, work: CofkCollectWork):
        """
        TODO try catch below, sometimes work data?
        TODO does the order of languages matter?
        """
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
            self.process_languages(work, work_languages)

    def process_work(self, work_data: dict):
        """
        This method processes one row of data from the Excel sheet.
        """
        self.row_data = work_data

        self.row_data['upload_id'] = self.upload.upload_id
        self.iwork_id = work_data['iwork_id']

        self.check_data_types('Work')

        log.info(f'Processing work, iwork_id #{self.iwork_id}, upload_id #{self.upload.upload_id}')

        self.preprocess_data()

        # The relation between origin/destination locations and works are circular
        # foreign keys. They will be processed after the work has been saved.
        if 'origin_id' in self.row_data:
            del self.row_data['origin_id']

        if 'destination_id' in self.row_data:
            del self.row_data['destination_id']

        # Creating the work itself
        work = CofkCollectWork(**self.row_data)

        self.set_default_values(work)

        if not self.errors:
            try:
                work.save()

                self.ids.append(self.iwork_id)

                log.info(f'Work created iwork_id #{self.iwork_id}, upload_id #{self.upload.upload_id}')

                # Processing people mentioned in work
                self.process_authors(work)
                self.process_mentions(work)
                self.process_addressees(work)

                # Origin location needs to be processed before work is created
                # Is it possible that a work has more than one origin?
                self.process_origin(work)

                work.origin = CofkCollectOriginOfWork.objects.filter(iwork_id=work).first()

                # Destination location needs to be processed before work is created
                # Is it possible that a work has more than one destination?
                self.process_destination(work)

                work.destination = CofkCollectDestinationOfWork.objects.filter(iwork_id=work).first()
                # work.save()

                # Processing languages used in work
                self.preprocess_languages(work)

                # Processing resources in work
                self.process_resource(work)

                self.works.append(work)

            except ValidationError as ve:
                self.add_error(ve)
                log.warning(ve)
            # except TypeError as te:
            #    log.warning(te)

    def process_languages(self, work: CofkCollectWork, has_language: List[str]):
        l_id = CofkCollectLanguageOfWork.objects. \
            values_list('language_of_work_id', flat=True).order_by('-language_of_work_id').first()

        if l_id is None:
            l_id = 0

        l_id += 1

        for l_id, language in enumerate(has_language, start=l_id):
            lan = Iso639LanguageCode.objects.filter(code_639_3=language).first()

            if lan is not None:
                lang = CofkCollectLanguageOfWork(language_of_work_id=l_id, upload=self.upload, iwork=work,
                                                 language_code=lan)
                lang.save()
            else:
                msg = f'The value in column "language_id", "{language}" is not a valid ISO639 language.'
                log.error(msg)
                self.add_error(ValidationError(msg))

