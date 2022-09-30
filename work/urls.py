from core.helper import url_utils
from login.views import example_dashboard
from . import views

app_name = 'work'
urlpatterns = []
urlpatterns.extend(
    url_utils.create_common_urls_for_section(
        init_view=views.WorkInitView.as_view(),
        edit_view=example_dashboard,
        search_view=example_dashboard,
        merge_view=example_dashboard,
        edit_id_name='iwork_id',
    )
)

# urlpatterns.extend(url_utils.create_urls_for_quick_init(
#     views.PersonQuickInitView.as_view(),
#     views.return_quick_init,
# ))
