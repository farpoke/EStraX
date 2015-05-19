import numpy as np

MIX_HEIGHT = '../Data/bound_lay.nc'
LANDUSE_PATH ='../Data/Land/LanduseGLC.nc'
BC_PATHS ='../Data/Chem/AnnualEmisBC_Tot.nc'
NOx_PATHS ='../Data/Chem/AnnualEmisNOx_Tot.nc'
SOx_PATHS ='../Data/Chem/AnnualEmisSOx_Tot.nc'
NH3_PATHS ='../Data/Chem/AnnualEmisNH3_Tot.nc'
NMVOC_PATHS ='../Data/Chem/AnnualEmisNMVOC_Tot.nc'

from read_hysplit_data import read_hysplit_data
from define_date import define_date
from assign_nc_data import assign_landuse_data
from assign_nc_data import assign_wind_data
from assign_nc_data import assign_temperature_data
from assign_nc_data import assign_emission_data
from write_to_csv import write_to_csv
from emission_area import emission_area
from get_windspeed import get_windspeed
from assign_nc_data import assign_mixhgt


hysplit = read_hysplit_data()
lats = hysplit.lat
lons = hysplit.lon
print(lats)

date = define_date(hysplit)

area = emission_area(lats, lons)
#print(area)
landcovers = assign_landuse_data(lats, lons, LANDUSE_PATH)

tot_wind = get_windspeed(lats,lons)

mix_height = assign_mixhgt(lats,lons,MIX_HEIGHT,hysplit)

#temperatures = assign_temperature_data(lats,lons, ECMWF_PATH)

emissions = assign_emission_data(lats, lons, BC_PATHS, NOx_PATHS, SOx_PATHS, NH3_PATHS, NMVOC_PATHS)

emis_NOx = emissions[0]
emis_NOx = (1000/(30*24))*np.divide(emis_NOx,area)
emis_SOx = emissions[1]
emis_SOx = (1000/(30*24))*np.divide(emis_SOx,area)
emis_NMVOC = emissions[2]
emis_NMVOC = (1000/(30*24))*np.divide(emis_NMVOC,area)
emis_NH3 = emissions[3]
emis_NH3 = (1000/(30*24))*np.divide(emis_NH3,area)
emis_BC = emissions[4]
emis_BC = (1000/(30*24))*np.divide(emis_BC,area)
write_to_csv(hysplit, landcovers, lats, lons, tot_wind, emis_NOx, emis_SOx, emis_BC, emis_NMVOC, emis_NH3, mix_height)


