# test stpes:
#  1. Create and connect two ports
#  2. Create Dhcpv6 client and server
#  3. Start DHCP Server&Client
#  4. Check Device results
#  5. Disconnect the ports

from openhltspirent.httptransport import HttpTransport
import time
import sys, os

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
    print("\n  Check %s for detailed console log \n" % log_file)
else:
    # Log to standard console
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

print('\n  Create session\n')
session = openhltest.Sessions.create(Name = sessionname)

print('\n  Create and connect ports\n')
config = session.Config

port1 = config.Ports.create(Name='Ethernet1', Location=chassisip1)
port_handle1 = port1.Name
print("    port_handle1: %s\n" % port_handle1)

port2 = config.Ports.create(Name='Ethernet2', Location=chassisip2)
port_handle2 = port2.Name
print("    port_handle2: %s\n" % port_handle2)
config.PortControl({"targets": [], "mode": 'CONNECT'})

print('\n  Create devices under the port1 and port2, protocol stack: eth/ipv6/dhcpv6.\n')
print('\n  Create device groups under the port1')
device_groups1 = config.DeviceGroups.create(Name='device_groups1', Ports=port1)

print('\n  Create devices: Devices 1 under the device_group and set device count')
device1 = device_groups1.Devices.create(Name='device1', DeviceCountPerPort='1', ParentLink=None)

print('\n  Create device groups under the port2')
device_groups2 = config.DeviceGroups.create(Name='device_groups2', Ports=port2)

print('\n  Create devices: Devices 1 under the device_group and set device count')
device2 = device_groups2.Devices.create(Name='device2', DeviceCountPerPort='1', ParentLink=None)

print('\n  Create protocols ethernet')
EthIf1 = device1.Protocols.create(Name = 'EthIf1', ProtocolType='ETHERNET')
EthIf2 = device2.Protocols.create(Name = 'EthIf2', ProtocolType='ETHERNET')
ethernet1 = EthIf1.Ethernet
ethernet2 = EthIf2.Ethernet

print('\n  Create protocols IPv6')
protocol_ipv6_1 = device1.Protocols.create(Name = 'IPV6_1', ParentLink='EthIf1', ProtocolType='IPV6')
protocol_ipv6_2 = device2.Protocols.create(Name = 'IPV6_2', ParentLink='EthIf2', ProtocolType='IPV6')

print('\n  Configure mac address')
mac_1 = EthIf1.Ethernet.Mac.update( PatternType='SINGLE', Single='00:10:94:00:00:02')
mac_2 = EthIf2.Ethernet.Mac.update( PatternType='SINGLE', Single='00:10:95:00:00:01')

print('\n  Configure ipv6 source and gateway addresses')

ipv6_1_src_addr = protocol_ipv6_1.Ipv6.SourceAddress.update(PatternType='SINGLE', Single = '2001::1')
ipv6_1_gw_addr = protocol_ipv6_1.Ipv6.GatewayAddress.update(PatternType='SINGLE', Single = '2001::3')

ipv6_2_src_addr = protocol_ipv6_2.Ipv6.SourceAddress.update(PatternType='SINGLE', Single = '2001::3')
ipv6_2_gw_addr = protocol_ipv6_2.Ipv6.GatewayAddress.update(PatternType='SINGLE', Single = '2001::1')

print('\n  Create and configure DHCPv6 client protocol')
protocol_dhcpv6_1 = device1.Protocols.create(Name = 'DHCPV6_1', ParentLink='IPV6_1', ProtocolType='DHCPV6')
dhcpv6_1 = protocol_dhcpv6_1.Dhcpv6

dhcpv6_client_mode_1 = protocol_dhcpv6_1.Dhcpv6.Dhcpv6ClientMode.update(PatternType='SINGLE', Single = 'DHCPv6')
T1Timer_1 = protocol_dhcpv6_1.Dhcpv6.T1Timer.update(PatternType='SINGLE', Single = '302400')
T2Timer_1 = protocol_dhcpv6_1.Dhcpv6.T2Timer.update(PatternType='SINGLE', Single = '483840')
EnableRenew_1 = protocol_dhcpv6_1.Dhcpv6.EnableRenew.update(PatternType='SINGLE', Single = 'true')
InterfaceId_1 = protocol_dhcpv6_1.Dhcpv6.InterfaceId.update(PatternType='SINGLE', Single = 'spirent')

print('\n  Create and configure Dhcpv6 Server protocol')
protocol_dhcpv6_2 = device2.Protocols.create(Name = 'DHCPV6_2', ParentLink='IPV6_2', ProtocolType='DHCPV6_SERVER')
dhcpv6_2 = protocol_dhcpv6_2.Dhcpv6Server

EmulationMode_2 = protocol_dhcpv6_2.Dhcpv6Server.EmulationMode.update(PatternType='SINGLE', Single = 'DHCPV6')
PreferredLifetime_2 = protocol_dhcpv6_2.Dhcpv6Server.PreferredLifetime.update(PatternType='SINGLE', Single = '504800')
server_address_pool = dhcpv6_2.ServerAddressPool
StartIpv6Address_1 = server_address_pool.StartIpv6Address
StartIpv6Address_1.update(PatternType='SINGLE', Single='2002::1')

print('\n  SaveasXML\n')
save_config_input = config.Save({'mode': 'VENDOR_BINARY', 'file-name': os.path.join(os.path.dirname(__file__), 'dhcpv6_sample_script.xml')})

print('\n  Start dhcpv6 server\n')
dhcpv6_server_control_input = config.Dhcpv6ServerControl({"targets": ['DHCPV6_2'], "mode": 'START'})
#print(dhcpv6_server_control_input)

print('\n  Start dhcpv6 client\n')
dhcpv6_client_control_input = config.Dhcpv6Control({"targets": ['DHCPV6_1'], "mode": 'BIND'})
#print(dhcpv6_client_control_input)

time.sleep(60)

print('\n  Get the DHCP Client statistics\n')
statistics = session.Statistics
dhcp_statistics_1 = statistics.Dhcpv6Statistics.read(DeviceName = 'device1')
#print(dhcp_statistics_1)

print('\n  Get the DHCP Server statistics\n')
dhcp_server_statistics_2 = statistics.Dhcpv6ServerStatistics.read(DeviceName = 'device2')
#print(dhcp_server_statistics_2)

current_bound_count = dhcp_statistics_1.CurrentBoundCount
current_idle_count = dhcp_statistics_1.CurrentIdleCount
current_bound_count_server = dhcp_server_statistics_2.CurrentBoundCount

if (current_bound_count == 1 and current_idle_count == 0 and current_bound_count_server == 1) :
    print('*' * 40)
    print ("\n Info :Dhcpv6 session bind successful \n")
    print('*' * 40)
else :
    print ("\n <error> Failed to bind Dhcpv6 session \n")
    sys.exit();

print('\n  Disconnect ports\n')
port_control_input = config.PortControl({"targets": [], "mode": 'DISCONNECT'})

print('\n  delete session\n')
session.delete()
