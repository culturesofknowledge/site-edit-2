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

from urllib.parse import urljoin

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

import core.views
from core.helper import media_serv

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
    path('lang/', include('core.lang_urls')),
    path('user/', include('core.user_urls')),
    path('misc/', include('core.misc_urls')),
    path('tombstone/', include('tombstone.urls')),

    path("__reload__/", include("django_browser_reload.urls")),
]

for url_path, file_path in [
    ('img', media_serv.IMG_PATH),
]:
    urlpatterns += static(urljoin(settings.MEDIA_URL, url_path), document_root=file_path)

urlpatterns += [
    path('file-download/<path:file_path>', core.views.download_file, name='file-download'),
]
