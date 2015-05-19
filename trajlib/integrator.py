"""
This module provides methods for integrating trajectories, given a starting
point (latitude, longitude, z, time), a function
returning 3D velocities when given a point, a time step and optionally an
integration method.

See the methods module in this package.
"""


from .methods import move_euler


def integrate_forever(start_point, uvw_func, dt, method=move_euler):
    """
    Yields integrated points forever.
    :param start_point: Starting point of integration. Yielded first.
    :param uvw_func: Function returning a 3-tuple of velocities when given a point.
    :param dt: The time step.
    :param method: The integration method. Default to Euler.
    """
    point = start_point
    yield point
    while True:
        point = method(point, uvw_func, dt)
        yield point


def integrate(start_point, uvw_func, dt, duration, method=move_euler):
    """
    Yields integrated points for the specified duration.
    :param start_point: Starting point of integration. Yielded first.
    :param uvw_func: Function returning a 3-tuple of velocities when given a point.
    :param dt: The time step.
    :param duration: The duration for which to integrate.
    :param method: The integration method. Default to Euler.
    """
    steps = int(duration // abs(dt))
    integration = integrate_forever(start_point, uvw_func, dt, method=method)
    yield next(integration)
    for step in range(steps):
        yield next(integration)
    integration.close()
