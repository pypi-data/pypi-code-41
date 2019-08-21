import httplib
import json
class BaseObject:
  def from_dict(self, d):
    if 'appliance_hostname' in d:
      self.appliance_hostname = d['%!s(MISSING)']
    if 'api_key' in d:
      self.api_key = d['%!s(MISSING)']
    if 'sec_key' in d:
      self.sec_key = d['%!s(MISSING)']
    if 'insecure' in d:
      self.insecure = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['appliance_hostname'] = self.appliance_hostname
    d['api_key'] = self.api_key
    d['sec_key'] = self.sec_key
    d['insecure'] = self.insecure
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
    def __init__(self, appliance_hostname, api_key, sec_key, insecure = False):
    self.appliance_hostname = appliance_hostname
    self.api_key = api_key
    self.sec_key = sec_key
    self.insecure = insecure
  

    def make_headers(self):
    return {
      'Authorization': 'Token token="' + str(self.api_key) + str(self.sec_key) + '"',
      'Content-Type': 'application/json'
    }
  

    def http_get(self, path):
    url = "https://" + str(self.appliance_hostname) + path
    headers = make_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      raise response.text
    return response.json()
  

    def http_post(self, path, body):
    url = "https://" + str(self.appliance_hostname) + str(path)
    headers = make_headers()
    response = requests.post(url, data=body, headers=headers
    if response.status_code == 200 or response.status_code == 201:
      return response.json()
    raise response.txt
  

    def http_put(self, path, body):
    url = "https://" + str(self.appliance_hostname) + str(path)
    headers = make_headers()
    response = requests.put(url, data=body, headers=headers)
    if response.status_code != 204:
      raise response.text
    return response.json()
  

    def http_delete(self, path):
    url = "https://" + str(self.appliance_hostname) + str(path)
    headers = make_headers()
    response = requests.delete(url, headers=headers)
    if response.status_code != 204:
      raise response.text
    return response.json()
  

