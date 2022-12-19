from django.core.management import BaseCommand

from core.models import Iso639LanguageCode
import pycountry


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not Iso639LanguageCode.objects.exists():
            languages = []
            for l in pycountry.languages:
                languages.append(Iso639LanguageCode(language_name=l.name,
                                                    code_639_3=l.alpha_3))

            Iso639LanguageCode.objects.bulk_create(languages)

