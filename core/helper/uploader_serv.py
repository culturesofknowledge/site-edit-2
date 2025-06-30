import logging
import os
import time
from pathlib import Path
from zipfile import BadZipFile

from django.conf import settings
from django.core.files.storage import default_storage

from cllib_django import email_utils
from django.urls import reverse

from uploader.models import CofkCollectUpload
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.validation import CofkExcelFileError

log = logging.getLogger(__name__)

def file_path_and_size(upload: CofkCollectUpload) -> tuple[str, int]:
    """
    Returns the file path and size in kilobytes for the given upload.
    Raises FileNotFoundError if the file does not exist.
    """
    file_path = Path(settings.MEDIA_ROOT).joinpath(upload.upload_file.name).as_posix()
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    size = os.path.getsize(file_path) >> 10  # Convert bytes to kilobytes
    return file_path, size


def handle_upload(upload: CofkCollectUpload, email_results: bool = False, file_name: str = None) -> dict:
    start = time.time()
    report = {}
    elapsed = None

    try:
        file = default_storage.open(upload.upload_file.name, 'rb')
    except OSError as oe:
        report['total_errors'] = 1
        report['errors'] = {'file': {'total': 1, 'error': [oe]}}
        log.error(report['errors'])
        return report
    except Exception as e:
        report['total_errors'] = 1
        report['errors'] = 'Indeterminate error.'
        log.error(e)
        return report

    log.info(f'User: {upload.upload_username} uploaded file: "{file}" ({upload})')

    try:
        file_path, size = file_path_and_size(upload)
    except FileNotFoundError as fnfe:
        report['total_errors'] = 1
        report['errors'] = {'file': {'total': 1, 'error': [str(fnfe)]}}
        log.error(fnfe)
        return report

    cuef = None
    report = {
        'file': upload.upload_file.name,
        'time': upload.upload_timestamp,
        'size': size,
        'upload_id': upload.upload_id, }

    try:
        cuef = CofkUploadExcelFile(upload, file)

        elapsed = round(time.time() - start)

        if not elapsed:
            elapsed = '1 second'
        else:
            elapsed = f'{elapsed + 1} seconds'

        report['elapsed'] = elapsed

    except CofkExcelFileError as cmce:
        errors = [str(cmce)]
        report['total_errors'] = len(errors)
        report['errors'] = {'file': {'total': len(errors), 'error': errors}}
        log.error(cmce.msg)
    except (FileNotFoundError, BadZipFile, OSError) as e:
        report['total_errors'] = 1
        report['errors'] = {'file': {'total': 1, 'error': ['Could not read the file.']}}
        log.error(e)
    except ValueError as ve:
        report['total_errors'] = 1
        report['errors'] = {'file': {'total': 1, 'error': [ve]}}
        log.error(ve)
        log.exception(ve)
    except Exception as e:
        report['total_errors'] = 1
        report['errors'] = 'Indeterminate error.'
        log.error(e)
        log.exception(e)

    if cuef and cuef.errors:
        log.error(f'Deleting upload {upload}')
        upload.delete()
        # TODO delete uploaded file
        report['errors'] = cuef.errors
        report['total_errors'] = cuef.total_errors
    elif 'total_errors' in report:
        log.error(f'Deleting upload {upload}')
        upload.delete()
    else:
        upload.save()

    if email_results:
        upload_time = upload.upload_timestamp.strftime('%m/%d/%Y %H:%M:%S').split(' ')
        content = f'The file "{file_name}" you uploaded on {upload_time[0]} at {upload_time[1]} has been processed.\n'

        if elapsed:
            content += f'It took {elapsed} seconds to process.\n'

        if 'total_errors' in report:
            error_count = report['total_errors']
            content += f'\nThere were {error_count} errors.\n'

            if isinstance(report['errors'], str):
                # Indeterminate error
                content += f'\n{report["errors"]}\n'
            else:
                for sheet in report['errors']:
                    sheet_errors = report['errors'][sheet]['total']
                    content += f'\n{sheet} sheet had {sheet_errors} errors\n'

                    if 'errors' in report['errors'][sheet]:
                        for row in report['errors'][sheet]['errors']:
                            row_number = row['row']
                            content += f'\tRow {row_number}:\n'

                            for error in row['errors']:
                                content += f'\t\t— {error}\n'
        else:
            url = settings.UPLOAD_ROOT_URL + reverse('uploader:upload_review', args=[report["upload_id"]])
            content += f'\nYou can review the upload here: {url}'

        try:
            email_utils.send_email(upload.uploader_email,
                                   subject='EMLO Uploader Result',
                                   content=content)
        except Exception as e:
            log.error('Sending email failed')
            log.exception(e)

    return report
