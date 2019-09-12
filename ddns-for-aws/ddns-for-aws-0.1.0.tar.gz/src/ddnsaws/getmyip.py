import requests
import sys


def GetMyIP():
    try:
        request = requests.get('https://api.ipify.org')
    except Exception as err:
        print("Unexpected Error:\n", err)
        sys.exit([1])
    return request.text
