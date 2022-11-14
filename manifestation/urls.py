from django.urls import path

from . import views

app_name = 'manif'
urlpatterns = [
    path('search', views.ManifSearchView.as_view(), name='search'),
    path('', views.ManifSearchView.as_view(), name='home'),
    path('return_quick_init/<pk>', views.return_quick_init, name='return_quick_init'),
]
# urlpatterns.extend(
#     url_utils.create_common_urls_for_section(
#         init_view=views.PersonInitView.as_view(),
#         edit_view=views.full_form,
#         search_view=views.PersonSearchView.as_view(),
#         merge_view=views.PersonInitView.as_view(),
#         edit_id_name='iperson_id',
#     )
# )
#
# urlpatterns.extend(url_utils.create_urls_for_quick_init(
#     views.PersonQuickInitView.as_view(),
#     views.return_quick_init,
# ))
