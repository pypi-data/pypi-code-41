import BaseObject
class Account(BaseObject):
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
    def connection_managers(self):
    obj = http_get("/api/v2/connection_managers.json")
    list = []
    for x in obj:
      elem = ConnectionManager(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.hostname = x["hostname"]
      elem.last_contact = x["last_contact"]
      list.append(elem)
    return list
  

    def connection_manager_groups(self):
    obj = http_get("/api/v2/connection_manager_groups.json")
    list = []
    for x in obj:
      elem = ConnectionManagerGroup(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      list.append(elem)
    return list
  

    def new_environment(self):
    return Environment(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
  

    def environments(self):
    obj = http_get("/api/v2/environments.json")
    list = []
    for x in obj:
      elem = Environment(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      list.append(elem)
    return list
  

    def events_with_view_name(self, view_name):
    url = "/api/v2/events.json%!!(MISSING)S(string=?view_name=" + str(view_name) + ")"
    obj = http_get(url)
    list = []
    for x in list:
      elem = Event(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.type_id = x["type_id"]
      elem.environment_id = x["environment_id"]
      elem.created_at = x["created_at"]
      list.append(elem)
    return list
  

    def events_with_query(self, query):
    url = "/api/v2/events.json%!!(MISSING)S(string=?query=" + str(query) + ")"
    obj = http_get(url)
    list = []
    for x in list:
      elem = Event(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.type_id = x["type_id"]
      elem.environment_id = x["environment_id"]
      elem.created_at = x["created_at"]
      list.append(elem)
    return list
  

    def event_actions(self):
    obj = http_get("/api/v2/event_actions.json")
    list = []
    for x in obj:
      elem = EventAction(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      elem.status = x["status"]
      elem.type = x["type"]
      list.append(elem)
    return list
  

    def incidents(self):
    obj = http_get("/api/v2/incidents.json")
    list = []
    for x in obj:
      elem = Incident(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.external_id = x["external_id"]
      elem.short_description = x["short_description"]
      elem.started_at = x["started_at"]
      elem.ended_at = x["ended_at"]
      elem.url = x["url"]
      list.append(elem)
    return list
  

    def jobs(self):
    obj = http_get("/api/v2/jobs.json")
    list = []
    for x in obj:
      elem = Job(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.organisation_id = x["organisation_id"]
      elem.source_id = x["source_id"]
      elem.source_type = x["source_type"]
      elem.status = x["status"]
      list.append(elem)
    return list
  

    def new_node(self):
    return Node(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
  

    def nodes(self):
    obj = http_get("/api/v2/nodes.json")
    list = []
    for x in obj:
      elem = Node(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      elem.external_id = x["external_id"]
      elem.environment_id = x["environment_id"]
      elem.operating_system_family_id = x["operating_system_family_id"]
      elem.operating_system_id = x["operating_system_id"]
      list.append(elem)
    return list
  

    def node_groups(self):
    obj = http_get("/api/v2/node_groups.json")
    list = []
    for x in obj:
      elem = Node(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      list.append(elem)
    return list
  

    def operating_system_families(self):
    obj = http_get("/api/v2/operating_system_families.json")
    list = []
    for x in obj:
      elem = OperatingSystemFamily(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      list.append(elem)
    return list
  

    def operating_systems(self):
    obj = http_get("/api/v2/operating_systems.json")
    list = []
    for x in obj:
      elem = OperatingSystem(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      elem.operating_system_family_id = x["operating_system_family_id"]
      list.append(elem)
    return list
  

    def system_metrics(self):
    obj = http_get("/api/v2/system_metrics.json")
    list = []
    for x in obj:
      elem = SystemMetric(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.metric = x["metric"]
      elem.value = x["value"]
      elem.timestamp = x["timestamp"]
      list.append(elem)
    return list
  

    def users(self):
    obj = http_get("/api/v2/users.json")
    list = []
    for x in obj:
      elem = User(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
      elem.id = x["id"]
      elem.name = x["name"]
      elem.surname = x["surname"]
      elem.email = x["email"]
      elem.role = x["role"]
      list.append(elem)
    return list
  

    def invite_user(self, email, role):
    url = "/api/v2/users/invite.json?email=" + str(email) + "&role=" + str(role) + ""
    obj = http_post(url, None)
    return obj
  

    def find_node_by_external_id(self, external_id):
    url = "/api/v2/nodes/lookup.json?external_id=" + str(external_id) + ""
    obj = http_get(url)
    id = obj["node_id"]
    elem = Node(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = id
    elem.load()
    return elem
  

    def find_node_by_name(self, name):
    url = "/api/v2/nodes/lookup.json?name=" + str(name) + ""
    obj = http_get(url)
    id = obj["node_id"]
    elem = Node(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.id = id
    elem.load()
    return elem
  

    def find_node_by_id(self, id):
    url = /api/v2/nodes/{id}.json?id=" + str(id) + "
    obj = http_get(url)
    elem = Node(self.appliance_hostname, self.api_key, self.sec_key, self.insecure)
    elem.from_hash(obj)
    return elem

