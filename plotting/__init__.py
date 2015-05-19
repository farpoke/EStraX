"""
This package provides some basic helpers for plotting projected data using pyplot.
"""


import matplotlib.pyplot as pyplot
from . import projections


def in_bounding_box(points, bounding_box):
    """
    Returns true if any of the points are inside the given bounding box.

    :param points: A sequence of (x, y) points.
    :param bounding_box: A bounding box in pyplot style, i.e. a tuple (min_x, max_x, min_y, max_y).
    :return: Whether any of the points are inside the bounding box.
    """
    return any(bounding_box[0] < x < bounding_box[1] and
               bounding_box[2] < y < bounding_box[3] for x, y in points)


def plot_projected_line(lats=None, lons=None, latlons=None,
                        projection=projections.Identity, scale=1, bounding_box=None,
                        **kwargs):
    """
    Plot a projected line using pyplot. Either the keyword parameters lats and lons
    should be provided, or latlons should be provided. If all three are provided then
    latlons takes precedence.

    :param lats: A sequence of latitudes to be plotted, or None (default).
    :param lons: A sequence of longitudes to be plotted, or None (default).
    :param latlons: A sequence of tuples (latitude, longitude) to be plotted or None (default).
    :param projection: A projection to use when plotting. Defaults to the Identity projection.
    :param scale: A scale parameter by which the projected x, y values are divided. Default to one.
    :param bounding_box: An optional bounding box (min_x, max_x, min_y, max_y). If the supplied line
    falls entirely outside this bounding box no plotting is done.
    :param kwargs: Any other keyword arguments are passed to pyplot.plot.
    """
    if latlons is not None:
        lat_lon_points = latlons
    elif lats is not None and lons is not None:
        lat_lon_points = zip(lats, lons)
    else:
        raise Exception('Missing parameters lats and lons, or latlons.')
    #
    projected = [projection(lon, lat) for lat, lon in lat_lon_points]
    scaled = [(x / scale, y / scale) for x, y in projected]
    if bounding_box is not None and not in_bounding_box(scaled, bounding_box):
        return False
    #
    x, y = zip(*scaled)
    pyplot.plot(x, y, **kwargs)


def plot_shapefile(path, **kwargs):
    """
    Plot a shapefile.
    :param path: The path to the shapefile.
    :param kwargs: Keyword arguments are passed to plot_projected_line.
    """
    import shapefile
    reader = shapefile.Reader(path)
    for shape in reader.shapes():
        parts = list(shape.parts) + [len(shape.points)]
        parts = zip(parts[:-1], parts[1:])
        point_slices = (shape.points[a:b] for a, b in parts)
        for point_slice in point_slices:
            lat_lon = [(lat, lon) for lon, lat in point_slice]
            plot_projected_line(latlons=lat_lon, **kwargs)
