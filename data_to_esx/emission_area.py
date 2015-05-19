import math
import numpy as np
from assign_nc_data import find_latlonindex



EARTH_RAD = 6378137.0     # earth circumference in meters

def great_circle_distance(latlong_a, latlong_b):

	(lat1,lon1) = latlong_a
	(lat2,lon2) = latlong_b

	dLat = math.radians(lat2 - lat1)
	dLon = math.radians(lon2 - lon1)
	a = (math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2))
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	d = EARTH_RAD * c
	d = d/1000 #To recieve km
		
	return d

def emission_area(lats, lons):
	area = []
	latvar = np.arange(-89.95,90.00,0.1)
	lonvar = np.arange(-179.95,180.00,0.1)
	for la,lo in zip(lats,lons):
		(lat,lon) = find_latlonindex(latvar,lonvar,la,lo)
		#print("Latlon = "lat,lon)
		width = great_circle_distance((latvar[lat],lonvar[lon]),(latvar[lat],lonvar[lon+1]))
		#print("Width = " width)
		length = great_circle_distance((latvar[lat],lonvar[lon]),(latvar[lat+1],lonvar[lon]))
		#print("Length = " length)
		area.append(width*length)

	return area

distance = great_circle_distance((57.70,11.97),(57.72,12.93))
print(distance)

a = emission_area([39.9],[116.4])
print(a)


	







