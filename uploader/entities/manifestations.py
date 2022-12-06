import logging
from typing import Generator, Tuple, List

from openpyxl.cell import Cell

from institution.models import CofkCollectInstitution
from manifestation.models import CofkCollectManifestation
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload
from work.models import CofkCollectWork

log = logging.getLogger(__name__)


class CofkManifestations(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet,
                 repositories: List[CofkCollectInstitution], works: List[CofkCollectWork]):
        super().__init__(upload, sheet)

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

    def get_work(self, work_id: str):
        work = [w for w in self.works if w.iwork_id == int(work_id)]

        if work:
            return work[0]

    def get_repository(self, institution_id: str):
        repository = [r for r in self.repositories if r.institution_id == int(institution_id)]

        if repository:
            return repository[0]

