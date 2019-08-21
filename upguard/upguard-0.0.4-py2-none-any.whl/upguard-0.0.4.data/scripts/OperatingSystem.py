import BaseObject
class OperatingSystem(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.description = None
    self.id = None
    self.name = None
    self.operating_system_family_id = None
  def from_dict(self, d):
    if 'description' in d:
      self.description = d['%!s(MISSING)']
    if 'id' in d:
      self.id = d['%!s(MISSING)']
    if 'name' in d:
      self.name = d['%!s(MISSING)']
    if 'operating_system_family_id' in d:
      self.operating_system_family_id = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['description'] = self.description
    d['id'] = self.id
    d['name'] = self.name
    d['operating_system_family_id'] = self.operating_system_family_id
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
    def operating_system_family(self):
    obj = self.http_get("/api/v2/operating_system_families/{operating_system_family_id}.json")
    elem = OperatingSystemFamily(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = obj["id"]
    elem.name = obj["name"]
    return elem
  

