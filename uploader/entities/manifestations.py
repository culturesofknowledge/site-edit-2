import logging

import pandas as pd
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from manifestation.models import CofkCollectManifestation
from uploader.entities.entity import CofkEntity
from uploader.entities.repositories import CofkRepositories
from uploader.entities.work import CofkWork
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkManifestations(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, repositories: CofkRepositories,
                 works: CofkWork):
        super().__init__(upload, sheet_data)

        self.repositories = repositories
        self.works = works
        self.__manifestation_id = None
        self.__non_manifestation_data = {}
        self.ids = []

        self.check_data_types('Manifestation')

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, len(self.sheet_data.index)):
            self.process_manifestation({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})

    def preprocess_data(self):
        if 'printed_edition_notes' in self.row_data:
            self.row_data['manifestation_notes'] = self.row_data.pop('printed_edition_notes')
        if 'manifestation_type_p' in self.row_data:
            self.row_data['manifestation_type'] = self.row_data.pop('manifestation_type_p')

        # Isolating data relevant to a work
        non_work_keys = list(set(self.row_data.keys()) - set([c for c in CofkCollectManifestation.__dict__.keys()]))

        # Removing non work data so that variable work_data_raw can be used to pass parameters
        # to create a CofkCollectWork object
        for m in non_work_keys:
            self.__non_manifestation_data[m] = self.row_data[m]
            del self.row_data[m]

    def process_manifestation(self, manifestation_data):
        self.row_data = manifestation_data

        institution = None

        try:
            institution = [i2 for i2 in self.repositories.institutions if
                           'repository_id' in self.row_data and
                           self.row_data['repository_id'] == i2.institution_id][0]
        except IndexError:
            pass

        self.preprocess_data()
        self.row_data['upload'] = self.upload
        work = None

        try:
            work = [w2 for w2 in self.works.works if
                    self.row_data['iwork_id'] == w2.iwork_id][0]
        except IndexError:
            pass

        self.row_data['iwork'] = work
        del self.row_data['iwork_id']

        if institution:
            self.row_data['repository'] = institution
            del self.row_data['repository_id']

        self.__manifestation_id = str(manifestation_data['manifestation_id'])

        log.info("Processing manifestation, manifestation_id #{}, upload_id #{}".format(
            self.__manifestation_id, self.upload.upload_id))

        manifestation = CofkCollectManifestation(**self.row_data)

        try:
            manifestation.save()
        except IntegrityError as ie:
            self.add_error(ValidationError(ie))

        self.ids.append(self.__manifestation_id)

        log.info("Manifestation created.")
