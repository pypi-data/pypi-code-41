import os
import json
import sys
from argparse import ArgumentParser
from ddnsaws.getmyip import GetMyIP
from ddnsaws.setddns import SetDDNS


try:
    with open('config.json') as f:
        config = json.loads(f.read())
    try:
        HostedZoneId = config['HostedZoneId']
    except:
        HostedZoneId = None
    try:
        DNSName = config['DNSName']
    except:
        DNSName = None
except:
    HostedZoneId = None
    DNSName = None


def create_parser():
    parser = ArgumentParser()
    if HostedZoneId:
        parser.add_argument('--HostedZoneId', '-z', help="HostedZoneId to upload A Record to", default=f"{HostedZoneId}", nargs="?")
    elif not HostedZoneId:
        parser.add_argument('--HostedZoneId', '-z', help="HostedZoneId to upload A Record to")
    if DNSName:
        parser.add_argument('--DNSName', '-d', help="FQDN for A Record", default=f"{DNSName}", nargs="?")
    elif not DNSName:
        parser.add_argument('--DNSName', '-d', help="FQDN for A Record")
    parser.add_argument('--verbose', '-v', help="Output Verbose", action='store_true')
    return parser


def main():
    args = create_parser().parse_args()
    if args.verbose:
        print(f"args = {vars(args)}")
    try:
        MyIP = GetMyIP()
        if args.verbose:
            print(f"IP = {MyIP}")
    except Exception as err:
        print("Unexpected Error:\n", err)
        sys.exit([1])
    try:
        response = SetDDNS(MyIP,args.DNSName,args.HostedZoneId)
        if args.verbose:
            print(response)
    except Exception as err:
        print("Unexpected Error:\n", err)
        sys.exit([1])
