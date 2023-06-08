import logging
from abc import ABC
from typing import List, Generator, Tuple

from openpyxl.cell import Cell

from location.models import CofkUnionLocation
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectLocation

log = logging.getLogger(__name__)


class CofkLocations(CofkEntity, ABC):
    """
    This class processes the Places spreadsheet
    """
    def __init__(self, upload: CofkCollectUpload, sheet, work_data: Generator[Tuple[Cell], None, None]):
        super().__init__(upload, sheet)
        self.work_data = work_data
        self.locations: List[CofkCollectLocation] = []
        location_ids = list(CofkCollectLocation.objects.values_list('location_id').order_by('-location_id')[:1])
        latest_location_id = location_ids[0][0] if len(location_ids) == 1 else 0

        for index, row in enumerate(self.iter_rows(), start=1 + self.sheet.header_length):
            loc_dict = self.get_row(row, index)
            self.check_required(loc_dict)
            self.check_data_types(loc_dict)

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
            elif 'location_name' in loc_dict and not self.location_exists_by_name(loc_dict['location_name']):
                latest_location_id += 1
                location = {'location_name': loc_dict['location_name'],
                            'upload': upload,
                            'location_id': latest_location_id,
                            'editors_notes': loc_dict['editors_notes'] if 'editors_notes' in loc_dict else None}
                self.locations.append(CofkCollectLocation(**location))

    def location_exists_by_name(self, name: str) -> bool:
        return len([p for p in self.locations if p.location_name == name and p.location_id is None]) > 0
