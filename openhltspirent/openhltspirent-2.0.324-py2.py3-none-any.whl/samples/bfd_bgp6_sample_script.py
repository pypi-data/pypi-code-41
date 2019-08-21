###Test Steps
    #Step 1:  Create a session and connect to two back to back stc ports
    #Step 2:  Configue 2 bgp devices with bfd on each port
    #Step 3:  Configure 2 bgp a routes one each bgp device
    #Step 4:  Configure traffic group between two bgp devices
    #Step 5:  Save the configuration as an XML file
    #Step 6:  Start the bgp devices
    #Step 7:  Start the traffic
    #Step 8:  Validate the bgp stats
    #Step 9:  Validate the traffic stats
    #Step 10: Delete session and release resources

import time
import sys, os
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

print('\n  Create a session\n')
try:
    session = openhltest.Sessions.read(Name = sessionname)
    session.delete()
    print("    ######## Deleted existing session with name %s ######### \n" % sessionname)
except:
    print("    ######## There is no session exist with name %s ######## \n" % sessionname)

session = openhltest.Sessions.create(Name = sessionname)
config = session.Config
print("    Created new session - %s" % sessionname)

print('\n  Create and connect ports\n')
port1 = config.Ports.create(Name='Ethernet1', Location=chassisip1)
port_handle1 = port1.Name
print("    port_handle1: %s\n" % port_handle1)

port2 = config.Ports.create(Name='Ethernet2', Location=chassisip2)
port_handle2 = port2.Name
print("    port_handle2: %s\n" % port_handle2)
config.PortControl({"targets": [], "mode": 'CONNECT'})

print('\n  Create a device under port1, protocol stack: eth/vlan/vlan/ipv6/BGP\n')

print('\n  Create device groups: East Side - Device group 1 under the port Ethernet1')
device_group_east_1 = config.DeviceGroups.create(Name = 'EastSideDevicegroup1', Ports = [port_handle1])

print('\n  Create devices: Devices 1 under the device_group_east and set device count')
devices_1 = device_group_east_1.Devices.create(Name = 'Device1', DeviceCountPerPort = '1')

print('\n  Create protocols ethernet')
protocol_eth_1 = devices_1.Protocols.create(Name = 'Ethernet1', ProtocolType= 'ETHERNET')

print('\n  Create protocols vlan outer')
protocol_vlan_1 = devices_1.Protocols.create(Name = 'Vlan1_Outer', ProtocolType= 'VLAN', ParentLink = 'Ethernet1')

print('\n  Create protocols vlan inner')
protocol_vlan_2 = devices_1.Protocols.create(Name = 'Vlan1_Inner', ProtocolType= 'VLAN', ParentLink = 'Vlan1_Outer')

print('\n  Create protocols IPv6')
protocol_ipv6_1 = devices_1.Protocols.create(Name = 'IPV61', ProtocolType= 'IPV6', ParentLink = 'Vlan1_Inner')

print('\n  Configure mac addr with increment modifier')
eth_1_mac = protocol_eth_1.Ethernet.Mac.update(PatternType='INCREMENT')
eth_1_mac_incr = eth_1_mac.Increment.update(Start = '00:10:94:11:00:01', Step = '00:00:00:00:00:02')

print('\n  Configure ipv6 source and gateway addresses')
ipv6_1_src_addr = protocol_ipv6_1.Ipv6.SourceAddress.update(PatternType='SINGLE', Single = '2000::1')
ipv6_1_gw_addr = protocol_ipv6_1.Ipv6.GatewayAddress.update(PatternType='SINGLE', Single = '2000::11')

print('\n  Configure inner vlan and outer vlan ')
vlan_id_1_1 = protocol_vlan_1.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_1_incr_1 = vlan_id_1_1.Increment.update(Start = '100', Step = '1')
priority1_1 = protocol_vlan_1.Vlan.Priority.update(PatternType='SINGLE', Single='7')

vlan_id_1_2 = protocol_vlan_2.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_1_incr_2 = vlan_id_1_2.Increment.update(Start = '200', Step = '2')
priority1_2 = protocol_vlan_2.Vlan.Priority.update(PatternType='SINGLE', Single='7')

print('\n  Create a device under port2, protocol stack: eth/vlan/vlan/ipv6/BGP.\n')
print('\n  Create device groups: West Side - Device group 1 under the port Ethernet 2')
device_group_west_1 = config.DeviceGroups.create(Name = 'WestSideDevicegroup1', Ports = [port_handle2])

print('\n  Create devices: Devices 2 under the device_group_west and set device count')
devices_2 = device_group_west_1.Devices.create(Name = 'Device2', DeviceCountPerPort = '1')

print('\n  Create protocols ethernet')
protocol_eth_2 = devices_2.Protocols.create(Name = 'Ethernet2', ProtocolType= 'ETHERNET')

print('\n  Create protocols vlan outer')
protocol_vlan_3 = devices_2.Protocols.create(Name = 'Vlan2_Outer', ProtocolType= 'VLAN', ParentLink = 'Ethernet2')

print('\n  Create protocols vlan inner')
protocol_vlan_4 = devices_2.Protocols.create(Name = 'Vlan2_Inner', ProtocolType= 'VLAN', ParentLink = 'Vlan2_Outer')

print('\n  Create protocols IPv6')
protocol_ipv6_2 = devices_2.Protocols.create(Name = 'IPV62', ProtocolType= 'IPV6', ParentLink = 'Vlan2_Inner')

print('\n  Configure mac addr with increment modifier')
eth_2_mac = protocol_eth_2.Ethernet.Mac.update(PatternType='INCREMENT')
eth_2_mac_incr = eth_2_mac.Increment.update(Start = '00:10:95:22:00:01', Step = '00:00:00:00:00:04')

print('\n  Configure ipv6 source and gateway addresses')
ipv6_2_src_addr = protocol_ipv6_2.Ipv6.SourceAddress.update(PatternType='SINGLE', Single = '2000::11')
ipv6_2_gw_addr = protocol_ipv6_2.Ipv6.GatewayAddress.update(PatternType='SINGLE', Single = '2000::1')

print('\n  Configure inner vlan and outer vlan')
vlan_id_2_1 = protocol_vlan_3.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_2_incr_1 = vlan_id_2_1.Increment.update(Start = '100', Step = '1')
priority2_1 = protocol_vlan_3.Vlan.Priority.update(PatternType='SINGLE', Single='7')

vlan_id_2_2 = protocol_vlan_4.Vlan.Id.update(PatternType='INCREMENT')
vlan_id_2_incr_2 = vlan_id_2_2.Increment.update(Start = '200', Step = '1')
priority2_2 = protocol_vlan_4.Vlan.Priority.update(PatternType='SINGLE', Single='7')

print('\n  Create and configure BFDv6 protocol on port1')
protocol_bfd_1 = devices_1.Protocols.create(Name = 'BFD1', ParentLink='IPV61', ProtocolType='BFDV6')
bfdv6_handle1 = protocol_bfd_1.Name
bfd_1 = protocol_bfd_1.Bfdv6

TransmitInterval_1 = bfd_1.TransmitInterval.update(PatternType='SINGLE', Single='20')
ReceiveInterval_1 = bfd_1.ReceiveInterval.update(PatternType='SINGLE', Single='30')
EchoReceiveInterval_1 = bfd_1.EchoReceiveInterval.update(PatternType='SINGLE', Single='40')

print('\n  Create and configure BGPv6 protocol on port1')
protocol_bgp_1 = devices_1.Protocols.create(Name = 'BGP1', ParentLink='IPV61', ProtocolType='BGPV6')
bgpv6_handle1 = protocol_bgp_1.Name
bgp_1 = protocol_bgp_1.Bgpv6

dut_ipv6_address_1 = bgp_1.DutIpv6Address
dut_ipv6_address_1.update(PatternType='SINGLE', Single='2000::11')

hold_time_interval_1 = bgp_1.HoldTimeInterval
hold_time_interval_1.update(PatternType='SINGLE', Single='100')

keep_alive_interval_1 = bgp_1.KeepAliveInterval
keep_alive_interval_1.update(PatternType='SINGLE', Single='50')

as_number_2byte = protocol_bgp_1.Bgpv6.AsNumber2Byte.create()
as_number_2byte.AsNumber.Increment.update(Start='20')
as_number_2byte.DutAsNumber.Increment.update(Start='10')

print('\n  Create simulated_networks under the device_group_east')
simulated_networks_1 = device_group_east_1.SimulatedNetworks.create(Name='simulated-networks_1', ParentLink = 'Device1')
networks_1 = simulated_networks_1.Networks.create(Name='BGPV6Networks1', FlowLink='BGP1', NetworkType='BGPV6_ROUTE_RANGE')

print('\n  Create BGPV6 Route Range under the simulated_networks_1')
bgpv6_route_range_1 = networks_1.Bgpv6RouteRange
bgpv6_route_range_1.update(Active='true')

address_1 = bgpv6_route_range_1.Address
address_1.update(PatternType='SINGLE', Single='3000::4')

prefix_length_1 = bgpv6_route_range_1.PrefixLength
prefix_length_1.update(PatternType='SINGLE', Single='24')

as_path_1 = bgpv6_route_range_1.AsPath
as_path_1.update(PatternType='SINGLE', Single='20')

next_hop_address_1 = bgpv6_route_range_1.NextHopAddress
next_hop_address_1.update(PatternType='SINGLE', Single='3000::5')

print('\n  Create and configure BFDv6 protocol on port2')
protocol_bfd_2 = devices_2.Protocols.create(Name = 'BFD2', ParentLink='IPV62', ProtocolType='BFDV6')
bfdv6_handle2 = protocol_bfd_2.Name
bfd_2 = protocol_bfd_2.Bfdv6

TransmitInterval_2 = bfd_2.TransmitInterval.update(PatternType='SINGLE', Single='20')
ReceiveInterval_2 = bfd_2.ReceiveInterval.update(PatternType='SINGLE', Single='30')
EchoReceiveInterval_2 = bfd_2.EchoReceiveInterval.update(PatternType='SINGLE', Single='40')

print('\n  Create and configure BGPv6 protocol on port2')
protocol_bgp_2 = devices_2.Protocols.create(Name = 'BGP2', ParentLink='IPV62', ProtocolType='BGPV6')
bgpv6_handle2 = protocol_bgp_2.Name
bgp_2 = protocol_bgp_2.Bgpv6

dut_ipv6_address_2 = bgp_2.DutIpv6Address.update(PatternType='SINGLE', Single='2000::1')
hold_time_interval_2 = bgp_2.HoldTimeInterval.update(PatternType='SINGLE', Single='100')
keep_alive_interval_2 = bgp_2.KeepAliveInterval.update(PatternType='SINGLE', Single='50')

as_number_2byte = protocol_bgp_2.Bgpv6.AsNumber2Byte.create()
as_number_2byte.AsNumber.Increment.update(Start='10')
as_number_2byte.DutAsNumber.Increment.update(Start='20')

print('\n  Create simulated_networks under the device_group_west')
simulated_networks_2 = device_group_west_1.SimulatedNetworks.create(Name='simulated-networks_2', ParentLink = 'Device2')
networks_2 = simulated_networks_2.Networks.create(Name='BGPV6Networks2', FlowLink='BGP2', NetworkType='BGPV6_ROUTE_RANGE')

print('\n  Create BGPV6 Route Range under the simulated_networks_2')
bgpv6_route_range_2 = networks_2.Bgpv6RouteRange
bgpv6_route_range_2.update(Active='true')

address_2 = bgpv6_route_range_2.Address
address_2.update(PatternType='SINGLE', Single='3000::11')

prefix_length_2 = bgpv6_route_range_2.PrefixLength
prefix_length_2.update(PatternType='SINGLE', Single='24')

as_path_2 = bgpv6_route_range_2.AsPath
as_path_2.update(PatternType='SINGLE', Single='20')

next_hop_address_2 = bgpv6_route_range_2.NextHopAddress
next_hop_address_2.update(PatternType='SINGLE', Single='3000::13')

print('\n  Save XML')
save_config_input = config.Save({'mode': 'VENDOR_BINARY', 'file-name': os.path.join(os.path.dirname(__file__), 'bfd_bgpv6_sample_script.xml')})

print('\n  Start BFDv6 protocol\n')
bgpv6_control_input1 = config.Bfdv6Control({"targets": [bfdv6_handle1 , bfdv6_handle2], "mode": 'START'})

print('\n  Start BGP protocol\n')
bgpv6_control_input1 = config.Bgpv6Control({"targets": [bgpv6_handle1 , bgpv6_handle2], "mode": 'START'})

time.sleep(60)

print('\n  Get the BGP statistics\n')
statistics = session.Statistics
bgpv6_statistics_1 = statistics.Bgpv6Statistics.read(DeviceName = 'Device1')
print('  BGP statistics of Device1:')
#print(bgpv6_statistics_1)

bgpv6_statistics_2 = statistics.Bgpv6Statistics.read(DeviceName = 'Device2')
print('  BGP statistics of Device2:')
#print(bgpv6_statistics_2)

bgp1_state = bgpv6_statistics_1.RouterState
bgp2_state = bgpv6_statistics_2.RouterState

if (bgp1_state == 'ESTABLISHED'and bgp2_state == 'ESTABLISHED') :
    print('*' * 40)
    print ("\n Info :BGP session established successful \n")
    print('*' * 40)
else :
    print ("\n <error> Failed to establish bgp sessions")
    sys.exit();

print('\n  Get the BFDv6 statistics\n')
statistics = session.Statistics
bfdv6_statistics_1 = statistics.Bfdv6Statistics.read(DeviceName = 'Device1')
print('  BFDv6 statistics of Device1:')
#print(bfdv6_statistics_1)

bfdv6_statistics_2 = statistics.Bfdv6Statistics.read(DeviceName = 'Device2')
print('  BFDv6 statistics of Device2:')
#print(bfdv6_statistics_2)

print('\n  Create BOUND streamblock - IPv6 endpoints\n')
device_traffic = config.DeviceTraffic.create(Name='IPV6Stream1', Encapsulation='IPV6', Sources=['simulated-networks_1'], Destinations=['simulated-networks_2'], BiDirectional='true')

#Config Frame Size
frame_length = device_traffic.FrameLength
frame_length.update(LengthType='FIXED', Fixed='512')

print('\n  Start the traffic\n')
traffic_control_input1 = config.TrafficControl( {"targets": ['IPV6Stream1'], "mode": 'START'})

time.sleep(5)

traffic_control_input1 = config.TrafficControl( {"targets": ['IPV6Stream1'], "mode": 'STOP'})

print('\n  Get traffic statistics\n')
traffic_statistics_1 = statistics.DeviceTraffic.read(Name='IPV6Stream1',)
#print(traffic_statistics_1)

tx_frames = traffic_statistics_1.TxFrames
rx_frames = traffic_statistics_1.RxFrames

if (tx_frames == rx_frames):
    print('*' * 40)
    print ("\n Info: Traffic is transmitted successfully \n")
    print('*' * 40)
else :
    print ("\n <error> Traffic is not transmitted successfully")
    sys.exit();

print('\n  Disconnect ports\n')
port_control_input = config.PortControl({"targets": [], "mode": 'DISCONNECT'})

print('\n  delete session\n')
session.delete()
