"""
This sub-module provides methods for integrating trajectories in three dimensions.

Positions are represented as tuples with the first four values being (latitude, longitude, z, time) with latitude and
longitude in degrees, while z and time are unit agnostic. Additional values may follow and will be ignored.

Velocities are represented as tuples with (u, v, w) where u and v are the eastward and northward velocities in units
of meters per time unit. The last value, w, is expected to match whatever unit z positions are given in, per time unit.

Horizontal movement is done on the WGS84 reference ellipsoid.
"""

import math
import pyproj


GEOD = pyproj.Geod(ellps='WGS84')


def move(point, uvw, dt):
    lat, lon, z, t = point[0:4]
    u, v, w = uvw
    azimuth = math.degrees(math.atan2(u, v))
    distance = math.sqrt(u*u + v*v) * dt
    new_lon, new_lat, _ = GEOD.fwd(lon, lat, azimuth, distance)
    new_lon %= 360  # Keep longitude in 0 to 360 range.
    new_lat = (new_lat + 90) % 180 - 90  # Keep latitude in -90 to 90 range.
    return (new_lat, new_lon, z + w * dt, t + dt) + point[4:]


def move_euler(point, uvw_func, dt):
    """
    Euler method of integration.
    """
    return move(point, uvw_func(point), dt)


def move_trapezoid(point, uvw_func, dt):
    """
    Trapezoid method of integration.
    """
    uvw_1 = uvw_func(point)
    first_step = move(point, uvw_1, dt)
    uvw_2 = uvw_func(first_step)
    uvw = ((uvw_1[0] + uvw_2[0]) / 2,
           (uvw_1[1] + uvw_2[1]) / 2,
           (uvw_1[2] + uvw_2[2]) / 2)
    return move(point, uvw, dt)


def move_rk4(point, uvw_func, dt):
    """
    Runge-Kutta fourth degree method of integration (RK4).
    """
    uvw_1 = uvw_func(point)
    uvw_2 = uvw_func(move(point, uvw_1, dt / 2))
    uvw_3 = uvw_func(move(point, uvw_2, dt / 2))
    uvw_4 = uvw_func(move(point, uvw_3, dt))
    uvw = ((uvw_1[0] + uvw_2[0] * 2 + uvw_3[0] * 2 + uvw_4[0]) / 6,
           (uvw_1[1] + uvw_2[1] * 2 + uvw_3[1] * 2 + uvw_4[1]) / 6,
           (uvw_1[2] + uvw_2[2] * 2 + uvw_3[2] * 2 + uvw_4[2]) / 6)
    return move(point, uvw, dt)
