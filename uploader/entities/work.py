import logging

from typing import List, Generator, Tuple, Type, Any

from django.core.exceptions import ValidationError
from django.db import models
from openpyxl.cell import Cell

from location.models import CofkCollectLocation
from person.models import CofkCollectPerson
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectStatus, Iso639LanguageCode
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
        self.works:List[CofkCollectWork] = []
        self.people: List[CofkCollectPerson] = people
        self.authors: List[CofkCollectAuthorOfWork] = []
        self.mentioned: List[CofkCollectPersonMentionedInWork] = []
        self.addressees: List[CofkCollectAddresseeOfWork] = []
        self.locations: List[CofkCollectLocation] = locations
        self.origins: List[CofkCollectOriginOfWork] = []
        self.destinations: List[CofkCollectDestinationOfWork] = []
        self.resources: List[CofkCollectWorkResource] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            work_dict = {self.get_column_name_by_index(cell.column): cell.value for cell in row}
            self.check_required(work_dict, index)
            # self.check_data_types(work_dict, index)
            work_dict['upload_status_id'] = 1
            work_dict['upload'] = upload
            log.debug(work_dict)

            w = CofkCollectWork(**{k: work_dict[k] for k in work_dict if k in CofkCollectWork.__dict__.keys() and
                                   k not in ['origin_id', 'destination_id']})
            w.save()
            self.works.append(w)

            self.process_people(w, self.authors, CofkCollectAuthorOfWork, work_dict, 'author_ids', 'author_names')
            self.process_people(w, self.mentioned, CofkCollectPersonMentionedInWork, work_dict, 'emlo_mention_id',
                                'mention_id')
            self.process_people(w, self.addressees, CofkCollectAddresseeOfWork, work_dict, 'addressee_ids',
                                'addressee_names')

            self.process_locations(w, self.origins, CofkCollectOriginOfWork, work_dict, 'origin_id',
                                   'origin_name')
            self.process_locations(w, self.destinations, CofkCollectDestinationOfWork, work_dict, 'destination_id',
                                   'destination_name')

            resource_dict = {k: work_dict[k] for k in work_dict if
                             k in ['resource_name', 'resource_url', 'resource_details']}
            if resource_dict:
                resource_dict['upload'] = upload
                resource_dict['iwork'] = w
                self.resources.append(CofkCollectWorkResource(**resource_dict))

        if self.authors:
            CofkCollectAuthorOfWork.objects.bulk_create(self.authors, batch_size=500)

        if self.resources:
            CofkCollectWorkResource.objects.bulk_create(self.resources, batch_size=500)
            log.debug(f'Created {len(self.resources)} work resources')

        # Process each row in turn, using a dict comprehension to filter out empty values
        '''for i in range(1, len(self.sheet_data.index)):
            self.process_work({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})
            self.row += 1

        CofkCollectWork.objects.bulk_update(self.works, ['origin', 'destination'], batch_size=500)'''

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

    '''def process_authors2(self, w, author_ids, author_names):
        author_ids = author_ids.split(';')
        author_names = author_names.split(';')

        if len(author_ids) < len(author_names):
            log.warning('Fewer ids than names')
        elif len(author_ids) > len(author_names):
            log.warning('Fewer names than ids')

        if '' in author_ids:
            log.warning('Empty string in ids')
        if '' in author_names:
            log.warning('Empty string in names')

        for id, name in zip(author_ids, author_names):
            log.debug(f'{id} {name} {self.get_person(id)}')
            self.authors.append(CofkCollectAuthorOfWork(upload=self.upload, iwork=w, iperson=self.get_person(id)))'''

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

    def process_authors(self, work: CofkCollectWork):
        a_id = CofkCollectAuthorOfWork.objects. \
            values_list('author_id', flat=True).order_by('-author_id').first()

        if a_id is None:
            a_id = 1

        for a_id, p in enumerate(self.people.authors, start=a_id):
            try:
                person = [p2 for p2 in self.people.people if p['id'] == p2.iperson_id][0]
            except IndexError:
                continue

            author = CofkCollectAuthorOfWork(author_id=a_id, upload=self.upload, iwork=work, iperson=person)

            try:
                author.save()
            except ValueError:
                pass

    def process_addressees(self, work: CofkCollectWork):
        a_id = CofkCollectAddresseeOfWork.objects. \
            values_list('addressee_id', flat=True).order_by('-addressee_id').first()
        if a_id is None:
            a_id = 1

        for a_id, p in enumerate(self.people.addressees, start=a_id):
            try:
                person = [p2 for p2 in self.people.people if p['id'] == p2.iperson_id][0]
            except IndexError:
                continue

            addressee = CofkCollectAddresseeOfWork(addressee_id=a_id, upload=self.upload, iwork=work, iperson=person)
            try:
                addressee.save()
            except ValueError:
                pass

    def preprocess_data(self):
        # Isolating data relevant to a work
        non_work_keys = list(set(self.row_data.keys()) - set([c for c in CofkCollectWork.__dict__.keys()]))
        # log.debug(self.row_data)

        # Removing non-work data so that variable row_data_raw can be used to pass parameters
        # to create a CofkCollectWork object
        for m in non_work_keys:
            self.non_work_data[m] = self.row_data[m]
            del self.row_data[m]

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

    def process_mentions(self, work: CofkCollectWork):
        m_id = CofkCollectPersonMentionedInWork.objects. \
            values_list('mention_id', flat=True).order_by('-mention_id').first()

        if m_id is None:
            m_id = 0

        for m_id, p in enumerate(self.people.mentioned, start=m_id):
            try:
                person = [p2 for p2 in self.people.people if p['id'] == p2.iperson_id][0]
            except IndexError:
                continue

            log.info(f'Processing people mentioned , iwork_id #{self.iwork_id}, upload_id #{self.upload.upload_id}')

            person_mentioned = CofkCollectPersonMentionedInWork(mention_id=m_id, upload=self.upload, iwork=work,
                                                                iperson=person)
            try:
                person_mentioned.save()
            except ValueError:
                pass

    def process_origin(self, work: CofkCollectWork):
        o_id = CofkCollectOriginOfWork.objects. \
            values_list('origin_id', flat=True).order_by('-origin_id').first()
        if o_id is None:
            o_id = 0

        for o_id, o in enumerate(self.locations.origins, start=o_id):
            try:
                origin = [o2 for o2 in self.locations.locations if o['id'] == o2.location_id][0]
            except IndexError:
                continue

            log.info(f'Processing origin location, iwork_id #{self.iwork_id}, upload_id #{self.upload.upload_id}')

            origin_location = CofkCollectOriginOfWork(origin_id=o_id, upload=self.upload, iwork=work, location=origin)

            origin_location.save()
            log.debug(f'{origin_location} saved')

    def process_destination(self, work: CofkCollectWork):
        d_id = CofkCollectDestinationOfWork.objects. \
            values_list('destination_id', flat=True).order_by('-destination_id').first()
        if d_id is None:
            d_id = 0

        for d_id, d in enumerate(self.locations.destinations, start=d_id):
            try:
                destination = [d2 for d2 in self.locations.locations if d['id'] == d2.location_id][0]
            except IndexError:
                continue

            log.info(f'Processing destination location, iwork_id #{self.iwork_id}, upload_id #{self.upload.upload_id}')

            destination_location = CofkCollectDestinationOfWork(destination_id=d_id, upload=self.upload, iwork=work,
                                                                location=destination)

            try:
                destination_location.save()
            except ValueError:
                # Will error if location_id != int
                pass

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

    def process_resource(self, work: CofkCollectWork):
        resource_name = self.non_work_data['resource_name'] if 'resource_name' in self.non_work_data else ''
        resource_url = self.non_work_data['resource_url'] if 'resource_url' in self.non_work_data else ''
        resource_details = self.non_work_data['resource_details'] if 'resource_details' in self.non_work_data else ''

        r_id = CofkCollectWorkResource.objects. \
            values_list('resource_id', flat=True).order_by('-resource_id').first()

        if r_id is None:
            r_id = 0

        resource = CofkCollectWorkResource(upload=self.upload, iwork=work,
                                           resource_id=r_id + 1, resource_name=resource_name,
                                           resource_url=resource_url, resource_details=resource_details)
        resource.save()

        log.info(f'Resource created #{resource.resource_id} iwork_id #{self.iwork_id},'
                 f' upload_id #{self.upload.upload_id}')

    def set_default_values(self, work: CofkCollectWork):
        """
        These repetitive ifs are required because it's not possible to set default values
        to the database fields
        """
        work.upload_status = CofkCollectStatus.objects.filter(status_id=1).first()

        fields = ['mentioned_inferred', 'mentioned_uncertain', 'place_mentioned_inferred', 'place_mentioned_uncertain',
                  'date_of_work2_approx', 'date_of_work2_inferred', 'date_of_work2_uncertain',
                  'date_of_work_std_is_range', 'date_of_work_inferred', 'date_of_work_uncertain',
                  'date_of_work_approx', 'authors_inferred', 'authors_uncertain', 'addressees_inferred',
                  'addressees_uncertain', 'destination_inferred', 'destination_uncertain', 'origin_inferred',
                  'origin_uncertain']

        for field in [field for field in fields if field not in self.row_data]:
            setattr(work, field, 0)
