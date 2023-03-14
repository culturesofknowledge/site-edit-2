import datetime
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

IMG_PATH = Path(settings.MEDIA_ROOT).joinpath('img')
IMG_PATH.mkdir(parents=True, exist_ok=True)

FILE_DOWNLOAD_PATH = Path(settings.MEDIA_ROOT).joinpath('file_download')
FILE_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)


def get_img_url_by_file_path(file_path: str) -> str:
    return settings.MEDIA_URL + 'img/' + file_path


def save_uploaded_img(file: InMemoryUploadedFile) -> str:
    file_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    file_name = f'{file_time}__{file.name}'

    file_path = IMG_PATH.joinpath(file_name)
    file_path.write_bytes(file.read())
    return file_name
