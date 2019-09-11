import requests
from datetime import datetime

def get_lat_long(place=None):
	query_url = (
		"https://api.weather.com/v3/location/search"
		"?apiKey=d522aa97197fd864d36b418f39ebb323"
		"&format=json"
		"&language=en-IN"
		"&locationType=locale"
		"&query="
		)
	query_url = query_url+place
	print(("Get request at API endpoint : {0}")
		.format(query_url))
	r = requests.get(query_url)
	if r.status_code == 200:
		return r.json()
	else:
		return None

def selected_place_lat_long(loc_json,selection=0):
	print("Found Place is : "
		+ loc_json["location"]["address"][selection])
	return(loc_json["location"]["latitude"][selection]
		,loc_json["location"]["longitude"][selection])

def get_daily_forecast(lat=0,lon=0):
	query_url = (
		"https://api.weather.com/v2/turbo/vt1observation"
		"?apiKey=d522aa97197fd864d36b418f39ebb323"
		"&format=json"
		"&geocode="
		+str(lat)+
		"%2C"
		+str(lon)+
		"&language=en-IN"
		"&units=m"
		)
	print(("Get request at API endpoint : {0}")
		.format(query_url))
	r = requests.get(query_url)
	if r.status_code == 200:
		print("========== Daily Metrics ========== ")
		print(r.json()["vt1observation"])
		return r.json()["vt1observation"]
	else:
		return None

def get_monthly_forecast(lat=0,lon=0,count=None,date=None):
	query_url = (
		"https://api.weather.com/v2/turbo/vt1dailyForecast"
		"?apiKey=d522aa97197fd864d36b418f39ebb323"
		"&format=json"
		"&geocode="
		+str(lat)+
		"%2C"
		+str(lon)+
		"&language=en-IN"
		"&units=m"
		)
	print(("Get request at API endpoint : {0}")
		.format(query_url))
	r = requests.get(query_url)
	if r.status_code == 200:
		ret_dict = r.json()["vt1dailyForecast"]
		del ret_dict['day']
		del ret_dict['night']
		day_dict = r.json()["vt1dailyForecast"]["day"]
		night_dict = r.json()["vt1dailyForecast"]["night"]
		ret_list = [dict(zip(ret_dict,t)) for t in zip(*ret_dict.values())]
		day_list = [dict(zip(day_dict,t)) for t in zip(*day_dict.values())]
		night_list = [dict(zip(night_dict,t)) for t in zip(*night_dict.values())]
		if date==None:
			if count == None:
				count = len(ret_list)
				print("========== Monthly Metrics ========== ")
			else:
				print("========== {0}-Day Metrics ========== ".format(count))
			for i in range(count):
				print("=================================")
				print("Overall : ")
				print(ret_list[i])
				print("Day Metrics : ")
				print(day_list[i])
				print("Night Metrics : ")
				print(night_list[i])
				print("=================================")
		else:
			print("========== "+str(date)+" Metrics ========== ")
			count1 = 0
			for i in range(len(ret_list)):
				if str(date) in str(ret_list[i]["validDate"]):
					count1 = count1+1
					print("=================================")
					print("Overall : ")
					print(ret_list[i])
					print("Day Metrics : ")
					print(day_list[i])
					print("Night Metrics : ")
					print(night_list[i])
					print("=================================")
			if(count1==0):
				print("No Data Found for : "+str(date))
		return ret_list,day_list,night_list
	else:
		return None

def get_climate_data_type(lat,lon,selection=0,date=datetime.today().strftime('%Y-%m-%d')):
	if selection==0:
		return get_monthly_forecast(lat,lon,date=date)
	elif selection==1:
		return  get_daily_forecast(lat,lon),None,None
	elif selection==3:
		return get_monthly_forecast(lat,lon,count=5)
	elif selection==4:
		return get_monthly_forecast(lat,lon,count=10)
	else:
		return get_monthly_forecast(lat,lon)
