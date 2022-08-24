from core.helper import url_utils
from . import views

app_name = 'location'
urlpatterns = []
urlpatterns.extend(
    url_utils.create_common_urls_for_section(
        init_view=views.init_form,
        edit_view=views.full_form,
        search_view=views.LocationSearchView.as_view(),
        merge_view=views.LocationMergeView.as_view(),
        edit_id_name='location_id',
    )
)
