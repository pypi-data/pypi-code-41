'''The script does the following:
	- loads a vendor binary configuration
	- connects abstract ports to test ports
	- starts protocols
	- starts traffic
	- waits until traffic is complete
	- prints out port and traffic statistics

Vendor configuration details:
	- Ports:
		- 2 ethernet ports at a line speed of 1G
	- Protocols:
		- each port will have ethernet + ipv4 + bgpv4
	- Traffic:
		- one traffic item
		- traffic mesh of one to one, port1 -> port2
		- fixed frame size of 128 byte
		- 1,000,000 frames sent over 10 seconds at a rate of 100,000
'''
import time
import sys, os
from openhltspirent.httptransport import HttpTransport

serverip=sys.argv[1]
portnumber=sys.argv[2]
sessionname=sys.argv[3]

OPENHLTEST_SERVER = serverip + ':' + portnumber
VENDOR_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'demo_config.xml')

#transport = HttpTransport()
LOG_TO_FILE = False
if True == LOG_TO_FILE:
	log_file = os.path.join(os.path.dirname(__file__), 'demo.log')
else:
	log_file = None
transport = HttpTransport(OPENHLTEST_SERVER, log_file_name=log_file)
transport.set_debug_level()

transport.info("get an instance of the OpenHlTest module class")
openhltest = transport.OpenHlTest

transport.info("get a list of Sessions")
try:
    session = openhltest.Sessions.read(Name = sessionname)
    session.delete()
    print("######## Deleted existing session with name %s ######### \n" % sessionname)
except:
    print("######## There is no session exist with name %s ######## \n" % sessionname)

# create session : "SampleTest"
session = openhltest.Sessions.create(Name = sessionname)

transport.info("get an instance of the Config class")
config = session.Config

# import os
# out = config.Save({'mode': "VENDOR_BINARY", 'file-name': os.path.join(os.path.dirname(__file__), "stc_config.xml")})
# config.Load({'mode': "RESTCONF_JSON", 'file-name': os.path.join(os.path.dirname(__file__), "stc_config.xml")})

transport.info("load a vendor specific binary configuration")
config.Load({'mode': 'VENDOR_BINARY', 'file-name': VENDOR_CONFIG_FILE})

config.Save({'mode': 'VENDOR_BINARY', 'file-name': os.path.join(os.path.dirname(__file__), 'demo_saved_config.xml')})

transport.info("connect the abstract ports to test ports")
output = config.PortControl({"mode": "CONNECT", "targets": []})
transport.info('output: %s' % output)

transport.info("start the device-groups")
output = config.DeviceGroupsControl({"mode": "START", "targets": []})
transport.info('output: %s' % output)

transport.info("start the device-traffic")
output = config.TrafficControl({"mode": "START", "targets": []})
transport.info('output: %s' % output)

time.sleep(15)

transport.info("port statistics")
for port in session.Statistics.Port.read():
	transport.info('%s tx-frames:%s rx-frames:%s' % (port.Name, port.TxFrames, port.RxFrames))

transport.info("device-traffic statistics")
for device_traffic in session.Statistics.DeviceTraffic.read():
	transport.info('%s tx-frames:%s rx-frames:%s' % (device_traffic.Name, device_traffic.TxFrames, device_traffic.RxFrames))

print ("delete session %s" % sessionname)
session.delete()