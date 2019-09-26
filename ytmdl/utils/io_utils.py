import os


def makedirs_auto(path):
    if not os.path.exists(path):
        os.makedirs(path)
    assert os.path.isdir(path)


def safe_open(path, *args, **kwargs):
    dir_path = os.path.split(path)[0]
    makedirs_auto(dir_path)
    return open(path, *args, **kwargs)
