import logging
from typing import List

from institution.models import CofkCollectInstitution, CofkUnionInstitution
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkRepositories(CofkEntity):
    def __init__(self, upload: CofkCollectUpload, sheet):
        super().__init__(upload, sheet)
        self.institutions: List[CofkCollectInstitution] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            inst_dict = self.get_row(row)
            self.check_required(inst_dict, index)
            self.check_data_types(inst_dict, index)

            # Collect institutions while there's no errors,
            # no reason to do so if there's errors
            if not self.errors:
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
                else:
                    # New repo to be created?
                    pass

        if self.institutions:
            self.bulk_create(self.institutions)

