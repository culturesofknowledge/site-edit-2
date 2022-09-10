import logging

import pandas as pd
from django.core.exceptions import ValidationError

from location.models import CofkCollectLocation
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload

log = logging.getLogger(__name__)


class CofkLocations(CofkEntity):
    def __init__(self, upload: CofkCollectUpload, sheet_data: pd.DataFrame, limit=None):
        super().__init__(upload, sheet_data)
        self.__location_id = None
        limit = limit if limit else len(self.sheet_data.index)
        self.ids = []

        # Process each row in turn, using a dict comprehension to filter out empty values
        for i in range(1, limit):
            self.process_location({k: v for k, v in self.sheet_data.iloc[i].to_dict().items() if v is not None})

    def process_location(self, repository_data):
        self.row_data = repository_data
        self.row_data['upload_id'] = self.upload.upload_id
        self.__location_id = repository_data['location_id']

        self.check_data_types('Places')

        log.info("Processing location, location_id #{}, upload_id #{}".format(
            1, self.upload.upload_id))

        if not self.already_exists():
            # Name, city and country are required
            location = CofkCollectLocation(**self.row_data)
            location.location_id = 1
            location.element_1_eg_room = 0
            location.element_2_eg_building = 0
            location.element_3_eg_parish = 0
            location.element_4_eg_city = 0
            location.element_5_eg_county = 0
            location.element_6_eg_country = 0
            location.element_7_eg_empire = 0

            try:
                location.save()
            except ValidationError as ve:
                self.add_error(ve)
                print(ve)

            self.ids.append(self.__location_id)

            log.info("Location created.")

    def already_exists(self) -> bool:
        return CofkCollectLocation.objects \
            .filter(upload_id=self.upload) \
            .exists()
