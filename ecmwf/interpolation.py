"""
This module provides interpolation methods for when accessing data. This is used by the
Variable class, which uses interpolate_lerp by default.

An interpolation function shall take two positional arguments: a target value and a sequence
of sorted values which are available. It shall return a sequence of tuples (index, factor)
which may be used to construct an interpolated value.
"""


from bisect import bisect


def interpolate_closest(target, values):
    if target < values[0] or target > values[-1]:
        raise ValueError('Target ' + str(target) + ' outside range ' + str(values[0]) + ', ' + str(values[-1]) + '.')
    upper_index = bisect(values, target)  # Guaranteed to be larger than zero.
    if upper_index == len(values):
        return (upper_index - 1, 1),
    elif (values[upper_index] - target) < (target - values[upper_index - 1]):
        return (upper_index, 1),
    else:
        return (upper_index - 1, 1),


def interpolate_lerp(target, values):
    if target < values[0] or target > values[-1]:
        raise ValueError('Target ' + str(target) + ' outside range ' + str(values[0]) + ', ' + str(values[-1]) + '.')
    upper_index = bisect(values, target)  # Guaranteed to be larger than zero.
    if upper_index == len(values):
        upper_index -= 1
    lower_index = upper_index - 1
    lerp_factor = (target - values[lower_index]) / (values[upper_index] - values[lower_index])
    return (upper_index, lerp_factor), (lower_index, 1 - lerp_factor)
