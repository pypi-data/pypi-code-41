# test stpes:
#  1. create and connect two ports

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
print("protnumber",portnumber)

print("ohtweb server ip", serverip)
print("chassis ip: %s, %s" % (chassisip1, chassisip2))
    
print("session name", sessionname)
print("portnumber",portnumber)

# connect openhltest server
LOG_TO_FILE = True
if True == LOG_TO_FILE:
    log_file = '.'.join(__file__.split(os.path.sep)[-1].split('.')[0:-1]) + ".log"
else:
    # Log to standard console
    log_file = None
transport = HttpTransport(serverip + ":" + portnumber, log_file_name= log_file)
#transport = HttpTransport()
transport.set_debug_level()
openhltest = transport.OpenHlTest

try:
    session = openhltest.Sessions.read(Name = sessionname)
    session.delete()
    print("######## Deleted existing session with name %s ######### \n" % sessionname)
except:
    print("######## There is no session exist with name %s ######## \n" % sessionname)

# create session : "SampleTest"
session = openhltest.Sessions.create(Name = sessionname)
config = session.Config

#  step 1. create and connect one ports
print('\n  step 1. create and connect one ports\n')
port1 = config.Ports.create(Name='Ethernet1', Location=chassisip1)
port2 = config.Ports.create(Name='Ethernet2', Location=chassisip2)

input = {"command":'stc.get("project1",children-port)'}
ret = config.Invoke(input)
print('Cur ports: %s' % ret['retvalue'])

print('\n  step 2. create ipv4 raw streamblock\n')
port_traffic_1 = config.PortTraffic.create( Name = 'Stream1', Source='Ethernet1')
#Config Frame Size
frame_length_1 = port_traffic_1.FrameLength.update(LengthType='FIXED', Fixed=512)
frame_1 = port_traffic_1.Frames.create(Name = 'Ethernet1', FrameType = 'ETHERNET')

# ethernet header
ethernet_frame_1 = frame_1.Ethernet
eth_src_addr_1 = ethernet_frame_1.Source.update( PatternType='INCREMENT')
eth_src_addr_1.Increment.update( Start='00:10:94:00:00:12', Step='00:00:00:00:00:02', Count = '10')
eth_dest_addr = ethernet_frame_1.Destination.update( PatternType='SINGLE', Single= '00:10:94:00:00:80')

#ipv4
frame_4 = port_traffic_1.Frames.create(Name = 'Ipv41', FrameType = 'IPV4')
ipv4_source_addr = frame_4.Ipv4.SourceAddress.update( PatternType='SINGLE', Single= '10.10.10.10')
ipv4_dest_addr = frame_4.Ipv4.DestinationAddress.update(  PatternType='SINGLE', Single= '10.10.10.10')

ipv4_ttl = frame_4.Ipv4.Ttl.update( PatternType='SINGLE', Single= '243')

#OSPFv2 Hello
frame_1 = port_traffic_1.Frames.create(Name = 'ospf_hello1', FrameType = 'OSPFV2_HELLO')

hello_frame_1 = frame_1.Ospfv2Hello

designated_router = hello_frame_1.DesignatedRouterAddress.update( PatternType='SINGLE', Single= '11.1.1.1')
backup_designated_router = hello_frame_1.BackupDesignatedRouterAddress.update( PatternType='SINGLE', Single= '12.1.1.1')
area_id = hello_frame_1.AreaId.update( PatternType = 'INCREMENT')
area_id_incr = area_id.Increment.update(  Start='10.1.1.1', Step='0.0.0.2', Count = '10')
router_id = hello_frame_1.RouterId.update(PatternType='SINGLE', Single= '13.1.1.1')
reserved_bit_7 = hello_frame_1.OptionsReservedBit7.update( PatternType='SINGLE', Single='1')
reserved_bit_6 = hello_frame_1.OptionsReservedBit6.update( PatternType='SINGLE', Single='1')
options_dc_bit = hello_frame_1.OptionsDcBit.update( PatternType='SINGLE', Single='1')
options_dc_bit = hello_frame_1.OptionsMcBit.update( PatternType='SINGLE', Single='1')
auth_type = hello_frame_1.AuthType.update( PatternType='SINGLE', Single='MD5')
auth_value1 = hello_frame_1.AuthValue1.update( PatternType='SINGLE', Single='254')
auth_value2 = hello_frame_1.AuthValue2.update( PatternType='SINGLE', Single='10000000')
neighbors = hello_frame_1.Neighbors.create(Name = 'neighbors_1')
neighbors_id = neighbors.NeighborsId.update( PatternType='SINGLE', Single='1.1.1.1')

#openhltest.Licenseserver({"server": ['10.61.43.250'], 'backupserver': ['10.61.43.251']})
config.Commit()

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

print('\n  step 4. strat traffic\n')
traffic_control_input1 = config.TrafficControl( {"targets": ['Stream1'], "mode": 'START'})

time.sleep(5)

print('\n  step 6. stop traffic\n')
traffic_control_input1 = config.TrafficControl({"targets": ['Stream1'], "mode": 'STOP'})

print('\n  step 7. get statistics\n')
statistics = session.Statistics

statistics_traffic = statistics.PortTraffic.read( Name='Stream1')
print('%s \n' % statistics_traffic)
print('%s \n' % statistics_traffic.TxFrames)
print('%s \n' % statistics_traffic.RxFrames)

statistics_traffic = statistics.Port.read( Name='Ethernet1')
print('%s \n' % statistics_traffic)
print('%s \n' % statistics_traffic.TxFrames)
print('%s \n' % statistics_traffic.RxFrames)

#disconnect ports
port_control_input = config.PortControl({"targets": ['Ethernet1', 'Ethernet2'], "mode": 'DISCONNECT'})

print('\n  step 9. delete session\n')
session.delete()
