def assert_equal(expected, actual):
  if expected == actual:
    print "PASS"
  else:
    print "FAIL"
    print "  Expected: " + str(expected)
    print "  Actual  : " + str(actual)
    print ""

def assert_not_equal(expected, actual):
  if expected != actual:
    print "PASS"
  else:
    print "FAIL"
    print "  Expected: " + str(expected)
    print "  Actual  : " + str(actual)
    print ""

def assert_includes(haystack, needle):
  if needle in haystack:
    print "PASS"
  else:
    print "FAIL"
    print "Haystack: " + str(haystack)
    print "Needle  : " + str(needle)
    print ""


from upguard import *

hostname = None
api_key = None
sec_key = None
fh = open("api-creds.txt", "r")
lines = fh.readlines()
re_hostname = re.compile(r"^hostname (\S+)\s*$")
re_api_key = re.compile(r"^api_key (\S+)\s*$")
re_sec_key = re.compile(r"^sec_key (\S+)\s*$")
for line in lines:
  m_hostname = re_hostname.search(line)
  if m_hostname != None:
    hostname = m.group(1)
  m_api_key = re_api_key.search(line)
  if m_api_key != None:
    api_key = m.group(1)
  m_sec_key = re_sec_key.search(line)
  if m_sec_key != None:
    sec_key = m.group(1)
o = Account(hostname, api_key, sec_key)


list = o.connection_managers()
for x in list:
  print x.hostname


list = o.connection_manager_groups()
for x in list:
  print x.name


list = o.environments()
for x in list:
  print x.name


list = o.event_actions()
for x in list:
  print x.name


list = o.nodes()
for x in list:
  print x.name


list = o.node_groups()
for x in list:
  print x.name


list = o.system_metrics()
for x in list:
  print x.value


list = o.users()
for x in list:
  print x.name


all = o.nodes()
for x in all:
  if x.name == "New Node From SDK":
    v.delete()


x = o.new_node()
x.name = "New Node From SDK"
assert_true(x.id == 0 or x.id == None)
x.save()
assert_false(x.id == 0 or x.id == None)
assert_true(typeof(x.id) is int)
x.load()
x.node_type = "RB"
x.save()
x.delete()

all = o.environments()
for x in all:
  if x.name == "New Environment From SDK":
    v.delete()


x = o.new_environment()
x.name = "New Environment From SDK"
assert_true(x.id == 0 or x.id == None)
x.save()
assert_false(x.id == 0 or x.id == None)
assert_true(typeof(x.id) is int)
x.load()
x.short_description = "new short description"
x.save()
x.delete()

