## Test Steps:
    #Step 1: Create a session and connect to two back to back stc ports
    #Step 2: Configue 2 raw streamblocks on each port with icmpv4 headers - echo request, reply, time exceeded and redirect
    #Step 3: Save the configuration as an XML file
    #Step 4: Start the traffic
    #Step 5: Validate the traffic stats
    #Step 6: Delete session and release resources

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

print('\n  step 3. create ipv6 raw streamblock and add ICMP echo Reply header\n')
port_traffic_1 = config.PortTraffic.create(Name = 'Stream1', Source = port_handle1)
stream1_handle = port_traffic_1.Name
print ("    stream1_handle: %s\n" % stream1_handle)

#Config Frame Size
frame_length_1 = port_traffic_1.FrameLength.update(LengthType = 'FIXED', Fixed = '512')

frame_1 = port_traffic_1.Frames.create(Name = 'Ethernet1', FrameType = 'ETHERNET')

# ethernet header
ethernet_frame_1 = frame_1.Ethernet

eth_src_addr_1 = ethernet_frame_1.Source.update(PatternType = 'INCREMENT')
eth_src_addr_1_incr = eth_src_addr_1.Increment.update(Start = '00:10:94:00:00:12', Step = '00:00:00:00:00:02', Count = '2')
eth_dest_addr = ethernet_frame_1.Destination.update(PatternType = 'SINGLE', Single = '00:10:94:00:00:80')

#ipv6
frame_6 = port_traffic_1.Frames.create(Name = 'Ipv61', FrameType = 'IPV6')
ipv6_frame_1 = frame_6.Ipv6
ipv6_source_addr = ipv6_frame_1.SourceAddress.update(PatternType = 'SINGLE', Single = '2000::1')
ipv6_dest_addr = ipv6_frame_1.DestinationAddress.update(PatternType = 'SINGLE', Single = '3000::1')

#ICMPV6 ECHO REPLY
frame_3 = port_traffic_1.Frames.create(Name = 'icmpv6_echoreply', FrameType = 'ICMPV6_ECHO_REPLY')

echo_icmpv6reply_frame_1 = frame_3.Icmpv6EchoReply
code_1 = echo_icmpv6reply_frame_1.Code.update(PatternType = 'SINGLE', Single = '100')
checksum_1 = echo_icmpv6reply_frame_1.Checksum.update(PatternType = 'SINGLE', Single = '1000')
sequence_number_1 = echo_icmpv6reply_frame_1.SequenceNumber.update(PatternType = 'INCREMENT')
sequence_number_1_incr = sequence_number_1.Increment.update(Start = '1', Step = '2', Count = '2')
echo_data_1 = echo_icmpv6reply_frame_1.EchoData.update(PatternType = 'DECREMENT')
echo_data_1_incr = echo_data_1.Decrement.update(Start = '1000', Step = '0001', Count = '5')
identifier_1 = echo_icmpv6reply_frame_1.Identifier.update(PatternType = 'SINGLE', Single = '3000')

print('\n  step 4. create ipv6 raw streamblock and add ICMP Destination Unreachable header\n')
port_traffic_2 = config.PortTraffic.create(Name = 'Stream2', Source = port_handle1)
stream2_handle = port_traffic_2.Name
print ("    stream2_handle: %s\n" % stream2_handle)

#Config Frame Size
frame_length_1 = port_traffic_2.FrameLength.update(LengthType = 'FIXED', Fixed = '512')
frame_1 = port_traffic_2.Frames.create(Name = 'Ethernet2', FrameType = 'ETHERNET')

# ethernet header
ethernet_frame_1 = frame_1.Ethernet

eth_src_addr_1 = ethernet_frame_1.Source.update(PatternType = 'INCREMENT')
eth_src_addr_1_incr = eth_src_addr_1.Increment.update(Start = '00:10:94:00:00:12', Step = '00:00:00:00:00:02', Count = '2')
eth_dest_addr = ethernet_frame_1.Destination.update(PatternType = 'SINGLE', Single = '00:10:94:00:00:80')

#ipv6
frame_6 = port_traffic_2.Frames.create(Name = 'Ipv62', FrameType = 'IPV6')
ipv6_frame_1 = frame_6.Ipv6
ipv6_source_addr = ipv6_frame_1.SourceAddress.update(PatternType = 'SINGLE', Single = '2000::1')
ipv6_dest_addr = ipv6_frame_1.DestinationAddress.update(PatternType = 'SINGLE', Single = '3000::1')

#ICMPV6_DESTINATION_UNREACHABLE
frame_3 = port_traffic_2.Frames.create(Name = 'icmpv6_destination_unreachable', FrameType = 'ICMPV6_DESTINATION_UNREACHABLE')
echo_icmpv6_dest_unreach_1 = frame_3.Icmpv6DestinationUnreachable
code_1 = echo_icmpv6_dest_unreach_1.Code.update(PatternType = 'SINGLE', Single = '3')
checksum_1 = echo_icmpv6_dest_unreach_1.Checksum.update(PatternType = 'SINGLE', Single = '1000')
ipv6_source_address_1 = echo_icmpv6_dest_unreach_1.Ipv6SourceAddress.update(PatternType = 'INCREMENT')
ipv6_source_address_1_incr = ipv6_source_address_1.Increment.update(Start = '3000::21', Step = '0000::1', Count = '4')
destination_address_1 = echo_icmpv6_dest_unreach_1.Ipv6DestinationAddress.update(PatternType = 'SINGLE', Single = '4000::1')
ipv6_gateway_address_1 = echo_icmpv6_dest_unreach_1.Ipv6GatewayAddress.update(PatternType = 'SINGLE', Single = '3000::1')
ipv6_hop_limit_1 = echo_icmpv6_dest_unreach_1.Ipv6HopLimit.update(PatternType = 'DECREMENT')
ipv6_hop_limit_1_incr = ipv6_hop_limit_1.Decrement.update(Start = '100', Step = '2', Count = '2')
traffic_class_1 = echo_icmpv6_dest_unreach_1.Ipv6TrafficClass.update(PatternType = 'SINGLE', Single = '10')
ipv6_next_header_1 = echo_icmpv6_dest_unreach_1.Ipv6NextHeader.update(PatternType = 'SINGLE', Single = '59')
ipv6_flow_label_1 = echo_icmpv6_dest_unreach_1.Ipv6FlowLabel.update(PatternType = 'SINGLE', Single = '1000')

print('\n  step 4. create ipv6 raw streamblock and add icmpv6 time exceeded header\n')

port_traffic_3 = config.PortTraffic.create(Name = 'Stream3', Source = port_handle2)
stream3_handle = port_traffic_3.Name
print ("    stream3_handle: %s\n" % stream3_handle)

#Config Frame Size
frame_length_1 = port_traffic_3.FrameLength.update(LengthType = 'FIXED', Fixed = '512')
frame_1 = port_traffic_3.Frames.create(Name = 'Ethernet3', FrameType = 'ETHERNET')

# ethernet header
ethernet_frame_1 = frame_1.Ethernet

eth_src_addr_1 = ethernet_frame_1.Source.update(PatternType = 'INCREMENT')
eth_src_addr_1_incr = eth_src_addr_1.Increment.update(Start = '00:10:94:00:00:12', Step = '00:00:00:00:00:02', Count = '2')
eth_dest_addr = ethernet_frame_1.Destination.update(PatternType = 'SINGLE', Single = '00:10:94:00:00:80')

#ipv6
frame_6 = port_traffic_3.Frames.create(Name = 'Ipv63', FrameType = 'IPV6')
ipv6_frame_1 = frame_6.Ipv6
ipv6_source_addr = ipv6_frame_1.SourceAddress.update(PatternType = 'SINGLE', Single = '2000::1')
ipv6_dest_addr = ipv6_frame_1.DestinationAddress.update(PatternType = 'SINGLE', Single = '3000::1')

#ICMPV6_TIME_EXCEEDED
frame_3 = port_traffic_3.Frames.create(Name = 'icmpv6_time_exceeded', FrameType = 'ICMPV6_TIME_EXCEEDED')

icmpv6_time_exceeded_1 = frame_3.Icmpv6TimeExceeded
code_1 = icmpv6_time_exceeded_1.Code.update(PatternType = 'SINGLE', Single = '100')
checksum_1 = icmpv6_time_exceeded_1.Checksum.update(PatternType = 'SINGLE', Single = '1000')
ipv6_source_address_1 = icmpv6_time_exceeded_1.Ipv6SourceAddress.update(PatternType = 'INCREMENT')
ipv6_source_address_1_incr = ipv6_source_address_1.Increment.update(Start = '3000::21', Step = '0000::1', Count = '5')
destination_address_1 = icmpv6_time_exceeded_1.Ipv6DestinationAddress.update(PatternType = 'SINGLE', Single = '4000::1')
ipv6_gateway_address_1 = icmpv6_time_exceeded_1.Ipv6GatewayAddress.update(PatternType = 'SINGLE', Single = '3000::1')
ipv6_hop_limit_1 = icmpv6_time_exceeded_1.Ipv6HopLimit.update(PatternType = 'DECREMENT')
ipv6_hop_limit_1_incr = ipv6_hop_limit_1.Decrement.update(Start = '100', Step = '2', Count = '5')
traffic_class_1 = icmpv6_time_exceeded_1.Ipv6TrafficClass.update(PatternType = 'SINGLE', Single = '10')
ipv6_next_header_1 = icmpv6_time_exceeded_1.Ipv6NextHeader.update(PatternType = 'SINGLE', Single = '59')
ipv6_flow_label_1 = icmpv6_time_exceeded_1.Ipv6FlowLabel.update(PatternType = 'SINGLE', Single = '1000')

print('\n    save config in xml/json format.\n')
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

print('\n  step 7. start traffic\n')

streamblock_list = [stream1_handle, stream2_handle, stream3_handle]

config.TrafficControl( {"targets": streamblock_list , "mode": 'START'})

time.sleep(5)

print('\n  step 8. stop traffic\n')
config.TrafficControl( {"targets": streamblock_list , "mode": 'STOP'})

print('\n  step 9. get statistics\n')
statistics = session.Statistics

port_list = [port_handle1, port_handle2]

for stream in streamblock_list:
    statistics_traffic = statistics.PortTraffic.read(Name = stream)
    tx_frames = statistics_traffic.TxFrames
    rx_frames = statistics_traffic.RxFrames
    if (tx_frames == rx_frames):
        print ("\n    Info: Traffic is transmitted successfully \n")
        print ("    TxFrames: %s \n" % tx_frames)
        print ("    RxFrames: %s \n" % rx_frames)
    else :
        print ("\n    <error> Traffic is not transmitted successfully")
        print ("    TxFrames: %s \n" % tx_frames)
        print ("    RxFrames: %s \n" % rx_frames)

for port in port_list:
    statistics_traffic = statistics.Port.read(port)
    print('\n    %s stats: %s \n' % (port, statistics_traffic.TxFrames))
    print('    %s stats: %s \n' % (port, statistics_traffic.RxFrames))

#disconnect ports
print('\n  step 10. Disconnect ports and delete session\n')
port_control_input = config.PortControl({"targets": [port_handle1, port_handle2], "mode": 'DISCONNECT'})

session.delete()
try:
    session = openhltest.Sessions.read(Name = sessionname)
except:
    print("    Deleted session - %s\n" % sessionname)