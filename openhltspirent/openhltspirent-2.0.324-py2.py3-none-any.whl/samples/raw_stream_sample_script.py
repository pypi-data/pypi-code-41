# Test steps:
#  1. Connect to openhltest server and create a session.
#  2. Create and connect two back to back stc ports
#  3. Create ipv4 raw streamblock by adding inner and outer vlans and tcp header on port1.
#  4. Create ipv6 raw streamblock by adding inner and outer vlans and udp header on port2.
#  5. Start and stop traffic on both ports.
#  6. Get and validate received statistics.
#  7. Disconnect ports and delete session.

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

print('\n  step 3. create ipv4 raw streamblock\n')
port_traffic_1 = config.PortTraffic.create( Name = 'Stream1', Source = port_handle1)
streamblock1 = port_traffic_1.Name
print("    StreamblockHandle1: %s" % streamblock1)

#Config Frame Size
frame_length_1 = port_traffic_1.FrameLength.update(LengthType='FIXED', Fixed=512)
frame_1 = port_traffic_1.Frames.create(Name = 'Ethernet1', FrameType = 'ETHERNET')

# ethernet header
ethernet_frame_1 = frame_1.Ethernet
eth_src_addr_1 = ethernet_frame_1.Source.update( PatternType='INCREMENT')
eth_src_addr_1.Increment.update( Start='00:10:94:00:00:12', Step='00:00:00:00:00:02', Count = '10')
eth_dest_addr = ethernet_frame_1.Destination.update( PatternType='SINGLE', Single= '00:10:94:00:00:80')

# outer Vlan
# Vlan

frame_2 = port_traffic_1.Frames.create(Name = 'Vlan1', FrameType = 'VLAN')
priority1 = frame_2.Vlan.Priority.update(PatternType='SINGLE', Single='3')
priority1.Increment.update(Start='1')
id = frame_2.Vlan.Id.update(PatternType='SINGLE', Single='1')
id.Increment.update(Start='1')

# Inner Vlan
# Vlan

frame_3 = port_traffic_1.Frames.create(Name = 'Vlan2', FrameType = 'VLAN')
priority2 = frame_3.Vlan.Priority.update(PatternType='SINGLE', Single='6')
priority2.Increment.update(Start='1')
id2 = frame_3.Vlan.Id.update(PatternType='SINGLE', Single='2')
id2.Increment.update(Start='2')

#ipv4
frame_4 = port_traffic_1.Frames.create(Name = 'Ipv41', FrameType = 'IPV4')
ipv4_source_addr = frame_4.Ipv4.SourceAddress.update( PatternType='VALUE_LIST', ValueList = ['1.1.1.1','2.2.2.2'])
ipv4_dest_addr = frame_4.Ipv4.DestinationAddress.update(  PatternType='SINGLE', Single= '20.20.20.20')
ipv4_ttl = frame_4.Ipv4.Ttl.update( PatternType='SINGLE', Single= '243')

# tcp
frame_5 = port_traffic_1.Frames.create(Name = 'Tcp1', FrameType = 'TCP')
tcp_source_port = frame_5.Tcp.SourcePort.update(PatternType = 'SINGLE', Single = '1111')
tcp_dest_port = frame_5.Tcp.DestinationPort.update(PatternType = 'SINGLE', Single = '2222')
tcp_checksum = frame_5.Tcp.Checksum.update(PatternType = 'SINGLE', Single = '98')
tcp_ack_num = frame_5.Tcp.AcknowledgementNumber.update(PatternType = 'SINGLE', Single = '234569')
tcp_header_length = frame_5.Tcp.HeaderLength.update(PatternType = 'SINGLE', Single = '8')
tcp_reserved = frame_5.Tcp.Reserved.update(PatternType = 'SINGLE', Single = '33')
tcp_sequence_number = frame_5.Tcp.SequenceNumber.update(PatternType = 'SINGLE', Single = '123455')
tcp_urgent_pointer = frame_5.Tcp.UrgentPointer.update(PatternType = 'SINGLE', Single = '9')
tcp_window_size = frame_5.Tcp.UrgentPointer.update(PatternType = 'SINGLE', Single = '2046')
tcp_acknowledgement_flag = frame_5.Tcp.AcknowledgementFlag.update(PatternType = 'SINGLE', Single = '0')
tcp_fin_flag = frame_5.Tcp.FinFlag.update(PatternType = 'SINGLE', Single = '0')
tcp_push_flag = frame_5.Tcp.PushFlag.update(PatternType = 'SINGLE', Single = '1')
tcp_reset_flag = frame_5.Tcp.ResetFlag.update(PatternType = 'SINGLE', Single = '1')
tcp_sync_flag = frame_5.Tcp.SyncFlag.update(PatternType = 'SINGLE', Single = '1')
tcp_urgent_flag = frame_5.Tcp.UrgentFlag.update(PatternType = 'SINGLE', Single = '1')

print('\n  step 4. create ipv6 raw streamblock\n')
# create IPv6 raw streamblock
port_traffic_2 = config.PortTraffic.create(Name = 'Stream2', Source = port_handle2)
streamblock2 = port_traffic_2.Name
print("    StreamblockHandle2: %s" % streamblock2)

#Config Frame Size
frame_length_1 = port_traffic_2.FrameLength.update(LengthType='FIXED', Fixed='256')

frame_1 = port_traffic_2.Frames.create(Name = 'Ethernet2', FrameType = 'ETHERNET')

# ethernet header
ethernet_frame_1 = frame_1.Ethernet
eth_source_addr = ethernet_frame_1.Source.update(PatternType = 'SINGLE', Single = '00:10:94:00:00:12')
eth_dest_addr = ethernet_frame_1.Destination.update( PatternType='SINGLE', Single= '00:10:94:00:00:23')

# outer Vlan
# Vlan

frame_2 = port_traffic_2.Frames.create(Name = 'Vlan3', FrameType = 'VLAN')
priority1 = frame_2.Vlan.Priority.update(PatternType='SINGLE', Single='3')
priority1.Increment.update(Start='1')
id = frame_2.Vlan.Id.update(PatternType='SINGLE', Single='100')
id.Increment.update(Start='1')

# Inner Vlan
# Vlan

frame_3 = port_traffic_2.Frames.create(Name = 'Vlan4', FrameType = 'VLAN')
priority2 = frame_3.Vlan.Priority.update(PatternType='SINGLE', Single='6')
priority2.Increment.update(Start='1')
id2 = frame_3.Vlan.Id.update(PatternType='SINGLE', Single='200')
id2.Increment.update(Start='1')

# ipv6
frame_4 = port_traffic_2.Frames.create(Name = 'Ipv61', FrameType = 'IPV6')
ipv6_source_addr = frame_4.Ipv6.SourceAddress.update( PatternType='INCREMENT')
ipv6_source_addr.Increment.update(Start = '3000::2', Step = '::4', Count = '13')
ipv6_dest_addr = frame_4.Ipv6.DestinationAddress.update( PatternType='SINGLE', Single= '4000::3')


# udp
frame_5 = port_traffic_2.Frames.create( Name = 'Udp1', FrameType = 'UDP')

udp_source_port = frame_5.Udp.SourcePort.update(PatternType='SINGLE', Single= '1023')
udp_dst_port = frame_5.Udp.SourcePort.update(PatternType='SINGLE', Single= '1025')

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

print('\n  step 5. start traffic\n')
traffic_control_input1 = config.TrafficControl( {"targets": [streamblock1 , streamblock2], "mode": 'START'})

time.sleep(5)

print('\n  step 6. stop traffic\n')
traffic_control_input1 = config.TrafficControl({"targets": [streamblock1 , streamblock2], "mode": 'STOP'})

print('\n  step 7. get statistics\n')
statistics = session.Statistics

statistics_traffic = statistics.PortTraffic.read( Name = streamblock1)

tx_stats = statistics_traffic.TxFrames
rx_stats = statistics_traffic.RxFrames

if (tx_stats == rx_stats):
    print("    Received traffic successfully. Number of Rx and Tx frames are matched\n")
    print("    TxFrames: %s" % statistics_traffic.TxFrames)
    print("    RxFrames: %s\n" % statistics_traffic.RxFrames)
else :
    print("    <error>: Failed to receive traffic. Mismatch in Rx and Tx frames\n")
    print(statistics_traffic)

statistics_traffic = statistics.Port.read( Name = port_handle1)

if (statistics_traffic.RxFrames > '0'):
    print("    Received port statistics successfully\n")
    print("    RxFrames: %s\n" % statistics_traffic.RxFrames)
else :
    print("    <error>: Failed to receive port statistics\n")
    print(statistics_traffic)

statistics_traffic = statistics.PortTraffic.read( Name = streamblock2)

tx_stats = statistics_traffic.TxFrames
rx_stats = statistics_traffic.RxFrames

if (tx_stats == rx_stats):
    print("    Received traffic successfully. Number of Rx and Tx frames are matched \n")
    print("    TxFrames: %s" % statistics_traffic.TxFrames)
    print("    RxFrames: %s\n" % statistics_traffic.RxFrames)
else :
    print("    <error>: Failed to receive traffic. Mismatch in Rx and Tx frames\n")
    print(statistics_traffic)

statistics_traffic = statistics.Port.read( Name = port_handle2)


if (statistics_traffic.RxFrames > '0'):
    print("    Received port statistics successfully\n")
    print("    RxFrames: %s\n" % statistics_traffic.RxFrames)
else :
    print("    <error>: Failed to receive port statistics\n")
    print(statistics_traffic)

#disconnect ports
port_control_input = config.PortControl({"targets": [port_handle1, port_handle2], "mode": 'DISCONNECT'})

print('\n  step 8. Disconnect ports and delete session\n')
session.delete()
try:
    session = openhltest.Sessions.read(Name = sessionname)
except:
    print("    Deleted session - %s\n" % sessionname)
