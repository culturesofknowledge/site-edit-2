import logging
from typing import List

import pandas as pd
from django.core.exceptions import ValidationError

from location.models import CofkCollectLocation
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkLocations(CofkEntity):

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

        CofkCollectLocation.objects.bulk_create(self.locations)

        log.debug(f'Created {len(self.locations)} locations.')

        return sheet_locations

    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, work_data: pd.DataFrame):
        super().__init__(upload, sheet_data)
        self.work_data = work_data
        self.locations = []
        self.origins = []
        self.destinations = []

        unique_sheet_locations = set(self.process_places_sheet())
        unique_work_locations = set(self.process_work_sheet())

        if unique_work_locations != unique_sheet_locations:
            if unique_work_locations > unique_sheet_locations:
                loc = [f'{l[0]} #{l[1]}' for l in list(unique_sheet_locations - unique_work_locations)]
                loc_joined = ', '.join(loc)
                self.add_error(ValidationError(f'The location {loc_joined} is referenced in the Work spreadsheet'
                                               f' but is missing from the Places spreadsheet'))
            elif unique_work_locations < unique_sheet_locations:
                loc = [str(l) for l in list(unique_work_locations - unique_sheet_locations)]
                loc_joined = ', '.join(loc)
                self.add_error(ValidationError(f'The person {loc_joined} is referenced in the Places spreadsheet'
                                               f' but is missing from the Work spreadsheet'))

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

                if 'origin' in locations_relation[0]:
                    self.origins.append({'name': related_location[0], 'id': related_location[1]})
                elif 'destination' in locations_relation[0]:
                    self.destinations.append({'name': related_location[0], 'id': related_location[1]})

                work_locations.append(related_location)

        return work_locations
