from location.models import CofkUnionLocation


def get_recref_display_name(location: CofkUnionLocation):
    return location and location.location_name


def get_recref_target_id(location: CofkUnionLocation):
    return location and location.location_id
