from core.helper import url_utils
from . import views

app_name = 'publication'

urlpatterns = []
urlpatterns.extend(
    url_utils.create_common_urls_for_section(
        init_view=views.PubInitView.as_view(),
        edit_view=views.full_form,
        search_view=views.PubSearchView.as_view(),
        merge_view=views.PubInitView.as_view(),
        edit_id_name='pk',
    )
)

urlpatterns.extend(url_utils.create_urls_for_quick_init(
    views.PubQuickInitView.as_view(),
    views.return_quick_init,
))
