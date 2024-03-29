from core.helper import url_serv
from . import views

app_name = 'publication'

urlpatterns = []
urlpatterns.extend(
    url_serv.create_common_urls_for_section(
        init_view=views.PubInitView.as_view(),
        edit_view=views.full_form,
        delete_view=views.PubDeleteConfirmView.as_view(),
        search_view=views.PubSearchView.as_view(),
        merge_view=views.PubInitView.as_view(),
        edit_id_name='pk',
    )
)

urlpatterns.extend(url_serv.create_urls_for_quick_init(
    views.PubQuickInitView.as_view(),
    views.return_quick_init,
))
