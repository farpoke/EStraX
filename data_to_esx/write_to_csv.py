import csv

# write alla data above to a csv file nc_data.csv

def write_to_csv(hysplit, landcovers, lats, lons, tot_wind, emis_NOx, emis_SOx, emis_BC, emis_NMVOC, emis_NH3, mix_height):

	with open("../ESX/examples/Lagrange0/rao_4d_13072818.csv", "w") as myfile:
		wr = csv.writer(myfile, delimiter= ",")
		wr.writerow(["yyyy","mm","dd","hh","LC","lat","lon","t2C","wspeed","rh","hmix","precipation","emis_NO","emis_SOX","emis_BC","emis_NMVOC","emis_NH3"])
		wr.writerow(["int","int","int","int","txt","degN","degE","degC","m/s","frac","m","mm/h","kg/km2/h","kg/km2/h","kg/km2/h","kg/km2/h","kg/km2/h"])
	
		for i in range(len(hysplit.year)): #does not matter wich array one takes, they all have the same length.
				wr.writerow([str(hysplit.year[len(hysplit.year)-1-i]+2000), str(hysplit.month[len(hysplit.year)-1-i]), str(hysplit.day[len(hysplit.year)-1-i]), str(hysplit.hour[len(hysplit.year)-1-i]),str(landcovers[len(hysplit.year)-1-i]), str(lats[len(hysplit.year)-1-i]), str(lons[len(hysplit.year)-1-i]), 
				str(hysplit.temp[len(hysplit.year)-1-i]-273.15), str(tot_wind[len(hysplit.year)-1-i]), str(hysplit.relhum[len(hysplit.year)-1-i]/100), str(mix_height[len(hysplit.year)-1-i]), str(hysplit.precip[len(hysplit.year)-1-i]), str(emis_NOx[len(hysplit.year)-1-i]), str(emis_SOx[len(hysplit.year)-1-i]), str(emis_BC[len(hysplit.year)-1-i]), 
				str(emis_NMVOC[len(hysplit.year)-1-i]), str(emis_NH3[len(hysplit.year)-1-i])])
