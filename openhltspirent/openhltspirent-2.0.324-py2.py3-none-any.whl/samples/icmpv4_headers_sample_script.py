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

print('\n  step 3. create ipv4 raw streamblock and add ICMP echo Request header\n')
port_traffic_1 = config.PortTraffic.create(Name = 'Stream1', Source = 'Ethernet1')
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

#ipv4
frame_4 = port_traffic_1.Frames.create(Name = 'Ipv41', FrameType = 'IPV4')
ipv4_frame_1 = frame_4.Ipv4
ipv4_source_addr = ipv4_frame_1.SourceAddress.update(PatternType = 'SINGLE', Single = '10.10.10.10')
ipv4_dest_addr = ipv4_frame_1.DestinationAddress.update(PatternType = 'SINGLE', Single = '20.20.20.20')
ipv4_ttl = ipv4_frame_1.Ttl.update(PatternType = 'SINGLE', Single = '243')

#ICMP Echo Request
frame_7 = port_traffic_1.Frames.create(Name = 'icmp_echorequest', FrameType = 'ICMP_ECHO_REQUEST')
echo_request_frame_1 = frame_7.IcmpEchoRequest

code_1 = echo_request_frame_1.Code.update(PatternType = 'SINGLE', Single = '100')
checksum_1 = echo_request_frame_1.Checksum.update(PatternType = 'SINGLE', Single = '1000')
sequence_number_1 = echo_request_frame_1.SequenceNumber.update(PatternType = 'INCREMENT')
sequence_number_1_incr = sequence_number_1.Increment.update(Start = '1', Step = '2', Count = '2')
echo_data_1 = echo_request_frame_1.EchoData.update(PatternType = 'INCREMENT')
echo_data_1_incr = echo_data_1.Increment.update(Start = '1000', Step = '0001', Count = '2')
identifier_1 = echo_request_frame_1.Identifier.update(PatternType = 'SINGLE', Single = '1000')

print('\n  step 4. create ipv4 raw streamblock and add icmp echo reply header\n')

port_traffic_3 = config.PortTraffic.create(Name = 'Stream3', Source = 'Ethernet1')
stream3_handle = port_traffic_3.Name
print ("    stream3_handle: %s\n" % stream3_handle)

#Config Frame Size
frame_length_1 = port_traffic_3.FrameLength.update(LengthType = 'FIXED', Fixed = '512')

frame_1 = port_traffic_3.Frames.create(Name = 'Ethernet3', FrameType = 'ETHERNET')

# ethernet header
ethernet_frame_3 = frame_1.Ethernet

eth_src_addr_1 = ethernet_frame_3.Source.update(PatternType = 'INCREMENT')
eth_src_addr_1_incr = eth_src_addr_1.Increment.update(Start = '00:10:94:00:00:12', Step = '00:00:00:00:00:02', Count = '2')
eth_dest_addr = ethernet_frame_3.Destination.update(PatternType = 'SINGLE', Single = '00:10:94:00:00:80')

#ipv4
frame_4 = port_traffic_3.Frames.create(Name = 'Ipv43', FrameType = 'IPV4')
ipv4_frame_1 = frame_4.Ipv4
ipv4_source_addr = ipv4_frame_1.SourceAddress.update(PatternType = 'SINGLE', Single = '10.10.10.10')
ipv4_dest_addr = ipv4_frame_1.DestinationAddress.update(PatternType = 'SINGLE', Single = '20.20.20.20')
ipv4_ttl = ipv4_frame_1.Ttl.update(PatternType = 'SINGLE', Single = '243')

#ICMP ECHO REPLY

frame_7 = port_traffic_3.Frames.create(Name = 'icmp_echoreply', FrameType = 'ICMP_ECHO_REPLY')
echo_reply_frame_1 = frame_7.IcmpEchoReply

code_1 = echo_reply_frame_1.Code.update(PatternType = 'SINGLE', Single = '100')
checksum_1 = echo_reply_frame_1.Checksum.update(PatternType = 'SINGLE', Single = '1000')
sequence_number_1 = echo_reply_frame_1.SequenceNumber.update(PatternType = 'INCREMENT')
sequence_number_1_incr = sequence_number_1.Increment.update(Start = '1', Step = '2', Count = '10')
echo_data_1 = echo_reply_frame_1.EchoData.update(PatternType = 'DECREMENT')
echo_data_1_incr = echo_data_1.Increment.update(Start = '1000', Step = '0001', Count = '5')
identifier_1 = echo_reply_frame_1.Identifier.update(PatternType = 'SINGLE', Single = '1000')

print('\n  step 5. create ipv4 raw streamblock and add icmp time exceeded header\n')

port_traffic_2 = config.PortTraffic.create(Name = 'Stream2', Source = 'Ethernet2')
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

#ipv4
frame_4 = port_traffic_2.Frames.create(Name = 'Ipv42', FrameType = 'IPV4')
ipv4_frame_1 = frame_4.Ipv4
ipv4_source_addr = ipv4_frame_1.SourceAddress.update(PatternType = 'SINGLE', Single = '11.11.11.11')
ipv4_dest_addr = ipv4_frame_1.DestinationAddress.update(PatternType = 'SINGLE', Single = '22.22.22.22')
ipv4_ttl = ipv4_frame_1.Ttl.update(PatternType = 'SINGLE', Single = '243')

#ICMP_TIME_EXCEEDED
frame_7 = port_traffic_2.Frames.create(Name = 'icmp_time_exceeded', FrameType = 'ICMP_TIME_EXCEEDED')
icmp_time_exceeded_frame_1 = frame_7.IcmpTimeExceeded

code_1 = icmp_time_exceeded_frame_1.Code.update(PatternType = 'SINGLE', Single = '100')
ipv4_source_address_3 = icmp_time_exceeded_frame_1.Ipv4SourceAddress.update(PatternType = 'SINGLE', Single = '10.10.10.10')
ipv4_destination_address = icmp_time_exceeded_frame_1.Ipv4DestinationAddress.update(PatternType = 'INCREMENT')
ipv4_destination_address_3_incr = ipv4_destination_address.Increment.update(Start = '20.20.20.20', Step = '0.0.0.4', Count = '2')
reserved_bit = icmp_time_exceeded_frame_1.Ipv4ReservedBit.update(PatternType = 'SINGLE', Single = '1')
ipv4_checksum = icmp_time_exceeded_frame_1.Ipv4Checksum.update(PatternType = 'SINGLE', Single = '100')
unused = icmp_time_exceeded_frame_1.Unused.update(PatternType = 'SINGLE', Single = '2000')

print('\n  step 6. create ipv4 raw streamblock and add icmp redirect header\n')

port_traffic_4 = config.PortTraffic.create(Name = 'Stream4', Source = 'Ethernet2')
stream4_handle = port_traffic_4.Name
print ("    stream4_handle: %s\n" % stream4_handle)

#Config Frame Size
frame_length_1 = port_traffic_4.FrameLength.update(LengthType = 'FIXED', Fixed = '512')

frame_1 = port_traffic_4.Frames.create(Name = 'Ethernet4', FrameType = 'ETHERNET')

# ethernet header
ethernet_frame_1 = frame_1.Ethernet

eth_src_addr_1 = ethernet_frame_1.Source.update(PatternType = 'INCREMENT')
eth_src_addr_1_incr = eth_src_addr_1.Increment.update(Start = '00:10:94:00:00:12', Step = '00:00:00:00:00:02', Count = '10')
eth_dest_addr = ethernet_frame_1.Destination.update(PatternType = 'SINGLE', Single = '00:10:94:00:00:80')

#ipv4
frame_4 = port_traffic_4.Frames.create(Name = 'Ipv44', FrameType = 'IPV4')
ipv4_frame_1 = frame_4.Ipv4
ipv4_source_addr = ipv4_frame_1.SourceAddress.update(PatternType = 'SINGLE', Single = '11.11.11.11')
ipv4_dest_addr = ipv4_frame_1.DestinationAddress.update(PatternType = 'SINGLE', Single = '22.22.22.22')
ipv4_ttl = ipv4_frame_1.Ttl.update(PatternType = 'SINGLE', Single = '243')

#ICMP redirect
frame_1 = port_traffic_4.Frames.create(Name = 'icmp_redirect', FrameType = 'ICMP_REDIRECT')
icmp_redirect_frame_1 = frame_1.IcmpRedirect
code = icmp_redirect_frame_1.Code.update(PatternType = 'SINGLE', Single = '100')
gateway_address = icmp_redirect_frame_1.GatewayAddress.update(PatternType = 'SINGLE', Single = '12.1.1.1')
ipv4_source_address = icmp_redirect_frame_1.Ipv4SourceAddress.update(PatternType = 'INCREMENT')
ipv4_source_address_incr = ipv4_source_address.Increment.update(Start = '10.10.10.10', Step = '0.0.0.2', Count = '2')
ipv4_destination_address = icmp_redirect_frame_1.Ipv4DestinationAddress.update(PatternType = 'SINGLE', Single = '20.20.20.20')
reserved_bit = icmp_redirect_frame_1.Ipv4ReservedBit.update(PatternType = 'SINGLE', Single = '1')
ipv4_checksum = icmp_redirect_frame_1.Ipv4Checksum.update(PatternType = 'SINGLE', Single = '100')
ipv4_df_bit = icmp_redirect_frame_1.Ipv4DfBit.update(PatternType = 'INCREMENT')
ipv4_df_bit_incr = ipv4_df_bit.Increment.update(Start = '1', Step = '1', Count = '1')

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

streamblock_list = [stream1_handle, stream2_handle, stream3_handle, stream4_handle]

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