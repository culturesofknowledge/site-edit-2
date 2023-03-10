"""siteedit2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from urllib.parse import urljoin

urlpatterns = [
    path('', RedirectView.as_view(url='/login/dashboard')),
    path('login/', include('login.urls')),
    path('admin/', admin.site.urls),
    path('repositories/', include('institution.urls')),
    path('location/', include('location.urls')),
    path('person/', include('person.urls')),
    path('publication/', include('publication.urls')),
    path('upload/', include('uploader.urls')),
    path('manif/', include('manifestation.urls')),
    path('work/', include('work.urls')),
    path('audit/', include('audit.urls')),
    path('list/', include('list.urls')),
]

urlpatterns += static(urljoin(settings.MEDIA_URL, 'img'),
                      document_root=os.path.join(settings.MEDIA_ROOT, 'img'))

urlpatterns += static(urljoin(settings.MEDIA_URL, 'export_data'),
                      document_root=settings.MEDIA_EXPORT_PATH)
