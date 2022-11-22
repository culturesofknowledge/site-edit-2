import logging
from typing import Generator, Tuple

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from openpyxl.cell import Cell

from institution.models import CofkCollectInstitution
from uploader.constants import mandatory_sheets
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkRepositories(CofkEntity):
    def __init__(self, upload: CofkCollectUpload, sheet_data: Generator[Tuple[Cell], None, None]):
        super().__init__(upload, sheet_data)

        self.__institution_id = None
        self.institutions = []

        for r in sheet_data:
            mc = mandatory_sheets['Repositories']['columns'][r[0].column - 1]
            log.debug(f'{r[0].value} ({r[0].row}, {r[0].column} ({mc}))')

        # Process each row in turn, using a dict comprehension to filter out empty values
        #for index, row in self.sheet_data.iterrows():
        #    log.debug((index, row))
        #    #self.process_repository({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})

        #self.add_error(ValidationError('wrong'))

        #try:
        #    CofkCollectInstitution.objects.bulk_create(self.institutions)
        #except IntegrityError as ie:
        #    # Will error if location_id != int
        #    self.add_error(ValidationError(ie))

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