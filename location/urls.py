from core.helper import url_serv
from . import views

app_name = 'location'
urlpatterns = []
urlpatterns.extend(
    url_serv.create_common_urls_for_section(
        init_view=views.LocationInitView.as_view(),
        edit_view=views.full_form,
        delete_view=views.LocationDeleteConfirmView.as_view(),
        search_view=views.LocationSearchView.as_view(),
        merge_view=views.LocationMergeChoiceView.as_view(),
        merge_action_view=views.LocationMergeActionView.as_view(),
        merge_confirm_view=views.LocationMergeConfirmView.as_view(),
        edit_id_name='location_id',
    )
)

urlpatterns.extend(url_serv.create_urls_for_quick_init(
    views.LocationQuickInitView.as_view(),
    views.return_quick_init,
))
