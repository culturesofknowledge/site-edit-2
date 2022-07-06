from django.core.management import BaseCommand

from location.models import CofkCollectLocation


class Command(BaseCommand):
    help = 'playground for try some python code'

    def handle(self, *args, **options):
        print('yyyyyy')

        coll_location: CofkCollectLocation = CofkCollectLocation.objects.first()
        a = coll_location.resources
        print(coll_location)
        print(a)

        self.stdout.write('xxxxxxxxx')
