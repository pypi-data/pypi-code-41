# test stpes:
#  1. Create and connect two ports
#  2. Create DHCPv4 client and server
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

print('\n  Create devices under the port1 and port2, protocol stack: eth/ipv4/dhcpv4.\n')
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

print('\n  Create protocols IPv4')
protocol_ipv4_1 = device1.Protocols.create(Name = 'IPV4_1', ParentLink='EthIf1', ProtocolType='IPV4')
protocol_ipv4_2 = device2.Protocols.create(Name = 'IPV4_2', ParentLink='EthIf2', ProtocolType='IPV4')

print('\n  Configure mac address')
mac_1 = EthIf1.Ethernet.Mac.update( PatternType='SINGLE', Single='00:10:94:00:00:02')
mac_2 = EthIf2.Ethernet.Mac.update( PatternType='SINGLE', Single='00:10:94:00:00:01')

print('\n  Configure ipv4 source and gateway addresses')

ipv4_1_src_addr = protocol_ipv4_1.Ipv4.SourceAddress.update(PatternType='SINGLE', Single = '10.10.10.2')
ipv4_1_gw_addr = protocol_ipv4_1.Ipv4.GatewayAddress.update(PatternType='SINGLE', Single = '10.10.10.1')

ipv4_2_src_addr = protocol_ipv4_2.Ipv4.SourceAddress.update(PatternType='SINGLE', Single = '10.10.10.1')
ipv4_2_gw_addr = protocol_ipv4_2.Ipv4.GatewayAddress.update(PatternType='SINGLE', Single = '10.10.10.2')

print('\n  Create and configure DHCPv4 client protocol')
protocol_dhcpv4_1 = device1.Protocols.create(Name = 'DHCPV4_1', ParentLink='IPV4_1', ProtocolType='DHCPV4')
dhcpv4_1 = protocol_dhcpv4_1.Dhcpv4

session_host_name_1 = protocol_dhcpv4_1.Dhcpv4.SessionHostName.update(PatternType='SINGLE', Single = 'dhcpv41')
default_host_address_prefix_length_1 = protocol_dhcpv4_1.Dhcpv4.DefaultHostAddressPrefixLength.update(PatternType='SINGLE', Single = '16')
enable_arp_server_id_1 = protocol_dhcpv4_1.Dhcpv4.EnableArpServerId.update(PatternType='SINGLE', Single = 'false')
enable_auto_retry_1 = protocol_dhcpv4_1.Dhcpv4.EnableAutoRetry.update(PatternType='SINGLE', Single = 'true')
auto_retry_attempts_1 = protocol_dhcpv4_1.Dhcpv4.AutoRetryAttempts.update(PatternType='SINGLE', Single = '3')
enable_broadcast_flag_1 = protocol_dhcpv4_1.Dhcpv4.EnableBroadcastFlag.update(PatternType='SINGLE', Single = 'false')
enable_client_mac_address_dataplane_1 = protocol_dhcpv4_1.Dhcpv4.EnableClientMacAddressDataplane.update(PatternType='SINGLE', Single = 'false')
enable_router_option_1 = protocol_dhcpv4_1.Dhcpv4.EnableRouterOption.update(PatternType='SINGLE', Single = 'false')
tos_1 = protocol_dhcpv4_1.Dhcpv4.Tos.update(PatternType='SINGLE', Single = '192')

print('\n  Create and configure DHCPv4 Server protocol')
protocol_dhcpv4_2 = device2.Protocols.create(Name = 'DHCPV4_2', ParentLink='IPV4_2', ProtocolType='DHCPV4_SERVER')
dhcpv4_2 = protocol_dhcpv4_2.Dhcpv4Server

host_name_2 = protocol_dhcpv4_2.Dhcpv4Server.HostName.update(PatternType='SINGLE', Single = 'dhcpv4server1')
tos_2 = protocol_dhcpv4_2.Dhcpv4Server.Tos.update(PatternType='SINGLE', Single = '192')
assign_strategy_2 = protocol_dhcpv4_2.Dhcpv4Server.AssignStrategy.update(PatternType='SINGLE', Single = 'GATEWAY')
decline_reserve_time_2 = protocol_dhcpv4_2.Dhcpv4Server.DeclineReserveTime.update(PatternType='SINGLE', Single = '10')
default_server_address_pool = dhcpv4_2.DefaultServerAddressPool
start_ipv4_address = default_server_address_pool.StartIpv4Address
start_ipv4_address.update(PatternType='SINGLE', Single='10.10.10.10')

print('\n  Create and configure DHCPv4 global_protocols')
global_protocols = config.GlobalProtocols
global_protocols_1 = global_protocols.Dhcpv4.create(Name='DHCPv4_Global_Config1', Ports=[port_handle1])
RequestRate_1 = global_protocols_1.RequestRate.update(PatternType='SINGLE', Single='90')
LeaseTime_1 = global_protocols_1.LeaseTime.update(PatternType='SINGLE', Single='82')
MaxMsgSize_1 = global_protocols_1.MaxMsgSize.update(PatternType='SINGLE', Single='610')
MsgTimeout_1 = global_protocols_1.MsgTimeout.update(PatternType='SINGLE', Single='75')
OutstandingSessionCount_1 = global_protocols_1.OutstandingSessionCount.update(PatternType='SINGLE', Single='11100')
ReleaseRate_1 = global_protocols_1.ReleaseRate.update(PatternType='SINGLE', Single='85')
RetryCount_1 = global_protocols_1.RetryCount.update(PatternType='SINGLE', Single='5')
SequenceType_1 = global_protocols_1.SequenceType.update(PatternType='SINGLE', Single='PARALLEL')
StartTransactionId_1 = global_protocols_1.StartTransactionId.update(PatternType='SINGLE', Single='2')
MaxDnaV4RetryCount_1 = global_protocols_1.MaxDnaV4RetryCount.update(PatternType='SINGLE', Single='1')
DnaV4Timeout_1 = global_protocols_1.DnaV4Timeout.update(PatternType='SINGLE', Single='1111')
EnableCustomOptionAssignForRelayAgents_1 = global_protocols_1.EnableCustomOptionAssignForRelayAgents.update(PatternType='SINGLE', Single='true')

print('\n  Create and configure DHCPv4 global_protocols port2')
global_protocols_2 = global_protocols.Dhcpv4.create(Name='DHCPv4_Global_Config2', Ports=[port_handle2])
request_rate_2 = global_protocols_2.RequestRate
request_rate_2.update(PatternType='SINGLE', Single='100')

print('\n  SaveasXML\n')
save_config_input = config.Save({'mode': 'VENDOR_BINARY', 'file-name': os.path.join(os.path.dirname(__file__), 'dhcpv4_sample_script.xml')})

print('\n  Start dhcpv4 server\n')
dhcpv4_server_control_input = config.Dhcpv4ServerControl({"targets": ['DHCPV4_2'], "mode": 'START'})
#print(dhcpv4_server_control_input)

print('\n  Start dhcpv4 client\n')
dhcpv4_client_control_input = config.Dhcpv4Control({"targets": ['DHCPV4_1'], "mode": 'BIND'})
#print(dhcpv4_client_control_input)

time.sleep(60)

print('\n  Get the DHCP Client statistics\n')
statistics = session.Statistics
dhcp_statistics_1 = statistics.Dhcpv4Statistics.read(DeviceName = 'device1')
#print(dhcp_statistics_1)

print('\n  Get the DHCP Server statistics\n')
dhcp_server_statistics_2 = statistics.Dhcpv4ServerStatistics.read(DeviceName = 'device2')
#print(dhcp_server_statistics_2)

current_bound_count = dhcp_statistics_1.CurrentBoundCount
current_idle_count = dhcp_statistics_1.CurrentIdleCount
current_bound_count_server = dhcp_server_statistics_2.CurrentBoundCount

if (current_bound_count == 1 and current_idle_count == 0 and current_bound_count_server == 1) :
    print('*' * 40)
    print ("\n Info :DHCPv4 session bind successful \n")
    print('*' * 40)
else :
    print ("\n <error> Failed to bind DHCPv4 session \n")
    #sys.exit();

print('\n  Disconnect ports\n')
port_control_input = config.PortControl({"targets": [], "mode": 'DISCONNECT'})

print('\n  delete session\n')
session.delete()
