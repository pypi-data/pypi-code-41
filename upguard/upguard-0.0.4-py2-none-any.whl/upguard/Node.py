import BaseObject
class Node(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.connection_manager_group_id = None
    self.environment_id = None
    self.external_id = None
    self.hostname = None
    self.id = None
    self.medium_hostname = None
    self.medium_type = None
    self.name = None
    self.node_type = None
    self.operating_system_family_id = None
    self.operating_system_id = None
  def from_dict(self, d):
    if 'connection_manager_group_id' in d:
      self.connection_manager_group_id = d['%!s(MISSING)']
    if 'environment_id' in d:
      self.environment_id = d['%!s(MISSING)']
    if 'external_id' in d:
      self.external_id = d['%!s(MISSING)']
    if 'hostname' in d:
      self.hostname = d['%!s(MISSING)']
    if 'id' in d:
      self.id = d['%!s(MISSING)']
    if 'medium_hostname' in d:
      self.medium_hostname = d['%!s(MISSING)']
    if 'medium_type' in d:
      self.medium_type = d['%!s(MISSING)']
    if 'name' in d:
      self.name = d['%!s(MISSING)']
    if 'node_type' in d:
      self.node_type = d['%!s(MISSING)']
    if 'operating_system_family_id' in d:
      self.operating_system_family_id = d['%!s(MISSING)']
    if 'operating_system_id' in d:
      self.operating_system_id = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['connection_manager_group_id'] = self.connection_manager_group_id
    d['environment_id'] = self.environment_id
    d['external_id'] = self.external_id
    d['hostname'] = self.hostname
    d['id'] = self.id
    d['medium_hostname'] = self.medium_hostname
    d['medium_type'] = self.medium_type
    d['name'] = self.name
    d['node_type'] = self.node_type
    d['operating_system_family_id'] = self.operating_system_family_id
    d['operating_system_id'] = self.operating_system_id
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
    def load(self):
    obj = self.http_get("/api/v2/nodes/{id}.json")
    from_hash(obj)
  

    def save(self):
    if self.id == 0 or self.id == None:
      return self.create()
    else:
      return self.update()
  

    def create(self):
    d = self.to_dict()
    out = self.http_post("/api/v2/nodes.json", d)
    self.from_dict(out)
  

    def update(self):
    d = self.to_dict()
    del d["id"]
    self.http_put("/api/v2/nodes/{id}.json", d)
  

    def delete(self):
    self.http_delete("/api/v2/nodes/{id}.json")
  

    def connection_manager_group(self):
    obj = self.http_get("/api/v2/connection_manager_groups/{connection_manager_group_id}.json")
    elem = ConnectionManagerGroup(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = obj["id"]
    elem.name = obj["name"]
    return elem
  

    def environment(self):
    obj = self.http_get("/api/v2/environments/" + str(self.environment_id) + ".json")
    elem = Environment(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = obj["id"]
    elem.name = obj["name"]
    return elem
  

    def operating_system(self):
    obj = self.http_get("/api/v2/operating_systems/{operating_system_id}.json")
    elem = OperatingSystem(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = obj["id"]
    elem.name = obj["name"]
    return elem
  

    def operating_system_family(self):
    obj = self.http_get("/api/v2/operating_system_families/{operating_system_family_id}.json")
    elem = OperatingSystemFamily(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = obj["id"]
    elem.name = obj["name"]
    return elem
  

    def start_scan(self, ):
    url = "/api/v2/nodes/{id}/start_scan.json"
    obj = http_post(url, None)
    return obj
  

