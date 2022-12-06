import logging
from typing import List, Generator, Tuple

from django.core.exceptions import ValidationError
from openpyxl.cell import Cell

from location.models import CofkCollectLocation, CofkUnionLocation
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload
from work.models import CofkCollectOriginOfWork, CofkCollectDestinationOfWork

log = logging.getLogger(__name__)


class CofkLocations(CofkEntity):

    def __init__(self, upload: CofkCollectUpload, sheet, work_data: Generator[Tuple[Cell], None, None]):
        super().__init__(upload, sheet)
        self.work_data = work_data
        self.locations: List[CofkCollectLocation] = []
        # self.origins: List[CofkCollectOriginOfWork] = []
        # self.destinations: List[CofkCollectDestinationOfWork] = []

        for index, row in enumerate(self.iter_rows(), start=1):
            loc_dict = {self.get_column_name_by_index(cell.column): cell.value for cell in row}
            self.check_required(loc_dict, index)
            self.check_data_types(loc_dict, index)

            if not self.errors:
                if 'location_id' in loc_dict:
                    loc_dict['union_location'] = CofkUnionLocation.objects\
                        .filter(location_id=loc_dict['location_id']).first()
                    del loc_dict['location_id']

                loc_dict['upload'] = upload
                self.locations.append(CofkCollectLocation(**loc_dict))

        if self.locations:
            CofkCollectLocation.objects.bulk_create(self.locations, batch_size=500)
            log.debug(f'{len(self.locations)} locations created')

        # When we've iterated over all rows we can check whether all locations mentioned in work sheet
        # occur in places sheet
        # This could be done at the end? During the one work iteration?

        # unique_sheet_locations = set(self.process_places_sheet())
        '''unique_work_locations = set(self.process_work_sheet())

        if unique_work_locations != unique_sheet_locations:
            if unique_work_locations > unique_sheet_locations:
                loc = [f'{l[0]} #{l[1]}' for l in list(unique_work_locations - unique_sheet_locations)]
                loc_joined = ', '.join(loc)
                plural = 'location is' if len(loc) == 1 else f'following {len(loc)} locations are'
                tense = 'is' if len(loc) == 1 else 'are'
                self.add_error(ValidationError(f'The {plural} referenced in the Work spreadsheet'
                                               f' but {tense} missing from the Places spreadsheet: {loc_joined}'))
            elif unique_work_locations < unique_sheet_locations:
                loc = [f'{l[0]} #{l[1]}' for l in list(unique_sheet_locations - unique_work_locations)]
                loc_joined = ', '.join(loc)
                plural = 'location is' if len(loc) == 1 else f'following {len(loc)} locations are'
                tense = 'is' if len(loc) == 1 else 'are'
                self.add_error(ValidationError(f'The {plural} referenced in the Places spreadsheet'
                                               f' but {tense} missing from the Work spreadsheet: {loc_joined}'))'''

    def process_places_sheet(self) -> List[tuple]:
        """
        Get all people from people spreadsheet
        Populating a list of tuples of (Name, iperson_id)
        TODO where does Geonames lookup happen?
        """
        sheet_locations = []
        for i in range(1, len(self.sheet_data.index)):
            self.row_data = {k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None}

            self.check_data_types('Places')
            location_id = self.row_data['location_id'] if 'location_id' in self.row_data else 1

            location = CofkCollectLocation(**self.row_data)

            if location_id and isinstance(location_id, int):
                location.union_location = CofkUnionLocation.objects.filter(location_id=location_id).first()

            location.location_id = location_id
            location.element_1_eg_room = 0
            location.element_2_eg_building = 0
            location.element_3_eg_parish = 0
            location.element_4_eg_city = 0
            location.element_5_eg_county = 0
            location.element_6_eg_country = 0
            location.element_7_eg_empire = 0

            self.locations.append(location)

            sheet_locations.append((self.row_data['location_name'], location_id))

        return sheet_locations

    def process_work_sheet(self) -> List[tuple]:
        """
        Get all people from references in Work spreadsheet.
        Work sheets can contain multiple values for people per work. If so, the values are separated by
        a semicolon with no space on either side.
        Populating a list of tuples of (Name, iperson_id)
        """
        work_locations = []
        work_locations_fields = [('origin_name', 'origin_id'), ('destination_name', 'destination_id')]

        for i in range(1, len(self.work_data.index)):
            self.row_data = {k: v for k, v in self.work_data.iloc[i].to_dict().items() if v is not None}

            for locations_relation in [w for w in work_locations_fields if w[0] in self.row_data]:
                related_location = (self.row_data[locations_relation[0]],
                                    self.row_data[locations_relation[1]])
                loc = {'name': related_location[0], 'id': related_location[1]}

                if 'origin' in locations_relation[0] and loc not in self.origins:
                    self.origins.append(loc)
                elif 'destination' in locations_relation[0] and loc not in self.destinations:
                    self.destinations.append(loc)

                work_locations.append(related_location)

        return work_locations
