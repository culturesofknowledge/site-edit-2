#!/usr/bin/env python
"""
Export works (letters) to a CSV file, using the same columns as the
"export" feature of the work search page.

The script is meant to be run on the server, from the project root::

    python devscript/export_works_csv.py --list
    python devscript/export_works_csv.py -q bad_calendar -o works.csv

Adding a new query for future needs only requires adding one entry to
``QUERIES`` below, e.g.::

    'unknown_calendar': Query(
        description='Works without any calendar marked',
        condition=Q(original_calendar=''),
    ),

Ad-hoc queries can also be given on the command line without editing the
script, e.g.::

    python devscript/export_works_csv.py -f original_calendar__in=g,J
    python devscript/export_works_csv.py -f date_of_work_std__startswith=1612
"""
import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import django
from django.db.models import Q

log = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS = 'siteedit2.settings.local_dev'


@dataclass
class Query:
    """ A named, reusable query definition """
    description: str
    condition: Q
    order_by: list[str] = field(default_factory=lambda: ['iwork_id'])


QUERIES: dict[str, Query] = {
    'bad_calendar': Query(
        description="Works with a lower case 'g' or a single 'J' calendar marked in the data",
        condition=Q(original_calendar__in=['g', 'J']),
    ),
    'non_standard_calendar': Query(
        description='Works with a calendar value outside the valid list '
                    "('', G, JJ, JM, O)",
        condition=~Q(original_calendar__in=['', 'G', 'JJ', 'JM', 'O']),
    ),
    'all': Query(
        description='All works',
        condition=Q(),
    ),
}

FORMATS = ('search', 'excel')

# Extra columns prepended to the export, mapped to an attribute of the work.
# The application's export only contains "EMLO Letter ID Number" (iwork_id),
# so the internal primary key and the queried calendar values are added here,
# allowing the exported records to be confirmed against the query.
EXTRA_COLUMNS: dict[str, str] = {
    'Work ID': 'work_id',
    'Original Calendar': 'original_calendar',
    'Original Calendar (decoded)': 'original_calendar_decoded',
    'Manifestation Creation Calendar': 'manif_creation_calendars',
    'Manifestation Receipt Calendar': 'manif_receipt_calendars',
}


def _extra_column_value(obj, attr):
    """ Resolve an extra column value, with a few computed values on top of plain fields """
    if attr == 'original_calendar_decoded':
        from core.helper import date_serv
        return date_serv.decode_calendar(obj.original_calendar)
    if attr in ('manif_creation_calendars', 'manif_receipt_calendars'):
        manif_attr = ('manifestation_creation_calendar' if attr == 'manif_creation_calendars'
                      else 'manifestation_receipt_calendar')
        return ' ~ '.join(str(getattr(m, manif_attr) or '') for m in obj.manif_set.all())
    return getattr(obj, attr, None)


def setup_django(settings_module: str):
    sys.path.insert(0, str(PROJECT_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    django.setup()


def parse_filter(raw_filter: str) -> Q:
    """
    Convert ``field__lookup=value`` into a Q object.
    Values containing ',' are turned into a list (useful for ``__in``).
    """
    if '=' not in raw_filter:
        raise ValueError(f'Invalid filter, expected field=value : {raw_filter!r}')
    key, value = raw_filter.split('=', 1)
    if ',' in value:
        value = value.split(',')
    return Q(**{key.strip(): value})


def create_queryset(query: Query, extra_filters: list[str], limit: int | None):
    from work.work_serv import DisplayableWork

    condition = query.condition
    for raw_filter in extra_filters:
        condition &= parse_filter(raw_filter)

    queryset = DisplayableWork.objects.filter(condition)
    if query.order_by:
        queryset = queryset.order_by(*query.order_by)
    if limit:
        queryset = queryset[:limit]
    return queryset


def create_header_values(export_format: str, extra_columns: bool = True):
    if export_format == 'excel':
        from core.export_data.excel_header_values import WorkExcelHeaderValues
        header_values = WorkExcelHeaderValues()
    else:
        from work.views import WorkCsvHeaderValues
        header_values = WorkCsvHeaderValues()

    if extra_columns:
        header_values = ExtraColumnsHeaderValues(header_values, EXTRA_COLUMNS)
    return header_values


class ExtraColumnsHeaderValues:
    """ Wraps a HeaderValues and prepends extra columns taken from the work object """

    def __init__(self, header_values, extra_columns: dict[str, str]):
        self.header_values = header_values
        self.extra_columns = extra_columns

    def get_header_list(self) -> list[str]:
        return list(self.extra_columns) + list(self.header_values.get_header_list())

    def obj_to_values(self, obj) -> list:
        extra_values = [_extra_column_value(obj, attr) for attr in self.extra_columns.values()]
        return extra_values + list(self.header_values.obj_to_values(obj))


def export(query_name: str, output_path: Path, export_format: str,
           extra_filters: list[str], limit: int | None,
           extra_columns: bool = True) -> int:
    from core.helper.view_components import DownloadCsvHandler

    query = QUERIES[query_name]
    queryset = create_queryset(query, extra_filters, limit)
    record_count = queryset.count() if limit is None else len(queryset)

    handler = DownloadCsvHandler(create_header_values(export_format, extra_columns))
    handler.create_csv_file(queryset.iterator(), output_path)
    return record_count


def print_queries():
    print('Available queries:')
    for name, query in QUERIES.items():
        print(f'  {name:<22} {query.description}')


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-q', '--query', default='bad_calendar', choices=sorted(QUERIES),
                        help='Name of the predefined query (default: bad_calendar)')
    parser.add_argument('-o', '--output', default=None,
                        help='Output CSV file (default: <query>_works.csv)')
    parser.add_argument('-t', '--format', default='search', choices=FORMATS,
                        help="Column set: 'search' (work search page export, default) "
                             "or 'excel' (excel style export)")
    parser.add_argument('-f', '--filter', action='append', default=[], metavar='FIELD=VALUE',
                        help='Extra ORM filter, can be repeated, '
                             'e.g. -f original_calendar__in=g,J')
    parser.add_argument('-l', '--limit', type=int, default=None,
                        help='Export at most this number of works (useful for testing)')
    parser.add_argument('--no-extra-columns', action='store_true',
                        help='Do not prepend the extra columns '
                             f'({", ".join(EXTRA_COLUMNS)}) to the export')
    parser.add_argument('--list', action='store_true',
                        help='List the predefined queries and exit')
    parser.add_argument('-s', '--settings', default=os.environ.get('DJANGO_SETTINGS_MODULE',
                                                                   DEFAULT_SETTINGS),
                        help=f'Django settings module (default: {DEFAULT_SETTINGS})')
    return parser


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    args = create_arg_parser().parse_args()

    if args.list:
        print_queries()
        return

    setup_django(args.settings)

    output_path = Path(args.output or f'{args.query}_works.csv')
    record_count = export(args.query, output_path, args.format, args.filter, args.limit,
                          extra_columns=not args.no_extra_columns)
    log.info(f'Exported {record_count} work(s) to {output_path}')


if __name__ == '__main__':
    main()
