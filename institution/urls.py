from core.helper import url_utils
from . import views

app_name = 'institution'

urlpatterns = []
urlpatterns.extend(
    url_utils.create_common_urls_for_section(
        init_view=views.InstInitView.as_view(),
        edit_view=views.full_form,
        search_view=views.InstSearchView.as_view(),
        merge_view=views.InstMergeChoiceView.as_view(),
        merge_action_view=views.InstMergeActionView.as_view(),
        merge_confirm_view=views.InstMergeConfirmView.as_view(),
        edit_id_name='pk',
    )
)
urlpatterns.extend(url_utils.create_urls_for_quick_init(
    views.InstQuickInitView.as_view(),
    views.return_quick_init,
))
