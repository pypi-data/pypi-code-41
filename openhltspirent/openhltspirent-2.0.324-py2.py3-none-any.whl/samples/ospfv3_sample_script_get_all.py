##Test Steps
    #Step 1:  Create a session and connect to two back to back stc ports
    #Step 2:  Configue ospfv3 devices on each port
    #Step 3:  Configure ospfv3 routes one each ospf device
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
import generate_url

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
config.PortControl({"targets": [], "mode": 'CONNECT'})

#  step 3. create a device under the port1, protocol stack: eth/vlan/vlan/IPv6/ospfv3. 
print('\n  step 3. create a device under port1, protocol stack: eth/vlan/vlan/IPv6/ospfv3.\n')
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

# create protocols IPv6
protocol_IPv6_1 = devices_1.Protocols.create(Name = 'IPv61', ProtocolType= 'IPV6', ParentLink = 'Vlan2')

# config mac addr with increment modifier
eth_1_mac = protocol_eth_1.Ethernet.Mac.update(PatternType='INCREMENT')
eth_1_mac_incr = eth_1_mac.Increment.update(Start = '00:10:84:00:00:01', Step = '00:00:00:00:00:01')

# config IPv6 source and gateway addresses

IPv6_1_src_addr = protocol_IPv6_1.Ipv6.SourceAddress.update(PatternType='SINGLE', Single = '2000::6')
IPv6_1_gw_addr = protocol_IPv6_1.Ipv6.GatewayAddress.update(PatternType='SINGLE', Single = '2000::16')

#create and config ospfv3 protocol
protocol_ospfv3_1 = devices_1.Protocols.create(Name = 'ospfv31', ProtocolType= 'OSPFV3', ParentLink = 'IPv61')
ospfv3_handle1 = protocol_ospfv3_1.Name
print("    ospfv3_handle1: %s\n" % protocol_ospfv3_1.Name)
ospfv3 = protocol_ospfv3_1.Ospfv3
router_id = ospfv3.RouterId.update(PatternType='SINGLE', Single = '11.1.1.1')
area_id = ospfv3.AreaId.update(PatternType='SINGLE', Single = '10.10.10.10')
network_type = ospfv3.NetworkType.update(PatternType='SINGLE', Single = 'NATIVE')
router_priority = ospfv3.RouterPriority.update(PatternType='SINGLE', Single = '1')
interface_cost = ospfv3.InterfaceCost.update(PatternType='SINGLE', Single = '1')
hello_interval = ospfv3.HelloInterval.update(PatternType='SINGLE', Single = '10')
router_dead_interval = ospfv3.RouterDeadInterval.update(PatternType='SINGLE', Single = '40')
retransmit_interval = ospfv3.RetransmitInterval.update(PatternType='SINGLE', Single = '5')

#ospfv3 route creation on ospfv3 device
simulated_networks_1 = device_group_east_1.SimulatedNetworks.create(Name = 'SimulatedNetworks1', ParentLink = 'Device1')

# create 'ospfv3 Route Range' under the simulated_networks_1
networks_1 = simulated_networks_1.Networks.create(Name = 'ospfv3Networks1', FlowLink = ospfv3_handle1, NetworkType = 'OSPFV3_ROUTE_RANGE')

#config the ospfv3_route_range_1
ospfv3_route_range_1 = networks_1.Ospfv3RouteRange.update(Active = 'true')

advertise_router_id = ospfv3_route_range_1.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.5')
ospfv3_route_age = ospfv3_route_range_1.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv3_route_range_1.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

#config the ospfv3_router link
ospfv3_router_link_1 = ospfv3_route_range_1.Ospfv3RouterLink.create(Name = 'routerlink1')
router_link_type_1 = ospfv3_router_link_1.RouterLinkType.update(PatternType = 'SINGLE', Single = 'POINT_TO_POINT')
interface_id_1 = ospfv3_router_link_1.InterfaceId.update(PatternType = 'SINGLE', Single = '1000')

# create 'ospfv3 Inter area prefix Range' under the simulated_networks_1
networks_2 = simulated_networks_1.Networks.create(Name = 'ospfv3Networks1_2', FlowLink = ospfv3_handle1, NetworkType = 'OSPFV3_INTER_AREA_PREFIX_RANGE')

#config the ospfv3_inter_area_prefix_range_1
ospfv3_inter_area_prefix_range_1 = networks_2.Ospfv3InterAreaPrefixRange

advertise_router_id = ospfv3_inter_area_prefix_range_1.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.11')
ospfv3_sumamry_age = ospfv3_inter_area_prefix_range_1.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv3_inter_area_prefix_range_1.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# create 'ospfv3 intra area prefix range' under the simulated_networks_1
networks_3 = simulated_networks_1.Networks.create(Name = 'ospfv3Networks1_3', FlowLink = ospfv3_handle1, NetworkType = 'OSPFV3_INTRA_AREA_PREFIX_RANGE')

#config the ospfv3_intra_area_prefix_range_1
ospfv3_intra_area_prefix_range_1 = networks_3.Ospfv3IntraAreaPrefixRange

advertise_router_id = ospfv3_intra_area_prefix_range_1.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.13')
ospfv3_sumamry_age = ospfv3_intra_area_prefix_range_1.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv3_intra_area_prefix_range_1.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# create 'ospfv3 AS external prefix Range' under the simulated_networks_1
networks_4 = simulated_networks_1.Networks.create(Name = 'ospfv3Networks1_4', FlowLink = ospfv3_handle1, NetworkType = 'OSPFV3_AS_EXTERNAL_PREFIX_RANGE')

#config the ospfv3_as_external_prefix_range_1
ospfv3_as_external_prefix_range_1 = networks_4.Ospfv3AsExternalPrefixRange

advertise_router_id = ospfv3_as_external_prefix_range_1.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.4.0')
ospfv3_sumamry_age = ospfv3_as_external_prefix_range_1.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv3_as_external_prefix_range_1.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

print('\n  step 4. create a device under port2, protocol stack: eth/vlan/vlan/IPv6/ospfv3.\n')

device_group_west_1 = config.DeviceGroups.create(Name = 'WestSideDevicegroup1', Ports = [port_handle2])

# create devices: 'Devices 2' under the device_group_west and set device count
devices_2 = device_group_west_1.Devices.create(Name = 'Device2', DeviceCountPerPort = '1')

# create protocols ethernet
protocol_eth_2 = devices_2.Protocols.create(Name = 'WestEthernet2', ProtocolType= 'ETHERNET')

# create protocols vlan outer
protocol_vlan_3 = devices_2.Protocols.create(Name = 'WestVlan1', ProtocolType= 'VLAN', ParentLink = 'WestEthernet2')

# create protocols vlan inner
protocol_vlan_4 = devices_2.Protocols.create(Name = 'WestVlan2', ProtocolType= 'VLAN', ParentLink = 'WestVlan1')

# create protocols IPv6
protocol_IPv6_2 = devices_2.Protocols.create(Name = 'WestIPv61', ProtocolType= 'IPV6', ParentLink = 'WestVlan2')

# config mac addr with increment modifier
eth_2_mac = protocol_eth_2.Ethernet.Mac.update(PatternType='INCREMENT')
eth_2_mac_incr = eth_2_mac.Increment.update(Start = '00:10:94:00:10:01', Step = '00:00:00:00:00:01')

# config IPv6 source and gateway addresses

IPv6_2_src_addr = protocol_IPv6_2.Ipv6.SourceAddress.update(PatternType='SINGLE', Single = '2000::16')
IPv6_2_gw_addr = protocol_IPv6_2.Ipv6.GatewayAddress.update(PatternType='SINGLE', Single = '2000::6')

#create and config ospfv3 protocol
protocol_ospfv3_2 = devices_2.Protocols.create(Name = 'ospfv32', ProtocolType= 'OSPFV3', ParentLink = 'WestIPv61')
ospfv3_handle2 = protocol_ospfv3_2.Name
print("    ospfv3_handle2: %s\n" % protocol_ospfv3_2.Name)
ospfv3 = protocol_ospfv3_2.Ospfv3
router_id = ospfv3.RouterId.update(PatternType='SINGLE', Single = '12.1.1.1')
area_id = ospfv3.AreaId.update(PatternType='SINGLE', Single = '10.10.10.10')
network_type = ospfv3.NetworkType.update(PatternType='SINGLE', Single = 'NATIVE')
router_priority = ospfv3.RouterPriority.update(PatternType='SINGLE', Single = '0')
interface_cost = ospfv3.InterfaceCost.update(PatternType='SINGLE', Single = '1')
hello_interval = ospfv3.HelloInterval.update(PatternType='SINGLE', Single = '10')
router_dead_interval = ospfv3.RouterDeadInterval.update(PatternType='SINGLE', Single = '40')
retransmit_interval = ospfv3.RetransmitInterval.update(PatternType='SINGLE', Single = '5')

#ospfv3 route creation on ospfv3 device
simulated_networks_2 = device_group_west_1.SimulatedNetworks.create(Name = 'SimulatedNetworks2', ParentLink = 'Device2')

# create 'ospfv3 Route Range' under the simulated_networks_1
networks_2 = simulated_networks_2.Networks.create(Name = 'ospfv3Networks2', FlowLink = ospfv3_handle2, NetworkType = 'OSPFV3_ROUTE_RANGE')

#config the ospfv3_route_range_1
ospfv3_route_range_2 = networks_2.Ospfv3RouteRange.update(Active = 'true')

advertise_router_id = ospfv3_route_range_2.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.7')
ospfv3_route_age = ospfv3_route_range_2.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv3_route_range_2.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

#config the ospfv3_router link
ospfv3_router_link_2 = ospfv3_route_range_2.Ospfv3RouterLink.create(Name = 'routerlink2')
router_link_type_2 = ospfv3_router_link_2.RouterLinkType.update(PatternType = 'SINGLE', Single = 'POINT_TO_POINT')
interface_id_2 = ospfv3_router_link_2.InterfaceId.update(PatternType = 'SINGLE', Single = '2000')

# create 'ospfv3 Inter area prefix Range' under the simulated_networks_2
networks_21 = simulated_networks_2.Networks.create(Name = 'ospfv3Networks2_2', FlowLink = ospfv3_handle2, NetworkType = 'OSPFV3_INTER_AREA_PREFIX_RANGE')

#config the ospfv3_inter_area_prefix_range_2
ospfv3_inter_area_prefix_range_2 = networks_21.Ospfv3InterAreaPrefixRange

advertise_router_id = ospfv3_inter_area_prefix_range_2.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.11')
ospfv3_sumamry_age = ospfv3_inter_area_prefix_range_2.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv3_inter_area_prefix_range_2.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# create 'ospfv3 intra area prefix range' under the simulated_networks_2
networks_31 = simulated_networks_2.Networks.create(Name = 'ospfv3Networks2_3', FlowLink = ospfv3_handle2, NetworkType = 'OSPFV3_INTRA_AREA_PREFIX_RANGE')

#config the ospfv3_intra_area_prefix_range_2
ospfv3_intra_area_prefix_range_2 = networks_31.Ospfv3IntraAreaPrefixRange

advertise_router_id = ospfv3_intra_area_prefix_range_2.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.13')
ospfv3_sumamry_age = ospfv3_intra_area_prefix_range_2.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv3_intra_area_prefix_range_2.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# create 'ospfv3 AS external prefix Range' under the simulated_networks_2
networks_41 = simulated_networks_2.Networks.create(Name = 'ospfv3Networks2_4', FlowLink = ospfv3_handle2, NetworkType = 'OSPFV3_AS_EXTERNAL_PREFIX_RANGE')

#config the ospfv3_as_external_prefix_range_2
ospfv3_as_external_prefix_range_2 = networks_41.Ospfv3AsExternalPrefixRange

advertise_router_id = ospfv3_as_external_prefix_range_2.AdvertiseRouterId.update(PatternType = 'SINGLE', Single = '192.0.1.15')
ospfv3_sumamry_age = ospfv3_as_external_prefix_range_2.Age.update(PatternType = 'SINGLE', Single = '67')
advertise_seq_num = ospfv3_as_external_prefix_range_2.SequenceNumber.update(PatternType = 'SINGLE', Single = '80000089')

# print('\n    save config in json format.\n')
# filename = __file__.split(os.path.sep)[-1].partition('.')[0] #strip filename from absolute file path and file extension
# #Save json file
# saved_json_file = os.path.join(os.path.dirname(__file__), filename + '_saved.json')
# config.Save({'mode': 'RESTCONF_JSON', 'file-name': saved_json_file})
# content_dict={}
# with open(saved_json_file, 'r') as f:
#     content_dict = json.load( f)
# if len(content_dict['openhltest:config']['ports']) != 2:
#     print('\n port number should be 2 in saved json file.\n')
#     exit(1)

# print('\n    load json config and reserve ports.\n')
# config.Load({'mode': 'RESTCONF_JSON', 'file-name': saved_json_file})
# ports = config.Ports.read()
# if len(ports) != 2:
#     print('\n port number should be 2 after loading json config file.\n')
#     exit(1)
# config.PortControl({"targets": [], "mode": 'CONNECT'})

print('\n  step 5. start OSPF protocol\n')
config.Ospfv3Control( {"targets": [ospfv3_handle1, ospfv3_handle2], "mode": 'START'})

time.sleep(45)

#  step 5. Get the OSPF statistics
print('\n  step 6. Get the OSPF statistics\n')

statistics = session.Statistics
ospfv3_statistics1 = statistics.Ospfv3Statistics.read(DeviceName = 'Device1')
ospfv3_statistics2 = statistics.Ospfv3Statistics.read(DeviceName = 'Device2')

ospfv3_state1 = ospfv3_statistics1.AdjacencyStatus
ospfv3_state2 = ospfv3_statistics2.AdjacencyStatus

if (ospfv3_state1 == 'FULL'and ospfv3_state2 == 'FULL') :
    print ("\n    Info :OSPF session established successfully \n")
    print ("    ospfv3 device1 state: %s \n" % ospfv3_state1)
    print ("    ospfv3 device2 state: %s \n" % ospfv3_state2)
else :
    print ("\n <error> Failed to establish OSPF sessions")
    print ("    ospfv3 device1 state: %s \n" % ospfv3_state1)
    print ("    ospfv3 device2 state: %s \n" % ospfv3_state2)

# create BOUND streamblock - IPv6 endpoints
print('\n  step 7. Create bound streamblock\n')
device_traffic = config.DeviceTraffic.create(Name = 'Ipv6Stream1', Encapsulation = 'IPV6', Sources = ['ospfv3Networks1_4'], Destinations = ['ospfv3Networks2_4'], BiDirectional = 'true')

#Config Frame Size
frame_length_1 = device_traffic.FrameLength.update(LengthType = 'FIXED', Fixed = '512')

#SaveAsxml
save_config_input = config.Save({'mode': 'VENDOR_BINARY', 'file-name': os.path.join(os.path.dirname(__file__), 'ospfv3_sample_config.xml')})

config.TrafficControl( {"targets": ['Ipv6Stream1'] , "mode": 'START'})

time.sleep(5)

config.TrafficControl( {"targets": ['Ipv6Stream1'] , "mode": 'STOP'})

#  Get the traffic statistics
print('\n  step 8. Get traffic statistics\n')
statistics = session.Statistics
traffic_statistics_1 = statistics.DeviceTraffic.read(Name = 'Ipv6Stream1')

tx_frames = traffic_statistics_1.TxFrames
rx_frames = traffic_statistics_1.RxFrames

if (tx_frames == rx_frames):
    print ("\n    Info: Traffic is transmitted successfully \n")
    print ("    TxFrames: %s \n" % tx_frames)
    print ("    RxFrames: %s \n" % rx_frames)
else :
    print ("\n    <error> Traffic is not transmitted successfully")
    print ("    TxFrames: %s \n" % tx_frames)
    print ("    RxFrames: %s \n" % rx_frames)

#  stop the ospfv3 protocol
print('\n  step 9. stop ospfv3 protocol\n')
config.Ospfv3Control( {"targets": [ospfv3_handle1, ospfv3_handle2], "mode": 'STOP'})

# Get all possible results
num_of_failed = generate_url.url_gen(server_ip = serverip, server_port = portnumber, session_name = sessionname).get_all()

#disconnect ports
print('\n  step 10. Disconnect ports and delete session\n')
port_control_input = config.PortControl({"targets": [port_handle1, port_handle2], "mode": 'DISCONNECT'})

session.delete()
try:
    session = openhltest.Sessions.read(Name = sessionname)
except:
    print("    Deleted session - %s\n" % sessionname)

if num_of_failed:
    print("failed GET requests: " + str(num_of_failed) + ". Check logs for detail.")
    # sys.exit(1)