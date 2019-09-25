import time
from datetime import datetime


def get_posix_now():
    """
    Gets the current UTC timestamp
    :return: integer representation of the UTC timestamp
    """
    return get_posix(datetime.now())


def get_posix(datime_obj):
    """
    Converts a DateTime object into an integer
    :param datime_obj: DateTime object to convert
    :return: integer representation of the given DateTime object
    """
    utc = datime_obj.utctimetuple()
    t = time.mktime(utc)
    return int(t)
