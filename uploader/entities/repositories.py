import logging

import pandas as pd
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectInstitution

log = logging.getLogger(__name__)


class CofkRepositories(CofkEntity):
    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame):
        super().__init__(upload, sheet_data)

        self.__institution_id = None
        self.institutions = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, len(self.sheet_data.index)):
            self.process_repository({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})

        try:
            CofkCollectInstitution.objects.bulk_create(self.institutions)
        except IntegrityError as ie:
            # Will error if location_id != int
            self.add_error(ValidationError(ie))

    def process_repository(self, repository_data):
        self.row_data = repository_data
        self.row_data['upload'] = self.upload
        self.__institution_id = repository_data['institution_id']

        log.info("Processing repository, institution_id #{}, upload_id #{}".format(
            self.__institution_id, self.upload.upload_id))

        self.check_data_types('Repositories')

        if not self.already_exists():
            repository = CofkCollectInstitution(**self.row_data)
            self.institutions.append(repository)

            log.info(f'Repository {repository} created.')

    def already_exists(self) -> bool:
        try:
            return CofkCollectInstitution.objects \
                .filter(institution_id=self.__institution_id, upload=self.upload) \
                .exists()
        except ValueError:
            return True