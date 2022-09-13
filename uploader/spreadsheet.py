import logging

import pandas as pd
from pandas import ExcelFile

from uploader.OpenpyxlReaderWOFormatting import OpenpyxlReaderWOFormatting
from uploader.constants import mandatory_sheets
from uploader.entities.locations import CofkLocations
from uploader.entities.manifestations import CofkManifestations
from uploader.entities.people import CofkPeople
from uploader.entities.repositories import CofkRepositories
from uploader.entities.work import CofkWork
from uploader.models import CofkCollectUpload
from uploader.validation import CofkMissingSheetError, CofkMissingColumnError

log = logging.getLogger(__name__)


class CofkUploadExcelFile:

    def __init__(self, upload: CofkCollectUpload, filename: str):
        """
        :param logger:
        :param filename:
        """
        self.errors = {}
        self.works = None
        self.upload = upload
        self.filename = filename
        self.repositories = None
        self.locations = None
        self.people = None
        self.manifestations = None
        self.total_errors = 0
        self.data = {}

        """
        Setting sheet_name to None returns a dict with sheet name as key and data frame as value
        Occasionally additional data is included that we cannot parse, so we ignore "Unnamed:" columns
        Supports xls, xlsx, xlsm, xlsb, odf, ods and odt file extensions read from a local filesystem or URL.
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
        """
        try:
            self.wb = pd.read_excel(filename, sheet_name=None, usecols=lambda c: not c.startswith('Unnamed:'))
        except ValueError:
            ExcelFile._engines['openpyxl_wo_formatting'] = OpenpyxlReaderWOFormatting
            self.wb = pd.read_excel(filename, sheet_name=None,
                                    usecols=lambda c: not c.startswith('Unnamed:'),
                                    engine='openpyxl_wo_formatting')

        self.check_sheets()

        for sheet in [s['name'] for s in mandatory_sheets]:
            self.data[sheet.lower()] = self.get_sheet_data(sheet)

        self.check_columns()

        self.check_data_present()

        # It's process the sheets in reverse order, starting with repositories/institutions
        self.repositories = CofkRepositories(upload=self.upload, sheet_data=self.data['repositories'])

        # The next sheet is places/locations
        self.locations = CofkLocations(upload=self.upload, sheet_data=self.data['places'],
                                       work_data=self.data['work'])

        # The next sheet is people
        self.people = CofkPeople(upload=self.upload, sheet_data=self.data['people'],
                                 work_data=self.data['work'])

        # Second last but not least, the works themselves
        self.works = CofkWork(upload=self.upload, sheet_data=self.data['work'], people=self.people,
                              locations=self.locations)
        self.upload.total_works = len(self.works.ids)

        # The last sheet is manifestations
        self.manifestations = CofkManifestations(upload=self.upload, sheet_data=self.data['manifestation'])

        if self.people.other_errors:
            for row_index in self.people.other_errors:
                for error in self.people.other_errors[row_index]:
                    if error['entity'] == 'work':
                        self.works.add_error(error['error'], None, row_index)

        if self.works.errors:
            self.errors['work'] = self.works.format_errors_for_template()
            self.total_errors += self.errors['work']['total']

        if self.people.errors:
            self.errors['people'] = self.people.format_errors_for_template()
            self.total_errors += self.errors['people']['total']

        if self.repositories.errors:
            self.errors['repositories'] = self.repositories.format_errors_for_template()
            self.total_errors += self.errors['repositories']['total']

        if self.locations.errors:
            self.errors['locations'] = self.locations.format_errors_for_template()
            self.total_errors += self.errors['locations']['total']

        if self.manifestations.errors:
            self.errors['manifestations'] = self.manifestations.format_errors_for_template()
            self.total_errors += self.errors['manifestations']['total']

    def get_sheet_data(self, sheet_name: str) -> pd.DataFrame:
        return self.wb[sheet_name].where(pd.notnull(self.wb[sheet_name]), None)

    def check_data_present(self):
        # if index length is less than 2 then there's only the header, no data
        if len(self.data['work'].index) < 2:
            msg = "Spreadsheet contains no data"
            log.error(msg)

            raise ValueError(msg)

    def check_sheets(self):
        # Verify all required sheets are present
        sheet_names = [s['name'] for s in mandatory_sheets]

        if not all(elem in list(self.wb.keys()) for elem in sheet_names):
            msg = "Missing sheet/s: {}".format(", ".join(list(sheet_names - self.wb.keys())))
            log.error(msg)
            raise CofkMissingSheetError(msg)

        log.debug("All {} sheets verified".format(len(mandatory_sheets)))

    def check_columns(self):
        total_missing_columns = []
        for sheet in mandatory_sheets:
            missing_columns = []
            sheet_name = sheet['name']
            for ms in set(sheet['columns']).difference(set(self.data[sheet_name.lower()].columns)):
                missing_columns.append(ms)

            if missing_columns:
                if len(missing_columns) > 1:
                    ms = ', '.join(missing_columns)
                    missing_columns.append(CofkMissingColumnError(f'Missing columns {ms} from the sheet {sheet_name}'))
                else:
                    missing_columns.append(
                        CofkMissingColumnError(f'Missing column {missing_columns[0]} from the sheet {sheet_name}'))
                total_missing_columns += missing_columns

        if total_missing_columns:
            log.info(total_missing_columns)
            raise CofkMissingColumnError(total_missing_columns)
