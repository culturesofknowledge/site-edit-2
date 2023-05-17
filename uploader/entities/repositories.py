import logging
from abc import ABC
from typing import List

from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectInstitution
from institution.models import CofkUnionInstitution

log = logging.getLogger(__name__)


class CofkRepositories(CofkEntity, ABC):

    def __init__(self, upload: CofkCollectUpload, sheet):
        super().__init__(upload, sheet)
        self.institutions: List[CofkCollectInstitution] = []

        for index, row in enumerate(self.iter_rows(), start=1 + self.sheet.header_length):
            inst_dict = self.get_row(row, index)
            self.check_required(inst_dict)
            self.check_data_types(inst_dict)

            if 'institution_id' in inst_dict:
                inst_id = inst_dict['institution_id']
                if inst_id not in self.ids:
                    inst_dict['union_institution'] = CofkUnionInstitution.objects.filter(
                        institution_id=inst_id).first()

                    inst_dict['upload'] = upload
                    self.institutions.append(CofkCollectInstitution(**inst_dict))
                    self.ids.append(inst_id)
                else:
                    log.warning(f'{inst_id} duplicated in {self.sheet.name} sheet.')

        if self.institutions:
            self.bulk_create(self.institutions)
            self.log_summary.append(f'{len(self.institutions)} CofkCollectInstitution')
