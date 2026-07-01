import logging
from abc import ABC
from typing import List, Generator, Tuple

from django.db.models import Max
from openpyxl.cell import Cell

from location.models import CofkUnionLocation
from uploader.constants import BULK_LOCATIONS_SHEET, BULK_LOCATIONS_HEADER_MAP, normalize_header
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
        latest_location_id = CofkCollectLocation.objects.aggregate(Max('location_id'))['location_id__max'] or 0

        for index, row in enumerate(self.sheet.worksheet.iter_rows(), start=1):
            row_dict = self.get_row(row, index)

            if index <= self.sheet.header_length or row_dict == {}:
                continue

            self.check_required(row_dict)
            self.check_data_types(row_dict)

            for loc_dict in self.clean_lists(row_dict, 'location_id', 'location_name'):
                if loc_dict['location_id'] is not None:
                    try:
                        loc_id = int(loc_dict['location_id'])
                        loc_dict['location_id'] = loc_id  # Update dict with integer value
                    except (ValueError, TypeError):
                        self.add_error(f'Location_id "{loc_dict["location_id"]}" is not a number')
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
                elif not self.location_exists_by_name(loc_dict['location_name']):
                    latest_location_id += 1
                    location = {'location_name': loc_dict['location_name'],
                                'upload': upload,
                                'location_id': latest_location_id,
                                'editors_notes': loc_dict['editors_notes'] if 'editors_notes' in loc_dict else None}
                    self.locations.append(CofkCollectLocation(**location))

    def location_exists_by_name(self, name: str) -> bool:
        loc = [p for p in self.locations if p.location_name and p.location_name.lower() == name.lower() and p.union_location is None]
        return len(loc) > 0


class CofkBulkLocations(CofkEntity, ABC):
    """
    Processes the bulk Places spreadsheet (BULKnewLOCATIONrecordsTEMPLATE format).

    All records are treated as new locations — no IDs referencing the Union catalogue.
    Columns are mapped by position using BULK_LOCATIONS_SHEET.
    The location_name is constructed from the individual place-name component fields.
    """

    @property
    def fields(self) -> dict:
        return BULK_LOCATIONS_SHEET

    def __init__(self, upload: CofkCollectUpload, sheet):
        super().__init__(upload, sheet)
        self.locations: List[CofkCollectLocation] = []
        latest_location_id = CofkCollectLocation.objects.aggregate(Max('location_id'))['location_id__max'] or 0

        col_to_field = {
            col: BULK_LOCATIONS_HEADER_MAP[normalize_header(header)]
            for col, header in self.sheet.header_cols.items()
            if normalize_header(header) in BULK_LOCATIONS_HEADER_MAP
        }

        for index, row in enumerate(self.sheet.worksheet.iter_rows(), start=1):
            row_dict = self.get_row_by_header_map(row, index, col_to_field)

            if index <= self.sheet.header_length or row_dict == {}:
                continue

            self.check_required(row_dict)
            self.check_data_types(row_dict)

            location_name = self._build_location_name(row_dict)

            if not location_name:
                self.add_error('Row contains no location data; at least one place name field is required.')
                continue

            if self.location_exists_by_name(location_name):
                log.warning(f'Duplicate location "{location_name}" in bulk Places sheet, skipping.')
                continue

            latest_location_id += 1
            loc_kwargs = {
                'location_id': latest_location_id,
                'upload': upload,
                'location_name': location_name,
            }

            _system_fields = {'upload', 'location_id', 'union_location', 'location_name'}
            for field, value in row_dict.items():
                if field not in _system_fields:
                    # latitude and longitude are stored as CharField but come from Excel as floats
                    loc_kwargs[field] = str(value) if field in ('latitude', 'longitude') else value

            self.locations.append(CofkCollectLocation(**loc_kwargs))

    def _build_location_name(self, row_dict: dict) -> str:
        """Build a display name from whichever place component fields are present."""
        ordered_fields = ['element_1_eg_room', 'element_2_eg_building', 'element_3_eg_parish',
                          'element_4_eg_city', 'element_5_eg_county', 'element_6_eg_country',
                          'element_7_eg_empire']
        parts = [str(row_dict[f]) for f in ordered_fields if f in row_dict and row_dict[f] is not None]
        return ', '.join(parts)

    def location_exists_by_name(self, name: str) -> bool:
        return any(
            loc.location_name and loc.location_name.lower() == name.lower()
            for loc in self.locations
        )
