from django.urls import path

from core.helper import url_utils
from login.views import example_dashboard
from . import views

app_name = 'work'
urlpatterns = [
    path(f'form/<int:iwork_id>/corr', views.CorrView.as_view(), name='corr_form'),
]
urlpatterns.extend(
    url_utils.create_common_urls_for_section(
        init_view=views.CorrView.as_view(),
        # edit_view=views.full_form,
        search_view=views.WorkSearchView.as_view(),
        merge_view=example_dashboard,
        edit_id_name='iwork_id',
    )
)

urlpatterns.extend(url_utils.create_urls_for_quick_init(
    views.WorkQuickInitView.as_view(),
    views.return_quick_init,
))
