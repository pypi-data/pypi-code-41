#!python
'''
Created on Dec 15, 2014

@author: lwoydziak
'''
import sys, traceback
from jsonconfigfile import Env
from providers import digitalOceanHosting

'''usage: 
list_locations.py                                                                                                 # clean up
'''



def ListLocations():
    initialJson = '{ \
        "DigitalOcean" : { \
            "Access Token"  : "None", \
            "location"      : "None", \
            "image"         : "None", \
            "size"          : "None" \
        },\
        "BaseHostName": "None"\
    }'
    Env(initialJson, ".dynamicMachine", "DYNAMIC_MACHINE_CONFIG")
    onDigitalOcean = digitalOceanHosting()
    print("Available Targets:")
    for target in onDigitalOcean.list_locations():
        print (str(target))



if __name__ == '__main__':
    try:
        ListLocations()
        exit(0)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print (str(e))
        exit(1)
