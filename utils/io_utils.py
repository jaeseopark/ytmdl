import os


def safe_open(path, *args, **kwargs):
    dir_path = os.path.split(path)[0]
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    assert os.path.isdir(dir_path)

    return open(path, *args, **kwargs)
