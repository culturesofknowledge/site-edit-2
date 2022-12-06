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


def get_common_languages():
    # results from select distinct(language_code) from cofk_collect_language_of_work;
    common_languages = ["otk", "fro", "ara", "ces", "hye", "cat", "syr", "dan", "rus", "por", "swe", "nld", "hrv",
                        "yes", "nds", "pol", "gla", "heb", "grc", "eng", "spa", "aii", "fas", "chu", "cym", "fra",
                        "deu", "tam", "kat", "eus", "lat", "cop", "ita", "cor", "tur"]
    return list(Iso639LanguageCode.objects.filter(code_639_3__in=common_languages).all())


class CofkWork(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet_data: Generator[Tuple[Cell], None, None], people, locations,
                 sheet_name: str):
        super().__init__(upload, sheet_data, sheet_name)

        self.works: List[CofkCollectWork] = []
        self.people: List[CofkCollectPerson] = people
        self.locations: List[CofkCollectLocation] = locations
        self.common_languages: List[Iso639LanguageCode] = get_common_languages()

        self.authors: List[CofkCollectAuthorOfWork] = []
        self.mentioned: List[CofkCollectPersonMentionedInWork] = []
        self.addressees: List[CofkCollectAddresseeOfWork] = []
        self.origins: List[CofkCollectOriginOfWork] = []
        self.destinations: List[CofkCollectDestinationOfWork] = []
        self.resources: List[CofkCollectWorkResource] = []
        self.languages: List[CofkCollectLanguageOfWork] = []

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

            if 'author_ids' in work_dict and 'author_names' in work_dict:
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

            if 'language_id' in work_dict:
                self.process_languages(work_dict, w)

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
                people_list.append(people_model(upload=self.upload, iwork=work,
                                                iperson=self.get_person(_id)))
        else:
            log.info(self.errors)

    def process_locations(self, work: CofkCollectWork, location_list: List[Any], location_model: Type[models.Model],
                          work_dict: dict, ids: str, names: str):
        id_list, name_list = self.clean_lists(work_dict, ids, names)

        if not self.errors:
            for _id, name in zip(id_list, name_list):
                location_list.append(location_model(upload=self.upload, iwork=work,
                                                    location=self.get_location(_id)))
        else:
            log.info(self.errors)

    def process_languages(self, work_dict: dict, work: CofkCollectWork):
        work_languages = work_dict['language_id'].split(';')

        if 'hashebrew' in work_dict:
            work_languages.append("heb")

        if 'hasarabic' in work_dict:
            work_languages.append("ara")

        if 'hasgreek' in work_dict:
            work_languages.append("ell")

        if 'haslatin' in work_dict:
            work_languages.append("lat")

        for language in work_languages:
            lan = [l for l in self.common_languages if l.code_639_3 == language]

            if not lan:
                lan = Iso639LanguageCode.objects.filter(code_639_3=language).first()
            else:
                lan = lan[0]

            if lan is not None:
                self.languages.append(CofkCollectLanguageOfWork(upload=self.upload, iwork=work, language_code=lan))
            else:
                msg = f'The value in column "language_id", "{language}" is not a valid ISO639 language.'
                log.error(msg)
                self.add_error(ValidationError(msg))

    def create_all(self):
        for entities in [self.authors, self.mentioned, self.addressees, self.origins, self.destinations,
                         self.resources, self.languages]:
            if entities:
                self.bulk_create(entities)
