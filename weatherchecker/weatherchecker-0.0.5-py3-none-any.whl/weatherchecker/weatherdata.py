import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
place_search_api = "https://api.weather.com/v3/location/search?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&language=en-IN&locationType=locale&query={}"
daily_base_url = "https://weather.com/en-IN/weather/today/l/{}"
hourly_base_url = "https://weather.com/en-IN/weather/hourbyhour/l/{}"
monthly_base_url = "https://dsx.weather.com/wxd/v2/PastObsAvg/en_IN/{}/{}/{},{}?api=7bb1c920-7027-4289-9c96-ae5e263980bc"
requests.packages.urllib3.disable_warnings()


class weather(object):
    """docstring for weather"""
    def __init__(self, place_details={}):
        self.place_details = place_details

    def findplace(self, searchkey=None):
        try:
            if searchkey:
                url = place_search_api.format(searchkey)
                htmlresponse = requests.get(url)
                place_response = htmlresponse.json()
                loc = place_response["location"]
                spd = self.place_details
                spd["ianaTimeZone"] = loc["ianaTimeZone"][0]
                spd["city"] = loc["city"][0]
                spd["displayName"] = loc["displayName"][0]
                spd["countryCode"] = loc["countryCode"][0]
                spd["locale"] = loc["locale"][0]
                spd["country"] = loc["country"][0]
                spd["locId"] = loc["locId"][0]
                spd["adminDistrictCode"] = loc["adminDistrictCode"][0]
                spd["longitude"] = loc["longitude"][0]
                spd["placeId"] = loc["placeId"][0]
                spd["pwsId"] = loc["pwsId"][0]
                spd["postalCode"] = loc["postalCode"][0]
                spd["locationCategory"] = loc["locationCategory"][0]
                spd["address"] = loc["address"][0]
                spd["latitude"] = loc["latitude"][0]
                spd["neighborhood"] = loc["neighborhood"][0]
                spd["adminDistrict"] = loc["adminDistrict"][0]
                spd["disputedArea"] = loc["disputedArea"][0]
                spd["type"] = loc["type"][0]
        except Exception as e:
            raise e
        return

    def monthly_weather(self, date=None, no_of_days=30):
        try:
            latitude = self.place_details['latitude']
            longitude = self.place_details['longitude']
            url = monthly_base_url.format(
                    date, str(no_of_days),
                    str("%.2f" % latitude), str("%.2f" % longitude))
            monthlyresponse = requests.get(url)
            monthly_data = monthlyresponse.json()
            new_colums = {
                'Temperatures': {
                    'High temperature(c)': 'highC',
                    'Low Temperature(c)': 'lowC'},
                'WxDetails': {'discription': 'wx'}}
            categorys = {'Temperatures', 'WxDetails'}
            new_month_data = []
            for data in monthly_data:
                single_day = {}
                for category in categorys:
                    for key, value in new_colums[category].items():
                        single_day[key] = data[category][value]
                date = data['Temperatures']['highTmISOLocal'][:10]
                single_day['Date'] = date
                new_month_data.append(single_day)
            final_data = pd.DataFrame(new_month_data)
        except Exception as e:
            raise e
        return final_data

    def weather_today(self):
        try:
            url = daily_base_url.format(self.place_details['placeId'])
            dailyresponse = requests.get(url)
            dailyresponsescrape = BeautifulSoup(
                dailyresponse.text, 'html.parser')
            tabledata = dailyresponsescrape.find_all(
              "div", class_="today_nowcard-sidecar component panel"
                                                    )[0].find("table")
            final_data = pd.read_html(str(tabledata))
        except Exception as e:
            raise e
        return final_data

    def hourly_weather(self):

        try:
            url = hourly_base_url.format(self.place_details['placeId'])
            hourlyresponse = requests.get(url)
            hourlyresponsescrap = BeautifulSoup(
                    hourlyresponse.text, 'html.parser')
            tabledata = hourlyresponsescrap.find_all(
                    "table", classname="twc-table")[0]
            # print(tabledata)
            for td in tabledata.find_all(
                    'td', class_="twc-sticky-col cell-hide"):
                td.decompose()
            final_data = pd.read_html(str(tabledata))
        except Exception as e:
            raise e
        return final_data

def  weatherreport(place=None, forecasttype="daily", date=None):
    valid = False
    if place:
        weather_object=weather()
        weather_object.findplace(place)
        data = None
        if forecasttype == "daily":
            if date:
                data = weather_object.monthly_weather(date,1)
                valid = True
            else:
                data = weather_object.weather_today()
                valid = True
        elif forecasttype == "hourly":
            data = weather_object.hourly_weather()
            valid = True
        elif forecasttype == "monthly":
            if date:
                data = weather_object.monthly_weather(date,30)
                valid = True
            else:
                date = datetime.now().strftime("%Y%m%d")
                data = weather_object.monthly_weather(date,30)
                valid = True
        else:
            raise Exception("Invalid input")
        if valid:
            print(data)
    else:
        raise Exception("Invalid input")
    return