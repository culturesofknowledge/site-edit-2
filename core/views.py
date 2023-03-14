from django.http import FileResponse

from core.services import media_service


def download_file(request, file_path):
    real_file_path = media_service.FILE_DOWNLOAD_PATH.joinpath(file_path).resolve()
    if not real_file_path.as_posix().startswith(media_service.FILE_DOWNLOAD_PATH.as_posix()):
        raise ValueError('Invalid path')

    response = FileResponse(real_file_path.open('rb'),
                            as_attachment=True,
                            filename=real_file_path.name)
    response['Content-Type'] = 'application/force-download'
    response['Content-Disposition'] = f'attachment; filename={real_file_path.name}'
    return response
