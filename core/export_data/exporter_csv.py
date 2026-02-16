import csv
import logging
from pathlib import Path
from typing import Type

from core.export_data import excel_header_values
from core.helper.view_components import HeaderValues
from core.models import CofkUnionResource, CofkUnionComment, CofkUnionImage
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation
from person.models import CofkUnionPerson
from work.work_serv import DisplayableWork

log = logging.getLogger(__name__)


def export_csv_by_header_values(header_values: HeaderValues, queryset, csv_path: Path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header_values.get_header_list())
        for obj in queryset.iterator():
            writer.writerow(header_values.obj_to_values(obj))


class CommentExcelHeaderValues(HeaderValues):
    def get_header_list(self) -> list[str]:
        return [
            "Comment ID",
            "Comment",
            "UUID",
        ]

    def obj_to_values(self, obj: CofkUnionComment) -> list:
        return [
            obj.comment_id,
            obj.comment,
            obj.uuid,
        ]


class ImageExcelHeaderValues(HeaderValues):
    def get_header_list(self) -> list[str]:
        return [
            "Image ID",
            "Image Filename",
            "UUID",
        ]

    def obj_to_values(self, obj: CofkUnionImage) -> list:
        return [
            obj.image_id,
            obj.image_filename,
            obj.uuid,
        ]


def export_all_excel_style(output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    export_configs = [
        (excel_header_values.WorkExcelHeaderValues, DisplayableWork.objects.all(), 'work.csv'),
        (excel_header_values.PersonExcelHeaderValues, CofkUnionPerson.objects.all(), 'person.csv'),
        (excel_header_values.LocationExcelHeaderValues, CofkUnionLocation.objects.all(), 'location.csv'),
        (excel_header_values.InstExcelHeaderValues, CofkUnionInstitution.objects.all(), 'institution.csv'),
        (excel_header_values.ManifExcelHeaderValues, CofkUnionManifestation.objects.all(), 'manifestation.csv'),
        (excel_header_values.ResourceExcelHeaderValues, CofkUnionResource.objects.all(), 'resource.csv'),
        (CommentExcelHeaderValues, CofkUnionComment.objects.all(), 'comment.csv'),
        (ImageExcelHeaderValues, CofkUnionImage.objects.all(), 'image.csv'),
    ]

    for header_values_class, queryset, filename in export_configs:
        log.info(f'Exporting {filename}...')
        export_csv_by_header_values(header_values_class(), queryset, output_path / filename)
