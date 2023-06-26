from django.urls import path
from . import views


app_name = 'uploader'

urlpatterns = [
    path('', views.UploadView.as_view(), name='upload_form'),
    path('<int:upload_id>/', views.upload_review, name='upload_review'),

]
