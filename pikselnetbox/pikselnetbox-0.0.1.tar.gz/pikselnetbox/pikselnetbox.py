#!/usr/bin/env python3


#### Import Modules ####
import requests
import pprint
import os
import socket
import netifaces
import logmatic
import logging
import logging.handlers
import datetime
from ipaddress import ip_network, ip_address

#### LOGGING ####
# Default Parameters
LOGFILE_PATH = '/var/log/netbox_update'
LOGFILE_NAME = 'netbox_update.log'
# Initialisation log number - increments on each log message - used to help elk track log ordering
LOG_NO = 0
DEBUG = True
MAXBYTES     = 10000000
BACKUP_COUNT = 5
##### Initialise Logging #####
# open logfile
LOGFILE = LOGFILE_PATH + "/" + LOGFILE_NAME
logger = logging.getLogger('MyLogger')
if (DEBUG == True):
   logger.setLevel(logging.DEBUG)
else:
   logger.setLevel(logging.WARN)

if not (os.path.exists(LOGFILE_PATH)):
    print ("Unable to open logfile \"%s\" - exiting" % LOGFILE)

handler = logging.handlers.RotatingFileHandler(LOGFILE,'a', MAXBYTES, BACKUP_COUNT)
handler.setFormatter(logmatic.JsonFormatter(extra={"hostname":socket.gethostname()}))
logger.addHandler(handler)

#### Variables ####
HOSTNAME = socket.gethostname()
NETWORKS = []
GET_INDIVIDUAL_IP = "/api/ipam/ip-addresses/?address="
GET_PREFIXES = "/api/ipam/prefixes/?limit=0"
IPAM = "/api/ipam/ip-addresses/"
GET_PREFIX = "/api/ipam/prefixes/?prefix="


#### Logger ####
class Logger:
    def log_error(message):
        global LOG_NO
        LOG_NO += 1
        logger.error(message, extra={"datetime":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + str(LOG_NO).zfill(3)})

    def log_warn(message):
        global LOG_NO
        LOG_NO += 1
        logger.warn(message, extra={"datetime":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + str(LOG_NO).zfill(3)})

    def log_info(message):
        global LOG_NO
        LOG_NO += 1
        logger.info(message, extra={"datetime":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + str(LOG_NO).zfill(3)})

    def log_debug(message):
        global LOG_NO
        LOG_NO += 1
        logger.debug(message, extra={"datetime":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + str(LOG_NO).zfill(3)})


#### Define Functions ####
class Client:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization':'Token ' + self.token}
        self.client = requests.Session()
        self.client.headers.update(self.headers)

    def post(self, base_url, query, payload):
        request = self.client.post(base_url + query, data = payload)
        print(request)
        return request

    def get(self, base_url, query):
        request = self.client.get(base_url + query)
        return request

    def patch(self, base_url, query, payload):
        request = self.client.patch(base_url + query, data = payload)
        return request

    def delete(self, base_url, query):
        request = self.client.delete(base_url + query)
        return request

class Helper:
    def __init__(self, token, base_url):
        self.httpclient = Client(token)
        self.logger = Logger
        self.base_url = base_url
        self.get_single_ip = GET_INDIVIDUAL_IP
        self.ipam_query = IPAM
        self.get_prefixes = GET_PREFIXES
        self.get_single_prefix = GET_PREFIX

    def get_ipam_object(self, address):
        try:
            queries = self.get_single_ip + address
            individual_ip = self.httpclient.get(self.base_url, queries)
            content = individual_ip.text
        except:
            self.logger.log_error("There has been an error fetching the IP address from Netbox: " + content + " EXITING")
            exit()
        iip_json = individual_ip.json()
        if iip_json['count'] > 0:
            return iip_json['results']
        else:
            self.logger.log_info("No IP's were found in Netbox matching " + address + ". Now attempting to create entry.")
            return False

    def get_prefixes_all(self):
        results = []
        try:
            prefixes = self.httpclient.get(self.base_url, self.get_prefixes)
            print(prefixes)
            prefixes_json = [prefixes.json()]
            for prefix in prefixes_json:
                results += prefix['results']
            return results
        except:
            self.logger.log_error("Couldn't fetch prefixes from: " + self.base_url + " EXITING")
            exit()

    def get_interface_ips(self):
        interface_ips = []
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            ifaces = netifaces.ifaddresses(interface)
            interface_ips.append(ifaces[2][0]['addr'])
        return interface_ips

    def get_dns_names(self, ip_address):
        try:
            dns_results = []
            dns_lookup = socket.gethostbyaddr(ip_address)
            dns_results += [dns_lookup[0]]
            return dns_results
        except:
            self.logger.log_error("Error when performing reverse lookup. CHECK PTR RECORD")
            dns_results += ["Missing PTR Record"]
            return dns_results

    def get_prefix_ranges(self, ip_address):
        ip_add = ip_address.split('.')
        dot = '.'
        search_ip = dot.join(ip_add[0:3])
        prefixes = Helper.get_prefixes_all(self)
        matches = []
        calculated_range = ''
        try:
            for prefix in prefixes:
                if search_ip in prefix['prefix']:
                    matches.append(prefix['prefix'])
                elif not (search_ip in prefixes):
                    search_ip = dot.join(ip_add[0:2])
                    if search_ip in prefix['prefix']:
                        matches.append(prefix['prefix'])
            return matches
        except:
            self.logger.log_error("Couldnt find any matching prefixes for: " + ip_address + " EXITING")
            exit()

    def update_description(self, ipam_id, description):
        try:
            date_time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.")
            payload = {"description": description + " - Added automatically by netbox python at: " + date_time_now, 'tags':str(["ULS Netbox Automation",]).replace("'", '"')}
            update = self.httpclient.patch(self.base_url, self.ipam_query + ipam_id + '/', payload)
            return update
        except:
            self.logger.log_error("Error when updating description " + update + " EXITING")
            exit()

    def update_dns_name(self, ipam_id, dns_name):
        try:
            payload = {"dns_name":dns_name}
            update = ''
            update = self.httpclient.patch(self.base_url, self.ipam_query + ipam_id + '/', payload)
            content = update.text
            return update
        except:
            self.logger.log_error("Error when updating dns_name for " + dns_name + " - " + content + " EXITING")
            exit()

    def create_ipam_object(self, ip_address, hostname, prefix_range, dns_name, tag_name):
        try:
            date_time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.")
            payload = {"address":ip_address + '/' + str(prefix_range), "description":hostname + " - Added automatically by netbox python at: " + date_time_now, "status": 1, "dns_name":dns_name, 'tags':str([tag_name,]).replace("'", '"')}
            create = self.httpclient.post(self.base_url, self.ipam_query, payload)
            content = create.text
            return content
        except:
            self.logger.log_error("Error creating IPAM entry in Netbox for: " + ip_address + " - " + hostname + " - " + content + " EXITING")
            exit()

    def get_interface_ips(self):
        try:
            interface_ips = []
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                ifaces = netifaces.ifaddresses(interface)
                interface_ips.append(ifaces[2][0]['addr'])
            return interface_ips
        except:
            self.logger.log_error("Error when getting IP address(es).. EXITING")
            exit()

    def get_dns_names(self, ip_address):
        try:
            dns_results = []
            dns_lookup = socket.gethostbyaddr(ip_address)
            dns_results += [dns_lookup[0]]
            return dns_results
        except:
            self.logger.log_error("Error when performing reverse lookup, CHECK PTR RECORD")
            dns_results += [hostname + ": Missing PTR Record", "MISSING PTR"]
            return dns_results

    def calculate_prefix(self, prefixes, interface):
        try:
            networks = []
            for prefix in prefixes:
                network = ip_network(prefix)
                if ip_address(interface) in network:
                    networks.append(str(network))
            return networks[-1]
        except:
            self.logger.log_error("Error when calculating prefix from " + str(network) + " EXITING")
            exit()
