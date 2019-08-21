import BaseObject
class Event(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.id = None
    self.type_id = None
    self.environment_id = None
    self.created_at = None
  def from_dict(self, d):
    if 'id' in d:
      self.id = d['%!s(MISSING)']
    if 'type_id' in d:
      self.type_id = d['%!s(MISSING)']
    if 'environment_id' in d:
      self.environment_id = d['%!s(MISSING)']
    if 'created_at' in d:
      self.created_at = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['id'] = self.id
    d['type_id'] = self.type_id
    d['environment_id'] = self.environment_id
    d['created_at'] = self.created_at
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
    def environment(self):
    obj = self.http_get("/api/v2/environments/" + str(self.environment_id) + ".json")
    elem = Environment(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = obj["id"]
    elem.name = obj["name"]
    elem.organisation_id = obj["organisation_id"]
    elem.short_description = obj["short_description"]
    elem.node_rules = obj["node_rules"]
    return elem
  

