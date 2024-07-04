"""
This module contains the functions to create Excel file and object(Workbook)
for modules (e.g. work, person, location, etc.)

This module and package `export_data` is designed for web search page export.
"""
import itertools
import logging
from typing import Iterable, NoReturn, Callable

from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from cllib import data_utils
from core import constant
from core.export_data import excel_header_values, excel_serv
from core.helper import model_serv
from core.helper.view_components import HeaderValues
from core.models import CofkUnionResource
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


def fill_sheet(sheet: 'Worksheet',
               rows: Iterable[CofkUnionWork],
               header_values: HeaderValues,
               sheet_name,
               header_format=None) -> NoReturn:
    log.debug(f'start fill sheet [{sheet_name=}]')
    sheet.name = sheet_name

    # fill header
    for col_idx, col_val in enumerate(header_values.get_header_list()):
        args = [0, col_idx, col_val]
        if header_format:
            args.append(header_format)
        sheet.write(*args)

    rows = (header_values.obj_to_values(obj) for obj in rows)
    rows = map(data_utils.to_str_list_no_none, rows)
    rows = map(excel_serv.escape_xlsx_char_by_row, rows)
    for row_idx, row in enumerate(rows, start=1):
        for col_idx, col_val in enumerate(row):
            sheet.write_string(row_idx, col_idx, col_val)


def fill_work_sheet(sheet, rows, header_format=None):
    return fill_sheet(sheet, rows=rows,
                      header_values=excel_header_values.WorkExcelHeaderValues(),
                      sheet_name='Work',
                      header_format=header_format,
                      )


def fill_person_sheet(sheet, rows, header_hormat=None):
    return fill_sheet(sheet, rows=rows,
                      header_values=excel_header_values.PersonExcelHeaderValues(),
                      sheet_name='Person',
                      header_format=header_hormat,
                      )


def fill_location_sheet(sheet, rows, header_hormat=None):
    return fill_sheet(sheet, rows=rows,
                      header_values=excel_header_values.LocationExcelHeaderValues(),
                      sheet_name='Location',
                      header_format=header_hormat,
                      )


def fill_manif_sheet(sheet, rows, header_hormat=None):
    return fill_sheet(sheet, rows=rows,
                      header_values=excel_header_values.ManifExcelHeaderValues(),
                      sheet_name='Manifestation',
                      header_format=header_hormat,
                      )


def fill_inst_sheet(sheet, rows, header_hormat=None):
    return fill_sheet(sheet, rows=rows,
                      header_values=excel_header_values.InstExcelHeaderValues(),
                      sheet_name='Institution',
                      header_format=header_hormat,
                      )


def fill_resource_sheet(sheet, rows, header_hormat=None):
    return fill_sheet(sheet, rows=rows,
                      header_values=excel_header_values.ResourceExcelHeaderValues(),
                      sheet_name='Resource',
                      header_format=header_hormat,
                      )


def get_flat_resource_list(objects, get_resource_map_set_fn) -> Iterable['CofkUnionResource']:
    return itertools.chain.from_iterable((r.resource for r in get_resource_map_set_fn(w).iterator())
                                         for w in objects)


def _create_excel_by_fill_fn(fill_fn: Callable[[Workbook], NoReturn],
                             file_path: str = None):
    log.info('[Start] create excel')
    wb = Workbook(file_path)
    fill_fn(wb)
    wb.close()
    log.info(f'[Completed] create excel [{file_path=}] ')


def create_work_excel(queryable_works: Iterable[CofkUnionWork],
                      file_path: str = None) -> 'Workbook':
    queryable_works = list(queryable_works)

    def _find_manif_list():
        manif_list = itertools.chain.from_iterable(w.manif_set.iterator()
                                                   for w in queryable_works)
        return model_serv.UniqueModelPkFilter(manif_list)

    def _find_person_list():
        person_list = itertools.chain.from_iterable(w.find_persons_by_rel_type([
            constant.REL_TYPE_CREATED,
            constant.REL_TYPE_SENT,
            constant.REL_TYPE_SIGNED,
            constant.REL_TYPE_WAS_ADDRESSED_TO,
            constant.REL_TYPE_INTENDED_FOR,
            constant.REL_TYPE_MENTION,
        ]) for w in queryable_works)
        return model_serv.UniqueModelPkFilter(person_list)

    def _find_location_list():
        location_list = itertools.chain.from_iterable(w.find_locations_by_rel_type([
            constant.REL_TYPE_WAS_SENT_FROM,
            constant.REL_TYPE_WAS_SENT_TO,
        ]) for w in queryable_works)
        return model_serv.UniqueModelPkFilter(location_list)

    def _find_inst_list():
        inst_list = (manif.inst for manif in model_serv.UniqueModelPkFilter(_find_manif_list()))
        inst_list = filter(None, inst_list)
        return model_serv.UniqueModelPkFilter(inst_list)

    def _fill_fn(workbook: Workbook):
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': 'D3D3D3',
        })
        fill_work_sheet(workbook.add_worksheet(), queryable_works, header_format=header_format)
        fill_person_sheet(workbook.add_worksheet(), _find_person_list(), header_hormat=header_format)
        fill_location_sheet(workbook.add_worksheet(), _find_location_list(), header_hormat=header_format)
        fill_manif_sheet(workbook.add_worksheet(), _find_manif_list(), header_hormat=header_format)
        fill_inst_sheet(workbook.add_worksheet(), _find_inst_list(), header_hormat=header_format)

        resource_list = itertools.chain(
            get_flat_resource_list(queryable_works, lambda obj: obj.cofkworkresourcemap_set),
            get_flat_resource_list(_find_person_list(), lambda obj: obj.cofkpersonresourcemap_set),
            get_flat_resource_list(_find_location_list(), lambda obj: obj.cofklocationresourcemap_set),
            get_flat_resource_list(_find_inst_list(), lambda obj: obj.cofkinstitutionresourcemap_set),
        )
        fill_resource_sheet(workbook.add_worksheet(), resource_list, header_hormat=header_format)

    return _create_excel_by_fill_fn(_fill_fn, file_path=file_path)
