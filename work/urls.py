from django.urls import path, re_path

from core.helper import url_serv
from core.views import default_view
from . import views

app_name = 'work'
urlpatterns = [
    re_path('form/corr/(?P<iwork_id>[0-9]+)?\\Z', views.CorrView.as_view(), name='corr_form'),
    re_path('form/dates/(?P<iwork_id>[0-9]+)?\\Z', views.DatesView.as_view(), name='dates_form'),
    re_path('form/places/(?P<iwork_id>[0-9]+)?\\Z', views.PlacesView.as_view(), name='places_form'),
    path('form/manif/<int:iwork_id>', views.ManifView.as_view(), name='manif_init'),
    path('form/manif/<int:iwork_id>/<str:manif_id>', views.ManifView.as_view(), name='manif_update'),
    re_path('form/resources/(?P<iwork_id>[0-9]+)?\\Z', views.ResourcesView.as_view(), name='resources_form'),
    re_path('form/details/(?P<iwork_id>[0-9]+)?\\Z', views.DetailsView.as_view(), name='details_form'),
    path('form/overview/<int:iwork_id>', views.overview_view, name='overview_form'),
]
urlpatterns.extend(
    url_serv.create_common_urls_for_section(
        init_view=views.CorrView.as_view(),
        # edit_view=views.full_form,
        search_view=views.WorkSearchView.as_view(),
        merge_view=default_view,
        edit_id_name='iwork_id',
    )
)

urlpatterns.extend(url_serv.create_urls_for_quick_init(
    views.WorkQuickInitView.as_view(),
    views.return_quick_init,
))
