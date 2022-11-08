from django.urls import reverse

from location.models import CofkUnionLocation


def get_recref_display_name(location: CofkUnionLocation):
    return location and location.location_name


def get_recref_target_id(location: CofkUnionLocation):
    return location and location.location_id


def get_form_url(location_id):
    return reverse('location:full_form', args=[location_id])