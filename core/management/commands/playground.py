from django.core.management import BaseCommand

from location import fixtures
from location.models import CofkCollectLocation


class Command(BaseCommand):
    help = 'playground for try some python code'

    def handle(self, *args, **options):
        main1()


def main1():
    print('yyyyyy')

    # coll_location: CofkCollectLocation = CofkCollectLocation.objects.first()
    # a = coll_location.resources
    # print(coll_location)
    # print(a)



def main2():
    loc_a = fixtures.create_location_a()
    print(loc_a.location_id)
    loc_a.save()
    print(loc_a.location_id)
