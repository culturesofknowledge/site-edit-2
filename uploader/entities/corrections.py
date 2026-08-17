import logging
from typing import List

from openpyxl.cell.read_only import EmptyCell

from core.models import CofkLookupCatalogue
from uploader.constants import CORRECTION_WORK_SHEET, MAX_YEAR, MIN_YEAR
from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectWorkCorrection
from work.models import CofkUnionWork

log = logging.getLogger(__name__)

IDENTIFIER_COL = CORRECTION_WORK_SHEET['identifier']   # 'EMLO Letter ID Number'
COMMAND_COL    = CORRECTION_WORK_SHEET['command_col']  # 'Command'
COL_TO_FIELD   = CORRECTION_WORK_SHEET['columns']      # exact header -> CofkUnionWork field name


class CofkWorkCorrections(CofkEntity):
    """
    Parses a bulk work corrections spreadsheet ('Corrections' sheet, 1 header row).

    Each data row identifies an existing CofkUnionWork via 'EMLO Letter ID Number'
    and supplies one or more correction fields. Corrections are stored as a JSON dict
    {field_name: new_value} on CofkCollectWorkCorrection.

    'Original Catalogue name' expects the catalogue's name (e.g. 'Early Modern Letters
    Online'), looked up against CofkLookupCatalogue.catalogue_name. The matching
    catalogue's catalogue_code is what actually gets stored, under
    'original_catalogue_code' - CofkUnionWork.original_catalogue is a FK keyed on
    catalogue_code (see work.models), not the name, so the code is still required
    for storage even though the sheet column and lookup are name-based.
    """

    @property
    def fields(self) -> dict:
        return CORRECTION_WORK_SHEET

    def __init__(self, upload: CofkCollectUpload, sheet):
        super().__init__(upload, sheet)
        self.corrections: List[CofkCollectWorkCorrection] = []

        header = sheet.header  # list of column name strings from row 1

        for row_number, row in enumerate(sheet.worksheet.iter_rows(), start=1):
            if row_number <= sheet.header_length:
                continue

            row_by_header = {
                header[cell.column - 1]: cell.value
                for cell in row
                if not isinstance(cell, EmptyCell)
                and cell.column <= len(header)
                and cell.value not in (None, '')
            }

            if not row_by_header:
                continue

            self.row = row_number

            # --- Identify the work ---
            if IDENTIFIER_COL not in row_by_header:
                self.add_error(f'Row {row_number}: missing required column "{IDENTIFIER_COL}".')
                continue

            try:
                iwork_id = int(row_by_header[IDENTIFIER_COL])
                if iwork_id < 1:
                    raise ValueError
            except (ValueError, TypeError):
                self.add_error(
                    f'Row {row_number}: "{IDENTIFIER_COL}" value '
                    f'"{row_by_header[IDENTIFIER_COL]}" is not a valid positive integer.'
                )
                continue

            command = str(row_by_header.get(COMMAND_COL, 'UPDATE')).strip().upper()
            if command != 'UPDATE':
                self.add_error(
                    f'Row {row_number}: Command "{command}" is not supported. Only "UPDATE" is allowed.'
                )
                continue

            try:
                union_work = CofkUnionWork.objects.get(iwork_id=iwork_id)
            except CofkUnionWork.DoesNotExist:
                self.add_error(
                    f'Row {row_number}: no work found with EMLO Letter ID Number {iwork_id}.'
                )
                continue

            if iwork_id in self.ids:
                log.warning(f'Duplicate iwork_id {iwork_id} in correction sheet — skipping row {row_number}.')
                continue

            # --- Build corrections dict ---
            corrections_dict = {}
            has_error = False

            for col_header, field_name in COL_TO_FIELD.items():
                if col_header not in row_by_header:
                    continue
                raw = row_by_header[col_header]

                if field_name in CORRECTION_WORK_SHEET.get('ints', []):
                    try:
                        raw = int(raw)
                    except (ValueError, TypeError):
                        self.add_error(
                            f'Row {row_number}: "{col_header}" must be an integer (got "{raw}").'
                        )
                        has_error = True
                        break

                if field_name in CORRECTION_WORK_SHEET.get('bools', []):
                    try:
                        v = int(raw)
                        if v not in (0, 1):
                            raise ValueError
                        raw = v
                    except (ValueError, TypeError):
                        self.add_error(
                            f'Row {row_number}: "{col_header}" must be 0 or 1 (got "{raw}").'
                        )
                        has_error = True
                        break

                if field_name in CORRECTION_WORK_SHEET.get('years', []) and isinstance(raw, int):
                    if not MIN_YEAR <= raw <= MAX_YEAR:
                        self.add_error(
                            f'Row {row_number}: "{col_header}" year {raw} must be between '
                            f'{MIN_YEAR} and {MAX_YEAR}.'
                        )
                        has_error = True
                        break

                if field_name in CORRECTION_WORK_SHEET.get('months', []) and isinstance(raw, int):
                    if not 1 <= raw <= 12:
                        self.add_error(
                            f'Row {row_number}: "{col_header}" month {raw} must be between 1 and 12.'
                        )
                        has_error = True
                        break

                if field_name in CORRECTION_WORK_SHEET.get('dates', []) and isinstance(raw, int):
                    if raw > 31:
                        self.add_error(
                            f'Row {row_number}: "{col_header}" day {raw} cannot exceed 31.'
                        )
                        has_error = True
                        break

                if field_name == 'original_catalogue':
                    catalogue = CofkLookupCatalogue.objects.filter(
                        catalogue_name__iexact=str(raw).strip()
                    ).first()
                    if catalogue is None:
                        self.add_error(
                            f'Row {row_number}: catalogue "{raw}" not found by name in the catalogue lookup.'
                        )
                        has_error = True
                        break
                    # Store the catalogue_code string (used as FK value via original_catalogue_id)
                    corrections_dict['original_catalogue_code'] = catalogue.catalogue_code
                    continue

                corrections_dict[field_name] = raw

            if has_error:
                continue

            if not corrections_dict:
                log.warning(f'Row {row_number}: iwork_id {iwork_id} — no correction columns found, skipping.')
                continue

            self.ids.append(iwork_id)
            self.corrections.append(
                CofkCollectWorkCorrection(
                    upload=upload,
                    iwork_id=iwork_id,
                    union_work=union_work,
                    corrections=corrections_dict,
                    upload_status_id=1,
                )
            )

        log.info(
            f'{upload}: parsed {len(self.corrections)} corrections, '
            f'{sum(len(v) for v in self.errors.values())} errors.'
        )
