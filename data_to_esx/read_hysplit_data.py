import numpy as np

def read_hysplit_data():
	# Specify format for numpy recfromtxt routine
	# Give names to columns
	nam = ['traj', 'grid-nb', 'year', 'month', 'day', 'hour', 'minute', 'fhour', 'ageoftraj',
		   'lat', 'lon', 'height', 'pres','temp','precip','mixhgt','relhum']
	# Specify format strings for each column
	form = ['<i4', '<i4', '<i4', '<i4', '<i4', '<i4', '<i4', '<i4', '<f8', '<f8', '<f8', '<f8', '<f8','<f8', '<f8', '<f8', '<f8']
	# Read data
	hysplit = np.recfromtxt('../Data/rao_4d_13072818', skip_header=5, dtype={'names':nam, 'formats':form},
		                    delimiter=(6,6,6,6,6,6,6,6,8,9,9,9,9,9,9,9,9))
	return hysplit
