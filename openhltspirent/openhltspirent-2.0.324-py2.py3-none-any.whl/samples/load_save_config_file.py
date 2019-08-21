import os,sys
from openhltspirent.httptransport import HttpTransport

#Commandline arguments
serverip=sys.argv[1]
portnumber=sys.argv[2]
sessionname=sys.argv[3]
chassisip1=sys.argv[4]
chassisip2=sys.argv[5]

print("ohtweb server ip", serverip)
print("chassis ip", chassisip1, chassisip2)
print("session name", sessionname)
print("portnumber",portnumber)

print("ohtweb server ip", serverip)
print("chassis ip: %s, %s" % (chassisip1, chassisip2))
    
print("session name", sessionname)
print("portnumber",portnumber)

# connect openhltest server
LOG_TO_FILE = True
if True == LOG_TO_FILE:
    log_file = '.'.join(__file__.split(os.path.sep)[-1].split('.')[0:-1]) + ".log"
    print("\n  Check %s for detailed console log \n" % log_file)
else:
    # Log to standard console
    log_file = None
transport = HttpTransport(serverip + ":" + portnumber, log_file_name= log_file)
transport.set_debug_level()
openhltest = transport.OpenHlTest

print('\n  step 1. create a session\n')
try:
    session = openhltest.Sessions.read(Name = sessionname)
    session.delete()
    print("    ######## Deleted existing session with name %s ######### \n" % sessionname)
except:
    print("    ######## There is no session exist with name %s ######## \n" % sessionname)

# create session : "SampleTest"
session = openhltest.Sessions.create(Name = sessionname)
config = session.Config
print("    Created new session - %s" % sessionname)

def validate_ports(expected_portnames):
    ports = config.Ports.read()
    ports_name = []
    for port in ports:
        ports_name.append(port.Name)
    if ports_name != expected_portnames:
        session.delete()
        raise Exception("Expected port names: %s, but got %s" %(expected_portnames, ports_name))

# import os
config.Load({'mode': "RESTCONF_JSON", 'file-name': os.path.join(os.path.dirname(__file__), "config1.json")})
out = config.Save({'mode': "VENDOR_BINARY", 'file-name': os.path.join(os.path.dirname(__file__), "config1_saved.xml")})
out = config.Save({'mode': "RESTCONF_JSON", 'file-name': os.path.join(os.path.dirname(__file__), "config1_saved.json")})
expected_portnames = ['Port_A', 'Port_2']
validate_ports(expected_portnames)

config.Load({'mode': "RESTCONF_JSON", 'file-name': os.path.join(os.path.dirname(__file__), "config.json")})
out = config.Save({'mode': "VENDOR_BINARY", 'file-name': os.path.join(os.path.dirname(__file__), "config_saved.xml")})
out = config.Save({'mode': "RESTCONF_JSON", 'file-name': os.path.join(os.path.dirname(__file__), "config_saved.json")})
expected_portnames = ['Port_1', 'Port_2']
validate_ports(expected_portnames)

session.delete()
