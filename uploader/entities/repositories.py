import logging
from typing import Generator, Tuple, List

from django.core.exceptions import ValidationError
from openpyxl.cell import Cell

from institution.models import CofkCollectInstitution
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
        self.institution_ids: List[int] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            repo = {self.get_column_name_by_index(cell.column): cell.value for cell in row}
            self.check_required(repo, index)
            self.check_data_types(repo, index)

            # Collect institutions while there's no errors,
            # no reason to do so if there's errors
            if not self.errors:
                inst = CofkCollectInstitution(**repo)

                if inst.institution_id not in self.institution_ids:
                    inst.upload = upload
                    self.institutions.append(inst)
                    self.institution_ids.append(inst.institution_id)
                else:
                    msg = f'Column institution_id in {self.sheet_name} is a duplicate id.'
                    log.error(msg)
                    self.add_error(ValidationError(msg), index)
