# Test steps:
#  1. Connect to openhltest server and create a session.
#  2. Create and connect two back to back stc ports
#  3. Create devices under the port1 and port2 protocol stack: eth/vlan/vlan/ipv4
#  4. Create devices under the port1 and port2 protocol stack: eth/vlan/vlan/ipv6
#  5. Create bound streamblocks with Ipv4 and Ipv6 end points
#  6. Start and stop traffic on both ports.
#  7. Get and validate received statistics.
#  8. Disconnect ports and delete session.

import time
import sys, os
import json
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

#  step 2. create and connect ports
print('\n  step 2. create and connect ports\n')
port1 = config.Ports.create(Name='Ethernet1', Location=chassisip1)
port_handle1 = port1.Name
print("    port_handle1: %s\n" % port_handle1)

port2 = config.Ports.create(Name='Ethernet2', Location=chassisip2)
port_handle2 = port2.Name
print("    port_handle2: %s\n" % port_handle2)

print('\n  step 3. create devices under the port1, protocol stack: eth/vlan/vlan/ipv4.\n')
device_group_east_1 = config.DeviceGroups.create(Name = 'EastSideDevicegroup1', Ports = ['Ethernet1'])

# create devices: 'Devices 1' under the device_group_east and set device count
devices_1 = device_group_east_1.Devices.create(Name = 'Device1', DeviceCountPerPort = '2')

# create protocols ethernet
protocol_eth_1 = devices_1.Protocols.create(Name = 'Ethernet1', ProtocolType= 'ETHERNET')

# create protocols vlan outer
protocol_vlan_1 = devices_1.Protocols.create(Name = 'Vlan1', ProtocolType= 'VLAN', ParentLink = 'Ethernet1')

# create protocols vlan inner
protocol_vlan_2 = devices_1.Protocols.create(Name = 'Vlan2', ProtocolType= 'VLAN', ParentLink = 'Vlan1')

# create protocols IPv4
protocol_ipv4_1 = devices_1.Protocols.create(Name = 'IPV41', ProtocolType= 'IPV4', ParentLink = 'Vlan2')

# config mac addr with increment modifier
eth_1_mac = protocol_eth_1.Ethernet.Mac.update(PatternType='INCREMENT')
eth_1_mac_incr = eth_1_mac.Increment.update(Start = '00:10:94:00:00:01', Step = '00:00:00:00:00:01')

# config vlan outer
vlan_id_1 = protocol_vlan_1.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_1_incr = vlan_id_1.Increment.update(Start = '100', Step = '1')

vlan_pri_1 = protocol_vlan_1.Vlan.Priority.update(PatternType='SINGLE', Single = '7')

# config vlan inner

vlan_id_2 = protocol_vlan_2.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_2_incr = vlan_id_2.Increment.update(Start = '200', Step = '2')

vlan_pri_2 = protocol_vlan_2.Vlan.Priority.update(PatternType='SINGLE', Single = '7')

# config ipv4 source and gateway addresses

ipv4_1_src_addr = protocol_ipv4_1.Ipv4.SourceAddress.update(PatternType='SINGLE', Single = '192.85.1.3')
ipv4_1_gw_addr = protocol_ipv4_1.Ipv4.GatewayAddress.update(PatternType='SINGLE', Single = '192.85.1.13')

# get ipv4 source address value
print('\n    IPV4 1 source address : %s \n' % ipv4_1_src_addr.Single)


#  step 4. create two devices under the port2, protocol stack: eth/vlan/vlan/ipv4
print('\n  step 4. create two devices under the port2, protocol stack: eth/vlan/vlan/ipv4.\n')

# config device groups 'West Side - Device group 1' under the port 'Ethernet - 002'
device_group_west_1 = config.DeviceGroups.create(Name = 'WestSideDevicegroup1', Ports = ['Ethernet2'])

# create 'Device 2' under the device_group_west and set device count
devices_2 = device_group_west_1.Devices.create(Name = 'Device2', DeviceCountPerPort = '2')

# create protocols ethernet
protocol_eth_2 = devices_2.Protocols.create(Name = 'Ethernet2', ProtocolType= 'ETHERNET')

# create protocols vlan outer
protocol_vlan_3 = devices_2.Protocols.create(Name = 'Vlan3', ProtocolType= 'VLAN', ParentLink = 'Ethernet2')

# create protocols vlan inner
protocol_vlan_4 = devices_2.Protocols.create(Name = 'Vlan4', ProtocolType= 'VLAN', ParentLink = 'Vlan3')

# create protocols IPv4
protocol_ipv4_2 = devices_2.Protocols.create(Name = 'IPV42', ProtocolType= 'IPV4', ParentLink = 'Vlan4')

# config mac addr with increment modifier
eth_2_mac = protocol_eth_2.Ethernet.Mac.update(PatternType='INCREMENT')
eth_2_mac_incr = eth_2_mac.Increment.update(Start = '00:10:94:00:00:10', Step = '00:00:00:00:00:01')

# config vlan outer
vlan_id_3 = protocol_vlan_3.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_3_incr = vlan_id_3.Increment.update(Start = '100', Step = '1')
vlan_pri_3 = protocol_vlan_3.Vlan.Priority.update(PatternType='SINGLE', Single = '7')

# config vlan inner
vlan_id_4 = protocol_vlan_4.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_4_incr = vlan_id_4.Increment.update(Start = '200', Step = '2')
vlan_pri_4 = protocol_vlan_4.Vlan.Priority.update(PatternType='SINGLE', Single = '7')

# config ipv4 source and gateway addresses
ipv4_2_src_addr = protocol_ipv4_2.Ipv4.SourceAddress.update(PatternType='SINGLE', Single = '192.85.1.13')
ipv4_2_gw_addr = protocol_ipv4_2.Ipv4.GatewayAddress.update(PatternType='SINGLE', Single = '192.85.1.3')

# get ipv4 source address value
print('\n    IPV4 2 source address : %s \n' % ipv4_2_src_addr.Single)

print('\n  step 5. create two devices under the port1, protocol stack: eth/vlan/vlan/ipv6.\n')

device_group_east_2 = config.DeviceGroups.create(Name = 'EastSideDevicegroup2', Ports = ['Ethernet1'])

# create devices: 'Devices 1' under the device_group_east and set device count
devices_3 = device_group_east_2.Devices.create(Name = 'Device3', DeviceCountPerPort = '2')

# create protocols ethernet
protocol_eth_3 = devices_3.Protocols.create(Name = 'Ethernet3', ProtocolType= 'ETHERNET')

# create protocols vlan outer
protocol_vlan_5 = devices_3.Protocols.create(Name = 'Vlan5', ProtocolType= 'VLAN', ParentLink = 'Ethernet3')

# create protocols vlan inner
protocol_vlan_6 = devices_3.Protocols.create(Name = 'Vlan6', ProtocolType= 'VLAN', ParentLink = 'Vlan5')

# create protocols IPv6
protocol_ipv6_1 = devices_3.Protocols.create(Name = 'IPV61', ProtocolType= 'IPV6', ParentLink = 'Vlan6')

# config mac addr with increment modifier
eth_3_mac = protocol_eth_3.Ethernet.Mac.update(PatternType='INCREMENT')
eth_3_mac_incr = eth_3_mac.Increment.update(Start = '00:10:94:00:00:31', Step = '00:00:00:00:00:01')

# config vlan outer
vlan_id_5 = protocol_vlan_5.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_5_incr = vlan_id_5.Increment.update(Start = '100', Step = '1')

vlan_pri_5 = protocol_vlan_5.Vlan.Priority.update(PatternType='SINGLE', Single = '7')

# config vlan inner

vlan_id_6 = protocol_vlan_6.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_6_incr = vlan_id_6.Increment.update(Start = '200', Step = '2')

vlan_pri_6 = protocol_vlan_6.Vlan.Priority.update(PatternType='SINGLE', Single = '7')

# config ipv6 source and gateway addresses

ipv6_1_src_addr = protocol_ipv6_1.Ipv6.SourceAddress.update(PatternType='SINGLE', Single = '2000::10')
ipv6_1_gw_addr = protocol_ipv6_1.Ipv6.GatewayAddress.update(PatternType='SINGLE', Single = '2000::1')

# get ipv6 source address value
print('\n    IPV6 1 source address : %s \n' % ipv6_1_src_addr.Single)


print('\n  step 6. create two devices under the port2, protocol stack: eth/vlan/vlan/ipv6.\n')

# config device groups 'West Side - Device group 1' under the port 'Ethernet - 002'
device_group_west_2 = config.DeviceGroups.create(Name = 'WestSideDevicegroup2', Ports = ['Ethernet2'])

# create 'Device 2' under the device_group_west and set device count
devices_4 = device_group_west_2.Devices.create(Name = 'Device4', DeviceCountPerPort = '2')

# create protocols ethernet
protocol_eth_4 = devices_4.Protocols.create(Name = 'Ethernet4', ProtocolType= 'ETHERNET')

# create protocols vlan outer
protocol_vlan_7 = devices_4.Protocols.create(Name = 'Vlan7', ProtocolType= 'VLAN', ParentLink = 'Ethernet4')

# create protocols vlan inner
protocol_vlan_8 = devices_4.Protocols.create(Name = 'Vlan8', ProtocolType= 'VLAN', ParentLink = 'Vlan7')

# create protocols IPv6
protocol_ipv6_2 = devices_4.Protocols.create(Name = 'IPV62', ProtocolType= 'IPV6', ParentLink = 'Vlan8')

# config mac addr with increment modifier
eth_4_mac = protocol_eth_4.Ethernet.Mac.update(PatternType='INCREMENT')
eth_4_mac_incr = eth_4_mac.Increment.update(Start = '00:10:94:00:00:40', Step = '00:00:00:00:00:01')

# config vlan outer
vlan_id_7 = protocol_vlan_7.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_7_incr = vlan_id_7.Increment.update(Start = '100', Step = '1')
vlan_pri_7 = protocol_vlan_7.Vlan.Priority.update(PatternType='SINGLE', Single = '7')

# config vlan inner
vlan_id_8 = protocol_vlan_8.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_8_incr = vlan_id_8.Increment.update(Start = '200', Step = '2')
vlan_pri_8 = protocol_vlan_8.Vlan.Priority.update(PatternType='SINGLE', Single = '7')

# config ipv6 source and gateway addresses
ipv6_2_src_addr = protocol_ipv6_2.Ipv4.SourceAddress.update(PatternType='SINGLE', Single = '2000::1')
ipv6_2_gw_addr = protocol_ipv6_2.Ipv4.GatewayAddress.update(PatternType='SINGLE', Single = '2000::10')

# get ipv6 source address value
print('\n    IPV6 1 source address : %s \n' % ipv6_2_src_addr.Single)

print('\n  step 7. create bound streamblocks with Ipv4 and Ipv6 end points\n')
# create BOUND streamblock - IPv4 endpoints
device_traffic_1 = config.DeviceTraffic.create(Name = 'IPV4Stream1', Encapsulation = 'IPV4', Sources = ['IPV41'], Destinations = ['IPV42'], BiDirectional = 'true')

#Config Frame Size
frame_length_1 = device_traffic_1.FrameLength.update(LengthType = 'FIXED', Fixed = '512')

# create BOUND streamblock - IPv6 endpoints
device_traffic_2 = config.DeviceTraffic.create(Name = 'IPV6Stream1', Encapsulation = 'IPV6', Sources = ['Device3'], Destinations = ['Device4'], BiDirectional = 'true')

#Config Frame Size
frame_length_2 = device_traffic_2.FrameLength.update(LengthType = 'FIXED', Fixed = '256')

print('\n    save config in xml/json format.\n')
filename = __file__.split(os.path.sep)[-1].partition('.')[0] #strip filename from absolute file path and file extension
#SaveAsxml
saved_xml_file = os.path.join(os.path.dirname(__file__), filename + '_saved.xml')
config.Save({'mode': 'VENDOR_BINARY', 'file-name': saved_xml_file})
#Save json file
saved_json_file = os.path.join(os.path.dirname(__file__), filename + '_saved.json')
config.Save({'mode': 'RESTCONF_JSON', 'file-name': saved_json_file})
content_dict={}
with open(saved_json_file, 'r') as f:
    content_dict = json.load( f)
if len(content_dict['openhltest:config']['ports']) != 2:
    print('\n port number should be 2 in saved json file.\n')
    exit(1)

print('\n    load json config and reserve ports.\n')
config.Load({'mode': 'RESTCONF_JSON', 'file-name': saved_json_file})
ports = config.Ports.read()
if len(ports) != 2:
    print('\n port number should be 2 after loading json config file.\n')
    exit(1)
config.PortControl({"targets": [], "mode": 'CONNECT'})

print('\n  step 8. Start Traffic \n')
# Start traffic
config.TrafficControl( {"targets": ['IPV4Stream1' , 'IPV6Stream1'], "mode": 'START'})

print('    wait for 5 seconds..\n')
time.sleep(5)

print('\n  step 9. Stop Traffic \n')
# Stop traffic
config.TrafficControl( {"targets": ['IPV4Stream1' , 'IPV6Stream1'], "mode": 'STOP'})

#  Get the traffic statistics
print('\n  step 10. Get traffic statistics\n')
statistics = session.Statistics
traffic_statistics_1 = statistics.DeviceTraffic.read( Name = 'IPV4Stream1')

tx_stats = traffic_statistics_1.TxFrames
rx_stats = traffic_statistics_1.RxFrames

if (tx_stats == rx_stats):
    print("    Received Ipv4 traffic successfully. Number of Rx and Tx frames are matched\n")
    print("    TxFrames: %s" % traffic_statistics_1.TxFrames)
    print("    RxFrames: %s\n" % traffic_statistics_1.RxFrames)
else :
    print("    <error>: Failed to receive traffic. Mismatch in Rx and Tx frames\n")
    print(traffic_statistics_1)

traffic_statistics_2 =  statistics.DeviceTraffic.read( Name = 'IPV6Stream1')

tx_stats = traffic_statistics_2.TxFrames
rx_stats = traffic_statistics_2.RxFrames

if (tx_stats == rx_stats):
    print("    Received Ipv6 traffic successfully. Number of Rx and Tx frames are matched\n")
    print("    TxFrames: %s" % traffic_statistics_2.TxFrames)
    print("    RxFrames: %s\n" % traffic_statistics_2.RxFrames)
else :
    print("    <error>: Failed to receive traffic. Mismatch in Rx and Tx frames\n")
    print(traffic_statistics_2)

#disconnect ports
print('\n  step 11. Disconnect ports and delete session\n')
port_control_input = config.PortControl({"targets": [port_handle1, port_handle2], "mode": 'DISCONNECT'})

session.delete()
try:
    session = openhltest.Sessions.read(Name = sessionname)
except:
    print("    Deleted session - %s\n" % sessionname)
