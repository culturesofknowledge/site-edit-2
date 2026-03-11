from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import redirect

from core.helper import media_serv
from login.views import dashboard

default_view = dashboard


def download_file(request, file_path):
    real_file_path = media_serv.FILE_DOWNLOAD_PATH.joinpath(file_path).resolve()
    if not real_file_path.as_posix().startswith(media_serv.FILE_DOWNLOAD_PATH.as_posix()):
        raise ValueError('Invalid path')

    response = FileResponse(real_file_path.open('rb'),
                            as_attachment=True,
                            filename=real_file_path.name)
    response['Content-Type'] = 'application/force-download'
    response['Content-Disposition'] = f'attachment; filename={real_file_path.name}'
    return response


def permission_denied_to_dashboard(request, exception=None):
    messages.error(request, 'To make this addition, please contact the supervisor editor.')
    return redirect(request.path if request.path else 'login:dashboard')
