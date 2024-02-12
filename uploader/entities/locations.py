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

        for index, row in enumerate(self.sheet.worksheet.iter_rows(), start=1):
            row_dict = self.get_row(row, index)

            if index <= self.sheet.header_length or row_dict == {}:
                continue

            self.check_required(row_dict)
            self.check_data_types(row_dict)

            for loc_dict in self.clean_lists(row_dict, 'location_id', 'location_name'):
                if 'location_id' in loc_dict and loc_dict['location_id'] is not None:
                    loc_id = loc_dict['location_id']

                    try:
                        int(loc_id)
                    except ValueError:
                        self.add_error(f'Location_id "{loc_id}" is not a number')
                        continue

                    if loc_id not in self.ids:
                        loc_dict['union_location'] = CofkUnionLocation.objects.filter(location_id=loc_id).first()

                        if loc_dict['union_location'] is None:
                            self.add_error(f'There is no location with the id {loc_id} in the Union catalogue.')

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
        loc = [p for p in self.locations if p.location_name.lower() == name.lower() and p.union_location is None]
        return len(loc) > 0
