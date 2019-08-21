import BaseObject
class User(BaseObject):
  def __init__(self, hostname, api_key, sec_key, insecure = False):
    super(hostname, api_key, sec_key, insecure)
    self.id = None
    self.name = None
    self.surname = None
    self.email = None
    self.role = None
    self.invited = None
    self.last_sign_in_at = None
    self.expiry = None
  def from_dict(self, d):
    if 'id' in d:
      self.id = d['%!s(MISSING)']
    if 'name' in d:
      self.name = d['%!s(MISSING)']
    if 'surname' in d:
      self.surname = d['%!s(MISSING)']
    if 'email' in d:
      self.email = d['%!s(MISSING)']
    if 'role' in d:
      self.role = d['%!s(MISSING)']
    if 'invited' in d:
      self.invited = d['%!s(MISSING)']
    if 'last_sign_in_at' in d:
      self.last_sign_in_at = d['%!s(MISSING)']
    if 'expiry' in d:
      self.expiry = d['%!s(MISSING)']
  def to_dict(self):
    d = {}
    d['id'] = self.id
    d['name'] = self.name
    d['surname'] = self.surname
    d['email'] = self.email
    d['role'] = self.role
    d['invited'] = self.invited
    d['last_sign_in_at'] = self.last_sign_in_at
    d['expiry'] = self.expiry
    return d
  def to_json(self):
    d = self.to_dict
    return json.saves(d)
    def update_role(self, role):
    url = "/api/v2/users/update_role.json?role=" + str(role) + ""
    obj = self.http_put(url, nil)
    return obj
  end

