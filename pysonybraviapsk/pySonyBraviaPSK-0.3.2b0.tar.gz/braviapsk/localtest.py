#!/usr/bin/env python3
#
#   Sony Bravia - Home Assistant
#   gerard33
#
#   Enter the IP address, PSK and MAC address of the TV below
#

import re

def _get_mac_address(ip_address):
    """Get the MAC address of the device."""
    from subprocess import Popen, PIPE

    pid = Popen(["arp", "-n", ip_address], stdout=PIPE)
    pid_component = pid.communicate()[0]
    match = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})".encode('UTF-8'),
                      pid_component)
    if match is not None:
        return match.groups()[0]
    return None

# from sony_bravia_psk import BraviaRC

ip = '192.168.1.191'
psk = 'sony'
mac = 'FC:F1:52:D8:EB:1F'

# tv = BraviaRC(ip, psk, mac)

print(_get_mac_address(ip))

# try:
#     tvstatus = tv.get_power_status()
#     print('Status TV:', tvstatus)
# except KeyError:
#     print('TV not found')
#     sys.exit()

# if tvstatus == 'active':  
#     tvplaying = tv.get_playing_info()
#     #print(tvplaying)
#     if not tvplaying:
#         print('No info from TV available')
#     else:
#         if tvplaying['programTitle'] != None:
#             print(str(int(tvplaying['dispNum']))+':', tvplaying['title'],'-',tvplaying['programTitle'])
#             time_info = tv.playing_time(tvplaying['startDateTime'], tvplaying['durationSec'])
#             print(time_info.get('start_time'), '-', time_info.get('end_time'))
#             print('Progam media type:', tvplaying['programMediaType'])
#             print('Source:', tvplaying['source'])
#         else:
#             if tvplaying['title'] != '':
#                 print('Playing:', tvplaying['title'])
#                 print('Progam media type:', tvplaying['programMediaType'])
#                 print('Source:', tvplaying['source'])
#             else:
#                 print('App started')
#                 print(tvplaying['title'])
        
#     tvinfo = tv.get_system_info()
#     print('TV model:', tvinfo['model'])
    
#     network = tv.get_network_info()
#     print('MAC address:', network['mac'])
    
#     #test_vol = tv.set_volume_level("20")
#     #print(test_vol)
    
#     vol = tv.get_volume_info()
#     print('Volume:', vol['volume'])
#     print('Mute: ', vol['mute'])
    
#     #test_info = tv.get_test_info()
    
#     #test_mute = tv.get_mute_info()
#     #print(test_mute)
    
#     #commands = tv._refresh_commands()
#     #print(commands)
    
#     #test = tv.get_source('tv:dvbc')
#     #print('Source list:', test)
    
#     #test2 = tv.get_source('extInput:hdmi')
#     #print('Source list:', test2)
        
#     #test2= tv.load_source_list()
#     #print(test2)
#     #test3 = tv.select_source('HDMI 2')
#     #print(test3)
    
# else:
#     print('TV status:', tvstatus) #status is standby just after turning off
