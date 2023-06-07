import os
import tempfile
from typing import Dict, List

from django.test import TestCase
from openpyxl.workbook import Workbook

from uploader.constants import MANDATORY_SHEETS


class UploaderTestCase(TestCase):
    def create_excel_file(self, data: Dict[str, List[List]] = None) -> str:
        wb = Workbook()
        tf = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)

        for sheet_name in MANDATORY_SHEETS.keys():
            ws = wb.create_sheet(sheet_name)
            column_count = len(MANDATORY_SHEETS[sheet_name]['columns'])
            ws.append(MANDATORY_SHEETS[sheet_name]['columns'])
            ws.append(['-'] * column_count)

            if data and sheet_name in data:
                for row in data[sheet_name]:
                    ws.append(row)

        wb.save(tf.name)

        self.tmp_files.append(tf.name)

        return tf.name

    def setUp(self) -> None:
        self.tmp_files = []

    def tearDown(self) -> None:
        # Delete all tmp files
        for f in self.tmp_files:
            os.unlink(f)