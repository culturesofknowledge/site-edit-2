import datetime
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

IMG_PATH = Path(settings.MEDIA_ROOT).joinpath('img')
IMG_PATH.mkdir(parents=True, exist_ok=True)

FILE_DOWNLOAD_PATH = Path(settings.MEDIA_ROOT).joinpath('file_download')
FILE_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
IMG_URL = settings.MEDIA_URL + 'img/'


def get_img_url_by_file_path(file_path: str) -> str:
    return IMG_URL + file_path


def is_img_exists_by_url(img_url: str) -> bool:
    if not img_url:
        return False

    idx = img_url.rfind(IMG_URL)
    if idx == -1:
        return False

    file_path = img_url[idx + len(IMG_URL):]
    return IMG_PATH.joinpath(file_path).is_file()


def save_uploaded_img(file: InMemoryUploadedFile) -> str:
    file_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    file_name = f'{file_time}__{file.name}'

    file_path = IMG_PATH.joinpath(file_name)
    file_path.write_bytes(file.read())
    return file_name
