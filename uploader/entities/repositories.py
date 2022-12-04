import logging
from typing import Generator, Tuple, List

from django.core.exceptions import ValidationError
from openpyxl.cell import Cell

from institution.models import CofkCollectInstitution, CofkUnionInstitution
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkRepositories(CofkEntity):
    def __init__(self, upload: CofkCollectUpload, sheet_data: Generator[Tuple[Cell], None, None],
                 sheet_name: str):
        """
        This entity processes the repositories/institutions from the Excel sheet.
        They do not need to be cross-referenced or verified.
        No entities are committed at this stage, they are aggregated in self.institutions.
        """
        super().__init__(upload, sheet_data, sheet_name)
        self.institutions: List[CofkCollectInstitution] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            inst_dict = {self.get_column_name_by_index(cell.column): cell.value for cell in row}
            self.check_required(inst_dict, index)
            self.check_data_types(inst_dict, index)
            log.debug(inst_dict)

            # Collect institutions while there's no errors,
            # no reason to do so if there's errors
            if not self.errors:
                if 'institution_id' in inst_dict:
                    inst_dict['union_institution'] = CofkUnionInstitution.objects.filter(
                        institution_id=inst_dict['institution_id']).first()
                    del inst_dict['institution_id']

                inst_dict['upload'] = upload
                self.institutions.append(CofkCollectInstitution(**inst_dict))
                # self.ids_to_be_created.append(inst.institution_id)

