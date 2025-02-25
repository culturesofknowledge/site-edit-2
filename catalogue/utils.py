from core import constant
from core.models import CofkLookupCatalogue


def get_user_catalogues(request):
    """
    Fetch catalogues based on the user's group.

    :param request: HttpRequest object containing user information.
    :return: QuerySet of catalogues.
    """
    # Check if the user belongs to 'editor' or 'supervisor' groups
    user_in_privileged_group = request.user.groups.filter(name__in=[constant.ROLE_EDITOR, constant.ROLE_SUPER]).exists()

    # Query based on the group check
    if user_in_privileged_group:
        # User is in 'editor' or 'supervisor', fetch all catalogues
        catalogues = CofkLookupCatalogue.objects.all().order_by('catalogue_name')
    else:
        # Fetch catalogues owned by the user only
        catalogues = CofkLookupCatalogue.objects.filter(owner=request.user).order_by('catalogue_name')

    return catalogues