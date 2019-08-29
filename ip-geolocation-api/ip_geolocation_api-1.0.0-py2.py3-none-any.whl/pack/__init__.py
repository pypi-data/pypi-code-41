import requests
import json

class IPwhoisio:

    def __init__(self, ip=""):
        url = "http://free.ipwhois.io/json"
        if not(ip == ""):
            url = "http://free.ipwhois.io/json" + ip
        j = requests.get(url).content.decode()
        j = json.loads(j)
        self.ip = j['ip']
        self.type = j['type']
        self.continent = j['continent']
        self.country = j['country']
        self.country_code = j['country_code']
        self.region = j['region']
        self.city = j['city']
        self.latitude = j['latitude']
        self.longitude = j['longitude']
        self.asn = j['asn']
        self.org = j['org']
        self.isp = j['isp']
        self.timezone = j['timezone']
        self.currency = j['currency']