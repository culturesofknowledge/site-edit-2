import logging

import pandas as pd

from manifestation.models import CofkCollectManifestation
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkManifestations(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame):
        super().__init__(upload, sheet_data)

        self.__manifestation_id = None
        self.__non_manifestation_data = {}
        self.__manifestation_data = {}
        self.ids = []

        self.check_data_types('Manifestation')

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, len(self.sheet_data.index)):
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