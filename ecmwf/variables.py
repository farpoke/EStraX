"""
This module provides some predefined descriptions of ECMWF variables.

They are described as a tuple (name, dimensions) matching the variable name
and dimensions in the ECMWF generated netCDF4 files.
"""


TYPE_AXIS = tuple()
TYPE_LAT_LON = ('latitude', 'longitude')
TYPE_TIME_LAT_LON = ('time', 'latitude', 'longitude')
TYPE_TIME_PRESSURE_LAT_LON = ('time', 'level', 'latitude', 'longitude')


U_VELOCITY = ('u', TYPE_TIME_PRESSURE_LAT_LON)
V_VELOCITY = ('v', TYPE_TIME_PRESSURE_LAT_LON)
W_VELOCITY = ('w', TYPE_TIME_PRESSURE_LAT_LON)

RELATIVE_HUMIDITY = ('r', TYPE_TIME_PRESSURE_LAT_LON)

RELATIVE_HUMIDITY_SINGLE_LEVEL = ('r', TYPE_TIME_LAT_LON)

U_VELOCITY_10M = ('u10', TYPE_TIME_LAT_LON)
V_VELOCITY_10M = ('v10', TYPE_TIME_LAT_LON)

SURFACE_TEMPERATURE = ('t2m', TYPE_TIME_LAT_LON)
SURFACE_PRESSURE = ('sp', TYPE_TIME_LAT_LON)

BOUNDARY_LAYER_HEIGHT = ('blh', TYPE_TIME_LAT_LON)

LARGE_SCALE_PRECIPITATION = ('lsp', TYPE_TIME_LAT_LON)
TOTAL_PRECIPITATION = ('tp', TYPE_TIME_LAT_LON)
