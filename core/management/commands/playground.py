from django.conf import settings
from django.core.management import BaseCommand

from core.models import CofkUnionResource, CofkUnionComment
from location import fixtures
from location.models import CofkUnionLocation


class Command(BaseCommand):
    help = 'playground for try some python code'

    def handle(self, *args, **options):
        main3()


def main1():
    print('yyyyyy')
    res: CofkUnionResource = CofkUnionResource(
        # resource_id = models.AutoField(primary_key=True)
        resource_name='resource_name val',
        resource_details='resource_details val',
        resource_url='resource_url val',
        # creation_timestamp = models.DateTimeField(blank=True, null=True)
        creation_user='creation_user val',
        # change_timestamp = models.DateTimeField(blank=True, null=True)
        change_user='change_user val',
        # uuid = models.UUIDField(blank=True, null=True)
    )
    res.save()

    loc: CofkUnionLocation = CofkUnionLocation.objects.first()
    l = list(loc.resources.iterator())
    print(l)
    loc.resources.add(l[0])
    # loc.resources.add(res)
    # loc.save()

    loc.refresh_from_db()

    print(list(loc.resources.iterator()))
    # x = loc.resources.a
    # print(x)

    # coll_location: CofkCollectLocation = CofkCollectLocation.objects.first()
    # a = coll_location.resources
    # print(coll_location)
    # print(a)


def main2():
    loc_a = fixtures.create_location_a()
    print(loc_a.location_id)
    loc_a.save()
    print(loc_a.location_id)



def main3():

    print(settings.MEDIA_ROOT)

    c = CofkUnionComment()
    c.update_current_user_timestamp('aaa')
    print(c.__dict__)