from core.helper import url_serv

from . import views
from list.views import CatalogueListView

app_name = 'catalogue'

urlpatterns = url_serv.create_common_urls_for_section(
    init_view=views.update_catalogue,
    edit_view=views.update_catalogue,
    search_view=views.CatalogueSearchView.as_view(),
)