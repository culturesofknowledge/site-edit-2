import os
import tempfile


def create_new_tmp_file_path(*args, **kwargs):
    for _ in range(1000):
        file = tempfile.NamedTemporaryFile(*args, **kwargs)
        file.close()  # close to remove file
        if os.path.exists(file.name):
            continue
        else:
            return file.name
    raise FileExistsError('can\' create tmp file, file already exist')
