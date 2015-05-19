"""
This module provides functions to convert to and from the ECMFW time format.

ECMWF handles time as hours from Januari 1st 1900.
"""


import datetime


ECMWF_EPOCH = datetime.datetime(1900, 1, 1)


def datetime_to_ecmwf_hours(dt):
    """
    Convert a datetime object to ECMWF time.
    :param dt: A standard datetime object.
    :return: Hours from the ECMWF epoch.
    """
    return (dt - ECMWF_EPOCH).total_seconds() / 3600.0


def ecmwf_hours_to_datetime(hours):
    """
    Convert a number representing ECMWF time. Only the integer part is used.
    :param hours: Number of hours from ECMWF epoch.
    :return: A standard datetime object.
    """
    return ECMWF_EPOCH + datetime.timedelta(hours=int(hours))  # int cast in case of numpy integer.
