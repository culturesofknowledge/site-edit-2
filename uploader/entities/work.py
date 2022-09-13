import logging

from typing import List

import pandas as pd
from django.core.exceptions import ValidationError

from uploader.entities.entity import CofkEntity
from uploader.entities.locations import CofkLocations
from uploader.entities.people import CofkPeople
from uploader.models import CofkCollectUpload, CofkCollectStatus, Iso639LanguageCode
from work.models import CofkCollectWork, CofkCollectLanguageOfWork, CofkCollectWorkResource, \
    CofkCollectPersonMentionedInWork, CofkCollectAuthorOfWork, CofkCollectAddresseeOfWork, CofkCollectOriginOfWork, \
    CofkCollectDestinationOfWork

log = logging.getLogger(__name__)


class CofkWork(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, people: CofkPeople,
                 locations: CofkLocations):
        """
        non_work_data will contain any raw data about:
        1. origin location
        2. destination location
        3. people mentioned
        4. languages used
        5. resources
        6. authors
        7. addressees
        :param upload:
        """
        super().__init__(upload, sheet_data)

        self.iwork_id = None
        self.non_work_data = {}
        self.ids = []
        self.people = people
        self.locations = locations

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, len(self.sheet_data.index)):
            self.process_work({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})
            self.row += 1

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
        a_id = CofkCollectAuthorOfWork.objects.\
                values_list('author_id', flat=True).order_by('-author_id').first()

        if a_id is None:
            a_id = 1

        for a_id, p in enumerate(self.people.authors, start=a_id):
            try:
                person = [p2 for p2 in self.people.people if p['id'] == p2.iperson_id][0]
            except IndexError:
                continue

            author = CofkCollectAuthorOfWork(author_id=a_id, upload=self.upload, iwork=work, iperson=person)
            author.save()

    def process_addressees(self, work: CofkCollectWork):
        a_id = CofkCollectAddresseeOfWork.objects.\
                values_list('addressee_id', flat=True).order_by('-addressee_id').first()
        if a_id is None:
            a_id = 1

        for a_id, p in enumerate(self.people.addressees, start=a_id):
            try:
                person = [p2 for p2 in self.people.people if p['id'] == p2.iperson_id][0]
            except IndexError:
                continue

            addressee = CofkCollectAddresseeOfWork(addressee_id=a_id, upload=self.upload, iwork=work, iperson=person)
            addressee.save()

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
            work.save()

            # Processing languages used in work
            self.preprocess_languages(work)

            # Processing resources in work
            if 'resource_name' in self.non_work_data or 'resource_url' in self.non_work_data:
                self.process_resource()
        except ValidationError as ve:
            self.add_error(ve)
            log.warning(ve)
        # except TypeError as te:
        #    log.warning(te)

    def process_mentions(self, work: CofkCollectWork):
        m_id = CofkCollectPersonMentionedInWork.objects.\
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
            person_mentioned.save()

    def process_origin(self, work: CofkCollectWork):
        o_id = CofkCollectOriginOfWork.objects.\
                values_list('origin_id', flat=True).order_by('-origin_id').first()
        if o_id is None:
            o_id = 0

        for o_id, o in enumerate(self.locations.origins, start=o_id):
            try:
                origin = [o2 for o2 in self.locations.locations if o['id'] == o2.location_id][0]
            except IndexError:
                continue

            log.info(f'Processing origin location , iwork_id #{self.iwork_id}, upload_id #{self.upload.upload_id}')

            origin_location = CofkCollectOriginOfWork(origin_id=o_id, upload=self.upload, iwork=work, location=origin)

            origin_location.save()
            log.debug(f'{origin_location} saved')

    def process_destination(self, work: CofkCollectWork):
        d_id = CofkCollectDestinationOfWork.objects.\
                values_list('destination_id', flat=True).order_by('-destination_id').first()
        if d_id is None:
            d_id = 0

        for d_id, d in enumerate(self.locations.destinations, start=d_id):
            try:
                destination = [d2 for d2 in self.locations.locations if d['id'] == d2.location_id][0]
            except IndexError:
                continue

            log.info(f'Processing destination location , iwork_id #{self.iwork_id}, upload_id #{self.upload.upload_id}')

            destination_location = CofkCollectDestinationOfWork(destination_id=d_id, upload=self.upload, iwork=work,
                                                                location=destination)

            destination_location.save()

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
                msg = f'"{language}" is not a valid ISO639 language.'
                log.error(msg)
                self.add_error(ValidationError(msg))

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

        resource = CofkCollectWorkResource(upload_id=self.upload.upload_id, iwork_id=self.iwork_id,
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
