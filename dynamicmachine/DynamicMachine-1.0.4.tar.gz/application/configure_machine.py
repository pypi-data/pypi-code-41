#!/usr/bin/python3
'''
Created on Jun 14, 2014

@author: lwoydziak
'''
import sys, traceback
from jsonconfigfile import Env
from json import load, dumps, loads
from dynamic_machine.cli_process_json import CliProcessingJson
from time import sleep
from builtins import exit

def configureNode(ip, jsonFileName):
    if not jsonFileName:
        json = '{\
            "username" : "root",\
            "password" : "",\
            "commands" : [ \
                {"wget http://pertino-installers.s3-website-us-east-1.amazonaws.com/clients/linux/300-4050/pertino_300.4050-1_amd64.deb":\
                    {"assertResultEquals":"saved"}}\
            ]}'
        json = loads(json)
    else:
        with open(jsonFileName, "r") as jsonFile:
            json = load(jsonFile)
    json['hostname'] = ip
    cliProcessor = CliProcessingJson(None, initialJsonString=dumps(json))
    for _ in range(1,20):
        try:
            cliProcessor.execute()
            return
        except (RuntimeWarning, Exception):
            sleep(30)
            continue
    raise RuntimeError("Could not establish ssh connection (or configure) "+ip)    
    
def ConfigureMachine(ip, jsonFileName):
    initialJson = '{ \
        "DigitalOcean" : { \
            "Access Token"  : "None", \
            "location"      : "None", \
            "image"         : "None", \
            "size"          : "None" \
        },\
        "BaseHostName": "None"\
    }'
    Env(initialJson, jsonFileName, "DYNAMIC_MACHINE_CONFIG")
    configureNode(ip, jsonFileName)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Configure a machine.')
    parser.add_argument('--ip', help='The IP address of the machine.', required=True)
    parser.add_argument('--jsonFile', default=".dynamicMachine", help='The filename of the JSON file containing the list of commands.',required=False)
    args = parser.parse_args()
    try:
        ConfigureMachine(args.ip, args.jsonFile)
        exit(0)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print (str(e))
        exit(1)
