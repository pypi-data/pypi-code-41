import csv
import os
import re
import json
import requests
import pkg_resources
from datetime import datetime

DEFAULT_LOCATION_NAME = 'Johnson City'
DEFUALT_LOCATION_COORDS = ['36.3406', '-82.3804']
LOCATION_DATA = []

# Read in location data from worldcities.csv.
# In LOCATION_DATA row[0], is city name;  row[1] and [2] are lat. & long.;
# row[4] is country code, row[6] is state/providence/territory.
def parse_location_data():
    # Join the package's path with the data path to access config.
    #this_dir = os.path.split(__file__)
    csvfile = pkg_resources.resource_filename(__name__, 'data/worldcities.csv')
    with open(csvfile, 'r') as file_data:
        csv_reader = csv.reader(file_data)

        for row in csv_reader:
            LOCATION_DATA.append(row)

# Called on by send_forecast_in() or send_forecast_here() to create and return
# a formatted forecast message.
def create_forecast_message(weather_response):
    current_temp = str(weather_response['properties']['periods'][0]
                           ['temperature']) + ' degrees. '

    current_hour = datetime.now().hour

    # Correctly display forecast for 6am to 12pm.
    if (current_hour < 6) or (current_hour > 17):
        forecast_msg = (
            # Current day temp + forecast.
            '\n\n' + weather_response['properties']['periods'][0]['name']
            + ': ' + current_temp + (weather_response['properties']
                                    ['periods'][0]['detailedForecast'])
            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][1]['name']
            + ': ' + (weather_response['properties']['periods'][1]
                     ['detailedForecast'])

            # Next day temp + forecast.
           + '\n\n' + weather_response['properties']['periods'][3]['name']
            + ': ' + (weather_response['properties']['periods'][3]
                     ['detailedForecast'])

            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][5]['name']
            + ': ' + (weather_response['properties']['periods'][5]
                     ['detailedForecast'])

            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][7]['name']
            + ': ' + (weather_response['properties']['periods'][7]
                     ['detailedForecast'])

            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][9]['name']
            + ': ' + (weather_response['properties']['periods'][9]
                     ['detailedForecast'])
            )

    else:
        # Correctly display forecast for 6pm to 5am.
        forecast_msg = (
            # Current day temp + forecast.
            '\n\n' + weather_response['properties']['periods'][0]['name']
            + ': ' + current_temp + (weather_response['properties']
                                       ['periods'][0]['detailedForecast'])
            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][2]['name']
            + ': ' + (weather_response['properties']['periods'][2]
                     ['detailedForecast'])

            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][4]['name']
            + ': ' + (weather_response['properties']['periods'][4]
                     ['detailedForecast'])

            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][6]['name']
            + ': ' + (weather_response['properties']['periods'][6]
                     ['detailedForecast'])

            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][8]['name']
            + ': ' + (weather_response['properties']['periods'][8]
                     ['detailedForecast'])

            # Next day temp + forecast.
            + '\n\n' + weather_response['properties']['periods'][10]['name']
            + ': ' + (weather_response['properties']['periods'][10]
                     ['detailedForecast'])
            )

    return forecast_msg


# Create and return the current weather info for the default location.
def send_weather_here():
    weather_response = (requests.get('https://api.weather.gov/points/'
                     + DEFUALT_LOCATION_COORDS[0] + ','
                     + DEFUALT_LOCATION_COORDS[1] + '/forecast').json())

    temp_string = str(weather_response['properties']['periods'][0]
                                      ['temperature']) + ' degrees. '

    current_weather = (weather_response['properties']['periods'][0]['name']
                    + ': ' + temp_string + (weather_response['properties']
                                           ['periods'][0]['detailedForecast']))

    return 'Weather for ' + DEFAULT_LOCATION_NAME + ': ' + current_weather


# Create and return the current weather info for a location other than the
# default location.
def send_weather_in(message):
    # Default reply if the territory is not in LOCATION_DATA:
    weather_msg = 'Weather data could not be found for that location.'

    # Split string in 2 and store 2nd string as place name to search.
    msg_split = message.split('weather in ', 1)
    place = msg_split[1]

    row_found = False
    str_search = re.match('.*,.*', place)
    # '.*,.*' means 'city, state/providence' or 'city, state/country' so both
    # of these will be searched for in the for-loop.
    if (str_search):
        split_str = place.split(',', 1)
        for row in LOCATION_DATA:
            if ((row[0] in split_str[0])
               and (row[4] in split_str[1])):
                city = row[0]
                row_found = True
                break
            elif ((row[0] in split_str[0])
                 and (row[6]in split_str[1])):
                row_found = True
                break

    # else, only the city was specified. If two of the same cities, it will
    # return forecast of the first one it came accross in LOCATION_DATA.
    else:
         for row in LOCATION_DATA:
            if (row[0] == place):
                row_found = True
                break


    if (row_found):

        weather_response = (requests.get('https://api.weather.gov/points/'
                         + row[1] + ',' + row[2] + '/forecast').json())

        if not('status' in weather_response.keys()):
            current_weather = ((weather_response['properties']['periods'][0]
                                                ['name']) + ' '
                            + (weather_response['properties']['periods'][0]
                                               ['detailedForecast']))

            weather_msg = ('Weather for ' + row[0].capitalize() + ', '
                           + row[6].capitalize() + ': ' + current_weather)

    return weather_msg


# Create and return a 6-day weather forecast message for the default
# location.
def send_forecast_here():
    weather_response = (requests.get('https://api.weather.gov/points/'
                     + DEFUALT_LOCATION_COORDS[0]
                     + ',' + DEFUALT_LOCATION_COORDS[1] + '/forecast').json())

    current_weather = create_forecast_message(weather_response)

    return 'Weather for ' + DEFAULT_LOCATION_NAME + ': ' + current_weather


# Create and return a 6-day weather forecast message for a location other
# than the default location.
def send_forecast_in(message):
    # Default reply if the territory is not in LOCATION_DATA:
    weather_msg = 'Weather data could not be found for that location.'

    # Split string in 2 and store 2nd string as place name to search.
    msg_split = message.split('forecast in ', 1)
    place = msg_split[1]

    row_found = False
    str_search = re.match('.*,.*', place)
    # '.*,.*' means 'city, state/providence' or 'city, state/country' so both
    # of these will be searched for in the for-loop.
    if (str_search and ',' in place):
        split_str = place.split(',', 1)
        for row in LOCATION_DATA:
            if ((row[0] in split_str[0]) # Try to match city, country.
               and (row[4] in split_str[1])):
                row_found = True
                break
            elif ((row[0] in split_str[0]) # Try to match city, state.
                 and (row[6] in split_str[1])):
                row_found = True
                break
    # else, only the city was specified. If two of the same cities, it will
    # return forecast of the first one it came accross in LOCATION_DATA.
    else:
         for row in LOCATION_DATA:
            if (row[0] == place):
                row_found = True
                break


    if (row_found):

        weather_response = (requests.get('https://api.weather.gov/points/'
                         + row[1] + ',' + row[2] + '/forecast').json())

        # When the response contains a 'status' this means an error occurred
        # (such as not having info about the coordinates specified),
        # therefore, we wouldn't be able to create a forecast message; code
        # would throw exception.
        if not ('status' in weather_response.keys()):
            current_weather = create_forecast_message(weather_response)
            weather_msg = ('Weather for ' + row[0].capitalize() + ', '
                           + row[6].capitalize() + ': ' + current_weather)

    return weather_msg


# Search strings about weather to determine whether to send
# default weather or weather in specified location.
def get_weather(msg):
    msg_text = msg.lower()

    reply = ''
    while True:
        str_search = re.search('tell.*weather in.*', msg_text)
        if (str_search):
            reply = send_weather_in(msg_text)
            break
        else:
            str_search = re.search('tell.*weather', msg_text)
            if (str_search):
                reply = send_weather_here()
                break

        str_search = re.search('what.*s.*weather in.*', msg_text)
        if (str_search):
            reply = send_weather_in(msg_text)
            break
        else:
            str_search = re.search('what.*s.*weather', msg_text)
            if (str_search):
                reply = send_weather_here()
                break

    return reply


# Search strings about forecast to determine whether to send
# default forecast or forecast in specified location.
def get_forecast(msg):
    msg_text = msg.lower()

    reply = ''
    while True:
        str_search = re.search('tell.*forecast in.*', msg_text)
        if (str_search):
            reply = send_forecast_in(msg_text)
            break
        else:
            str_search = re.search('tell.*forecast', msg_text)
            if (str_search):
                reply = send_forecast_here()
                break

        str_search = re.search('what.*s.*forecast in.*', msg_text)
        if (str_search):
            reply = send_forecast_in(msg_text)
            break
        else:
            str_search = re.search('what.*s.*forecast', msg_text)
            if (str_search):
                reply = send_forecast_here()
                break

    return reply
