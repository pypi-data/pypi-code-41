# app.py

import os
import re
import time
import random
import requests
import pkg_resources
from multiprocessing import Process
from motioneyebot import config_util
from motioneyebot import pops_calls
from motioneyebot import weather_util

config_constants = []

# Join the package's path with the data path to access config.
configfile = pkg_resources.resource_filename(__name__, 'data/config.txt')
with open(configfile, 'r') as f:
    for i, line in enumerate(f):
        # Parse user's string and store in config_constants[]:
        if ('=' in line):
            split_str = line.split('=', 1)
            var = split_str[1].replace("'", '')
            config_constants.append(re.sub(r'#.*', '', var).strip())

ACCESS_TOKEN = config_constants[0]
BOT_ID = config_constants[1]
GROUP_ID = config_constants[2]
INDEX_LOCATION = config_constants[3]
MOTIONEYE_IP = config_constants[4]
PUBLIC_IP = config_constants[5]
UPLOADS_URL = config_constants[6]
BOT_NAME = config_constants[7]
GROUP_NAME = config_constants[8]

POST_URL = 'https://api.groupme.com/v3/bots/post'

request_params = { 'token': ACCESS_TOKEN }


def send_reply(reply, message):
    post_params = { 'bot_id': BOT_ID, 'text': reply }
    req = requests.post(POST_URL, params = post_params)
    request_params['since_id'] = message['id']

    print(message['text'] + '\n')
    print('Sent reply: ' + reply)
    print(req) # Print http response.


def send_snap_reply(message):

    # Location of web server's index page and dir where images are
    # stored so they can be accessed by url
    # 'public_ip_address/image_name.jpeg'
    # for example, '12.345.67.89/0002021312312312.jpeg'
    test = os.listdir(INDEX_LOCATION)

    i = 0
    for item in test:
        i += 1

    if (i > 49): # Clear out folder every 50 images.
        for item in test:
            # Remove all old jpegs from previous downloads.
            if (item.endswith('.jpeg')):
                os.remove(os.path.join(INDEX_LOCATION, item))

    # Goal here is basically to create an image name that will never be
    # used again. Workaround for groupme api caching first image from
    # url and never sending new image even after content in
    # 'current.jpeg', for example, had changed.

    filename = (str(random.randint(0, 90000000))
             + str(random.randint(0, 90000000)) + '.jpeg')

    with open('/var/www/html/' + filename, 'wb') as jpeg:
        jpeg.write(requests.get('http://' + MOTIONEYE_IP
                            + '/picture/1/current/').content)

    post_params = { 'bot_id': BOT_ID, 'text': '' }
    post_data = {'text': 'current.jpeg', 'picture_url':
    ('http://' + PUBLIC_IP + '/' + filename)}
    req = requests.post(POST_URL, params = post_params, data = post_data)
    request_params['since_id'] = message['id']

    print(message['text'] + '\n')
    print('Sent most recent image snap')
    print(req) # Print http response.


def main():
    # Parse in all the location data from file:
    weather_util.parse_location_data()

    while True:
        try:
            response = requests.get('https://api.groupme.com/v3/groups/'
                     + GROUP_ID + '/messages', params = request_params)

            if (response.status_code == 200):
                response_messages = response.json()['response']['messages']

                print('\n####################'
                     + '\n# Bot: ' + BOT_NAME
                     + '\n# Group: ' + GROUP_NAME
                     + '\n# Status: Listening'
                     + '\n ###################')

                # Iterate through each message, checking its text
                for message in response_messages:
                    if not (message['text'] == None):
                        # Test for Weather query first
                        # Forecast searches before weather because ppl may
                        # say "Whats the weather forecast":
                        str_search = re.search('what.*s.*forecast',
                        message['text'].lower())
                        if (str_search):
                            reply = weather_util.get_forecast(message['text'])
                            send_reply(reply, message)
                            break

                        str_search = re.search('tell.*forecast',
                        message['text'].lower())
                        if (str_search):
                            reply = weather_util.get_forecast(message['text'])
                            send_reply(reply, message)
                            break

                        str_search = re.search('what.*s.*weather',
                        message['text'].lower())
                        if (str_search):
                            reply = weather_util.get_weather(message['text'])
                            send_reply(reply, message)
                            break

                        str_search = re.search('tell.*weather',
                        message['text'].lower())
                        if (str_search):
                            reply = weather_util.get_weather(message['text'])
                            send_reply(reply, message)
                            break

                        # If someone tags Pops (and not to ask weather),
                        # pops_calls handles the reply:
                        if ('@pops' in message['text'].lower()):
                            reply = pops_calls.get_reply(message)
                            send_reply(reply, message)
                            break

                        # Key words to get info from MotionEye camera;
                        # popcam_calls handles these.

                        # I have an IFTTT webhook which when called by
                        # MotionEye, posts 'ALERT!!...' when motion is
                        # detected. Then my bot knows to post a current
                        # snapshot:
                        elif (('ALERT!!' in message['text'])
                             or (message['text'] == 'SNAP')):

                            attempt_send = Process(target =
                            send_snap_reply(message))

                            attempt_send.start()
                            # Max time function can run is 45 secs.
                            attempt_send.join(timeout = 45)
                            # Terminate if still running after 45.
                            attempt_send.terminate()
                            break

                        elif (message['text'] == 'STREAM'):
                            send_reply(MOTIONEYE_IP, message)
                            break

                        elif (message['text'] == 'UPLOADS'):
                            # A dash is stored if no URL was given.
                            if not (UPLOADS_URL == '-'):
                                send_reply(UPLOADS_URL, message)
                            break

        except requests.exceptions.ConnectionError as e:
            print('No connection')
            print(e)

        except requests.exceptions.Timeout as e:
            print('Connection timed out')
            print(e)

        except requests.exceptions.RequestException as e:
            print('A request error ocurred')
            print(e)

        except:
            print('An error occurred')

        time.sleep(5)
main()

