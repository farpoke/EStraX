import datetime as dt
import numpy as np

def define_date(hysplit):
	#
	# Create datetime array
	#
	date = []
	for y,m,d,h,mi in zip(hysplit.year, hysplit.month, hysplit.day, hysplit.hour, hysplit.minute):
		date.append(dt.datetime(y+2000,m,d,h,mi))
	date = np.array(date)
	return date
