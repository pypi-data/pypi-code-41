import BaseObject
class ConnectionManager(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.id = None
    self.hostname = None
    self.last_contact = None
  def from_dict(self, d):
    if 'id' in d:
      self.id = d['%!s(MISSING)']
    if 'hostname' in d:
      self.hostname = d['%!s(MISSING)']
    if 'last_contact' in d:
      self.last_contact = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['id'] = self.id
    d['hostname'] = self.hostname
    d['last_contact'] = self.last_contact
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
    def connection_manager_group(self):
    obj = self.http_get("/api/v2/connection_manager_groups/{connection_manager_group_id}.json")
    elem = ConnectionManagerGroup(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = obj["id"]
    elem.name = obj["name"]
    return elem
  

