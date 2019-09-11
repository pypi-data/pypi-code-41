from API import get_lat_long,selected_place_lat_long,get_climate_data_type
from datetime import datetime
import sys

def driver(place,date=None,type_of_forecast=1):
	received_locs = get_lat_long(place)
	if received_locs == None:
		print("Place Name Not Found!!")
		return None
	sel_loc = 0
	lat,lon=selected_place_lat_long(received_locs,sel_loc)
	print("Found Place has latitude : " +str(lat) +" and logitude : " +str(lon))
	date_entry = date
	if date==None:
		forecast = get_climate_data_type(lat,lon,
		selection=int(type_of_forecast))
	else:
		get_climate_data_type(lat,lon,
		date=date)

if __name__ == '__main__':
	if len(sys.argv)==1 or len(sys.argv)>3:
		print("Please pass arguments in order : Place Name, "
		"{Forecast Date in [YYYY-MM-DD] format}/"
		"{Type of forecast [Optional]('1' for today {Default Selection},"
		" '2' for monthly,"
		" '3' for 5-day and"
		" '4' for 10-day)}"
		)
	elif len(sys.argv)==2:
		driver(sys.argv[1])
	elif len(sys.argv)==3:
		try:
			date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
		except:
			if (sys.argv[2].isdigit()==False) or not (1<=int(sys.argv[2])<=4):
				print("Illegal Format of Second Parameter")
				print("Please pass arguments in order : Place Name, "
				"{Forecast Date in [YYYY-MM-DD] format}/"
				"{Type of forecast [Optional]('1' for today {Default Selection},"
				" '2' for monthly,"
				" '3' for 5-day and"
				" '4' for 10-day)}"
				)
			else:
				driver(sys.argv[1],type_of_forecast=sys.argv[2])
		else:
			driver(sys.argv[1],date=date.strftime('%Y-%m-%d'))

	#print(yaml.dump(forecast))
