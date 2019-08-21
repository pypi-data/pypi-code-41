import BaseObject
class Environment(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.id = None
    self.name = None
    self.organisation_id = None
    self.short_description = None
  def from_dict(self, d):
    if 'id' in d:
      self.id = d['%!s(MISSING)']
    if 'name' in d:
      self.name = d['%!s(MISSING)']
    if 'organisation_id' in d:
      self.organisation_id = d['%!s(MISSING)']
    if 'short_description' in d:
      self.short_description = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['id'] = self.id
    d['name'] = self.name
    d['organisation_id'] = self.organisation_id
    d['short_description'] = self.short_description
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
    def load(self):
    obj = self.http_get("/api/v2/environments/{id}.json")
    from_hash(obj)
  

    def save(self):
    if self.id == 0 or self.id == None:
      return self.create()
    else:
      return self.update()
  

    def create(self):
    d = self.to_dict()
    out = self.http_post("/api/v2/environments.json", d)
    self.from_dict(out)
  

    def update(self):
    d = self.to_dict()
    del d["id"]
    del d["organisation_id"]
    self.http_put("/api/v2/environments/{id}.json", d)
  

    def delete(self):
    self.http_delete("/api/v2/environments/{id}.json")
  

    def nodes(self):
    obj = http_get("/api/v2/environments/{id}/nodes.json")
    list = []
    for x in obj:
      elem = Node(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      list.append(elem)
    return list
  

