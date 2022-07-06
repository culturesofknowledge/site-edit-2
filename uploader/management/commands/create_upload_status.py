from django.core.management import BaseCommand

from uploader.models import CofkCollectStatus


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not CofkCollectStatus.objects.exists():
            statuses = [CofkCollectStatus(status_id=1, status_desc="Awaiting review"),
                        CofkCollectStatus(status_id=2, status_desc="Partly reviewed"),
                        CofkCollectStatus(status_id=3, status_desc="Review complete", editable=0),
                        CofkCollectStatus(status_id=4, status_desc="Accepted and saved into main database", editable=0),
                        CofkCollectStatus(status_id=5, status_desc="Rejected", editable=0)]

            CofkCollectStatus.objects.bulk_create(statuses)
