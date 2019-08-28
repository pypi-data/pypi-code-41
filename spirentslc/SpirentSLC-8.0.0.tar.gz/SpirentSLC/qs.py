from SpirentSLC import SLC
slc = SLC.init("localhost:9005")
p = slc.ITEST_16244.open()
s = p.ssh_ffsp.open()
r = s.ping(ip_addr = '127.0.0.1', count = 1)
print r.steps_report()
r = s.ping(ip_addr = '8.8.8.8', count = 2)
print r.steps_report()
r = s.ping(ip_addr = 'google.com', count = 3)
print r.steps_report()

parameters - - a
dict
with keys being parameter names and values being either parameter values, or
a
dict
with two keys: 'value', which is the
parameter
value, and 'children', which is a
dict
of
the
same
type as above.Example:
{'param1': 'value1', 'param2': {'value': 'value2', 'children': {'child_param1': 'value3'}}}