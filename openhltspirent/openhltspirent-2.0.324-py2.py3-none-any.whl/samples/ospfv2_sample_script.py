##Test Steps
    #Step 1:  Create a session and connect to two back to back stc ports
    #Step 2:  Configue ospfv2 devices on each port
    #Step 3:  Configure ospfv2 routes one each ospf device
    #Step 4:  Configure traffic group between two ospf devices
    #Step 5:  Save the configuration as an XML file
    #Step 6:  Start the ospf devices
    #Step 7:  Start the traffic
    #Step 8:  Validate the ospf stats
    #Step 9:  Validate the traffic stats
    #Step 10: Delete session and release resources

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

#  step 3. create a device under the port1, protocol stack: eth/vlan/vlan/ipv4/ospfv2. 
print('\n  step 3. create a device under port1, protocol stack: eth/vlan/vlan/ipv4/ospfv2.\n')
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

#create and config OSPFv2 protocol
protocol_ospfv2_1 = devices_1.Protocols.create(Name = 'OSPFV21', ProtocolType= 'OSPFV2', ParentLink = 'IPV41')
Ospfv2_handle1 = protocol_ospfv2_1.Name
print("    Ospfv2_handle1: %s\n" % protocol_ospfv2_1.Name)
ospfv2 = protocol_ospfv2_1.Ospfv2
router_id = ospfv2.RouterId.update(PatternType='SINGLE', Single = '11.1.1.1')
area_id = ospfv2.AreaId.update(PatternType='SINGLE', Single = '10.10.10.10')
network_type = ospfv2.NetworkType.update(PatternType='SINGLE', Single = 'NATIVE')
router_priority = ospfv2.RouterPriority.update(PatternType='SINGLE', Single = '1')
interface_cost = ospfv2.InterfaceCost.update(PatternType='SINGLE', Single = '1')
hello_interval = ospfv2.HelloInterval.update(PatternType='SINGLE', Single = '10')
router_dead_interval = ospfv2.RouterDeadInterval.update(PatternType='SINGLE', Single = '40')
retransmit_interval = ospfv2.RetransmitInterval.update(PatternType='SINGLE', Single = '5')

#OSPFV2 route creation on OSPFV2 device
simulated_networks_1 = device_group_east_1.SimulatedNetworks.create(Name = 'SimulatedNetworks1', ParentLink = 'Device1')

# create 'OSPFV2 Route Range' under the simulated_networks_1
networks_1 = simulated_networks_1.Networks.create(Name = 'OSPFV2Networks1', FlowLink = Ospfv2_handle1, NetworkType = 'OSPFV2_ROUTE_RANGE')

#config the ospfv2_route_range_1
ospfv2_route_range_1 = networks_1.Ospfv2RouteRange.update(Active = 'true')

advertise_router_id = ospfv2_route_range_1.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.0')
ospfv2_route_age = ospfv2_route_range_1.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv2_route_range_1.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

#config the ospfv2_router link
ospfv2_router_link_1 = ospfv2_route_range_1.Ospfv2RouterLink.create(Name = 'routerlink1')
router_link_type_1 = ospfv2_router_link_1.RouterLinkType.update(PatternType = 'SINGLE', Single = 'POINT_TO_POINT')
router_link_id_1 = ospfv2_router_link_1.RouterLinkId.update(PatternType = 'SINGLE', Single = '11.1.1.1')

# create 'OSPFV2 summary Range' under the simulated_networks_1
networks_2 = simulated_networks_1.Networks.create(Name = 'OSPFV2Networks1_2', FlowLink = Ospfv2_handle1, NetworkType = 'OSPFV2_SUMMARY_RANGE')

#config the ospfv2_sumamry_range_1
ospfv2_summary_range_1 = networks_2.Ospfv2SummaryRange

advertise_router_id = ospfv2_summary_range_1.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.2.0')
ospfv2_sumamry_age = ospfv2_summary_range_1.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv2_summary_range_1.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# create 'OSPFV2 external Range' under the simulated_networks_1
networks_3 = simulated_networks_1.Networks.create(Name = 'OSPFV2Networks1_3', FlowLink = Ospfv2_handle1, NetworkType = 'OSPFV2_EXTERNAL_RANGE')

#config the ospfv2_external_range_1
ospfv2_external_range_1 = networks_3.Ospfv2ExternalRange

advertise_router_id = ospfv2_external_range_1.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.3.0')
ospfv2_sumamry_age = ospfv2_external_range_1.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv2_external_range_1.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# create 'OSPFV2 nssa Range' under the simulated_networks_1
networks_4 = simulated_networks_1.Networks.create(Name = 'OSPFV2Networks1_4', FlowLink = Ospfv2_handle1, NetworkType = 'OSPFV2_NSSA_RANGE')

#config the ospfv2_nssa_range_1
ospfv2_nssa_range_1 = networks_4.Ospfv2NssaRange

advertise_router_id = ospfv2_nssa_range_1.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.4.0')
ospfv2_sumamry_age = ospfv2_nssa_range_1.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv2_nssa_range_1.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

print('\n  step 4. create a device under port2, protocol stack: eth/vlan/vlan/ipv4/ospfv2.\n')

device_group_west_1 = config.DeviceGroups.create(Name = 'WestSideDevicegroup1', Ports = [port_handle2])

# create devices: 'Devices 2' under the device_group_west and set device count
devices_2 = device_group_west_1.Devices.create(Name = 'Device2', DeviceCountPerPort = '1')

# create protocols ethernet
protocol_eth_2 = devices_2.Protocols.create(Name = 'WestEthernet2', ProtocolType= 'ETHERNET')

# create protocols vlan outer
protocol_vlan_3 = devices_2.Protocols.create(Name = 'WestVlan1', ProtocolType= 'VLAN', ParentLink = 'WestEthernet2')

# create protocols vlan inner
protocol_vlan_4 = devices_2.Protocols.create(Name = 'WestVlan2', ProtocolType= 'VLAN', ParentLink = 'WestVlan1')

# create protocols IPv4
protocol_ipv4_2 = devices_2.Protocols.create(Name = 'WestIPV41', ProtocolType= 'IPV4', ParentLink = 'WestVlan2')

# config mac addr with increment modifier
eth_2_mac = protocol_eth_2.Ethernet.Mac.update(PatternType='INCREMENT')
eth_2_mac_incr = eth_2_mac.Increment.update(Start = '00:10:94:00:10:01', Step = '00:00:00:00:00:01')

# config ipv4 source and gateway addresses

ipv4_2_src_addr = protocol_ipv4_2.Ipv4.SourceAddress.update(PatternType='SINGLE', Single = '192.85.1.13')
ipv4_2_gw_addr = protocol_ipv4_2.Ipv4.GatewayAddress.update(PatternType='SINGLE', Single = '192.85.1.3')

#create and config OSPFv2 protocol
protocol_ospfv2_2 = devices_2.Protocols.create(Name = 'OSPFV22', ProtocolType= 'OSPFV2', ParentLink = 'WestIPV41')
Ospfv2_handle2 = protocol_ospfv2_2.Name
print("    Ospfv2_handle2: %s\n" % protocol_ospfv2_2.Name)
ospfv2 = protocol_ospfv2_2.Ospfv2
router_id = ospfv2.RouterId.update(PatternType='SINGLE', Single = '12.1.1.1')
area_id = ospfv2.AreaId.update(PatternType='SINGLE', Single = '10.10.10.10')
network_type = ospfv2.NetworkType.update(PatternType='SINGLE', Single = 'NATIVE')
router_priority = ospfv2.RouterPriority.update(PatternType='SINGLE', Single = '0')
interface_cost = ospfv2.InterfaceCost.update(PatternType='SINGLE', Single = '1')
hello_interval = ospfv2.HelloInterval.update(PatternType='SINGLE', Single = '10')
router_dead_interval = ospfv2.RouterDeadInterval.update(PatternType='SINGLE', Single = '40')
retransmit_interval = ospfv2.RetransmitInterval.update(PatternType='SINGLE', Single = '5')

#OSPFV2 route creation on OSPFV2 device
simulated_networks_2 = device_group_west_1.SimulatedNetworks.create(Name = 'SimulatedNetworks2', ParentLink = 'Device2')

# create 'OSPFV2 Route Range' under the simulated_networks_1
networks_2 = simulated_networks_2.Networks.create(Name = 'OSPFV2Networks2', FlowLink = Ospfv2_handle2, NetworkType = 'OSPFV2_ROUTE_RANGE')

#config the ospfv2_route_range_1
ospfv2_route_range_2 = networks_2.Ospfv2RouteRange.update(Active = 'true')

advertise_router_id = ospfv2_route_range_2.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.10')
ospfv2_route_age = ospfv2_route_range_2.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv2_route_range_2.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

#config the ospfv2_router link
ospfv2_router_link_2 = ospfv2_route_range_2.Ospfv2RouterLink.create(Name = 'routerlink2')
router_link_type_2 = ospfv2_router_link_2.RouterLinkType.update(PatternType = 'SINGLE', Single = 'POINT_TO_POINT')
router_link_id_2 = ospfv2_router_link_2.RouterLinkId.update(PatternType = 'SINGLE', Single = '11.1.1.12')

# create 'OSPFV2 summary Range' under the simulated_networks_2
networks_21 = simulated_networks_2.Networks.create(Name = 'OSPFV2Networks2_2', FlowLink = Ospfv2_handle2, NetworkType = 'OSPFV2_SUMMARY_RANGE')

#config the ospfv2_sumamry_range_2
ospfv2_summary_range_2 = networks_21.Ospfv2SummaryRange

advertise_router_id = ospfv2_summary_range_2.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.2.10')
ospfv2_sumamry_age = ospfv2_summary_range_2.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv2_summary_range_2.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# create 'OSPFV2 external Range' under the simulated_networks_1
networks_31 = simulated_networks_2.Networks.create(Name = 'OSPFV2Networks2_3', FlowLink = Ospfv2_handle2, NetworkType = 'OSPFV2_EXTERNAL_RANGE')

#config the ospfv2_external_range_1
ospfv2_external_range_2 = networks_31.Ospfv2ExternalRange

advertise_router_id = ospfv2_external_range_2.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.3.10')
ospfv2_sumamry_age = ospfv2_external_range_2.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv2_external_range_2.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# create 'OSPFV2 nssa Range' under the simulated_networks_1
networks_41 = simulated_networks_2.Networks.create(Name = 'OSPFV2Networks2_4', FlowLink = Ospfv2_handle2, NetworkType = 'OSPFV2_NSSA_RANGE')

#config the ospfv2_nssa_range_1
ospfv2_nssa_range_2 = networks_41.Ospfv2NssaRange

advertise_router_id = ospfv2_nssa_range_2.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.4.10')
ospfv2_sumamry_age = ospfv2_nssa_range_2.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv2_nssa_range_2.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

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

print('\n  step 5. start OSPF protocol\n')
config.Ospfv2Control( {"targets": [Ospfv2_handle1, Ospfv2_handle2], "mode": 'START'})

time.sleep(45)

#  step 5. Get the OSPF statistics
print('\n  step 6. Get the OSPF statistics\n')

statistics = session.Statistics
ospfv2_statistics1 = statistics.Ospfv2Statistics.read(DeviceName = 'Device1')
ospfv2_statistics2 = statistics.Ospfv2Statistics.read(DeviceName = 'Device2')

ospfv2_state1 = ospfv2_statistics1.AdjacencyStatus
ospfv2_state2 = ospfv2_statistics2.AdjacencyStatus

if (ospfv2_state1 == 'FULL'and ospfv2_state2 == 'FULL') :
    print ("\n    Info :OSPF session established successfully \n")
    print ("    Ospfv2 device1 state: %s \n" % ospfv2_state1)
    print ("    Ospfv2 device2 state: %s \n" % ospfv2_state2)
else :
    print ("\n <error> Failed to establish OSPF sessions")
    exit(1)

# create BOUND streamblock - IPv4 endpoints
print('\n  step 7. Create bound streamblock\n')
device_traffic = config.DeviceTraffic.create(Name = 'IPV4Stream1', Encapsulation = 'IPV4', Sources = ['OSPFV2Networks1_2'], Destinations = ['OSPFV2Networks2_2'], BiDirectional = 'true')

#Config Frame Size
frame_length_1 = device_traffic.FrameLength.update(LengthType = 'FIXED', Fixed = '512')

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

#  stop the ospfv2 protocol
print('\n  step 9. stop ospfv2 protocol\n')
config.Ospfv2Control( {"targets": [Ospfv2_handle1, Ospfv2_handle2], "mode": 'STOP'})
    
#disconnect ports
print('\n  step 10. Disconnect ports and delete session\n')
port_control_input = config.PortControl({"targets": [port_handle1, port_handle2], "mode": 'DISCONNECT'})

session.delete()
try:
    session = openhltest.Sessions.read(Name = sessionname)
except:
    print("    Deleted session - %s\n" % sessionname)