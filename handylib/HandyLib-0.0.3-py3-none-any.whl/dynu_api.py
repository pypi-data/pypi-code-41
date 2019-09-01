import requests
def list_domains(api_key):
	url = 'https://api.dynu.com/v2/dns'
	headers = {}
	headers["accept"]="application/json"
	headers['API-Key']=api_key
	r = requests.get(url,headers = headers)
	print(r.status_code)
	print(r.text)

def update_ip(api_key, hostname, pwd, ip='',debug=False):
	url = 'https://api.dynu.com/nic/update?hostname={0}'.format(hostname)
	if ip != '':
		url += '&myip={0}'.format(ip)
	url += '&password={0}'.format(pwd)
	r = requests.get(url)
	headers = {}
	headers["accept"]="application/json"
	headers['API-Key']=api_key

	if debug:
		print(url)
		print(r.status_code)
		print(r.text)

	if r.status_code==200:
		if r.text[:4] in ['good','nochg']:
			return True
		else:
			return r
