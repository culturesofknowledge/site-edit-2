import logging
from typing import Union, List, Generator, Tuple, Set, Type, Callable

from openpyxl.cell import Cell
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
# import pandas as pd
from pandas import ExcelFile

from institution.models import CofkCollectInstitution
from location.models import CofkCollectLocation
from person.models import CofkCollectPerson
from uploader.OpenpyxlReaderWOFormatting import OpenpyxlReaderWOFormatting
from uploader.constants import mandatory_sheets
from uploader.entities.entity import CofkEntity
from uploader.entities.locations import CofkLocations
from uploader.entities.manifestations import CofkManifestations
from uploader.entities.people import CofkPeople
from uploader.entities.repositories import CofkRepositories
from uploader.entities.work import CofkWork
from uploader.models import CofkCollectUpload
from uploader.validation import CofkMissingSheetError, CofkMissingColumnError, CofkNoDataError

log = logging.getLogger(__name__)


class CofkColumn:
    def __init__(self, name):
        self.name = name
        self.required: bool = False
        self.validation: Union[Callable, None] = None


class CofkSheet:
    def __init__(self, sheet: Worksheet):
        self.worksheet: Worksheet = sheet
        self.header: List[str]
        self.rows: int
        self.name: str = sheet.title
        self.entities: Union[Type[CofkEntity], None] = None

        # Obtain header and row count of non-empty rows
        rows = (row for row in self.worksheet.iter_rows() if any([cell.value is not None for cell in row]))
        self.header = [cell.value for cell in next(rows) if cell.value is not None]
        next(rows)
        self.rows = sum(1 for _ in rows)

    @property
    def data(self) -> Generator[Tuple[Cell], None, None]:
        rows = (row for row in self.worksheet.iter_rows() if any([cell.value is not None for cell in row]))
        next(rows)  # First row is header names
        next(rows)  # Second row is explanatory notes
        return rows

    @property
    def missing_columns(self) -> Set[str]:
        return set(mandatory_sheets[self.name]['columns']).difference(set(self.header))


class CofkUploadExcelFile:

    def __init__(self, upload: CofkCollectUpload, filename: str):
        """
        :param filename:
        """
        self.errors = {}
        self.wb: Union[Workbook, None] = None
        self.works = None
        self.upload = upload
        self.filename = filename
        self.repositories = None
        self.locations = None
        self.people = None
        self.manifestations = None
        self.total_errors = 0
        self.data = {}
        self.missing_columns: List[CofkMissingColumnError] = []

        try:
            # read_only mode
            self.wb = load_workbook(filename=filename, data_only=True, read_only=True)
            # pd.read_excel(filename, sheet_name=None, usecols=lambda c: not c.startswith('Unnamed:'))
        except ValueError:
            pass
            # from OpenpyxlReaderWOFormatting import load_workbook as l2
            # ExcelFile._engines['openpyxl_wo_formatting'] = OpenpyxlReaderWOFormatting
            # self.wb = pd.read_excel(filename, sheet_name=None,
            #                        usecols=lambda c: not c.startswith('Unnamed:'),
            #                        engine='openpyxl_wo_formatting')

        # Make sure all sheets are present
        self.check_sheets()

        for sheet in mandatory_sheets.keys():
            self.data[sheet] = CofkSheet(self.wb[sheet])

            log.debug(f'{sheet} {self.data[sheet].rows}')

            # Using same iteration to verify that required columns are present
            if len(self.data[sheet].missing_columns) > 1:
                ms = ', '.join(self.data[sheet].missing_columns)
                self.missing_columns.append(CofkMissingColumnError(f'Missing columns {ms} from the sheet {sheet}'))
            elif len(self.data[sheet].missing_columns) == 1:
                self.missing_columns.append(
                    CofkMissingColumnError(
                        f'Missing column {self.data[sheet].missing_columns.pop()} from the sheet {sheet}'))

        if self.missing_columns:
            raise CofkMissingColumnError(self.missing_columns)

        # Quick check that works are present in upload, no need to go further if not
        # sheets have already been verified to be present so no KeyError raised
        if self.data['Work'].rows == 0:
            msg = "Spreadsheet contains no data"
            log.error(msg)
            raise CofkNoDataError(msg)

        # It's process the sheets in reverse order, starting with repositories/institutions
        self.data['Repositories'].entities = CofkRepositories(upload=self.upload,
                                                              sheet_data=self.data['Repositories'].data,
                                                              sheet_name='Repositories')

        # The next sheet is places/locations,
        self.data['Places'].entities = CofkLocations(upload=self.upload, sheet_data=self.data['Places'].data,
                                                     work_data=self.data['Work'].worksheet,
                                                     sheet_name='Places')

        # The next sheet is people
        self.data['People'].entities = CofkPeople(upload=self.upload, sheet_data=self.data['People'].data,
                                                  work_data=self.data['Work'].worksheet, sheet_name='People')

        # Second last but not least, the works themselves
        self.data['Work'].entities = CofkWork(upload=self.upload, sheet_data=self.data['Work'].data,
                                              people=self.data['People'].entities.people,
                                              locations=self.data['Places'].entities.locations,
                                              sheet_name='Work')
        log.debug(vars(self))
        raise ValueError('stuff')
        self.upload.total_works = len(self.works.ids)
        '''
        # The last sheet is manifestations
        if self.works.works:
            self.manifestations = CofkManifestations(upload=self.upload, sheet_data=self.data['manifestation'],
                                                     repositories=self.repositories, works=self.works)

        if self.people.other_errors:
            for row_index in self.people.other_errors:
                for error in self.people.other_errors[row_index]:
                    if error['entity'] == 'work':
                        self.works.add_error(error['error'], None, row_index)'''

        if self.works.errors:
            self.errors['work'] = self.works.format_errors_for_template()
            self.total_errors += self.errors['work']['total']

        '''if self.people.errors:
            self.errors['people'] = self.people.format_errors_for_template()
            self.total_errors += self.errors['people']['total']'''

        if self.repositories.errors:
            self.errors['repositories'] = self.repositories.format_errors_for_template()
            self.total_errors += self.errors['repositories']['total']

        '''if self.locations.errors:
            self.errors['locations'] = self.locations.format_errors_for_template()
            self.total_errors += self.errors['locations']['total']

        if self.manifestations and self.manifestations.errors:
            self.errors['manifestations'] = self.manifestations.format_errors_for_template()
            self.total_errors += self.errors['manifestations']['total']'''

    def check_sheets(self):
        # Verify all required sheets are present
        difference = list(set(mandatory_sheets.keys()) - set([n for n in self.wb.sheetnames]))

        if difference:
            if len(difference) == 1:
                msg = f'Missing sheet: {difference[0].title()}'
            else:
                msg = f'Missing sheets: {", ".join([n.title() for n in difference])}'
            log.error(msg)
            raise CofkMissingSheetError(msg)

        log.debug(f'All {len(mandatory_sheets)} sheets verified')

    def create_objects(self):

        CofkCollectInstitution.objects.bulk_create(self.repositories)

        try:
            CofkCollectLocation.objects.bulk_create(self.locations)
        except ValueError:
            # Will error if location_id != int
            pass

        log.debug(f'Created {len(self.locations)} locations.')
