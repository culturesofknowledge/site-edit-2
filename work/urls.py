from django.urls import path

from core.helper import url_utils
from login.views import example_dashboard
from . import views

app_name = 'work'
urlpatterns = [
    path(f'form/<int:iwork_id>/corr', views.CorrView.as_view(), name='corr_form'),
    path(f'form/<int:iwork_id>/dates', views.DatesView.as_view(), name='dates_form'),
    path(f'form/<int:iwork_id>/places', views.PlacesView.as_view(), name='places_form'),
    path(f'form/<int:iwork_id>/manif', views.ManifView.as_view(), name='manif_init'),
    path(f'form/<int:iwork_id>/manif/<str:manif_id>', views.ManifView.as_view(), name='manif_update'),
    path(f'form/<int:iwork_id>/resources', views.ResourcesView.as_view(), name='resources_form'),
    path(f'form/<int:iwork_id>/details', views.DetailsView.as_view(), name='details_form'),
    path(f'form/<int:iwork_id>/overview', views.overview_view, name='overview_form'),
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
