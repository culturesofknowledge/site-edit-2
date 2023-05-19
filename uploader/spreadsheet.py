import logging
from typing import Union, List, Generator, Tuple, Set, Type

from openpyxl.cell import Cell
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from uploader.constants import MANDATORY_SHEETS
from uploader.entities.entity import CofkEntity
from uploader.entities.locations import CofkLocations
from uploader.entities.manifestations import CofkManifestations
from uploader.entities.people import CofkPeople
from uploader.entities.repositories import CofkRepositories
from uploader.entities.work import CofkWork
from uploader.models import CofkCollectUpload
from uploader.validation import CofkExcelFileError

log = logging.getLogger(__name__)


class CofkSheet:
    def __init__(self, sheet: Worksheet):
        self.worksheet: Worksheet = sheet
        self.header: List[str]
        self.rows: int
        self.name: str = sheet.title
        self.entities: Union[Type[CofkEntity], None] = None
        # Hard-coded number of header rows
        self.header_length: int = 2

        # Obtain header and row count of non-empty rows
        rows = (row for row in self.worksheet.iter_rows() if any([cell.value is not None for cell in row]))
        self.header = [cell.value for cell in next(rows) if cell.value is not None]
        next(rows)
        self.rows = sum(1 for _ in rows)

    @property
    def data(self) -> Generator[Tuple[Cell], None, None]:
        rows = (row for row in self.worksheet.iter_rows() if any([cell.value is not None for cell in row]))

        for i in range(self.header_length):
            next(rows)

        return rows

    @property
    def missing_columns(self) -> Set[str]:
        return set(MANDATORY_SHEETS[self.name]['columns']).difference(set(self.header))


class CofkUploadExcelFile:

    def __init__(self, upload: CofkCollectUpload, filename: str):
        """
        :param filename:
        """
        self.errors = {}
        self.wb: Workbook | None = None
        self.works = None
        self.upload = upload
        self.filename = filename
        self.total_errors = 0
        self.sheets: dict[str: CofkSheet] = {}
        self.missing: List[str] = []

        self.wb = load_workbook(filename=filename, data_only=True, read_only=True)

        # Make sure all sheets are present
        self.check_sheets()

        for sheet in MANDATORY_SHEETS.keys():
            try:
                self.sheets[sheet] = CofkSheet(self.wb[sheet])
            except StopIteration:
                self.missing.append(f'{sheet} is missing its header rows.')
                #raise CofkExcelFileError(f'{sheet} is missing its header rows.')

            # Using same iteration to verify that required columns are present
            if sheet in self.sheets and self.sheets[sheet].missing_columns:
                if len(self.sheets[sheet].missing_columns) > 1:
                    ms = 'columns ' + ', '.join(self.sheets[sheet].missing_columns)

                else:
                    ms = f'column "{self.sheets[sheet].missing_columns.pop()}"'
                self.missing.append(f'Missing {ms} from the sheet {sheet}.')

        if self.missing:
            raise CofkExcelFileError('</br> '.join(self.missing))

        # Quick check that works are present in upload, no need to go further if not
        # sheets have already been verified to be present so no KeyError raised
        if self.sheets['Work'].rows == 0:
            raise CofkExcelFileError("Spreadsheet contains no works.")

        sheets = ', '.join([f'{sheet}: {self.sheets[sheet].rows}' for sheet in MANDATORY_SHEETS.keys()])
        log.info(f'{self.upload}: all {len(MANDATORY_SHEETS)} sheets verified: [{sheets}]')

        # It's process the sheets in reverse order, starting with repositories/institutions
        self.sheets['Repositories'].entities = CofkRepositories(upload=self.upload,
                                                                sheet=self.sheets['Repositories'])

        # The next sheet is places/locations,
        self.sheets['Places'].entities = CofkLocations(upload=self.upload, sheet=self.sheets['Places'],
                                                       work_data=self.sheets['Work'].worksheet)

        # The next sheet is people
        self.sheets['People'].entities = CofkPeople(upload=self.upload, sheet=self.sheets['People'])

        # Second last but not least, the works themselves
        self.sheets['Work'].entities = CofkWork(upload=self.upload, sheet=self.sheets['Work'],
                                                people=self.sheets['People'].entities.people,
                                                locations=self.sheets['Places'].entities.locations)

        # The last sheet is manifestations
        self.sheets['Manifestation'].entities = CofkManifestations(upload=self.upload,
                                                                   sheet=self.sheets['Manifestation'],
                                                                   repositories=self.sheets[
                                                                       'Repositories'].entities.institutions,
                                                                   works=self.sheets['Work'].entities.works)

        if self.sheets['People'].entities.other_errors:
            for row_index in self.sheets['People'].entities.other_errors:
                for error in self.sheets['People'].entities.other_errors[row_index]:
                    if error['entity'] == 'work':
                        self.sheets['Work'].entities.add_error(error['error'], None, row_index)

        if self.sheets['Work'].entities.errors:
            self.errors['work'] = self.sheets['Work'].entities.format_errors_for_template()
            self.total_errors += self.errors['work']['total']

        if self.sheets['People'].entities.errors:
            self.errors['people'] = self.sheets['People'].entities.format_errors_for_template()
            self.total_errors += self.errors['people']['total']

        if self.sheets['Repositories'].entities.errors:
            self.errors['repositories'] = self.sheets['Repositories'].entities.format_errors_for_template()
            self.total_errors += self.errors['repositories']['total']

        if self.sheets['Places'].entities.errors:
            self.errors['locations'] = self.sheets['Places'].entities.format_errors_for_template()
            self.total_errors += self.errors['locations']['total']

        if self.sheets['Manifestation'].entities and self.sheets['Manifestation'].entities.errors:
            self.errors['manifestations'] = self.sheets['Manifestation'].entities.format_errors_for_template()
            self.total_errors += self.errors['manifestations']['total']

        # Create all collect objects if there are no errors
        if self.total_errors == 0:
            people = self.sheets['People'].entities.people
            self.sheets['People'].entities.bulk_create(people)
            self.sheets['People'].entities.log_summary.append(f'{len(people)} CofkCollectPerson')

            locations = self.sheets['Places'].entities.locations
            self.sheets['Places'].entities.bulk_create(locations)
            self.sheets['Places'].entities.log_summary.append(f'{len(locations)} CofkCollectLocation')

            self.sheets['Work'].entities.create_all()

            inst = self.sheets['Repositories'].entities.institutions
            self.sheets['Repositories'].entities.bulk_create(inst)
            self.sheets['Repositories'].entities.log_summary.append(f'{len(inst)} CofkCollectInstitution')

            manifs = self.sheets['Manifestation'].entities.manifestations
            self.sheets['Manifestation'].entities.bulk_create(manifs)
            self.sheets['Manifestation'].entities.log_summary.append(f'{len(manifs)} CofkCollectManifestation')

            log_msg = self.sheets['Work'].entities.log_summary + self.sheets['Manifestation'].entities.log_summary\
                      + self.sheets['Repositories'].entities.log_summary
            log.info(f'{self.upload}: created ' + ', '.join(log_msg))

    def check_sheets(self):
        # Verify all required sheets are present
        difference = list(set(MANDATORY_SHEETS.keys()) - set([n for n in self.wb.sheetnames]))

        if difference:
            if len(difference) == 1:
                msg = f'Missing sheet: {difference[0].title()}'
            else:
                msg = f'Missing sheets: {", ".join(sorted([n.title() for n in difference]))}'
            log.error(msg)
            raise CofkExcelFileError(msg)
