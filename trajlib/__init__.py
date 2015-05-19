"""
This package provides various methods for integrating 3D trajectories.
"""


from . import methods
from . import nilu
from .integrator import integrate, integrate_forever


def straight_line(lat_lon, azimuth, distances):
    """
    Yields a sequence of tuples (latitude, longitude) representing a points
    going from the given start point lat_lon, in the direction azimuth for
    the given distances.

    The origin point is yielded first.

    :param lat_lon: Origin (latitude, longitude).
    :param azimuth: The direction of travel, defined as degrees CW from north.
    :param distances: A sequence of distances of travel.
    """
    yield lat_lon
    for dist in distances:
        lon, lat, _ = methods.GEOD.fwd(lat_lon[0], lat_lon[1], azimuth, dist)
        yield lat, lon
