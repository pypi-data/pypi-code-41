import BaseObject
class OperatingSystemFamily(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.id = None
    self.name = None
  def from_dict(self, d):
    if 'id' in d:
      self.id = d['%!s(MISSING)']
    if 'name' in d:
      self.name = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['id'] = self.id
    d['name'] = self.name
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
    def operating_systems(self):
    obj = http_get("/api/v2/operating_system_families/{id}/operating_systems.json")
    list = []
    for x in obj:
      elem = OperatingSystem(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      list.append(elem)
    return list
  

