import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-o', '--output-dir', type=str, default='.')
        parser.add_argument('-s', '--skip-url-check', action='store_true', default=False)

    def handle(self, *args, **options):
        from core import exporter
        exporter.export_all(options['output_dir'], skip_url_check=options['skip_url_check'])
