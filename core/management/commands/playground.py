import logging

from django.conf import settings
from django.core.management import BaseCommand

from core.helper import email_utils, model_utils
from core.models import CofkUnionResource, CofkUnionComment
from location import fixtures
from location.models import CofkUnionLocation

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'playground for try some python code'

    def handle(self, *args, **options):
        main5()


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


def main4():
    email_utils.send_email('philip.k@cottagelabs.com', 'testtingingi', 'yoooooooo')
    # resp = requests.post(
    #     "https://api.mailgun.net/v3/sandbox04d746d0f42d4ecfbe5d976c15220b96.mailgun.org/messages",
    #     auth=("api", "81d5c16d440c1a7ca3e90d5716711c7f-c76388c3-a5f07d21"),
    #     data={"from": "Mailgun Sandbox <postmaster@sandbox04d746d0f42d4ecfbe5d976c15220b96.mailgun.org>",
    #           "to": "Philip <philip.k@cottagelabs.com>",
    #           "subject": "Hello Philip",
    #           "text": "Congratulations Philip, you just sent an email with Mailgun!  You are truly awesome!"})
    # print(resp)

    # You can see a record of this email in your logs: https://app.mailgun.com/app/logs.

    # You can send up to 300 emails/day from this sandbox server.
    # Next, you should add your own domain so you can send 10000 emails/month for free.


def main5():
    result = model_utils.next_seq_safe('xxkks')
    print(result)
