import logging
from typing import Generator, Tuple, List

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from openpyxl.cell import Cell

from institution.models import CofkCollectInstitution
from manifestation.models import CofkCollectManifestation
from uploader.entities.entity import CofkEntity
from uploader.entities.repositories import CofkRepositories
from uploader.entities.work import CofkWork
from uploader.models import CofkCollectUpload
from work.models import CofkCollectWork

log = logging.getLogger(__name__)


class CofkManifestations(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet_data: Generator[Tuple[Cell], None, None],
                 repositories: List[CofkCollectInstitution], works: List[CofkCollectWork], sheet_name: str):
        super().__init__(upload, sheet_data, sheet_name)

        self.repositories = repositories
        self.works = works
        self.ids = []
        self.manifestations: List[CofkCollectManifestation] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            man_dict = {self.get_column_name_by_index(cell.column): cell.value for cell in row if cell.value is not None}
            self.check_data_types(man_dict, index)

            if not self.errors:
                if 'iwork_id' in man_dict:
                    man_dict['iwork'] = self.get_work(man_dict.pop('iwork_id'))

                if 'repository_id' in man_dict:
                    man_dict['repository'] = self.get_repository(man_dict.pop('repository_id'))

                if 'printed_edition_notes' in man_dict:
                    man_dict['manifestation_notes'] = man_dict.pop('printed_edition_notes')
                if 'manifestation_type_p' in man_dict:
                    man_dict['manifestation_type'] = man_dict.pop('manifestation_type_p')

                if 'repository_name' in man_dict:
                    del man_dict['repository_name']

                man_dict['upload'] = upload
                log.debug(man_dict)
                self.manifestations.append(CofkCollectManifestation(**man_dict))

        if self.manifestations:
            self.bulk_create(self.manifestations)

        # Process each row in turn, using a dict comprehension to filter out empty values
        '''for i in range(1, len(self.sheet_data.index)):
            self.process_manifestation({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})

        try:
            CofkCollectManifestation.objects.bulk_create(self.manifestations)
        except IntegrityError as ie:
            # Will error if location_id != int
            self.add_error(ValidationError(ie))'''

    def get_work(self, work_id: str):
        work = [w for w in self.works if w.iwork_id == int(work_id)]

        if work:
            return work[0]

    def get_repository(self, institution_id: str):
        repository = [r for r in self.repositories if r.institution_id == int(institution_id)]

        if repository:
            return repository[0]

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
        self.manifestations.append(manifestation)
        self.ids.append(self.__manifestation_id)

        log.info("Manifestation created.")
