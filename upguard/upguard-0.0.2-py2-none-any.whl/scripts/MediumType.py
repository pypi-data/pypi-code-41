import BaseObject
class MediumType(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
  def from_dict(self, d):
  def to_dict(self):
    d = {}
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
