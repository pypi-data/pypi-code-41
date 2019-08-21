# Test steps:
#  1. Connect to openhltest server and create a session.
#  2. Create and connect two back to back stc ports
#  3. Create ipv4 raw streamblock
#  4. Create ipv6 raw streamblock
#  5. Create devices under the port1, protocol stack: eth/ipv4
#  6. Create two devices under the port2, protocol stack: eth/ipv4
#  7. Create devices under the port1, protocol stack: eth/ipv6
#  8. Create two devices under the port2, protocol stack: eth/ipv6
#  9. Create BOUND streamblock - IPv4 endpoints.
#  10. Create BOUND streamblock - IPv6 endpoints
#  11. Start traffic and verify the traffic stats
#  12. Stop traffic and verify the traffic stats
#  13. Disconnect ports and delete session.

from __future__ import print_function
from openhltspirent.httptransport import HttpTransport

import time
import os,sys
import json

step = 0

def printStep(msg):
    global step
    step += 1
    print('\n  step ' + str(step) +'. '+ str(msg) +'\n')

def pprint_output(output):
    print("\npretty print:")
    for table in ["item-table", "flow-table"]:
        if table in output:
            print(table, ":")
            print(output[table])

    for stats in ["item-stats", "flow-stats"]:
        if stats in output:
            print(stats, ":")
            print(json.dumps(output[stats], indent=4))

# Commandline arguments
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

printStep("create a session")
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
printStep("create and connect ports")
port1 = config.Ports.create(Name='Ethernet Port 1', Location=chassisip1)
port_handle1 = port1.Name
print("    port_handle1: %s\n" % port_handle1)

port2 = config.Ports.create(Name='Ethernet Port 2', Location=chassisip2)
port_handle2 = port2.Name
print("    port_handle2: %s\n" % port_handle2)
config.PortControl({"targets": [], "mode": 'CONNECT'})

################### create raw streamblocks ###################
print('\n  Create Raw Steramblock\n')
printStep('Create ipv4 raw streamblock')
port_traffic_1 = config.PortTraffic.create( Name = 'IPV4Stream1 raw', Source = port_handle1)

printStep('Create ipv6 raw streamblock')
# create IPv6 raw streamblock
port_traffic_2 = config.PortTraffic.create( Name = 'IPV6Stream1 raw', Source = port_handle2)

################### create bound streamblocks ###################
print('\n  Create Bound Steramblock\n')
printStep('Create devices under the port1, protocol stack: eth/ipv4.\n')
device_group_east_1 = config.DeviceGroups.create(Name = 'EastSide Device group1', Ports = [port_handle1])

# create devices: 'Devices 1' under the device_group_east
devices_1 = device_group_east_1.Devices.create(Name = 'Device 1', DeviceCountPerPort = '2')

# create protocols ethernet
protocol_eth_1 = devices_1.Protocols.create(Name = 'Ethernet 1', ProtocolType = 'ETHERNET')

# create protocols IPv4
protocol_ipv4_1 = devices_1.Protocols.create(Name = 'IPV4 1', ProtocolType = 'IPV4', ParentLink = 'Ethernet 1')

# config ipv4 address
ipv4_1 = protocol_ipv4_1.Ipv4
ipv4_1_src_addr = ipv4_1.SourceAddress.update(PatternType = 'SINGLE', Single = '192.85.1.3')
ipv4_1_gw_addr = ipv4_1.GatewayAddress.update(PatternType = 'SINGLE', Single = '192.85.1.13')

# get ipv4 source address value
print('\n      IPV4 1 source address : %s \n' % ipv4_1_src_addr.Single)

printStep('Create two devices under the port2, protocol stack: eth/ipv4.')

# config device groups 'West Side - Device group 1' unde the port 'Ethernet - 002'
device_group_west_1 = config.DeviceGroups.create(Name = 'WestSide Device group1', Ports = [port_handle2])

# create 'Device 2' under the device_group_west 
devices_2 = device_group_west_1.Devices.create(Name = 'Device 2', DeviceCountPerPort = '2')

# create protocol ethernet
protocol_eth_2 = devices_2.Protocols.create(Name = 'Ethernet 2', ProtocolType = 'ETHERNET')

# create protocol IPv4
protocol_ipv4_2 = devices_2.Protocols.create(Name = 'IPV4 2', ProtocolType = 'IPV4', ParentLink = 'Ethernet 2')

# config ipv4 address
ipv4_2 = protocol_ipv4_2.Ipv4
ipv4_2_src_addr = ipv4_2.SourceAddress.update(PatternType = 'SINGLE', Single = '192.85.1.13')
ipv4_2_gw_addr = ipv4_2.GatewayAddress.update(PatternType = 'SINGLE', Single = '192.85.1.3')


printStep('Create devices under the port1, protocol stack: eth/ipv6.')
device_group_east_2 = config.DeviceGroups.create(Name = 'EastSide Device group2', Ports = [port_handle1])

# create devices: 'Devices 1' under the device_group_east
devices_3 = device_group_east_2.Devices.create(Name = 'Device 3', DeviceCountPerPort = '2')

# create protocols ethernet
protocol_eth_3 = devices_3.Protocols.create(Name = 'Ethernet 3', ProtocolType = 'ETHERNET')

# create protocols IPv6
protocol_ipv6_1 = devices_3.Protocols.create(Name = 'IPV61', ProtocolType = 'IPV6', ParentLink = 'Ethernet 3')

# config ipv6 address
ipv6_1 = protocol_ipv6_1.Ipv6
ipv6_1_src_addr = ipv6_1.SourceAddress.update(PatternType = 'SINGLE', Single = '2000::10')
ipv6_1_gw_addr = ipv6_1.GatewayAddress.update(PatternType = 'SINGLE', Single = '2000::1')

# get ipv6 source address value
print('\n      IPV6 1 source address : %s \n' % ipv6_1_src_addr.Single)

printStep('Create two devices under the port2, protocol stack: eth/ipv6.')

# config device groups 'West Side - Device group 1' unde the port 'Ethernet - 002'
device_group_west_2 = config.DeviceGroups.create(Name = 'WestSide Device group2', Ports = [port_handle2])

devices_4 = device_group_west_2.Devices.create(Name = 'Device 4', DeviceCountPerPort = '2')

# create protocol ethernet
protocol_eth_4 = devices_4.Protocols.create(Name = 'Ethernet 4', ProtocolType = 'ETHERNET')

# create protocol IPv6
protocol_ipv6_2 = devices_4.Protocols.create(Name = 'IPV62', ProtocolType = 'IPV6', ParentLink = 'Ethernet 4')

# config ipv6 address
ipv6_2 = protocol_ipv6_2.Ipv6

ipv6_2_src_addr = ipv6_2.SourceAddress.update(PatternType = 'SINGLE', Single = '2000::1')
ipv6_2_gw_addr = ipv6_2.GatewayAddress.update(PatternType = 'SINGLE', Single = '2000::10')

# create BOUND streamblock - IPv4 endpoints
device_traffic_1 = config.DeviceTraffic.create(Name = 'IPV4Stream1 bound', Encapsulation = 'IPV4', Sources = ['IPV4 1'], Destinations = ['IPV4 2'], BiDirectional = 'true')

#Config Frame Size
frame_length_1 = device_traffic_1.FrameLength.update(LengthType = 'FIXED', Fixed = '512')

# create BOUND streamblock - IPv6 endpoints
device_traffic_2 = config.DeviceTraffic.create(Name = 'IPV6Stream1 bound', Encapsulation = 'IPV6', Sources = ['Device 3'], Destinations = ['Device 4'], BiDirectional = 'true')

#Config Frame Size
frame_length_2 = device_traffic_2.FrameLength.update(LengthType = 'FIXED', Fixed = '256')

################### create bound streamblocks end ###################

#SaveAsxml
save_config_input = config.Save({'mode': 'VENDOR_BINARY', 'file-name': os.path.join(os.path.dirname(__file__), 'verify_traffic_sample_script.xml')})
printStep("Start traffic")

config.TrafficControl( {"targets": ['IPV4Stream1 raw' , 'IPV6Stream1 raw', 'IPV4Stream1 bound', 'IPV6Stream1 bound'], "mode": 'START'})

time.sleep(5)

# Verify traffic during running
printStep("Verify traffic during running #1")

verify_traffic_input1 = config.VerifyTraffic({'verify_mode':'dropped_frames', 'debug':'True', 'save_db': 'True', "openhltest:traffic-items":{'all-traffic-items':'False','traffic-item-spec':[{'name':'IPV4Stream1 raw'}, {'name':'IPV6Stream1 raw'}, {'name':'IPV4Stream1 bound'}, {'name':'IPV6Stream1 bound'}]}})

pprint_output(verify_traffic_input1)


# Verify traffic during running
printStep("Verify traffic during running #2")
verify_traffic_input1 = config.VerifyTraffic({'tolerance':'1', 'debug':'True', 'save_db':'False', "openhltest:traffic-items":{'all-traffic-items':'True'}})

pprint_output(verify_traffic_input1)


# Verify traffic during running
printStep("Verify traffic during running #3")
verify_traffic_input1 = config.VerifyTraffic({'mode':'rx_port', 'tolerance':'100000', 'tolerance_mode':'frame', 'debug':'False', 'save_db':'False', 'openhltest:traffic-items':{'all-traffic-items':'False', 'traffic-item-spec':[{'name':'IPV4Stream1 bound'}]},'openhltest:ports':{'all-ports':'True'}})

pprint_output(verify_traffic_input1)


printStep("Verify traffic during running #4")
verify_traffic_input1 = config.VerifyTraffic({'mode':'rx_port', 'tolerance':'1', 'debug':'True', 'save_db':'False', 'openhltest:traffic-items':{'all-traffic-items':'False', 'traffic-item-spec':[{'name':'IPV4Stream1 raw'}, {'name':'IPV6Stream1 bound'}]},'openhltest:ports':{'all-ports':'True','port-spec':[{'name':'IPV4Stream1 raw','expected':'90', 'port-stream-spec':[{'name':port_handle2,'expected':'95'},{'name':port_handle1,'expected':'91'}]},{'name':'IPV6Stream1 bound','expected':'70', 'port-stream-spec':[{'name':port_handle2,'expected':'75'},{'name':port_handle1,'expected':'75'}]}]}})

pprint_output(verify_traffic_input1)


# Stop traffic
printStep("Stop traffic")
config.TrafficControl( {"targets": ['IPV4Stream1 raw' , 'IPV6Stream1 raw', 'IPV4Stream1 bound', 'IPV6Stream1 bound'], "mode": 'STOP'})


# Verify traffic after stop
printStep("Verify traffic after stop #5")

verify_traffic_input1 = config.VerifyTraffic({'tolerance':'3.2', 'mode':'tx_port', 'debug':'True', 'flow_per_stream':'10', 'save_db':'True', 'openhltest:traffic-items':{'all-traffic-items':'False', 'traffic-item-spec':[{'name':'IPV4Stream1 bound'}, {'name':'IPV6Stream1 bound'}]}, 'openhltest:ports':{'all-ports':'False','port-spec':[{'name': port_handle1}]}})

pprint_output(verify_traffic_input1)

printStep("Verify traffic after stop #6")

verify_traffic_input1 = config.VerifyTraffic({'tolerance':'3.2', 'expected':'100', 'debug':'False', 'flow_per_stream':'10', 'save_db':'True', 'openhltest:traffic-items':{'all-traffic-items':'False', 'traffic-item-spec':[{'name':'IPV4Stream1 raw'}, {'name':'IPV6Stream1 raw'}]}})

pprint_output(verify_traffic_input1)

#disconnect ports
port_control_input = config.PortControl({"targets": [port_handle1, port_handle2], "mode": 'DISCONNECT'})

printStep("Disconnect ports and delete session")
session.delete()
try:
    session = openhltest.Sessions.read(Name = sessionname)
except:
    print("    Deleted session - %s\n" % sessionname)