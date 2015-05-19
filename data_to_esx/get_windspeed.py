import math
from emission_area import great_circle_distance

def get_windspeed(lats,lons):
	windspeeds = []
	for i in range(len(lats)-1):
		dist = great_circle_distance((lats[i],lons[i]),(lats[i+1],lons[i+1]))
		speed = (dist*1000)/3600	#m/s
		windspeeds.append(speed)
	windspeeds.append(windspeeds[len(windspeeds)-1])
	return windspeeds
