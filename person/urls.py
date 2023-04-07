from core.helper import url_utils
from . import views

app_name = 'person'
urlpatterns = []
urlpatterns.extend(
    url_utils.create_common_urls_for_section(
        init_view=views.PersonInitView.as_view(),
        edit_view=views.full_form,
        delete_view=views.PersonDeleteConfirmView.as_view(),
        search_view=views.PersonSearchView.as_view(),
        merge_view=views.PersonMergeChoiceView.as_view(),
        merge_action_view=views.PersonMergeActionView.as_view(),
        merge_confirm_view=views.PersonMergeConfirmView.as_view(),
        edit_id_name='iperson_id',
    )
)

urlpatterns.extend(url_utils.create_urls_for_quick_init(
    views.PersonQuickInitView.as_view(),
    views.return_quick_init,
))
