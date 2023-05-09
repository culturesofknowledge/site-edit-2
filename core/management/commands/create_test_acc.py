from argparse import ArgumentParser

from django.core.management import BaseCommand

from login.models import CofkUser


class Command(BaseCommand):
    help = 'Copy / move data from selected DB to project db '

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-u', '--user')
        parser.add_argument('-p', '--password')
        parser.add_argument('-e', '--email')
        parser.add_argument('-s', '--superuser', action='store_true', default=False)

    def handle(self, *args, **options):
        user = CofkUser()
        user.username = options['user']
        user.set_password(options['password'])
        if email := options.get('email'):
            user.email = email
        if options['superuser']:
            user.is_superuser = True
            user.is_staff = True
        user.save()
        print(f'User created: {user}')
