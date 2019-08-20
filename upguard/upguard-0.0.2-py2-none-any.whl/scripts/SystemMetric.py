import BaseObject
class SystemMetric(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.metric = None
    self.value = None
    self.timestamp = None
  def from_dict(self, d):
    if 'metric' in d:
      self.metric = d['%!s(MISSING)']
    if 'value' in d:
      self.value = d['%!s(MISSING)']
    if 'timestamp' in d:
      self.timestamp = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['metric'] = self.metric
    d['value'] = self.value
    d['timestamp'] = self.timestamp
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
