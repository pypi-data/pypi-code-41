import BaseObject
class EventAction(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.id = None
    self.name = None
    self.status = None
    self.type = None
  def from_dict(self, d):
    if 'id' in d:
      self.id = d['%!s(MISSING)']
    if 'name' in d:
      self.name = d['%!s(MISSING)']
    if 'status' in d:
      self.status = d['%!s(MISSING)']
    if 'type' in d:
      self.type = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['id'] = self.id
    d['name'] = self.name
    d['status'] = self.status
    d['type'] = self.type
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
