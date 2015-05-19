"""
This module provides some help with using projections.
"""


import pyproj

Identity = lambda lon, lat: (lon, lat)
Mercator = pyproj.Proj(proj='merc', ellps='WGS84')


def get_stereographic(lat, lon, k=1):
    """
    Return a stereographic projection centered on the given latitude and longitude.
    :param lat: The center latitude.
    :param lon: The center longitude.
    :param k: The scaling factor in the projection center. Defaults to one.
    :return: A stereographic projection with the given parameters.
    """
    return pyproj.Proj(proj='sterea', ellps='WGS84', lat_0=lat, lon_0=lon, k_0=k)
