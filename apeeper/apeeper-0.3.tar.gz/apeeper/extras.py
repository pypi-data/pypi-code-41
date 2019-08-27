import pwd, grp
import os
from collections import namedtuple
from subprocess import check_output, check_call
import requests
# from flask import request

NetstatInfo = namedtuple('NetstatInfo',['protocol', 'local_address', 'remote_address', 'state','pid'])
TTL=149

def get_ip():
	import socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
	    # doesn't even have to be reachable
	    s.connect(('10.255.255.255', 1))
	    IP = s.getsockname()[0]
	except:
	    IP = None
	finally:
	    s.close()
	return IP


def get_uid(user):
	# Get the uid/gid from the name
    runningUid = pwd.getpwnam(user).pw_uid
    return runningUid

def get_process_id():
	return os.getpid()

def get_instance_id():
	import requests
	resp = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
	resp.raise_for_status()
	return (resp.text).encode('utf-8')

def get_region():
	import requests
	resp = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone')
	resp.raise_for_status()
	return (resp.text).encode('utf-8')

def is_gunicorn():
	return "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")

# TODO: The check_call will raise an Exception if the exit code is non-zero. So we should probably surround and handle these somewhere

def create_iptables_rules():
	ip = get_ip()
	if ip:
		check_call(['sudo','iptables','-t','nat','-A','OUTPUT','-m','ttl','--ttl-eq','{}'.format(TTL),'-p','tcp','-j','ACCEPT','-s','{}'.format(ip)])
	else:
		#if no ip retrieved, we i will allow source to be anywhere
		check_call(['sudo','iptables','-t','nat','-A','OUTPUT','-m','ttl','--ttl-eq','{}'.format(TTL),'-p','tcp','-j','ACCEPT'])
	check_call(['sudo','iptables','-t','nat','-A','OUTPUT','-p','tcp','--dport','80','-j','DNAT','--to-destination','127.0.0.1:5000', '-d','169.254.169.254'])


def remove_apeeper_iprules():
	print "============== REMOVING APEEPER IPTABLES RULES ================"
	if check_existing_iptables_rules():
		ip = get_ip()
		if ip:
			check_call(['sudo','iptables','-t','nat','-D','OUTPUT','-m','ttl','--ttl-eq','{}'.format(TTL),'-p','tcp','-j','ACCEPT','-s','{}'.format(ip)])
		else:
			#if no ip retrieved, we i will allow source to be anywhere
			check_call(['sudo','iptables','-t','nat','-D','OUTPUT','-m','ttl','--ttl-eq','{}'.format(TTL),'-p','tcp','-j','ACCEPT'])
		check_call(['sudo','iptables','-t','nat','-D','OUTPUT','-p','tcp','--dport','80','-j','DNAT','--to-destination','127.0.0.1:5000', '-d','169.254.169.254'])
	else:
		print "Apeeper rules not detected. Wierd. Not removing rules"


def check_existing_iptables_rules():
	import iptc
	ttl_match = False
	dest_match = False
	chain = iptc.Chain(iptc.Table(iptc.Table.NAT), "OUTPUT")
	for rule in chain.rules:
		for match in rule.matches:
			if match.parameters == {'ttl_eq':'149'}:
				ttl_match = True
			elif match.parameters == {u'dport': u'80'} and match.rule.dst == '169.254.169.254/255.255.255.255':
				dest_match = True
	return (ttl_match, dest_match)


def get_additional_details(request):
	additional_details = {}
	(pidprogram, netstat_details) = get_netstat_data(request)
	# Stage 3: Get process owner
	program_info = pidprogram.split('/')
	if program_info and len(program_info) == 2:
		pid = program_info[0]
		program = program_info[1]
		if pid:
			additional_details['pid'] = pid
			owner = get_process_owner(pid)
			if owner:
				additional_details['owner'] = owner
	# Stage 4: Get cmdline
	if pid:
		cmdline = get_cmdline_var(pid)
		if cmdline:
			additional_details['cmdline'] = cmdline
	# Stage 5: Add offending meta data service url
	additional_details['url'] = request.path

	return additional_details


def trigger_token(url, data):
	resp = requests.get(url, params=data)

def get_netstat_data(request):
	# Stage 1: Get Address we looking for
	remote_port = request.environ.get('REMOTE_PORT',None)
	target_addr = "{}:{}".format(request.remote_addr,remote_port)

	# Stage 2: Parse netstat output
	results = []
	pid = None
	for line in check_output('sudo netstat -tunp'.split(), universal_newlines=True).splitlines():
		item = parse_netstat_line(line)
		if item and item.local_address == target_addr:  # parsed successfully
			pid = item.pid
		elif item:
			results.append(item)

	# Results: [NetstatInfo(protocol='tcp', local_address='172.31.15.14:59952', remote_address='169.254.169.254:80', state='ESTABLISHED',
	# pid='13999/curl'), NetstatInfo(protocol='tcp', local_address='172.31.15.14:22', remote_address='129.205.140.132:58466',
	# state='ESTABLISHED', pid='13764/sshd'), NetstatInfo(protocol='tcp', local_address='127.0.0.1:5000', remote_address='172.31.15.14:59952',
	# state='ESTABLISHED', pid='13993/python')]

	return (pid,results)

def get_cmdline_var(pid):
	try:
		result = check_output(['sudo','cat','/proc/{}/cmdline'.format(pid)])
		return result.replace('\x00',' ')
	except Exception as e:
		print e.message
		return None

def get_process_owner(pid):
	try:
		result = check_output(['ps','-o','user=','-p','{}'.format(pid)])
		return result.replace('\n','')
	except Exception as e:
		print e.message
		return None

def parse_netstat_line(line):
	fields = line.split()
	if len(fields) == 7 and fields[0] in ('tcp', 'udp'):
		# alter this condition to taste;
	    # remember that netstat injects column headers.
    	# consider other checks, too.
		return NetstatInfo(fields[0], fields[3], fields[4], fields[5], fields[6])


class HTTPAdapterWithSocketOptions(requests.adapters.HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.socket_options = kwargs.pop("socket_options", None)
        super(HTTPAdapterWithSocketOptions, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.socket_options is not None:
            kwargs["socket_options"] = self.socket_options
        super(HTTPAdapterWithSocketOptions, self).init_poolmanager(*args, **kwargs)