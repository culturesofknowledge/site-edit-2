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

from cllib import data_utils, debug_utils
from core import constant
from core.export_data import excel_header_values, excel_serv
from core.helper import query_serv
from core.helper.view_components import HeaderValues
from core.models import CofkUnionResource
from institution.models import CofkUnionInstitution, CofkInstitutionResourceMap
from location.models import CofkUnionLocation, CofkLocationResourceMap
from manifestation.models import CofkUnionManifestation, CofkManifInstMap
from person.models import CofkUnionPerson, CofkPersonResourceMap
from work.models import CofkUnionWork, CofkWorkPersonMap, CofkWorkLocationMap, CofkWorkResourceMap

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


@debug_utils.Timer(name='create_work_excel').measure_fn
def create_work_excel(queryable_works: Iterable[CofkUnionWork],
                      file_path: str = None) -> 'Workbook':
    queryable_works = list(queryable_works)

    def _find_manif_ids(_work_ids):
        return CofkUnionManifestation.objects.filter(work_id__in=_work_ids).values_list('pk', flat=True)

    def _find_person_ids(_work_ids):
        return CofkWorkPersonMap.objects.filter(relationship_type__in=[
            constant.REL_TYPE_CREATED,
            constant.REL_TYPE_SENT,
            constant.REL_TYPE_SIGNED,
            constant.REL_TYPE_WAS_ADDRESSED_TO,
            constant.REL_TYPE_INTENDED_FOR,
            constant.REL_TYPE_MENTION,
        ], work_id__in=_work_ids).values_list('person_id', flat=True)

    def _find_location_ids(_work_ids):
        return CofkWorkLocationMap.objects.filter(relationship_type__in=[
            constant.REL_TYPE_WAS_SENT_FROM,
            constant.REL_TYPE_WAS_SENT_TO,
        ], work_id__in=_work_ids).values_list('location_id', flat=True)

    def _find_inst_ids(_manif_ids):
        return CofkManifInstMap.objects.filter(manif_id__in=_manif_ids).values_list('inst_id', flat=True)

    def _find_resource_ids_my_recref_class(recref_class, _ids, query_field, output_field='resource'):
        def _batch_fn(_sub_ids):
            return (recref_class.objects
                    .filter(**{query_field: _ids})
                    .values_list(output_field, flat=True))

        resource_ids = query_serv.find_ids_by_batch_ids_fn(_batch_fn, _ids)
        return query_serv.find_by_batch_ids_fn(lambda _ids: CofkUnionResource.objects.filter(pk__in=_ids), resource_ids)

    work_ids = [w.pk for w in queryable_works]
    person_ids = query_serv.find_ids_by_batch_ids_fn(_find_person_ids, work_ids)
    manif_ids = query_serv.find_ids_by_batch_ids_fn(_find_manif_ids, work_ids)
    location_ids = query_serv.find_ids_by_batch_ids_fn(_find_location_ids, work_ids)
    inst_ids = query_serv.find_ids_by_batch_ids_fn(_find_inst_ids, manif_ids)

    def _find_records_by_class(model_class, ids, prefetch_relateds=None, select_relateds=None):
        def query_fn(_ids):
            q = model_class.objects.filter(pk__in=_ids)
            if prefetch_relateds:
                q = q.prefetch_related(*prefetch_relateds)
            if select_relateds:
                q = q.select_related(*select_relateds)
            return q

        return query_serv.find_by_batch_ids_fn(query_fn, ids)

    def _fill_fn(workbook: Workbook):
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': 'D3D3D3',
        })
        fill_work_sheet(workbook.add_worksheet(), queryable_works, header_format=header_format)
        fill_person_sheet(workbook.add_worksheet(),
                          _find_records_by_class(CofkUnionPerson, person_ids),
                          header_hormat=header_format)
        fill_location_sheet(workbook.add_worksheet(),
                            _find_records_by_class(CofkUnionLocation, location_ids),
                            header_hormat=header_format)
        fill_manif_sheet(workbook.add_worksheet(),
                         _find_records_by_class(
                             CofkUnionManifestation, manif_ids,
                             prefetch_relateds=['comments'],
                             select_relateds=['work']),
                         header_hormat=header_format)
        fill_inst_sheet(workbook.add_worksheet(),
                        _find_records_by_class(CofkUnionInstitution, inst_ids),
                        header_hormat=header_format)

        resource_list = itertools.chain(
            _find_resource_ids_my_recref_class(CofkWorkResourceMap, work_ids, 'work_id__in'),
            _find_resource_ids_my_recref_class(CofkPersonResourceMap, person_ids, 'person_id__in'),
            _find_resource_ids_my_recref_class(CofkLocationResourceMap, location_ids, 'location_id__in'),
            _find_resource_ids_my_recref_class(CofkInstitutionResourceMap, inst_ids, 'institution_id__in'),
        )
        fill_resource_sheet(workbook.add_worksheet(), resource_list, header_hormat=header_format)

    return _create_excel_by_fill_fn(_fill_fn, file_path=file_path)
