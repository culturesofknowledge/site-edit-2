from django.urls import reverse
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
        location = self.location_name

        if self.location_synonyms:
            location += f'\n\nAlternative names: {self.location_synonyms}'

        return mark_safe(location)