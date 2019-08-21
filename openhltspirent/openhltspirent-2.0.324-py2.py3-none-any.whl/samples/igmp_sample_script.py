# test stpes:
#  1. create and connect two ports

from openhltspirent.httptransport import HttpTransport
import time
import sys, os
import json

#Commandline arguments
serverip=sys.argv[1]
portnumber=sys.argv[2]
sessionname=sys.argv[3]
chassisip1=sys.argv[4]
chassisip2=sys.argv[5]

print("ohtweb server ip", serverip)
print("chassis ip: %s, %s" % (chassisip1, chassisip2))
    
print("session name", sessionname)
print("portnumber",portnumber)

# connect openhltest server
LOG_TO_FILE = True
if True == LOG_TO_FILE:
    log_file = '.'.join(__file__.split(os.path.sep)[-1].split('.')[0:-1]) + ".log"
else:
    log_file = None
transport = HttpTransport(serverip + ":" + portnumber, log_file_name= log_file)
transport.set_debug_level()
openhltest = transport.OpenHlTest

try:
    session = openhltest.Sessions.read(Name = sessionname)
    session.delete()
    print("######## Deleted existing session with name %s ######### \n" % sessionname)
except:
    print("######## There is no session exist with name %s ######## \n" % sessionname)

# create session : "SampleTest"
session = openhltest.Sessions.create(Name = sessionname)

#  step 1. create and connect one ports
print('\n  step 1. create and connect one ports\n')
config = session.Config

port1 = config.Ports.create(Name='Eth1', Location=chassisip1)

#  step 2. create global multicast group
print('\n  step 2. create global multicast group\n')
global_multicast_groups = config.GlobalMulticastGroups.create(Name='globalmulticastgroupconfig1')
multicast_groups = global_multicast_groups.MulticastGroups.create(Name='Ipv4Group1', NumberOfGroups=1, GroupType='IPV4')

ipv4_group = multicast_groups.Ipv4Group
address = ipv4_group.Address.update( PatternType='INCREMENT')
address.Increment.update(Start='225.0.0.1', Step='1', Count='100')

#  step 3. create one devices under the port1, protocol stack: eth/vlan/vlan/ipv4/dhcpv4. 
print('\n  step 3. create two devices under the port1, protocol stack: eth/ipv4/dhcpv4.\n')
# create device groups: 'Device group 1' under the port 'Eth1'
device_group_1 = config.DeviceGroups.create(Name='DeviceGroup1', Ports=['Eth1'])

# create devices: 'Devices 1' under the device_group_east
devices_1 = device_group_1.Devices.create(Name ='Device1', DeviceCountPerPort=1)

# create protocols ethernet
protocol_eth_1 = devices_1.Protocols.create(Name = 'EthIf', ProtocolType='ETHERNET')

# create protocols IPv4
protocol_ipv4_1 = devices_1.Protocols.create(Name = 'IPv4If', ParentLink='EthIf', ProtocolType='IPV4')

# config mac addr
protocol_eth_1.Ethernet.Mac.update( PatternType='SINGLE', Single='00:10:94:00:00:02')

# config ipv4 address
ipv4_1 = protocol_ipv4_1.Ipv4
ipv4_1.SourceAddress.update( PatternType='SINGLE', Single='10.10.10.2')
ipv4_1.GatewayAddress.update( PatternType='SINGLE', Single='10.10.10.1')

#create and config IGMP client protocol
protocol_igmp_1 = devices_1.Protocols.create(Name = 'IGMP_1', ParentLink='IPv4If', ProtocolType='IGMP')

igmp_1 = protocol_igmp_1.Igmp.update(MulticastGroup = ['Ipv4Group1'])

version = igmp_1.Version.update( PatternType='SINGLE', Single='IGMP_V1')

force_leave = igmp_1.ForceLeave.update( PatternType='SINGLE', Single='true')

print('\n    save config in json format.\n')
filename = __file__.split(os.path.sep)[-1].partition('.')[0] #strip filename from absolute file path and file extension
#Save json file
saved_json_file = os.path.join(os.path.dirname(__file__), filename + '_saved.json')
config.Save({'mode': 'RESTCONF_JSON', 'file-name': saved_json_file})
content_dict={}
with open(saved_json_file, 'r') as f:
    content_dict = json.load( f)
if len(content_dict['openhltest:config']['ports']) != 1:
    print('\n port number should be 1 in saved json file.\n')
    exit(1)

print('\n    load json config and reserve ports.\n')
config.Load({'mode': 'RESTCONF_JSON', 'file-name': saved_json_file})
ports = config.Ports.read()
if len(ports) != 1:
    print('\n port number should be 1 after loading json config file.\n')
    exit(1)
config.PortControl({"targets": [], "mode": 'CONNECT'})

#  step 4. start igmp
print('\n  step 4. start igmp protocol\n')
igmp_control_input = config.IgmpControl(input={
    "calculate-latency": "false", 
    "join-leave-delay": "0", 
    "rx-data-duration": "10", 
    "join-failed-retry-counter": "0", 
    "mode": "JOIN", 
    "targets": ["IGMP_1"]})

time.sleep(10)

#  step 5. Get the igmp statistics
print('\n  step 5. Get the IGMP statistics\n')
statistics = session.Statistics
igmp_statistics = statistics.IgmpStatistics.read(DeviceName = 'Device1')
print(igmp_statistics)

if (igmp_statistics.TxFrameCount == 200) :
    print('*' * 40)
    print ("\n Info :IGMP session bind successful \n")
    print('*' * 40)
else :
    print ("\n <error> Failed to bind IGMP session \n")

#  step 6. disconnect ports
print('\n  step 6. Disconnect ports\n')
port_control_input = config.PortControl( input={"targets": ['Eth1'], "mode": 'DISCONNECT'})

print('\n  step 7. delete session\n')
session.delete()
