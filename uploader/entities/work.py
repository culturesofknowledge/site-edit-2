import logging

from typing import List

import pandas as pd
from django.core.exceptions import ValidationError

from location.models import CofkCollectLocation
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

    def preprocess_languages(self):
        """
        TODO try catch below, sometimes work data?
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
            self.process_languages(work_languages)

    def process_authors(self, work: CofkCollectWork):
        try:
            a_id = CofkCollectAuthorOfWork.objects.order_by('-author_id').first().author_id
        except AttributeError:
            a_id = 0

        for p in self.people.authors:
            try:
                person = [p2 for p2 in self.people.people if p['id'] == p2.iperson_id][0]
            except IndexError:
                continue

            author = CofkCollectAuthorOfWork(
                author_id=a_id,
                upload=self.upload,
                iwork_id=work,
                iperson_id=person)

            a_id = a_id + 1

            author.save()

    def process_addressees(self, work: CofkCollectWork):
        try:
            a_id = CofkCollectAddresseeOfWork.objects.order_by('-addressee_id').first().addressee_id
        except AttributeError:
            a_id = 0

        for p in self.people.addressees:
            try:
                person = [p2 for p2 in self.people.people if p['id'] == p2.iperson_id][0]
            except IndexError:
                continue

            addressee = CofkCollectAddresseeOfWork(
                addressee_id=a_id,
                upload=self.upload,
                iwork_id=work,
                iperson_id=person)

            #try:
            addressee.save()
            #except IntegrityError as ie:
            #    log.error(ie)

            a_id = a_id + 1

    def preprocess_data(self):
        # Isolating data relevant to a work
        non_work_keys = list(set(self.row_data.keys()) - set([c for c in CofkCollectWork.__dict__.keys()]))
        #log.debug(self.row_data)

        # Removing non-work data so that variable row_data_raw can be used to pass parameters
        # to create a CofkCollectWork object
        for m in non_work_keys:
            self.non_work_data[m] = self.row_data[m]
            del self.row_data[m]

        #log.debug(self.non_work_data)

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

        # The relation between origin/destination locations and works are circular
        # foreign keys. They will be processed after the work has been saved.
        if 'origin_id' in self.row_data:
            del self.row_data['origin_id']

        if 'destination_id' in self.row_data:
            del self.row_data['destination_id']

        #log.debug(self.row_data)

        # Creating the work itself
        work = CofkCollectWork(**self.row_data)

        self.set_default_values(work)

        try:
            work.save()

            self.ids.append(self.iwork_id)

            log.info("Work created iwork_id #{}, upload_id #{}".format(
                self.iwork_id, self.upload.upload_id))

            # Processing people mentioned in work
            # if 'emlo_mention_id' in self.work_data and 'mention_id' in self.work_data:
            self.process_authors(work)
            self.process_mentions(work)
            self.process_addressees(work)

            # Origin location needs to be processed before work is created
            # Is it possible that a work has more than one origin?
            self.process_origin(work)

            # Destination location needs to be processed before work is created
            # Is it possible that a work has more than one destination?
            self.process_destination(work)

            # Processing languages used in work
            self.preprocess_languages()

            # Processing resources in work
            if 'resource_name' in self.non_work_data or 'resource_url' in self.non_work_data:
                self.process_resource()
        except ValidationError as ve:
            self.add_error(ve)
            log.warning(ve)
        except TypeError as te:
            log.warning(te)

    def process_mentions(self, work: CofkCollectWork):
        try:
            m_id = CofkCollectPersonMentionedInWork.objects.order_by('-mention_id').first().mention_id
        except AttributeError:
            m_id = 0

        for p in self.people.mentioned:
            try:
                person = [p2 for p2 in self.people.people if p['id'] == p2.iperson_id][0]
            except IndexError:
                continue

            log.info("Processing people mentioned , iwork_id #{}, upload_id #{}".format(
                self.iwork_id, self.upload.upload_id))

            person_mentioned = CofkCollectPersonMentionedInWork(
                mention_id=m_id,
                upload=self.upload,
                iwork_id=work,
                iperson_id=person)

            m_id = m_id + 1

            person_mentioned.save()

    def process_origin(self, work: CofkCollectWork):
        try:
            o_id = CofkCollectOriginOfWork.objects.order_by('-origin_id').first().origin_id
        except AttributeError:
            o_id = 0

        for o in self.locations.origins:
            try:
                origin = [o2 for o2 in self.locations.locations if o['id'] == o2.location_id][0]
            except IndexError:
                continue

            log.info("Processing origin location , iwork_id #{}, upload_id #{}".format(
                self.iwork_id, self.upload.upload_id))

            origin_location = CofkCollectOriginOfWork(
                origin_id=o_id,
                upload=self.upload,
                iwork_id=work,
                location_id=origin)

            o_id = o_id + 1

            origin_location.save()

    def process_destination(self, work: CofkCollectWork):
        try:
            d_id = CofkCollectDestinationOfWork.objects.order_by('-destination_id').first().destination_id
        except AttributeError:
            d_id = 0

        for d in self.locations.destinations:
            try:
                destination = [d2 for d2 in self.locations.locations if d['id'] == d2.location_id][0]
            except IndexError:
                continue

            log.info("Processing destination location , iwork_id #{}, upload_id #{}".format(
                self.iwork_id, self.upload.upload_id))

            destination_location = CofkCollectDestinationOfWork(
                destination_id=d_id,
                upload=self.upload,
                iwork_id=work,
                location_id=destination)

            d_id = d_id + 1

            destination_location.save()

    '''def process_location(self, location_id: str, location_name: str) -> CofkCollectLocation:
        """
        Method that checks if a location specific to the location id and upload exists,
        if so it returns the id provided id if not a new location is created incrementing
        the highest location id by one.
        :param location_id:
        :param location_name:
        :param name:
        :return:
        """
        # TODO where does Geonames lookup happen?

        location = CofkCollectLocation.objects.filter(location_id=self.row_data[location_id],
                                                      upload_id=self.upload.upload_id).first()

        if not location:
            location_id = CofkCollectLocation.objects.order_by('-location_id').first().location_id + 1
            location = CofkCollectLocation(upload_id=self.upload.upload_id,
                                           location_id=location_id,
                                           location_name=self.non_work_data[location_name])
            location.save()

            log.info(f'Created location {self.non_work_data[location_name]}, upload_id #{self.upload.upload_id}')

        return location'''

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
