## Test Steps:
    #Step 1: Create a session and connect to two back to back stc ports
    #Step 2: Configue 2 isisv4 devices on each port
    #Step 3: Configure 2 isisv4 routes one each isis device
    #Step 4: Configure traffic group between two isis devices
    #Step 5: Save the configuration as an XML file
    #Step 6: Start the isis devices
    #Step 7: Start the traffic
    #Step 8: Validate the isis stats
    #Step 7: Validate the traffic stats
    #Step 8: Delete session and release resources

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

#  step 3. create a device under the port1, protocol stack: eth/vlan/vlan/ipv4/isisv4. 
print('\n  step 3. create a device under port1, protocol stack: eth/vlan/vlan/ipv4/isisv4.\n')
# create device groups: 'East Side - Device group 1' under the port 'Ethernet - 001'
device_group_east_1 = config.DeviceGroups.create(Name = 'EastSideDevicegroup1', Ports = [port_handle1])

# create devices: 'Devices 1' under the device_group_east and set device count
devices_1 = device_group_east_1.Devices.create(Name = 'Device1', DeviceCountPerPort = '1')

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

# config ipv4 source and gateway addresses

ipv4_1_src_addr = protocol_ipv4_1.Ipv4.SourceAddress.update(PatternType='SINGLE', Single = '192.85.1.3')
ipv4_1_gw_addr = protocol_ipv4_1.Ipv4.GatewayAddress.update(PatternType='SINGLE', Single = '192.85.1.13')

#create and config ISISv4 protocol
protocol_isisv4_1 = devices_1.Protocols.create(Name = 'ISISV41', ProtocolType = 'ISIS', ParentLink = 'IPV41')
Isis_handle1 = protocol_isisv4_1.Name
print("    Isis_handle1: %s\n" % protocol_isisv4_1.Name)
isis = protocol_isisv4_1.Isis
system_id = isis.SystemId.update(PatternType = 'SINGLE', Single = '00:10:94:00:00:01')
router_priority = isis.RouterPriority.update(PatternType = 'SINGLE', Single = '1')
network_type = isis.NetworkType.update(PatternType = 'SINGLE', Single = 'BROADCAST')
hello_interval = isis.HelloInterval.update(PatternType = 'SINGLE', Single = '10')
level = isis.Level.update(PatternType = 'SINGLE', Single = 'L2')

#ISISv4 route creation on ISISv4 device
simulated_networks_1 = device_group_east_1.SimulatedNetworks.create(Name = 'SimulatedNetworks1', ParentLink = 'Device1')

# create 'ISISV4 Route Range' under the simulated_networks_1
networks_1 = simulated_networks_1.Networks.create(Name = 'ISISV4Networks1', FlowLink = 'ISISV41', NetworkType = 'ISIS_ROUTE_RANGE')

#config the isisv4_route_range_1
isisv4_route_range_1 = networks_1.IsisRouteRange  

system_id_route = isisv4_route_range_1.SystemId.update(PatternType = 'SINGLE', Single = '00:10:94:00:10:01')
isisv4_routes1 = isisv4_route_range_1.Ipv4Routes.create(Name = 'isisv4route1')
address = isisv4_routes1.Address.update(PatternType = 'SINGLE', Single = '192.0.1.0')

#  step 4. create a device under the port2, protocol stack: eth/vlan/vlan/ipv4/isisv4. 
print('\n  step 4. create a device under port2, protocol stack: eth/vlan/vlan/ipv4/isisv4.\n')

# create device groups: 'East Side - Device group 1' under the port 'Ethernet - 001'
device_group_west_1 = config.DeviceGroups.create(Name = 'WestSideDevicegroup1', Ports = [port_handle2])

# create devices: 'Devices 1' under the device_group_east and set device count
devices_2 = device_group_west_1.Devices.create(Name = 'Device2', DeviceCountPerPort = '1')

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
eth_2_mac_incr = eth_2_mac.Increment.update(Start = '00:10:94:00:10:01', Step = '00:00:00:00:00:01')

# config ipv4 source and gateway addresses

ipv4_2_src_addr = protocol_ipv4_2.Ipv4.SourceAddress.update(PatternType='SINGLE', Single = '192.85.1.13')
ipv4_2_gw_addr = protocol_ipv4_2.Ipv4.GatewayAddress.update(PatternType='SINGLE', Single = '192.85.1.3')

#create and config ISISv4 protocol
protocol_isisv4_2 = devices_2.Protocols.create(Name = 'ISISV42', ProtocolType = 'ISIS', ParentLink = 'IPV42')
Isis_handle2 = protocol_isisv4_2.Name
print("    Isis_handle2: %s\n" % protocol_isisv4_2.Name)
isis = protocol_isisv4_2.Isis
system_id = isis.SystemId.update(PatternType = 'SINGLE', Single = '00:20:94:00:00:01')
router_priority = isis.RouterPriority.update(PatternType = 'SINGLE', Single = '1')
network_type = isis.NetworkType.update(PatternType = 'SINGLE', Single = 'BROADCAST')
hello_interval = isis.HelloInterval.update(PatternType = 'SINGLE', Single = '10')
level = isis.Level.update(PatternType = 'SINGLE', Single = 'L2')

#ISISv4 route creation on ISISv4 device
simulated_networks_2 = device_group_west_1.SimulatedNetworks.create(Name = 'SimulatedNetworks2', ParentLink = 'Device2')

# create 'ISISV4 Route Range' under the simulated_networks_1
networks_2 = simulated_networks_2.Networks.create(Name = 'ISISV4Networks2', FlowLink = 'ISISV42', NetworkType = 'ISIS_ROUTE_RANGE')

#config the isisv4_route_range_1
isisv4_route_range_2 = networks_2.IsisRouteRange  

system_id_route = isisv4_route_range_2.SystemId.update(PatternType = 'SINGLE', Single = '00:10:94:00:20:01')
isisv4_routes2 = isisv4_route_range_2.Ipv4Routes.create(Name = 'isisv4route2')
address = isisv4_routes2.Address.update(PatternType = 'SINGLE', Single = '192.0.1.0')

print('\n    save config in json format.\n')
filename = __file__.split(os.path.sep)[-1].partition('.')[0] #strip filename from absolute file path and file extension
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

#  start ISISv4 protocol
print('\n  step 5. start ISISV4 protocol\n')
config.IsisControl({"targets": [Isis_handle1, Isis_handle2], "mode": 'START'})

print('\n  Waiting for 60 secs to establish desired state\n')
time.sleep(60)

#   Get the ISISv4 statistics
print('\n  step 6. Get the ISISv4 statistics\n')
statistics = session.Statistics

isisv4_statistics_1 = statistics.IsisStatistics.read(DeviceName = 'Device1')
isisv4_statistics_2 = statistics.IsisStatistics.read(DeviceName = 'Device2')

isis1_state = isisv4_statistics_1.RouterState
isis2_state = isisv4_statistics_2.RouterState

if (isis1_state == 'UP'and isis2_state == 'UP') :
    print ("\n   Info :ISIS session established successful \n")
    print ("    Isisv4 device1 state: %s \n" % isis1_state)
    print ("    Isisv4 device2 state: %s \n" % isis2_state)
else :
    print ("\n <error> Failed to establish isis sessions")
    print ("    Isisv4 device1 state: %s \n" % isis1_state)
    print ("    Isisv4 device2 state: %s \n" % isis2_state)

print('\n  step 7. create BOUND streamblock - IPv4 endpoints\n')
# create BOUND streamblock - IPv4 endpoints
device_traffic = config.DeviceTraffic.create(Name = 'IPV4Stream1', Encapsulation = 'IPV4', Sources = ['SimulatedNetworks1'], Destinations = ['SimulatedNetworks2'], BiDirectional = 'true')

#Config Frame Size
frame_length_1 = device_traffic.FrameLength.update(LengthType = 'FIXED', Fixed = '512')

#SaveAsxml
save_config_input = config.Save({'mode': 'VENDOR_BINARY', 'file-name': os.path.join(os.path.dirname(__file__), 'isisv4_sample_config.xml')})

config.TrafficControl( {"targets": ['IPV4Stream1'] , "mode": 'START'})

time.sleep(5)

config.TrafficControl( {"targets": ['IPV4Stream1'] , "mode": 'STOP'})

#  Get the traffic statistics
print('\n  step 8. Get traffic statistics\n')
statistics = session.Statistics
traffic_statistics_1 = statistics.DeviceTraffic.read(Name = 'IPV4Stream1')

tx_frames = traffic_statistics_1.TxFrames
rx_frames = traffic_statistics_1.RxFrames

if (tx_frames == rx_frames):
    print ("\n    Info: Traffic is transmitted successfully \n")
else :
    print ("\n    <error> Traffic is not transmitted successfully")

# stop the ISISv4 protocol
print('\n  step 9. start ISISV4 protocol\n')
config.IsisControl({"targets": [Isis_handle1, Isis_handle2], "mode": 'STOP'})

#disconnect ports
print('\n  step 10. Disconnect ports and delete session\n')
port_control_input = config.PortControl({"targets": [port_handle1, port_handle2], "mode": 'DISCONNECT'})

session.delete()
try:
    session = openhltest.Sessions.read(Name = sessionname)
except:
    print("    Deleted session - %s\n" % sessionname)