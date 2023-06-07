import logging
from typing import List, Type, Any

from django.db import models

from core.models import Iso639LanguageCode
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectWork, CofkCollectAddresseeOfWork, \
    CofkCollectAuthorOfWork, CofkCollectDestinationOfWork, CofkCollectLanguageOfWork, CofkCollectOriginOfWork, \
    CofkCollectPersonMentionedInWork, CofkCollectWorkResource, CofkCollectLocation, CofkCollectPerson

log = logging.getLogger(__name__)


def get_common_languages():
    common = list(CofkCollectLanguageOfWork.objects.distinct('language_code').values_list('language_code', flat=True))
    return Iso639LanguageCode.objects.filter(code_639_3__in=common).all()


class CofkWork(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet, people, locations):
        super().__init__(upload, sheet)

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

        self.resource_id: int = 0
        self.author_id: int = 0
        self.mention_id: int = 0
        self.addressee_id: int = 0
        self.origin_id: int = 0
        self.destination_id: int = 0
        self.language_of_work_id: int = 0

        for index, row in enumerate(self.iter_rows(), start=1 + self.sheet.header_length):
            work_dict = self.get_row(row, index)
            self.check_required(work_dict)
            # TODO check work data types
            self.check_data_types(work_dict)
            work_dict['upload_status_id'] = 1
            work_dict['upload'] = upload

            w = CofkCollectWork(**{k: work_dict[k] for k in work_dict if k in CofkCollectWork.__dict__.keys()})
            self.works.append(w)

            if 'author_ids' in work_dict and 'author_names' in work_dict:
                self.process_people(w, self.authors, CofkCollectAuthorOfWork, work_dict, 'author_ids', 'author_names',
                                    'author_id')

            if 'emlo_mention_id' in work_dict and 'mention_id' in work_dict:
                self.process_people(w, self.mentioned, CofkCollectPersonMentionedInWork, work_dict, 'emlo_mention_id',
                                    'mention_id', 'mention_id')
            if 'addressee_ids' in work_dict and 'addressee_names' in work_dict:
                self.process_people(w, self.addressees, CofkCollectAddresseeOfWork, work_dict, 'addressee_ids',
                                    'addressee_names', 'addressee_id')

            if 'origin_id' in work_dict and 'origin_name' in work_dict:
                self.process_locations(w, self.origins, CofkCollectOriginOfWork, work_dict, 'origin_id',
                                       'origin_name', 'origin_id')

            if 'destination_id' in work_dict and 'destination_name' in work_dict:
                self.process_locations(w, self.destinations, CofkCollectDestinationOfWork, work_dict, 'destination_id',
                                       'destination_name', 'destination_id')

            resource_dict = {k: work_dict[k] for k in work_dict if
                             k in ['resource_name', 'resource_url', 'resource_details']}
            if resource_dict:
                resource_dict['upload'] = upload
                resource_dict['iwork'] = w
                self.resource_id += 1
                resource_dict['resource_id'] = self.resource_id
                self.resources.append(CofkCollectWorkResource(**resource_dict))

            if 'language_id' in work_dict:
                self.process_languages(work_dict, w)

        upload.total_works = len(self.works)
        upload.save()

    def get_person(self, person_id: str, person_name: str=None) -> CofkCollectPerson:
        if person_id == '':
            people = [p for p in self.people if p.primary_name == person_name and p.iperson_id is None]

            if len(people) == 1:
                return people[0]
            elif len(people) > 1:
                self.add_error('Ambiguity in submitted people.')
        elif person := [p for p in self.people if
                      p.union_iperson is not None and p.union_iperson.iperson_id == int(person_id)]:
            return person[0]
        elif person := [p for p in self.people if p.iperson_id == int(person_id)]:
            return person[0]

    def get_location(self, location_id: str) -> CofkCollectLocation:
        if location := [l for l in self.locations if
                        l.union_location is not None and l.union_location.location_id == int(location_id)]:
            return location[0]
        elif location := [l for l in self.locations if l.location_id == int(location_id)]:
            return location[0]

    def process_people(self, work: CofkCollectWork, people_list: List[Any], people_model: Type[models.Model],
                       work_dict: dict, ids: str, names: str, id_type: str):
        id_list, name_list = self.clean_lists(work_dict, ids, names)

        for _id, name in zip(id_list, name_list):
            if person := self.get_person(_id, name):
                related_person = people_model(upload=self.upload, iwork=work, iperson=person)
                setattr(related_person, id_type, self.get_new_id(id_type))
                people_list.append(related_person)

                if person.iperson_id and not person.union_iperson:
                    self.add_error(f'There is no person with the id {_id} in the Union catalogue.')

            else:
                # Person not present in people sheet
                self.add_error(f'Person with the id {_id} was listed in the {self.sheet.name} sheet but is'
                               f' not present in the People sheet.')

    def process_locations(self, work: CofkCollectWork, location_list: List[Any], location_model: Type[models.Model],
                          work_dict: dict, ids: str, names: str, id_type: str):
        id_list, name_list = self.clean_lists(work_dict, ids, names)

        for _id, name in zip(id_list, name_list):
            if location := self.get_location(_id):
                if location.union_location:
                    related_location = location_model(upload=self.upload, iwork=work, location=location)
                    setattr(related_location, id_type, self.get_new_id(id_type))
                    location_list.append(related_location)
                else:
                    self.add_error(f'There is no location with the id {_id} in the Union catalogue.')
            else:
                self.add_error(f'Location with the id {_id} was listed in the {self.sheet.name} sheet but is'
                               f' not present in the Places sheet.')

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
                self.languages.append(CofkCollectLanguageOfWork(upload=self.upload, iwork=work, language_code=lan,
                                                                language_of_work_id=self.get_new_id('language_of_work_id')))
            else:
                self.add_error(f'The value in column "language_id", "{language}" is not a valid ISO639 language.')

    def create_all(self):
        self.bulk_create(self.works)
        self.log_summary =  [f'{len(self.works)} {type(self.works[0]).__name__}']

        for entities in [self.authors, self.mentioned, self.addressees, self.origins, self.destinations,
                         self.resources, self.languages]:
            if entities:
                self.bulk_create(entities)
                self.log_summary.append(f'{len(entities)} {type(entities[0]).__name__}')

    def get_new_id(self, id_type: str):
        setattr(self, id_type, getattr(self, id_type) + 1)
        return getattr(self, id_type)
