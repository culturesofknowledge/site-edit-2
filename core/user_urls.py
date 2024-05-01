from core import user_views
from core.helper import url_serv

app_name = 'user'


urlpatterns = url_serv.create_common_urls_for_section(
    init_view=user_views.full_form,
    edit_view=user_views.full_form,
    search_view=user_views.UserSearchView.as_view(),
)
