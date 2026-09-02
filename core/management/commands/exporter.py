import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-o', '--output-dir', type=str, default='.')
        parser.add_argument('-s', '--skip-url-check', action='store_true', default=False)
        parser.add_argument('-t', '--type', type=str, default='flat', choices=['flat', 'excel'],
                            help='Type of export: flat (default) or excel-style CSV')
        parser.add_argument('-m', '--module', type=str, default=None,
                            help='Export only a specific module, e.g. work, person, location, '
                                 'manifestation, institution, comment, image, resource, '
                                 'relationship_type, relationship')

    def handle(self, *args, **options):
        if options['type'] == 'excel':
            from core.export_data import exporter_csv
            exporter_csv.export_all_excel_style(options['output_dir'])
        else:
            from core import exporter
            exporter.export_all(options['output_dir'], skip_url_check=options['skip_url_check'],
                                module=options['module'])
