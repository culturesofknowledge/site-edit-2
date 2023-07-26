from django.urls import path
from . import views


app_name = 'uploader'

urlpatterns = [
    path('', views.UploadView.as_view(), name='upload_list'),
    path('add', views.AddUploadView.as_view(), name='upload_add'),
    path('<int:upload_id>/', views.upload_review, name='upload_review'),
    path('works', views.ColWorkSearchView.as_view(), name='upload_works')

]
