import logging
from abc import ABC
from typing import List

from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectManifestation, CofkCollectWork, CofkCollectInstitution

log = logging.getLogger(__name__)


class CofkManifestations(CofkEntity, ABC):

    def __init__(self, upload: CofkCollectUpload, sheet,
                 repositories: List[CofkCollectInstitution], works: List[CofkCollectWork]):
        super().__init__(upload, sheet)

        self.repositories = repositories
        self.works = works
        self.manifestations: List[CofkCollectManifestation] = []

        for index, row in enumerate(self.iter_rows(), start=1 + self.sheet.header_length):
            man_dict = self.get_row(row, index)
            self.check_required(man_dict)
            self.check_data_types(man_dict)

            if not self.errors:
                if 'iwork_id' in man_dict:
                    man_dict['iwork'] = self.get_work(man_dict.pop('iwork_id'))

                if 'repository_id' in man_dict:
                    man_dict['repository'] = self.get_repository(man_dict.pop('repository_id'))

                if 'printed_edition_notes' in man_dict:
                    man_dict['printed_edition_details'] = man_dict.pop('printed_edition_notes')
                # TODO can this be right?
                if 'manifestation_type_p' in man_dict:
                    man_dict['manifestation_type'] = man_dict.pop('manifestation_type_p')

                if 'repository_name' in man_dict:
                    del man_dict['repository_name']

                man_dict['upload'] = upload
                self.manifestations.append(CofkCollectManifestation(**man_dict))

        if self.manifestations:
            self.bulk_create(self.manifestations)

    def get_work(self, work_id: str) -> CofkCollectWork:
        work = [w for w in self.works if w.iwork_id == int(work_id)]

        if work:
            return work[0]

    def get_repository(self, institution_id: str) -> CofkCollectInstitution:
        repository = [r for r in self.repositories if r.institution_id == int(institution_id)]

        if repository:
            return repository[0]
