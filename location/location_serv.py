import re

from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from location.models import CofkUnionLocation


def get_recref_display_name(location: CofkUnionLocation):
    return location and location.location_name


def get_recref_target_id(location: CofkUnionLocation):
    return location and location.location_id


def get_form_url(location_id):
    return reverse('location:full_form', args=[location_id])

class DisplayableLocation(CofkUnionLocation):
    """
    Wrapper for display location
    """

    class Meta:
        proxy = True


    def display_location(self) -> str:
        location = escape(self.location_name)

        if self.location_synonyms:
            items = re.split(r'[;\r\n]+', str(self.location_synonyms))
            items = [i.strip() for i in items if i and i.strip()]
            if items:
                synonyms_str = '\n'.join(escape(i) for i in items)
                location += f'\n<div class="alt_names_container"><span class="alt_names_title">Alternative names:</span>\n{synonyms_str}</div>'

        return mark_safe(location)
