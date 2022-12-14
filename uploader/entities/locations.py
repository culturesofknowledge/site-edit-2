import logging
from abc import ABC
from typing import List, Generator, Tuple

from openpyxl.cell import Cell

from location.models import CofkCollectLocation, CofkUnionLocation
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkLocations(CofkEntity, ABC):

    def __init__(self, upload: CofkCollectUpload, sheet, work_data: Generator[Tuple[Cell], None, None]):
        super().__init__(upload, sheet)
        self.work_data = work_data
        self.locations: List[CofkCollectLocation] = []

        for index, row in enumerate(self.iter_rows(), start=1 + self.sheet.header_length):
            loc_dict = self.get_row(row, index)
            self.check_required(loc_dict)
            self.check_data_types(loc_dict)

            if not self.errors:
                if 'location_id' in loc_dict:
                    loc_id = loc_dict['location_id']

                    if loc_id not in self.ids:
                        loc_dict['union_location'] = CofkUnionLocation.objects\
                            .filter(location_id=loc_id).first()

                        loc_dict['upload'] = upload
                        self.locations.append(CofkCollectLocation(**loc_dict))
                        self.ids.append(loc_id)
                    else:
                        log.warning(f'{loc_id} duplicated in {self.sheet.name} sheet.')
                else:
                    log.warning(f'New location {loc_dict} to be created?')

        if self.locations:
            self.bulk_create(self.locations)
