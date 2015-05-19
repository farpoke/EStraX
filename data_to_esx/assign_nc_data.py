import matplotlib.pyplot as plt
import datetime as dt
import netCDF4 as netcdf
import numpy as np
import math

##########################
#find lat and lon index
##########################
def find_latlonindex(latvar,lonvar,lat,lon):
    lon_index = (np.abs(lonvar-lon)).argmin()
    lat_index = (np.abs(latvar-lat)).argmin()
    return (lat_index,lon_index)

def find_mixhgt_index(time,diff):
	index = (np.abs(time-diff)).argmin()
	return index

################
   #landcovers
################
def assign_landuse_data(lats, lons, LANDUSE_PATH):	
	
	def find_landcover(lat,lon):
		f = netcdf.Dataset(LANDUSE_PATH,'r')
		landcovers = {'CF' : [],'DF' : [],'NF' : [],'BF' : [],'TC' : [],'MC' : [],'RC' : [],'SNL' : [],
		              'GR' : [],'MS' : [],'WE' : [],'TU' : [],'DE' : [],'W' : [], 'ICE' : [], 'U' : []}
		for landcover in landcovers:
		    landcovers[landcover] = f.variables[landcover][:]
		lonvar = f.variables['lon'][:]
		latvar = f.variables['lat'][:]
		(lat_index,lon_index) = find_latlonindex(latvar,lonvar,lat,lon)
		for landcover in landcovers:
		    landcovers[landcover] = landcovers[landcover][0,lat_index,lon_index]
		cover = max(landcovers, key = landcovers.get)
		return cover

	f_land = netcdf.Dataset(LANDUSE_PATH,'r')
	landcovers = []

	for la,lo in zip(lats,lons):
		(lat,lon) = find_latlonindex(f_land.variables['lat'][:],f_land.variables['lon'][:],la,lo)  
		landcovers.append(find_landcover(la,lo))

	f_land.close()

	return(landcovers)

######################
#total wind velocity
######################
def assign_wind_data(lats, lons, ECMWF_PATH):	
	
	f_ecmwf = netcdf.Dataset(ECMWF_PATH,'r')
	u_wind1 = f_ecmwf.variables['u10'][:]
	v_wind1 = f_ecmwf.variables['v10'][:]
	u_wind = []
	v_wind = []

	for la,lo in zip(lats,lons):
		(lat,lon) = find_latlonindex(f_ecmwf.variables['latitude'][:],f_ecmwf.variables['longitude'][:],la,lo)
		u_wind.append(u_wind1[0,lat,lon])
		(lat,lon) = find_latlonindex(f_ecmwf.variables['latitude'][:],f_ecmwf.variables['longitude'][:],la,lo)
		v_wind.append(v_wind1[0,lat,lon])

	def windspeed(uw,vw):
		tot_wind =[]
		for i in range(0,len(uw)):
		    tot_wind.append(np.sqrt(uw[i]**2 + vw[i]**2))
		return tot_wind

	tot_wind = windspeed(u_wind, v_wind)

	f_ecmwf.close()

	return tot_wind

################
  #temperatures
################
def assign_temperature_data(lats, lons, ECMWF_PATH):	
	
	f_ecmwf = netcdf.Dataset(ECMWF_PATH,'r')
	temperatures1 = f_ecmwf.variables['t2m'][:]
	temperatures = []

	for la,lo in zip(lats,lons):
		(lat,lon) = find_latlonindex(f_ecmwf.variables['latitude'][:],f_ecmwf.variables['longitude'][:],la,lo)
		temperatures.append(temperatures1[0,lat,lon])

	
	f_ecmwf.close()

	return(temperatures)

################	
 #emissions
################
def assign_emission_data(lats, lons, BC_PATHS, NOx_PATHS, SOx_PATHS, NH3_PATHS, NMVOC_PATHS):	
	
	f_NOx = netcdf.Dataset(NOx_PATHS,'r')
	emis_NOx1 = f_NOx.variables['NOx_sec01'][:]
	f_SOx = netcdf.Dataset(SOx_PATHS,'r')
	emis_SOx1 = f_SOx.variables['SOx_sec01'][:]
	f_NMVOC = netcdf.Dataset(NMVOC_PATHS,'r')
	emis_NMVOC1 = f_NMVOC.variables['NMVOC_sec01'][:]
	f_NH3 = netcdf.Dataset(NH3_PATHS,'r')
	emis_NH31 = f_NH3.variables['NH3_sec01'][:]
	f_BC = netcdf.Dataset(BC_PATHS,'r')
	emis_BC1 = f_BC.variables['BC_sec01'][:]

	emis_NOx = []
	emis_SOx = []
	emis_NMVOC = []
	emis_NH3 = []
	emis_BC = []

	for la,lo in zip(lats,lons):
		(lat,lon) = find_latlonindex(f_NOx.variables['lat'][:],f_NOx.variables['lon'][:],la,lo)
		emis_NOx.append(emis_NOx1[0,lat,lon])
		(lat,lon) = find_latlonindex(f_SOx.variables['lat'][:],f_SOx.variables['lon'][:],la,lo)
		emis_SOx.append(emis_SOx1[0,lat,lon])
		(lat,lon) = find_latlonindex(f_NMVOC.variables['lat'][:],f_NMVOC.variables['lon'][:],la,lo)
		emis_NMVOC.append(emis_NMVOC1[0,lat,lon])
		(lat,lon) = find_latlonindex(f_NH3.variables['lat'][:],f_NH3.variables['lon'][:],la,lo)
		emis_NH3.append(emis_NH31[0,lat,lon])
		(lat,lon) = find_latlonindex(f_BC.variables['lat'][:],f_BC.variables['lon'][:],la,lo)
		emis_BC.append(emis_BC1[0,lat,lon])

	emissions = [emis_NOx,emis_SOx,emis_NMVOC,emis_NH3,emis_BC]

	f_BC.close()
	f_NH3.close()
	f_NMVOC.close()
	f_SOx.close()
	f_NOx.close()

	return(emissions)


################
  #mixing height
################

def assign_mixhgt(lats, lons, ECMWF_PATH, hysplit):	
	
	f_ecmwf = netcdf.Dataset(ECMWF_PATH,'r')
	blh = f_ecmwf.variables['blh'][:]
	mix_hgt = []

	start_time = dt.datetime(1900,1,1)

	for la,lo,year,month,day,hour in zip(lats,lons,hysplit.year,hysplit.month,hysplit.day,hysplit.hour):
		(lat,lon) = find_latlonindex(f_ecmwf.variables['latitude'][:],f_ecmwf.variables['longitude'][:],la,lo)
		time_now = dt.datetime(year+2000,month,day,hour)
		diff = (time_now - start_time).total_seconds()/3600
		time = f_ecmwf.variables['time']
		time = time[:]
		index = find_mixhgt_index(time,diff)
		mix_hgt.append(blh[index,lat,lon])

	
	f_ecmwf.close()

	return(mix_hgt)





