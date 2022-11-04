from django.urls import path, re_path

from core.helper import url_utils
from login.views import example_dashboard
from . import views

app_name = 'work'
urlpatterns = [
    re_path(r'form/corr/(<int:iwork_id>)?', views.CorrView.as_view(), name='corr_form'),
    re_path(r'form/dates/(<int:iwork_id>)?', views.DatesView.as_view(), name='dates_form'),
    re_path(r'form/places/(<int:iwork_id>)?', views.PlacesView.as_view(), name='places_form'),
    re_path(r'form/manif/<int:iwork_id>', views.ManifView.as_view(), name='manif_init'),
    re_path(r'form/manif/<int:iwork_id>/<str:manif_id>', views.ManifView.as_view(), name='manif_update'),
    re_path(r'form/resources/(<int:iwork_id>)?', views.ResourcesView.as_view(), name='resources_form'),
    re_path(r'form/details/(<int:iwork_id>)?', views.DetailsView.as_view(), name='details_form'),
    path('form/overview/<int:iwork_id>', views.overview_view, name='overview_form'),
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
