import os
import json
import sys
import logging
from apeeper.extras import get_ip, create_iptables_rules, check_existing_iptables_rules, get_process_id, \
get_instance_id, get_region

logger = logging.getLogger('apeeper')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('/tmp/apeeper.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class SetupException(Exception):
	def __init__(self,msg):
		Exception.__init__(self, msg)
		self.message = msg

# CONFIG_FILE=os.path.expanduser('~')+"/.apeeper.conf"

# class Config:

# 	def __init__(self, configfile=CONFIG_FILE):

def create_config(auth_url):
	with open(os.path.expanduser('~')+"/.apeeper.conf","w+") as f:
		a = {'auth_url':auth_url}
		f.write(json.dumps(a))

def read_apeeper_config():
	contents = '[]'
	try:
		with open(os.path.expanduser('~')+"/.apeeper.conf","r") as f:
			contents = f.read()
	except IOError:
		pass
	return contents

def read_apeeper_config_obj():
	return json.loads(read_apeeper_config())

def get_auth_url():
	config = read_apeeper_config_obj()
	if 'auth_url' in config:
		return config['auth_url']
	else:
		return None

def get_instance_name():
	config = read_apeeper_config_obj()
	if 'instancename' in config:
		return config['instancename']
	else:
		return ''

def get_list():
	config = read_apeeper_config_obj()
	# remove_list()
	if 'whitelist' in config and 'blacklist' in config:
		logger.error("[*] Both blacklist and whitelist are present in config. Please only add one. Continuing with default.")
		return [], 'default'
	if 'whitelist' in config:
		return config['whitelist'].split(','), 'whitelist'
	elif 'blacklist' in config:
		return config['blacklist'].split(','), 'blacklist'
	else:
		return [], 'default'

def remove_list():
	config = read_apeeper_config_obj()
	if 'whitelist' in config:
		del config['whitelist']
	elif 'blacklist' in config:
		del config['blacklist']
	with open(os.path.expanduser('~')+"/.apeeper.conf","w+") as f:
		f.write(json.dumps(config))

def get_token_url_from_config():
	config = read_apeeper_config_obj()
	if 'token' in config:
		return config['token']
	else:
		raise SetupException('token is missing from config.')

def get_token_url_from_canary_console(url):
	import requests
	instanceid = get_instance_id()
	region = get_region()
	data = {'instanceid':instanceid,'region':region}
	data['instancename'] = get_instance_name()
	resp = requests.post(url, data=data)
	if 'canarytoken' in resp.json() and 'url' in resp.json()['canarytoken']:
		return resp.json()['canarytoken']['url']
	else:
		logger.error("[*] Failed to retrieve canarytoken using the factory url. Please double check and try again, or contact support.")
		logger.error("[e] Error: {}".format(resp.json() if resp.json() else resp.text))
		sys.exit()

def write_to_apeeper_config(new_dict=None, key=None, value=None):
	config = read_apeeper_config_obj()
	if new_dict and type(new_dict) is dict:
		config.update(new_dict)

	if key and value:
		config[key] = value 
		
	with open(os.path.expanduser('~')+"/.apeeper.conf","w+") as f:
		f.write(json.dumps(config))


def remove_auth_url():
	config = read_apeeper_config_obj()
	del config['auth_url']
	with open(os.path.expanduser('~')+"/.apeeper.conf","w+") as f:
		f.write(json.dumps(config))

def check_config_exists():
	exists = os.path.isfile(os.path.expanduser('~')+"/.apeeper.conf")
	return exists

def check_token_exists():
	config = read_apeeper_config_obj()
	if 'token' in config:
		return True
	else:
		return False

def set_pid_file():
	pid = get_process_id()
	path = sys.prefix+'/bin/apeeperd.pid'
	with open(path,"w+") as f:
		f.write(str(pid))

def setup_apeeper():
	logger.debug("============== RUNNING APEEPER SETUP ================")
	if not check_config_exists():
		logger.error("[*] No config file found. Please use -a <factory_url>.")
		sys.exit()

	auth_url=get_auth_url()
	if not check_token_exists():
		if auth_url is None:
			logger.error("[*] There is no factory url or canarytoken in the config file. Please insert the factory url generated on your Canary Console using `apeeperd -a.\r\n")
			sys.exit()
		logger.debug("[*] Couldn't find apeeper token. Retrieving one from your Canary Console using {}".format(auth_url))
		token = get_token_url_from_canary_console(auth_url)
		write_to_apeeper_config(key='token',value=token)
		if not check_token_exists():
			logger.error("[*] Retrieving of your canarytoken failed. Please try again or contact support.")
			sys.exit()
	
	if auth_url:
		logger.debug('[*] Factory url is being removed.')
		remove_auth_url()

	if not check_existing_iptables_rules() == (True, True):
		logger.debug("[*] Couldn't find known iptables rules needed. Adding them.")
		#TODO: check which rule failed and add just that one. 
		create_iptables_rules()
	logger.debug("============== FINISHED APEEPER SETUP ================")

# if __name__ == "__main__":
# 	setup_apeeper()


# EXTRA NOTES
# # call(['apeeper'])
# #create special user with no home or login ability for uid method route
# # check_call(['sudo','adduser','--shell','/bin/false','--no-create-home','myappuser'])
# # check_call(['sudo','iptables','-t','nat','-A','OUTPUT','-p','tcp','-j','ACCEPT','-m','owner','--uid-owner','{}'.format('myappuser')])
# ip = get_ip()
# if ip:
# 	result = check_call(['sudo','iptables','-t','nat','-A','OUTPUT','-m','ttl','--ttl-eq','{}'.format(TTL),'-p','tcp','-j','ACCEPT','-s','{}'.format(ip)])
# else:
# #if no ip retrieved, we i will allow source to be anywhere
# result = check_call(['sudo','iptables','-t','nat','-A','OUTPUT','-m','ttl','--ttl-eq','{}'.format(TTL),'-p','tcp','-j','ACCEPT'])
# check_call(['sudo','iptables','-t','nat','-A','OUTPUT','-p','tcp','--dport','80','-j','DNAT','--to-destination','127.0.0.1:5000', '-d','169.254.169.254'])


# <div class="col-xs-8"><input type="text" value="106890046964239623114" id="clientId" readonly></div>
# <div class="col-xs-2"><button class="btn btn-default btn-clipboard-copy-id" data-clipboard-target="#clientId" type="button"><img src="/static/images/clippy.svg" alt="Copy to clipboard">Copy ID</button></div>

# $('.btn-clipboard-copy-id').tooltipster({
#       trigger: 'click',
#       distance: 10
#     });
#     $('.btn-clipboard-copy-scopes').tooltipster({
#       trigger: 'click',
#       distance: 10
#     });
#     var clipboard_id = new Clipboard('.btn-clipboard-copy-id',
#           { container: document.getElementById('canarytoken-add-modal'),
#             text: '106890046964239623114'}
#           );
#     clipboard_id.on('success', function(e){
#       $('.btn-clipboard-copy-id').tooltipster('content', 'ID Copied')
#       $('.btn-clipboard-copy-id').tooltipster('open');
#     });
#     clipboard_id.on('failure', function(e){
#       $('.btn-clipboard-copy-id').tooltipster('content', 'ID Copy failed!')
#       $('.btn-clipboard-copy-id').tooltipster('open');
#     })