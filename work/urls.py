from core.helper import url_utils
from login.views import example_dashboard
from . import views

app_name = 'work'
urlpatterns = []
urlpatterns.extend(
    url_utils.create_common_urls_for_section(
        init_view=views.init_form,
        edit_view=views.full_form,
        search_view=views.WorkSearchView.as_view(),
        merge_view=example_dashboard,
        edit_id_name='iwork_id',
    )
)

urlpatterns.extend(url_utils.create_urls_for_quick_init(
    # KTODO
    example_dashboard,
    views.full_form,
    # views.PersonQuickInitView.as_view(),
    # views.return_quick_init,
))
